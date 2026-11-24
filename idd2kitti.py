"""Convert IDD-3D (front camera cam3) into the KITTI-tracking layout used by cusp_eval.py.

IDD-3D gives 3D boxes in the LiDAR frame and no camera calibration or odometry. This script uses
  * the camera model fitted by idd_pilot.py (calib_cam3.json) to express every box in camera
    coordinates (KITTI convention) and to derive its 2D box, truncation and occlusion level,
  * labelled static objects (riderless two-wheelers, pedestrians' along-road motion) to estimate the
    ego speed, written as ego/<seq>.txt (v [m/s], a [m/s^2] per frame).
Images are symlinked, not copied.

Usage:
  python idd2kitti.py --idd-root /Volumes/SKOS-APFS/PHD-CUSP/data/idd3d/train_val \
      --calib idd_pilot/calib_cam3.json --splits idd_pilot/idd3d_splits.json \
      --out /Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti
Creates <out>/{calibration,validation,test}/{image_02,label_02,calib,ego}/ and <out>/mapping.csv
"""
import argparse, csv, glob, json, math, os
import numpy as np
import idd_pilot as P

TYPE_MAP = {"car": "Car", "tourcar": "Auto", "truck": "Truck", "bus": "Bus", "van": "Car",
            "motorcylerider": "Motorcycle", "motorcyclerider": "Motorcycle", "scooterrider": "Motorcycle",
            "motorcycle": "TwoWheelerParked", "scooter": "TwoWheelerParked"}
STATIC_TYPES = {"TwoWheelerParked"}


def kitti_type(name):
    n = name.lower().replace(" ", "")
    if n in TYPE_MAP:
        return TYPE_MAP[n]
    if "pedestrian" in n or "bicycle" in n:
        return None
    g = P.group_of(name)
    return {"four": "Car", "two": "Motorcycle", "two_parked": "TwoWheelerParked"}.get(g)


BAD_LABELS = []


def read_label(path):
    """Some IDD-3D label files carry trailing data after the JSON array; keep the first array, log the file."""
    txt = open(path).read()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        try:
            obj, _ = json.JSONDecoder().raw_decode(txt.lstrip())
            BAD_LABELS.append((path, "trailing data ignored"))
            return obj if isinstance(obj, list) else []
        except json.JSONDecodeError:
            BAD_LABELS.append((path, "unreadable, frame has no labels"))
            return []


def occlusion_levels(items, W, H, scale=4):
    """items: list of (Z, box). Fraction of each box hidden by nearer boxes -> 0 (<10%), 1 (<50%), 2."""
    w, h = W // scale, H // scale
    order = sorted(range(len(items)), key=lambda i: items[i][0])
    mask = np.zeros((h, w), bool); lev = [0] * len(items)
    for i in order:
        x1, y1, x2, y2 = (np.array(items[i][1]) / scale).astype(int)
        x1, y1 = max(x1, 0), max(y1, 0); x2, y2 = min(x2, w - 1), min(y2, h - 1)
        if x2 <= x1 or y2 <= y1:
            continue
        cov = mask[y1:y2, x1:x2].mean()
        lev[i] = 0 if cov < 0.1 else (1 if cov < 0.5 else 2)
        mask[y1:y2, x1:x2] = True
    return lev


def ego_speed(frames_boxes, cam, dt=0.1):
    """Ego speed from labelled static objects: they move backwards along the camera's forward axis."""
    fwd = cam.R[2].copy(); fwd[2] = 0; fwd /= np.linalg.norm(fwd)
    lat = np.array([-fwd[1], fwd[0], 0.0])
    n = len(frames_boxes); v = np.full(n, np.nan)
    for k in range(n - 1):
        a = {b["id"]: b for b in frames_boxes[k]}; b = {o["id"]: o for o in frames_boxes[k + 1]}
        d = []
        for i in set(a) & set(b):
            t = kitti_type(a[i]["cls"])
            dp = b[i]["c"] - a[i]["c"]
            if t in STATIC_TYPES or a[i]["cls"].lower().startswith("pedestrian"):
                d.append((float(dp @ fwd), float(dp @ lat)))
        if d:
            d = np.array(d)
            # pedestrians walk; keep displacements consistent with the median of the frame
            med = np.median(d[:, 0]); keep = np.abs(d[:, 0] - med) < 0.3
            v[k] = -np.median(d[keep, 0]) / dt
    good = ~np.isnan(v)
    frac = float(good.mean()) if n else 0.0
    if good.sum() < 2:
        # no labelled static objects: take the mode of all objects' along-road displacement
        # (static road users dominate the mode except in moving queues); flagged in mapping.csv
        for k in range(n - 1):
            a = {o["id"]: o for o in frames_boxes[k]}; b = {o["id"]: o for o in frames_boxes[k + 1]}
            d = np.array([float((b[i]["c"] - a[i]["c"]) @ fwd) for i in set(a) & set(b)])
            if len(d) >= 3:
                hist, edges = np.histogram(d, bins=np.arange(-2.5, 0.51, 0.1))
                j = int(np.argmax(hist)); v[k] = -0.5 * (edges[j] + edges[j + 1]) / dt
        good = ~np.isnan(v); frac = -float(good.mean())        # negative = fallback source
    if good.sum() >= 2:
        v = np.interp(np.arange(n), np.flatnonzero(good), v[good])
    elif good.sum() == 1:
        v[:] = v[good][0]
    else:
        v[:] = 0.0
    v = np.clip(np.convolve(np.pad(v, 2, mode="edge"), np.ones(5) / 5, mode="valid"), 0, None)
    a = np.gradient(v, dt)
    return v, a, frac


def convert_seq(idd_root, seq, cam, out_root, sid):
    d = os.path.join(idd_root, seq)
    keys = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(d, "label", "*.json")))
    W, H = P.IMG_W, P.IMG_H
    os.makedirs(os.path.join(out_root, "image_02", sid), exist_ok=True)
    lines, frames_boxes, missing = [], [], 0
    for fr, k in enumerate(keys):
        img = os.path.join(d, "camera", P.CAM, k + ".png")
        dst = os.path.join(out_root, "image_02", sid, f"{fr:06d}.png")
        if os.path.exists(img):
            if os.path.lexists(dst):
                os.remove(dst)
            os.symlink(os.path.abspath(img), dst)
        else:
            missing += 1
        raw = read_label(os.path.join(d, "label", k + ".json"))
        boxes = []
        for o in raw:
            p, s, r = o["psr"]["position"], o["psr"]["scale"], o["psr"]["rotation"]
            boxes.append(dict(id=str(o["obj_id"]), cls=str(o["obj_type"]), c=np.array([p["x"], p["y"], p["z"]]),
                              size=np.array([s["x"], s["y"], s["z"]]), yaw=r["z"]))
        frames_boxes.append(boxes)
        vis = []
        for b in boxes:
            t = kitti_type(b["cls"])
            if t is None:
                continue
            pr = cam.project_box(b, require_inside=False)
            if pr is None:
                continue
            Xc = pr["Xc"]
            u = cam.f * Xc[:, 0] / Xc[:, 2] + cam.u0; v = cam.f * Xc[:, 1] / Xc[:, 2] + cam.v0
            full = np.array([u.min(), v.min(), u.max(), v.max()])
            clip = np.clip(full, 0, [W - 1, H - 1, W - 1, H - 1])
            a_full = (full[2] - full[0]) * (full[3] - full[1]); a_clip = (clip[2] - clip[0]) * (clip[3] - clip[1])
            if a_clip <= 4:
                continue
            trunc = float(np.clip(1 - a_clip / max(a_full, 1e-6), 0, 1))
            l, w, h = b["size"]
            ctr = cam.to_cam(b["c"][None])[0]
            loc = ctr + np.array([0, h / 2, 0])                       # KITTI: bottom centre, y down
            dvec = cam.R @ np.array([math.cos(b["yaw"]), math.sin(b["yaw"]), 0.0])
            ry = math.atan2(-dvec[2], dvec[0])
            vis.append(dict(t=t, id=b["id"], box=clip, trunc=trunc, hwl=(h, w, l), loc=loc, ry=ry,
                            Z=float(Xc[:4, 2].min())))
        occ = occlusion_levels([(o["Z"], o["box"]) for o in vis], W, H)
        for o, oc in zip(vis, occ):
            x1, y1, x2, y2 = o["box"]; h, w, l = o["hwl"]; X, Y, Z = o["loc"]
            lines.append(f"{fr} {o['id']} {o['t']} {o['trunc']:.2f} {oc} -10 {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} "
                         f"{h:.3f} {w:.3f} {l:.3f} {X:.3f} {Y:.3f} {Z:.3f} {o['ry']:.4f}")
    # track ids must be integers for KITTI readers
    ids = {}
    out = []
    for ln in lines:
        p = ln.split(" ", 2); ids.setdefault(p[1], len(ids)); out.append(f"{p[0]} {ids[p[1]]} {p[2]}")
    os.makedirs(os.path.join(out_root, "label_02"), exist_ok=True)
    open(os.path.join(out_root, "label_02", sid + ".txt"), "w").write("\n".join(out) + "\n")
    os.makedirs(os.path.join(out_root, "calib"), exist_ok=True)
    P2 = [cam.f, 0, cam.u0, 0, 0, cam.f, cam.v0, 0, 0, 0, 1, 0]
    open(os.path.join(out_root, "calib", sid + ".txt"), "w").write("P2: " + " ".join(f"{x:.6f}" for x in P2) + "\n")
    v, a, frac = ego_speed(frames_boxes, cam)
    os.makedirs(os.path.join(out_root, "ego"), exist_ok=True)
    open(os.path.join(out_root, "ego", sid + ".txt"), "w").write("\n".join(f"{x:.4f} {y:.4f}" for x, y in zip(v, a)) + "\n")
    return len(keys), missing, len(out), frac, float(np.mean(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--idd-root", required=True)
    ap.add_argument("--calib", required=True)
    ap.add_argument("--splits", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cam = P.Camera(json.load(open(a.calib))["params"])
    sp = json.load(open(a.splits))
    rows = []
    for split, key in (("calibration", "calibration"), ("validation", "validation"), ("test", "test_locked")):
        if not sp.get(key):
            continue
        root = os.path.join(a.out, split)
        for i, seq in enumerate(sp[key]):
            sid = f"{i:04d}"
            n, miss, nl, frac, vm = convert_seq(a.idd_root, seq, cam, root, sid)
            rows.append(dict(split=split, kitti_seq=sid, idd_seq=seq, frames=n, missing_images=miss, labels=nl,
                             ego_frames_with_static=round(frac, 2), mean_ego_speed=round(vm, 2)))
            print(f"{split:12s} {sid} <- {seq}: {n} frames, {miss} missing images, {nl} boxes, "
                  f"ego from static objects in {frac * 100:.0f}% of frames, mean v {vm:.1f} m/s")
    with open(os.path.join(a.out, "mapping.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("mapping ->", os.path.join(a.out, "mapping.csv"))
    with open(os.path.join(a.out, "bad_labels.txt"), "w") as f:
        f.writelines(f"{p}\t{why}\n" for p, why in BAD_LABELS)
    print(f"{len(BAD_LABELS)} malformed label files (listed in bad_labels.txt)")


if __name__ == "__main__":
    main()

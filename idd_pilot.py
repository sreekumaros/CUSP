"""IDD-3D pilot: front-camera calibration from labelled 3D boxes + monocular range accuracy.

IDD-3D ships 3D boxes in the LiDAR frame but no camera calibration. This script
  1. runs YOLO26s on the front camera (cam3) and caches the detections,
  2. FITS the camera model (rotation, camera centre, focal length, principal point) by aligning
     projected 3D label boxes with the detections on the *fit* sequences only,
  3. derives camera height h and horizon row y_h from the fitted pose and the labelled box bottoms,
     and fits the tyre-contact offset delta per class group (four-wheel / two-wheel) on the fit sequences,
  4. reports the monocular range error (ground-contact cue and width cue) against the LiDAR-labelled
     range on the *pilot* sequences, which are not used in steps 2-3.

Usage (Mac, inside the project .venv):
  python idd_pilot.py --root /Volumes/SKOS-APFS/PHD-CUSP/data/idd3d/train_val \
      --fit 20220118103808_seq_1 20220118103808_seq_10 20220118103808_seq_11 20220118103808_seq_12 \
      --pilot 20220118103808_seq_2 --out idd_pilot --device mps
Outputs in --out: calib_cam3.json, pilot_obs.csv, pilot_summary.md, overlays/*.jpg
"""
import argparse, glob, json, math, os, sys, time
import numpy as np

CAM = "cam3"
IMG_W, IMG_H = 1440, 1080
COCO_FOUR, COCO_TWO = {2, 5, 7}, {3}            # car, bus, truck | motorcycle
BANDS = [(1, 10), (10, 30), (30, 60)]


# ----------------------------------------------------------------------------- labels
def group_of(name):
    n = str(name).lower()
    if "pedestrian" in n or "person" in n or "bicycle" in n:
        return None
    if "rider" in n:                                 # MotorcyleRider / ScooterRider: one box for vehicle + rider
        return "two"
    if "motor" in n or "scoot" in n:                 # Motorcycle / Scooter without rider (mostly parked)
        return "two_parked"
        return "two"
    if any(k in n for k in ("car", "bus", "truck", "auto", "van", "tempo", "vehicle", "jeep", "tractor")):
        return "four"
    return None


def load_labels(path):
    out = []
    for o in json.load(open(path)):
        g = group_of(o["obj_type"])
        if g is None:
            continue
        p, s, r = o["psr"]["position"], o["psr"]["scale"], o["psr"]["rotation"]
        out.append(dict(id=str(o["obj_id"]), cls=str(o["obj_type"]), group=g,
                        c=np.array([p["x"], p["y"], p["z"]]), size=np.array([s["x"], s["y"], s["z"]]), yaw=r["z"]))
    return out


def corners(b):
    l, w, h = b["size"]
    x = np.array([1, 1, -1, -1, 1, 1, -1, -1]) * l / 2
    y = np.array([1, -1, -1, 1, 1, -1, -1, 1]) * w / 2
    z = np.array([-1, -1, -1, -1, 1, 1, 1, 1]) * h / 2
    c, s = math.cos(b["yaw"]), math.sin(b["yaw"])
    return np.stack([c * x - s * y, s * x + c * y, z], 1) + b["c"]      # 8x3, first 4 = bottom


def seq_frames(root, seq):
    d = os.path.join(root, seq)
    fr = []
    for lp in sorted(glob.glob(os.path.join(d, "label", "*.json"))):
        k = os.path.splitext(os.path.basename(lp))[0]
        ip = os.path.join(d, "camera", CAM, k + ".png")
        if os.path.exists(ip):
            fr.append(dict(seq=seq, key=k, label=lp, image=ip))
    return fr


# ----------------------------------------------------------------------------- detections
def detect(frames, cache_dir, device, conf=0.25):
    os.makedirs(cache_dir, exist_ok=True)
    model = None
    for f in frames:
        cp = os.path.join(cache_dir, f"{f['seq']}_{f['key']}.json")
        if os.path.exists(cp):
            f["dets"] = json.load(open(cp)); continue
        if model is None:
            from ultralytics import YOLO
            model = YOLO("yolo26s.pt")
        r = model.predict(f["image"], device=device, conf=conf, classes=sorted(COCO_FOUR | COCO_TWO | {0}), verbose=False)[0]
        d = [dict(box=[float(v) for v in b], cls=int(c), conf=float(s))
             for b, c, s in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist())]
        json.dump(d, open(cp, "w")); f["dets"] = d
    for f in frames:
        f["dets"] = merge_riders(f["dets"])
    return frames


def merge_riders(dets):
    """Two-wheeler unit = motorcycle box united with the person box riding it (IDD-3D labels rider + vehicle as one)."""
    bikes = [d for d in dets if d["cls"] in COCO_TWO]; people = [d for d in dets if d["cls"] == 0]
    out = [d for d in dets if d["cls"] in COCO_FOUR]
    for b in bikes:
        x1, y1, x2, y2 = b["box"]; bw = x2 - x1
        best = None
        for p in people:
            px1, py1, px2, py2 = p["box"]
            ov = max(0, min(x2, px2) - max(x1, px1)) / max(1e-3, min(bw, px2 - px1))
            if ov > 0.5 and y1 - 0.2 * (y2 - y1) < py2 < y2 + 0.05 * (y2 - y1) and py1 < y1:
                if best is None or py1 < best["box"][1]:
                    best = p
        box = [x1, y1, x2, y2] if best is None else [min(x1, best["box"][0]), min(y1, best["box"][1]), max(x2, best["box"][2]), y2]
        out.append(dict(box=box, cls=b["cls"], conf=b["conf"], rider=best is not None))
    return out


# ----------------------------------------------------------------------------- camera model
def rodrigues(v):
    th = np.linalg.norm(v)
    if th < 1e-12:
        return np.eye(3)
    k = v / th; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def base_rot(psi, pitch=0.0):
    """Camera axes (rows: x right, y down, z forward) for a camera looking along azimuth psi in a z-up LiDAR frame."""
    f = np.array([math.cos(psi) * math.cos(pitch), math.sin(psi) * math.cos(pitch), -math.sin(pitch)])
    r = np.array([math.sin(psi), -math.cos(psi), 0.0])
    d = np.cross(f, r)
    return np.stack([r, d, f])


class Camera:
    def __init__(self, p):              # p = [psi, rx, ry, rz, cx, cy, cz, f, u0, v0]
        self.p = np.asarray(p, float)
        self.R = rodrigues(self.p[1:4]) @ base_rot(self.p[0])
        self.C = self.p[4:7]; self.f, self.u0, self.v0 = self.p[7:10]

    def to_cam(self, X):
        return (X - self.C) @ self.R.T

    def project_box(self, b, require_inside=True):
        Xc = self.to_cam(corners(b))
        if (Xc[:, 2] < 0.5).any():
            return None
        u = self.f * Xc[:, 0] / Xc[:, 2] + self.u0; v = self.f * Xc[:, 1] / Xc[:, 2] + self.v0
        box = np.array([u.min(), v.min(), u.max(), v.max()])
        inside = box[0] >= 0 and box[1] >= 0 and box[2] <= IMG_W - 1 and box[3] <= IMG_H - 1
        if require_inside and not inside:
            return None
        return dict(box=np.clip(box, 0, [IMG_W - 1, IMG_H - 1, IMG_W - 1, IMG_H - 1]), Xc=Xc, inside=inside)

    def horizon_row(self):
        fwd = self.R[2].copy(); fwd[2] = 0; fwd /= np.linalg.norm(fwd)      # horizontal direction of the optical axis
        d = self.R @ fwd
        return self.f * d[1] / d[2] + self.v0


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1]); x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    i = max(0, x2 - x1) * max(0, y2 - y1)
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def compatible(group, coco):
    return (group == "four" and coco in COCO_FOUR) or (group in ("two", "two_parked") and coco in COCO_TWO)


def match_frame(cam, f, thr, require_inside=True):
    from scipy.optimize import linear_sum_assignment
    gts = []
    for b in f["boxes"]:
        pr = cam.project_box(b, require_inside)
        if pr is not None:
            gts.append((b, pr))
    dets = f["dets"]
    if not gts or not dets:
        return []
    M = np.zeros((len(gts), len(dets)))
    for i, (b, pr) in enumerate(gts):
        for j, d in enumerate(dets):
            if compatible(b["group"], d["cls"]):
                M[i, j] = iou(pr["box"], d["box"])
    ri, ci = linear_sum_assignment(-M)
    return [(gts[i][0], gts[i][1], dets[j], M[i, j]) for i, j in zip(ri, ci) if M[i, j] >= thr]


def objective(p, frames, thr=0.3):
    cam = Camera(p)
    return -sum(m[3] for f in frames for m in match_frame(cam, f, thr))


PP_SIGMA = 20.0


def fit_camera(frames, log):
    from scipy.optimize import minimize
    best = None
    t0 = time.time()
    for psi in np.radians(np.arange(0, 360, 5)):                  # coarse: heading x focal length
        for fl in (700, 900, 1100, 1300, 1600, 2000, 2500, 3000):
            p = [psi, 0, 0, 0, 0, 0, 0, fl, IMG_W / 2, IMG_H / 2]
            s = objective(p, frames, 0.1)
            if best is None or s < best[0]:
                best = (s, p)
    log(f"coarse: heading {math.degrees(best[1][0]):.0f} deg, f {best[1][7]:.0f}, score {-best[0]:.1f} ({time.time() - t0:.0f} s)")
    p = np.array(best[1], float)
    r = minimize(objective, p, args=(frames, 0.1), method="Powell", options=dict(maxiter=3000, xtol=1e-4, ftol=1e-4))
    p = r.x
    log(f"IoU search: score {-r.fun:.1f}")
    # box-edge least squares: fix the matches, fit all parameters to the detected box edges, re-match, repeat.
    # Near and far vehicles together separate focal length from camera position.
    from scipy.optimize import least_squares
    for it, thr in enumerate((0.3, 0.5, 0.5, 0.5)):
        cam = Camera(p)
        pairs = [(b, np.array(d["box"])) for f in frames for b, pr, d, s in match_frame(cam, f, thr)]
        if len(pairs) < 10:
            break
        def res(q):
            c = Camera(q); out = []
            for b, db in pairs:
                pr = c.project_box(b, require_inside=False)
                out.extend((pr["box"] - db) if pr is not None else [100.0] * 4)
            out.extend(np.maximum(np.abs(q[4:7]) - 2.0, 0) * 50)    # weak prior: camera within ~2 m of the LiDAR
            out.extend([(q[8] - IMG_W / 2) / PP_SIGMA, (q[9] - IMG_H / 2) / PP_SIGMA])   # weak prior: principal point near centre
            return np.array(out)
        r = least_squares(res, p, loss="soft_l1", f_scale=4.0, x_scale="jac", max_nfev=400)
        p = r.x
        log(f"edge LSQ {it + 1}: {len(pairs)} pairs, median |edge residual| {np.median(np.abs(r.fun[:4 * len(pairs)])):.2f} px")
    return Camera(p)


# ----------------------------------------------------------------------------- observations
def observations(cam, frames, h, yh, thr=0.5):
    rows = []
    for f in frames:
        for b, pr, d, s in match_frame(cam, f, thr, require_inside=False):
            Xc = pr["Xc"]; bottom = Xc[:4]
            Z = float(bottom[:, 2].min())                             # nearest bottom-corner depth (as on KITTI)
            X = float(Xc[:, 0].mean())
            x1, y1, x2, y2 = d["box"]
            rows.append(dict(seq=f["seq"], key=f["key"], id=b["id"], cls=b["cls"], group=b["group"],
                             Z=Z, X=X, W=float(b["size"][1]), yb=y2, w=x2 - x1, iou=s, conf=d["conf"],
                             border=int(y2 >= IMG_H - 3), proj_yb=float(pr["box"][3])))
    return rows


def fit_delta(rows, h, yh, f):
    out = {}
    for g in ("four", "two"):
        r = [o for o in rows if o["group"] == g and not o["border"] and 3 < o["Z"] < 50 and o["yb"] - yh > 5]
        if len(r) < 10:
            out[g] = 0.0; continue
        Zc = np.array([f * h / (o["yb"] - yh) for o in r]); Z = np.array([o["Z"] for o in r])
        grid = np.arange(0, 2.01, 0.05)
        loss = [np.median(np.abs(np.log(np.maximum(Zc - dl, 0.3)) - np.log(Z))) for dl in grid]
        out[g] = float(grid[int(np.argmin(loss))])
    return out


def summarise(rows, f, h, yh, delta, Wg):
    lines = ["| Group | Band (m) | n | Contact cue: bias (m) | MAE (m) | median rel. err | 90th pct rel. err | Width cue: MAE (m) | median rel. err |",
             "|---|---|---|---|---|---|---|---|---|"]
    for g in ("four", "two"):
        for lo, hi in BANDS + [(1, 60)]:
            r = [o for o in rows if o["group"] == g and lo < o["Z"] <= hi]
            if not r:
                continue
            Z = np.array([o["Z"] for o in r])
            dy = np.array([o["yb"] - yh for o in r]); ok = (dy > 2) & (np.array([o["border"] for o in r]) == 0)
            Zc = np.where(ok, f * h / np.maximum(dy, 1e-3) - delta[g], np.nan)
            Zw = f * Wg[g] / np.array([max(o["w"], 1) for o in r])
            e = Zc - Z; rel = np.abs(e) / Z; ew = Zw - Z; relw = np.abs(ew) / Z
            band = "all" if (lo, hi) == (1, 60) else f"{lo}-{hi}"
            lines.append(f"| {g} | {band} | {len(r)} ({int(ok.sum())} contact) | {np.nanmedian(e):+.2f} | {np.nanmean(np.abs(e)):.2f} | "
                         f"{np.nanmedian(rel) * 100:.1f}% | {np.nanpercentile(rel, 90) * 100:.1f}% | {np.mean(np.abs(ew)):.2f} | {np.median(relw) * 100:.1f}% |")
    return "\n".join(lines)


def overlays(cam, frames, out, n=6):
    import cv2
    os.makedirs(out, exist_ok=True)
    for f in frames[:: max(1, len(frames) // n)][:n]:
        im = cv2.imread(f["image"])
        for b in f["boxes"]:
            pr = cam.project_box(b, require_inside=False)
            if pr is not None:
                x1, y1, x2, y2 = map(int, pr["box"]); cv2.rectangle(im, (x1, y1), (x2, y2), (0, 220, 0), 3)
                cv2.putText(im, f"{b['cls'][:5]} {pr['Xc'][:4, 2].min():.1f}m", (x1, max(20, y1 - 6)), 0, 0.8, (0, 220, 0), 2)
        for d in f["dets"]:
            x1, y1, x2, y2 = map(int, d["box"]); cv2.rectangle(im, (x1, y1), (x2, y2), (0, 0, 255), 2)
        yh = int(cam.horizon_row()); cv2.line(im, (0, yh), (IMG_W, yh), (255, 200, 0), 2)
        cv2.imwrite(os.path.join(out, f"{f['seq']}_{f['key']}.jpg"), cv2.resize(im, (960, 720)))


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--fit", nargs="+", required=True, help="sequences used to fit the camera and delta")
    ap.add_argument("--pilot", nargs="+", required=True, help="held-out sequences for the accuracy check")
    ap.add_argument("--out", default="idd_pilot")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--pp-sigma", type=float, default=20.0, help="prior sd (px) of the principal point around the image centre")
    ap.add_argument("--fit-stride", type=int, default=4, help="use every n-th frame for the camera fit")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    global PP_SIGMA
    PP_SIGMA = a.pp_sigma
    logf = open(os.path.join(a.out, "log.txt"), "w")
    def log(s):
        print(s); logf.write(s + "\n"); logf.flush()
    if set(a.fit) & set(a.pilot):
        sys.exit("fit and pilot sequences must be disjoint")

    fit_fr = [f for s in a.fit for f in seq_frames(a.root, s)]
    pil_fr = [f for s in a.pilot for f in seq_frames(a.root, s)]
    log(f"fit frames {len(fit_fr)} from {a.fit}; pilot frames {len(pil_fr)} from {a.pilot}")
    for f in fit_fr + pil_fr:
        f["boxes"] = load_labels(f["label"])
    classes = {}
    for f in fit_fr + pil_fr:
        for o in json.load(open(f["label"])):
            classes[o["obj_type"]] = classes.get(o["obj_type"], 0) + 1
    log("label classes: " + json.dumps(classes))
    detect(fit_fr + pil_fr, os.path.join(a.out, "dets_cache"), a.device)

    cal_path = os.path.join(a.out, "calib_cam3.json")
    if os.path.exists(cal_path):
        cam = Camera(json.load(open(cal_path))["params"]); log("loaded existing calibration")
    else:
        cam = fit_camera(fit_fr[:: a.fit_stride], log)
    # ground and mounting from the fit sequences only
    bottoms = np.array([b["c"][2] - b["size"][2] / 2 for f in fit_fr for b in f["boxes"]
                        if cam.project_box(b) is not None])
    ground_z = float(np.median(bottoms))
    h = float(cam.C[2] - ground_z); yh = float(cam.horizon_row())
    fit_rows = observations(cam, fit_fr, h, yh)
    m = [abs(o["yb"] - o["proj_yb"]) for o in fit_rows if not o["border"]]
    ious = [o["iou"] for o in fit_rows]
    delta = fit_delta(fit_rows, h, yh, cam.f)
    Wg = {g: float(np.median([o["W"] for o in fit_rows if o["group"] == g] or [1.8 if g == "four" else 0.7])) for g in ("four", "two")}
    cal = dict(params=cam.p.tolist(), R=cam.R.tolist(), C=cam.C.tolist(), f=cam.f, u0=cam.u0, v0=cam.v0,
               heading_deg=math.degrees(cam.p[0]), cam_height=h, horizon_row=yh, ground_z_lidar=ground_z,
               delta=delta, width=Wg, fit_sequences=a.fit, fit_matches=len(fit_rows),
               fit_median_iou=float(np.median(ious)) if ious else None,
               fit_bottom_row_err_px_median=float(np.median(m)) if m else None,
               fit_bottom_row_err_px_p90=float(np.percentile(m, 90)) if m else None)
    json.dump(cal, open(cal_path, "w"), indent=1)
    log(f"camera: f={cam.f:.1f} u0={cam.u0:.1f} v0={cam.v0:.1f} heading={cal['heading_deg']:.1f} deg  h={h:.2f} m  y_h={yh:.1f}")
    log(f"fit quality: {len(fit_rows)} matches, median IoU {cal['fit_median_iou']:.3f}, "
        f"bottom-row error median {cal['fit_bottom_row_err_px_median']:.1f} px (p90 {cal['fit_bottom_row_err_px_p90']:.1f})")
    log(f"contact offset delta: {delta}; median widths: {Wg}")

    rows = observations(cam, pil_fr, h, yh)
    import csv
    if rows:
        with open(os.path.join(a.out, "pilot_obs.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    md = [f"# IDD-3D pilot (front camera {CAM})", "",
          f"Fit sequences: {', '.join(a.fit)} ({len(fit_fr)} frames). Pilot (held out): {', '.join(a.pilot)} ({len(pil_fr)} frames).",
          f"Camera fit: f = {cam.f:.1f} px, principal point ({cam.u0:.0f}, {cam.v0:.0f}), height {h:.2f} m, horizon row {yh:.1f}; "
          f"median IoU of projected labels vs detections {cal['fit_median_iou']:.3f}, bottom-row error median "
          f"{cal['fit_bottom_row_err_px_median']:.1f} px (90th pct {cal['fit_bottom_row_err_px_p90']:.1f}).",
          f"Contact offset delta (fit sequences): four-wheel {delta['four']:.2f} m, two-wheel {delta['two']:.2f} m.",
          f"Pilot observations (detections matched to labels, IoU >= 0.5): {len(rows)} "
          f"({sum(o['group'] == 'four' for o in rows)} four-wheel, {sum(o['group'] == 'two' for o in rows)} two-wheel).", "",
          summarise(rows, cam.f, h, yh, delta, Wg) if rows else "no matched observations"]
    open(os.path.join(a.out, "pilot_summary.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    overlays(cam, pil_fr, os.path.join(a.out, "overlays"))
    log("overlays written (green = projected 3D labels, red = YOLO26s, blue line = horizon)")


if __name__ == "__main__":
    main()

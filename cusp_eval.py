#!/usr/bin/env python3
"""
cusp_eval.py  -  Evaluate CUSP on public camera datasets (KITTI-tracking format).

CUSP itself uses the camera only. Dataset 3D labels are used solely as ground
truth for (a) offline calibration of the conformal scores and (b) measuring
coverage and speed-cap safety on held-out sequences.

What it produces (in --out):
  results.json         every number below, machine-readable
  tables.md            paper-ready tables (coverage, cap safety, latency)
  coverage_by_band.csv coverage per method x range band x occlusion
  alpha_trace.csv      adaptive level alpha_t per frame (for the ACI figure)
  *.png                figures, with --plots (needs matplotlib)

Dataset layout (KITTI tracking; other datasets: convert to this layout)
  <root>/image_02/<seq>/<frame:06d>.png      left colour images (needed for --frontend yolo)
  <root>/label_02/<seq>.txt                  frame id type trunc occl alpha x1 y1 x2 y2 h w l X Y Z ry
  <root>/calib/<seq>.txt                     line "P2: 12 numbers"
  <root>/oxts/<seq>.txt                      KITTI OXTS (vf = col 8, af = col 14)
     or <root>/ego/<seq>.txt                 two columns per frame: speed [m/s] accel [m/s^2]

Typical use
  # 1) same-dataset split: calibrate on KITTI 0000-0010, test on 0011-0020
  python cusp_eval.py --calib kitti=/data/kitti/training:0-10 \
                      --test  kitti=/data/kitti/training:11-20 \
                      --frontend yolo --weights yolo26s.pt --out out_kitti --plots
  # 2) cross-dataset shift: calibrate on all KITTI, test on IDD-3D (converted)
  python cusp_eval.py --calib kitti=/data/kitti/training:0-20 \
                      --test  idd3d=/data/idd3d_kittifmt:all --frontend yolo --out out_cross --plots
  # quick check without a detector: ground-truth 2D boxes (+ optional pixel noise)
  python cusp_eval.py --calib kitti=...:0-10 --test kitti=...:11-20 --frontend gt --gt-box-noise 1.5

Detector output is cached per sequence in <out>/cache, so YOLO runs only once.
"""
from __future__ import annotations
import argparse, csv, json, math, os, time
from collections import defaultdict
import numpy as np

from cusp import Camera, Pipeline, Conformal, safe_speed, DecisionCfg, FilterCfg

VEH_TYPES_DEFAULT = ("Car", "Van", "Truck")
COCO_VEHICLES = [2, 3, 5, 7]          # car, motorcycle, bus, truck
BANDS = [(1.0, 10.0), (10.0, 30.0), (30.0, 60.0)]
ZONES = [(0.0, 1.8), (1.8, 5.5), (5.5, 1e9)]          # |X| own lane / adjacent lane / kerbside
ZONE_NAMES = ["own lane", "adjacent", "kerbside"]
Z975 = 1.959964


# ----------------------------------------------------------------------------
# Dataset reading
# ----------------------------------------------------------------------------
def parse_spec(spec: str):
    """'name=root:seqs'  seqs = 'all' | '0-10' | '0,3,5-7'."""
    name, rest = spec.split("=", 1)
    root, seqs = rest.rsplit(":", 1)
    lab_dir = os.path.join(root, "label_02")
    avail = sorted(f[:-4] for f in os.listdir(lab_dir) if f.endswith(".txt"))
    if seqs == "all":
        chosen = avail
    else:
        want = set()
        for part in seqs.split(","):
            if "-" in part:
                a, b = part.split("-"); want.update(range(int(a), int(b) + 1))
            else:
                want.add(int(part))
        chosen = [s for s in avail if s.isdigit() and int(s) in want]
    if not chosen:
        raise SystemExit(f"no sequences matched '{seqs}' in {lab_dir}")
    return name, root, chosen


def read_P2(root, seq):
    for line in open(os.path.join(root, "calib", f"{seq}.txt")):
        p = line.replace(":", " ").split()
        if p and p[0] == "P2":
            return np.array([float(x) for x in p[1:13]]).reshape(3, 4)
    raise ValueError(f"P2 missing in calib/{seq}.txt")


def nearest_depth(X, Y, Z, h, w, l, ry):
    """Depth (camera z) of the nearest bottom corner of a KITTI 3D box. This is the
    point whose image row the 2D box bottom edge measures."""
    xs = np.array([l, l, -l, -l]) / 2.0
    zs = np.array([w, -w, -w, w]) / 2.0
    zc = -math.sin(ry) * xs + math.cos(ry) * zs + Z
    return float(zc.min())


def read_labels(root, seq, veh_types):
    """frame -> list of objects (vehicles); also a list of DontCare boxes per frame."""
    objs, dontcare = defaultdict(list), defaultdict(list)
    for line in open(os.path.join(root, "label_02", f"{seq}.txt")):
        p = line.split()
        if len(p) < 17:
            continue
        fr, tid, typ = int(p[0]), int(p[1]), p[2]
        box = [float(v) for v in p[6:10]]
        if typ == "DontCare":
            dontcare[fr].append(box); continue
        if typ not in veh_types:
            continue
        h, w, l, X, Y, Z, ry = (float(v) for v in p[10:17])
        objs[fr].append(dict(id=tid, trunc=float(p[3]), occl=int(float(p[4])), box=box,
                             X=X, Y=Y, Zc=Z, Zn=nearest_depth(X, Y, Z, h, w, l, ry)))
    return objs, dontcare


def read_ego(root, seq, n_frames):
    """Per-frame ego speed and acceleration."""
    oxts = os.path.join(root, "oxts", f"{seq}.txt")
    ego = os.path.join(root, "ego", f"{seq}.txt")
    if os.path.exists(oxts):
        rows = [list(map(float, l.split())) for l in open(oxts) if l.strip()]
        v = np.array([r[8] for r in rows]); a = np.array([r[14] for r in rows])
    elif os.path.exists(ego):
        rows = [list(map(float, l.split())) for l in open(ego) if l.strip()]
        v = np.array([r[0] for r in rows]); a = np.array([r[1] for r in rows])
    else:
        raise SystemExit(f"no ego motion for {seq}: need oxts/{seq}.txt or ego/{seq}.txt")
    if len(v) < n_frames:
        v = np.pad(v, (0, n_frames - len(v)), mode="edge"); a = np.pad(a, (0, n_frames - len(a)), mode="edge")
    return v, a


def image_size(root, seq, default):
    d = os.path.join(root, "image_02", seq)
    if os.path.isdir(d):
        files = sorted(os.listdir(d))
        if files:
            try:
                from PIL import Image
                with Image.open(os.path.join(d, files[0])) as im:
                    return im.size
            except Exception:
                pass
    return default


# ----------------------------------------------------------------------------
# Front ends: ground-truth boxes or detector + tracker
# ----------------------------------------------------------------------------
def frontend_gt(objs, n_frames, noise_px, rng):
    """Ground-truth 2D boxes and identities, optional Gaussian corner noise."""
    out = []
    for fr in range(n_frames):
        dets = []
        for o in objs.get(fr, []):
            b = np.array(o["box"]) + (rng.normal(0, noise_px, 4) if noise_px > 0 else 0)
            dets.append((o["id"], *map(float, b)))
        out.append(dets)
    return out, None


def corrupt_image(img, kind, sev, seed):
    """Camera degradations applied to the image before detection (test split only)."""
    import cv2
    rng = np.random.default_rng(seed)
    x = img.astype(np.float32) / 255.0
    if kind == "dark":            # low light: gamma + exposure drop + sensor noise
        x = (x ** (1.0 + 1.2 * sev)) * max(0.15, 0.55 - 0.2 * sev)
        x = x + rng.normal(0, 0.02 * sev, x.shape)
    elif kind == "noise":         # sensor noise
        x = x + rng.normal(0, 0.08 * sev, x.shape)
    elif kind == "blur":          # horizontal motion blur
        k = max(3, int(7 * sev) | 1)
        ker = np.zeros((k, k), np.float32); ker[k // 2, :] = 1.0 / k
        x = cv2.filter2D(x, -1, ker)
    elif kind == "rain":          # rain: slanted streaks, veiling glare, defocus, darker scene
        h, w = x.shape[:2]
        streak = np.zeros((h, w), np.float32)
        n = int(1500 * sev * h * w / (1242 * 375))
        ys, xs = rng.integers(0, h, n), rng.integers(0, w, n)
        streak[ys, xs] = rng.uniform(0.5, 1.0, n)
        L = max(9, int(25 * sev)) | 1
        ker = np.zeros((L, L), np.float32)
        for i in range(L):
            ker[i, int(round((L - 1) / 2 + (i - (L - 1) / 2) * 0.25))] = 1.0
        streak = cv2.filter2D(streak, -1, ker / ker.sum()) * 6.0
        x = cv2.GaussianBlur(x, (0, 0), 0.8 * sev)
        x = x * (0.85 - 0.1 * sev) + 0.12 * sev
        x = x + np.clip(streak, 0, 0.6)[:, :, None] * 0.6
    elif kind == "fog":           # contrast loss towards the horizon
        h = x.shape[0]
        t = np.clip(np.linspace(1.0, 0.25, h), 0, 1)[:, None, None] ** (0.6 * sev)
        x = x * t + 0.75 * (1 - t)
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)


def merge_riders(dets, persons):
    """Two-wheeler with rider = motorcycle box united with the person riding it (IDD-3D labels both as one)."""
    out = []
    for tid, x1, y1, x2, y2, cls in dets:
        if cls == 3:
            best = None
            for px1, py1, px2, py2 in persons:
                ov = max(0.0, min(x2, px2) - max(x1, px1)) / max(1e-3, min(x2 - x1, px2 - px1))
                if ov > 0.5 and y1 - 0.2 * (y2 - y1) < py2 < y2 + 0.05 * (y2 - y1) and py1 < y1:
                    if best is None or py1 < best[1]:
                        best = (px1, py1, px2, py2)
            if best is not None:
                x1, y1, x2 = min(x1, best[0]), min(y1, best[1]), max(x2, best[2])
        out.append((tid, x1, y1, x2, y2))
    return out


def frontend_yolo(root, seq, n_frames, weights, cache_dir, conf, device=None, corrupt="none", severity=1.0,
                  riders=False):
    """YOLO + ByteTrack (Ultralytics). Cached as JSON per sequence (and per corruption)."""
    os.makedirs(cache_dir, exist_ok=True)
    tag = os.path.splitext(os.path.basename(weights))[0] + ("_mr" if riders else "")
    if corrupt != "none":
        tag += f"_{corrupt}{severity:g}"
    cpath = os.path.join(cache_dir, f"{os.path.basename(os.path.normpath(root))}_{seq}_{tag}.json")
    if os.path.exists(cpath):
        c = json.load(open(cpath))
        return [[tuple(d) for d in fr] for fr in c["dets"]], c["ms"]
    import cv2
    from ultralytics import YOLO
    model = YOLO(weights)                 # fresh model => fresh tracker state per sequence
    dets_all, ms = [], []
    img_dir = os.path.join(root, "image_02", seq)
    for fr in range(n_frames):
        path = os.path.join(img_dir, f"{fr:06d}.png")
        img = cv2.imread(path)
        if img is None:
            dets_all.append([]); ms.append(None); continue
        if corrupt != "none":
            img = corrupt_image(img, corrupt, severity, seed=int(seq) * 100000 + fr if seq.isdigit() else fr)
        t0 = time.perf_counter()
        r = model.track(img, persist=True, tracker="bytetrack.yaml",
                        classes=COCO_VEHICLES + ([0] if riders else []), conf=conf, device=device, verbose=False)[0]
        dets, persons = [], []
        if r.boxes is not None and r.boxes.id is not None:
            for (x1, y1, x2, y2), tid, c in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.id.cpu().numpy(),
                                                 r.boxes.cls.cpu().numpy()):
                if int(c) == 0:
                    persons.append((float(x1), float(y1), float(x2), float(y2)))
                else:
                    dets.append((int(tid), float(x1), float(y1), float(x2), float(y2), int(c)))
        dets = merge_riders(dets, persons) if riders else [d[:5] for d in dets]
        ms.append((time.perf_counter() - t0) * 1e3)
        dets_all.append(dets)
    json.dump({"dets": dets_all, "ms": ms}, open(cpath, "w"))
    return dets_all, ms


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def match(dets, gts, thr=0.5):
    """Greedy IoU matching; returns {det_track_id: gt_object}."""
    pairs = sorted(((iou(d[1:5], g["box"]), i, j) for i, d in enumerate(dets) for j, g in enumerate(gts)),
                   reverse=True)
    used_d, used_g, out = set(), set(), {}
    for v, i, j in pairs:
        if v < thr:
            break
        if i in used_d or j in used_g:
            continue
        used_d.add(i); used_g.add(j); out[dets[i][0]] = gts[j]
    return out


def occlusion_flags(boxes):
    n = len(boxes); occ = [False] * n
    for i in range(n):
        x1, y1, x2, y2 = boxes[i]
        for j in range(n):
            if j == i:
                continue
            a1, b1, a2, b2 = boxes[j]
            if b2 > y2 and b1 < y2 and min(x2, a2) - max(x1, a1) > 0.2 * (x2 - x1):
                occ[i] = True; break
    return occ


# ----------------------------------------------------------------------------
# Running CUSP over one sequence
# ----------------------------------------------------------------------------
def true_rate(zseries, fr, dt):
    """d ln Z / dt by central difference over +-2 frames (falls back to +-1)."""
    for k in (2, 1):
        a, b = zseries.get(fr - k), zseries.get(fr + k)
        if a and b and a > 0.5 and b > 0.5:
            return (math.log(b) - math.log(a)) / (2 * k * dt)
    return None


class SeqData:
    def __init__(self, name, root, seq, args, rng, corrupt="none"):
        self.name, self.root, self.seq = name, root, seq
        self.objs, self.dontcare = read_labels(root, seq, args.veh_types)
        n_lab = max(self.objs) + 1 if self.objs else 0
        img_dir = os.path.join(root, "image_02", seq)
        n_img = len(os.listdir(img_dir)) if os.path.isdir(img_dir) else 0
        self.n = max(n_lab, n_img)
        self.P2 = read_P2(root, seq)
        self.v, self.a = read_ego(root, seq, self.n)
        self.W, self.H = image_size(root, seq, tuple(args.img_size))
        if args.frontend == "gt":
            self.dets, self.ms = frontend_gt(self.objs, self.n, args.gt_box_noise, rng)
        else:
            self.dets, self.ms = frontend_yolo(root, seq, self.n, args.weights,
                                               args.cache_dir or os.path.join(args.out, "cache"), args.det_conf, args.device,
                                               corrupt, args.severity, args.merge_riders)
        self.zs = defaultdict(dict)          # gt id -> frame -> nearest depth
        for fr, lst in self.objs.items():
            for o in lst:
                self.zs[o["id"]][fr] = o["Zn"]


def matched_pairs(sd, args):
    """Yield (frame, detection, gt) for detections matched to ground truth."""
    for fr in range(sd.n):
        dets, gts = sd.dets[fr], sd.objs.get(fr, [])
        if args.frontend == "gt":
            by_id = {o["id"]: o for o in gts}
            for d in dets:
                if d[0] in by_id:
                    yield fr, d, by_id[d[0]]
        else:
            byid = {d[0]: d for d in dets}
            for tid, g in match(dets, gts, args.match_iou).items():
                yield fr, byid[tid], g


def mounting(seqs, args):
    """One-off mounting calibration from labelled frames, using the SAME front end
    as at run time. Model for the box bottom row of a vehicle seen from behind:

        y_b = y_h + f h / (Z + delta)

    y_h horizon row, h camera height, Z true range to the vehicle's nearest face,
    delta = contact offset: the box bottom is where the tyres meet the road, which
    lies about one rear overhang beyond the nearest face. Only vehicles in the own
    and adjacent lanes (seen from behind) are used. Fitted by grid search on
    delta with robust least squares on (y_h, h)."""
    f = seqs[0].P2[0, 0]; cy = seqs[0].P2[1, 2]
    ys, zs = [], []
    for sd in seqs:
        for fr, d, g in matched_pairs(sd, args):
            x1, y1, x2, y2 = d[1:5]
            if (g["occl"] == 0 and g["trunc"] < 0.05 and 3.0 < g["Zn"] < 50.0 and abs(g["X"]) < 5.5
                    and y2 < sd.H - 2 and x1 > 2 and x2 < sd.W - 2):
                ys.append(y2); zs.append(g["Zn"])
    if len(ys) < 30:
        return dict(h=args.cam_height or 1.65, yh=cy, delta=0.0, n=len(ys), resid_px=float("nan"))
    y, Z = np.array(ys), np.array(zs)
    best = None
    grid = np.arange(0.0, 2.0001, 0.05) if not args.no_contact_offset else [0.0]
    for dlt in grid:
        g = f / (Z + dlt)
        if args.cam_height:
            h = args.cam_height; yh = float(np.median(y - h * g))
        else:
            A = np.c_[np.ones_like(g), g]; keep = np.ones(len(g), bool)
            for _ in range(3):
                sol = np.linalg.lstsq(A[keep], y[keep], rcond=None)[0]
                r = y - A @ sol
                mad = 1.4826 * np.median(np.abs(r[keep] - np.median(r[keep]))) + 1e-9
                keep = np.abs(r) < 3 * mad
            yh, h = float(sol[0]), float(sol[1])
        cost = float(np.median(np.abs(y - yh - h * g)))
        if best is None or cost < best["resid_px"]:
            best = dict(h=h, yh=yh, delta=float(dlt), n=len(ys), resid_px=cost)
    return best


def band_of(z):
    return next((i for i, (a, b) in enumerate(BANDS) if a <= z < b), len(BANDS) - 1 if z >= BANDS[-1][0] else 0)


def zone_of(x):
    return next(i for i, (a, b) in enumerate(ZONES) if a <= abs(x) < b)


def run_sequence(sd, mnt, cal, args, collect_scores):
    """Run the filter over one sequence. The filter tracks the contact range
    Zc = Z + delta; bounds on Z follow as Zc_lo - delta."""
    P2 = sd.P2
    f, cx = P2[0, 0], P2[0, 2]
    cam = Camera(f=f, h=mnt["h"])
    y_h, delta = mnt["yh"], mnt["delta"]
    dt = 1.0 / args.fps
    method = "CUSP (full)" if cal is not None else "Gaussian-KF"
    pipe = Pipeline(method, cal, cam=cam, alpha=args.alpha)
    recs, scores, alphas, cusp_ms = [], dict(s=[], sd=[], nu=[], band=[], zone=[]), [], []
    for fr in range(sd.n):
        dets = sd.dets[fr]
        gts = sd.objs.get(fr, [])
        boxes = [d[1:5] for d in dets]
        occ = occlusion_flags(boxes)
        obs = {}
        for (tid, x1, y1, x2, y2), oc in zip(dets, occ):
            side_cut = x1 <= 2 or x2 >= sd.W - 2
            bottom_cut = y2 >= sd.H - 2
            dy = None if bottom_cut else (y2 - y_h)
            if dy is not None and dy <= 2.0:
                continue
            obs[tid] = (dy, x2 - x1, 0.5 * (x1 + x2) - cx, bool(oc or side_cut))
        t0 = time.perf_counter()
        pipe.perceive(obs, float(sd.a[fr]), dt, float(sd.v[fr]))
        cusp_ms.append((time.perf_counter() - t0) * 1e3)
        if cal is not None:
            alphas.append(pipe.conf.alpha_t)
        if args.frontend == "gt":
            gt_by_id = {o["id"]: o for o in gts}
            m = {tid: gt_by_id.get(tid) for tid in obs}
        else:
            m = match(dets, gts, args.match_iou)
        for tid, g in m.items():
            if g is None or tid not in pipe.tracks:
                continue
            lf, xf = pipe.tracks[tid]
            if lf.age < 5 or not (1.0 < g["Zn"] <= 60.0):
                continue
            zc = {k: v + delta for k, v in sd.zs[g["id"]].items()}
            sdot_t = true_rate(zc, fr, dt)
            z_hat = max(math.exp(lf.x[0]) - delta, 0.1)
            rec = dict(seq=sd.seq, fr=fr, Z=g["Zn"], Zc=g["Zn"] + delta, X=g["X"], sdot=sdot_t,
                       occl=g["occl"], s_hat=float(lf.x[0]), sd_hat=float(lf.x[1]),
                       sig_s=lf.sig_s, sig_sd=lf.sig_sd, v_e=float(sd.v[fr]), nu=lf.last_nu,
                       band=band_of(g["Zn"]), band_hat=band_of(z_hat),
                       zone=zone_of(g["X"]), zone_hat=zone_of(float(xf.x[0])),
                       alpha_t=pipe.conf.alpha_t if cal is not None else args.alpha)
            recs.append(rec)
            if collect_scores and sdot_t is not None and fr % args.subsample == 0:
                scores["s"].append((rec["s_hat"] - math.log(rec["Zc"])) / rec["sig_s"])
                scores["sd"].append((rec["sd_hat"] - sdot_t) / rec["sig_sd"])
                scores["nu"].append(abs(lf.last_nu) if lf.last_nu is not None else 0.0)
                scores["band"].append(rec["band_hat"])
                scores["zone"].append(rec["zone_hat"])
    return recs, scores, alphas, cusp_ms


# ----------------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------------
METHODS = ("Point-KF", "Gaussian-KF", "Split-CP", "CUSP", "Split-CP (group)", "CUSP (group)")


def qtile(sorted_scores, level):
    return max(0.0, Conformal._q(sorted_scores, level))


def mults(rec, m, cal, alpha):
    if m == "Point-KF":
        return 0.0, 0.0
    if m == "Gaussian-KF":
        return Z975, Z975
    a = alpha if m.startswith("Split") else rec["alpha_t"]
    src = cal["group"][(rec["zone_hat"], rec["band_hat"])] if m.endswith("(group)") else cal["w"]
    return qtile(src["s"], 1 - a / 2), qtile(src["sd"], 1 - a / 2)


def evaluate(recs, cal, args):
    dcfg = DecisionCfg()
    out = {}
    rows_band = []
    off = args.cam_to_front + dcfg.d0
    for m in METHODS:
        acc = defaultdict(lambda: [0, 0, 0, 0, 0.0])   # key -> [n_s, cov_s, n_v, cov_v, margin_sum]
        cap = dict(n=0, unsafe=0, slack=0.0, slack_rel=0.0)
        for r in recs:
            qs, qv = mults(r, m, cal, args.alpha)
            s_lo = r["s_hat"] - qs * r["sig_s"]
            sd_lo = r["sd_hat"] - qv * r["sig_sd"]
            z_hat = max(math.exp(r["s_hat"]) - args.delta, 0.5)
            z_lo = math.exp(s_lo) - args.delta
            corridor = abs(r["X"]) < args.half_w
            keys = [("all",), ("corridor",) if corridor else None, ("band", r["band"]), ("occl", int(r["occl"] > 0)),
                    ("zone", r["zone"]), ("cband", r["band"]) if corridor else None]
            cov_s = z_lo <= r["Z"]
            cov_v = (sd_lo <= r["sdot"]) if r["sdot"] is not None else None
            for k in keys:
                if k is None:
                    continue
                a = acc[k]
                a[0] += 1; a[1] += cov_s; a[4] += max(0.0, 1.0 - z_lo / z_hat)
                if cov_v is not None:
                    a[2] += 1; a[3] += cov_v
            # per-vehicle speed-cap safety for in-corridor vehicles with a known true rate
            if corridor and r["sdot"] is not None:
                v_l_lo = max(0.0, r["v_e"] + sd_lo * math.exp(r["s_hat"]))
                v_l_true = max(0.0, r["v_e"] + r["sdot"] * r["Zc"])
                v_hat = safe_speed(z_lo - off, v_l_lo, dcfg)
                v_true = safe_speed(r["Z"] - off, v_l_true, dcfg)
                cap["n"] += 1
                cap["unsafe"] += v_hat > v_true + 1e-6
                cap["slack"] += max(0.0, v_true - v_hat)
                cap["slack_rel"] += max(0.0, v_true - v_hat) / max(v_true, 0.5)

        def pct(a, b):
            return 100.0 * b / a if a else float("nan")
        res = {}
        for k, a in acc.items():
            name = "_".join(str(x) for x in k)
            res[name] = dict(n=a[0], cov_range=pct(a[0], a[1]), n_rate=a[2], cov_rate=pct(a[2], a[3]),
                             margin_pct=100.0 * a[4] / a[0] if a[0] else float("nan"))
            if k[0] in ("band", "occl", "zone", "cband"):
                rows_band.append([m, name, a[0], res[name]["cov_range"], res[name]["cov_rate"], res[name]["margin_pct"]])
        res["cap"] = dict(n=cap["n"], unsafe_pct=pct(cap["n"], cap["unsafe"]),
                          mean_slack_mps=cap["slack"] / cap["n"] if cap["n"] else float("nan"),
                          mean_slack_rel_pct=100 * cap["slack_rel"] / cap["n"] if cap["n"] else float("nan"))
        out[m] = res
    return out, rows_band


def fmt(x, d=1):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def tables_md(res, info):
    L = [f"# CUSP real-data evaluation\n",
         f"Calibration: {info['calib']}  \nTest: {info['test']}  \nFront end: {info['frontend']}  \n"
         f"Target coverage per bound: {100 * (1 - info['alpha'] / 2):.1f}%  \n"
         f"Calibration scores: {info['n_cal']}; test observations: {info['n_test']}\n"]
    L.append("\n## Table A. Coverage (%) and relative range margin (%)\n")
    L.append("| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for m in METHODS:
        a, c = res[m].get("all", {}), res[m].get("corridor", {})
        L.append(f"| {m} | {fmt(a.get('cov_range'))} | {fmt(a.get('cov_rate'))} | {fmt(c.get('cov_range'))} | "
                 f"{fmt(c.get('cov_rate'))} | {fmt(a.get('margin_pct'))} |")
    L.append("\n## Table B. Range coverage (%) by distance band and occlusion\n")
    hdr = [f"{int(a)}-{int(b)} m" for a, b in BANDS] + ["not occluded", "occluded"]
    L.append("| Method | " + " | ".join(hdr) + " |")
    L.append("| --- " * (len(hdr) + 1) + "|")
    for m in METHODS:
        cells = [fmt(res[m].get(f"band_{i}", {}).get("cov_range")) for i in range(len(BANDS))]
        cells += [fmt(res[m].get(f"occl_{i}", {}).get("cov_range")) for i in (0, 1)]
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone\n")
    hdr = [f"own lane {int(a)}-{int(b)} m" for a, b in BANDS] + ZONE_NAMES
    L.append("| Method | " + " | ".join(hdr) + " |")
    L.append("| --- " * (len(hdr) + 1) + "|")
    for m in METHODS:
        cells = [fmt(res[m].get(f"cband_{i}", {}).get("cov_range")) for i in range(len(BANDS))]
        cells += [fmt(res[m].get(f"zone_{i}", {}).get("cov_range")) for i in range(len(ZONES))]
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n| Method | " + " | ".join(f"margin, {h}" for h in hdr) + " |")
    L.append("| --- " * (len(hdr) + 1) + "|")
    for m in METHODS:
        cells = [fmt(res[m].get(f"cband_{i}", {}).get("margin_pct")) for i in range(len(BANDS))]
        cells += [fmt(res[m].get(f"zone_{i}", {}).get("margin_pct")) for i in range(len(ZONES))]
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)\n")
    L.append("Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. "
             "Slack = how much lower the estimated cap is than the true cap (cost of caution).\n")
    L.append("| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |")
    L.append("| --- | --- | --- | --- | --- |")
    for m in METHODS:
        c = res[m]["cap"]
        L.append(f"| {m} | {c['n']} | {fmt(c['unsafe_pct'], 2)} | {fmt(c['mean_slack_mps'], 2)} | {fmt(c['mean_slack_rel_pct'])} |")
    L.append("\n## Table D. Latency per frame (ms)\n")
    L.append("| Stage | Mean | 99th percentile |")
    L.append("| --- | --- | --- |")
    for k, v in info["latency"].items():
        L.append(f"| {k} | {fmt(v['mean'], 2)} | {fmt(v['p99'], 2)} |")
    L.append(f"\nAdaptive level alpha_t on test: mean {fmt(info['alpha_mean'], 3)}, "
             f"min {fmt(info['alpha_min'], 3)}, max {fmt(info['alpha_max'], 3)}.  \n"
             f"Mounting calibration (test camera): height {info['mount_test']['h']:.3f} m, horizon row "
             f"{info['mount_test']['yh']:.1f} px, contact offset {info['mount_test']['delta']:.2f} m "
             f"(median residual {info['mount_test']['resid_px']:.2f} px, n={info['mount_test']['n']}).  \n"
             f"Calibration scores per group (lateral zone x range): {info['band_scores']}.  \n"
             f"Test-image corruption: {info['corrupt']}.")
    return "\n".join(L) + "\n"


def make_plots(res, rows_band, alpha_rows, out):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plots"); return
    # coverage by band
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    w = 0.2
    for i, m in enumerate(("Gaussian-KF", "CUSP", "CUSP (group)")):
        vals = [res[m].get(f"band_{b}", {}).get("cov_range", np.nan) for b in range(len(BANDS))]
        ax.bar(np.arange(len(BANDS)) + (i - 1) * w, vals, w, label=m)
    ax.axhline(97.5, ls="--", lw=1, color="k")
    ax.set_xticks(range(len(BANDS))); ax.set_xticklabels([f"{int(a)}-{int(b)} m" for a, b in BANDS])
    ax.set_ylabel("Range coverage (%)"); ax.set_ylim(80, 100); ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out, "coverage_by_band.png"), dpi=200); plt.close(fig)
    # alpha trace
    if alpha_rows:
        fig, ax = plt.subplots(figsize=(6.5, 2.6))
        t = np.arange(len(alpha_rows)); a = [r[2] for r in alpha_rows]
        ax.plot(t, a, lw=1)
        ax.set_xlabel("Test frame (sequences concatenated)"); ax.set_ylabel(r"$\alpha_t$")
        fig.tight_layout(); fig.savefig(os.path.join(out, "alpha_trace.png"), dpi=200); plt.close(fig)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calib", action="append", required=True, help="name=root:seqs (repeatable)")
    ap.add_argument("--test", action="append", required=True, help="name=root:seqs (repeatable)")
    ap.add_argument("--frontend", choices=("gt", "yolo"), default="yolo")
    ap.add_argument("--weights", default="yolo26s.pt")
    ap.add_argument("--det-conf", type=float, default=0.25)
    ap.add_argument("--device", default=None, help="YOLO device: cpu, mps (Apple GPU), 0 (CUDA)")
    ap.add_argument("--gt-box-noise", type=float, default=0.0, help="px noise on GT boxes (--frontend gt)")
    ap.add_argument("--match-iou", type=float, default=0.5)
    ap.add_argument("--veh-types", nargs="+", default=list(VEH_TYPES_DEFAULT))
    ap.add_argument("--fps", type=float, default=10.0, help="KITTI tracking is 10 Hz")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--subsample", type=int, default=2, help="keep every k-th frame for calibration scores")
    ap.add_argument("--half-w", type=float, default=1.8, help="corridor half width [m]")
    ap.add_argument("--cam-to-front", type=float, default=0.0,
                    help="camera-to-front-bumper distance [m] subtracted from range in the speed law")
    ap.add_argument("--cam-height", type=float, default=None, help="known camera height [m] (KITTI: 1.65); else fitted")
    ap.add_argument("--no-contact-offset", action="store_true", help="ablation: force contact offset delta = 0")
    ap.add_argument("--min-group-scores", type=int, default=150,
                    help="fewer calibration scores in a zone x band group => fall back to zone, then global")
    ap.add_argument("--corrupt", choices=("none", "dark", "noise", "blur", "fog", "rain"), default="none",
                    help="degrade TEST images (calibration stays clean) to create a real camera shift")
    ap.add_argument("--severity", type=float, default=1.0, help="corruption strength, 0.5-2")
    ap.add_argument("--cache-dir", default=None, help="shared detection cache (default <out>/cache)")
    ap.add_argument("--merge-riders", action="store_true",
                    help="IDD-3D: unite each motorcycle box with its rider (labels cover vehicle + rider)")
    ap.add_argument("--img-size", type=int, nargs=2, default=[1242, 375])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="cusp_eval_out")
    ap.add_argument("--plots", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    def load(specs, corrupt="none"):
        seqs = []
        for spec in specs:
            name, root, chosen = parse_spec(spec)
            for s in chosen:
                print(f"  loading {name}/{s}" + (f" [{corrupt} x{args.severity}]" if corrupt != "none" else ""), flush=True)
                seqs.append(SeqData(name, root, s, args, rng, corrupt))
        return seqs

    if args.corrupt != "none" and args.frontend != "yolo":
        raise SystemExit("--corrupt needs --frontend yolo (it degrades images before detection)")
    print("calibration sequences:"); cal_seqs = load(args.calib)
    print("test sequences:"); test_seqs = load(args.test, args.corrupt)

    # --- mounting calibration (once per camera). Same dataset => reuse calibration-split mounting.
    mnt_c = mounting(cal_seqs, args)
    same_cam = {sd.name for sd in test_seqs} <= {sd.name for sd in cal_seqs}
    mnt_t = mnt_c if same_cam else mounting(test_seqs, args)
    print(f"mounting (calib): h={mnt_c['h']:.3f} m  y_h={mnt_c['yh']:.1f}px  delta={mnt_c['delta']:.2f} m  "
          f"resid={mnt_c['resid_px']:.2f}px  n={mnt_c['n']}")
    if not same_cam:
        print(f"mounting (test camera, fitted on test labels): h={mnt_t['h']:.3f} m  y_h={mnt_t['yh']:.1f}px  "
              f"delta={mnt_t['delta']:.2f} m")

    # --- offline calibration
    S = dict(s=[], sd=[], nu=[], band=[], zone=[])
    for sd in cal_seqs:
        _, sc, _, _ = run_sequence(sd, mnt_c, None, args, collect_scores=True)
        for k in S:
            S[k] += sc[k]
    n_cal = len(S["s"])
    if n_cal < 200:
        raise SystemExit(f"only {n_cal} calibration scores; add calibration sequences")
    arr = {k: np.array(v) for k, v in S.items()}
    cal = {"w": {k: np.sort(arr[k]) for k in ("s", "sd", "nu")}, "group": {}}
    group_n, group_src = {}, {}
    for z in range(len(ZONES)):
        zsel = arr["zone"] == z
        for b in range(len(BANDS)):
            sel = zsel & (arr["band"] == b)
            if sel.sum() >= args.min_group_scores:
                use, src = sel, "zone x band"
            elif zsel.sum() >= args.min_group_scores:
                use, src = zsel, "zone"
            else:
                use, src = np.ones(len(arr["s"]), bool), "global"
            cal["group"][(z, b)] = {k: np.sort(arr[k][use]) for k in ("s", "sd")}
            group_n[f"{ZONE_NAMES[z]} {int(BANDS[b][0])}-{int(BANDS[b][1])} m"] = int(sel.sum())
            group_src[f"{ZONE_NAMES[z]} {int(BANDS[b][0])}-{int(BANDS[b][1])} m"] = src
    band_n = group_n
    np.savez(os.path.join(args.out, "cal_scores.npz"), **cal["w"])
    print(f"calibration scores: {n_cal}  groups: {group_n}")
    print(f"group fallback: {group_src}")
    print(f"global q_s(97.5%)={np.quantile(cal['w']['s'], .975):.2f} "
          f"q_v(97.5%)={np.quantile(cal['w']['sd'], .975):.2f} q_nu(95%)={np.quantile(cal['w']['nu'], .95):.2f}")
    args.delta = mnt_t["delta"]

    # --- test
    recs, alpha_rows, cusp_ms, det_ms = [], [], [], []
    for sd in test_seqs:
        r, _, al, ms = run_sequence(sd, mnt_t, cal, args, collect_scores=False)
        recs += r; cusp_ms += ms
        alpha_rows += [(sd.name, sd.seq, a) for a in al]
        if sd.ms:
            det_ms += [x for x in sd.ms if x is not None]
    if not recs:
        raise SystemExit("no matched test observations")
    res, rows_band = evaluate(recs, cal, args)

    def lat(x):
        x = np.array(x) if x else np.array([np.nan])
        return dict(mean=float(np.nanmean(x)), p99=float(np.nanpercentile(x, 99)))
    latency = {"CUSP module": lat(cusp_ms)}
    if det_ms:
        latency["Detector + tracker"] = lat(det_ms)
        latency["End to end"] = lat([a + b for a, b in zip(det_ms, cusp_ms)])
    alphas = np.array([a for *_, a in alpha_rows])
    info = dict(calib=args.calib, test=args.test, frontend=args.frontend + (f" ({args.weights})" if args.frontend == "yolo" else f" (noise {args.gt_box_noise} px)"),
                alpha=args.alpha, n_cal=n_cal, n_test=len(recs), latency=latency,
                alpha_mean=float(alphas.mean()), alpha_min=float(alphas.min()), alpha_max=float(alphas.max()),
                mount_calib=mnt_c, mount_test=mnt_t, same_camera=same_cam, band_scores=band_n,
                group_source=group_src, corrupt=f"{args.corrupt} x{args.severity}" if args.corrupt != "none" else "none",
                cal_quantiles=dict(q_s_975=float(np.quantile(cal["w"]["s"], .975)),
                                   q_v_975=float(np.quantile(cal["w"]["sd"], .975)),
                                   q_nu_95=float(np.quantile(cal["w"]["nu"], .95))))

    json.dump(dict(info=info, results=res), open(os.path.join(args.out, "results.json"), "w"), indent=1, default=float)
    md = tables_md(res, info)
    open(os.path.join(args.out, "tables.md"), "w").write(md)
    with open(os.path.join(args.out, "coverage_by_band.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["method", "group", "n", "cov_range", "cov_rate", "margin_pct"]); w.writerows(rows_band)
    with open(os.path.join(args.out, "alpha_trace.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["dataset", "seq", "alpha_t"]); w.writerows(alpha_rows)
    if args.plots:
        make_plots(res, rows_band, alpha_rows, args.out)
    print(md)


if __name__ == "__main__":
    main()

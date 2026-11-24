"""Learned-depth baseline: Depth Anything V2 (metric, outdoor) on the same detections as CUSP.

For every detection matched to a labelled vehicle, the range is read from the DAv2 metric depth map
(median depth in the lower-central part of the box); the closing rate is a causal finite difference of
log range along the detection track. Two variants are scored with the SAME metrics as cusp_eval.py:
  * "DAv2 (point)"        - raw estimates, no bound
  * "DAv2 + Split-CP"     - one-sided split-conformal bounds on log range and rate (alpha/2 each),
                            calibrated on the calibration split.
Detections come from the shared YOLO26s + ByteTrack cache written by cusp_eval.py (run that first).

Usage (Mac, project venv):
  pip install transformers
  python dav2_baseline.py --calib idd=$K/calibration:all --test idd=$K/validation:all \
      --cache-dir out_idd_cache --merge-riders --veh-types Car Auto Truck Bus Motorcycle --out out_idd_val_dav2
"""
import argparse, json, math, os, time
from collections import defaultdict
import numpy as np
import cusp_eval as E
from cusp import safe_speed, DecisionCfg

MODEL_ID = "depth-anything/Depth-Anything-V2-Metric-Outdoor-Small-hf"


class DepthModel:
    def __init__(self, model_id, device):
        import torch
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        self.torch = torch
        self.proc = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForDepthEstimation.from_pretrained(model_id).to(device).eval()
        self.device = device

    def __call__(self, bgr):
        import cv2
        torch = self.torch
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        inp = self.proc(images=rgb, return_tensors="pt").to(self.device)
        with torch.no_grad():
            d = self.model(**inp).predicted_depth            # 1 x h x w, metres
        d = torch.nn.functional.interpolate(d[:, None], size=rgb.shape[:2], mode="bilinear", align_corners=False)
        return d[0, 0].float().cpu().numpy()


def box_depth(depth, box):
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    h, w = depth.shape
    x1, x2 = max(0, x1), min(w - 1, x2); y1, y2 = max(0, y1), min(h - 1, y2)
    if x2 - x1 < 3 or y2 - y1 < 3:
        return None
    cx1, cx2 = x1 + (x2 - x1) // 4, x2 - (x2 - x1) // 4             # central half of the width
    cy1 = y1 + (y2 - y1) // 2                                       # lower half of the box
    patch = depth[cy1:y2, cx1:cx2]
    return float(np.median(patch)) if patch.size else None


def seq_depths(sd, args, model, corrupt):
    """{frame: {track_id: depth}} for frames that contain a matched detection; cached per sequence."""
    import cv2
    tag = f"{os.path.basename(os.path.normpath(sd.root))}_{sd.seq}_dav2" + (f"_{corrupt}{args.severity:g}" if corrupt != "none" else "")
    cp = os.path.join(args.cache_dir, tag + ".json")
    if os.path.exists(cp):
        c = json.load(open(cp))
        return {int(k): {int(t): v for t, v in d.items()} for k, d in c["d"].items()}, c["ms"]
    out, ms = {}, []
    for fr in range(sd.n):
        dets = sd.dets[fr]
        if not dets:
            continue
        img = cv2.imread(os.path.join(sd.root, "image_02", sd.seq, f"{fr:06d}.png"))
        if img is None:
            continue
        if corrupt != "none":
            img = E.corrupt_image(img, corrupt, args.severity, seed=int(sd.seq) * 100000 + fr if sd.seq.isdigit() else fr)
        t0 = time.perf_counter(); dep = model(img); ms.append((time.perf_counter() - t0) * 1e3)
        out[fr] = {d[0]: box_depth(dep, d[1:5]) for d in dets}
    json.dump({"d": {str(k): {str(t): v for t, v in d.items()} for k, d in out.items()}, "ms": ms}, open(cp, "w"))
    return out, ms


def records(sd, dep, args):
    dt = 1.0 / args.fps
    hist = defaultdict(dict)                     # track id -> frame -> log depth
    for fr, dd in dep.items():
        for t, z in dd.items():
            if z and z > 0.3:
                hist[t][fr] = math.log(z)
    recs = []
    for fr, d, g in E.matched_pairs(sd, args):
        t = d[0]; h = hist.get(t, {})
        if fr not in h or not (1.0 < g["Zn"] <= 60.0):
            continue
        if sum(1 for k in range(fr - 6, fr) if k in h) < 4:             # same maturity rule as CUSP (age >= 5)
            continue
        rate = None
        for k in (4, 2):                                                # causal difference
            if fr - k in h:
                rate = (h[fr] - h[fr - k]) / (k * dt); break
        if rate is None:
            continue
        zc = {k: v for k, v in sd.zs[g["id"]].items()}
        recs.append(dict(seq=sd.seq, fr=fr, Z=g["Zn"], X=g["X"], occl=g["occl"], ls=h[fr], rate=rate,
                         sdot=E.true_rate(zc, fr, dt), v_e=float(sd.v[fr]), band=E.band_of(g["Zn"]),
                         zone=E.zone_of(g["X"])))
    return recs


def conformal_q(scores, level):
    s = np.sort(np.asarray(scores)); n = len(s)
    k = min(n - 1, max(0, math.ceil((n + 1) * level) - 1))
    return float(s[k])


def evaluate(recs, qs, qv, args):
    dcfg = DecisionCfg(); off = args.cam_to_front + dcfg.d0
    acc = defaultdict(lambda: [0, 0, 0, 0, 0.0]); cap = dict(n=0, unsafe=0, slack_rel=0.0)
    for r in recs:
        z_hat = math.exp(r["ls"]); z_lo = z_hat * math.exp(-qs); sd_lo = r["rate"] - qv
        corridor = abs(r["X"]) < args.half_w
        cov_s = z_lo <= r["Z"]; cov_v = (sd_lo <= r["sdot"]) if r["sdot"] is not None else None
        for k in [("all",), ("corridor",) if corridor else None, ("band", r["band"]), ("occl", int(r["occl"] > 0)),
                  ("zone", r["zone"]), ("cband", r["band"]) if corridor else None]:
            if k is None:
                continue
            a = acc[k]; a[0] += 1; a[1] += cov_s; a[4] += max(0.0, 1 - z_lo / z_hat)
            if cov_v is not None:
                a[2] += 1; a[3] += cov_v
        if corridor and r["sdot"] is not None:
            v_hat = safe_speed(z_lo - off, max(0.0, r["v_e"] + sd_lo * z_hat), dcfg)
            v_true = safe_speed(r["Z"] - off, max(0.0, r["v_e"] + r["sdot"] * r["Z"]), dcfg)
            cap["n"] += 1; cap["unsafe"] += v_hat > v_true + 1e-6
            cap["slack_rel"] += max(0.0, v_true - v_hat) / max(v_true, 0.5)
    pct = lambda a, b: 100.0 * b / a if a else float("nan")
    res = {"_".join(map(str, k)): dict(n=a[0], cov_range=pct(a[0], a[1]), n_rate=a[2], cov_rate=pct(a[2], a[3]),
                                       margin_pct=100 * a[4] / a[0] if a[0] else float("nan")) for k, a in acc.items()}
    res["cap"] = dict(n=cap["n"], unsafe_pct=pct(cap["n"], cap["unsafe"]),
                      mean_slack_rel_pct=100 * cap["slack_rel"] / cap["n"] if cap["n"] else float("nan"))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calib", action="append", required=True)
    ap.add_argument("--test", action="append", required=True)
    ap.add_argument("--cache-dir", default="out_idd_cache")
    ap.add_argument("--weights", default="yolo26s.pt")
    ap.add_argument("--det-conf", type=float, default=0.25)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--merge-riders", action="store_true")
    ap.add_argument("--veh-types", nargs="+", default=["Car", "Auto", "Truck", "Bus", "Motorcycle"])
    ap.add_argument("--match-iou", type=float, default=0.5)
    ap.add_argument("--fps", type=float, default=10.0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--subsample", type=int, default=2)
    ap.add_argument("--half-w", type=float, default=1.8)
    ap.add_argument("--cam-to-front", type=float, default=0.0)
    ap.add_argument("--corrupt", default="none")
    ap.add_argument("--severity", type=float, default=1.0)
    ap.add_argument("--img-size", type=int, nargs=2, default=[1440, 1080])
    ap.add_argument("--model", default=MODEL_ID)
    ap.add_argument("--out", default="out_dav2")
    a = ap.parse_args()
    a.frontend, a.gt_box_noise, a.out_cache = "yolo", 0.0, a.cache_dir
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.cache_dir, exist_ok=True)
    model = None

    def load(specs, corrupt):
        nonlocal model
        allr, ms = [], []
        for spec in specs:
            name, root, chosen = E.parse_spec(spec)
            for s in chosen:
                print(f"  {name}/{s}" + (f" [{corrupt}]" if corrupt != "none" else ""), flush=True)
                b = argparse.Namespace(**vars(a)); b.out = a.out
                sd = E.SeqData(name, root, s, b, np.random.default_rng(0), corrupt)
                tag = os.path.join(a.cache_dir, f"{os.path.basename(os.path.normpath(root))}_{s}_dav2"
                                   + (f"_{corrupt}{a.severity:g}" if corrupt != "none" else "") + ".json")
                if model is None and not os.path.exists(tag):
                    model = DepthModel(a.model, a.device)
                dep, m = seq_depths(sd, a, model, corrupt)
                allr += records(sd, dep, a); ms += m
        return allr, ms

    print("calibration:"); cal, _ = load(a.calib, "none")
    sub = [r for r in cal if r["fr"] % a.subsample == 0 and r["sdot"] is not None]
    s_scores = [r["ls"] - math.log(r["Z"]) for r in sub]          # >0: range over-estimated (unsafe)
    v_scores = [r["rate"] - r["sdot"] for r in sub]                # >0: closing under-estimated (unsafe)
    qs, qv = conformal_q(s_scores, 1 - a.alpha / 2), conformal_q(v_scores, 1 - a.alpha / 2)
    print(f"calibration scores {len(sub)}; q_s={qs:.3f} (log range), q_v={qv:.3f} 1/s")
    print("test:"); test, ms = load(a.test, a.corrupt)
    res = {"DAv2 (point)": evaluate(test, 0.0, 0.0, a), "DAv2 + Split-CP": evaluate(test, qs, qv, a)}
    lat = dict(mean=float(np.mean(ms)) if ms else None, p99=float(np.percentile(ms, 99)) if ms else None)
    info = dict(calib=a.calib, test=a.test, model=a.model, n_cal=len(sub), n_test=len(test), q_s=qs, q_v=qv,
                corrupt=a.corrupt, severity=a.severity, dav2_ms=lat)
    json.dump(dict(info=info, results=res), open(os.path.join(a.out, "results.json"), "w"), indent=1)
    lines = [f"# DAv2 baseline ({a.model})", "", f"calibration scores {len(sub)}, test observations {len(test)}, "
             f"q_s={qs:.3f}, q_v={qv:.3f}; DAv2 time per frame {lat['mean']} ms (p99 {lat['p99']})", "",
             "| Method | Range cov. | Rate cov. | Range cov. corridor | Margin | Unsafe caps | Speed given up |",
             "|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        c = r.get("corridor", {})
        lines.append(f"| {m} | {r['all']['cov_range']:.1f} | {r['all']['cov_rate']:.1f} | {c.get('cov_range', float('nan')):.1f} | "
                     f"{r['all']['margin_pct']:.1f} | {r['cap']['unsafe_pct']:.1f} | {r['cap']['mean_slack_rel_pct']:.1f} |")
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

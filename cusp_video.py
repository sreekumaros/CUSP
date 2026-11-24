#!/usr/bin/env python3
"""
CUSP on real video: detector + tracker front end for the modules in cusp.py.

STATUS: integration template. It was syntax-checked but NOT executed against
video in the authors' environment (no model weights or footage were available
when it was written). Verify the Ultralytics calls against the version you
install, and validate on labelled data before reporting any numbers.

Requires:  pip install ultralytics opencv-python numpy
Example:
  python cusp.py --save-cal cal.npz --quick          # or build cal.npz from LiDAR-labelled data
  python cusp_video.py --video drive.mp4 --weights yolo26s.pt --cal cal.npz \
      --focal 1000 --cam-height 1.30 --horizon-row 360 --speed-csv speed.csv

speed.csv: one ego speed [m/s] per frame (from CAN/GPS). If omitted, a constant
           speed is assumed, which is only suitable for visual debugging.
cal.npz  : arrays s, sd, nu = sorted calibration scores of eq. (12).
"""
from __future__ import annotations
import argparse, csv, math, time
import numpy as np

from cusp import Camera, Pipeline, DecisionCfg

VEHICLE_CLASSES = {1, 2, 3, 5, 7}   # COCO: bicycle, car, motorcycle, bus, truck


def occlusion_flags(boxes: np.ndarray) -> np.ndarray:
    """A box is flagged when a nearer box (lower bottom edge) covers part of its bottom edge."""
    n = len(boxes)
    occ = np.zeros(n, bool)
    for i in range(n):
        x1, y1, x2, y2 = boxes[i]
        for j in range(n):
            if j == i:
                continue
            a1, b1, a2, b2 = boxes[j]
            overlap = min(x2, a2) - max(x1, a1)
            if b2 > y2 and b1 < y2 and overlap > 0.2 * (x2 - x1):
                occ[i] = True
                break
    return occ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--weights", default="yolo26s.pt")
    ap.add_argument("--cal", required=True)
    ap.add_argument("--focal", type=float, required=True, help="focal length [px]")
    ap.add_argument("--cam-height", type=float, required=True, help="camera height [m]")
    ap.add_argument("--horizon-row", type=float, required=True, help="image row of the horizon [px]")
    ap.add_argument("--principal-col", type=float, default=None)
    ap.add_argument("--speed-csv", default=None)
    ap.add_argument("--const-speed", type=float, default=8.0)
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    import cv2
    from ultralytics import YOLO

    z = np.load(a.cal)
    cal = {"w": dict(s=z["s"], sd=z["sd"], nu=z["nu"])}
    cam = Camera(f=a.focal, h=a.cam_height)
    pipe = Pipeline("CUSP (full)", cal, cam=cam)

    speeds = None
    if a.speed_csv:
        with open(a.speed_csv) as fh:
            speeds = [float(r[0]) for r in csv.reader(fh) if r]

    model = YOLO(a.weights)
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    dt = 1.0 / fps
    u0 = a.principal_col
    k, v_prev = 0, None
    t_cusp = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if u0 is None:
            u0 = frame.shape[1] / 2.0
        v_e = speeds[min(k, len(speeds) - 1)] if speeds else a.const_speed
        a_e = 0.0 if v_prev is None else (v_e - v_prev) / dt
        v_prev = v_e

        res = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)[0]
        obs = {}
        if res.boxes is not None and res.boxes.id is not None:
            xyxy = res.boxes.xyxy.cpu().numpy()
            ids = res.boxes.id.cpu().numpy().astype(int)
            cls = res.boxes.cls.cpu().numpy().astype(int)
            keep = np.array([c in VEHICLE_CLASSES for c in cls], bool)
            xyxy, ids = xyxy[keep], ids[keep]
            occ = occlusion_flags(xyxy)
            for (x1, y1, x2, y2), tid, oc in zip(xyxy, ids, occ):
                dy = y2 - a.horizon_row                 # bottom edge below horizon
                if dy <= 2.0:                           # above/at horizon: no ground contact
                    continue
                obs[int(tid)] = (float(dy), float(x2 - x1), float(0.5 * (x1 + x2) - u0), bool(oc))

        t0 = time.perf_counter()
        pipe.perceive(obs, a_e, dt, v_e)
        a_cmd = pipe.act(v_e, dt)
        t_cusp.append((time.perf_counter() - t0) * 1e3)

        if a.show:
            views = pipe.views()
            for (x1, y1, x2, y2), tid in zip(xyxy if obs else [], ids if obs else []):
                v = views.get(int(tid))
                if v is None:
                    continue
                tau = -1.0 / v.sd_lo if v.sd_lo < -1e-6 else math.inf
                col = (0, 0, 255) if v.p_conf >= 0.5 else (0, 200, 255) if v.p_conf >= 0.05 else (0, 200, 0)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), col, 2)
                cv2.putText(frame, f"Z>={v.Z_lo:.1f}m tau>={min(tau, 99):.1f}s p={v.p_conf:.2f}",
                            (int(x1), int(y1) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
            cv2.putText(frame, f"a_cmd={a_cmd:+.2f} m/s^2  alpha_t={pipe.conf.alpha_t:.3f}",
                        (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("CUSP", frame)
            if cv2.waitKey(1) == 27:
                break
        k += 1
    cap.release()
    if t_cusp:
        t = np.array(t_cusp)
        print(f"frames={k}  CUSP module: mean {t.mean():.2f} ms, p99 {np.percentile(t, 99):.2f} ms")


if __name__ == "__main__":
    main()

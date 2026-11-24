#!/usr/bin/env python3
"""Self-test data: writes KITTI-tracking-format sequences (labels, calib, oxts,
optionally blank images) from the cusp.py traffic simulator. Used only to test
cusp_eval.py end to end; it is NOT a substitute for real data.

  python tests/make_fake_kitti.py --out /tmp/fake_kitti --seqs 8 --frames 300 [--noise 1.5] [--images 3]
"""
import argparse, math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cusp

F, CX, CY, HCAM, W, H = 721.5377, 609.5593, 172.854, 1.65, 1242, 375
VEH_H, VEH_L = 1.5, 4.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seqs", type=int, default=8)
    ap.add_argument("--frames", type=int, default=300)
    ap.add_argument("--density", default="high")
    ap.add_argument("--noise", default="nominal")
    ap.add_argument("--box-noise", type=float, default=1.5, help="px noise on box edges written to labels")
    ap.add_argument("--overhang", type=float, default=0.0,
                    help="rear overhang [m]: tyres touch the road this far beyond the rear face")
    ap.add_argument("--kerb", type=float, default=0.0,
                    help="parked cars per 100 m on each kerb (|X| ~ 7 m), seen obliquely => heavy-tailed errors")
    ap.add_argument("--images", type=int, default=0, help="write blank PNGs for the first N sequences")
    ap.add_argument("--seed0", type=int, default=0)
    a = ap.parse_args()
    for d in ("label_02", "calib", "oxts", "image_02"):
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    rng = np.random.default_rng(a.seed0)
    for k in range(a.seqs):
        seq = f"{k:04d}"
        w = cusp.World(a.seed0 + k, a.density, a.noise, T_end=1e9)
        pipe = cusp.Pipeline("Oracle perception", None)
        with open(os.path.join(a.out, "calib", f"{seq}.txt"), "w") as fh:
            P = f"{F} 0 {CX} 0 0 {F} {CY} 0 0 0 1 0"
            for name in ("P0", "P1", "P2", "P3"):
                fh.write(f"{name}: {P}\n")
            fh.write("R_rect 1 0 0 0 1 0 0 0 1\n")
        lab = open(os.path.join(a.out, "label_02", f"{seq}.txt"), "w")
        ox = open(os.path.join(a.out, "oxts", f"{seq}.txt"), "w")
        if k < a.images:
            os.makedirs(os.path.join(a.out, "image_02", seq), exist_ok=True)
        fr, step = 0, 0
        parked = []                                # (vid, absolute position, X, W, extra contact error [m])
        if a.kerb > 0:
            pos = 5.0
            while pos < 3000:
                pos += float(rng.exponential(100.0 / a.kerb))
                side = 1 if rng.random() < 0.5 else -1
                parked.append((100000 + len(parked), pos, side * float(rng.uniform(6.0, 8.0)),
                               float(rng.uniform(1.6, 1.9)), float(rng.choice([rng.uniform(-0.5, 0.5), rng.uniform(1.0, 4.0)], p=[0.0, 1.0]) if rng.random() < 0.3 else rng.uniform(-0.3, 0.6))))
        while fr < a.frames and not w.collided:
            if step % 2 == 0:                     # 20 Hz simulator -> 10 Hz dataset
                pitch = F * w.N["k_pitch"] * w.ae + w.road_pitch
                vis = sorted([o for o in w.vehs if 0.5 < o.pos - w.se < 80], key=lambda o: o.pos)
                class P:  # parked car as a vehicle-like object
                    pass
                for vid, pos, X, Wd, ext in parked:
                    if 0.5 < pos - w.se < 80:
                        o = P(); o.vid, o.pos, o.X, o.W, o.ext = vid, pos, X, Wd, ext
                        vis.append(o)
                vis.sort(key=lambda o: o.pos)
                for i, o in enumerate(vis):
                    gap = o.pos - w.se
                    x1 = CX + F * (o.X - o.W / 2) / gap; x2 = CX + F * (o.X + o.W / 2) / gap
                    oh = a.overhang * float(rng.uniform(0.8, 1.2)) + getattr(o, "ext", 0.0)
                    y2 = CY + F * HCAM / (gap + oh) + pitch; y1 = CY + F * (HCAM - VEH_H) / gap + pitch
                    if x2 < 0 or x1 > W:
                        continue
                    b = np.array([x1, y1, x2, y2]) + rng.normal(0, a.box_noise, 4)
                    raw_w = b[2] - b[0]
                    c = np.array([np.clip(b[0], 0, W - 1), np.clip(b[1], 0, H - 1),
                                  np.clip(b[2], 0, W - 1), np.clip(b[3], 0, H - 1)])
                    trunc = 1 - (c[2] - c[0]) / max(raw_w, 1e-3)
                    occl = int(any(abs(n.X - o.X) < 1.5 for n in vis[:i]))
                    lab.write(f"{fr} {o.vid} Car {trunc:.2f} {occl} 0 {c[0]:.2f} {c[1]:.2f} {c[2]:.2f} {c[3]:.2f} "
                              f"{VEH_H} {o.W:.2f} {VEH_L} {o.X:.3f} {HCAM} {gap + VEH_L / 2:.3f} {-math.pi / 2:.4f}\n")
                row = [0.0] * 30
                row[8], row[14] = w.ve, w.ae
                ox.write(" ".join(f"{v:.6f}" for v in row) + "\n")
                if k < a.images:
                    from PIL import Image
                    Image.new("RGB", (W, H), (90, 90, 90)).save(os.path.join(a.out, "image_02", seq, f"{fr:06d}.png"))
                fr += 1
            obs = w.observe(pipe.cam)
            pipe.perceive(obs, w.ae, cusp.DT, w.ve)
            a_cmd = pipe.act(w.ve, cusp.DT, w.truth())
            w.step(a_cmd)
            step += 1
        lab.close(); ox.close()
        print(f"{seq}: {fr} frames")


if __name__ == "__main__":
    main()

"""Per-stage latency benchmark for the CUSP front end on a CUDA GPU (e.g. Kaggle T4).

For each model (PyTorch FP32, TensorRT FP16, TensorRT INT8) it runs YOLO + ByteTrack over
KITTI Tracking test images and records, per frame:
  preprocess, inference, postprocess (Ultralytics' own timers), tracker (rest of the call),
  and total detector+tracker time. Results go to <out>/bench_stages.csv and bench_stages.md.

Usage (Kaggle notebook cell):
  !python kaggle_bench.py --root /kaggle/input/<your-kitti-dataset>/training \
      --seqs 0011-0020 --models yolo26s.pt yolo26s_fp16.engine yolo26s_int8.engine --out /kaggle/working/bench
"""
import argparse, os, time, json, glob
import numpy as np

COCO_VEHICLES = [2, 5, 7]          # car, bus, truck


def seq_list(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); out += [f"{i:04d}" for i in range(int(a), int(b) + 1)]
        else:
            out.append(f"{int(part):04d}")
    return out


def stats(x):
    x = np.asarray([v for v in x if v is not None], float)
    return dict(mean=float(x.mean()), p50=float(np.percentile(x, 50)), p99=float(np.percentile(x, 99)), n=int(x.size))


def bench(weights, root, seqs, device, conf, warmup, max_frames):
    import cv2
    from ultralytics import YOLO
    rows = {k: [] for k in ("pre", "inf", "post", "track", "total")}
    for seq in seqs:
        model = YOLO(weights, task="detect")          # fresh tracker per sequence
        files = sorted(glob.glob(os.path.join(root, "image_02", seq, "*.png")))
        if max_frames: files = files[:max_frames]
        img0 = cv2.imread(files[0])
        for _ in range(warmup):                       # warm-up: CUDA context, TensorRT, cuDNN autotune
            model.predict(img0, device=device, verbose=False, classes=COCO_VEHICLES, conf=conf)
        model = YOLO(weights, task="detect")
        for f in files:
            img = cv2.imread(f)
            t0 = time.perf_counter()
            r = model.track(img, persist=True, tracker="bytetrack.yaml", classes=COCO_VEHICLES,
                            conf=conf, device=device, verbose=False)[0]
            tot = (time.perf_counter() - t0) * 1e3
            sp = r.speed                              # ms: preprocess, inference, postprocess
            rows["pre"].append(sp["preprocess"]); rows["inf"].append(sp["inference"])
            rows["post"].append(sp["postprocess"])
            rows["track"].append(max(0.0, tot - sp["preprocess"] - sp["inference"] - sp["postprocess"]))
            rows["total"].append(tot)
        print(f"  {os.path.basename(weights)} seq {seq}: {len(files)} frames")
    return {k: stats(v) for k, v in rows.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="KITTI tracking 'training' folder (image_02/...)")
    ap.add_argument("--seqs", default="0011-0020")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--device", default="0")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--warmup", type=int, default=30)
    ap.add_argument("--max-frames", type=int, default=0, help="0 = all frames")
    ap.add_argument("--out", default="bench")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    seqs = seq_list(a.seqs)

    import torch, platform
    env = dict(gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
               torch=torch.__version__, cpu=platform.processor() or platform.machine())
    try:
        import tensorrt; env["tensorrt"] = tensorrt.__version__
    except Exception:
        pass
    print("Environment:", env)

    res = {}
    for w in a.models:
        print("Benchmarking", w)
        res[os.path.basename(w)] = bench(w, a.root, seqs, a.device, a.conf, a.warmup, a.max_frames)

    json.dump(dict(env=env, results=res), open(os.path.join(a.out, "bench_stages.json"), "w"), indent=2)
    with open(os.path.join(a.out, "bench_stages.csv"), "w") as f:
        f.write("model,stage,mean_ms,p50_ms,p99_ms,n\n")
        for m, d in res.items():
            for k, s in d.items():
                f.write(f"{m},{k},{s['mean']:.3f},{s['p50']:.3f},{s['p99']:.3f},{s['n']}\n")
    with open(os.path.join(a.out, "bench_stages.md"), "w") as f:
        f.write(f"GPU: {env['gpu']}  torch {env['torch']}  TensorRT {env.get('tensorrt', '-')}\n\n")
        f.write("| Model | Pre | Inference | Post | Tracker | Total mean | Total p99 | FPS |\n|---|---|---|---|---|---|---|---|\n")
        for m, d in res.items():
            f.write(f"| {m} | {d['pre']['mean']:.2f} | {d['inf']['mean']:.2f} | {d['post']['mean']:.2f} | "
                    f"{d['track']['mean']:.2f} | {d['total']['mean']:.2f} | {d['total']['p99']:.2f} | "
                    f"{1000 / d['total']['mean']:.1f} |\n")
    print(open(os.path.join(a.out, "bench_stages.md")).read())


if __name__ == "__main__":
    main()

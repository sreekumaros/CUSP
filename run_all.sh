#!/usr/bin/env bash
# Runs every experiment for the paper, then writes summary.md.
# Usage:  bash run_all.sh /path/to/kitti_tracking/training [device]
#   device: mps (Apple GPU, default), cpu, or 0 (CUDA)
# Detections are cached in out_kitti/cache and reused by every run.
set -euo pipefail

K="${1:?give the KITTI tracking 'training' folder}"
DEV="${2:-mps}"
SEV="${SEV:-1.5}"
COMMON=(--cam-height 1.65 --frontend yolo --weights yolo26s.pt --device "$DEV" --plots)

copy_cache () { mkdir -p "$1/cache"; cp -n out_kitti/cache/*.json "$1/cache/" 2>/dev/null || true; }

echo "== 1/6 clean: calibrate 0-10, test 11-20"
python cusp_eval.py --calib kitti=$K:0-10 --test kitti=$K:11-20 "${COMMON[@]}" --out out_kitti

echo "== 2/6 swapped split: calibrate 11-20, test 0-10"
copy_cache out_kitti_swap
python cusp_eval.py --calib kitti=$K:11-20 --test kitti=$K:0-10 "${COMMON[@]}" --out out_kitti_swap

echo "== 3/6 ablation: no contact offset"
copy_cache out_kitti_nooff
python cusp_eval.py --calib kitti=$K:0-10 --test kitti=$K:11-20 "${COMMON[@]}" --no-contact-offset --out out_kitti_nooff

i=4
for c in dark noise fog; do
  echo "== $i/6 camera shift: $c x$SEV (test images only)"
  copy_cache out_kitti_$c
  python cusp_eval.py --calib kitti=$K:0-10 --test kitti=$K:11-20 "${COMMON[@]}" \
      --corrupt $c --severity "$SEV" --out out_kitti_$c
  i=$((i+1))
done

python summarize.py out_kitti out_kitti_swap out_kitti_nooff out_kitti_dark out_kitti_noise out_kitti_fog > summary.md
echo "== done: summary.md"
echo "Simulation on fresh seeds (about 5-15 min):  python cusp.py --episodes 200 --seed0 500000 --out results_fresh.json"

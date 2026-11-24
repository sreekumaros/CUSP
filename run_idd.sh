#!/usr/bin/env bash
# IDD-3D evaluation: calibration split -> validation split. The locked test split is NOT run here.
# Run from the cusp folder inside the project venv:  bash run_idd.sh
set -e
IDD=/Volumes/SKOS-APFS/PHD-CUSP/data/idd3d/train_val
K=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti
DEV=${DEV:-mps}
FOUR="Car Auto Truck Bus"; TWO="Motorcycle"
COMMON="--frontend yolo --device $DEV --merge-riders --cam-height 1.90 --fps 10 --img-size 1440 1080 --cache-dir out_idd_cache"

if [ ! -f "$K/mapping.csv" ]; then
  echo "== converting IDD-3D to KITTI layout"
  python idd2kitti.py --idd-root "$IDD" --calib idd_pilot/calib_cam3.json --splits idd_pilot/idd3d_splits.json --out "$K"
fi

run () {   # name, extra args
  echo "== $1"; python cusp_eval.py --calib idd=$K/calibration:all --test idd=$K/validation:all $COMMON --out "out_idd_val_$1" "${@:2}" \
     > "out_idd_val_$1.log" 2>&1 || { echo "   failed, see out_idd_val_$1.log"; return; }
  tail -3 "out_idd_val_$1.log"
}
run clean       --veh-types $FOUR $TWO --plots
run four        --veh-types $FOUR
run two         --veh-types $TWO
run nooffset    --veh-types $FOUR $TWO --no-contact-offset
run dark        --veh-types $FOUR $TWO --corrupt dark  --severity 1.5
run rain        --veh-types $FOUR $TWO --corrupt rain  --severity 1.5
run fog         --veh-types $FOUR $TWO --corrupt fog   --severity 1.5
run noise       --veh-types $FOUR $TWO --corrupt noise --severity 1.5
echo "done: out_idd_val_* folders and logs"

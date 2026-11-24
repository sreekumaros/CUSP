#!/usr/bin/env bash
# Depth Anything V2 baseline on the IDD-3D validation split (after run_idd.sh). Needs: pip install transformers
set -e
K=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti
DEV=${DEV:-mps}
C="--calib idd=$K/calibration:all --test idd=$K/validation:all --cache-dir out_idd_cache --merge-riders --device $DEV"
python -c "import transformers" 2>/dev/null || pip install -q transformers
for cond in none dark rain fog noise; do
  name=$([ $cond = none ] && echo clean || echo $cond)
  echo "== DAv2 $name"
  python dav2_baseline.py $C --corrupt $cond --severity 1.5 --out out_idd_val_dav2_$name > out_idd_val_dav2_$name.log 2>&1 \
    || { echo "   failed, see out_idd_val_dav2_$name.log"; continue; }
  tail -4 out_idd_val_dav2_$name.log
done

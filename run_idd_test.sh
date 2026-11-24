#!/usr/bin/env bash
# LOCKED TEST: run once, only after the validation results are reviewed and the settings frozen.
set -e
K=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti
DEV=${DEV:-mps}
if ls -d out_idd_test_* >/dev/null 2>&1; then echo "test outputs already exist - the test split is run only once"; exit 1; fi
mkdir -p out_idd_test_freeze
{ date; echo "code and protocol hashes at test time:"; shasum -a 256 cusp.py cusp_eval.py idd2kitti.py dav2_baseline.py \
  idd_pilot/calib_cam3.json idd_pilot/idd3d_splits.json run_idd.sh run_idd_test.sh; } > out_idd_test_freeze/FROZEN.txt
FOUR="Car Auto Truck Bus"; TWO="Motorcycle"
COMMON="--calib idd=$K/calibration:all --test idd=$K/test:all --frontend yolo --device $DEV --merge-riders --cam-height 1.90 --fps 10 --img-size 1440 1080 --cache-dir out_idd_cache"
run () { echo "== $1"; python cusp_eval.py $COMMON --out "out_idd_test_$1" "${@:2}" > "out_idd_test_$1.log" 2>&1 || echo "   failed: out_idd_test_$1.log"; }
run clean    --veh-types $FOUR $TWO --plots
run four     --veh-types $FOUR
run two      --veh-types $TWO
run nooffset --veh-types $FOUR $TWO --no-contact-offset
for c in dark rain fog noise; do run $c --veh-types $FOUR $TWO --corrupt $c --severity 1.5; done
D="--calib idd=$K/calibration:all --test idd=$K/test:all --cache-dir out_idd_cache --merge-riders --device $DEV"
for cond in none dark rain fog noise; do
  name=$([ $cond = none ] && echo clean || echo $cond)
  echo "== DAv2 $name"; python dav2_baseline.py $D --corrupt $cond --severity 1.5 --out out_idd_test_dav2_$name > out_idd_test_dav2_$name.log 2>&1 || echo "   failed"
done
echo "test done"

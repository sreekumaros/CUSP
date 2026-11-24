# CUSP: Conformal Near-Vehicle Kinematics for Uncertainty-Aware Real-Time Speed Decision in Dense Mixed Traffic

Code, protocol files and logged results for the CUSP paper.

CUSP is a constant-time module that sits between an off-the-shelf detector–tracker and the
longitudinal controller of a camera-only vehicle. From tracked bounding boxes it estimates range and
closing rate with a log-range Kalman filter, turns them into one-sided conformal lower bounds whose
level adapts online (label-free, only towards caution), weights neighbouring vehicles by a
corridor-entry probability, and returns a closed-form stopping-distance speed cap. It costs about
0.17 ms per frame in single-threaded Python.

> **Evaluation protocol.** KITTI Tracking was used during development and is reported as
> development data only. The independent evaluation uses IDD-3D (Indian roads, LiDAR-labelled 3D
> boxes, many two-wheelers) with calibration / validation / locked-test splits fixed in advance.
> The test split was run **once**; the SHA-256 hashes of the code and protocol files at that moment
> are in `results/idd3d/out_idd_test_freeze/FROZEN.txt` and can be checked with `verify_frozen.sh`.

---

## Repository layout

| Path | Contents |
| --- | --- |
| `cusp.py` | The method (filters, conformal bounds with adaptive level, corridor-entry probability, safe speed, governor) **and** the dense-traffic closed-loop simulator. NumPy only. |
| `cusp_eval.py` | Real-image evaluation on any dataset in KITTI-tracking layout (YOLO26s + ByteTrack front end, all baselines, image corruptions, tables and plots). |
| `dav2_baseline.py` | Learned-depth baseline: Depth Anything V2 (metric, outdoor, small), raw and with split-conformal bounds. |
| `idd_pilot.py` | IDD-3D front-camera self-calibration from labelled 3D boxes + pilot accuracy study. |
| `idd2kitti.py` | Converts IDD-3D (front camera) to the KITTI-tracking layout, estimates ego speed, writes the three splits. |
| `cusp_video.py` | Runs CUSP live on any video with an overlay. |
| `run_all.sh` | All KITTI development runs (clean, swapped split, no-offset ablation, dark / noise / fog). |
| `run_idd.sh` | IDD-3D: conversion + all **validation** runs. |
| `run_idd_dav2.sh` | Depth Anything V2 baseline on the validation split. |
| `run_idd_test.sh` | **Locked test** (refuses to run twice; writes the hash manifest first). |
| `summarize.py`, `make_figures.py` | Tables and figures from the KITTI outputs. |
| `idd_pilot/` | Fitted camera model (`calib_cam3.json`), pre-registered split file (`idd3d_splits.json`), pilot results. |
| `tools/` | IDD-3D download helpers (resumable login download; range-request fetch of selected files from the zip) and a dataset inspector. |
| `benchmark/` | GPU latency benchmark (PyTorch FP32 / TensorRT FP16 / INT8), script and Kaggle notebook. |
| `figures/` | Scripts for the paper figures: `cd figures && python figs.py && python fig_idd.py` (architecture diagram, KITTI and IDD-3D coverage by distance). |
| `tests/make_fake_kitti.py` | Writes simulator data in KITTI format to test the evaluator without any download. |
| `results/` | Logged outputs used in the paper: simulation, KITTI (development), IDD-3D validation and locked test. |

The files listed in `FROZEN.txt` (`cusp.py`, `cusp_eval.py`, `idd2kitti.py`, `dav2_baseline.py`,
`idd_pilot/calib_cam3.json`, `idd_pilot/idd3d_splits.json`, `run_idd.sh`, `run_idd_test.sh`) are kept
byte-identical to the versions used for the test run. Their data paths therefore still point to the
original machine (`/Volumes/...`); edit the `IDD=` / `K=` lines at the top of the shell scripts for your
system (this changes their hashes, which is expected).

---

## Installation

Python 3.10 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

The YOLO26s weights (`yolo26s.pt`) are downloaded automatically by Ultralytics on first use.
`--device mps` uses the Apple GPU, `--device 0` a CUDA GPU, `--device cpu` the CPU.

Quick check without any dataset (a few minutes on a laptop):

```bash
python cusp.py --quick
python tests/make_fake_kitti.py --out /tmp/fake_kitti --seqs 4 --frames 200
python cusp_eval.py --calib fake=/tmp/fake_kitti:0-1 --test fake=/tmp/fake_kitti:2-3 \
    --frontend gt --gt-box-noise 1.5 --cam-height 1.65 --out /tmp/cusp_selftest
```

---

## 1. Closed-loop simulation

```bash
python cusp.py --episodes 200 --seed0 500000 --out results_sim.json
```

Calibration uses 360 nominal episodes (seeds from 900000); each method is tested on 200 fresh
episodes per density and sensor condition (seeds from 500000). The paper's numbers are in
`results/simulation/results.json`; `results_dev_seeds.json` is the earlier development run
(seeds from 1000).

## 2. KITTI Tracking (development data)

Download the KITTI tracking benchmark (left colour images, labels, calibration, OXTS) and unzip into
one folder with `training/image_02`, `training/label_02`, `training/calib`, `training/oxts`.

```bash
bash run_all.sh /path/to/kitti_tracking/training mps
```

Runs the clean split (calibrate 0000–0010, test 0011–0020), the swapped split, the no-contact-offset
ablation and dark / noise / fog test-image corruptions, then writes `summary.md`.
Logged outputs: `results/kitti/`.

## 3. IDD-3D (independent evaluation)

### 3.1 Data

IDD-3D is distributed by IIIT Hyderabad after registration (https://idd.insaan.iiit.ac.in/). The full
archive is very large; only the front camera (`cam3`) and the labels are needed.

```bash
IDD_USER=... IDD_PASS=... bash tools/idd_download.sh <download-link> data/idd3d   # log in once (Ctrl-C after "Logged in.")
python tools/idd_zip_peek.py list  --out data/idd3d                                  # table of contents
python tools/idd_zip_peek.py fetch --out data/idd3d --include "*/cam3/*" "*/label/*" "*annot_data.json" \
       --exclude "train_val/*/2022*/*"                                               # skip duplicated nested folders
```

Do not commit the dataset to this repository; it is licensed by its providers.

### 3.2 Camera calibration (already done; output included)

IDD-3D has no camera intrinsics or camera–LiDAR extrinsics, so the front camera was fitted from
labelled 3D boxes on four calibration-split sequences:

```bash
python idd_pilot.py --root data/idd3d/train_val \
    --fit 20220118103808_seq_1 20220118103808_seq_11 20220118103808_seq_12 20220118103808_seq_13 \
    --pilot 20220118103808_seq_2 --out idd_pilot --device mps
```

Result (`idd_pilot/calib_cam3.json`): f = 2464 px, principal point (528, 525), camera height 1.90 m,
median IoU 0.785 between projected labels and detections, median bottom-row error 6.4 px.

### 3.3 Splits

`idd_pilot/idd3d_splits.json` (fixed before any evaluation): split by recording bag —
28 calibration, 24 validation and 49 locked-test sequences; 4 sequences adjacent to a bag boundary
between sets are excluded.

### 3.4 Validation, baseline and locked test

```bash
bash run_idd.sh          # convert + validation runs (all vehicles, four-wheel, two-wheel, no offset, dark/rain/fog/noise)
bash run_idd_dav2.sh     # Depth Anything V2 baseline (pip install transformers)
bash run_idd_test.sh     # LOCKED TEST - run once, after the settings are frozen
bash verify_frozen.sh    # check the hashed files against results/idd3d/out_idd_test_freeze/FROZEN.txt
```

Logged outputs: `results/idd3d/out_idd_val_*` and `results/idd3d/out_idd_test_*`
(`tables.md` for reading, `results.json` for every number).

---

## Main results (IDD-3D locked test, 49 sequences, all vehicles)

| Method | Range coverage (%) | Rate coverage (%) | Unsafe speed caps (%) | Speed given up (%) | Added time per frame |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 36.0 | 47.6 | 60.7 | 2.3 | 0.17 ms |
| Gaussian-KF | 49.6 | 75.1 | 40.0 | 4.1 | 0.17 ms |
| Split-CP | 92.7 | 96.6 | 7.0 | 17.9 | 0.17 ms |
| **CUSP** | **93.5** | **97.1** | 6.9 | 18.7 | **0.17 ms** |
| DAv2 + Split-CP | 90.3 | 95.1 | **3.1** | 15.7 | 159 ms |

Target coverage is 97.5%. CUSP meets it beyond 10 m (97.5% at 10–30 m, 99.9% at 30–60 m) but not
below 10 m (68.5%), where the ground-contact point leaves this camera's narrow field of view; the
learned-depth baseline fails in the same band (72.1%). The detector and tracker take 24.4 ms per
1440×1080 frame on an Apple M2, about 41 fps end to end.

---

## Citation

```bibtex
@article{cusp2026,
  title   = {{CUSP}: Conformal Near-Vehicle Kinematics for Uncertainty-Aware Real-Time Speed Decision in Dense Mixed Traffic},
  author  = {[Authors]},
  journal = {[Journal]},
  year    = {2026},
  note    = {Under review}
}
```

## Licence

Code: see `LICENSE`. KITTI and IDD-3D are subject to their own licences and are not redistributed here.

# CUSP real-data evaluation

Calibration: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:0-10']  
Test: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:11-20']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 4436; test observations: 8300


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 50.3 | 55.2 | 30.3 | 45.3 | 0.1 |
| Gaussian-KF | 72.6 | 86.6 | 66.6 | 85.9 | 11.9 |
| Split-CP | 91.4 | 98.1 | 97.4 | 99.2 | 28.7 |
| CUSP | 91.4 | 98.1 | 97.5 | 99.2 | 28.9 |
| Split-CP (group) | 90.1 | 98.3 | 87.1 | 98.7 | 30.1 |
| CUSP (group) | 90.3 | 98.3 | 87.3 | 98.7 | 30.2 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 47.6 | 51.0 | 50.7 | 49.1 | 52.8 |
| Gaussian-KF | 52.3 | 77.0 | 78.5 | 69.2 | 79.9 |
| Split-CP | 63.4 | 97.5 | 99.3 | 88.7 | 97.3 |
| CUSP | 63.5 | 97.6 | 99.3 | 88.7 | 97.4 |
| Split-CP (group) | 72.2 | 94.2 | 95.0 | 87.8 | 95.3 |
| CUSP (group) | 72.6 | 94.2 | 95.0 | 87.9 | 95.3 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 93.1 | 17.0 | 38.4 | 30.3 | 51.5 | 62.2 |
| Gaussian-KF | 98.5 | 59.3 | 71.6 | 66.6 | 71.4 | 78.5 |
| Split-CP | 100.0 | 96.7 | 98.0 | 97.4 | 83.4 | 99.2 |
| CUSP | 100.0 | 96.8 | 98.1 | 97.5 | 83.5 | 99.2 |
| Split-CP (group) | 100.0 | 87.5 | 84.0 | 87.1 | 85.3 | 99.5 |
| CUSP (group) | 100.0 | 87.7 | 84.2 | 87.3 | 85.4 | 99.5 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 |
| Gaussian-KF | 3.5 | 8.6 | 15.8 | 10.8 | 11.3 | 13.5 |
| Split-CP | 9.6 | 22.3 | 37.5 | 26.8 | 27.0 | 32.4 |
| CUSP | 9.7 | 22.3 | 37.6 | 26.9 | 27.3 | 32.6 |
| Split-CP (group) | 8.0 | 18.1 | 24.2 | 19.6 | 28.5 | 39.8 |
| CUSP (group) | 8.0 | 18.1 | 24.3 | 19.6 | 28.7 | 39.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1783 | 67.64 | 0.16 | 1.3 |
| Gaussian-KF | 1783 | 28.32 | 0.74 | 5.0 |
| Split-CP | 1783 | 2.52 | 2.55 | 16.7 |
| CUSP | 1783 | 2.47 | 2.56 | 16.8 |
| Split-CP (group) | 1783 | 8.64 | 1.65 | 11.1 |
| CUSP (group) | 1783 | 8.58 | 1.66 | 11.2 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.12 | 0.38 |
| Detector + tracker | 21.98 | 29.87 |
| End to end | 22.10 | 30.02 |

Adaptive level alpha_t on test: mean 0.047, min 0.026, max 0.050.  
Mounting calibration (test camera): height 1.650 m, horizon row 175.8 px, contact offset 1.15 m (median residual 2.98 px, n=4017).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 61, 'own lane 10-30 m': 520, 'own lane 30-60 m': 302, 'adjacent 1-10 m': 702, 'adjacent 10-30 m': 1050, 'adjacent 30-60 m': 544, 'kerbside 1-10 m': 62, 'kerbside 10-30 m': 660, 'kerbside 30-60 m': 535}.  
Test-image corruption: fog x1.5.

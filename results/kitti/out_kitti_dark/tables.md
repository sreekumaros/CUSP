# CUSP real-data evaluation

Calibration: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:0-10']  
Test: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:11-20']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 4436; test observations: 4390


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 48.8 | 52.0 | 17.9 | 45.8 | 0.4 |
| Gaussian-KF | 64.6 | 80.4 | 38.9 | 81.9 | 10.6 |
| Split-CP | 84.4 | 96.8 | 89.9 | 97.9 | 25.8 |
| CUSP | 84.8 | 96.9 | 91.3 | 98.1 | 26.3 |
| Split-CP (group) | 80.5 | 96.4 | 71.1 | 96.1 | 29.1 |
| CUSP (group) | 81.3 | 96.7 | 73.7 | 96.8 | 29.4 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 41.9 | 57.5 | 32.3 | 43.3 | 67.8 |
| Gaussian-KF | 48.8 | 71.9 | 66.7 | 58.8 | 84.5 |
| Split-CP | 56.6 | 93.5 | 100.0 | 81.4 | 94.6 |
| CUSP | 58.0 | 93.5 | 100.0 | 81.9 | 94.6 |
| Split-CP (group) | 62.2 | 86.2 | 91.6 | 77.0 | 92.3 |
| CUSP (group) | 62.8 | 86.5 | 94.3 | 78.0 | 92.3 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 57.9 | 15.5 | 8.9 | 17.9 | 48.7 | 72.6 |
| Gaussian-KF | 67.4 | 29.6 | 52.4 | 38.9 | 62.2 | 88.0 |
| Split-CP | 74.7 | 88.3 | 100.0 | 89.9 | 72.8 | 98.7 |
| CUSP | 88.4 | 88.3 | 100.0 | 91.3 | 73.0 | 98.7 |
| Split-CP (group) | 73.7 | 67.2 | 80.2 | 71.1 | 73.2 | 99.3 |
| CUSP (group) | 76.8 | 67.9 | 87.5 | 73.7 | 73.5 | 99.4 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.5 |
| Gaussian-KF | 4.2 | 9.2 | 15.4 | 10.3 | 9.2 | 13.1 |
| Split-CP | 11.4 | 23.7 | 37.0 | 25.8 | 22.5 | 31.2 |
| CUSP | 15.4 | 24.1 | 37.8 | 26.7 | 22.7 | 31.6 |
| Split-CP (group) | 9.8 | 18.7 | 23.4 | 19.1 | 27.9 | 38.8 |
| CUSP (group) | 10.3 | 18.8 | 24.0 | 19.3 | 28.1 | 39.2 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 992 | 80.75 | 0.13 | 1.2 |
| Gaussian-KF | 992 | 50.60 | 0.46 | 3.5 |
| Split-CP | 992 | 9.88 | 2.05 | 14.1 |
| CUSP | 992 | 8.67 | 2.15 | 14.8 |
| Split-CP (group) | 992 | 17.34 | 1.33 | 9.3 |
| CUSP (group) | 992 | 15.83 | 1.37 | 9.6 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.07 | 0.25 |
| Detector + tracker | 19.70 | 29.75 |
| End to end | 19.77 | 29.82 |

Adaptive level alpha_t on test: mean 0.044, min 0.007, max 0.050.  
Mounting calibration (test camera): height 1.650 m, horizon row 175.8 px, contact offset 1.15 m (median residual 2.98 px, n=4017).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 61, 'own lane 10-30 m': 520, 'own lane 30-60 m': 302, 'adjacent 1-10 m': 702, 'adjacent 10-30 m': 1050, 'adjacent 30-60 m': 544, 'kerbside 1-10 m': 62, 'kerbside 10-30 m': 660, 'kerbside 30-60 m': 535}.  
Test-image corruption: dark x1.5.

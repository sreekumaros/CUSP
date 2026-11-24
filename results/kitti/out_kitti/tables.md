# CUSP real-data evaluation

Calibration: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:0-10']  
Test: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:11-20']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 4436; test observations: 8759


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 58.4 | 59.4 | 48.1 | 52.0 | 0.2 |
| Gaussian-KF | 79.3 | 89.5 | 76.1 | 91.3 | 12.2 |
| Split-CP | 93.2 | 98.9 | 98.9 | 99.6 | 29.2 |
| CUSP | 93.2 | 98.9 | 98.9 | 99.6 | 29.2 |
| Split-CP (group) | 92.0 | 99.2 | 90.2 | 99.7 | 30.6 |
| CUSP (group) | 92.0 | 99.2 | 90.2 | 99.7 | 30.6 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 50.8 | 61.1 | 58.7 | 57.9 | 59.6 |
| Gaussian-KF | 58.4 | 85.8 | 81.3 | 73.9 | 90.2 |
| Split-CP | 69.6 | 98.3 | 99.7 | 90.6 | 98.7 |
| CUSP | 69.6 | 98.3 | 99.7 | 90.6 | 98.7 |
| Split-CP (group) | 76.2 | 95.7 | 95.8 | 89.5 | 97.1 |
| CUSP (group) | 76.2 | 95.7 | 95.8 | 89.5 | 97.1 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 95.4 | 40.4 | 50.4 | 48.1 | 56.7 | 68.2 |
| Gaussian-KF | 98.5 | 73.5 | 75.7 | 76.1 | 75.0 | 88.1 |
| Split-CP | 100.0 | 98.3 | 99.4 | 98.9 | 86.9 | 99.2 |
| CUSP | 100.0 | 98.3 | 99.4 | 98.9 | 86.9 | 99.2 |
| Split-CP (group) | 100.0 | 91.6 | 86.4 | 90.2 | 87.9 | 99.4 |
| CUSP (group) | 100.0 | 91.6 | 86.4 | 90.2 | 87.9 | 99.4 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.1 |
| Gaussian-KF | 3.5 | 8.3 | 15.6 | 10.7 | 11.8 | 13.8 |
| Split-CP | 9.5 | 21.7 | 37.0 | 26.6 | 27.9 | 32.9 |
| CUSP | 9.5 | 21.7 | 37.1 | 26.6 | 28.0 | 33.0 |
| Split-CP (group) | 7.9 | 18.0 | 24.0 | 19.5 | 29.1 | 40.3 |
| CUSP (group) | 7.9 | 18.0 | 24.0 | 19.6 | 29.1 | 40.4 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1849 | 56.08 | 0.23 | 1.8 |
| Gaussian-KF | 1849 | 21.42 | 0.94 | 6.4 |
| Split-CP | 1849 | 1.14 | 2.78 | 18.3 |
| CUSP | 1849 | 1.14 | 2.79 | 18.3 |
| Split-CP (group) | 1849 | 5.46 | 1.87 | 12.6 |
| CUSP (group) | 1849 | 5.46 | 1.87 | 12.6 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.12 | 0.39 |
| Detector + tracker | 21.11 | 32.48 |
| End to end | 21.24 | 32.63 |

Adaptive level alpha_t on test: mean 0.049, min 0.031, max 0.050.  
Mounting calibration (test camera): height 1.650 m, horizon row 175.8 px, contact offset 1.15 m (median residual 2.98 px, n=4017).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 61, 'own lane 10-30 m': 520, 'own lane 30-60 m': 302, 'adjacent 1-10 m': 702, 'adjacent 10-30 m': 1050, 'adjacent 30-60 m': 544, 'kerbside 1-10 m': 62, 'kerbside 10-30 m': 660, 'kerbside 30-60 m': 535}.  
Test-image corruption: none.

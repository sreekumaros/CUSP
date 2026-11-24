# CUSP real-data evaluation

Calibration: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:0-10']  
Test: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:11-20']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 4436; test observations: 7056


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 57.9 | 55.9 | 41.7 | 49.9 | 0.2 |
| Gaussian-KF | 79.4 | 87.1 | 77.9 | 90.4 | 10.9 |
| Split-CP | 91.8 | 97.9 | 99.9 | 99.9 | 26.5 |
| CUSP | 91.8 | 98.0 | 99.9 | 99.9 | 26.7 |
| Split-CP (group) | 92.5 | 98.3 | 95.9 | 100.0 | 28.8 |
| CUSP (group) | 92.7 | 98.4 | 96.7 | 100.0 | 28.9 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 53.2 | 61.6 | 53.1 | 56.7 | 60.8 |
| Gaussian-KF | 59.4 | 89.3 | 75.3 | 74.6 | 91.8 |
| Split-CP | 66.1 | 99.3 | 99.7 | 88.8 | 99.5 |
| CUSP | 66.3 | 99.3 | 99.7 | 88.9 | 99.5 |
| Split-CP (group) | 74.1 | 98.1 | 97.9 | 90.1 | 98.8 |
| CUSP (group) | 74.1 | 98.1 | 98.8 | 90.4 | 98.8 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 96.9 | 30.6 | 50.5 | 41.7 | 61.0 | 65.0 |
| Gaussian-KF | 99.2 | 77.2 | 73.5 | 77.9 | 75.6 | 86.9 |
| Split-CP | 100.0 | 99.8 | 100.0 | 99.9 | 83.5 | 99.1 |
| CUSP | 100.0 | 99.8 | 100.0 | 99.9 | 83.6 | 99.1 |
| Split-CP (group) | 100.0 | 96.1 | 94.4 | 95.9 | 86.5 | 99.7 |
| CUSP (group) | 100.0 | 96.1 | 97.2 | 96.7 | 86.5 | 99.7 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 |
| Gaussian-KF | 3.4 | 8.4 | 14.5 | 9.8 | 10.2 | 12.8 |
| Split-CP | 9.3 | 21.7 | 35.2 | 24.7 | 24.7 | 30.7 |
| CUSP | 9.3 | 21.8 | 35.6 | 24.9 | 25.0 | 30.8 |
| Split-CP (group) | 7.8 | 18.0 | 22.6 | 18.5 | 28.0 | 38.0 |
| CUSP (group) | 7.8 | 18.0 | 22.7 | 18.6 | 28.2 | 38.0 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1586 | 59.90 | 0.22 | 1.8 |
| Gaussian-KF | 1586 | 17.34 | 0.86 | 6.1 |
| Split-CP | 1586 | 0.00 | 2.65 | 18.1 |
| CUSP | 1586 | 0.00 | 2.67 | 18.2 |
| Split-CP (group) | 1586 | 2.52 | 1.84 | 12.9 |
| CUSP (group) | 1586 | 1.70 | 1.85 | 13.0 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.10 | 0.31 |
| Detector + tracker | 22.43 | 30.01 |
| End to end | 22.52 | 30.17 |

Adaptive level alpha_t on test: mean 0.048, min 0.023, max 0.050.  
Mounting calibration (test camera): height 1.650 m, horizon row 175.8 px, contact offset 1.15 m (median residual 2.98 px, n=4017).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 61, 'own lane 10-30 m': 520, 'own lane 30-60 m': 302, 'adjacent 1-10 m': 702, 'adjacent 10-30 m': 1050, 'adjacent 30-60 m': 544, 'kerbside 1-10 m': 62, 'kerbside 10-30 m': 660, 'kerbside 30-60 m': 535}.  
Test-image corruption: noise x1.5.

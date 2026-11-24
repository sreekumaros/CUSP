# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1367; test observations: 1194


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 44.8 | 47.6 | 38.2 | 46.3 | 0.0 |
| Gaussian-KF | 59.1 | 67.7 | 55.9 | 74.5 | 4.4 |
| Split-CP | 97.7 | 94.7 | 98.6 | 94.0 | 31.8 |
| CUSP | 98.0 | 94.8 | 98.6 | 94.0 | 32.5 |
| Split-CP (group) | 97.5 | 93.6 | 98.6 | 88.0 | 30.1 |
| CUSP (group) | 97.8 | 93.7 | 98.6 | 88.0 | 31.0 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 37.5 | 47.9 | 40.7 | 46.1 | 39.6 |
| Gaussian-KF | 75.0 | 65.5 | 50.1 | 59.8 | 56.5 |
| Split-CP | 100.0 | 96.1 | 100.0 | 98.5 | 94.3 |
| CUSP | 100.0 | 96.5 | 100.0 | 98.5 | 95.7 |
| Split-CP (group) | 100.0 | 95.6 | 100.0 | 98.2 | 94.3 |
| CUSP (group) | 100.0 | 96.2 | 100.0 | 98.3 | 95.7 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 44.2 | 21.6 | 38.2 | 52.0 | 27.2 |
| Gaussian-KF | 75.0 | 63.6 | 29.4 | 55.9 | 66.1 | 38.8 |
| Split-CP | 100.0 | 98.2 | 100.0 | 98.6 | 98.4 | 94.6 |
| CUSP | 100.0 | 98.2 | 100.0 | 98.6 | 98.5 | 95.5 |
| Split-CP (group) | 100.0 | 98.2 | 100.0 | 98.6 | 98.0 | 94.6 |
| CUSP (group) | 100.0 | 98.2 | 100.0 | 98.6 | 98.3 | 95.5 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 1.4 | 3.9 | 5.6 | 4.2 | 3.9 | 6.1 |
| Split-CP | 11.9 | 28.8 | 39.7 | 31.0 | 29.3 | 41.0 |
| CUSP | 12.3 | 29.1 | 40.2 | 31.3 | 29.9 | 42.0 |
| Split-CP (group) | 11.9 | 24.6 | 39.8 | 27.9 | 27.6 | 40.9 |
| CUSP (group) | 12.0 | 25.1 | 40.1 | 28.3 | 28.6 | 41.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 216 | 60.19 | 0.24 | 1.6 |
| Gaussian-KF | 216 | 32.41 | 0.63 | 4.3 |
| Split-CP | 216 | 0.00 | 3.71 | 24.4 |
| CUSP | 216 | 0.00 | 3.76 | 24.7 |
| Split-CP (group) | 216 | 5.56 | 2.65 | 17.0 |
| CUSP (group) | 216 | 5.56 | 2.72 | 17.5 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.10 | 0.28 |
| Detector + tracker | 23.79 | 36.98 |
| End to end | 23.89 | 37.05 |

Adaptive level alpha_t on test: mean 0.044, min 0.016, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.4 px, contact offset 1.10 m (median residual 8.10 px, n=1292).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 141, 'own lane 10-30 m': 296, 'own lane 30-60 m': 67, 'adjacent 1-10 m': 116, 'adjacent 10-30 m': 501, 'adjacent 30-60 m': 146, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 23, 'kerbside 30-60 m': 77}.  
Test-image corruption: none.

# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1367; test observations: 5524


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 30.9 | 47.5 | 27.6 | 51.1 | 0.0 |
| Gaussian-KF | 45.8 | 76.5 | 41.3 | 80.5 | 4.4 |
| Split-CP | 91.1 | 96.2 | 86.6 | 98.3 | 30.7 |
| CUSP | 91.5 | 96.5 | 87.2 | 98.5 | 31.8 |
| Split-CP (group) | 89.7 | 94.2 | 85.2 | 93.0 | 28.8 |
| CUSP (group) | 90.4 | 94.6 | 85.9 | 93.6 | 30.2 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 17.5 | 29.7 | 45.3 | 32.8 | 26.6 |
| Gaussian-KF | 23.0 | 44.9 | 67.1 | 44.9 | 47.8 |
| Split-CP | 61.1 | 96.6 | 99.9 | 88.4 | 97.1 |
| CUSP | 61.8 | 97.0 | 99.9 | 88.9 | 97.5 |
| Split-CP (group) | 59.6 | 94.7 | 99.9 | 86.7 | 96.4 |
| CUSP (group) | 60.8 | 95.6 | 99.9 | 87.5 | 97.0 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 28.4 | 26.0 | 34.2 | 27.6 | 30.4 | 40.5 |
| Gaussian-KF | 33.0 | 39.7 | 64.2 | 41.3 | 46.0 | 56.1 |
| Split-CP | 61.9 | 92.7 | 100.0 | 86.6 | 91.8 | 99.8 |
| CUSP | 62.1 | 93.5 | 100.0 | 87.2 | 92.2 | 99.9 |
| Split-CP (group) | 59.5 | 91.4 | 100.0 | 85.2 | 90.0 | 99.8 |
| CUSP (group) | 59.7 | 92.4 | 100.0 | 85.9 | 90.9 | 99.9 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 3.5 | 2.8 | 4.6 | 3.2 | 4.8 | 6.4 |
| Split-CP | 23.4 | 22.0 | 33.7 | 23.8 | 32.4 | 41.8 |
| CUSP | 24.3 | 22.8 | 34.7 | 24.7 | 33.5 | 43.6 |
| Split-CP (group) | 23.1 | 18.9 | 33.4 | 21.7 | 30.4 | 40.9 |
| CUSP (group) | 23.7 | 20.2 | 33.9 | 22.7 | 31.8 | 42.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1973 | 69.84 | 0.15 | 1.5 |
| Gaussian-KF | 1973 | 49.21 | 0.32 | 3.0 |
| Split-CP | 1973 | 11.30 | 1.98 | 16.5 |
| CUSP | 1973 | 11.20 | 2.07 | 17.3 |
| Split-CP (group) | 1973 | 12.82 | 1.63 | 13.6 |
| CUSP (group) | 1973 | 12.42 | 1.73 | 14.5 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.16 | 0.39 |
| Detector + tracker | 24.39 | 67.52 |
| End to end | 24.56 | 67.58 |

Adaptive level alpha_t on test: mean 0.042, min 0.011, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.4 px, contact offset 1.10 m (median residual 8.10 px, n=1292).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 141, 'own lane 10-30 m': 296, 'own lane 30-60 m': 67, 'adjacent 1-10 m': 116, 'adjacent 10-30 m': 501, 'adjacent 30-60 m': 146, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 23, 'kerbside 30-60 m': 77}.  
Test-image corruption: none.

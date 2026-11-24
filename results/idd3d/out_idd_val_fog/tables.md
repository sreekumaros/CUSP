# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 1664


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 44.3 | 45.6 | 46.9 | 42.7 | 0.0 |
| Gaussian-KF | 56.3 | 69.0 | 60.0 | 74.0 | 3.8 |
| Split-CP | 98.4 | 94.8 | 99.1 | 95.9 | 27.3 |
| CUSP | 98.4 | 95.5 | 99.1 | 96.4 | 27.9 |
| Split-CP (group) | 97.7 | 94.2 | 99.1 | 92.0 | 24.1 |
| CUSP (group) | 97.8 | 94.5 | 99.1 | 92.2 | 24.9 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 35.3 | 49.0 | 36.0 | 45.3 | 39.0 |
| Gaussian-KF | 58.8 | 62.2 | 45.6 | 55.9 | 58.7 |
| Split-CP | 88.2 | 97.6 | 100.0 | 98.9 | 95.8 |
| CUSP | 88.2 | 97.7 | 100.0 | 98.9 | 95.8 |
| Split-CP (group) | 88.2 | 96.5 | 100.0 | 98.1 | 95.4 |
| CUSP (group) | 88.2 | 96.8 | 100.0 | 98.3 | 95.4 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 33.3 | 51.5 | 28.2 | 46.9 | 46.9 | 28.1 |
| Gaussian-KF | 83.3 | 66.3 | 30.8 | 60.0 | 57.9 | 42.9 |
| Split-CP | 100.0 | 98.8 | 100.0 | 99.1 | 98.5 | 96.5 |
| CUSP | 100.0 | 98.8 | 100.0 | 99.1 | 98.6 | 96.5 |
| Split-CP (group) | 100.0 | 98.8 | 100.0 | 99.1 | 97.3 | 96.5 |
| CUSP (group) | 100.0 | 98.8 | 100.0 | 99.1 | 97.6 | 96.5 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 1.4 | 2.9 | 4.7 | 3.2 | 3.5 | 5.7 |
| Split-CP | 11.6 | 22.0 | 34.6 | 24.2 | 26.3 | 37.1 |
| CUSP | 11.9 | 22.3 | 35.1 | 24.5 | 27.0 | 38.2 |
| Split-CP (group) | 14.4 | 16.2 | 33.8 | 19.4 | 23.2 | 36.8 |
| CUSP (group) | 14.4 | 16.5 | 34.3 | 19.7 | 24.1 | 37.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 412 | 55.10 | 0.32 | 2.0 |
| Gaussian-KF | 412 | 31.31 | 0.69 | 4.4 |
| Split-CP | 412 | 1.70 | 3.31 | 21.5 |
| CUSP | 412 | 1.21 | 3.38 | 21.9 |
| Split-CP (group) | 412 | 3.88 | 2.20 | 13.9 |
| CUSP (group) | 412 | 3.16 | 2.26 | 14.2 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.10 | 0.29 |
| Detector + tracker | 25.14 | 41.02 |
| End to end | 25.24 | 41.28 |

Adaptive level alpha_t on test: mean 0.043, min 0.016, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: fog x1.5.

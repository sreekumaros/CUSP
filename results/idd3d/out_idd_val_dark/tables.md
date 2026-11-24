# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 1475


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 49.6 | 44.8 | 54.4 | 47.4 | 0.0 |
| Gaussian-KF | 62.0 | 65.5 | 68.9 | 73.3 | 3.7 |
| Split-CP | 98.4 | 94.8 | 99.4 | 95.2 | 27.1 |
| CUSP | 98.5 | 95.4 | 99.4 | 96.4 | 27.7 |
| Split-CP (group) | 97.6 | 93.7 | 99.4 | 90.4 | 24.0 |
| CUSP (group) | 97.7 | 94.4 | 99.4 | 91.6 | 24.8 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 66.7 | 55.1 | 38.9 | 50.7 | 44.2 |
| Gaussian-KF | 77.8 | 68.0 | 50.6 | 61.3 | 65.1 |
| Split-CP | 100.0 | 97.6 | 100.0 | 98.9 | 96.4 |
| CUSP | 100.0 | 97.7 | 100.0 | 98.9 | 96.8 |
| Split-CP (group) | 100.0 | 96.2 | 100.0 | 98.0 | 95.6 |
| CUSP (group) | 100.0 | 96.4 | 100.0 | 98.0 | 96.4 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 100.0 | 59.2 | 23.5 | 54.4 | 53.7 | 28.2 |
| Gaussian-KF | 100.0 | 74.8 | 33.3 | 68.9 | 63.9 | 45.6 |
| Split-CP | 100.0 | 99.3 | 100.0 | 99.4 | 98.8 | 96.0 |
| CUSP | 100.0 | 99.3 | 100.0 | 99.4 | 98.8 | 96.4 |
| Split-CP (group) | 100.0 | 99.3 | 100.0 | 99.4 | 97.3 | 96.0 |
| CUSP (group) | 100.0 | 99.3 | 100.0 | 99.4 | 97.4 | 96.4 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 1.3 | 2.9 | 4.4 | 3.1 | 3.4 | 5.4 |
| Split-CP | 11.2 | 22.5 | 32.3 | 23.8 | 25.8 | 36.4 |
| CUSP | 11.6 | 22.9 | 33.1 | 24.3 | 26.3 | 37.2 |
| Split-CP (group) | 13.9 | 16.6 | 31.4 | 18.8 | 22.6 | 36.0 |
| CUSP (group) | 13.9 | 16.9 | 31.8 | 19.1 | 23.5 | 36.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 333 | 46.25 | 0.41 | 2.5 |
| Gaussian-KF | 333 | 25.23 | 0.81 | 5.2 |
| Split-CP | 333 | 1.20 | 3.36 | 22.4 |
| CUSP | 333 | 1.20 | 3.45 | 23.0 |
| Split-CP (group) | 333 | 3.90 | 2.25 | 14.8 |
| CUSP (group) | 333 | 2.40 | 2.33 | 15.3 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.08 | 0.28 |
| Detector + tracker | 25.51 | 39.92 |
| End to end | 25.58 | 40.13 |

Adaptive level alpha_t on test: mean 0.043, min 0.014, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: dark x1.5.

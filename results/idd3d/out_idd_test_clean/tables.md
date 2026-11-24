# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 8298


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 36.0 | 47.6 | 40.1 | 48.6 | 0.0 |
| Gaussian-KF | 49.6 | 75.1 | 52.7 | 77.9 | 3.9 |
| Split-CP | 92.7 | 96.6 | 91.3 | 98.5 | 27.0 |
| CUSP | 93.5 | 97.1 | 91.9 | 99.0 | 28.0 |
| Split-CP (group) | 91.0 | 93.8 | 89.3 | 92.6 | 24.2 |
| CUSP (group) | 91.8 | 94.9 | 89.8 | 94.2 | 25.6 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 26.2 | 35.6 | 47.0 | 37.0 | 33.3 |
| Gaussian-KF | 33.1 | 49.0 | 68.1 | 48.7 | 52.2 |
| Split-CP | 68.1 | 96.5 | 99.9 | 90.9 | 97.6 |
| CUSP | 68.5 | 97.5 | 99.9 | 91.9 | 97.8 |
| Split-CP (group) | 66.9 | 94.2 | 99.9 | 88.8 | 97.0 |
| CUSP (group) | 68.1 | 95.1 | 99.9 | 89.7 | 97.4 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 39.8 | 40.3 | 39.8 | 40.1 | 31.2 | 40.2 |
| Gaussian-KF | 46.6 | 52.2 | 68.4 | 52.7 | 45.6 | 55.0 |
| Split-CP | 72.4 | 95.5 | 100.0 | 91.3 | 92.4 | 99.3 |
| CUSP | 72.9 | 96.2 | 100.0 | 91.9 | 93.5 | 99.3 |
| Split-CP (group) | 71.6 | 92.8 | 100.0 | 89.3 | 90.5 | 99.3 |
| CUSP (group) | 71.8 | 93.4 | 100.0 | 89.8 | 91.8 | 99.3 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 3.5 | 2.6 | 4.5 | 3.0 | 4.2 | 6.0 |
| Split-CP | 22.4 | 20.2 | 32.4 | 21.8 | 28.7 | 39.0 |
| CUSP | 23.2 | 21.0 | 33.3 | 22.6 | 29.7 | 40.5 |
| Split-CP (group) | 25.1 | 15.2 | 32.1 | 18.8 | 25.6 | 37.9 |
| CUSP (group) | 26.3 | 16.5 | 32.8 | 20.0 | 27.1 | 39.6 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 3436 | 60.65 | 0.24 | 2.3 |
| Gaussian-KF | 3436 | 40.02 | 0.45 | 4.1 |
| Split-CP | 3436 | 7.01 | 2.12 | 17.9 |
| CUSP | 3436 | 6.90 | 2.22 | 18.7 |
| Split-CP (group) | 3436 | 9.60 | 1.61 | 13.8 |
| CUSP (group) | 3436 | 8.59 | 1.76 | 15.0 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.17 | 0.41 |
| Detector + tracker | 24.39 | 67.52 |
| End to end | 24.56 | 67.58 |

Adaptive level alpha_t on test: mean 0.040, min 0.010, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: none.

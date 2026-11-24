# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 1698


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 44.2 | 44.4 | 46.7 | 43.7 | 0.0 |
| Gaussian-KF | 56.8 | 67.0 | 60.4 | 76.1 | 3.9 |
| Split-CP | 97.8 | 95.1 | 99.1 | 95.9 | 28.2 |
| CUSP | 98.1 | 95.8 | 99.1 | 96.9 | 28.7 |
| Split-CP (group) | 97.1 | 94.2 | 99.1 | 92.0 | 24.9 |
| CUSP (group) | 97.5 | 94.6 | 99.1 | 92.3 | 25.8 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 38.5 | 47.7 | 37.9 | 45.2 | 38.9 |
| Gaussian-KF | 61.5 | 62.3 | 46.8 | 57.1 | 55.1 |
| Split-CP | 92.3 | 96.7 | 100.0 | 98.4 | 94.7 |
| CUSP | 92.3 | 97.0 | 100.0 | 98.4 | 96.2 |
| Split-CP (group) | 92.3 | 95.5 | 100.0 | 97.5 | 94.7 |
| CUSP (group) | 92.3 | 96.2 | 100.0 | 97.8 | 96.2 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 33.3 | 51.8 | 26.2 | 46.7 | 47.2 | 28.2 |
| Gaussian-KF | 83.3 | 66.0 | 35.0 | 60.4 | 59.9 | 38.9 |
| Split-CP | 100.0 | 98.8 | 100.0 | 99.1 | 98.2 | 94.3 |
| CUSP | 100.0 | 98.8 | 100.0 | 99.1 | 98.3 | 95.4 |
| Split-CP (group) | 100.0 | 98.8 | 100.0 | 99.1 | 96.9 | 94.3 |
| CUSP (group) | 100.0 | 98.8 | 100.0 | 99.1 | 97.4 | 95.4 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 1.8 | 2.9 | 5.0 | 3.3 | 3.7 | 5.7 |
| Split-CP | 14.3 | 22.2 | 35.4 | 24.6 | 27.3 | 37.5 |
| CUSP | 14.5 | 22.4 | 35.9 | 24.9 | 27.8 | 38.5 |
| Split-CP (group) | 17.6 | 16.3 | 34.6 | 19.8 | 24.0 | 37.0 |
| CUSP (group) | 17.6 | 16.5 | 35.0 | 20.0 | 25.0 | 38.1 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 414 | 55.07 | 0.32 | 1.9 |
| Gaussian-KF | 414 | 29.23 | 0.69 | 4.4 |
| Split-CP | 414 | 1.45 | 3.36 | 21.7 |
| CUSP | 414 | 0.97 | 3.41 | 22.0 |
| Split-CP (group) | 414 | 3.86 | 2.23 | 14.0 |
| CUSP (group) | 414 | 3.14 | 2.28 | 14.3 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.10 | 0.28 |
| Detector + tracker | 23.79 | 36.98 |
| End to end | 23.89 | 37.05 |

Adaptive level alpha_t on test: mean 0.043, min 0.013, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: none.

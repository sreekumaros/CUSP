# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1985; test observations: 8341


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 35.0 | 47.5 | 32.8 | 50.7 | 0.0 |
| Gaussian-KF | 45.7 | 74.1 | 42.5 | 78.7 | 3.4 |
| Split-CP | 94.0 | 96.5 | 92.3 | 99.2 | 34.8 |
| CUSP | 94.4 | 97.0 | 92.5 | 99.4 | 36.7 |
| Split-CP (group) | 92.5 | 94.4 | 91.8 | 94.2 | 30.0 |
| CUSP (group) | 93.1 | 95.5 | 92.1 | 95.4 | 31.0 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 5.5 | 33.3 | 69.9 | 34.0 | 37.6 |
| Gaussian-KF | 7.3 | 45.3 | 83.7 | 43.4 | 52.0 |
| Split-CP | 65.1 | 99.0 | 100.0 | 92.3 | 98.6 |
| CUSP | 66.9 | 99.1 | 100.0 | 92.7 | 98.9 |
| Split-CP (group) | 63.5 | 97.1 | 100.0 | 90.5 | 98.0 |
| CUSP (group) | 65.0 | 97.5 | 100.0 | 91.1 | 98.3 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 8.1 | 34.0 | 75.8 | 32.8 | 32.9 | 51.3 |
| Gaussian-KF | 10.3 | 44.6 | 94.5 | 42.5 | 44.1 | 63.8 |
| Split-CP | 68.2 | 97.9 | 100.0 | 92.3 | 94.1 | 100.0 |
| CUSP | 69.4 | 98.0 | 100.0 | 92.5 | 94.7 | 100.0 |
| Split-CP (group) | 68.1 | 97.3 | 100.0 | 91.8 | 91.3 | 100.0 |
| CUSP (group) | 69.1 | 97.4 | 100.0 | 92.1 | 92.2 | 100.0 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 2.9 | 2.3 | 4.1 | 2.6 | 3.7 | 5.3 |
| Split-CP | 27.0 | 27.2 | 42.1 | 28.6 | 36.9 | 48.7 |
| CUSP | 28.4 | 28.9 | 43.9 | 30.2 | 38.8 | 51.5 |
| Split-CP (group) | 27.4 | 27.2 | 44.7 | 28.9 | 27.4 | 44.3 |
| CUSP (group) | 28.5 | 27.7 | 45.8 | 29.6 | 28.4 | 46.4 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 3444 | 65.24 | 0.24 | 1.9 |
| Gaussian-KF | 3444 | 46.49 | 0.44 | 3.5 |
| Split-CP | 3444 | 6.24 | 2.71 | 22.0 |
| CUSP | 3444 | 6.10 | 2.89 | 23.6 |
| Split-CP (group) | 3444 | 6.94 | 2.47 | 20.0 |
| CUSP (group) | 3444 | 6.74 | 2.58 | 20.9 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.16 | 0.40 |
| Detector + tracker | 24.39 | 67.52 |
| End to end | 24.56 | 67.58 |

Adaptive level alpha_t on test: mean 0.041, min 0.010, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 546.5 px, contact offset 0.00 m (median residual 10.76 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 87, 'own lane 10-30 m': 686, 'own lane 30-60 m': 84, 'adjacent 1-10 m': 94, 'adjacent 10-30 m': 812, 'adjacent 30-60 m': 168, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 17, 'kerbside 30-60 m': 37}.  
Test-image corruption: none.

# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1985; test observations: 1704


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 49.1 | 50.6 | 42.8 | 54.8 | 0.0 |
| Gaussian-KF | 58.6 | 72.3 | 49.9 | 83.8 | 3.5 |
| Split-CP | 99.1 | 96.3 | 99.3 | 99.0 | 36.8 |
| CUSP | 99.5 | 96.9 | 100.0 | 99.0 | 37.8 |
| Split-CP (group) | 98.8 | 96.4 | 99.3 | 94.4 | 29.7 |
| CUSP (group) | 98.9 | 96.7 | 99.5 | 94.4 | 30.4 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 7.7 | 47.7 | 52.4 | 50.0 | 44.1 |
| Gaussian-KF | 7.7 | 58.0 | 60.8 | 58.5 | 59.3 |
| Split-CP | 92.3 | 98.7 | 100.0 | 99.2 | 98.9 |
| CUSP | 92.3 | 99.3 | 100.0 | 99.4 | 99.6 |
| Split-CP (group) | 84.6 | 98.2 | 100.0 | 98.7 | 98.9 |
| CUSP (group) | 92.3 | 98.4 | 100.0 | 99.0 | 98.9 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 44.5 | 38.8 | 42.8 | 53.3 | 42.6 |
| Gaussian-KF | 0.0 | 52.2 | 43.8 | 49.9 | 63.7 | 53.2 |
| Split-CP | 100.0 | 99.1 | 100.0 | 99.3 | 99.4 | 97.7 |
| CUSP | 100.0 | 100.0 | 100.0 | 100.0 | 99.7 | 97.7 |
| Split-CP (group) | 100.0 | 99.1 | 100.0 | 99.3 | 98.8 | 97.7 |
| CUSP (group) | 100.0 | 99.4 | 100.0 | 99.5 | 99.0 | 97.7 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 1.5 | 2.6 | 4.3 | 2.9 | 3.3 | 5.0 |
| Split-CP | 19.2 | 29.7 | 45.1 | 32.5 | 36.0 | 47.0 |
| CUSP | 19.6 | 29.9 | 45.7 | 32.7 | 37.0 | 48.8 |
| Split-CP (group) | 19.5 | 29.9 | 45.7 | 32.7 | 24.5 | 44.6 |
| CUSP (group) | 19.7 | 29.9 | 46.1 | 32.8 | 25.2 | 46.2 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 414 | 51.21 | 0.39 | 2.2 |
| Gaussian-KF | 414 | 30.19 | 0.76 | 4.6 |
| Split-CP | 414 | 0.72 | 4.33 | 27.2 |
| CUSP | 414 | 0.72 | 4.39 | 27.5 |
| Split-CP (group) | 414 | 0.72 | 3.49 | 21.7 |
| CUSP (group) | 414 | 0.72 | 3.53 | 21.9 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.10 | 0.28 |
| Detector + tracker | 23.79 | 36.98 |
| End to end | 23.89 | 37.05 |

Adaptive level alpha_t on test: mean 0.044, min 0.012, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 546.5 px, contact offset 0.00 m (median residual 10.76 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 87, 'own lane 10-30 m': 686, 'own lane 30-60 m': 84, 'adjacent 1-10 m': 94, 'adjacent 10-30 m': 812, 'adjacent 30-60 m': 168, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 17, 'kerbside 30-60 m': 37}.  
Test-image corruption: none.

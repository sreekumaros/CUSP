# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 639; test observations: 513


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 41.7 | 37.8 | 54.9 | 42.4 | 0.0 |
| Gaussian-KF | 51.7 | 66.1 | 64.7 | 80.3 | 2.7 |
| Split-CP | 96.5 | 96.4 | 100.0 | 98.0 | 18.8 |
| CUSP | 96.9 | 99.2 | 100.0 | 98.0 | 20.0 |
| Split-CP (group) | 89.7 | 97.4 | 100.0 | 98.0 | 14.9 |
| CUSP (group) | 94.0 | 99.2 | 100.0 | 98.0 | 16.6 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 40.0 | 45.6 | 26.5 | 42.5 | 31.6 |
| Gaussian-KF | 40.0 | 56.4 | 33.3 | 52.4 | 42.1 |
| Split-CP | 80.0 | 95.8 | 100.0 | 96.6 | 94.7 |
| CUSP | 80.0 | 96.3 | 100.0 | 96.6 | 100.0 |
| Split-CP (group) | 60.0 | 87.4 | 100.0 | 89.3 | 94.7 |
| CUSP (group) | 80.0 | 92.6 | 100.0 | 93.5 | 100.0 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 100.0 | 57.8 | 34.5 | 54.9 | 33.6 | 29.8 |
| Gaussian-KF | 100.0 | 66.5 | 51.7 | 64.7 | 45.0 | 31.9 |
| Split-CP | 100.0 | 100.0 | 100.0 | 100.0 | 95.4 | 87.2 |
| CUSP | 100.0 | 100.0 | 100.0 | 100.0 | 95.4 | 91.5 |
| Split-CP (group) | 100.0 | 100.0 | 100.0 | 100.0 | 82.1 | 87.2 |
| CUSP (group) | 100.0 | 100.0 | 100.0 | 100.0 | 89.7 | 91.5 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 2.4 | 2.0 | 3.8 | 2.3 | 3.0 | 3.3 |
| Split-CP | 17.0 | 14.4 | 25.5 | 16.0 | 20.4 | 22.0 |
| CUSP | 17.0 | 14.8 | 26.9 | 16.5 | 21.7 | 25.4 |
| Split-CP (group) | 19.3 | 12.4 | 26.2 | 14.4 | 14.3 | 20.6 |
| CUSP (group) | 19.3 | 12.4 | 26.6 | 14.5 | 16.6 | 25.4 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 198 | 48.99 | 0.43 | 2.4 |
| Gaussian-KF | 198 | 25.25 | 0.77 | 4.6 |
| Split-CP | 198 | 1.52 | 2.99 | 18.7 |
| CUSP | 198 | 1.52 | 3.16 | 19.7 |
| Split-CP (group) | 198 | 1.52 | 2.37 | 14.7 |
| CUSP (group) | 198 | 1.52 | 2.47 | 15.3 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.10 | 0.28 |
| Detector + tracker | 23.79 | 36.98 |
| End to end | 23.89 | 37.05 |

Adaptive level alpha_t on test: mean 0.041, min 0.009, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 556.5 px, contact offset 0.85 m (median residual 7.24 px, n=1338).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 9, 'own lane 10-30 m': 293, 'own lane 30-60 m': 41, 'adjacent 1-10 m': 2, 'adjacent 10-30 m': 261, 'adjacent 30-60 m': 31, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 1, 'kerbside 30-60 m': 1}.  
Test-image corruption: none.

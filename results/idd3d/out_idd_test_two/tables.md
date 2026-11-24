# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 639; test observations: 2833


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 44.8 | 49.4 | 53.3 | 48.3 | 0.0 |
| Gaussian-KF | 55.2 | 73.2 | 64.4 | 76.0 | 2.8 |
| Split-CP | 94.4 | 97.2 | 95.7 | 98.9 | 18.6 |
| CUSP | 95.6 | 99.3 | 96.5 | 99.5 | 20.6 |
| Split-CP (group) | 90.3 | 97.0 | 94.4 | 97.6 | 15.6 |
| CUSP (group) | 93.5 | 99.4 | 95.1 | 99.2 | 18.2 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 35.7 | 44.5 | 67.1 | 42.8 | 52.2 |
| Gaussian-KF | 45.6 | 55.0 | 76.8 | 53.0 | 63.2 |
| Split-CP | 81.7 | 95.9 | 98.8 | 93.5 | 97.8 |
| CUSP | 82.9 | 97.1 | 98.8 | 94.9 | 98.0 |
| Split-CP (group) | 80.2 | 91.1 | 98.8 | 88.9 | 95.3 |
| CUSP (group) | 82.6 | 94.7 | 98.8 | 92.4 | 97.5 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 39.9 | 55.3 | 70.7 | 53.3 | 33.7 | 42.9 |
| Gaussian-KF | 51.9 | 65.9 | 85.3 | 64.4 | 43.5 | 51.3 |
| Split-CP | 83.6 | 98.2 | 100.0 | 95.7 | 92.4 | 96.2 |
| CUSP | 84.3 | 99.1 | 100.0 | 96.5 | 94.2 | 96.2 |
| Split-CP (group) | 83.6 | 96.5 | 100.0 | 94.4 | 84.0 | 96.2 |
| CUSP (group) | 84.0 | 97.4 | 100.0 | 95.1 | 91.0 | 96.2 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 4.2 | 2.3 | 4.2 | 2.8 | 2.8 | 3.8 |
| Split-CP | 21.0 | 16.3 | 27.1 | 17.6 | 19.0 | 25.3 |
| CUSP | 23.1 | 17.9 | 29.9 | 19.4 | 21.1 | 28.4 |
| Split-CP (group) | 22.2 | 14.1 | 28.4 | 16.2 | 13.5 | 24.6 |
| CUSP (group) | 23.3 | 15.3 | 29.5 | 17.4 | 18.0 | 28.2 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1503 | 50.17 | 0.34 | 3.0 |
| Gaussian-KF | 1503 | 29.74 | 0.60 | 5.3 |
| Split-CP | 1503 | 2.73 | 2.17 | 18.8 |
| CUSP | 1503 | 2.53 | 2.48 | 21.3 |
| Split-CP (group) | 1503 | 3.39 | 1.89 | 16.5 |
| CUSP (group) | 1503 | 2.73 | 2.23 | 19.3 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.16 | 0.40 |
| Detector + tracker | 24.39 | 67.52 |
| End to end | 24.56 | 67.58 |

Adaptive level alpha_t on test: mean 0.038, min 0.005, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 556.5 px, contact offset 0.85 m (median residual 7.24 px, n=1338).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 9, 'own lane 10-30 m': 293, 'own lane 30-60 m': 41, 'adjacent 1-10 m': 2, 'adjacent 10-30 m': 261, 'adjacent 30-60 m': 31, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 1, 'kerbside 30-60 m': 1}.  
Test-image corruption: none.

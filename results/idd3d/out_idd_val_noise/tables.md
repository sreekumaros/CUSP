# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 1444


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 50.4 | 44.0 | 60.7 | 49.1 | 0.0 |
| Gaussian-KF | 63.4 | 67.5 | 73.6 | 77.2 | 3.7 |
| Split-CP | 97.4 | 95.5 | 98.8 | 96.2 | 27.2 |
| CUSP | 97.9 | 96.3 | 98.8 | 96.6 | 27.9 |
| Split-CP (group) | 96.7 | 94.8 | 98.8 | 92.2 | 24.2 |
| CUSP (group) | 97.2 | 95.5 | 98.8 | 92.5 | 25.0 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 73.7 | 55.7 | 40.1 | 52.4 | 41.5 |
| Gaussian-KF | 84.2 | 68.7 | 53.2 | 64.2 | 60.0 |
| Split-CP | 94.7 | 96.0 | 100.0 | 98.1 | 93.8 |
| CUSP | 94.7 | 96.8 | 100.0 | 98.2 | 96.5 |
| Split-CP (group) | 94.7 | 94.9 | 100.0 | 97.5 | 93.1 |
| CUSP (group) | 94.7 | 95.7 | 100.0 | 97.6 | 95.8 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 85.7 | 64.5 | 25.6 | 60.7 | 52.4 | 31.5 |
| Gaussian-KF | 92.9 | 78.8 | 30.8 | 73.6 | 64.7 | 46.8 |
| Split-CP | 100.0 | 98.5 | 100.0 | 98.8 | 97.5 | 95.1 |
| CUSP | 100.0 | 98.5 | 100.0 | 98.8 | 97.9 | 97.0 |
| Split-CP (group) | 100.0 | 98.5 | 100.0 | 98.8 | 96.4 | 95.1 |
| CUSP (group) | 100.0 | 98.5 | 100.0 | 98.8 | 96.7 | 97.0 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 2.1 | 3.1 | 4.8 | 3.2 | 3.5 | 5.1 |
| Split-CP | 17.2 | 23.1 | 34.7 | 24.2 | 25.9 | 34.8 |
| CUSP | 17.7 | 23.4 | 35.5 | 24.6 | 26.6 | 36.0 |
| Split-CP (group) | 21.0 | 17.2 | 34.2 | 19.4 | 22.8 | 34.5 |
| CUSP (group) | 21.0 | 17.4 | 34.8 | 19.7 | 23.8 | 35.7 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 320 | 44.06 | 0.38 | 2.7 |
| Gaussian-KF | 320 | 23.44 | 0.81 | 5.7 |
| Split-CP | 320 | 0.94 | 3.39 | 23.8 |
| CUSP | 320 | 0.94 | 3.46 | 24.3 |
| Split-CP (group) | 320 | 4.06 | 2.27 | 15.7 |
| CUSP (group) | 320 | 3.75 | 2.32 | 16.1 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.07 | 0.25 |
| Detector + tracker | 25.34 | 39.28 |
| End to end | 25.40 | 39.28 |

Adaptive level alpha_t on test: mean 0.042, min 0.018, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: noise x1.5.

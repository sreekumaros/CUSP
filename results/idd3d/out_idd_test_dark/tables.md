# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 6334


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 41.4 | 48.5 | 42.5 | 50.1 | 0.5 |
| Gaussian-KF | 55.2 | 75.0 | 55.0 | 77.7 | 4.1 |
| Split-CP | 95.5 | 96.6 | 93.9 | 97.4 | 26.4 |
| CUSP | 96.0 | 97.0 | 94.2 | 97.8 | 27.7 |
| Split-CP (group) | 94.1 | 94.3 | 92.4 | 92.5 | 23.5 |
| CUSP (group) | 95.2 | 95.1 | 93.7 | 93.7 | 25.3 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 32.4 | 40.5 | 52.2 | 42.9 | 37.3 |
| Gaussian-KF | 41.5 | 54.2 | 70.2 | 54.6 | 57.0 |
| Split-CP | 75.3 | 98.2 | 99.9 | 95.1 | 96.8 |
| CUSP | 76.3 | 98.6 | 99.9 | 95.6 | 97.1 |
| Split-CP (group) | 75.4 | 96.2 | 99.9 | 93.4 | 96.2 |
| CUSP (group) | 79.1 | 97.0 | 99.9 | 94.6 | 96.9 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 38.6 | 43.9 | 39.9 | 42.5 | 39.9 | 43.6 |
| Gaussian-KF | 43.9 | 56.9 | 61.5 | 55.0 | 54.6 | 58.6 |
| Split-CP | 72.2 | 98.8 | 100.0 | 93.9 | 96.2 | 98.8 |
| CUSP | 73.0 | 98.9 | 100.0 | 94.2 | 96.7 | 99.6 |
| Split-CP (group) | 74.0 | 96.2 | 100.0 | 92.4 | 94.5 | 98.8 |
| CUSP (group) | 77.1 | 97.2 | 100.0 | 93.7 | 95.5 | 99.6 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| Gaussian-KF | 3.2 | 2.4 | 3.8 | 2.7 | 5.1 | 5.4 |
| Split-CP | 22.2 | 19.1 | 28.7 | 20.7 | 29.0 | 36.4 |
| CUSP | 23.7 | 20.2 | 29.7 | 21.9 | 30.4 | 38.1 |
| Split-CP (group) | 24.5 | 14.4 | 28.3 | 17.8 | 25.9 | 35.4 |
| CUSP (group) | 26.6 | 15.8 | 29.0 | 19.2 | 27.9 | 37.2 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 2652 | 57.69 | 0.26 | 2.3 |
| Gaussian-KF | 2652 | 37.86 | 0.47 | 4.1 |
| Split-CP | 2652 | 4.79 | 2.10 | 17.7 |
| CUSP | 2652 | 4.52 | 2.22 | 18.8 |
| Split-CP (group) | 2652 | 7.09 | 1.60 | 13.6 |
| CUSP (group) | 2652 | 5.96 | 1.77 | 15.1 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.13 | 0.37 |
| Detector + tracker | 25.71 | 69.84 |
| End to end | 25.85 | 69.89 |

Adaptive level alpha_t on test: mean 0.039, min 0.005, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: dark x1.5.

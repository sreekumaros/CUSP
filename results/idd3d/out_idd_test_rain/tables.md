# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 7303


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 39.9 | 48.3 | 43.1 | 51.1 | 0.0 |
| Gaussian-KF | 53.5 | 75.6 | 55.3 | 79.6 | 3.6 |
| Split-CP | 93.1 | 96.7 | 91.8 | 98.5 | 25.6 |
| CUSP | 93.5 | 97.0 | 92.3 | 98.8 | 26.5 |
| Split-CP (group) | 92.0 | 94.2 | 90.8 | 93.4 | 22.8 |
| CUSP (group) | 92.7 | 95.0 | 91.5 | 94.7 | 24.1 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 27.2 | 39.8 | 53.8 | 40.1 | 39.2 |
| Gaussian-KF | 34.6 | 53.9 | 71.4 | 51.1 | 60.6 |
| Split-CP | 67.2 | 97.4 | 100.0 | 91.3 | 98.5 |
| CUSP | 68.2 | 97.8 | 100.0 | 91.8 | 98.7 |
| Split-CP (group) | 67.6 | 95.7 | 100.0 | 90.1 | 97.7 |
| CUSP (group) | 69.1 | 96.4 | 100.0 | 90.9 | 98.0 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 41.5 | 43.9 | 40.5 | 43.1 | 36.1 | 43.5 |
| Gaussian-KF | 46.2 | 56.3 | 66.3 | 55.3 | 51.1 | 56.8 |
| Split-CP | 69.0 | 96.8 | 100.0 | 91.8 | 92.9 | 99.5 |
| CUSP | 69.8 | 97.2 | 100.0 | 92.3 | 93.4 | 99.5 |
| Split-CP (group) | 70.8 | 95.0 | 100.0 | 90.8 | 91.4 | 99.5 |
| CUSP (group) | 71.7 | 95.6 | 100.0 | 91.5 | 92.3 | 99.5 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 3.7 | 2.5 | 4.0 | 2.8 | 3.9 | 5.2 |
| Split-CP | 23.0 | 19.3 | 29.6 | 21.0 | 27.7 | 35.3 |
| CUSP | 23.9 | 20.0 | 30.6 | 21.7 | 28.7 | 36.7 |
| Split-CP (group) | 25.7 | 14.4 | 28.9 | 17.9 | 24.7 | 34.3 |
| CUSP (group) | 27.3 | 15.5 | 29.8 | 19.1 | 26.2 | 35.8 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 3100 | 57.74 | 0.26 | 2.6 |
| Gaussian-KF | 3100 | 37.74 | 0.48 | 4.5 |
| Split-CP | 3100 | 6.90 | 2.10 | 18.4 |
| CUSP | 3100 | 6.61 | 2.19 | 19.1 |
| Split-CP (group) | 3100 | 9.19 | 1.59 | 14.3 |
| CUSP (group) | 3100 | 8.42 | 1.72 | 15.3 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.13 | 0.36 |
| Detector + tracker | 25.73 | 69.70 |
| End to end | 25.87 | 69.82 |

Adaptive level alpha_t on test: mean 0.040, min 0.008, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: rain x1.5.

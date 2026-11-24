# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 8236


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 35.9 | 47.0 | 40.3 | 48.9 | 0.1 |
| Gaussian-KF | 49.4 | 73.1 | 52.5 | 76.9 | 3.8 |
| Split-CP | 92.4 | 95.9 | 91.5 | 97.6 | 26.7 |
| CUSP | 93.1 | 96.4 | 92.2 | 97.9 | 27.8 |
| Split-CP (group) | 90.7 | 93.3 | 89.5 | 91.6 | 23.8 |
| CUSP (group) | 91.3 | 94.3 | 90.0 | 92.9 | 25.2 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 25.3 | 35.1 | 48.6 | 36.7 | 33.8 |
| Gaussian-KF | 31.7 | 48.3 | 69.3 | 48.0 | 53.0 |
| Split-CP | 63.7 | 96.6 | 99.9 | 90.5 | 97.9 |
| CUSP | 64.5 | 97.4 | 99.9 | 91.3 | 98.2 |
| Split-CP (group) | 62.4 | 94.3 | 99.9 | 88.3 | 97.0 |
| CUSP (group) | 63.4 | 95.0 | 99.9 | 89.1 | 97.3 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 38.3 | 40.5 | 42.6 | 40.3 | 31.1 | 39.4 |
| Gaussian-KF | 45.2 | 52.0 | 70.0 | 52.5 | 45.1 | 55.0 |
| Split-CP | 72.1 | 95.5 | 100.0 | 91.5 | 91.6 | 99.3 |
| CUSP | 73.0 | 96.2 | 100.0 | 92.2 | 92.4 | 99.3 |
| Split-CP (group) | 71.3 | 92.9 | 100.0 | 89.5 | 89.5 | 99.3 |
| CUSP (group) | 71.5 | 93.6 | 100.0 | 90.0 | 90.4 | 99.3 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 1.3 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 |
| Gaussian-KF | 4.2 | 2.6 | 4.6 | 3.1 | 4.0 | 6.1 |
| Split-CP | 21.0 | 20.0 | 33.0 | 21.5 | 28.2 | 39.2 |
| CUSP | 22.5 | 20.9 | 33.9 | 22.5 | 29.4 | 40.9 |
| Split-CP (group) | 23.7 | 15.1 | 32.5 | 18.5 | 25.1 | 38.1 |
| CUSP (group) | 24.9 | 16.3 | 33.3 | 19.6 | 26.6 | 39.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 3420 | 60.85 | 0.25 | 2.4 |
| Gaussian-KF | 3420 | 40.73 | 0.46 | 4.1 |
| Split-CP | 3420 | 6.81 | 2.12 | 17.6 |
| CUSP | 3420 | 6.40 | 2.23 | 18.6 |
| Split-CP (group) | 3420 | 9.85 | 1.61 | 13.5 |
| CUSP (group) | 3420 | 8.68 | 1.75 | 14.6 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.16 | 0.40 |
| Detector + tracker | 25.11 | 67.39 |
| End to end | 25.27 | 67.54 |

Adaptive level alpha_t on test: mean 0.040, min 0.005, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: fog x1.5.

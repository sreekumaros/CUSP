# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/test:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 7014


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 40.3 | 45.7 | 45.2 | 48.2 | 0.0 |
| Gaussian-KF | 54.9 | 74.4 | 57.0 | 78.1 | 3.7 |
| Split-CP | 94.4 | 96.4 | 94.0 | 98.7 | 26.1 |
| CUSP | 94.8 | 96.7 | 94.3 | 98.8 | 27.0 |
| Split-CP (group) | 92.9 | 94.1 | 92.3 | 93.7 | 23.1 |
| CUSP (group) | 93.6 | 95.0 | 93.0 | 95.0 | 24.5 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 31.7 | 38.9 | 55.1 | 41.0 | 38.3 |
| Gaussian-KF | 41.1 | 53.9 | 72.9 | 52.7 | 60.9 |
| Split-CP | 71.9 | 98.0 | 99.8 | 93.4 | 97.2 |
| CUSP | 72.6 | 98.4 | 99.8 | 93.8 | 97.5 |
| Split-CP (group) | 71.4 | 96.0 | 99.8 | 91.6 | 96.6 |
| CUSP (group) | 73.2 | 96.6 | 99.8 | 92.5 | 96.9 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 46.0 | 45.1 | 43.9 | 45.2 | 34.4 | 45.6 |
| Gaussian-KF | 52.4 | 57.1 | 66.8 | 57.0 | 51.4 | 61.1 |
| Split-CP | 74.3 | 98.8 | 100.0 | 94.0 | 93.9 | 98.5 |
| CUSP | 75.0 | 99.0 | 100.0 | 94.3 | 94.3 | 99.1 |
| Split-CP (group) | 75.0 | 96.2 | 100.0 | 92.3 | 92.2 | 98.5 |
| CUSP (group) | 76.4 | 96.7 | 100.0 | 93.0 | 93.0 | 99.1 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 3.0 | 2.5 | 4.0 | 2.7 | 4.2 | 5.4 |
| Split-CP | 20.3 | 19.5 | 29.4 | 20.6 | 29.0 | 36.2 |
| CUSP | 21.1 | 20.3 | 30.5 | 21.3 | 29.9 | 37.5 |
| Split-CP (group) | 22.9 | 14.6 | 28.5 | 17.5 | 25.7 | 35.2 |
| CUSP (group) | 23.8 | 15.7 | 29.4 | 18.6 | 27.3 | 36.6 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 3020 | 57.28 | 0.24 | 2.2 |
| Gaussian-KF | 3020 | 35.13 | 0.45 | 4.0 |
| Split-CP | 3020 | 4.80 | 2.08 | 17.9 |
| CUSP | 3020 | 4.74 | 2.17 | 18.6 |
| Split-CP (group) | 3020 | 6.72 | 1.56 | 13.6 |
| CUSP (group) | 3020 | 6.26 | 1.69 | 14.7 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.13 | 0.35 |
| Detector + tracker | 25.51 | 69.31 |
| End to end | 25.64 | 69.32 |

Adaptive level alpha_t on test: mean 0.041, min 0.012, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: noise x1.5.

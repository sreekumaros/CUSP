# CUSP real-data evaluation

Calibration: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:11-20']  
Test: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:0-10']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 4343; test observations: 9104


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 52.4 | 48.4 | 53.7 | 43.5 | 0.2 |
| Gaussian-KF | 78.8 | 78.3 | 85.3 | 85.1 | 11.5 |
| Split-CP | 99.7 | 94.1 | 100.0 | 97.3 | 74.6 |
| CUSP | 99.7 | 94.4 | 100.0 | 97.4 | 74.6 |
| Split-CP (group) | 95.8 | 93.5 | 96.0 | 94.3 | 32.2 |
| CUSP (group) | 95.9 | 93.8 | 96.0 | 94.5 | 32.5 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 36.5 | 51.1 | 63.5 | 54.7 | 48.0 |
| Gaussian-KF | 51.8 | 80.3 | 91.8 | 79.3 | 78.0 |
| Split-CP | 98.3 | 100.0 | 100.0 | 99.5 | 100.0 |
| CUSP | 98.3 | 100.0 | 100.0 | 99.5 | 100.0 |
| Split-CP (group) | 92.7 | 94.3 | 100.0 | 95.8 | 95.7 |
| CUSP (group) | 92.9 | 94.4 | 100.0 | 95.9 | 95.9 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 25.6 | 44.8 | 69.8 | 53.7 | 46.7 | 59.6 |
| Gaussian-KF | 35.9 | 80.0 | 97.0 | 85.3 | 76.1 | 79.1 |
| Split-CP | 100.0 | 100.0 | 100.0 | 100.0 | 99.4 | 100.0 |
| CUSP | 100.0 | 100.0 | 100.0 | 100.0 | 99.4 | 100.0 |
| Split-CP (group) | 46.2 | 95.4 | 100.0 | 96.0 | 97.6 | 93.1 |
| CUSP (group) | 48.7 | 95.4 | 100.0 | 96.0 | 97.8 | 93.2 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.2 |
| Gaussian-KF | 4.0 | 8.4 | 13.5 | 10.2 | 10.3 | 13.8 |
| Split-CP | 44.4 | 69.8 | 87.1 | 75.7 | 70.3 | 80.0 |
| CUSP | 44.4 | 69.9 | 87.1 | 75.7 | 70.3 | 80.0 |
| Split-CP (group) | 10.3 | 19.1 | 29.3 | 22.7 | 35.5 | 32.7 |
| CUSP (group) | 10.5 | 19.2 | 29.7 | 22.9 | 35.9 | 32.9 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1673 | 49.43 | 0.34 | 1.9 |
| Gaussian-KF | 1673 | 12.79 | 1.33 | 7.4 |
| Split-CP | 1673 | 0.00 | 9.79 | 57.4 |
| CUSP | 1673 | 0.00 | 9.81 | 57.5 |
| Split-CP (group) | 1673 | 3.95 | 2.84 | 15.8 |
| CUSP (group) | 1673 | 3.89 | 2.87 | 16.0 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.13 | 0.40 |
| Detector + tracker | 22.27 | 31.52 |
| End to end | 22.40 | 31.71 |

Adaptive level alpha_t on test: mean 0.047, min 0.026, max 0.050.  
Mounting calibration (test camera): height 1.650 m, horizon row 173.8 px, contact offset 0.50 m (median residual 3.41 px, n=4043).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 78, 'own lane 10-30 m': 514, 'own lane 30-60 m': 329, 'adjacent 1-10 m': 676, 'adjacent 10-30 m': 990, 'adjacent 30-60 m': 489, 'kerbside 1-10 m': 93, 'kerbside 10-30 m': 825, 'kerbside 30-60 m': 349}.  
Test-image corruption: none.

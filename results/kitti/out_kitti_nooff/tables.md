# CUSP real-data evaluation

Calibration: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:0-10']  
Test: ['kitti=/Volumes/SKOS-APFS/PHD-CUSP/data/kitti_tracking/training:11-20']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 4453; test observations: 8756


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 54.8 | 52.1 | 49.3 | 47.5 | 0.0 |
| Gaussian-KF | 76.5 | 85.3 | 76.8 | 90.9 | 10.4 |
| Split-CP | 93.6 | 99.1 | 100.0 | 100.0 | 50.4 |
| CUSP | 93.7 | 99.1 | 100.0 | 100.0 | 50.6 |
| Split-CP (group) | 97.0 | 99.5 | 95.4 | 99.8 | 32.0 |
| CUSP (group) | 97.0 | 99.5 | 95.4 | 99.8 | 32.2 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 16.0 | 58.4 | 73.5 | 51.0 | 62.4 |
| Gaussian-KF | 25.0 | 86.5 | 92.0 | 71.4 | 87.0 |
| Split-CP | 66.1 | 100.0 | 100.0 | 90.6 | 99.7 |
| CUSP | 66.3 | 100.0 | 100.0 | 90.7 | 99.7 |
| Split-CP (group) | 93.5 | 97.8 | 97.7 | 96.2 | 98.4 |
| CUSP (group) | 93.7 | 97.8 | 97.7 | 96.3 | 98.4 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 2.3 | 41.2 | 69.9 | 49.3 | 48.8 | 67.7 |
| Gaussian-KF | 6.9 | 79.5 | 86.0 | 76.8 | 67.5 | 90.1 |
| Split-CP | 100.0 | 100.0 | 100.0 | 100.0 | 86.6 | 100.0 |
| CUSP | 100.0 | 100.0 | 100.0 | 100.0 | 86.7 | 100.0 |
| Split-CP (group) | 93.1 | 96.7 | 94.0 | 95.4 | 96.2 | 99.2 |
| CUSP (group) | 93.1 | 96.7 | 94.0 | 95.4 | 96.2 | 99.2 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 2.9 | 7.4 | 13.4 | 9.3 | 9.8 | 12.0 |
| Split-CP | 19.5 | 43.0 | 63.1 | 48.9 | 47.0 | 56.5 |
| CUSP | 19.6 | 43.2 | 63.3 | 49.1 | 47.2 | 56.7 |
| Split-CP (group) | 9.0 | 20.8 | 19.6 | 19.5 | 33.1 | 38.9 |
| CUSP (group) | 9.0 | 20.8 | 19.7 | 19.6 | 33.3 | 39.0 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 1850 | 54.32 | 0.38 | 2.2 |
| Gaussian-KF | 1850 | 19.62 | 1.09 | 6.6 |
| Split-CP | 1850 | 0.00 | 5.93 | 38.1 |
| CUSP | 1850 | 0.00 | 5.96 | 38.3 |
| Split-CP (group) | 1850 | 3.78 | 2.22 | 14.4 |
| CUSP (group) | 1850 | 3.78 | 2.23 | 14.4 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.13 | 0.39 |
| Detector + tracker | 21.11 | 32.48 |
| End to end | 21.24 | 32.63 |

Adaptive level alpha_t on test: mean 0.048, min 0.026, max 0.050.  
Mounting calibration (test camera): height 1.650 m, horizon row 171.9 px, contact offset 0.00 m (median residual 3.77 px, n=4017).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 42, 'own lane 10-30 m': 580, 'own lane 30-60 m': 276, 'adjacent 1-10 m': 654, 'adjacent 10-30 m': 1225, 'adjacent 30-60 m': 501, 'kerbside 1-10 m': 44, 'kerbside 10-30 m': 692, 'kerbside 30-60 m': 439}.  
Test-image corruption: none.

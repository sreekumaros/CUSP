# CUSP real-data evaluation

Calibration: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/calibration:all']  
Test: ['idd=/Volumes/SKOS-APFS/PHD-CUSP/data/idd_kitti/validation:all']  
Front end: yolo (yolo26s.pt)  
Target coverage per bound: 97.5%  
Calibration scores: 1984; test observations: 1354


## Table A. Coverage (%) and relative range margin (%)

| Method | Range cov. (all) | Rate cov. (all) | Range cov. (corridor) | Rate cov. (corridor) | Margin |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 52.5 | 47.7 | 64.7 | 51.5 | 0.0 |
| Gaussian-KF | 66.2 | 71.6 | 79.0 | 87.9 | 3.7 |
| Split-CP | 97.8 | 96.8 | 98.8 | 100.0 | 26.6 |
| CUSP | 97.8 | 96.8 | 98.8 | 100.0 | 27.1 |
| Split-CP (group) | 96.9 | 96.7 | 98.8 | 99.1 | 23.4 |
| CUSP (group) | 97.0 | 96.8 | 98.8 | 99.4 | 24.1 |

## Table B. Range coverage (%) by distance band and occlusion

| Method | 1-10 m | 10-30 m | 30-60 m | not occluded | occluded |
| --- | --- | --- | --- | --- | --- |
| Point-KF | 50.0 | 55.8 | 45.3 | 54.7 | 41.7 |
| Gaussian-KF | 56.2 | 69.7 | 58.8 | 66.3 | 65.4 |
| Split-CP | 87.5 | 97.0 | 100.0 | 98.0 | 96.9 |
| CUSP | 87.5 | 97.0 | 100.0 | 98.0 | 96.9 |
| Split-CP (group) | 87.5 | 95.7 | 100.0 | 97.1 | 96.1 |
| CUSP (group) | 87.5 | 95.8 | 100.0 | 97.2 | 96.1 |

## Table B2. Range coverage (%): own-lane vehicles by distance, and all vehicles by lateral zone

| Method | own lane 1-10 m | own lane 10-30 m | own lane 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 100.0 | 66.1 | 45.7 | 64.7 | 54.1 | 27.1 |
| Gaussian-KF | 100.0 | 82.2 | 48.6 | 79.0 | 66.7 | 43.8 |
| Split-CP | 100.0 | 98.6 | 100.0 | 98.8 | 97.5 | 97.1 |
| CUSP | 100.0 | 98.6 | 100.0 | 98.8 | 97.5 | 97.1 |
| Split-CP (group) | 100.0 | 98.6 | 100.0 | 98.8 | 96.0 | 97.1 |
| CUSP (group) | 100.0 | 98.6 | 100.0 | 98.8 | 96.2 | 97.1 |

| Method | margin, own lane 1-10 m | margin, own lane 10-30 m | margin, own lane 30-60 m | margin, own lane | margin, adjacent | margin, kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Point-KF | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Gaussian-KF | 1.3 | 2.9 | 4.4 | 3.0 | 3.3 | 5.9 |
| Split-CP | 11.3 | 22.2 | 32.5 | 23.0 | 25.0 | 38.1 |
| CUSP | 11.7 | 22.5 | 32.9 | 23.3 | 25.6 | 39.1 |
| Split-CP (group) | 14.0 | 16.4 | 31.9 | 18.0 | 21.9 | 37.6 |
| CUSP (group) | 14.2 | 16.7 | 32.2 | 18.3 | 22.7 | 38.6 |

## Table C. Per-vehicle speed-cap safety (in-corridor vehicles)

Unsafe = estimated safe speed exceeds the safe speed computed from true range and true closing rate. Slack = how much lower the estimated cap is than the true cap (cost of caution).

| Method | Observations | Unsafe caps (%) | Mean slack (m/s) | Mean slack (% of true cap) |
| --- | --- | --- | --- | --- |
| Point-KF | 330 | 39.09 | 0.41 | 2.6 |
| Gaussian-KF | 330 | 18.18 | 0.86 | 5.6 |
| Split-CP | 330 | 0.00 | 3.58 | 24.1 |
| CUSP | 330 | 0.00 | 3.64 | 24.5 |
| Split-CP (group) | 330 | 0.61 | 2.48 | 16.3 |
| CUSP (group) | 330 | 0.30 | 2.54 | 16.8 |

## Table D. Latency per frame (ms)

| Stage | Mean | 99th percentile |
| --- | --- | --- |
| CUSP module | 0.07 | 0.26 |
| Detector + tracker | 25.55 | 42.78 |
| End to end | 25.62 | 42.83 |

Adaptive level alpha_t on test: mean 0.044, min 0.018, max 0.050.  
Mounting calibration (test camera): height 1.900 m, horizon row 559.5 px, contact offset 1.10 m (median residual 7.80 px, n=2627).  
Calibration scores per group (lateral zone x range): {'own lane 1-10 m': 150, 'own lane 10-30 m': 574, 'own lane 30-60 m': 100, 'adjacent 1-10 m': 118, 'adjacent 10-30 m': 760, 'adjacent 30-60 m': 177, 'kerbside 1-10 m': 0, 'kerbside 10-30 m': 24, 'kerbside 30-60 m': 81}.  
Test-image corruption: rain x1.5.

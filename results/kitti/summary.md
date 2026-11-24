# CUSP on KITTI Tracking: summary

Own lane = vehicles with true |X| < 1.8 m. Target coverage per bound: 97.5%. Unsafe = estimated safe speed above the true safe speed.

## Table 1. Own-lane safety per condition

| Condition | Method | Range cov. (%) | Rate cov. (%) | Unsafe caps (%) | Speed given up (% of true cap) | Margin (%) |
| --- | --- | --- | --- | --- | --- | --- |
| Clean | Point-KF | 48.1 | 52.0 | 56.08 | 1.8 | 0.0 |
| Clean | Gaussian-KF | 76.1 | 91.3 | 21.42 | 6.4 | 10.7 |
| Clean | Split-CP | 98.9 | 99.6 | 1.14 | 18.3 | 26.6 |
| Clean | CUSP | 98.9 | 99.6 | 1.14 | 18.3 | 26.6 |
| Clean, swapped split | Point-KF | 53.7 | 43.5 | 49.43 | 1.9 | 0.0 |
| Clean, swapped split | Gaussian-KF | 85.3 | 85.1 | 12.79 | 7.4 | 10.2 |
| Clean, swapped split | Split-CP | 100.0 | 97.3 | 0.00 | 57.4 | 75.7 |
| Clean, swapped split | CUSP | 100.0 | 97.4 | 0.00 | 57.5 | 75.7 |
| Clean, no contact offset | Point-KF | 49.3 | 47.5 | 54.32 | 2.2 | 0.0 |
| Clean, no contact offset | Gaussian-KF | 76.8 | 90.9 | 19.62 | 6.6 | 9.3 |
| Clean, no contact offset | Split-CP | 100.0 | 100.0 | 0.00 | 38.1 | 48.9 |
| Clean, no contact offset | CUSP | 100.0 | 100.0 | 0.00 | 38.3 | 49.1 |
| Shift: dark x1.5 | Point-KF | 17.9 | 45.8 | 80.75 | 1.2 | 0.0 |
| Shift: dark x1.5 | Gaussian-KF | 38.9 | 81.9 | 50.60 | 3.5 | 10.3 |
| Shift: dark x1.5 | Split-CP | 89.9 | 97.9 | 9.88 | 14.1 | 25.8 |
| Shift: dark x1.5 | CUSP | 91.3 | 98.1 | 8.67 | 14.8 | 26.7 |
| Shift: noise x1.5 | Point-KF | 41.7 | 49.9 | 59.90 | 1.8 | 0.0 |
| Shift: noise x1.5 | Gaussian-KF | 77.9 | 90.4 | 17.34 | 6.1 | 9.8 |
| Shift: noise x1.5 | Split-CP | 99.9 | 99.9 | 0.00 | 18.1 | 24.7 |
| Shift: noise x1.5 | CUSP | 99.9 | 99.9 | 0.00 | 18.2 | 24.9 |
| Shift: fog x1.5 | Point-KF | 30.3 | 45.3 | 67.64 | 1.3 | 0.0 |
| Shift: fog x1.5 | Gaussian-KF | 66.6 | 85.9 | 28.32 | 5.0 | 10.8 |
| Shift: fog x1.5 | Split-CP | 97.4 | 99.2 | 2.52 | 16.7 | 26.8 |
| Shift: fog x1.5 | CUSP | 97.5 | 99.2 | 2.47 | 16.8 | 26.9 |

## Table 2. Effect of online adaptation (CUSP vs static Split-CP)

| Condition | Mean alpha_t | Min alpha_t | Own-lane range cov. Split-CP / CUSP | Unsafe caps Split-CP / CUSP | Margin Split-CP / CUSP |
| --- | --- | --- | --- | --- | --- |
| Clean | 0.049 | 0.031 | 98.9 / 98.9 | 1.14 / 1.14 | 26.6 / 26.6 |
| Clean, swapped split | 0.047 | 0.026 | 100.0 / 100.0 | 0.00 / 0.00 | 75.7 / 75.7 |
| Clean, no contact offset | 0.048 | 0.026 | 100.0 / 100.0 | 0.00 / 0.00 | 48.9 / 49.1 |
| Shift: dark x1.5 | 0.044 | 0.007 | 89.9 / 91.3 | 9.88 / 8.67 | 25.8 / 26.7 |
| Shift: noise x1.5 | 0.048 | 0.023 | 99.9 / 99.9 | 0.00 / 0.00 | 24.7 / 24.9 |
| Shift: fog x1.5 | 0.047 | 0.026 | 97.4 / 97.5 | 2.52 / 2.47 | 26.8 / 26.9 |

## Table 3. CUSP range coverage (%) by distance (own lane) and lateral zone (all vehicles)

| Condition | own 1-10 m | own 10-30 m | own 30-60 m | own lane | adjacent | kerbside |
| --- | --- | --- | --- | --- | --- | --- |
| Clean | 100.0 | 98.3 | 99.4 | 98.9 | 86.9 | 99.2 |
| Clean, swapped split | 100.0 | 100.0 | 100.0 | 100.0 | 99.4 | 100.0 |
| Clean, no contact offset | 100.0 | 100.0 | 100.0 | 100.0 | 86.7 | 100.0 |
| Shift: dark x1.5 | 88.4 | 88.3 | 100.0 | 91.3 | 73.0 | 98.7 |
| Shift: noise x1.5 | 100.0 | 99.8 | 100.0 | 99.9 | 83.6 | 99.1 |
| Shift: fog x1.5 | 100.0 | 96.8 | 98.1 | 97.5 | 83.5 | 99.2 |

## Table 4. Ablation: group-conditional calibration (lateral zone x range)

| Condition | Own-lane range cov. CUSP / CUSP (group) | Unsafe caps CUSP / CUSP (group) | Own-lane margin CUSP / CUSP (group) |
| --- | --- | --- | --- |
| Clean | 98.9 / 90.2 | 1.14 / 5.46 | 26.6 / 19.6 |
| Clean, swapped split | 100.0 / 96.0 | 0.00 / 3.89 | 75.7 / 22.9 |
| Clean, no contact offset | 100.0 / 95.4 | 0.00 / 3.78 | 49.1 / 19.6 |
| Shift: dark x1.5 | 91.3 / 73.7 | 8.67 / 15.83 | 26.7 / 19.3 |
| Shift: noise x1.5 | 99.9 / 96.7 | 0.00 / 1.70 | 24.9 / 18.6 |
| Shift: fog x1.5 | 97.5 / 87.3 | 2.47 / 8.58 | 26.9 / 19.6 |

## Table 5. Latency per frame (ms) and mounting calibration

| Condition | CUSP mean / p99 | Detector + tracker mean / p99 | End to end mean | Contact offset (m) | Horizon row (px) |
| --- | --- | --- | --- | --- | --- |
| Clean | 0.12 / 0.39 | 21.1 / 32.5 | 21.2 | 1.15 | 175.8 |
| Clean, swapped split | 0.13 / 0.40 | 22.3 / 31.5 | 22.4 | 0.50 | 173.8 |
| Clean, no contact offset | 0.13 / 0.39 | 21.1 / 32.5 | 21.2 | 0.00 | 171.9 |
| Shift: dark x1.5 | 0.07 / 0.25 | 19.7 / 29.7 | 19.8 | 1.15 | 175.8 |
| Shift: noise x1.5 | 0.10 / 0.31 | 22.4 / 30.0 | 22.5 | 1.15 | 175.8 |
| Shift: fog x1.5 | 0.12 / 0.38 | 22.0 / 29.9 | 22.1 | 1.15 | 175.8 |

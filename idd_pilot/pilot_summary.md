# IDD-3D pilot (front camera cam3)

Fit sequences: 20220118103808_seq_1, 20220118103808_seq_11, 20220118103808_seq_12, 20220118103808_seq_13 (100 frames). Pilot (held out): 20220118103808_seq_2 (50 frames).
Camera fit: f = 2464.2 px, principal point (528, 525), height 1.90 m, horizon row 529.4; median IoU of projected labels vs detections 0.785, bottom-row error median 6.4 px (90th pct 18.6).
Contact offset delta (fit sequences): four-wheel 0.70 m, two-wheel 0.05 m.
Pilot observations (detections matched to labels, IoU >= 0.5): 257 (197 four-wheel, 60 two-wheel).

| Group | Band (m) | n | Contact cue: bias (m) | MAE (m) | median rel. err | 90th pct rel. err | Width cue: MAE (m) | median rel. err |
|---|---|---|---|---|---|---|---|---|
| four | 1-10 | 149 (52 contact) | +0.37 | 0.43 | 4.2% | 5.2% | 3.73 | 82.1% |
| four | 10-30 | 48 (48 contact) | +1.22 | 1.11 | 9.2% | 12.9% | 0.62 | 5.0% |
| four | all | 197 (100 contact) | +0.43 | 0.76 | 4.6% | 12.3% | 2.98 | 72.0% |
| two | 1-10 | 18 (8 contact) | +0.50 | 0.45 | 5.8% | 7.1% | 0.68 | 9.4% |
| two | 10-30 | 42 (42 contact) | +0.64 | 0.58 | 5.8% | 7.1% | 1.73 | 13.7% |
| two | all | 60 (50 contact) | +0.63 | 0.56 | 5.8% | 7.1% | 1.42 | 13.3% |

# Argo deep-current reconstruction — dataset

**What we have in mind.** Predict the ocean's deep horizontal current — Argo float velocity at
~1000 m, components `obs_u` (eastward) and `obs_v` (northward) — from continuous, gap-free
*observational* temperature/salinity fields (World Ocean Atlas 2023, 0.25°) and their horizontal
gradients. We frame it as a reconstruction / gap-filling problem: **30% of the velocity cells
have been held out at random** as a test set, and the true values for those cells are provided
separately so predictions can be scored.

Target: 2°×2° binned Argo parking-depth (≈950–1150 dbar) velocities (from the ANDRO
displacement dataset). Predictors: sampled from WOA23 at 1000 m.

## Files
| File | Rows | Contents |
|---|---|---|
| `train.csv` | 5159 | training cells — inputs **and** velocities |
| `gaps_to_predict.csv` | 2272 | held-out cells — inputs only |
| `gaps_answers.csv` | 2272 | true velocities for the held-out cells (join on `cell_id`) |

## Columns
| Column | Meaning | Units |
|---|---|---|
| `cell_id` | row id; links `gaps_to_predict` ↔ `gaps_answers` | — |
| `lat`, `lon` | location | degrees |
| `obs_u`, `obs_v` | eastward / northward current **(the target)** | m/s |
| `obs_speed` | √(u²+v²), in `gaps_answers.csv` only | m/s |
| `theta` | temperature | °C |
| `salt` | salinity (≈35) | g/kg |
| `dT_dx`, `dT_dy` | horizontal temperature gradient (eastward / northward) | °C per 100 km |
| `dS_dx`, `dS_dy` | horizontal salinity gradient (eastward / northward) | (g/kg) per 100 km |
| `f_coriolis` | Coriolis parameter, 2Ω·sin(lat) | s⁻¹ |
| `n_cycles` | float cycles averaged into the cell (confidence) | count |

**On the gradient columns:** these are the spatial rates of change of T/S — how much each
changes per 100 km going east (`_dx`) or north (`_dy`). They're included because deep currents
are set by *horizontal density gradients* (thermal wind), so the T/S values alone predict
velocity poorly while their gradients carry most of the signal.

## Notes
- All fields are long-term climatologies (not synoptic snapshots). Deep currents are weak (a
  few cm/s).
- The held-out 30% is random and scattered (an interpolation-style test).
- Built from ANDRO float displacements + WOA23; processing scripts available from us on request.

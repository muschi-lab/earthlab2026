# Bayesian Workgroup — Group Exercises (Wednesday)

Data and task brief for the three Bayesian group exercises. Each group works from its own
subfolder (data + a short README naming the source and key caveats). The full task brief —
model, task, and deliverables per group — is in **`EARTHLAB_Bayesian_Group_Tasks.pdf`** (project it
before the practical).

## Groups

| Folder | Data | Task in one line |
|---|---|---|
| `group1_sst/` | `ersstv5_annual_1854_2025.nc` (NOAA ERSSTv5, 2°, 1854–2025) | Per-cell change-point on SST → map P(change), t₀ uncertainty, and post-change rate |
| `group2_seaice_changepoints/` | `sia_series_1901_2024.csv` (+ `seaice_2deg_seasonal_1901_2024.nc` for the optional mapping) | One vs two change points in September Arctic sea-ice area; ice-free year as a posterior |
| `group3_seaice_forecast/` | `sia_series_1901_2024.csv` | Sequential Bayesian forecast with a CMIP/IPCC prior; predict held-out 2020–24 and 2026 |

## Every group's presentation must include

1. A **prior-sensitivity** comparison — show how much your prior changes the conclusion.
2. At least one result stated as a **posterior probability**.
3. One **posterior-predictive check** — test the model against data it did not see.
4. Your **assumptions** and how you fit it (**conjugate**, or **MCMC** with a convergence check).

Note: the `tau` fields in every dataset are **assumed** 1σ measurement errors (the noise term in the
likelihood), not published values — state that assumption.

## Sources

NOAA ERSSTv5 (Huang et al. 2017) · IAPICE1 reconstruction (Semenov et al. 2024) + HadISST1.1
(Rayner et al. 2003). Full citations and caveats are in each group folder's README.

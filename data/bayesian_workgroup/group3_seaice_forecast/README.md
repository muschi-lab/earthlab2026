# Group 3 — Sea Ice (Forecast)

September Northern-Hemisphere sea-ice **area**, mln km², 1901–2024 (IAPICE1 1901–2019 +
bias-adjusted HadISST1.1 2020–24).

**`sia_series_1901_2024.csv`** — use column `sia_sep_nh`. `tau_sia` = assumed 1σ
(0.50/0.25/0.10 mln km² by era); `source` flags IAPICE1 vs HadISST-adjusted.

**Train on 1979–2019, hold out 2020–2024** for the posterior-predictive check. The 2020–24 years
are the bias-adjusted HadISST segment (the validation target — that's intentional). For a real-world
sanity check of a 2026 forecast, independent NSIDC Sea Ice Index values exist for 2020–25, but note
those are **extent**, not **area**.

`tau_sia` is the assumed 1σ measurement error attached to each data point — the number that goes into
the likelihood as the observation's noise. The values are assumed, not published, so state that.

Sources: Semenov et al. (2024), *Adv. Atmos. Sci.* 41, 1483, doi:10.1007/s00376-024-3320-x ·
Rayner et al. (2003), *JGR* 108, 4407, doi:10.1029/2002JD002670 · NSIDC Sea Ice Index,
https://nsidc.org/data/seaice_index.

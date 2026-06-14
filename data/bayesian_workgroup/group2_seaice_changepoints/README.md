# Group 2 — Sea Ice (Change Points)

September Northern-Hemisphere sea ice, 1901–2024 (IAPICE1 reconstruction 1901–2019 +
bias-adjusted HadISST1.1 2020–24; `source` flags which).

**`sia_series_1901_2024.csv`** *(main task)* — pan-Arctic sea-ice **area**, mln km². Use
`sia_sep_nh`; `tau_sia` is the assumed 1σ (0.50/0.25/0.10 by era); `source` flags the dataset.

**`seaice_2deg_seasonal_1901_2024.nc`** *(for the optional mapping extra)* — gridded SIC
(fraction 0–1): `sic_sep_nh (year, lat_nh, lon)` + `tau_sep_nh`.

⚠ **Splice seam at 2019→2020.** A change point landing at 2019/20 is likely the dataset join,
not a discovery. ⚠ SIC is bounded [0,1] and saturates — for the gridded extra, keep only cells
with real variability (interannual σ > 0.02).

`tau` (e.g. `tau_sia`) is the assumed 1σ measurement error attached to each data point — the number
that goes into the likelihood as the observation's noise. The values are assumed, not published, so
state that.

Sources: Semenov et al. (2024), *Adv. Atmos. Sci.* 41, 1483, doi:10.1007/s00376-024-3320-x ·
Rayner et al. (2003), *JGR* 108, 4407, doi:10.1029/2002JD002670.

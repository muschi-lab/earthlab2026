# Group 1 — Sea Surface Temperature

**`ersstv5_annual_1854_2025.nc`** — annual-mean SST, NOAA **ERSSTv5**, 2° grid, 1854–2025.

| Variable | Meaning |
|---|---|
| `sst (year, lat, lon)` | annual-mean SST, °C (absolute; land/ice = NaN) |
| `tau_sst (year)` | assumed 1σ error: 0.10 (1854–99) / 0.05 (1900–49) / 0.03 (1950–) °C |

**Use absolute values → compute anomalies vs a baseline (e.g. 1961–90) before comparing cells.**
ENSO makes tropical Pacific cells noisy — test whether a change point is *significant* (BIC / Bayes
factor / posterior probability), not just best-fitting. Area-weight by cos(lat) for spatial means.

`tau_sst` is the assumed 1σ measurement error attached to each data point — the number that goes
into the likelihood as the observation's noise. The tiered values are themselves assumed (not from a
published uncertainty product), so state that.

Source: Huang et al. (2017), *J. Climate* 30, 8179. doi:10.1175/JCLI-D-16-0836.1 · data doi:10.7289/V5T72FNM.

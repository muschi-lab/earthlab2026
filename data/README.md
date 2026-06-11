# Data

Datasets for the EARTHLAB 2026 practicals, listed in the order they are used during the week.

## Monday — Claude Code & data fundamentals

- **hadcrut5.csv** — HadCRUT5 global surface temperature anomalies, annual means 1850–2025 (°C, relative to 1961–1990). Columns: `year`, `global_anomaly`, `nh_anomaly`, `sh_anomaly` (global / Northern / Southern Hemisphere), and `global_lower_ci` / `global_upper_ci` (95% confidence interval on the global mean). Source: [Met Office Hadley Centre](https://www.metoffice.gov.uk/hadobs/hadcrut5/).

## Tuesday — Neural networks

- **argo_current_reconstruction/** — Argo float velocities + WOA temperature/salinity for the ANN regression practical (`02_ann_argo_currents.ipynb`). See the README inside the folder.
- **sea_ice_dataset/** — Arctic sea ice satellite images (128×128 grayscale) for the CNN classification practical (`03_cnn_sea_ice.ipynb`). See the README inside the folder.

## Wednesday — Bayesian inference

- **Glac_Melt.csv** — Daily glacier melt vs air temperature, Spitsbergen, summer 1999 (data courtesy of Prof. Gareth Rees), for the Bayesian practical (`04_bayesian_glacier_melt.ipynb`). Columns: `Day` (day of year), `AvTemp` (°C), `Melt` (mm).

---

Larger datasets for the group exercises are available on Google Drive:
https://drive.google.com/drive/folders/15yY04_8PBkB3Jy00O1SzIyStFfxgbTYD?usp=sharing

Your own research data stays on your laptop — do not upload it here.

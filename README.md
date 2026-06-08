<img src="assets/form-banner.png" alt="EARTHLAB 2026" width="400">

# EARTHLAB 2026

**Earth Data Analytics Research Network**
Department of Geography & Department of Engineering, University of Cambridge

15–19 June 2026

---

A five-day intensive workshop in Bayesian methods, machine learning, and AI-powered research workflows for early-career geoscientists.

## Quick start

```bash
git clone https://github.com/muschi-lab/earthlab2026.git
cd earthlab2026
conda activate earthlab
pip install -r requirements.txt
jupyter notebook
```

Open `test_setup.ipynb` and run all cells to verify your environment.

## Repository structure

```
earthlab2026/
  data/                         ← Datasets for practicals
    argo_current_reconstruction/  (ANN regression task)
    sea_ice_dataset/              (CNN classification task)
  notebooks/                    ← Teaching notebooks
    01_data_screening.ipynb       (Monday — data exploration)
    02_ann_argo_currents.ipynb    (Tuesday AM — neural networks)
    03_cnn_sea_ice.ipynb          (Tuesday PM — convolutional networks)
  requirements.txt              ← Python dependencies
  test_setup.ipynb              ← Environment verification
```

## Organisers

- Francesco Muschitiello (Geography)
- Alice Cicirello (Engineering)

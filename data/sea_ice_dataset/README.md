# Arctic Sea-Ice Image Classification Dataset

A small, balanced, ready-to-train image dataset for a CNN / image-classification
teaching practical. **No climate background needed** — it is just labelled
grayscale images in three classes.

---

## 1. What is this, in one paragraph

Each image is a 128×128 grayscale satellite view of a ~100 km patch of the Arctic
Ocean. The brightness of a pixel = **how much sea ice is there** (black = open
ocean, white = solid ice). The task is to classify each image into one of three
classes:

| Class | Folder name | Plain meaning | Looks like |
|-------|-------------|---------------|-----------|
| Open water | `open_water` | Ocean, essentially no ice | Uniform **black** |
| Marginal ice zone | `miz` | The messy *edge* where ice meets ocean — broken, partial ice | **Mottled gray**, gradients |
| Ice | `ice` | Mostly/fully ice-covered ocean | **Bright white**, faint texture |

The "marginal ice zone" (MIZ) is the interesting, hard class: it is the
transition between the other two. A good model has to learn texture/gradient, not
just average brightness.

See `collage.png` (example images per class), `sample_grid.png` (10 per class),
and `data_map.png` (where on the Arctic map the patches come from).

---

## 2. Where the data comes from

- **Instrument:** AMSR2, a *microwave* radiometer on the Japanese satellite
  GCOM-W1. Microwave sees **through clouds**, so unlike normal (optical) satellite
  photos there are no clouds to confuse the model — labels are clean.
- **Product:** "ASI" sea-ice **concentration** (percent of each grid cell covered
  by ice, 0–100%), daily, 3.125 km resolution, produced by the
  **University of Bremen** and distributed free, no login:
  <https://data.seaice.uni-bremen.de/>
- **What a pixel really is:** not a photograph — it is a physical measurement
  (% ice cover) rendered to gray: `gray = round(concentration_percent / 100 * 255)`.

This is why the dataset is "climate-related": it is real operational sea-ice data
used by scientists, but reduced to a clean image-classification problem.

---

## 3. How the labels were made (objective, no human guessing)

Each 128×128 image is a tile of the concentration map. Its label comes directly
from the measured ice concentration inside it:

- mean concentration **≤ 12 %** → `open_water`
- mean concentration **≥ 85 %** → `ice`
- mean concentration **18–78 %** AND ≥40 % of pixels are genuinely intermediate
  (15–80 %) → `miz`
- everything in between (ambiguous) is **discarded**, so classes are clean.

The MIZ rule (the "≥40 % intermediate" part) matters: it stops a tile that is
just half-black/half-white (a sharp edge averaging to 50 %) from being called MIZ.
Real MIZ contains actual partial-ice pixels.

---

## 4. Folder layout (standard, framework-friendly)

```
sea_ice_dataset/
├── train/            # 2023, training set
│   ├── ice/          # *.png
│   ├── open_water/
│   └── miz/
├── test/             # 2023, held-out dates (same year as train)
│   ├── ice/  open_water/  miz/
├── test_2019/        # 2019  — DIFFERENT year (see §6)
│   ├── ice/  open_water/  miz/
├── test_2024/        # 2024  — DIFFERENT year
│   ├── ice/  open_water/  miz/
├── README.md                ← this file
├── dataset_metadata.json    ← machine-readable summary
├── load_example.py          ← runnable sanity-check loader
├── make_dataset.py          ← exact script that generated everything (provenance)
├── collage.png  sample_grid.png  data_map.png
```

This is exactly the layout PyTorch `ImageFolder` and Keras
`image_dataset_from_directory` expect — class = subfolder name.

---

## 5. Counts (balanced)

| Split | Year | per class | total |
|-------|------|-----------|-------|
| `train`      | 2023 | 1600 | 4800 |
| `test`       | 2023 |  400 | 1200 |
| `test_2019`  | 2019 |  600 | 1800 |
| `test_2024`  | 2024 |  600 | 1800 |
| **Total** | | | **9600** |

All splits are balanced 1:1:1 across the three classes (random guessing = 33 %).

---

## 6. The two "other-year" test sets (a teaching point)

`train` and `test` are both from **summer 2023**, split **by date** (no date is in
both, so there is no leakage from near-identical neighbouring days).

`test_2019` and `test_2024` are from **different years**. The Arctic ice edge sits
in different places in different summers (2019 was a low-ice year). So:

- High accuracy on `test` but **lower** accuracy on `test_2019` / `test_2024`
  = the model overfit to 2023 conditions.
- Comparing the three test sets shows students **generalisation vs memorisation** —
  a real, visual example of distribution shift.

---

## 7. Quick start

Sanity check with no ML framework:

```bash
python load_example.py
```

PyTorch:

```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

tf = transforms.Compose([transforms.Grayscale(), transforms.ToTensor()])
train = datasets.ImageFolder("sea_ice_dataset/train", transform=tf)
test  = datasets.ImageFolder("sea_ice_dataset/test",  transform=tf)
print(train.classes)            # ['ice', 'miz', 'open_water']
loader = DataLoader(train, batch_size=64, shuffle=True)
x, y = next(iter(loader))
print(x.shape)                  # torch.Size([64, 1, 128, 128])
```

Keras / TensorFlow:

```python
import tensorflow as tf
train = tf.keras.utils.image_dataset_from_directory(
    "sea_ice_dataset/train", color_mode="grayscale",
    image_size=(128, 128), batch_size=64)
```

---

## 8. Image specs

- Format: PNG, **grayscale (1 channel)**, **128 × 128** px, 8-bit (0–255).
- Pixel value = ice concentration: **0 = open water (black), 255 = full ice (white)**.
- Filenames encode provenance: `<class>_<YYYY-MM-DD>_<tileRow>_<tileCol>.png`.

---

## 9. Honest caveats (worth telling students)

- **Effective resolution is ~3.125 km/pixel.** Each image is a 32×32 native
  measurement upscaled to 128×128 — the upscaling is cosmetic, it adds no real
  detail. Sea-ice concentration is a smooth field, not a sharp photo.
- **`open_water` is an "easy" class** (near-uniform black). A model can nail it on
  average brightness alone. That is fine/intentional — `miz` vs `ice` is the real
  challenge.
- **Region:** patches are sampled from the whole pan-Arctic ice edge (not one sea).
  Labels are physical, so region does not affect correctness.
- This is a **teaching dataset**, deliberately simple — not a research benchmark.

---

## 10. Attribution / citation

Sea-ice concentration data: **University of Bremen**, ASI algorithm, AMSR2,
version v5.4. Free for research and educational use **with citation**:

> Spreen, G., Kaleschke, L., and Heygster, G. (2008). Sea ice remote sensing using
> AMSR-E 89-GHz channels. *Journal of Geophysical Research*, 113, C02S03.
> doi:10.1029/2005JC003384

Data portal: <https://data.seaice.uni-bremen.de/> — please check their terms for
redistribution. Dataset packaged for an SRI 2025 / EARTHLAB CNN teaching practical.

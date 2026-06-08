#!/usr/bin/env python3
"""
Build a labelled sea-ice classification dataset for a CNN teaching practical.

Three classes: ice, open_water, marginal_ice_zone (MIZ).

Data source
-----------
University of Bremen ASI AMSR2 daily Arctic sea-ice concentration, the 3.125 km
"Arctic3125" grid, distributed as palette GeoTIFFs whose pixel index IS the
concentration:  0-100 = sea-ice concentration (%),  120 = land.
Publicly accessible, no authentication, readable directly by Pillow.
(NSIDC's own AMSR2 HTTPS endpoints require an Earthdata login; Bremen does not.)

Why concentration instead of MODIS true-colour
-----------------------------------------------
MODIS true-colour over the summer Arctic is dominated by cloud, and cloud is
spectrally near-identical to ice, so brightness labelling mislabels cloud as ice.
A GIBS cloud-fraction screen does not help: the L3 product flags bright ice as
"cloudy" too, so it strips ice/MIZ and leaves only water. Sea-ice concentration
is cloud-independent (microwave) and gives exact, physical labels.

Resolution
----------
3.125 km native (Arctic3125 grid, 3584 x 2432). Each patch is a TILE_PX-pixel
native window (~100 km) resized to OUT_PX. 3.125 km is the real limit of this ASI
product; concentration is a smooth field, so any display upscaling beyond native
is cosmetic, not new information.

Why the full Arctic instead of the Barents Sea alone
----------------------------------------------------
At concentration-grid resolution a 64-128 px patch covers ~100 km, far wider than
the marginal ice zone, so MIZ patches are rare. We sample the whole pan-Arctic
summer ice edge (which includes the Barents) to get enough MIZ. Labels are exact
regardless of region.

MIZ purity
----------
A tile whose MEAN lands in 18-78% could be genuine intermediate-concentration ice
OR a sharp 0%/100% edge that averages into range. We keep a tile as MIZ only if
>= MIZ_MIN_INTER of its pixels are themselves intermediate (15-80%), so MIZ
patches show real marginal ice, not edge-straddle artefacts.

Splits
------
sea_ice_dataset/train/{ice,open_water,miz}/        2023, train dates   (in-year)
sea_ice_dataset/test/{ice,open_water,miz}/         2023, held-out dates (in-year)
sea_ice_dataset/test_2019/{ice,open_water,miz}/    2019, out-of-sample year
sea_ice_dataset/test_2024/{ice,open_water,miz}/    2024, out-of-sample year
Splits are BY DATE (never by patch) so adjacent-day near-duplicate tiles cannot
leak between train and test. The 2019/2024 sets test generalisation to ice-edge
positions the model never saw in the 2023 calibration year.

Outputs also: sample_grid.png, collage.png, data_map.png
"""

import datetime
import os
import random

import numpy as np
import requests
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# ---------------------------------------------------------------- config
BASE = "https://data.seaice.uni-bremen.de/amsr2/asi_daygrid_swath/n3125"
REGION = "Arctic3125"
GRID = "n3125"
VERSION = "v5.4"
MONTHS = {6: "jun", 7: "jul", 8: "aug"}

LAND = 120
TILE_PX = 32             # native tile (~100 km at 3.125 km/px), real 32x32 samples
OUT_PX = 128             # delivered patch size
MIN_VALID = 0.98
MAX_LAND = 0.02

WATER_MAX = 12.0
MIZ_LO, MIZ_HI = 18.0, 78.0
ICE_MIN = 85.0
INTER_LO, INTER_HI = 15.0, 80.0
MIZ_MIN_INTER = 0.40

# in-year (2023) caps -> 1600 train + 400 test = 2000/class
TRAIN_CAP = 1600
TEST_CAP = 400
TEST_FRAC = 0.20
# out-of-sample year caps
OUTYEAR_CAP = 600

SEED = 20230601
RAW_DIR = "sea_ice_build/raw3125"
OUT_DIR = "sea_ice_dataset"
CLASSES = ["ice", "open_water", "miz"]


def season_dates(year, step):
    out, d, end = [], datetime.date(year, 6, 1), datetime.date(year, 8, 31)
    while d <= end:
        out.append(d.isoformat())
        d += datetime.timedelta(days=step)
    return out


DATES_2023 = season_dates(2023, 3)            # ~31 dates
TEST_2023 = set(DATES_2023[3::5])             # ~6 held-out dates, spread
TRAIN_2023 = [d for d in DATES_2023 if d not in TEST_2023]
OUT_YEARS = {"2019": season_dates(2019, 8), "2024": season_dates(2024, 8)}  # ~12 each

# ---------------------------------------------------------------- download
def url_for(date_str):
    y, m, d = date_str.split("-")
    fname = f"asi-AMSR2-{GRID}-{y}{m}{d}-{VERSION}.tif"
    return f"{BASE}/{y}/{MONTHS[int(m)]}/{REGION}/{fname}", fname


def download(date_list, label):
    os.makedirs(RAW_DIR, exist_ok=True)
    paths = []
    for date_str in date_list:
        url, fname = url_for(date_str)
        dest = os.path.join(RAW_DIR, fname)
        if not os.path.exists(dest):
            try:
                r = requests.get(url, timeout=180)
            except Exception as e:
                print(f"  SKIP {date_str}: {e}"); continue
            if r.status_code != 200 or r.headers.get("content-type", "").startswith("text"):
                print(f"  SKIP {date_str}: HTTP {r.status_code}"); continue
            with open(dest, "wb") as f:
                f.write(r.content)
        paths.append((date_str, dest))
    print(f"  {label}: {len(paths)}/{len(date_list)} scenes")
    return paths


# ---------------------------------------------------------------- patchify
def classify(mean_conc, frac_inter):
    if mean_conc <= WATER_MAX:
        return "open_water"
    if mean_conc >= ICE_MIN:
        return "ice"
    if MIZ_LO <= mean_conc <= MIZ_HI and frac_inter >= MIZ_MIN_INTER:
        return "miz"
    return None


def tile_to_image(tile):
    g = np.clip(tile, 0, 100) / 100.0 * 255.0
    return Image.fromarray(g.astype(np.uint8)).resize((OUT_PX, OUT_PX), Image.BILINEAR)


def extract(scene_paths):
    """Return pool[class] -> list of (image, tag='date_i_j')."""
    pool = {c: [] for c in CLASSES}
    for date_str, path in scene_paths:
        a = np.array(Image.open(path)).astype(float)
        H, W = a.shape
        for i in range(H // TILE_PX):
            for j in range(W // TILE_PX):
                t = a[i * TILE_PX:(i + 1) * TILE_PX, j * TILE_PX:(j + 1) * TILE_PX]
                if np.mean(t == LAND) > MAX_LAND:
                    continue
                oc = t[t != LAND]
                if oc.size < t.size * MIN_VALID:
                    continue
                frac_inter = float(np.mean((oc >= INTER_LO) & (oc <= INTER_HI)))
                label = classify(float(oc.mean()), frac_inter)
                if label:
                    pool[label].append((tile_to_image(t), f"{date_str}_{i}_{j}"))
    return pool


def balanced_sample(pool, n_per, rng):
    out = {}
    for c in CLASSES:
        items = list(pool[c]); rng.shuffle(items); out[c] = items[:n_per]
    return out


def write_split(chosen, subdir):
    for c in CLASSES:
        d = os.path.join(OUT_DIR, subdir, c); os.makedirs(d, exist_ok=True)
        for img, tag in chosen[c]:
            img.save(os.path.join(d, f"{c}_{tag}.png"))


# ---------------------------------------------------------------- figures
COL = {"open_water": "#1f77ff", "miz": "#ff9900", "ice": "#e8e8e8"}


def sample_grid(chosen):
    rng = random.Random(SEED + 1)
    order = ["open_water", "miz", "ice"]; ncol = 10
    fig, ax = plt.subplots(len(order), ncol, figsize=(ncol, len(order) + 0.6))
    for r, c in enumerate(order):
        picks = rng.sample(chosen[c], min(ncol, len(chosen[c])))
        for k in range(ncol):
            a = ax[r, k]; a.axis("off")
            if k < len(picks):
                a.imshow(np.array(picks[k][0]), cmap="gray", vmin=0, vmax=255)
            if k == 0:
                a.axis("on"); a.set_xticks([]); a.set_yticks([])
                a.set_ylabel(c, rotation=0, ha="right", va="center", fontsize=11)
    fig.suptitle("AMSR2 3.125 km concentration patches (dark=water -> bright=ice)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(OUT_DIR, "sample_grid.png"), dpi=110); plt.close(fig)


def collage(chosen):
    rng = random.Random(SEED + 2)
    from PIL import ImageDraw
    cols, rpc, cell = 16, 3, 70
    W = cols * cell; H = len(CLASSES) * (rpc * cell + 22)
    sheet = Image.new("RGB", (W, H), (15, 15, 15)); dr = ImageDraw.Draw(sheet); y = 0
    for c in ["open_water", "miz", "ice"]:
        rgb = tuple(int(COL[c].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        dr.rectangle([0, y, W, y + 20], fill=rgb)
        dr.text((6, y + 5), f"{c}  (n={len(chosen[c])})", fill=(0, 0, 0)); y += 22
        picks = rng.sample(chosen[c], min(cols * rpc, len(chosen[c])))
        for k, (img, _) in enumerate(picks):
            r, cc = divmod(k, cols)
            sheet.paste(img.convert("L").resize((cell - 4, cell - 4)), (cc * cell + 2, y + r * cell + 2))
        y += rpc * cell
    sheet.save(os.path.join(OUT_DIR, "collage.png"))


def data_map(chosen_inyear, scene_paths):
    import re
    stack = []
    for _, p in scene_paths:
        a = np.array(Image.open(p)).astype(float); a[a == LAND] = np.nan; a[a > 100] = np.nan
        stack.append(a)
    bg = np.nanmean(np.dstack(stack), 2); H0, W0 = bg.shape
    land0 = np.array(Image.open(scene_paths[0][1]))
    fig, ax = plt.subplots(figsize=(9, 12))
    ax.imshow(bg, cmap="Blues_r", vmin=0, vmax=100)
    ax.imshow(np.where(land0 == LAND, 1.0, np.nan), cmap="Greys", vmin=0, vmax=1.6, alpha=0.6)
    pat = re.compile(r"(\d{4}-\d\d-\d\d)_(\d+)_(\d+)$"); cnt = {c: 0 for c in CLASSES}
    for c in CLASSES:
        for _, tag in chosen_inyear[c]:
            m = pat.search(tag)
            if not m:
                continue
            i, j = int(m.group(2)), int(m.group(3))
            ax.add_patch(Rectangle((j * TILE_PX, i * TILE_PX), TILE_PX, TILE_PX,
                                   facecolor=COL[c], edgecolor="none", alpha=0.08))
            cnt[c] += 1
    ax.set_xlim(0, W0); ax.set_ylim(H0, 0); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("2023 patch locations on AMSR2 Arctic3125 grid (3.125 km)\n"
                 "bg = mean Jun-Aug 2023 concentration; gray = land", fontsize=11)
    leg = [Line2D([0], [0], marker="s", color="w", markerfacecolor=COL[c], markersize=12,
                  label=f"{c} (n={cnt[c]})") for c in CLASSES]
    ax.legend(handles=leg, loc="lower left", framealpha=0.9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, "data_map.png"), dpi=110); plt.close(fig)


def dir_size_mb(path):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs) / 1e6


# ---------------------------------------------------------------- main
def main():
    rng = random.Random(SEED)

    print("1) downloading 2023 (in-year) ...")
    train_paths = download(TRAIN_2023, "train-dates")
    test_paths = download(sorted(TEST_2023), "test-dates")

    print("2) extracting 2023 patches ...")
    train_pool = extract(train_paths)
    test_pool = extract(test_paths)
    tr = {c: len(train_pool[c]) for c in CLASSES}
    te = {c: len(test_pool[c]) for c in CLASSES}
    print("   train-pool:", tr)
    print("   test-pool :", te)

    n_test = min(TEST_CAP, min(te.values()), min(tr.values()) // 4)
    n_train = min(TRAIN_CAP, 4 * n_test)
    n_test = n_train // 4
    print(f"   -> {n_train} train + {n_test} test per class")

    chosen_train = balanced_sample(train_pool, n_train, rng)
    chosen_test = balanced_sample(test_pool, n_test, rng)
    write_split(chosen_train, "train")
    write_split(chosen_test, "test")

    chosen_all = {c: chosen_train[c] + chosen_test[c] for c in CLASSES}

    print("3) out-of-sample years ...")
    for year, dates in OUT_YEARS.items():
        paths = download(dates, f"{year}")
        pool = extract(paths)
        counts = {c: len(pool[c]) for c in CLASSES}
        n_out = min(OUTYEAR_CAP, min(counts.values()))
        print(f"   {year} pool {counts} -> {n_out}/class")
        write_split(balanced_sample(pool, n_out, rng), f"test_{year}")

    print("4) figures ...")
    sample_grid(chosen_train)
    collage(chosen_train)
    data_map(chosen_all, train_paths + test_paths)

    print("\nDONE")
    print(f"  in-year 2023: {n_train} train + {n_test} test per class")
    print(f"  out-of-sample: test_2019, test_2024")
    print(f"  dataset size: {dir_size_mb(OUT_DIR):.1f} MB")
    print("\nCAVEATS (tell the workshop):")
    print("  * Grayscale = AMSR2 ice concentration (dark=water, bright=ice).")
    print("  * Native 3.125 km; OUT_PX is upscaled from 32x32 real samples (cosmetic).")
    print("  * 'miz' = tiles with >=40% genuinely intermediate-concentration pixels.")
    print("  * 'open_water' is a near-uniform 0% easy class (physically correct).")
    print("  * Pan-Arctic ice edge sampled (incl. Barents); labels region-agnostic.")
    print("  * train/test split BY DATE; test_2019 & test_2024 test cross-year generalisation.")


if __name__ == "__main__":
    main()

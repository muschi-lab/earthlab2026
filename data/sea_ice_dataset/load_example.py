#!/usr/bin/env python3
"""
Sanity-check loader for the Arctic Sea-Ice dataset. Pure stdlib + Pillow + numpy,
no ML framework needed. Run from the folder that contains `sea_ice_dataset/`,
or from inside it.

    python load_example.py
"""
import glob
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE  # README + splits live together
SPLITS = ["train", "test", "test_2019", "test_2024"]
CLASSES = ["ice", "open_water", "miz"]


def main():
    print("Arctic Sea-Ice dataset — summary\n" + "-" * 40)
    grand = 0
    for split in SPLITS:
        line = [f"{split:11s}"]
        for c in CLASSES:
            n = len(glob.glob(os.path.join(ROOT, split, c, "*.png")))
            line.append(f"{c}={n}")
            grand += n
        print("  " + "  ".join(line))
    print("-" * 40 + f"\n  TOTAL images: {grand}\n")

    print("One sample per class (train) — value 0=water .. 255=ice:")
    for c in CLASSES:
        fs = glob.glob(os.path.join(ROOT, "train", c, "*.png"))
        if not fs:
            continue
        a = np.array(Image.open(fs[0]))
        print(f"  {c:11s} shape={a.shape} dtype={a.dtype} "
              f"mean={a.mean():6.1f} std={a.std():5.1f}  ({os.path.basename(fs[0])})")

    print("\nClass mean-brightness should rank: open_water < miz < ice")


if __name__ == "__main__":
    main()

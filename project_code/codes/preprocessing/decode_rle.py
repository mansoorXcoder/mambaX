import os
import numpy as np
import pandas as pd
import tifffile as tiff
import matplotlib.pyplot as plt
from PIL import Image

# =====================================
# PROJECT PATHS
# =====================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "metadata",
    "train.csv"
)

TIFF_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "raw_tiff"
)

MASK_OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "generated_masks"
)

os.makedirs(MASK_OUTPUT_DIR, exist_ok=True)

# =====================================
# LOAD CSV
# =====================================

df = pd.read_csv(CSV_PATH)

print(f"\nCSV Loaded Successfully")
print(f"Total Rows: {len(df)}")

# =====================================
# GET TIFF FILES
# =====================================

tiff_files = [
    f for f in os.listdir(TIFF_DIR)
    if f.endswith(".tiff") or f.endswith(".tif")
]

if len(tiff_files) == 0:
    raise Exception("No TIFF files found!")

print(f"\nFound {len(tiff_files)} TIFF files")

# =====================================
# RLE DECODER
# =====================================

def rle_decode(mask_rle, shape):

    s = mask_rle.split()

    starts = np.asarray(s[0::2], dtype=int)
    lengths = np.asarray(s[1::2], dtype=int)

    starts -= 1

    ends = starts + lengths

    img = np.zeros(shape[0] * shape[1], dtype=np.uint8)

    for start, end in zip(starts, ends):
        img[start:end] = 1

    return img.reshape(shape).T

# =====================================
# PROCESS ALL TIFF FILES
# =====================================

for selected_tiff in tiff_files:

    print("\n===================================")
    print(f"Processing: {selected_tiff}")
    print("===================================")

    image_id = os.path.splitext(selected_tiff)[0]

    print(f"\nImage ID:")
    print(image_id)

    # =====================================
    # MATCH CSV ROW
    # =====================================

    row = df[df["id"] == image_id]

    if len(row) == 0:
        print(f"\nNo matching CSV row found for: {image_id}")
        continue

    rle = row.iloc[0]["encoding"]

    print("\nMatching RLE Encoding Found")

    # =====================================
    # LOAD TIFF IMAGE
    # =====================================

    tiff_path = os.path.join(TIFF_DIR, selected_tiff)

    print("\nLoading TIFF image...")

    image = tiff.imread(tiff_path)

    height, width = image.shape[:2]

    print(f"\nImage Shape: {image.shape}")

    # =====================================
    # GENERATE MASK
    # =====================================

    print("\nGenerating mask...")

    mask = rle_decode(rle, (width, height))

    print("\nMask Generated Successfully")

    # =====================================
    # SAVE MASK
    # =====================================

    mask_image = (mask * 255).astype(np.uint8)

    mask_save_path = os.path.join(
        MASK_OUTPUT_DIR,
        f"{image_id}_mask.png"
    )

    Image.fromarray(mask_image).save(mask_save_path)

    print(f"\nMask saved at:")
    print(mask_save_path)

    # =====================================
    # LIGHTWEIGHT VISUALIZATION
    # =====================================

    print("\nCreating lightweight preview...")

    preview_image = image[::32, ::32]
    preview_mask = mask[::32, ::32]

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(preview_image)
    plt.title(f"{image_id} TIFF")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(preview_mask, cmap="gray")
    plt.title(f"{image_id} Mask")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

# =====================================
# FINAL MESSAGE
# =====================================

print("\n===================================")
print("ALL TIFF MASKS GENERATED SUCCESSFULLY")
print("===================================")
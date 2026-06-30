import os
import numpy as np
import tifffile as tiff
from PIL import Image

# Allow very large pathology images
Image.MAX_IMAGE_PIXELS = None

# =========================================
# PROJECT PATHS
# =========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TIFF_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "raw_tiff"
)

MASK_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "generated_masks"
)

PATCH_IMAGE_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "extracted_patches",
    "images"
)

PATCH_MASK_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "extracted_patches",
    "masks"
)

os.makedirs(PATCH_IMAGE_DIR, exist_ok=True)
os.makedirs(PATCH_MASK_DIR, exist_ok=True)

# =========================================
# PATCH SETTINGS
# =========================================

PATCH_SIZE = 512

# Overlapping extraction
STRIDE = 256

# Allow more useful patches
MAX_PATCHES_PER_TIFF = 400

# =========================================
# GET TIFF FILES
# =========================================

tiff_files = [
    f for f in os.listdir(TIFF_DIR)
    if f.endswith(".tiff") or f.endswith(".tif")
]

print(f"\nFound {len(tiff_files)} TIFF files")

# =========================================
# PROCESS EACH TIFF
# =========================================

for selected_tiff in tiff_files:

    print("\n===================================")
    print(f"Processing TIFF: {selected_tiff}")
    print("===================================")

    image_id = os.path.splitext(selected_tiff)[0]

    # =====================================
    # LOAD TIFF
    # =====================================

    tiff_path = os.path.join(TIFF_DIR, selected_tiff)

    print("\nLoading TIFF image...")

    image = tiff.imread(tiff_path)

    print(f"TIFF Shape: {image.shape}")

    # =====================================
    # LOAD GENERATED MASK
    # =====================================

    mask_path = os.path.join(
        MASK_DIR,
        f"{image_id}_mask.png"
    )

    if not os.path.exists(mask_path):
        print(f"\nMask not found for {image_id}")
        continue

    mask = np.array(Image.open(mask_path))

    print("Mask loaded successfully")

    # =====================================
    # PATCH EXTRACTION
    # =====================================

    height, width = mask.shape

    saved_count = 0
    rejected_count = 0

    print("\nStarting patch extraction...")

    for y in range(0, height - PATCH_SIZE, STRIDE):

        for x in range(0, width - PATCH_SIZE, STRIDE):

            # ---------------------------------
            # IMAGE PATCH
            # ---------------------------------

            image_patch = image[
                y:y + PATCH_SIZE,
                x:x + PATCH_SIZE
            ]

            # ---------------------------------
            # MASK PATCH
            # ---------------------------------

            mask_patch = mask[
                y:y + PATCH_SIZE,
                x:x + PATCH_SIZE
            ]

            # ---------------------------------
            # FILTER 1
            # REMOVE WHITE BACKGROUND
            # ---------------------------------

            tissue_mean = np.mean(image_patch)

            if tissue_mean > 235:
                rejected_count += 1
                continue

            # ---------------------------------
            # FILTER 1B
            # REMOVE LOW-INFORMATION PATCHES
            # ---------------------------------
            
            tissue_std = np.std(image_patch)
            
            if tissue_std < 8:
                rejected_count += 1
                continue

            # ---------------------------------
            # FILTER 2
            # REQUIRE GLOMERULI
            # ---------------------------------
            mask_pixels = np.sum(mask_patch > 0)
            
            mask_ratio = mask_pixels / (PATCH_SIZE * PATCH_SIZE)

            # Reject patches dominated by mask
            if mask_ratio > 0.80:
                rejected_count += 1
                continue

            # Reject tiny glomerulus fragments
            if mask_pixels < 3000:
                rejected_count += 1
                continue

            # ---------------------------------
            # FILTER 3
            # REJECT BORDER-CUT OBJECTS
            # ---------------------------------

            top_edge = np.sum(mask_patch[0, :] > 0)
            bottom_edge = np.sum(mask_patch[-1, :] > 0)

            left_edge = np.sum(mask_patch[:, 0] > 0)
            right_edge = np.sum(mask_patch[:, -1] > 0)

            edge_pixels = (
                top_edge
                + bottom_edge
                + left_edge
                + right_edge
            )

            if edge_pixels > 100:
                rejected_count += 1
                continue

            # ---------------------------------
            # SAVE PATCHES
            # ---------------------------------

            patch_name = f"{image_id}_{saved_count}"

            image_save_path = os.path.join(
                PATCH_IMAGE_DIR,
                patch_name + ".png"
            )

            mask_save_path = os.path.join(
                PATCH_MASK_DIR,
                patch_name + "_mask.png"
            )

            Image.fromarray(image_patch).save(image_save_path)

            Image.fromarray(mask_patch).save(mask_save_path)

            saved_count += 1

            # ---------------------------------
            # LIMIT FOR FIRST TEST
            # ---------------------------------

            if saved_count >= MAX_PATCHES_PER_TIFF:
                break

        if saved_count >= MAX_PATCHES_PER_TIFF:
            break

    # =====================================
    # TIFF SUMMARY
    # =====================================

    print("\n-----------------------------------")
    print(f"TIFF Completed: {image_id}")
    print(f"Saved Patches: {saved_count}")
    print(f"Rejected Patches: {rejected_count}")
    print("-----------------------------------")

# =========================================
# FINAL SUMMARY
# =========================================

print("\n===================================")
print("PATCH EXTRACTION COMPLETED")
print("===================================")

print(f"\nImage patches saved at:")
print(PATCH_IMAGE_DIR)

print(f"\nMask patches saved at:")
print(PATCH_MASK_DIR)
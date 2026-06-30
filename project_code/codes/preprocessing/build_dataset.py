import os
import random
import shutil

# =====================================
# PATHS
# =====================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMAGES_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "extracted_patches",
    "images"
)

MASKS_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "extracted_patches",
    "masks"
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset"
)

# =====================================
# OUTPUT FOLDERS
# =====================================

TRAIN_IMAGES = os.path.join(PROCESSED_DIR, "train", "images")
TRAIN_MASKS = os.path.join(PROCESSED_DIR, "train", "masks")

VAL_IMAGES = os.path.join(PROCESSED_DIR, "val", "images")
VAL_MASKS = os.path.join(PROCESSED_DIR, "val", "masks")

TEST_IMAGES = os.path.join(PROCESSED_DIR, "test", "images")
TEST_MASKS = os.path.join(PROCESSED_DIR, "test", "masks")

folders = [
    TRAIN_IMAGES, TRAIN_MASKS,
    VAL_IMAGES, VAL_MASKS,
    TEST_IMAGES, TEST_MASKS
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# =====================================
# LOAD IMAGE FILES
# =====================================

image_files = sorted([
    f for f in os.listdir(IMAGES_DIR)
    if f.endswith(".png")
])

print(f"\nTotal Images Found: {len(image_files)}")

# =====================================
# SHUFFLE
# =====================================

random.seed(42)
random.shuffle(image_files)

# =====================================
# SPLIT
# =====================================

total = len(image_files)

train_end = int(total * 0.70)
val_end = int(total * 0.85)

train_files = image_files[:train_end]
val_files = image_files[train_end:val_end]
test_files = image_files[val_end:]

print(f"\nTrain: {len(train_files)}")
print(f"Validation: {len(val_files)}")
print(f"Test: {len(test_files)}")

# =====================================
# COPY FUNCTION
# =====================================

def copy_dataset(files, image_dest, mask_dest):

    for image_name in files:

        mask_name = image_name.replace(
            ".png",
            "_mask.png"
        )

        image_src = os.path.join(
            IMAGES_DIR,
            image_name
        )

        mask_src = os.path.join(
            MASKS_DIR,
            mask_name
        )

        shutil.copy2(
            image_src,
            os.path.join(image_dest, image_name)
        )

        shutil.copy2(
            mask_src,
            os.path.join(mask_dest, mask_name)
        )

# =====================================
# BUILD DATASET
# =====================================

print("\nCreating Train Dataset...")
copy_dataset(
    train_files,
    TRAIN_IMAGES,
    TRAIN_MASKS
)

print("Creating Validation Dataset...")
copy_dataset(
    val_files,
    VAL_IMAGES,
    VAL_MASKS
)

print("Creating Test Dataset...")
copy_dataset(
    test_files,
    TEST_IMAGES,
    TEST_MASKS
)

print("\nDataset Split Complete!")
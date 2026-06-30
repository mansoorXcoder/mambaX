import os

import torch
import numpy as np
import cv2

import matplotlib.pyplot as plt

from PIL import Image

from dataset import KidneyDataset
from model import AttentionUNet

from torch.utils.data import DataLoader


# =====================================
# DEVICE
# =====================================

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

print(f"\nUsing Device: {device}")

# =====================================
# PATHS
# =====================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

TEST_IMAGES = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset",
    "test",
    "images"
)

TEST_MASKS = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset",
    "test",
    "masks"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "checkpoints",
    "best_attention_unet.pth"
)

PRED_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "predictions",
    "test_masks"
)

OVERLAY_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "overlays"
)

os.makedirs(PRED_DIR, exist_ok=True)
os.makedirs(OVERLAY_DIR, exist_ok=True)

VIS_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "visualizations"
)

os.makedirs(
    VIS_DIR,
    exist_ok=True
)

# =====================================
# DATASET
# =====================================

test_dataset = KidneyDataset(
    TEST_IMAGES,
    TEST_MASKS
)

test_loader = DataLoader(
    test_dataset,
    batch_size=1,
    shuffle=False
)

print(
    f"\nTest Samples: {len(test_dataset)}"
)

# =====================================
# MODEL
# =====================================

model = AttentionUNet().to(device)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device
    )
)

model.eval()

print("\nBest Model Loaded")

print(
    f"Loaded Model: {MODEL_PATH}"
)

# =====================================
# METRICS
# =====================================

def dice_score(preds, masks):

    intersection = (
        preds * masks
    ).sum()

    return (
        (2 * intersection + 1e-8)
        /
        (
            preds.sum()
            + masks.sum()
            + 1e-8
        )
    ).item()


def iou_score(preds, masks):

    intersection = (
        preds * masks
    ).sum()

    union = (
        preds + masks
    ).clamp(0, 1).sum()

    return (
        (intersection + 1e-8)
        /
        (union + 1e-8)
    ).item()

# =====================================
# TEST LOOP
# =====================================

total_dice = 0
total_iou = 0

with torch.no_grad():

    for idx, (image, mask) in enumerate(test_loader):

        image = image.to(device)
        mask = mask.to(device)

        output = model(image)

        pred = torch.sigmoid(output)

        pred = (
            pred > 0.5
        ).float()

        total_dice += dice_score(
            pred,
            mask
        )

        total_iou += iou_score(
            pred,
            mask
        )

        # -------------------------
        # SAVE PREDICTED MASK
        # -------------------------

        pred_np = (
            pred.squeeze()
            .cpu()
            .numpy()
            * 255
        ).astype(np.uint8)

        pred_img = Image.fromarray(
            pred_np
        )

        pred_path = os.path.join(
            PRED_DIR,
            f"prediction_{idx}.png"
        )

        pred_img.save(pred_path)

        # -------------------------
        # SAVE OVERLAY
        # -------------------------

        image_np = (
            image.squeeze()
            .permute(1, 2, 0)
            .cpu()
            .numpy()
            * 255
        ).astype(np.uint8)

        green_mask = np.zeros_like(
            image_np,
            dtype=np.uint8
        )

        green_mask[:, :, 1] = pred_np

        overlay = cv2.addWeighted(
            image_np,
            1.0,
            green_mask,
            0.45,
            0
        )

        overlay_img = Image.fromarray(
           overlay
        )

        overlay_path = os.path.join(
            OVERLAY_DIR,
            f"overlay_{idx}.png"
        )

        overlay_img.save(
            overlay_path
        )

                # -------------------------
        # VISUALIZATION PANEL
        # -------------------------

        gt_np = (
            mask.squeeze()
            .cpu()
            .numpy()
        )

        fig, ax = plt.subplots(
            1,
            4,
            figsize=(16, 4)
        )

        ax[0].imshow(image_np)
        ax[0].set_title("Original")
        ax[0].axis("off")

        ax[1].imshow(
            gt_np,
            cmap="Blues"
        )
        ax[1].set_title("Ground Truth")
        ax[1].axis("off")

        ax[2].imshow(
            pred_np,
            cmap="Greens"
        )
        ax[2].set_title("Prediction")
        ax[2].axis("off")

        ax[3].imshow(image_np)

        ax[3].imshow(
            pred_np,
            cmap="Greens",
            alpha=0.35
        )

        ax[3].set_title("Overlay")
        ax[3].axis("off")

        vis_path = os.path.join(
            VIS_DIR,
            f"visualization_{idx}.png"
        )

        plt.tight_layout()

        plt.savefig(
            vis_path,
            bbox_inches="tight"
        )

        plt.close()


# =====================================
# RESULTS
# =====================================

avg_dice = (
    total_dice
    /
    len(test_loader)
)

avg_iou = (
    total_iou
    /
    len(test_loader)
)

print("\n===================")
print("TEST RESULTS")
print("===================")

print(
    f"Test Dice: {avg_dice:.4f}"
)

print(
    f"Test IoU: {avg_iou:.4f}"
)

print(
    "\nPrediction Masks Saved"
)

print(
    "Overlay Images Saved"
)
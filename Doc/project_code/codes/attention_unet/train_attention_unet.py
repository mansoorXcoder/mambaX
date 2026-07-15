import os

import torch
import torch.nn as nn

import random
import numpy as np

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)

from torch.amp import autocast
from torch.amp import GradScaler
from torch.utils.data import DataLoader

from dataset import KidneyDataset
from model import AttentionUNet

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

TRAIN_IMAGES = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset",
    "train",
    "images"
)

TRAIN_MASKS = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset",
    "train",
    "masks"
)

VAL_IMAGES = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset",
    "val",
    "images"
)

VAL_MASKS = os.path.join(
    BASE_DIR,
    "datasets",
    "processed_dataset",
    "val",
    "masks"
)

CHECKPOINT_PATH = os.path.join(
    BASE_DIR,
    "models",
    "checkpoints",
    "best_attention_unet_earlystop.pth"
)

# =====================================
# DATASETS
# =====================================

train_dataset = KidneyDataset(
    TRAIN_IMAGES,
    TRAIN_MASKS
)

val_dataset = KidneyDataset(
    VAL_IMAGES,
    VAL_MASKS
)

# =====================================
# DATALOADERS
# =====================================

train_loader = DataLoader(
    train_dataset,
    batch_size=4,
    shuffle=True,
    num_workers=0,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=4,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)

print(f"\nTrain Samples: {len(train_dataset)}")
print(f"Validation Samples: {len(val_dataset)}")

# =====================================
# MODEL
# =====================================

model = AttentionUNet().to(device)

criterion = nn.BCEWithLogitsLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.0001
)

scaler = GradScaler("cuda")

# =====================================
# DICE SCORE
# =====================================

def dice_score(preds, masks):

    preds = torch.sigmoid(preds)

    preds = (preds > 0.5).float()

    intersection = (preds * masks).sum()

    return (
        (2.0 * intersection + 1e-8)
        /
        (preds.sum() + masks.sum() + 1e-8)
    ).item()

# =====================================
# TRAINING
# =====================================

EPOCHS = 10

best_dice = 0

patience = 5

counter = 0

for epoch in range(EPOCHS):

    print(f"\nStarting Epoch {epoch+1}")

    model.train()

    train_loss = 0

    for images, masks in train_loader:

        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()

        with autocast("cuda"):

            outputs = model(images)

            loss = criterion(
                 outputs,
                 masks
            )

        scaler.scale(loss).backward()

        scaler.step(optimizer)

        scaler.update()

        train_loss += loss.item()

    train_loss /= len(train_loader)

    # ==========================
    # VALIDATION
    # ==========================

    model.eval()

    val_dice = 0

    with torch.no_grad():

        for images, masks in val_loader:

            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)

            val_dice += dice_score(
                outputs,
                masks
            )

    val_dice /= len(val_loader)

    print(
        f"\nEpoch {epoch+1}/{EPOCHS}"
    )

    print(
        f"Train Loss: {train_loss:.4f}"
    )

    print(
        f"Val Dice: {val_dice:.4f}"
    )

    # ==========================
    # SAVE BEST MODEL
    # ==========================

    if val_dice > best_dice:

        best_dice = val_dice

        counter = 0

        torch.save(
            model.state_dict(),
            CHECKPOINT_PATH
        )

        print(
            "Best model saved!"
        )
    
    else:
               
        counter += 1
                                           
        print(
            f"No improvement ({counter}/{patience})"
        )

        if counter >= patience:
                                               
            print(
                "\nEarly Stopping Triggered!"
            )

            break
print("\nTraining Complete!")
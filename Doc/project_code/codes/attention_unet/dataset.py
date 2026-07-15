import os

from PIL import Image

import torch
from torch.utils.data import Dataset

from torchvision import transforms


class KidneyDataset(Dataset):

    def __init__(self, image_dir, mask_dir):

        self.image_dir = image_dir
        self.mask_dir = mask_dir

        self.images = sorted(
            [f for f in os.listdir(image_dir) if f.endswith(".png")]
        )

        self.transform = transforms.ToTensor()

    def __len__(self):

        return len(self.images)

    def __getitem__(self, idx):

        image_name = self.images[idx]

        mask_name = image_name.replace(
            ".png",
            "_mask.png"
        )

        image_path = os.path.join(
            self.image_dir,
            image_name
        )

        mask_path = os.path.join(
            self.mask_dir,
            mask_name
        )

        image = Image.open(image_path).convert("RGB")

        mask = Image.open(mask_path).convert("L")

        image = self.transform(image)

        mask = self.transform(mask)

        mask = (mask > 0).float()

        return image, mask
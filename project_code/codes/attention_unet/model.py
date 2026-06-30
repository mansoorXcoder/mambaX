import torch
import torch.nn as nn


# =====================================
# DOUBLE CONV
# =====================================

class DoubleConv(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.conv = nn.Sequential(

            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True)
        )

    def forward(self, x):

        return self.conv(x)


# =====================================
# ATTENTION BLOCK
# =====================================

class AttentionBlock(nn.Module):

    def __init__(
        self,
        gate_channels,
        skip_channels,
        inter_channels
    ):

        super().__init__()

        self.W_g = nn.Sequential(

            nn.Conv2d(
                gate_channels,
                inter_channels,
                kernel_size=1
            ),

            nn.BatchNorm2d(
                inter_channels
            )
        )

        self.W_x = nn.Sequential(

            nn.Conv2d(
                skip_channels,
                inter_channels,
                kernel_size=1
            ),

            nn.BatchNorm2d(
                inter_channels
            )
        )

        self.psi = nn.Sequential(

            nn.Conv2d(
                inter_channels,
                1,
                kernel_size=1
            ),

            nn.BatchNorm2d(1),

            nn.Sigmoid()
        )

        self.relu = nn.ReLU(
            inplace=True
        )

    def forward(self, g, x):

        g1 = self.W_g(g)

        x1 = self.W_x(x)

        psi = self.relu(
            g1 + x1
        )

        psi = self.psi(psi)

        return x * psi


# =====================================
# ATTENTION U-NET
# =====================================

class AttentionUNet(nn.Module):

    def __init__(self):

        super().__init__()

        self.pool = nn.MaxPool2d(2)

        # Encoder

        self.down1 = DoubleConv(3, 64)

        self.down2 = DoubleConv(
            64,
            128
        )

        self.down3 = DoubleConv(
            128,
            256
        )

        # Bottleneck

        self.bottleneck = DoubleConv(
            256,
            512
        )

        # Decoder

        self.up3 = nn.ConvTranspose2d(
            512,
            256,
            kernel_size=2,
            stride=2
        )

        self.att3 = AttentionBlock(
            gate_channels=256,
            skip_channels=256,
            inter_channels=128
        )

        self.conv3 = DoubleConv(
            512,
            256
        )

        self.up2 = nn.ConvTranspose2d(
            256,
            128,
            kernel_size=2,
            stride=2
        )

        self.att2 = AttentionBlock(
            gate_channels=128,
            skip_channels=128,
            inter_channels=64
        )

        self.conv2 = DoubleConv(
            256,
            128
        )

        self.up1 = nn.ConvTranspose2d(
            128,
            64,
            kernel_size=2,
            stride=2
        )

        self.att1 = AttentionBlock(
            gate_channels=64,
            skip_channels=64,
            inter_channels=32
        )

        self.conv1 = DoubleConv(
            128,
            64
        )

        self.final = nn.Conv2d(
            64,
            1,
            kernel_size=1
        )

    def forward(self, x):

        d1 = self.down1(x)

        d2 = self.down2(
            self.pool(d1)
        )

        d3 = self.down3(
            self.pool(d2)
        )

        bottleneck = self.bottleneck(
            self.pool(d3)
        )

        # Decoder Level 3

        u3 = self.up3(
            bottleneck
        )

        d3_att = self.att3(
            u3,
            d3
        )

        u3 = torch.cat(
            [u3, d3_att],
            dim=1
        )

        u3 = self.conv3(u3)

        # Decoder Level 2

        u2 = self.up2(u3)

        d2_att = self.att2(
            u2,
            d2
        )

        u2 = torch.cat(
            [u2, d2_att],
            dim=1
        )

        u2 = self.conv2(u2)

        # Decoder Level 1

        u1 = self.up1(u2)

        d1_att = self.att1(
            u1,
            d1
        )

        u1 = torch.cat(
            [u1, d1_att],
            dim=1
        )

        u1 = self.conv1(u1)

        return self.final(u1)
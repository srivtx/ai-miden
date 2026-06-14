"""
DDPM on MNIST (PyTorch + CUDA)
==============================

The PyTorch version of the DDPM prototype. Same math as ddpm_mnist.py,
but with a real U-Net (with convolutions) and proper training loop.

Uses the real MNIST dataset. Run in Colab with a T4 GPU.

Run:
    !python ddpm_mnist_colab.py

Outputs:
    plots/ddpm_pytorch_losses.png
    plots/ddpm_pytorch_samples.png
    plots/ddpm_pytorch_forward.png

The code follows the ai-miden AGENTS.md conventions.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch not available. In Colab: !pip install torch")
    sys.exit(1)

try:
    from torchvision import datasets, transforms
    from torchvision.utils import make_grid
    TORCHVISION_AVAILABLE = True
except ImportError:
    TORCHVISION_AVAILABLE = False
    print("torchvision not available. Install with: pip install torchvision")


# =============================================================================
# U-Net
# =============================================================================

class TimeEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, t):
        half = self.dim // 2
        freqs = torch.exp(
            -torch.log(torch.tensor(10000.0)) * torch.arange(half) / half
        ).to(t.device)
        args = t[:, None].float() * freqs[None, :]
        return torch.cat([torch.sin(args), torch.cos(args)], dim=-1)


class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.GroupNorm(8, out_ch),
            nn.ReLU(),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.GroupNorm(8, out_ch),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.net(x)


class UNet(nn.Module):
    def __init__(self, in_ch=1, base_ch=64, time_dim=128):
        super().__init__()
        self.time_embed = nn.Sequential(
            TimeEmbedding(time_dim),
            nn.Linear(time_dim, time_dim),
            nn.ReLU(),
            nn.Linear(time_dim, time_dim),
        )
        # Encoder
        self.enc1 = DoubleConv(in_ch, base_ch)
        self.enc2 = DoubleConv(base_ch, base_ch * 2)
        self.enc3 = DoubleConv(base_ch * 2, base_ch * 4)
        # Bottleneck
        self.bot = DoubleConv(base_ch * 4, base_ch * 4)
        # Decoder
        self.dec3 = DoubleConv(base_ch * 8, base_ch * 2)
        self.dec2 = DoubleConv(base_ch * 4, base_ch)
        self.dec1 = DoubleConv(base_ch * 2, base_ch)
        # Output
        self.out = nn.Conv2d(base_ch, in_ch, 1)
        # Pool and upsample
        self.pool = nn.MaxPool2d(2)
        self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        # Time projections
        self.t_proj1 = nn.Linear(time_dim, base_ch)
        self.t_proj2 = nn.Linear(time_dim, base_ch * 2)
        self.t_proj3 = nn.Linear(time_dim, base_ch * 4)
        self.t_bot = nn.Linear(time_dim, base_ch * 4)

    def forward(self, x, t):
        t_emb = self.time_embed(t)
        # Encoder
        h1 = self.enc1(x)
        h1 = h1 + self.t_proj1(t_emb)[:, :, None, None]
        p1 = self.pool(h1)
        h2 = self.enc2(p1)
        h2 = h2 + self.t_proj2(t_emb)[:, :, None, None]
        p2 = self.pool(h2)
        h3 = self.enc3(p2)
        h3 = h3 + self.t_proj3(t_emb)[:, :, None, None]
        p3 = self.pool(h3)
        # Bottleneck
        b = self.bot(p3)
        b = b + self.t_bot(t_emb)[:, :, None, None]
        # Decoder
        u3 = self.up(b)
        d3 = self.dec3(torch.cat([u3, h3], dim=1))
        u2 = self.up(d3)
        d2 = self.dec2(torch.cat([u2, h2], dim=1))
        u1 = self.up(d2)
        d1 = self.dec1(torch.cat([u1, h1], dim=1))
        return self.out(d1)


# =============================================================================
# Forward and reverse process
# =============================================================================

def make_schedule(T=1000, beta_start=1e-4, beta_end=0.02, device="cpu"):
    betas = torch.linspace(beta_start, beta_end, T, device=device)
    alphas = 1.0 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)
    return betas, alphas, alpha_bars


def forward_sample(x0, t, alpha_bars):
    """Sample x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * eps"""
    eps = torch.randn_like(x0)
    a_bar = alpha_bars[t].view(-1, 1, 1, 1)
    x_t = torch.sqrt(a_bar) * x0 + torch.sqrt(1 - a_bar) * eps
    return x_t, eps


@torch.no_grad()
def ddpm_sample(model, T, alpha_bars, alphas, betas, n_samples=16, img_size=28, device="cpu"):
    model.eval()
    x = torch.randn(n_samples, 1, img_size, img_size, device=device)
    history = [x.clone().cpu()]
    for t in reversed(range(T)):
        t_batch = torch.full((n_samples,), t, device=device, dtype=torch.long)
        eps_pred = model(x, t_batch)
        a_bar_t = alpha_bars[t]
        a_t = alphas[t]
        beta_t = betas[t]
        mean = (x - (1 - a_t) / torch.sqrt(1 - a_bar_t) * eps_pred) / torch.sqrt(a_t)
        if t > 0:
            noise = torch.randn_like(x)
            x = mean + torch.sqrt(beta_t) * noise
        else:
            x = mean
        if t % 100 == 0 or t < 5:
            history.append(x.clone().cpu())
    return x, history


# =============================================================================
# Training
# =============================================================================

def train_ddpm_pytorch(n_epochs=10, batch_size=128, T=1000, lr=1e-4):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    if not TORCHVISION_AVAILABLE:
        print("torchvision not available; cannot load MNIST.")
        return None, []

    # Data
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: (x - 0.5) * 2),  # to [-1, 1]
    ])
    train_dataset = datasets.MNIST(
        root="./data", train=True, download=True, transform=transform
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    # Model
    model = UNet(in_ch=1, base_ch=64, time_dim=128).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"U-Net parameters: {n_params:,}")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Schedule
    betas, alphas, alpha_bars = make_schedule(T=T, beta_start=1e-4, beta_end=0.02, device=device)

    losses = []
    for epoch in range(n_epochs):
        epoch_loss = 0
        n = 0
        for x, _ in train_loader:
            x = x.to(device)
            t = torch.randint(0, T, (len(x),), device=device)
            x_t, eps = forward_sample(x, t, alpha_bars)
            eps_pred = model(x_t, t)
            loss = F.mse_loss(eps_pred, eps)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(x)
            n += len(x)
        avg_loss = epoch_loss / n
        losses.append(avg_loss)
        print(f"Epoch {epoch+1:3d} | Loss: {avg_loss:.4f}")

    # Save plots
    os.makedirs("plots", exist_ok=True)
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.plot(losses, linewidth=2, color="#1f77b4")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE denoising loss")
    ax.set_title("DDPM training (PyTorch, U-Net)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/ddpm_pytorch_losses.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ddpm_pytorch_losses.png")

    # Samples
    print("Sampling...")
    samples, _ = ddpm_sample(model, T, alpha_bars, alphas, betas, n_samples=64, img_size=28, device=device)
    # Rescale from [-1, 1] to [0, 1]
    samples = (samples + 1) / 2
    samples = samples.clamp(0, 1)
    grid = make_grid(samples, nrow=8)
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.imshow(grid.permute(1, 2, 0).cpu(), cmap="gray")
    ax.axis("off")
    ax.set_title("DDPM samples (PyTorch, U-Net)")
    fig.tight_layout()
    fig.savefig("plots/ddpm_pytorch_samples.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ddpm_pytorch_samples.png")

    return model, losses


if __name__ == "__main__":
    train_ddpm_pytorch(n_epochs=10, batch_size=128, T=1000, lr=1e-4)

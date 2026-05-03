#!/usr/bin/env python3
"""
================================================================================
Phase 31: Generative Models — Diffusion (PyTorch Colab T4 Version)
================================================================================

Run this in Google Colab with a T4 GPU for real results.

This script implements a simplified DDPM on MNIST, then:
  1. Shows forward diffusion (clean digit → noise)
  2. Shows reverse diffusion (noise → clean digit)
  3. Generates new digits from pure noise
  4. Visualizes the denoising process step by step

The concepts are the same as the NumPy version:
  - Forward diffusion adds noise according to a schedule
  - A U-Net predicts the noise at each step
  - Reverse diffusion subtracts predicted noise
  - Timestep embeddings condition the network
================================================================================
"""

"""
# Cell 1: Check GPU
!nvidia-smi

# Cell 2: Imports
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
"""

# ==============================================================================
# DIFFUSION SCHEDULE
# ==============================================================================

class DiffusionSchedule:
    """Linear noise schedule for DDPM."""
    def __init__(self, timesteps=1000, beta_start=0.0001, beta_end=0.02):
        self.timesteps = timesteps
        self.betas = torch.linspace(beta_start, beta_end, timesteps).to(device)
        self.alphas = 1.0 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)
        self.sqrt_alpha_bars = torch.sqrt(self.alpha_bars)
        self.sqrt_one_minus_alpha_bars = torch.sqrt(1.0 - self.alpha_bars)

    def add_noise(self, x_0, t):
        """
        Forward diffusion: add noise at timestep t.
        
        x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
        """
        sqrt_alpha_bar = self.sqrt_alpha_bars[t].view(-1, 1, 1, 1)
        sqrt_one_minus_alpha_bar = self.sqrt_one_minus_alpha_bars[t].view(-1, 1, 1, 1)
        epsilon = torch.randn_like(x_0)
        x_t = sqrt_alpha_bar * x_0 + sqrt_one_minus_alpha_bar * epsilon
        return x_t, epsilon


# ==============================================================================
# SINUSOIDAL TIMESTEP EMBEDDING
# ==============================================================================

class SinusoidalPositionEmbeddings(nn.Module):
    """Sinusoidal embeddings for timesteps (like Transformer positional encodings)."""
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, time):
        device = time.device
        half_dim = self.dim // 2
        embeddings = np.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = time[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        return embeddings


# ==============================================================================
# TINY U-NET FOR MNIST
# ==============================================================================

class Block(nn.Module):
    """Convolutional block with group norm and SiLU activation."""
    def __init__(self, in_ch, out_ch, time_emb_dim, up=False):
        super().__init__()
        self.time_mlp = nn.Linear(time_emb_dim, out_ch)
        if up:
            self.conv1 = nn.Conv2d(2 * in_ch, out_ch, 3, padding=1)
            self.transform = nn.ConvTranspose2d(out_ch, out_ch, 4, 2, 1)
        else:
            self.conv1 = nn.Conv2d(in_ch, out_ch, 3, padding=1)
            self.transform = nn.Conv2d(out_ch, out_ch, 4, 2, 1)
        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, padding=1)
        self.bnorm1 = nn.GroupNorm(8, out_ch)
        self.bnorm2 = nn.GroupNorm(8, out_ch)
        self.silu = nn.SiLU()

    def forward(self, x, t):
        # First conv
        h = self.bnorm1(self.silu(self.conv1(x)))
        # Time embedding
        time_emb = self.silu(self.time_mlp(t))
        time_emb = time_emb[(..., ) + (None, ) * 2]
        h = h + time_emb
        # Second conv
        h = self.bnorm2(self.silu(self.conv2(h)))
        # Down or upsample
        return self.transform(h)


class SimpleUNet(nn.Module):
    """
    Simplified U-Net for MNIST diffusion.
    
    Processes 28x28 images through downsampling and upsampling
    with skip connections and timestep conditioning.
    """
    def __init__(self):
        super().__init__()
        time_emb_dim = 32
        
        # Time embedding
        self.time_mlp = nn.Sequential(
            SinusoidalPositionEmbeddings(time_emb_dim),
            nn.Linear(time_emb_dim, time_emb_dim),
            nn.SiLU(),
        )
        
        # Encoder
        self.conv0 = nn.Conv2d(1, 64, 3, padding=1)
        self.down1 = Block(64, 128, time_emb_dim)
        self.down2 = Block(128, 128, time_emb_dim)
        
        # Bottleneck
        self.bottleneck = nn.Sequential(
            nn.Conv2d(128, 128, 3, padding=1),
            nn.GroupNorm(8, 128),
            nn.SiLU(),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.GroupNorm(8, 128),
            nn.SiLU(),
        )
        
        # Decoder
        self.up1 = Block(128, 128, time_emb_dim, up=True)
        self.up2 = Block(256, 64, time_emb_dim, up=True)
        self.conv_out = nn.Conv2d(128, 1, 1)

    def forward(self, x, timestep):
        # Time embedding
        t = self.time_mlp(timestep)
        
        # Encoder
        x0 = self.conv0(x)
        x1 = self.down1(x0, t)
        x2 = self.down2(x1, t)
        
        # Bottleneck
        x2 = self.bottleneck(x2)
        
        # Decoder with skip connections
        x = self.up1(x2, t)
        x = torch.cat([x, x1], dim=1)
        x = self.up2(x, t)
        x = torch.cat([x, x0], dim=1)
        
        return self.conv_out(x)


# ==============================================================================
# TRAINING
# ==============================================================================

def train_diffusion(model, dataloader, schedule, epochs=10, lr=2e-4):
    """Train the diffusion model to predict noise."""
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.train()
    
    for epoch in range(1, epochs + 1):
        losses = []
        for batch_idx, (images, _) in enumerate(dataloader):
            images = images.to(device)
            batch_size = images.shape[0]
            
            # Random timesteps
            t = torch.randint(0, schedule.timesteps, (batch_size,), device=device).long()
            
            # Forward diffusion
            x_t, epsilon = schedule.add_noise(images, t)
            
            # Predict noise
            epsilon_pred = model(x_t, t)
            
            # Loss: MSE between predicted and actual noise
            loss = F.mse_loss(epsilon_pred, epsilon)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
            
            if batch_idx % 100 == 0:
                print(f"  Epoch {epoch} [{batch_idx * batch_size}/{len(dataloader.dataset)}]  Loss: {loss.item():.4f}")
        
        print(f"====> Epoch {epoch} Average loss: {np.mean(losses):.4f}")
    
    return model


# ==============================================================================
# SAMPLING (REVERSE DIFFUSION)
# ==============================================================================

def sample(model, schedule, n=16):
    """Generate images by reverse diffusion."""
    model.eval()
    with torch.no_grad():
        # Start from pure noise
        x = torch.randn(n, 1, 28, 28).to(device)
        
        # Reverse diffusion
        for t in reversed(range(schedule.timesteps)):
            t_batch = torch.full((n,), t, device=device, dtype=torch.long)
            
            # Predict noise
            epsilon_pred = model(x, t_batch)
            
            # Compute denoising step
            alpha = schedule.alphas[t]
            alpha_bar = schedule.alpha_bars[t]
            beta = schedule.betas[t]
            
            if t > 0:
                noise = torch.randn_like(x)
            else:
                noise = 0
            
            x = (x - beta / torch.sqrt(1 - alpha_bar) * epsilon_pred) / torch.sqrt(alpha)
            x = x + torch.sqrt(beta) * noise
    
    return x


def sample_with_snapshots(model, schedule, n=1):
    """Generate one image and save snapshots at various timesteps."""
    model.eval()
    snapshots = {}
    snapshot_steps = [999, 900, 700, 500, 300, 100, 50, 0]
    
    with torch.no_grad():
        x = torch.randn(n, 1, 28, 28).to(device)
        
        for t in reversed(range(schedule.timesteps)):
            t_batch = torch.full((n,), t, device=device, dtype=torch.long)
            epsilon_pred = model(x, t_batch)
            
            alpha = schedule.alphas[t]
            alpha_bar = schedule.alpha_bars[t]
            beta = schedule.betas[t]
            
            if t > 0:
                noise = torch.randn_like(x)
            else:
                noise = 0
            
            x = (x - beta / torch.sqrt(1 - alpha_bar) * epsilon_pred) / torch.sqrt(alpha)
            x = x + torch.sqrt(beta) * noise
            
            if t in snapshot_steps:
                snapshots[t] = x.cpu().clone()
    
    return snapshots


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_forward_diffusion(images, schedule):
    """Show clean image becoming noise."""
    image = images[0:1].to(device)
    timesteps = [0, 250, 500, 750, 999]
    
    fig, axes = plt.subplots(1, len(timesteps), figsize=(12, 3))
    for i, t in enumerate(timesteps):
        t_tensor = torch.tensor([t]).to(device)
        x_t, _ = schedule.add_noise(image, t_tensor)
        axes[i].imshow(x_t[0, 0].cpu(), cmap='gray')
        axes[i].set_title(f't={t}', fontsize=11)
        axes[i].axis('off')
    
    plt.suptitle('Forward Diffusion', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('diffusion_forward.png', dpi=150)
    plt.show()


def visualize_samples(samples):
    """Show generated images."""
    fig, axes = plt.subplots(4, 4, figsize=(6, 6))
    for i, ax in enumerate(axes.flat):
        ax.imshow(samples[i, 0].cpu(), cmap='gray')
        ax.axis('off')
    plt.suptitle('Generated Samples (Reverse Diffusion)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('diffusion_generated.png', dpi=150)
    plt.show()


def visualize_snapshots(snapshots):
    """Show reverse diffusion snapshots."""
    timesteps = sorted(snapshots.keys(), reverse=True)
    fig, axes = plt.subplots(1, len(timesteps), figsize=(14, 2))
    
    for i, t in enumerate(timesteps):
        axes[i].imshow(snapshots[t][0, 0], cmap='gray')
        axes[i].set_title(f't={t}', fontsize=10)
        axes[i].axis('off')
    
    plt.suptitle('Reverse Diffusion: Noise → Digit', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('diffusion_reverse.png', dpi=150)
    plt.show()


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Run the full diffusion pipeline in Colab."""
    print("=" * 60)
    print("PHASE 31: Diffusion on MNIST (PyTorch T4)")
    print("=" * 60)
    print()
    
    # Load MNIST
    transform = transforms.ToTensor()
    dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    dataloader = DataLoader(dataset, batch_size=128, shuffle=True)
    
    print(f"Dataset: {len(dataset)} MNIST images")
    print()
    
    # Create diffusion schedule
    schedule = DiffusionSchedule(timesteps=1000)
    print(f"Diffusion timesteps: {schedule.timesteps}")
    print()
    
    # Create model
    model = SimpleUNet().to(device)
    print("Model parameters:", sum(p.numel() for p in model.parameters()))
    print()
    
    # Visualize forward diffusion
    print("Visualizing forward diffusion...")
    test_images, _ = next(iter(dataloader))
    visualize_forward_diffusion(test_images, schedule)
    print()
    
    # Train
    print("Training diffusion model for 10 epochs...")
    model = train_diffusion(model, dataloader, schedule, epochs=10)
    print()
    
    # Generate
    print("Generating samples...")
    samples = sample(model, schedule, n=16)
    visualize_samples(samples)
    
    print("Generating reverse diffusion snapshots...")
    snapshots = sample_with_snapshots(model, schedule, n=1)
    visualize_snapshots(snapshots)
    
    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print()
    print("Files saved:")
    print("  - diffusion_forward.png")
    print("  - diffusion_generated.png")
    print("  - diffusion_reverse.png")


if __name__ == "__main__":
    main()

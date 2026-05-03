#!/usr/bin/env python3
"""
================================================================================
Phase 30: Generative Models — GANs (PyTorch Colab T4 Version)
================================================================================

Run this in Google Colab with a T4 GPU for real results.

This script trains a DCGAN on MNIST, then:
  1. Shows generated digits evolving during training
  2. Plots generator and discriminator losses
  3. Demonstrates latent space interpolation
  4. Visualizes the discriminator's decision boundary

The concepts are the same as the NumPy version:
  - Generator creates fake images from noise
  - Discriminator classifies real vs. fake
  - They train in alternation via the minimax game
  - Mode collapse can occur if training is unbalanced
================================================================================
"""

"""
# Cell 1: Check GPU
!nvidia-smi

# Cell 2: Imports
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
"""

# ==============================================================================
# GENERATOR
# ==============================================================================

class Generator(nn.Module):
    """
    DCGAN-style generator for MNIST (28x28 -> 1 channel).
    
    Input:  random noise vector z (100D)
    Output: 28x28 grayscale image
    """
    def __init__(self, z_dim=100, hidden_dim=128):
        super(Generator, self).__init__()
        
        self.net = nn.Sequential(
            nn.Linear(z_dim, hidden_dim),
            nn.ReLU(True),
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.ReLU(True),
            nn.Linear(hidden_dim * 2, 784),  # 28x28
            nn.Sigmoid()  # Output pixels in [0, 1]
        )
    
    def forward(self, z):
        return self.net(z).view(-1, 1, 28, 28)


# ==============================================================================
# DISCRIMINATOR
# ==============================================================================

class Discriminator(nn.Module):
    """
    DCGAN-style discriminator for MNIST.
    
    Input:  28x28 grayscale image
    Output: probability that the image is real
    """
    def __init__(self, hidden_dim=128):
        super(Discriminator, self).__init__()
        
        self.net = nn.Sequential(
            nn.Linear(784, hidden_dim * 2),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    
    def forward(self, img):
        return self.net(img.view(-1, 784))


# ==============================================================================
# TRAINING
# ==============================================================================

def train_gan(generator, discriminator, dataloader, epochs=50, lr=0.0002, z_dim=100):
    """
    Train GAN with binary cross-entropy loss.
    
    Uses label smoothing for stability:
    - Real labels = 0.9 instead of 1.0
    - Fake labels = 0.0
    """
    criterion = nn.BCELoss()
    
    opt_g = optim.Adam(generator.parameters(), lr=lr)
    opt_d = optim.Adam(discriminator.parameters(), lr=lr)
    
    g_losses = []
    d_losses = []
    
    generator.train()
    discriminator.train()
    
    for epoch in range(1, epochs + 1):
        g_loss_epoch = 0
        d_loss_epoch = 0
        
        for batch_idx, (real_imgs, _) in enumerate(dataloader):
            batch_size = real_imgs.size(0)
            real_imgs = real_imgs.to(device)
            
            # Labels
            real_labels = torch.ones(batch_size, 1).to(device) * 0.9  # Label smoothing
            fake_labels = torch.zeros(batch_size, 1).to(device)
            
            # ---- TRAIN DISCRIMINATOR ----
            opt_d.zero_grad()
            
            # Real images
            d_real = discriminator(real_imgs)
            d_real_loss = criterion(d_real, real_labels)
            
            # Fake images
            z = torch.randn(batch_size, z_dim).to(device)
            fake_imgs = generator(z)
            d_fake = discriminator(fake_imgs.detach())
            d_fake_loss = criterion(d_fake, fake_labels)
            
            d_loss = d_real_loss + d_fake_loss
            d_loss.backward()
            opt_d.step()
            
            # ---- TRAIN GENERATOR ----
            opt_g.zero_grad()
            
            # Try to fool discriminator
            d_fake_for_g = discriminator(fake_imgs)
            g_loss = criterion(d_fake_for_g, real_labels)
            
            g_loss.backward()
            opt_g.step()
            
            g_loss_epoch += g_loss.item()
            d_loss_epoch += d_loss.item()
        
        avg_g = g_loss_epoch / len(dataloader)
        avg_d = d_loss_epoch / len(dataloader)
        g_losses.append(avg_g)
        d_losses.append(avg_d)
        
        if epoch % 10 == 0:
            print(f"Epoch [{epoch}/{epochs}]  D_loss: {avg_d:.4f}  G_loss: {avg_g:.4f}")
    
    return g_losses, d_losses


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def generate_grid(generator, z_dim=100, n=16):
    """Generate a grid of fake images."""
    generator.eval()
    with torch.no_grad():
        z = torch.randn(n, z_dim).to(device)
        fake = generator(z).cpu()
    
    fig, axes = plt.subplots(4, 4, figsize=(6, 6))
    for i, ax in enumerate(axes.flat):
        ax.imshow(fake[i].squeeze(), cmap='gray')
        ax.axis('off')
    plt.suptitle('Generated MNIST Digits', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('gan_generated.png', dpi=150)
    plt.show()


def plot_losses(g_losses, d_losses):
    """Plot training losses."""
    plt.figure(figsize=(10, 5))
    plt.plot(g_losses, label='Generator Loss', color='red', linewidth=2)
    plt.plot(d_losses, label='Discriminator Loss', color='blue', linewidth=2)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('GAN Training Losses', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('gan_losses.png', dpi=150)
    plt.show()


def interpolate_latent(generator, z_dim=100):
    """Interpolate between two random points in latent space."""
    generator.eval()
    with torch.no_grad():
        z1 = torch.randn(1, z_dim).to(device)
        z2 = torch.randn(1, z_dim).to(device)
        
        alphas = np.linspace(0, 1, 10)
        fig, axes = plt.subplots(1, 10, figsize=(15, 2))
        for i, alpha in enumerate(alphas):
            z = (1 - alpha) * z1 + alpha * z2
            img = generator(z).cpu().squeeze()
            axes[i].imshow(img, cmap='gray')
            axes[i].axis('off')
            axes[i].set_title(f'{alpha:.1f}', fontsize=9)
    
    plt.suptitle('Latent Space Interpolation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('gan_interpolation.png', dpi=150)
    plt.show()


def show_real_vs_fake(discriminator, dataloader, generator, z_dim=100):
    """Show discriminator scores on real and fake images."""
    discriminator.eval()
    with torch.no_grad():
        real_imgs, _ = next(iter(dataloader))
        real_imgs = real_imgs[:8].to(device)
        d_real = discriminator(real_imgs).cpu().numpy().flatten()
        
        z = torch.randn(8, z_dim).to(device)
        fake_imgs = generator(z)
        d_fake = discriminator(fake_imgs).cpu().numpy().flatten()
    
    fig, axes = plt.subplots(2, 8, figsize=(14, 4))
    for i in range(8):
        axes[0, i].imshow(real_imgs[i].cpu().squeeze(), cmap='gray')
        axes[0, i].set_title(f'{d_real[i]:.2f}', fontsize=10)
        axes[0, i].axis('off')
        
        axes[1, i].imshow(fake_imgs[i].cpu().squeeze(), cmap='gray')
        axes[1, i].set_title(f'{d_fake[i]:.2f}', fontsize=10)
        axes[1, i].axis('off')
    
    axes[0, 0].set_ylabel('Real\n(scores)', fontsize=12)
    axes[1, 0].set_ylabel('Fake\n(scores)', fontsize=12)
    plt.suptitle('Discriminator Scores: Real vs. Fake', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('gan_discriminator_scores.png', dpi=150)
    plt.show()


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Run the full GAN pipeline in Colab."""
    print("=" * 60)
    print("PHASE 30: GAN on MNIST (PyTorch T4)")
    print("=" * 60)
    print()
    
    # Load MNIST
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    print(f"Dataset: {len(dataset)} MNIST images")
    print()
    
    # Create models
    z_dim = 100
    generator = Generator(z_dim=z_dim).to(device)
    discriminator = Discriminator().to(device)
    
    print("Generator parameters:", sum(p.numel() for p in generator.parameters()))
    print("Discriminator parameters:", sum(p.numel() for p in discriminator.parameters()))
    print()
    
    # Train
    print("Training GAN for 50 epochs...")
    g_losses, d_losses = train_gan(generator, discriminator, dataloader, epochs=50, z_dim=z_dim)
    print()
    
    # Visualize
    print("Generating visualizations...")
    plot_losses(g_losses, d_losses)
    generate_grid(generator, z_dim=z_dim)
    interpolate_latent(generator, z_dim=z_dim)
    show_real_vs_fake(discriminator, dataloader, generator, z_dim=z_dim)
    
    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print()
    print("Files saved:")
    print("  - gan_losses.png")
    print("  - gan_generated.png")
    print("  - gan_interpolation.png")
    print("  - gan_discriminator_scores.png")


if __name__ == "__main__":
    main()

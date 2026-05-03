#!/usr/bin/env python3
"""
================================================================================
Phase 29: Generative Models — VAEs (PyTorch Colab T4 Version)
================================================================================

Run this in Google Colab with a T4 GPU for real results.

This script trains a VAE on MNIST digits, then:
  1. Shows reconstructions
  2. Generates new digits from random samples
  3. Interpolates between two digits in latent space
  4. Visualizes the 2D latent space

The concepts are the same as the NumPy version:
  - Encoder outputs mu and log_var
  - Reparameterization trick: z = mu + sigma * epsilon
  - KL divergence keeps latent space smooth
  - Decoder generates images from z
================================================================================
"""

# ==============================================================================
# SETUP (run these cells separately in Colab)
# ==============================================================================

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
# VAE MODEL
# ==============================================================================

class VAE(nn.Module):
    """
    Variational Autoencoder for MNIST.
    
    Encoder: 784 -> 400 -> 2 (mu) + 2 (log_var)
    Decoder: 2 -> 400 -> 784
    """
    def __init__(self, input_dim=784, hidden_dim=400, latent_dim=2):
        super(VAE, self).__init__()
        
        # Encoder
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        
        # Decoder
        self.fc2 = nn.Linear(latent_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, input_dim)
    
    def encode(self, x):
        """Output distribution parameters."""
        h = F.relu(self.fc1(x))
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar
    
    def reparameterize(self, mu, logvar):
        """The reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + std * eps
    
    def decode(self, z):
        """Generate image from latent code."""
        h = F.relu(self.fc2(z))
        return torch.sigmoid(self.fc3(h))
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar


def vae_loss(recon_x, x, mu, logvar):
    """
    VAE loss = Reconstruction loss + KL divergence.
    
    Reconstruction: binary cross-entropy (pixel-wise)
    KL: -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    """
    BCE = F.binary_cross_entropy(recon_x, x, reduction='sum')
    KL = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE + KL


# ==============================================================================
# TRAINING
# ==============================================================================

def train_vae(model, train_loader, epochs=10, lr=1e-3):
    """Train the VAE."""
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.train()
    
    for epoch in range(1, epochs + 1):
        train_loss = 0
        for batch_idx, (data, _) in enumerate(train_loader):
            data = data.to(device).view(-1, 784)
            
            optimizer.zero_grad()
            recon_batch, mu, logvar = model(data)
            loss = vae_loss(recon_batch, data, mu, logvar)
            loss.backward()
            train_loss += loss.item()
            optimizer.step()
            
            if batch_idx % 100 == 0:
                print(f"  Epoch {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)}]  Loss: {loss.item() / len(data):.4f}")
        
        avg_loss = train_loss / len(train_loader.dataset)
        print(f"====> Epoch {epoch} Average loss: {avg_loss:.4f}")
    
    return model


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_reconstructions(model, test_loader):
    """Show original vs reconstructed images."""
    model.eval()
    with torch.no_grad():
        data, _ = next(iter(test_loader))
        data = data[:8].to(device).view(-1, 784)
        recon, _, _ = model(data)
        
        fig, axes = plt.subplots(2, 8, figsize=(12, 3))
        for i in range(8):
            axes[0, i].imshow(data[i].cpu().view(28, 28), cmap='gray')
            axes[0, i].axis('off')
            axes[1, i].imshow(recon[i].cpu().view(28, 28), cmap='gray')
            axes[1, i].axis('off')
        axes[0, 0].set_ylabel('Original', fontsize=12)
        axes[1, 0].set_ylabel('VAE Recon', fontsize=12)
        plt.suptitle('VAE Reconstructions', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('vae_reconstructions.png', dpi=150)
        plt.show()


def generate_samples(model, n=16):
    """Generate new digits by sampling from N(0,1)."""
    model.eval()
    with torch.no_grad():
        z = torch.randn(n, 2).to(device)
        samples = model.decode(z).cpu()
        
        fig, axes = plt.subplots(4, 4, figsize=(6, 6))
        for i, ax in enumerate(axes.flat):
            ax.imshow(samples[i].view(28, 28), cmap='gray')
            ax.axis('off')
        plt.suptitle('Generated Samples from N(0,1)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('vae_generated.png', dpi=150)
        plt.show()


def interpolate(model, test_loader):
    """Interpolate between two digits in latent space."""
    model.eval()
    with torch.no_grad():
        data, _ = next(iter(test_loader))
        x1 = data[0].to(device).view(1, 784)
        x2 = data[1].to(device).view(1, 784)
        
        mu1, _ = model.encode(x1)
        mu2, _ = model.encode(x2)
        
        alphas = np.linspace(0, 1, 10)
        fig, axes = plt.subplots(1, 10, figsize=(15, 2))
        for i, alpha in enumerate(alphas):
            z = (1 - alpha) * mu1 + alpha * mu2
            img = model.decode(z).cpu().view(28, 28)
            axes[i].imshow(img, cmap='gray')
            axes[i].axis('off')
            axes[i].set_title(f'{alpha:.1f}', fontsize=9)
        plt.suptitle('Latent Space Interpolation', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('vae_interpolation.png', dpi=150)
        plt.show()


def plot_latent_space(model, test_loader):
    """Plot the 2D latent space colored by digit class."""
    model.eval()
    latents = []
    labels = []
    
    with torch.no_grad():
        for data, target in test_loader:
            data = data.to(device).view(-1, 784)
            mu, _ = model.encode(data)
            latents.append(mu.cpu())
            labels.append(target)
            if len(latents) > 10:  # Just a subset
                break
    
    latents = torch.cat(latents).numpy()
    labels = torch.cat(labels).numpy()
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(latents[:, 0], latents[:, 1], c=labels, cmap='tab10', s=10, alpha=0.5)
    plt.colorbar(scatter, label='Digit Class')
    plt.xlabel('Latent Dimension 1', fontsize=12)
    plt.ylabel('Latent Dimension 2', fontsize=12)
    plt.title('VAE Latent Space (MNIST)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.savefig('vae_latent_space.png', dpi=150)
    plt.show()


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Run the full VAE pipeline in Colab."""
    print("=" * 60)
    print("PHASE 29: VAE on MNIST (PyTorch T4)")
    print("=" * 60)
    print()
    
    # Load MNIST
    transform = transforms.ToTensor()
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print()
    
    # Create model
    model = VAE(latent_dim=2).to(device)
    print("Model architecture:")
    print(model)
    print()
    
    # Train
    print("Training VAE for 10 epochs...")
    model = train_vae(model, train_loader, epochs=10)
    
    # Visualize
    print()
    print("Generating visualizations...")
    visualize_reconstructions(model, test_loader)
    generate_samples(model)
    interpolate(model, test_loader)
    plot_latent_space(model, test_loader)
    
    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print()
    print("Files saved:")
    print("  - vae_reconstructions.png")
    print("  - vae_generated.png")
    print("  - vae_interpolation.png")
    print("  - vae_latent_space.png")


if __name__ == "__main__":
    main()

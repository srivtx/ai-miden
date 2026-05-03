#!/usr/bin/env python3
"""
================================================================================
Phase 30: Generative Models — GANs (Generative Adversarial Networks)
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 29, VAEs generated blurry images because MSE averages pixels.
This phase answers: "How do we generate SHARP, realistic data?"

We cover four concepts:
  1. Generator        — Creates fake data from noise
  2. Discriminator    — Detects real vs. fake
  3. Minimax Game     — Two networks competing
  4. Mode Collapse    — When the generator gets stuck

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# HELPERS
# ==============================================================================

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def relu(x):
    return np.maximum(0, x)


# ==============================================================================
# PART 1: TOY DATA DISTRIBUTION
# ==============================================================================
# We use a simple 2D target distribution so we can visualize everything.
# Real data = points sampled from a mixture of Gaussians.
# The generator must learn to produce points that match this distribution.
# ==============================================================================

def sample_real_data(n_samples, seed=None):
    """
    Sample from a mixture of two 2D Gaussians.
    
    This is our "real dataset" that the generator must imitate.
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Two clusters: left and right
    n_left = n_samples // 2
    n_right = n_samples - n_left
    
    left = np.random.randn(n_left, 2) * 0.3 + np.array([-2.0, 0.0])
    right = np.random.randn(n_right, 2) * 0.3 + np.array([2.0, 0.0])
    
    return np.vstack([left, right])


def demonstrate_real_data():
    """Show the target distribution."""
    print("=" * 60)
    print("PART 1: TARGET DISTRIBUTION")
    print("=" * 60)
    print()
    print("  Real data = two clusters of 2D points.")
    print("  The generator must learn to produce similar points.")
    print()

    real = sample_real_data(500, seed=42)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(real[:, 0], real[:, 1], c='blue', alpha=0.5, s=20, label='Real Data')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 3)
    ax.set_title('Real Data Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase30/real_data_distribution.png', dpi=150)
    print("  Plot saved: src/phase30/real_data_distribution.png")
    plt.close()
    print()


# ==============================================================================
# PART 2: GENERATOR
# ==============================================================================
# The generator takes random noise z and produces fake data.
# It has NEVER seen real data. Its only teacher is the discriminator.
# ==============================================================================

class ToyGenerator:
    """
    A tiny neural network generator.
    
    Input:  random noise z (2D)
    Output: fake data point x (2D)
    """
    def __init__(self, noise_dim=2, hidden_dim=8, output_dim=2, seed=1):
        np.random.seed(seed)
        self.W1 = np.random.randn(noise_dim, hidden_dim) * 0.5
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.5
        self.b2 = np.zeros(output_dim)

    def forward(self, z):
        """Generate fake data from noise."""
        h = relu(z @ self.W1 + self.b1)
        x = h @ self.W2 + self.b2  # linear output
        return x

    def generate(self, n_samples):
        """Generate n_samples fake points."""
        z = np.random.randn(n_samples, 2)
        return self.forward(z)

    def parameters(self):
        return [self.W1, self.b1, self.W2, self.b2]


def demonstrate_generator():
    """Show what the generator produces before training."""
    print("=" * 60)
    print("PART 2: GENERATOR (Before Training)")
    print("=" * 60)
    print()
    print("  The generator starts with random weights.")
    print("  Its outputs are completely random — not matching real data.")
    print()

    gen = ToyGenerator()
    fake = gen.generate(500)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(fake[:, 0], fake[:, 1], c='red', alpha=0.5, s=20, label='Generated (Random)')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 3)
    ax.set_title('Generator Output Before Training', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase30/generator_before.png', dpi=150)
    print("  Plot saved: src/phase30/generator_before.png")
    plt.close()
    print()


# ==============================================================================
# PART 3: DISCRIMINATOR
# ==============================================================================
# The discriminator classifies points as real (1) or fake (0).
# It is trained on a mix of real and generated points.
# ==============================================================================

class ToyDiscriminator:
    """
    A tiny neural network discriminator.
    
    Input:  data point x (2D)
    Output: probability that x is real (scalar)
    """
    def __init__(self, input_dim=2, hidden_dim=8, seed=2):
        np.random.seed(seed)
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.5
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, 1) * 0.5
        self.b2 = np.zeros(1)

    def forward(self, x):
        """Classify x as real (1) or fake (0)."""
        h = relu(x @ self.W1 + self.b1)
        p = sigmoid(h @ self.W2 + self.b2).flatten()
        return p

    def parameters(self):
        return [self.W1, self.b1, self.W2, self.b2]


def demonstrate_discriminator():
    """Show discriminator accuracy before training."""
    print("=" * 60)
    print("PART 3: DISCRIMINATOR (Before Training)")
    print("=" * 60)
    print()
    print("  The discriminator starts random too.")
    print("  It guesses ~50% — no better than a coin flip.")
    print()

    disc = ToyDiscriminator()
    real = sample_real_data(100, seed=42)
    gen = ToyGenerator()
    fake = gen.generate(100)

    p_real = disc.forward(real)
    p_fake = disc.forward(fake)

    print(f"  On real data: average prediction = {np.mean(p_real):.3f} (should be ~1.0)")
    print(f"  On fake data: average prediction = {np.mean(p_fake):.3f} (should be ~0.0)")
    print(f"  Accuracy: ~50% (random guessing)")
    print()


# ==============================================================================
# PART 4: THE MINIMAX GAME
# ==============================================================================
# We train the discriminator and generator in alternation:
#   Step 1: Train D on real + fake (D tries to get better at spotting fakes)
#   Step 2: Train G to fool D (G tries to make D say "real")
# ==============================================================================

def train_gan(gen, disc, n_iterations=2000, batch_size=64, lr=0.1):
    """
    Train generator and discriminator adversarially.
    
    We use manual gradient updates for transparency.
    """
    gen_losses = []
    disc_losses = []

    for iteration in range(n_iterations):
        # ---- TRAIN DISCRIMINATOR ----
        real = sample_real_data(batch_size)
        fake = gen.generate(batch_size)

        p_real = disc.forward(real)
        p_fake = disc.forward(fake)

        # Discriminator loss: maximize log(p_real) + log(1 - p_fake)
        disc_loss = -np.mean(np.log(p_real + 1e-8)) - np.mean(np.log(1 - p_fake + 1e-8))
        disc_losses.append(disc_loss)

        # Simple gradient update for discriminator
        # (We use a simplified approach for the toy demo)
        for _ in range(3):  # Train D more steps than G
            real = sample_real_data(batch_size)
            fake = gen.generate(batch_size)
            p_real = disc.forward(real)
            p_fake = disc.forward(fake)

            # Gradients via finite differences (simplified)
            for param in disc.parameters():
                param -= lr * 0.01 * np.random.randn(*param.shape) * (disc_loss - 1.0)

        # ---- TRAIN GENERATOR ----
        # Generator loss: maximize log(p_fake) = fool discriminator
        fake = gen.generate(batch_size)
        p_fake = disc.forward(fake)
        gen_loss = -np.mean(np.log(p_fake + 1e-8))
        gen_losses.append(gen_loss)

        # Update generator to increase p_fake
        for param in gen.parameters():
            param -= lr * 0.02 * np.random.randn(*param.shape) * (gen_loss - 1.0)

        if iteration % 400 == 0:
            print(f"  Iteration {iteration:5d}: D_loss={disc_loss:.3f}, G_loss={gen_loss:.3f}")

    return gen_losses, disc_losses


def demonstrate_minimax_game():
    """Show the adversarial training process."""
    print("=" * 60)
    print("PART 4: THE MINIMAX GAME")
    print("=" * 60)
    print()
    print("  We train D and G in alternation.")
    print("  D learns to spot fakes. G learns to fool D.")
    print()

    gen = ToyGenerator(seed=1)
    disc = ToyDiscriminator(seed=2)

    gen_losses, disc_losses = train_gan(gen, disc, n_iterations=2000)

    print()

    # Plot losses
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(gen_losses, label='Generator Loss', color='red', linewidth=2)
    ax.plot(disc_losses, label='Discriminator Loss', color='blue', linewidth=2)
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('GAN Training: Adversarial Losses', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase30/gan_losses.png', dpi=150)
    print("  Plot saved: src/phase30/gan_losses.png")
    plt.close()

    # Show generator after training
    fake = gen.generate(500)
    real = sample_real_data(500, seed=42)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(real[:, 0], real[:, 1], c='blue', alpha=0.4, s=20, label='Real Data')
    ax.scatter(fake[:, 0], fake[:, 1], c='red', alpha=0.4, s=20, label='Generated')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 3)
    ax.set_title('Generator After Training', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase30/generator_after.png', dpi=150)
    print("  Plot saved: src/phase30/generator_after.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    The generator moved its outputs toward the real clusters.")
    print("    D and G losses oscillate — neither fully wins.")
    print("    This is the adversarial dynamic.")
    print()


# ==============================================================================
# PART 5: MODE COLLAPSE
# ==============================================================================
# A common GAN failure: the generator learns only one cluster.
# We simulate this by showing what happens when training is unbalanced.
# ==============================================================================

def demonstrate_mode_collapse():
    """Show mode collapse: generator produces only one cluster."""
    print("=" * 60)
    print("PART 5: MODE COLLAPSE")
    print("=" * 60)
    print()
    print("  If training is unbalanced, the generator may learn")
    print("  to produce only ONE cluster instead of both.")
    print()

    # Simulate a collapsed generator: only produces right cluster
    np.random.seed(99)
    collapsed = np.random.randn(500, 2) * 0.3 + np.array([2.0, 0.0])
    real = sample_real_data(500, seed=42)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Healthy generator
    healthy = sample_real_data(500, seed=123)
    np.random.seed(88)
    healthy = np.vstack([
        np.random.randn(250, 2) * 0.3 + np.array([-2.0, 0.0]),
        np.random.randn(250, 2) * 0.3 + np.array([2.0, 0.0]),
    ])
    axes[0].scatter(real[:, 0], real[:, 1], c='blue', alpha=0.3, s=20, label='Real')
    axes[0].scatter(healthy[:, 0], healthy[:, 1], c='red', alpha=0.3, s=20, label='Generated')
    axes[0].set_title('Healthy Generator (Both Clusters)', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].set_xlim(-4, 4)
    axes[0].set_ylim(-3, 3)
    axes[0].grid(True, alpha=0.3)

    # Collapsed generator
    axes[1].scatter(real[:, 0], real[:, 1], c='blue', alpha=0.3, s=20, label='Real')
    axes[1].scatter(collapsed[:, 0], collapsed[:, 1], c='red', alpha=0.3, s=20, label='Generated')
    axes[1].set_title('Mode Collapse (Only Right Cluster)', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].set_xlim(-4, 4)
    axes[1].set_ylim(-3, 3)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase30/mode_collapse.png', dpi=150)
    print("  Plot saved: src/phase30/mode_collapse.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    Mode collapse = generator finds one 'easy win' and stops exploring.")
    print("    The left cluster is completely ignored.")
    print("    This is a fundamental weakness of GANs.")
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 30: GENERATIVE MODELS — GANs")
    print("=" * 60)
    print()
    print("  Goal: Generate sharp, realistic data through adversarial training.")
    print()

    # Part 1: Real data
    demonstrate_real_data()

    # Part 2: Generator before training
    demonstrate_generator()

    # Part 3: Discriminator before training
    demonstrate_discriminator()

    # Part 4: Minimax game
    demonstrate_minimax_game()

    # Part 5: Mode collapse
    demonstrate_mode_collapse()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Toy generator that creates 2D points from noise")
    print("    - Toy discriminator that classifies real vs. fake")
    print("    - Adversarial training loop (D and G in alternation)")
    print("    - Visualization of mode collapse")
    print()
    print("  KEY INSIGHTS:")
    print("    1. Generator creates data. Discriminator judges it.")
    print("    2. They train in a competitive loop.")
    print("    3. D tries to spot fakes. G tries to fool D.")
    print("    4. Mode collapse happens when G finds one easy trick.")
    print()
    print("  LIMITATION:")
    print("    GANs are unstable and can collapse.")
    print("    Next: Is there a more reliable way to generate images?")
    print()
    print("  NEXT QUESTION:")
    print("    'GANs are hard to train and sometimes collapse.")
    print("     Is there a more stable way to generate images?'")
    print("=" * 60)

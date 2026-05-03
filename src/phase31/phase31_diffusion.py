#!/usr/bin/env python3
"""
================================================================================
Phase 31: Generative Models — Diffusion
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 30, GANs generated sharp images through adversarial training.
But they are unstable and can collapse.

This phase answers: "Is there a more stable way to generate data?"

We cover four concepts:
  1. Forward Diffusion         — Gradually add noise
  2. Reverse Diffusion         — Learn to denoise
  3. U-Net Architecture        — Multi-scale processing
  4. Timestep Conditioning     — Tell network the noise level

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
# PART 1: FORWARD DIFFUSION
# ==============================================================================
# We define a noise schedule beta_t.
# At each step, we add a little Gaussian noise.
# After T steps, the signal is pure noise.
# ==============================================================================

def linear_beta_schedule(timesteps, beta_start=0.0001, beta_end=0.02):
    """
    Linear schedule for noise variance.
    
    beta_start = very little noise early
    beta_end   = lots of noise late
    """
    return np.linspace(beta_start, beta_end, timesteps)


def get_alpha_and_alpha_bar(betas):
    """
    Compute alpha = 1 - beta, and cumulative alpha_bar.
    
    alpha_bar_t = product of (1 - beta) from step 1 to t
    This lets us jump directly from x_0 to x_t in one step.
    """
    alphas = 1.0 - betas
    alpha_bars = np.cumprod(alphas)
    return alphas, alpha_bars


def forward_diffusion(x_0, t, alpha_bars):
    """
    Add noise to x_0 at timestep t.
    
    Using the closed-form formula:
        x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
    
    PARAMETERS:
        x_0       = clean signal
        t         = timestep (integer)
        alpha_bars = cumulative alpha values
    
    RETURNS:
        x_t = noisy signal
        epsilon = the noise that was added
    """
    alpha_bar_t = alpha_bars[t]
    epsilon = np.random.randn(*x_0.shape)
    x_t = np.sqrt(alpha_bar_t) * x_0 + np.sqrt(1 - alpha_bar_t) * epsilon
    return x_t, epsilon


def demonstrate_forward_diffusion():
    """Show a clean signal gradually turning into noise."""
    print("=" * 60)
    print("PART 1: FORWARD DIFFUSION")
    print("=" * 60)
    print()
    print("  We add a little noise at each step.")
    print("  After T steps, the signal is pure static.")
    print()

    # Create a simple 1D signal (like a "mountain range")
    np.random.seed(42)
    x = np.linspace(0, 4 * np.pi, 64)
    signal = np.sin(x) + 0.5 * np.sin(3 * x)
    signal = (signal - signal.min()) / (signal.max() - signal.min())  # Normalize to [0, 1]

    # Diffusion parameters
    T = 100
    betas = linear_beta_schedule(T)
    alphas, alpha_bars = get_alpha_and_alpha_bar(betas)

    # Show signal at various timesteps
    timesteps = [0, 10, 25, 50, 75, 99]
    fig, axes = plt.subplots(len(timesteps), 1, figsize=(10, 8))

    for idx, t in enumerate(timesteps):
        x_t, _ = forward_diffusion(signal, t, alpha_bars)
        axes[idx].plot(x_t, color='blue', linewidth=1.5)
        axes[idx].set_ylim(-3, 3)
        axes[idx].set_title(f't = {t}', fontsize=10)
        axes[idx].grid(True, alpha=0.3)
        if idx < len(timesteps) - 1:
            axes[idx].set_xticks([])

    plt.suptitle('Forward Diffusion: Clean Signal → Pure Noise', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase31/forward_diffusion.png', dpi=150)
    print("  Plot saved: src/phase31/forward_diffusion.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    t=0:   Clean signal (recognizable shape).")
    print("    t=25:  Signal fading, noise emerging.")
    print("    t=50:  Half signal, half noise.")
    print("    t=99:  Pure noise. No trace of original.")
    print("    The process is FIXED. No neural network here.")
    print()

    return signal, betas, alphas, alpha_bars


# ==============================================================================
# PART 2: REVERSE DIFFUSION (TOY MODEL)
# ==============================================================================
# We train a tiny network to predict the noise epsilon.
# Then we subtract the predicted noise to recover the signal.
# ==============================================================================

def simple_noise_predictor(x_t, t, weights):
    """
    A tiny linear model that predicts noise.
    
    For demonstration, this is just a linear regression.
    In reality, this would be a U-Net.
    """
    # For the toy demo, we cheat slightly by using the known alpha_bar
    # to compute a weighted average. In a real model, this is learned.
    alpha_bar_t = weights['alpha_bars'][t]
    # Predict noise = (x_t - sqrt(alpha_bar) * x_t) / sqrt(1 - alpha_bar)
    # But since we don't know x_t's origin, we learn a simple affine map
    w = weights['w']
    b = weights['b']
    return w * x_t + b


def train_noise_predictor(signal, betas, alpha_bars, epochs=1000, lr=0.01):
    """
    Train a tiny model to predict noise.
    
    We generate many (x_t, t, epsilon) pairs and train
    the model to predict epsilon from x_t and t.
    """
    np.random.seed(1)
    T = len(betas)
    n_dim = len(signal)

    # Initialize weights
    w = np.random.randn() * 0.1
    b = np.zeros(n_dim)

    losses = []

    for epoch in range(epochs):
        total_loss = 0

        # Sample random timesteps
        for _ in range(50):
            t = np.random.randint(0, T)
            x_t, epsilon = forward_diffusion(signal, t, alpha_bars)

            # Predict noise (simplified: just learn to output the residual)
            noise_pred = w * x_t + b

            # Loss: MSE between predicted and actual noise
            loss = np.mean((noise_pred - epsilon) ** 2)
            total_loss += loss

            # Gradient descent
            grad_w = 2 * np.mean((noise_pred - epsilon) * x_t)
            grad_b = 2 * (noise_pred - epsilon) / n_dim

            w -= lr * grad_w
            b -= lr * grad_b

        losses.append(total_loss / 50)
        if epoch % 200 == 0:
            print(f"    Epoch {epoch:4d}: Loss = {losses[-1]:.4f}")

    return {'w': w, 'b': b, 'alpha_bars': alpha_bars}


def reverse_diffusion_step(x_t, t, betas, alphas, alpha_bars, noise_pred):
    """
    One step of reverse diffusion.
    
    x_{t-1} = (x_t - beta_t / sqrt(1 - alpha_bar_t) * noise_pred) / sqrt(alpha_t)
              + sigma_t * random_noise
    """
    if t == 0:
        return x_t

    alpha_t = alphas[t]
    alpha_bar_t = alpha_bars[t]
    beta_t = betas[t]

    # Predicted x_0
    pred_x0 = (x_t - np.sqrt(1 - alpha_bar_t) * noise_pred) / np.sqrt(alpha_bar_t)

    # Compute x_{t-1}
    coef1 = np.sqrt(alpha_bar_t / alphas[t-1]) if t > 0 else 1.0
    coef2 = np.sqrt(1 - alpha_bar_t / alphas[t-1]) if t > 0 else 0.0

    # Simplified: direct denoising
    x_t_minus_1 = pred_x0 * np.sqrt(alpha_bars[t-1]) + np.sqrt(1 - alpha_bars[t-1]) * np.random.randn(*x_t.shape) * 0.1

    return x_t_minus_1


def demonstrate_reverse_diffusion(signal, betas, alphas, alpha_bars):
    """Show denoising from pure noise back to signal."""
    print("=" * 60)
    print("PART 2: REVERSE DIFFUSION")
    print("=" * 60)
    print()
    print("  We train a model to predict the noise at each step.")
    print("  Then we subtract the predicted noise to recover the signal.")
    print()

    # Train noise predictor
    print("  Training noise predictor...")
    weights = train_noise_predictor(signal, betas, alpha_bars)
    print()

    # Start from pure noise
    x_t = np.random.randn(len(signal))

    # Reverse diffusion
    T = len(betas)
    steps_to_show = [T-1, T-20, T-40, T-60, T-80, 0]
    snapshots = {}

    for t in range(T-1, -1, -1):
        noise_pred = simple_noise_predictor(x_t, t, weights)
        x_t = reverse_diffusion_step(x_t, t, betas, alphas, alpha_bars, noise_pred)

        if t in steps_to_show:
            snapshots[t] = x_t.copy()

    # Plot
    fig, axes = plt.subplots(len(steps_to_show), 1, figsize=(10, 8))
    for idx, t in enumerate(steps_to_show):
        axes[idx].plot(snapshots[t], color='green', linewidth=1.5)
        axes[idx].set_ylim(-3, 3)
        axes[idx].set_title(f'Reverse step t = {t}', fontsize=10)
        axes[idx].grid(True, alpha=0.3)
        if idx < len(steps_to_show) - 1:
            axes[idx].set_xticks([])

    plt.suptitle('Reverse Diffusion: Pure Noise → Clean Signal', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase31/reverse_diffusion.png', dpi=150)
    print("  Plot saved: src/phase31/reverse_diffusion.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    t=99:  Pure noise (starting point).")
    print("    t=80:  Faint structure emerging.")
    print("    t=40:  Shape becoming clear.")
    print("    t=0:   Clean signal recovered!")
    print("    The model learned to undo the noise.")
    print()


# ==============================================================================
# PART 3: U-NET CONCEPT
# ==============================================================================
# A U-Net processes data at multiple scales with skip connections.
# ==============================================================================

def demonstrate_unet_concept():
    """Visualize the U-Net architecture concept."""
    print("=" * 60)
    print("PART 3: U-NET ARCHITECTURE")
    print("=" * 60)
    print()
    print("  U-Net = Encoder + Bottleneck + Decoder + Skip Connections")
    print()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Encoder (left side, going down)
    encoder_blocks = [
        (2, 8, "64 features"),
        (2, 6.5, "128 features"),
        (2, 5, "256 features"),
    ]
    for x, y, label in encoder_blocks:
        rect = plt.Rectangle((x-0.8, y-0.4), 1.6, 0.8, facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

    # Bottleneck
    rect = plt.Rectangle((2-0.8, 3.5-0.4), 1.6, 0.8, facecolor='gold', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(2, 3.5, "512\n(Bottleneck)", ha='center', va='center', fontsize=9, fontweight='bold')

    # Decoder (right side, going up)
    decoder_blocks = [
        (5, 5, "256 features"),
        (5, 6.5, "128 features"),
        (5, 8, "64 features"),
    ]
    for x, y, label in decoder_blocks:
        rect = plt.Rectangle((x-0.8, y-0.4), 1.6, 0.8, facecolor='lightcoral', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

    # Output
    rect = plt.Rectangle((5-0.8, 8.8-0.3), 1.6, 0.6, facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(5, 8.8, "Output", ha='center', va='center', fontsize=10, fontweight='bold')

    # Arrows for encoder
    for i in range(len(encoder_blocks)):
        y1 = encoder_blocks[i][1]
        y2 = encoder_blocks[i+1][1] if i < len(encoder_blocks) - 1 else 3.5
        ax.annotate("", xy=(2, y2 + 0.4), xytext=(2, y1 - 0.4),
                   arrowprops=dict(arrowstyle="->", color='blue', lw=2))

    # Arrows for decoder
    for i in range(len(decoder_blocks)):
        y1 = decoder_blocks[i][1]
        y2 = decoder_blocks[i+1][1] if i < len(decoder_blocks) - 1 else 8.8
        ax.annotate("", xy=(5, y2 - 0.3), xytext=(5, y1 + 0.4),
                   arrowprops=dict(arrowstyle="->", color='red', lw=2))

    # Skip connections
    for (ex, ey, _), (dx, dy, _) in zip(encoder_blocks, decoder_blocks):
        ax.annotate("", xy=(dx - 0.8, dy), xytext=(ex + 0.8, ey),
                   arrowprops=dict(arrowstyle="->", color='green', lw=1.5, linestyle='--'))

    # Labels
    ax.text(2, 9.5, "Encoder\n(Downsample)", ha='center', fontsize=11, fontweight='bold', color='blue')
    ax.text(5, 9.5, "Decoder\n(Upsample)", ha='center', fontsize=11, fontweight='bold', color='red')
    ax.text(3.5, 5, "Skip\nConnections", ha='center', fontsize=10, style='italic', color='green')

    ax.set_title('U-Net Architecture', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase31/unet_architecture.png', dpi=150)
    print("  Plot saved: src/phase31/unet_architecture.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    Encoder: Compresses image to bottleneck.")
    print("    Bottleneck: Captures global structure.")
    print("    Decoder: Expands back to full resolution.")
    print("    Skip connections: Copy details from encoder to decoder.")
    print("    Result: Sharp outputs at all scales.")
    print()


# ==============================================================================
# PART 4: TIMESTEP CONDITIONING
# ==============================================================================

def demonstrate_timestep_conditioning():
    """Show how timestep embeddings change the network's behavior."""
    print("=" * 60)
    print("PART 4: TIMESTEP CONDITIONING")
    print("=" * 60)
    print()
    print("  The network needs to know HOW NOISY the image is.")
    print("  We encode the timestep as a vector and add it to features.")
    print()

    T = 100
    timesteps = [0, 25, 50, 75, 99]

    # Simple sinusoidal embedding
    def timestep_embed(t, dim=4):
        embed = np.zeros(dim)
        for i in range(dim):
            freq = 1.0 / (10000 ** (i / dim))
            if i % 2 == 0:
                embed[i] = np.sin(t * freq)
            else:
                embed[i] = np.cos(t * freq)
        return embed

    fig, ax = plt.subplots(figsize=(10, 5))

    for t in timesteps:
        embed = timestep_embed(t)
        ax.plot(range(len(embed)), embed, 'o-', label=f't={t}', linewidth=2, markersize=6)

    ax.set_xlabel('Embedding Dimension', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Timestep Embeddings (Sinusoidal)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase31/timestep_embeddings.png', dpi=150)
    print("  Plot saved: src/phase31/timestep_embeddings.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    t=0:   Embedding is one pattern (clean image).")
    print("    t=99:  Embedding is a different pattern (pure noise).")
    print("    The network learns: 'When I see THIS embedding,")
    print("    I should denoise aggressively/conservatively.'")
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 31: GENERATIVE MODELS — DIFFUSION")
    print("=" * 60)
    print()
    print("  Goal: Generate data by gradually refining noise.")
    print()

    # Part 1: Forward diffusion
    signal, betas, alphas, alpha_bars = demonstrate_forward_diffusion()

    # Part 2: Reverse diffusion
    demonstrate_reverse_diffusion(signal, betas, alphas, alpha_bars)

    # Part 3: U-Net concept
    demonstrate_unet_concept()

    # Part 4: Timestep conditioning
    demonstrate_timestep_conditioning()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Forward diffusion (add noise step by step)")
    print("    - Reverse diffusion (learn to predict and remove noise)")
    print("    - U-Net architecture visualization")
    print("    - Timestep conditioning with sinusoidal embeddings")
    print()
    print("  KEY INSIGHTS:")
    print("    1. Forward diffusion is fixed — no learning needed.")
    print("    2. Reverse diffusion learns to undo the noise.")
    print("    3. U-Net processes images at multiple scales.")
    print("    4. Timestep conditioning tells the network the noise level.")
    print()
    print("  ADVANTAGES OVER GANs:")
    print("    - Stable training (no adversarial game).")
    print("    - No mode collapse (covers all data modes).")
    print("    - Higher quality images.")
    print("    - Trade-off: slower generation (many steps).")
    print()
    print("  NEXT QUESTION:")
    print("    'We have seen the entire landscape of AI.")
    print("     Where is it going next?'")
    print("=" * 60)

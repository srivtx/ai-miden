#!/usr/bin/env python3
"""
================================================================================
Phase 29: Generative Models — VAEs (Variational Autoencoders)
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 28, we made the model SEE images.
Now we ask: "Can the model CREATE new images?"

We cover five concepts:
  1. Autoencoder          — Compress and reconstruct
  2. Latent Space         — The structured bottleneck
  3. VAE                  — Probabilistic latent codes
  4. Reparameterization   — Differentiable sampling
  5. KL Divergence        — Keeping the space smooth

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
# PART 1: AUTOENCODER
# ==============================================================================
# An autoencoder has two parts:
#   Encoder: input -> compressed code
#   Decoder: code -> reconstructed input
# It learns to copy the input to the output, forcing it to
# find an efficient compression in the middle.
# ==============================================================================

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def autoencoder_forward(x, W_enc, b_enc, W_dec, b_dec):
    """
    Forward pass through a simple autoencoder.
    
    PARAMETERS:
        x      = input vector (n_input,)
        W_enc  = encoder weights (n_input, n_latent)
        b_enc  = encoder bias (n_latent,)
        W_dec  = decoder weights (n_latent, n_input)
        b_dec  = decoder bias (n_input,)
    
    RETURNS:
        latent = compressed code
        output = reconstruction
    """
    # Encoder: compress
    latent = sigmoid(x @ W_enc + b_enc)

    # Decoder: reconstruct
    output = sigmoid(latent @ W_dec + b_dec)

    return latent, output


def train_autoencoder(X, n_latent=2, epochs=5000, lr=0.5):
    """Train a tiny autoencoder on simple patterns."""
    np.random.seed(42)
    n_input = X.shape[1]

    # Initialize weights
    W_enc = np.random.randn(n_input, n_latent) * 0.5
    b_enc = np.zeros(n_latent)
    W_dec = np.random.randn(n_latent, n_input) * 0.5
    b_dec = np.zeros(n_input)

    losses = []

    for epoch in range(epochs):
        total_loss = 0
        for x in X:
            # Forward
            latent, output = autoencoder_forward(x, W_enc, b_enc, W_dec, b_dec)

            # Loss: mean squared error
            loss = np.mean((x - output) ** 2)
            total_loss += loss

            # Backprop (simplified manual gradients)
            d_output = 2 * (output - x) / n_input
            d_output *= output * (1 - output)  # sigmoid derivative

            d_W_dec = np.outer(latent, d_output)
            d_b_dec = d_output

            d_latent = d_output @ W_dec.T
            d_latent *= latent * (1 - latent)

            d_W_enc = np.outer(x, d_latent)
            d_b_enc = d_latent

            # Update
            W_dec -= lr * d_W_dec
            b_dec -= lr * d_b_dec
            W_enc -= lr * d_W_enc
            b_enc -= lr * d_b_enc

        losses.append(total_loss / len(X))
        if epoch % 1000 == 0:
            print(f"    Epoch {epoch:5d}: Loss = {losses[-1]:.4f}")

    return W_enc, b_enc, W_dec, b_dec, losses


def demonstrate_autoencoder():
    """Show autoencoder compression and reconstruction."""
    print("=" * 60)
    print("PART 1: AUTOENCODER")
    print("=" * 60)
    print()
    print("  Encoder compresses. Decoder reconstructs.")
    print("  The bottleneck forces the model to learn what matters.")
    print()

    # Simple 8-pixel patterns (like tiny 2x4 images)
    patterns = np.array([
        [1, 1, 0, 0, 0, 0, 0, 0],  # left half bright
        [0, 0, 1, 1, 0, 0, 0, 0],  # middle-left bright
        [0, 0, 0, 0, 1, 1, 0, 0],  # middle-right bright
        [0, 0, 0, 0, 0, 0, 1, 1],  # right half bright
        [1, 0, 1, 0, 1, 0, 1, 0],  # checkerboard
        [0, 1, 0, 1, 0, 1, 0, 1],  # inverse checkerboard
        [1, 1, 1, 1, 0, 0, 0, 0],  # left half all bright
        [0, 0, 0, 0, 1, 1, 1, 1],  # right half all bright
    ])

    print(f"  Training on {len(patterns)} patterns of {patterns.shape[1]} pixels each.")
    print(f"  Compressing to 2 latent dimensions.")
    print()

    W_enc, b_enc, W_dec, b_dec, losses = train_autoencoder(patterns, n_latent=2)

    print()
    print("  Reconstructions:")
    print("  Pattern | Original          | Reconstructed     | Error")
    print("  " + "-" * 65)
    for i, x in enumerate(patterns):
        _, recon = autoencoder_forward(x, W_enc, b_enc, W_dec, b_dec)
        error = np.mean((x - recon) ** 2)
        orig_str = "".join(["█" if v > 0.5 else "░" for v in x])
        recon_str = "".join(["█" if v > 0.5 else "░" for v in recon])
        print(f"  {i:7d} | {orig_str} | {recon_str} | {error:.4f}")

    print()
    print("  KEY INSIGHT:")
    print("    8 pixels compressed to 2 numbers, then expanded back.")
    print("    The autoencoder learned the essential structure.")
    print("    But can it generate NEW patterns? Not yet.")
    print()

    return W_enc, b_enc, W_dec, b_dec, patterns


# ==============================================================================
# PART 2: VAE — VARIATIONAL AUTOENCODER
# ==============================================================================
# Instead of outputting a single latent code,
# the encoder outputs a DISTRIBUTION: mean and log_variance.
# We sample from that distribution, and a KL term keeps it
# close to a standard normal N(0, 1).
# ==============================================================================

def vae_encode(x, W_mu, b_mu, W_logvar, b_logvar):
    """
    Encoder outputs mu and log_var for a Gaussian distribution.
    """
    mu = x @ W_mu + b_mu
    log_var = x @ W_logvar + b_logvar
    return mu, log_var


def reparameterize(mu, log_var):
    """
    The reparameterization trick.
    
    z = mu + sigma * epsilon
    where epsilon ~ N(0, 1)
    
    This makes sampling differentiable!
    """
    std = np.exp(0.5 * log_var)
    epsilon = np.random.randn(*mu.shape)
    z = mu + std * epsilon
    return z


def vae_decode(z, W_dec, b_dec):
    """Decoder reconstructs from latent sample."""
    return sigmoid(z @ W_dec + b_dec)


def kl_divergence(mu, log_var):
    """
    KL divergence of N(mu, sigma^2) from N(0, 1).
    
    Formula: -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    """
    return -0.5 * np.sum(1 + log_var - mu**2 - np.exp(log_var))


def train_vae(X, n_latent=2, epochs=5000, lr=1.0, beta=0.5):
    """Train a VAE with KL divergence regularization."""
    np.random.seed(42)
    n_input = X.shape[1]

    # Initialize weights — start from a working point
    W_mu = np.random.randn(n_input, n_latent) * 0.5
    b_mu = np.zeros(n_latent)
    W_logvar = np.random.randn(n_input, n_latent) * 0.1
    b_logvar = np.zeros(n_latent)
    W_dec = np.random.randn(n_latent, n_input) * 0.5
    # Initialize decoder bias to data mean so default output isn't all zeros
    b_dec = np.mean(X, axis=0)

    recon_losses = []
    kl_losses = []
    total_losses = []

    for epoch in range(epochs):
        total_recon = 0
        total_kl = 0

        for x in X:
            # Forward
            mu, log_var = vae_encode(x, W_mu, b_mu, W_logvar, b_logvar)
            z = reparameterize(mu, log_var)
            output = vae_decode(z, W_dec, b_dec)

            # Losses
            recon_loss = np.mean((x - output) ** 2)
            kl_loss = kl_divergence(mu, log_var)
            loss = recon_loss + beta * kl_loss / n_latent

            total_recon += recon_loss
            total_kl += kl_loss

            # --- Gradients ---
            # Reconstruction gradient w.r.t. decoder output
            d_output = 2 * (output - x) / n_input
            d_output *= output * (1 - output)  # sigmoid derivative

            # Decoder gradients
            d_W_dec = np.outer(z, d_output)
            d_b_dec = d_output

            # Gradient w.r.t. z
            d_z = d_output @ W_dec.T

            # Reparameterization: z = mu + sigma * epsilon
            # So dL/dmu = dL/dz * dz/dmu = dL/dz * 1
            # And dL/d(sigma) = dL/dz * epsilon
            # But sigma = exp(0.5 * log_var), so:
            # dL/d(log_var) = dL/d(sigma) * d(sigma)/d(log_var)
            #               = dL/dz * epsilon * 0.5 * exp(0.5 * log_var)
            #               = dL/dz * 0.5 * sigma * epsilon
            #               = dL/dz * 0.5 * (z - mu)
            epsilon = (z - mu) / (np.exp(0.5 * log_var) + 1e-8)
            d_mu = d_z.copy()
            d_log_var = d_z * 0.5 * epsilon * np.exp(0.5 * log_var)

            # KL divergence gradients
            # KL = -0.5 * sum(1 + log_var - mu^2 - exp(log_var))
            # d(KL)/dmu = -0.5 * (-2*mu) = mu
            # d(KL)/d(log_var) = -0.5 * (1 - exp(log_var))
            d_mu += beta * mu / n_latent
            d_log_var += beta * (-0.5) * (1 - np.exp(log_var)) / n_latent

            # Encoder gradients
            d_W_mu = np.outer(x, d_mu)
            d_b_mu = d_mu
            d_W_logvar = np.outer(x, d_log_var)
            d_b_logvar = d_log_var

            # Update
            W_dec -= lr * d_W_dec
            b_dec -= lr * d_b_dec
            W_mu -= lr * d_W_mu
            b_mu -= lr * d_b_mu
            W_logvar -= lr * d_W_logvar
            b_logvar -= lr * d_b_logvar

        recon_losses.append(total_recon / len(X))
        kl_losses.append(total_kl / len(X))
        total_losses.append(recon_losses[-1] + beta * kl_losses[-1] / n_latent)

        if epoch % 1000 == 0:
            print(f"    Epoch {epoch:5d}: Recon={recon_losses[-1]:.4f}, KL={kl_losses[-1]:.4f}")

    return W_mu, b_mu, W_logvar, b_logvar, W_dec, b_dec, (recon_losses, kl_losses, total_losses)


def demonstrate_vae():
    """Show VAE encoding, sampling, and generation."""
    print("=" * 60)
    print("PART 2: VAE — VARIATIONAL AUTOENCODER")
    print("=" * 60)
    print()
    print("  Encoder outputs a DISTRIBUTION (mu, log_var).")
    print("  We sample from it using the reparameterization trick.")
    print("  KL divergence keeps the distribution close to N(0,1).")
    print()

    patterns = np.array([
        [1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1],
    ])

    print("  Training VAE...")
    W_mu, b_mu, W_logvar, b_logvar, W_dec, b_dec, loss_history = train_vae(patterns, n_latent=2)
    print()

    # Encode all patterns to see latent space
    print("  Latent codes (mu) for each pattern:")
    latents = []
    for i, x in enumerate(patterns):
        mu, _ = vae_encode(x, W_mu, b_mu, W_logvar, b_logvar)
        latents.append(mu)
        print(f"    Pattern {i}: mu = [{mu[0]:6.3f}, {mu[1]:6.3f}]")
    latents = np.array(latents)
    print()

    # Generate NEW patterns by sampling from N(0,1)
    print("  GENERATING NEW PATTERNS (sampling from N(0,1)):")
    print("  Sample | Latent z         | Generated Pattern")
    print("  " + "-" * 55)
    for i in range(5):
        z = np.random.randn(2)
        generated = vae_decode(z, W_dec, b_dec)
        gen_str = "".join(["█" if v > 0.5 else "░" for v in generated])
        print(f"  {i:6d} | [{z[0]:6.3f}, {z[1]:6.3f}] | {gen_str}")
    print()

    print("  KEY INSIGHT:")
    print("    The VAE learned a SMOOTH latent space.")
    print("    Any point in N(0,1) decodes to a plausible pattern.")
    print("    This is GENERATION — creating new data, not copying.")
    print()

    return W_mu, b_mu, W_logvar, b_logvar, W_dec, b_dec, latents, loss_history


# ==============================================================================
# PART 3: LATENT SPACE INTERPOLATION
# ==============================================================================
# In a smooth latent space, moving between two points
# produces a smooth morph between the two outputs.
# ==============================================================================

def demonstrate_interpolation(W_dec, b_dec, latents):
    """Show smooth transitions between latent codes."""
    print("=" * 60)
    print("PART 3: LATENT SPACE INTERPOLATION")
    print("=" * 60)
    print()
    print("  Moving smoothly between two latent codes should")
    print("  produce a smooth morph between the two patterns.")
    print()

    # Interpolate between pattern 0 and pattern 7
    z1 = latents[0]  # left half bright
    z2 = latents[7]  # right half bright

    print("  Interpolating from Pattern 0 to Pattern 7:")
    print("  Alpha | Latent z            | Output")
    print("  " + "-" * 50)

    alphas = np.linspace(0, 1, 7)
    interpolated = []
    for alpha in alphas:
        z = (1 - alpha) * z1 + alpha * z2
        output = vae_decode(z, W_dec, b_dec)
        interpolated.append(output)
        out_str = "".join(["█" if v > 0.5 else "░" for v in output])
        print(f"  {alpha:5.2f} | [{z[0]:6.3f}, {z[1]:6.3f}] | {out_str}")

    print()
    print("  KEY INSIGHT:")
    print("    At alpha=0: Pattern 0 (left bright).")
    print("    At alpha=1: Pattern 7 (right bright).")
    print("    In between: Smooth transition!")
    print("    This proves the latent space is structured.")
    print()

    return interpolated


# ==============================================================================
# PART 4: VISUALIZATION
# ==============================================================================

def visualize_results(losses_ae, latents, loss_history, interpolated):
    """Plot training curves and latent space."""
    print("=" * 60)
    print("VISUALIZATION")
    print("=" * 60)
    print()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Autoencoder loss
    axes[0, 0].plot(losses_ae, color='blue', linewidth=2)
    axes[0, 0].set_xlabel('Epoch', fontsize=11)
    axes[0, 0].set_ylabel('MSE Loss', fontsize=11)
    axes[0, 0].set_title('Autoencoder Training Loss', fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: VAE losses
    recon_losses, kl_losses, total_losses = loss_history
    axes[0, 1].plot(recon_losses, label='Reconstruction', color='blue', linewidth=2)
    axes[0, 1].plot([k / 10 for k in kl_losses], label='KL (scaled /10)', color='red', linewidth=2)
    axes[0, 1].set_xlabel('Epoch', fontsize=11)
    axes[0, 1].set_ylabel('Loss', fontsize=11)
    axes[0, 1].set_title('VAE Training: Reconstruction vs KL', fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Latent space
    axes[1, 0].scatter(latents[:, 0], latents[:, 1], c=range(len(latents)), 
                       cmap='tab10', s=200, edgecolors='black', linewidth=2)
    for i, (x, y) in enumerate(latents):
        axes[1, 0].annotate(str(i), (x, y), textcoords="offset points", 
                           xytext=(5, 5), fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Latent Dimension 1', fontsize=11)
    axes[1, 0].set_ylabel('Latent Dimension 2', fontsize=11)
    axes[1, 0].set_title('VAE Latent Space', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axhline(y=0, color='k', linewidth=0.5)
    axes[1, 0].axvline(x=0, color='k', linewidth=0.5)

    # Plot 4: Interpolation grid
    n_interp = len(interpolated)
    interp_grid = np.array(interpolated).reshape(n_interp, 1, 8)
    axes[1, 1].imshow(interp_grid.squeeze(), cmap='gray', aspect='auto')
    axes[1, 1].set_xlabel('Pixel Position', fontsize=11)
    axes[1, 1].set_ylabel('Interpolation Step', fontsize=11)
    axes[1, 1].set_title('Latent Space Interpolation', fontweight='bold')
    axes[1, 1].set_yticks(range(n_interp))
    axes[1, 1].set_yticklabels([f'{a:.2f}' for a in np.linspace(0, 1, n_interp)])

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase29/vae_results.png', dpi=150)
    print("  Plot saved: src/phase29/vae_results.png")
    plt.close()
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 29: GENERATIVE MODELS — VAEs")
    print("=" * 60)
    print()
    print("  Goal: Create new data by learning a smooth latent space.")
    print()

    # Part 1: Autoencoder
    W_enc, b_enc, W_dec_ae, b_dec_ae, patterns = demonstrate_autoencoder()

    # Train autoencoder to get loss curve
    _, _, _, _, losses_ae = train_autoencoder(patterns, n_latent=2)

    # Part 2: VAE
    W_mu, b_mu, W_logvar, b_logvar, W_dec, b_dec, latents, loss_history = demonstrate_vae()

    # Part 3: Interpolation
    interpolated = demonstrate_interpolation(W_dec, b_dec, latents)

    # Visualization
    visualize_results(losses_ae, latents, loss_history, interpolated)

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Autoencoder that compresses 8 pixels to 2 numbers")
    print("    - VAE with probabilistic latent distributions")
    print("    - Reparameterization trick for differentiable sampling")
    print("    - KL divergence to regularize the latent space")
    print("    - Latent space interpolation showing smooth morphs")
    print()
    print("  KEY INSIGHTS:")
    print("    1. Autoencoders compress but cannot generate.")
    print("    2. VAEs output distributions, not points.")
    print("    3. The reparameterization trick makes sampling work with backprop.")
    print("    4. KL divergence forces a smooth, structured latent space.")
    print("    5. Sampling from N(0,1) produces NEW, plausible data.")
    print()
    print("  LIMITATION:")
    print("    VAE reconstructions are blurry because MSE averages pixels.")
    print("    Next: How do we make generated images SHARP?")
    print()
    print("  NEXT QUESTION:")
    print("    'VAE images are blurry. How do we generate")
    print("     sharp, realistic images?'")
    print("=" * 60)

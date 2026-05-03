"""
Phase 103: Multimodal Data Curation
NumPy simulation of CLIP-style scoring.
Image embeddings and text embeddings, dot product as similarity.
Show how filtering by similarity score improves "dataset quality."
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

np.random.seed(103)


def generate_embeddings(n_pairs, dim=64, noise_std=0.5):
    """
    Generate synthetic image and text embeddings.
    A shared latent vector creates alignment; independent noise creates misalignment.
    """
    shared = np.random.randn(n_pairs, dim)
    image_emb = shared + np.random.normal(0, noise_std, size=(n_pairs, dim))
    text_emb = shared + np.random.normal(0, noise_std, size=(n_pairs, dim))
    return image_emb, text_emb


def clip_scores(image_emb, text_emb):
    """Compute dot product similarity for each pair."""
    return np.sum(image_emb * text_emb, axis=1)


def temporal_alignment_score(n_windows=20, max_shift=5):
    """
    Simulate temporal alignment: a true event at time t should match audio at time t.
    Score drops as temporal shift increases.
    """
    true_time = 10
    times = np.arange(n_windows)
    scores = np.exp(-0.5 * ((times - true_time) / max_shift) ** 2)
    return times, scores


def simulate_multimodal_data_curation(output_dir="."):
    n_pairs = 2000
    dim = 64

    # Generate aligned and noisy pairs
    image_aligned, text_aligned = generate_embeddings(n_pairs, dim, noise_std=0.3)
    # Noisy pairs: anti-correlated shared latent so dot product is low on average
    shared_noisy = np.random.randn(n_pairs, dim)
    image_noisy = shared_noisy + np.random.normal(0, 1.5, size=(n_pairs, dim))
    text_noisy = -shared_noisy + np.random.normal(0, 1.5, size=(n_pairs, dim))

    scores_aligned = clip_scores(image_aligned, text_aligned)
    scores_noisy = clip_scores(image_noisy, text_noisy)

    # Combine into a mock dataset
    all_scores = np.concatenate([scores_aligned, scores_noisy])
    is_aligned = np.array([True] * n_pairs + [False] * n_pairs)

    # Filter by threshold
    thresholds = np.percentile(all_scores, [25, 50, 75])

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # Plot 1: Score distributions
    ax = axes[0]
    ax.hist(scores_aligned, bins=50, alpha=0.6, color="blue", label="Aligned pairs", density=True)
    ax.hist(scores_noisy, bins=50, alpha=0.6, color="red", label="Noisy pairs", density=True)
    ax.set_title("CLIP Score Distributions")
    ax.set_xlabel("Dot-product similarity")
    ax.set_ylabel("Density")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    # Plot 2: Precision vs threshold
    ax = axes[1]
    precisions = []
    for thresh in thresholds:
        mask = all_scores >= thresh
        if mask.sum() == 0:
            precisions.append(0.0)
        else:
            precisions.append(is_aligned[mask].mean())
    ax.bar([f"P{t:.0f}" for t in [25, 50, 75]], precisions, color="green", alpha=0.7)
    ax.set_ylim(0, 1.1)
    ax.set_title("Precision After Filtering")
    ax.set_ylabel("Fraction of aligned pairs")
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    # Plot 3: Temporal alignment
    ax = axes[2]
    times, t_scores = temporal_alignment_score()
    ax.plot(times, t_scores, marker="o")
    ax.axvline(10, color="red", linestyle="--", label="True event time")
    ax.set_title("Temporal Alignment Score")
    ax.set_xlabel("Time window")
    ax.set_ylabel("Alignment score")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "phase103_multimodal_data.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot to {out_path}")

    print("\nDataset quality after filtering:")
    for t, p in zip([25, 50, 75], precisions):
        print(f"  Top {100-t:.0f}% by score: {p:.1%} aligned pairs")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    simulate_multimodal_data_curation(output_dir=script_dir)

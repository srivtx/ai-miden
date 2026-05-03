"""
Phase 102: Synthetic Data Bootstrapping
NumPy simulation of rejection sampling.
Generate samples from a distribution, keep only those above a threshold.
Show how this shifts the effective distribution.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

np.random.seed(102)


def generate_samples(n, mean=0.0, std=1.0):
    """Generate samples from a Gaussian."""
    return np.random.normal(mean, std, size=n)


def verifier_scores(samples, true_mean=2.0):
    """
    Verifier scores samples by negative distance to a true_mean.
    Higher score is better.
    """
    return -np.abs(samples - true_mean)


def rejection_sample(samples, scores, threshold):
    """Keep samples with score >= threshold."""
    mask = scores >= threshold
    return samples[mask], scores[mask]


def simulate_synthetic_data_bootstrapping(output_dir="."):
    n_total = 5000
    samples = generate_samples(n_total, mean=0.5, std=1.5)
    scores = verifier_scores(samples, true_mean=2.0)

    thresholds = [-0.5, 0.0, 0.5, 1.0]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    for idx, thresh in enumerate(thresholds):
        accepted, acc_scores = rejection_sample(samples, scores, thresh)
        acceptance_rate = len(accepted) / n_total

        ax = axes[idx]
        ax.hist(samples, bins=60, alpha=0.4, color="gray", label="All samples", density=True)
        ax.hist(accepted, bins=60, alpha=0.7, color="blue", label="Accepted", density=True)
        ax.axvline(2.0, color="red", linestyle="--", label="True mean")
        ax.set_title(f"Threshold={thresh:.1f} | Accept={acceptance_rate:.1%}")
        ax.set_xlabel("Sample value")
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "phase102_synthetic_data.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot to {out_path}")

    # Self-improvement loop simulation
    print("\nSelf-Improvement Loop Simulation:")
    current_mean = 0.5
    for step in range(5):
        s = generate_samples(2000, mean=current_mean, std=1.2)
        sc = verifier_scores(s, true_mean=2.0)
        accepted, _ = rejection_sample(s, sc, threshold=-1.0)
        if len(accepted) > 0:
            current_mean = np.mean(accepted)
        print(f"  Step {step+1}: mean={current_mean:.3f}, accepted={len(accepted)/2000:.1%}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    simulate_synthetic_data_bootstrapping(output_dir=script_dir)

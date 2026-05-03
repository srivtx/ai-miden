"""
Phase 110: Test-Time Compute Scaling (Search, Refinement)
NumPy simulation of best-of-N:
sample N outputs from a distribution, score them with a "verifier," return best.
Show accuracy vs N trade-off.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)


def sample_output(true_value, model_quality):
    """
    Simulate generating an answer.
    Higher model_quality -> lower variance around true_value.
    """
    noise_std = 1.0 / (model_quality + 0.1)
    return true_value + np.random.randn() * noise_std


def verifier_score(output, true_value, verifier_quality):
    """
    Simulate a verifier that scores how good an output is.
    Higher verifier_quality -> more correlated with true error.
    """
    true_error = abs(output - true_value)
    noise_std = 1.0 / (verifier_quality + 0.1)
    perceived_error = true_error + np.random.randn() * noise_std
    return -perceived_error  # higher is better


def best_of_n(true_value, n, model_quality, verifier_quality):
    """Sample N outputs and return the one with highest verifier score."""
    outputs = [sample_output(true_value, model_quality) for _ in range(n)]
    scores = [verifier_score(o, true_value, verifier_quality) for o in outputs]
    best_idx = np.argmax(scores)
    return outputs[best_idx]


def main():
    true_value = 5.0
    model_quality = 1.0
    verifier_quality = 2.0

    # Single sample baseline
    single_samples = [sample_output(true_value, model_quality) for _ in range(1000)]
    baseline_error = np.mean([abs(o - true_value) for o in single_samples])
    print(f"Baseline (single sample) mean absolute error: {baseline_error:.3f}")

    # Best-of-N sweep
    N_values = [1, 2, 4, 8, 16, 32, 64, 128]
    errors = []
    for N in N_values:
        trials = [best_of_n(true_value, N, model_quality, verifier_quality) for _ in range(1000)]
        mean_error = np.mean([abs(t - true_value) for t in trials])
        errors.append(mean_error)
        print(f"Best-of-{N:3d} mean absolute error: {mean_error:.3f}")

    print()

    # Also show with a weaker verifier
    verifier_quality_weak = 0.5
    errors_weak = []
    for N in N_values:
        trials = [best_of_n(true_value, N, model_quality, verifier_quality_weak) for _ in range(1000)]
        mean_error = np.mean([abs(t - true_value) for t in trials])
        errors_weak.append(mean_error)

    # Plot accuracy vs N
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(N_values, errors, marker='o', label='Strong verifier', color='blue')
    ax.plot(N_values, errors_weak, marker='s', label='Weak verifier', color='red')
    ax.axhline(baseline_error, color='gray', linestyle='--', label='Single-sample baseline')
    ax.set_xlabel('N (number of samples)')
    ax.set_ylabel('Mean absolute error')
    ax.set_title('Test-Time Compute Scaling: Best-of-N Accuracy Trade-off')
    ax.set_xscale('log', base=2)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig('src/phase110/best_of_n_tradeoff.png')
    print("Saved plot to src/phase110/best_of_n_tradeoff.png")

    # Plot: accuracy gain vs compute cost
    # Assume compute is proportional to N
    compute = np.array(N_values)
    gain_strong = baseline_error - np.array(errors)
    gain_weak = baseline_error - np.array(errors_weak)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(compute, gain_strong, marker='o', label='Strong verifier', color='blue')
    ax2.plot(compute, gain_weak, marker='s', label='Weak verifier', color='red')
    ax2.set_xlabel('Compute (proportional to N)')
    ax2.set_ylabel('Error reduction')
    ax2.set_title('Test-Time Compute: Accuracy Gain vs Compute Cost')
    ax2.set_xscale('log', base=2)
    ax2.legend()
    ax2.grid(True)
    fig2.tight_layout()
    fig2.savefig('src/phase110/compute_vs_gain.png')
    print("Saved plot to src/phase110/compute_vs_gain.png")


if __name__ == '__main__':
    main()

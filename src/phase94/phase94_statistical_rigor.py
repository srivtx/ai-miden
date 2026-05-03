"""
Phase 94: Experiment Design & Statistical Rigor
NumPy demo of bootstrapping confidence intervals and paired t-test simulation.
No PyTorch. Uses matplotlib Agg backend.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(94)


def generate_model_predictions(n_samples=200, model_bias=0.0):
    """
    Generate synthetic binary labels and two models' probability predictions.
    Model A is slightly better than Model B on average.
    """
    # True labels
    y = np.random.randint(0, 2, size=n_samples)

    # Model A predictions: more aligned with true labels
    probs_a = np.clip(y * 0.85 + (1 - y) * 0.15 + np.random.randn(n_samples) * 0.1, 0.01, 0.99)
    # Model B predictions: weaker signal
    probs_b = np.clip(y * 0.75 + (1 - y) * 0.25 + np.random.randn(n_samples) * 0.1 + model_bias, 0.01, 0.99)

    preds_a = (probs_a >= 0.5).astype(int)
    preds_b = (probs_b >= 0.5).astype(int)
    return y, preds_a, preds_b


def bootstrap_accuracy_ci(y_true, y_pred, n_bootstrap=1000, confidence=0.95):
    """
    Compute a bootstrap confidence interval for accuracy.
    """
    n = len(y_true)
    indices = np.arange(n)
    accuracies = []
    for _ in range(n_bootstrap):
        sample_idx = np.random.choice(indices, size=n, replace=True)
        acc = np.mean(y_pred[sample_idx] == y_true[sample_idx])
        accuracies.append(acc)

    alpha = 1 - confidence
    lower = np.percentile(accuracies, 100 * alpha / 2)
    upper = np.percentile(accuracies, 100 * (1 - alpha / 2))
    return lower, upper, accuracies


def paired_t_test_simulation(y_true, preds_a, preds_b, n_runs=30):
    """
    Simulate repeated evaluations on resampled data to compare two models
    with a paired t-test.
    """
    diffs = []
    for _ in range(n_runs):
        # Resample the test set to simulate evaluation variance
        idx = np.random.choice(len(y_true), size=len(y_true), replace=True)
        acc_a = np.mean(preds_a[idx] == y_true[idx])
        acc_b = np.mean(preds_b[idx] == y_true[idx])
        diffs.append(acc_a - acc_b)

    diffs = np.array(diffs)
    mean_diff = np.mean(diffs)
    std_diff = np.std(diffs, ddof=1)
    se = std_diff / np.sqrt(len(diffs))
    t_stat = mean_diff / se if se > 0 else 0.0

    # Two-tailed p-value approximation using t-distribution is complex in raw NumPy,
    # so we use a simple permutation test on the differences.
    observed = mean_diff
    # Null hypothesis: differences are centered at zero
    # Permute signs to simulate null
    n_perm = 2000
    perm_stats = []
    for _ in range(n_perm):
        signs = np.random.choice([-1, 1], size=len(diffs))
        perm_diffs = diffs * signs
        perm_stats.append(np.mean(perm_diffs))

    perm_stats = np.array(perm_stats)
    p_value = np.mean(np.abs(perm_stats) >= np.abs(observed))
    return mean_diff, t_stat, p_value, diffs


def plot_bootstrap_distribution(accuracies, ci_lower, ci_upper, output_path="phase94_bootstrap.png"):
    """
    Histogram of bootstrap accuracies with confidence interval marked.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(accuracies, bins=40, color="steelblue", edgecolor="white", alpha=0.8)
    ax.axvline(ci_lower, color="crimson", linestyle="--", label=f"95% CI lower={ci_lower:.3f}")
    ax.axvline(ci_upper, color="crimson", linestyle="--", label=f"95% CI upper={ci_upper:.3f}")
    ax.axvline(np.mean(accuracies), color="gold", linestyle="-", label=f"Mean={np.mean(accuracies):.3f}")
    ax.set_xlabel("Accuracy")
    ax.set_ylabel("Frequency")
    ax.set_title("Phase 94: Bootstrap Confidence Interval for Accuracy")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path)
    print(f"Saved bootstrap plot to {output_path}")


def main():
    # Generate synthetic predictions
    y_true, preds_a, preds_b = generate_model_predictions(n_samples=300, model_bias=0.0)

    # Bootstrap CI for Model A
    ci_low, ci_high, accs = bootstrap_accuracy_ci(y_true, preds_a, n_bootstrap=1000, confidence=0.95)
    print(f"Model A accuracy 95% CI: [{ci_low:.4f}, {ci_high:.4f}]")

    # Paired comparison of Model A vs Model B
    mean_diff, t_stat, p_value, diffs = paired_t_test_simulation(y_true, preds_a, preds_b, n_runs=30)
    print(f"\nPaired comparison (A vs B) over 30 resampled evaluations:")
    print(f"  Mean accuracy difference: {mean_diff:.4f}")
    print(f"  t-statistic (approx):     {t_stat:.4f}")
    print(f"  p-value (permutation):    {p_value:.4f}")

    if p_value < 0.05:
        print("  Result: Statistically significant improvement.")
    else:
        print("  Result: Not statistically significant at alpha=0.05.")

    # Variance reduction demo: compare single split vs averaged splits
    single_diffs = []
    for _ in range(30):
        idx = np.random.choice(len(y_true), size=len(y_true), replace=True)
        single_diffs.append(np.mean(preds_a[idx] == y_true[idx]) - np.mean(preds_b[idx] == y_true[idx]))
    print(f"\nVariance of single-split differences: {np.var(single_diffs):.6f}")
    print(f"Variance of averaged-run differences: {np.var(diffs):.6f}")

    plot_bootstrap_distribution(accs, ci_low, ci_high, output_path="phase94_bootstrap.png")


if __name__ == "__main__":
    main()

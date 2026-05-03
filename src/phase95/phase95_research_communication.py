"""
Phase 95: Open Source & Research Communication
NumPy demo with BEFORE/AFTER code.
BEFORE: poorly written research code with a subtle bug.
AFTER: well-documented, modular version where the bug is obvious and fixed.
No PyTorch. Uses matplotlib Agg backend.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(95)


# ============================================================================
# BEFORE: Poorly written research code
# ============================================================================
def run_exp_b(x, y, lr, iters):
    # no docstring, cryptic names
    w = np.zeros(x.shape[1])
    for i in range(iters):
        p = 1 / (1 + np.exp(-x @ w))
        # BUG: gradient uses wrong sign because author confused loss direction
        g = x.T @ (p - y) / len(y)
        w = w + lr * g  # BUG: should be minus for gradient descent
    return w


# ============================================================================
# AFTER: Well-documented, modular research code
# ============================================================================
def logistic_predictions(features, weights):
    """
    Compute logistic sigmoid predictions for binary classification.
    Parameters
    ----------
    features : ndarray, shape (n_samples, n_features)
    weights : ndarray, shape (n_features,)
    Returns
    -------
    probs : ndarray, shape (n_samples,)
    """
    logits = features @ weights
    # Numerically stable sigmoid
    probs = np.where(
        logits >= 0,
        1.0 / (1.0 + np.exp(-logits)),
        np.exp(logits) / (1.0 + np.exp(logits)),
    )
    return probs


def compute_gradients(features, labels, predictions):
    """
    Compute gradients of binary cross-entropy loss with respect to weights.
    Parameters
    ----------
    features : ndarray, shape (n_samples, n_features)
    labels : ndarray, shape (n_samples,)
    predictions : ndarray, shape (n_samples,)
    Returns
    -------
    gradients : ndarray, shape (n_features,)
    """
    errors = predictions - labels
    gradients = features.T @ errors / len(labels)
    return gradients


def train_logistic_regression(features, labels, learning_rate, n_iterations):
    """
    Train a logistic regression model using gradient descent.
    Parameters
    ----------
    features : ndarray, shape (n_samples, n_features)
    labels : ndarray, shape (n_samples,)
    learning_rate : float
    n_iterations : int
    Returns
    -------
    weights : ndarray, shape (n_features,)
    loss_history : list of float
    """
    n_features = features.shape[1]
    weights = np.zeros(n_features)
    loss_history = []

    for iteration in range(n_iterations):
        predictions = logistic_predictions(features, weights)
        # Binary cross-entropy
        eps = 1e-9
        loss = -np.mean(
            labels * np.log(predictions + eps)
            + (1 - labels) * np.log(1 - predictions + eps)
        )
        loss_history.append(loss)

        grads = compute_gradients(features, labels, predictions)
        # CORRECT: subtract gradient to minimize loss
        weights -= learning_rate * grads

    return weights, loss_history


# ============================================================================
# Shared data generation
# ============================================================================
def make_data(n_samples=400):
    """
    Generate a simple 2D binary classification dataset.
    """
    n_per_class = n_samples // 2
    X0 = np.random.randn(n_per_class, 2) + np.array([-1.0, -1.0])
    X1 = np.random.randn(n_per_class, 2) + np.array([1.0, 1.0])
    X = np.vstack([X0, X1])
    y = np.hstack([np.zeros(n_per_class), np.ones(n_per_class)])
    return X, y


# ============================================================================
# Evaluation and plotting
# ============================================================================
def accuracy(features, labels, weights):
    probs = logistic_predictions(features, weights)
    preds = (probs >= 0.5).astype(int)
    return np.mean(preds == labels)


def plot_loss_curves(loss_before, loss_after, output_path="phase95_code_quality.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(loss_before, label="BEFORE (buggy)", color="crimson")
    ax.plot(loss_after, label="AFTER (clean)", color="seagreen")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Binary Cross-Entropy Loss")
    ax.set_title("Phase 95: Code Quality Impact on Training")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path)
    print(f"Saved plot to {output_path}")


def main():
    X, y = make_data(n_samples=400)

    # BEFORE: train with buggy code
    w_before = run_exp_b(X, y, lr=0.1, iters=100)
    # Compute loss trajectory for buggy code manually
    w_tmp = np.zeros(X.shape[1])
    loss_before = []
    for _ in range(100):
        p = 1 / (1 + np.exp(-X @ w_tmp))
        eps = 1e-9
        loss = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
        loss_before.append(loss)
        g = X.T @ (p - y) / len(y)
        w_tmp = w_tmp + 0.1 * g  # BUG re-enacted for trajectory

    # AFTER: train with clean code
    w_after, loss_after = train_logistic_regression(
        X, y, learning_rate=0.1, n_iterations=100
    )

    acc_before = accuracy(X, y, w_before)
    acc_after = accuracy(X, y, w_after)

    print("=== BEFORE (Poor Code) ===")
    print(f"Final accuracy: {acc_before:.4f}")
    print("Note: The bug (gradient ascent instead of descent) causes divergence or poor fit.")

    print("\n=== AFTER (Clean Code) ===")
    print(f"Final accuracy: {acc_after:.4f}")
    print("Note: Clear structure and docstrings make the algorithm verifiable and correct.")

    plot_loss_curves(loss_before, loss_after, output_path="phase95_code_quality.png")

    print("\nKey takeaway:")
    print("Modular functions, descriptive names, and docstrings reduce cognitive load")
    print("and make bugs obvious during code review.")


if __name__ == "__main__":
    main()

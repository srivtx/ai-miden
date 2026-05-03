"""
Phase 92: Benchmark Design & Evaluation Science
NumPy demo of a toy benchmark, contamination, and metric computation.
No PyTorch. Uses matplotlib Agg backend.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(7)


def generate_toy_dataset(n_samples=500, n_features=10):
    """
    Create a synthetic binary classification dataset.
    The true decision boundary is a simple linear function.
    """
    X = np.random.randn(n_samples, n_features)
    # True weights: only first 3 features matter
    true_w = np.array([2.0, -1.5, 0.5] + [0.0] * (n_features - 3))
    logits = X @ true_w
    probs = 1.0 / (1.0 + np.exp(-logits))
    y = (probs >= 0.5).astype(int)
    return X, y, true_w


def contaminate_train(X_train, y_train, X_test, y_test, fraction=0.3):
    """
    Simulate data contamination by copying a fraction of the test set
    into the training set. This mirrors real-world leakage.
    """
    n_test = len(X_test)
    n_copy = int(n_test * fraction)
    indices = np.random.choice(n_test, size=n_copy, replace=False)
    X_copied = X_test[indices]
    y_copied = y_test[indices]
    X_contaminated = np.vstack([X_train, X_copied])
    y_contaminated = np.hstack([y_train, y_copied])
    return X_contaminated, y_contaminated


def train_simple_model(X, y, lr=0.05, epochs=100):
    """
    Train a logistic regression classifier with gradient descent.
    Returns trained weights and bias.
    """
    n_features = X.shape[1]
    W = np.random.randn(n_features) * 0.01
    b = 0.0
    for _ in range(epochs):
        logits = X @ W + b
        preds = 1.0 / (1.0 + np.exp(-logits))
        dlogits = preds - y
        dW = X.T @ dlogits / len(y)
        db = np.mean(dlogits)
        W -= lr * dW
        b -= lr * db
    return W, b


def evaluate(X, y, W, b):
    """
    Compute accuracy and F1 score for binary classification.
    """
    logits = X @ W + b
    probs = 1.0 / (1.0 + np.exp(-logits))
    preds = (probs >= 0.5).astype(int)

    tp = np.sum((preds == 1) & (y == 1))
    fp = np.sum((preds == 1) & (y == 0))
    fn = np.sum((preds == 0) & (y == 1))

    accuracy = np.mean(preds == y)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return accuracy, f1


def plot_comparison(clean_scores, contaminated_scores, output_path="phase92_comparison.png"):
    """
    Bar plot comparing clean vs contaminated evaluation metrics.
    """
    labels = ["Accuracy", "F1"]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - width / 2, clean_scores, width, label="Clean", color="steelblue")
    ax.bar(x + width / 2, contaminated_scores, width, label="Contaminated", color="coral")
    ax.set_ylabel("Score")
    ax.set_title("Phase 92: Clean vs Contaminated Benchmark")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_path)
    print(f"Saved comparison plot to {output_path}")


def main():
    # Generate full dataset
    X, y, true_w = generate_toy_dataset(n_samples=600, n_features=10)

    # Split into train and test
    split = 400
    X_train, y_train = X[:split], y[:split]
    X_test, y_test = X[split:], y[split:]

    # Clean scenario
    W_clean, b_clean = train_simple_model(X_train, y_train, lr=0.05, epochs=150)
    acc_clean, f1_clean = evaluate(X_test, y_test, W_clean, b_clean)

    # Contaminated scenario: leak 30% of test into train
    X_bad, y_bad = contaminate_train(X_train, y_train, X_test, y_test, fraction=0.3)
    W_bad, b_bad = train_simple_model(X_bad, y_bad, lr=0.05, epochs=150)
    acc_bad, f1_bad = evaluate(X_test, y_test, W_bad, b_bad)

    print("=== Toy Benchmark Results ===")
    print(f"Clean evaluation:      accuracy={acc_clean:.4f}, f1={f1_clean:.4f}")
    print(f"Contaminated evaluation: accuracy={acc_bad:.4f}, f1={f1_bad:.4f}")

    # Show that the contaminated model is over-confident on leaked examples
    plot_comparison(
        clean_scores=[acc_clean, f1_clean],
        contaminated_scores=[acc_bad, f1_bad],
        output_path="phase92_comparison.png",
    )

    # Validity note
    print("\nValidity check: If this benchmark only used the first 3 features,")
    print("it would have high validity because the true signal lives there.")
    print("Adding 7 noise features without regularization lowers validity slightly.")


if __name__ == "__main__":
    main()

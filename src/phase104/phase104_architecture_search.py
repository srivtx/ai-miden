"""
Phase 104: Architecture Search & Inductive Bias Design
NumPy demo comparing a "custom" architecture (locally connected layer)
vs fully connected on a structured task.
Show how inductive bias improves sample efficiency.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

np.random.seed(104)


def generate_grid_data(n_samples, grid_size=8):
    """
    Generate synthetic spatial data: a target pattern (cross) on a grid.
    Label is 1 if cross is present, 0 otherwise.
    """
    X = np.random.randn(n_samples, grid_size * grid_size)
    y = np.zeros(n_samples)
    for i in range(n_samples):
        if np.random.rand() > 0.5:
            # Inject a cross pattern
            center = grid_size // 2
            idx = i
            X[idx].reshape(grid_size, grid_size)[center, :] += 3.0
            X[idx].reshape(grid_size, grid_size)[:, center] += 3.0
            y[idx] = 1.0
    return X, y


def fully_connected_forward(X, W, b):
    """Simple linear layer."""
    return X @ W + b


def locally_connected_forward(X, grid_size, W_local, b_local):
    """
    A locally connected layer: each spatial position has its own filter
    applied to a small neighborhood, preserving spatial structure.
    Here we use a simple 3x3 neighborhood sum as a proxy.
    """
    n_samples = X.shape[0]
    out = np.zeros((n_samples, grid_size * grid_size))
    for i in range(n_samples):
        img = X[i].reshape(grid_size, grid_size)
        # 3x3 local sum with zero padding
        padded = np.pad(img, 1, mode="constant")
        for r in range(grid_size):
            for c in range(grid_size):
                patch = padded[r:r+3, c:c+3]
                out[i, r * grid_size + c] = np.sum(patch * W_local) + b_local
    return out


def train_simple_model(X_train, y_train, X_val, y_val, hidden_dim=32, lr=0.01, epochs=200):
    """Train a tiny 2-layer MLP with NumPy."""
    n_features = X_train.shape[1]
    W1 = np.random.randn(n_features, hidden_dim) * 0.01
    b1 = np.zeros(hidden_dim)
    W2 = np.random.randn(hidden_dim, 1) * 0.01
    b2 = np.zeros(1)

    train_losses = []
    val_accs = []

    for _ in range(epochs):
        # Forward
        h = np.maximum(0, X_train @ W1 + b1)  # ReLU
        logits = h @ W2 + b2
        preds = 1 / (1 + np.exp(-logits))

        # Loss (binary cross-entropy)
        loss = -np.mean(y_train * np.log(preds + 1e-8) + (1 - y_train) * np.log(1 - preds + 1e-8))
        train_losses.append(loss)

        # Backward
        d_logits = preds.squeeze() - y_train
        dW2 = h.T @ d_logits.reshape(-1, 1) / len(y_train)
        db2 = np.mean(d_logits)
        dh = d_logits.reshape(-1, 1) @ W2.T
        dh[h <= 0] = 0
        dW1 = X_train.T @ dh / len(y_train)
        db1 = np.mean(dh, axis=0)

        # Update
        W1 -= lr * dW1
        b1 -= lr * db1
        W2 -= lr * dW2
        b2 -= lr * db2

        # Validation accuracy
        h_val = np.maximum(0, X_val @ W1 + b1)
        logits_val = h_val @ W2 + b2
        preds_val = (1 / (1 + np.exp(-logits_val))) > 0.5
        val_acc = np.mean(preds_val.squeeze() == y_val)
        val_accs.append(val_acc)

    return train_losses, val_accs


def simulate_architecture_search(output_dir="."):
    grid_size = 8
    n_train_list = [50, 100, 200, 400, 800]
    n_val = 200
    X_val, y_val = generate_grid_data(n_val, grid_size)

    fc_accs = []
    lc_accs = []

    for n_train in n_train_list:
        X_train, y_train = generate_grid_data(n_train, grid_size)

        # --- Fully Connected ---
        loss_fc, acc_fc = train_simple_model(X_train, y_train, X_val, y_val, epochs=300)
        fc_accs.append(acc_fc[-1])

        # --- Locally Connected preprocessing + FC ---
        W_local = np.ones((3, 3))
        b_local = 0.0
        X_train_lc = locally_connected_forward(X_train, grid_size, W_local, b_local)
        X_val_lc = locally_connected_forward(X_val, grid_size, W_local, b_local)
        loss_lc, acc_lc = train_simple_model(X_train_lc, y_train, X_val_lc, y_val, hidden_dim=32, epochs=300)
        lc_accs.append(acc_lc[-1])

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot(n_train_list, fc_accs, marker="o", label="Fully Connected")
    ax.plot(n_train_list, lc_accs, marker="s", label="Locally Connected")
    ax.set_title("Sample Efficiency: FC vs Local")
    ax.set_xlabel("Training samples")
    ax.set_ylabel("Validation accuracy")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    # Simulate scaling law
    ax = axes[1]
    params = np.array([1e5, 5e5, 1e6, 5e6, 1e7])
    compute = params * 1e3
    loss = 2.5 * (compute ** -0.05) + 0.5  # synthetic power law
    ax.loglog(compute, loss, marker="o")
    ax.set_title("Synthetic Scaling Law")
    ax.set_xlabel("Compute (arbitrary units)")
    ax.set_ylabel("Loss")
    ax.grid(True, linestyle="--", alpha=0.5, which="both")

    plt.tight_layout()
    out_path = os.path.join(output_dir, "phase104_architecture_search.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot to {out_path}")

    for n, fc, lc in zip(n_train_list, fc_accs, lc_accs):
        print(f"  n={n:4d}: FC={fc:.2%}, Local={lc:.2%}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    simulate_architecture_search(output_dir=script_dir)

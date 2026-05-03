"""
Phase 105: Tiny ML & Edge Deployment
NumPy simulation of knowledge distillation.
A large "teacher" model's soft targets train a small "student."
Compare student trained on hard vs soft labels.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

np.random.seed(105)


def softmax(logits, temperature=1.0):
    """Softmax with temperature scaling."""
    exps = np.exp((logits - np.max(logits, axis=1, keepdims=True)) / temperature)
    return exps / np.sum(exps, axis=1, keepdims=True)


def generate_data(n_samples, true_W, n_features=20, n_classes=5):
    """Generate synthetic classification data."""
    X = np.random.randn(n_samples, n_features)
    logits = X @ true_W + np.random.normal(0, 1.0, size=(n_samples, n_classes))
    y = np.argmax(logits, axis=1)
    return X, y


def train_mlp(X, y, n_classes, hidden_dim, epochs, lr):
    """Train a 2-layer MLP with NumPy. Returns a predict function and the output probabilities on X."""
    n_features = X.shape[1]
    W1 = np.random.randn(n_features, hidden_dim) * 0.1
    b1 = np.zeros(hidden_dim)
    W2 = np.random.randn(hidden_dim, n_classes) * 0.1
    b2 = np.zeros(n_classes)
    one_hot = np.zeros((len(y), n_classes))
    one_hot[np.arange(len(y)), y] = 1.0

    for _ in range(epochs):
        h = np.maximum(0, X @ W1 + b1)
        logits = h @ W2 + b2
        probs = softmax(logits, temperature=1.0)

        d_logits = (probs - one_hot) / len(y)
        dW2 = h.T @ d_logits
        db2 = np.sum(d_logits, axis=0)
        dh = d_logits @ W2.T
        dh[h <= 0] = 0
        dW1 = X.T @ dh
        db1 = np.sum(dh, axis=0)

        W1 -= lr * dW1
        b1 -= lr * db1
        W2 -= lr * dW2
        b2 -= lr * db2

    def predict(X_):
        h = np.maximum(0, X_ @ W1 + b1)
        logits = h @ W2 + b2
        return np.argmax(logits, axis=1), logits

    return predict


def train_student(X_train, y_train, teacher_logits, n_classes=5, hidden_dim=8, epochs=400, lr=0.05, use_soft=False, temperature=4.0, alpha=0.7):
    """Train a small 2-layer student."""
    n_features = X_train.shape[1]
    W1 = np.random.randn(n_features, hidden_dim) * 0.1
    b1 = np.zeros(hidden_dim)
    W2 = np.random.randn(hidden_dim, n_classes) * 0.1
    b2 = np.zeros(n_classes)

    losses = []
    one_hot = np.zeros((len(y_train), n_classes))
    one_hot[np.arange(len(y_train)), y_train] = 1.0

    for _ in range(epochs):
        h = np.maximum(0, X_train @ W1 + b1)
        logits = h @ W2 + b2
        probs = softmax(logits, temperature=1.0)

        # Hard label cross-entropy
        loss_hard = -np.mean(np.sum(one_hot * np.log(probs + 1e-8), axis=1))

        if use_soft:
            # Distillation cross-entropy at temperature
            teacher_soft = softmax(teacher_logits, temperature=temperature)
            student_soft = softmax(logits, temperature=temperature)
            loss_soft = -np.mean(np.sum(teacher_soft * np.log(student_soft + 1e-8), axis=1))
            loss = alpha * loss_soft + (1 - alpha) * loss_hard
        else:
            loss = loss_hard

        losses.append(loss)

        # Backprop
        if use_soft:
            # Gradient of soft CE w.r.t. student logits at temperature T is (q - p) / T
            d_logits_soft = (student_soft - teacher_soft) / temperature
            d_logits_hard = (probs - one_hot)
            d_logits = alpha * d_logits_soft + (1 - alpha) * d_logits_hard
        else:
            d_logits = (probs - one_hot)

        dW2 = h.T @ d_logits / len(y_train)
        db2 = np.mean(d_logits, axis=0)
        dh = d_logits @ W2.T
        dh[h <= 0] = 0
        dW1 = X_train.T @ dh / len(y_train)
        db1 = np.sum(dh, axis=0)

        W1 -= lr * dW1
        b1 -= lr * db1
        W2 -= lr * dW2
        b2 -= lr * db2

    def predict(X):
        h = np.maximum(0, X @ W1 + b1)
        logits = h @ W2 + b2
        return np.argmax(logits, axis=1)

    return predict, losses


def simulate_tiny_ml(output_dir="."):
    n_train = 800
    n_val = 200
    n_features = 20
    n_classes = 5

    true_W = np.random.randn(n_features, n_classes)
    X_train, y_train = generate_data(n_train, true_W, n_features, n_classes)
    X_val, y_val = generate_data(n_val, true_W, n_features, n_classes)

    # Train a large teacher model
    teacher_predict = train_mlp(X_train, y_train, n_classes, hidden_dim=128, epochs=500, lr=0.1)
    _, teacher_logits = teacher_predict(X_train)

    # Train student on hard labels
    pred_hard, loss_hard = train_student(X_train, y_train, teacher_logits, n_classes=n_classes, hidden_dim=8, use_soft=False)
    acc_hard = np.mean(pred_hard(X_val) == y_val)

    # Train student on soft labels (distillation)
    pred_soft, loss_soft = train_student(X_train, y_train, teacher_logits, n_classes=n_classes, hidden_dim=8, use_soft=True, temperature=4.0, alpha=0.7)
    acc_soft = np.mean(pred_soft(X_val) == y_val)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot(loss_hard, label="Hard labels", alpha=0.8)
    ax.plot(loss_soft, label="Soft labels (distillation)", alpha=0.8)
    ax.set_title("Training Loss: Hard vs Soft Labels")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    ax = axes[1]
    methods = ["Hard labels", "Soft labels"]
    accs = [acc_hard, acc_soft]
    colors = ["gray", "blue"]
    ax.bar(methods, accs, color=colors, alpha=0.7)
    ax.set_ylim(0, 1.1)
    ax.set_title("Validation Accuracy")
    ax.set_ylabel("Accuracy")
    for i, v in enumerate(accs):
        ax.text(i, v + 0.02, f"{v:.2%}", ha="center")
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    plt.tight_layout()
    out_path = os.path.join(output_dir, "phase105_tiny_ml.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot to {out_path}")

    teacher_train_preds, _ = teacher_predict(X_train)
    teacher_train_acc = np.mean(teacher_train_preds == y_train)
    teacher_val_preds, _ = teacher_predict(X_val)
    teacher_val_acc = np.mean(teacher_val_preds == y_val)
    print(f"\nResults:")
    print(f"  Student (hard labels):   {acc_hard:.2%}")
    print(f"  Student (soft labels):   {acc_soft:.2%}")
    print(f"  Teacher (train accuracy): {teacher_train_acc:.2%}")
    print(f"  Teacher (val accuracy):   {teacher_val_acc:.2%}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    simulate_tiny_ml(output_dir=script_dir)

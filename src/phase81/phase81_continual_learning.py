"""
Phase 81: Continual Learning - NumPy Concept Demo
=================================================
This script demonstrates catastrophic forgetting and two solutions (EWC, Replay)
using a simple 2-layer MLP trained with NumPy only on synthetic 2D data.

Why NumPy? To make every gradient, every weight update, and every decision
completely transparent. No black-box frameworks.
"""

import numpy as np

# MUST set Agg backend before importing pyplot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# =============================================================================
# 1. DATA GENERATION: Two binary classification tasks in 2D
# =============================================================================

def make_task_a(n=500):
    """
    Task A: Circles (class 0) vs Squares (class 1).
    Circles cluster near (0, 0). Squares cluster near (2, 2).
    We make them slightly overlapping to be realistic.
    """
    np.random.seed(0)
    # Class 0: circles (cluster around origin)
    X0 = np.random.randn(n // 2, 2) * 0.6 + np.array([0.0, 0.0])
    y0 = np.zeros((n // 2, 1))
    # Class 1: squares (cluster around (2,2))
    X1 = np.random.randn(n // 2, 2) * 0.6 + np.array([2.0, 2.0])
    y1 = np.ones((n // 2, 1))
    X = np.vstack([X0, X1])
    y = np.vstack([y0, y1])
    # Shuffle
    idx = np.random.permutation(n)
    return X[idx], y[idx]


def make_task_b(n=500):
    """
    Task B: Triangles (class 0) vs Stars (class 1).
    Triangles cluster near (0, 2). Stars cluster near (2, 0).
    """
    np.random.seed(1)
    # Class 0: triangles
    X0 = np.random.randn(n // 2, 2) * 0.6 + np.array([0.0, 2.0])
    y0 = np.zeros((n // 2, 1))
    # Class 1: stars
    X1 = np.random.randn(n // 2, 2) * 0.6 + np.array([2.0, 0.0])
    y1 = np.ones((n // 2, 1))
    X = np.vstack([X0, X1])
    y = np.vstack([y0, y1])
    idx = np.random.permutation(n)
    return X[idx], y[idx]


# =============================================================================
# 2. MODEL: Simple 2-layer MLP (input 2 -> hidden 32 -> output 1)
# =============================================================================

class TwoLayerMLP:
    def __init__(self, input_dim=2, hidden_dim=32, seed=42):
        np.random.seed(seed)
        # Xavier-ish init
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, 1) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros((1, 1))
        # Cache for activations (needed for Fisher)
        self.z1 = None
        self.a1 = None
        self.z2 = None
        self.a2 = None

    def forward(self, X, store=True):
        """Forward pass. Returns probabilities."""
        z1 = X @ self.W1 + self.b1
        a1 = np.maximum(z1, 0)  # ReLU
        z2 = a1 @ self.W2 + self.b2
        a2 = 1.0 / (1.0 + np.exp(-z2))  # Sigmoid
        if store:
            self.z1 = z1
            self.a1 = a1
            self.z2 = z2
            self.a2 = a2
        return a2

    def backward(self, X, y, probs):
        """Backward pass. Returns gradients."""
        m = X.shape[0]
        # Output gradient (binary cross-entropy derivative)
        dz2 = (probs - y) / m
        dW2 = self.a1.T @ dz2
        db2 = np.sum(dz2, axis=0, keepdims=True)
        da1 = dz2 @ self.W2.T
        dz1 = da1 * (self.z1 > 0).astype(float)  # ReLU derivative
        dW1 = X.T @ dz1
        db1 = np.sum(dz1, axis=0, keepdims=True)
        return {'W1': dW1, 'b1': db1, 'W2': dW2, 'b2': db2}

    def get_params(self):
        return {'W1': self.W1, 'b1': self.b1, 'W2': self.W2, 'b2': self.b2}

    def set_params(self, params):
        self.W1 = params['W1'].copy()
        self.b1 = params['b1'].copy()
        self.W2 = params['W2'].copy()
        self.b2 = params['b2'].copy()

    def apply_gradients(self, grads, lr=0.01):
        self.W1 -= lr * grads['W1']
        self.b1 -= lr * grads['b1']
        self.W2 -= lr * grads['W2']
        self.b2 -= lr * grads['b2']

    def copy(self):
        m = TwoLayerMLP(input_dim=self.W1.shape[0], hidden_dim=self.W1.shape[1], seed=0)
        m.set_params(self.get_params())
        return m


# =============================================================================
# 3. TRAINING UTILITIES
# =============================================================================

def accuracy(model, X, y):
    probs = model.forward(X, store=False)
    preds = (probs > 0.5).astype(float)
    return np.mean(preds == y)


def train_epoch(model, X, y, lr=0.05, batch_size=32):
    """Standard SGD for one epoch."""
    m = X.shape[0]
    indices = np.random.permutation(m)
    for i in range(0, m, batch_size):
        idx = indices[i:i + batch_size]
        Xb, yb = X[idx], y[idx]
        probs = model.forward(Xb, store=True)
        grads = model.backward(Xb, yb, probs)
        model.apply_gradients(grads, lr=lr)


def train_task(model, X, y, epochs=50, lr=0.05, batch_size=32):
    """Train model on a task for N epochs. Returns accuracy history."""
    hist = []
    for _ in range(epochs):
        train_epoch(model, X, y, lr=lr, batch_size=batch_size)
        hist.append(accuracy(model, X, y))
    return hist


# =============================================================================
# 4. EWC: ELASTIC WEIGHT CONSOLIDATION
# =============================================================================

def compute_fisher(model, X, y, num_samples=200):
    """
    Compute diagonal Fisher information F_i = E[(dL/dw_i)^2] over data.
    We approximate the expectation by averaging squared gradients over
    a subset of the task data.
    
    WHY squared gradients? Because the Fisher information matrix approximates
    the curvature of the loss landscape around the optimum. Large squared
    gradient = weight is very sensitive / important for this task.
    """
    fisher = {'W1': np.zeros_like(model.W1),
              'b1': np.zeros_like(model.b1),
              'W2': np.zeros_like(model.W2),
              'b2': np.zeros_like(model.b2)}
    n = min(num_samples, X.shape[0])
    idx = np.random.choice(X.shape[0], size=n, replace=False)
    for i in idx:
        Xi = X[i:i + 1]
        yi = y[i:i + 1]
        probs = model.forward(Xi, store=True)
        grads = model.backward(Xi, yi, probs)
        for k in fisher:
            fisher[k] += grads[k] ** 2
    for k in fisher:
        fisher[k] /= n
    return fisher


def ewc_loss_extra(model, old_params, fisher, lam=1000.0):
    """
    Compute the EWC penalty term:
        (lambda / 2) * sum_i F_i * (w_i - w_i*)^2
    We return the gradient of this penalty w.r.t. each parameter.
    WHY gradients? So we can add them to the task loss gradient during backprop.
    """
    penalty_grads = {}
    for k in old_params:
        diff = model.get_params()[k] - old_params[k]
        # Gradient of penalty w.r.t w is: lambda * F * (w - w*)
        penalty_grads[k] = lam * fisher[k] * diff
    return penalty_grads


def train_epoch_ewc(model, X, y, old_params, fisher, lr=0.05, batch_size=32, lam=1000.0):
    """One epoch of SGD with EWC penalty."""
    m = X.shape[0]
    indices = np.random.permutation(m)
    for i in range(0, m, batch_size):
        idx = indices[i:i + batch_size]
        Xb, yb = X[idx], y[idx]
        probs = model.forward(Xb, store=True)
        grads = model.backward(Xb, yb, probs)
        # Add EWC penalty gradient
        ewc_grads = ewc_loss_extra(model, old_params, fisher, lam=lam)
        for k in grads:
            grads[k] += ewc_grads[k]
        model.apply_gradients(grads, lr=lr)


def train_task_ewc(model, X, y, old_params, fisher, epochs=50, lr=0.05, batch_size=32, lam=1000.0):
    hist = []
    for _ in range(epochs):
        train_epoch_ewc(model, X, y, old_params, fisher, lr=lr, batch_size=batch_size, lam=lam)
        hist.append(accuracy(model, X, y))
    return hist


# =============================================================================
# 5. REPLAY BUFFER
# =============================================================================

def train_epoch_replay(model, X_new, y_new, X_old, y_old, lr=0.05, batch_size=32, replay_ratio=0.25):
    """
    One epoch where each minibatch is a mix of new task data and replay data.
    replay_ratio = fraction of batch that comes from old data.
    WHY mix? Because the model sees both tasks simultaneously, so gradients
    point in a direction that improves both instead of overwriting A with B.
    """
    m_new = X_new.shape[0]
    m_old = X_old.shape[0]
    indices_new = np.random.permutation(m_new)
    # We iterate over the new data. For each batch, we grab some replay.
    for i in range(0, m_new, batch_size):
        idx_new = indices_new[i:i + batch_size]
        Xb_new, yb_new = X_new[idx_new], y_new[idx_new]
        # Determine how many replay samples to add
        replay_count = int(len(idx_new) * replay_ratio)
        if m_old > 0 and replay_count > 0:
            idx_old = np.random.choice(m_old, size=replay_count, replace=True)
            Xb_old, yb_old = X_old[idx_old], y_old[idx_old]
            Xb = np.vstack([Xb_new, Xb_old])
            yb = np.vstack([yb_new, yb_old])
        else:
            Xb, yb = Xb_new, yb_new
        probs = model.forward(Xb, store=True)
        grads = model.backward(Xb, yb, probs)
        model.apply_gradients(grads, lr=lr)


def train_task_replay(model, X_new, y_new, X_old, y_old, epochs=50, lr=0.05, batch_size=32, replay_ratio=0.25):
    hist = []
    for _ in range(epochs):
        train_epoch_replay(model, X_new, y_new, X_old, y_old, lr=lr, batch_size=batch_size, replay_ratio=replay_ratio)
        hist.append(accuracy(model, X_new, y_new))
    return hist


# =============================================================================
# 6. VISUALIZATION
# =============================================================================

def plot_decision_boundary(ax, model, X, y, title, xlim=(-2, 4), ylim=(-2, 4)):
    """Plot 2D decision boundary."""
    xx, yy = np.meshgrid(np.linspace(xlim[0], xlim[1], 200),
                         np.linspace(ylim[0], ylim[1], 200))
    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = model.forward(grid, store=False).reshape(xx.shape)
    ax.contourf(xx, yy, Z, levels=50, cmap='RdBu', alpha=0.6, vmin=0, vmax=1)
    ax.scatter(X[y[:, 0] == 0, 0], X[y[:, 0] == 0, 1], c='blue', edgecolors='k', s=30, label='Class 0')
    ax.scatter(X[y[:, 0] == 1, 0], X[y[:, 0] == 1, 1], c='red', edgecolors='k', s=30, label='Class 1')
    ax.set_title(title, fontsize=10)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.legend(fontsize=7)


# =============================================================================
# 7. MAIN EXPERIMENT
# =============================================================================

def run_experiment():
    print("=" * 70)
    print("PHASE 81: CONTINUAL LEARNING - NUMPY CONCEPT DEMO")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # Prepare data
    # -------------------------------------------------------------------------
    X_a, y_a = make_task_a(n=500)
    X_b, y_b = make_task_b(n=500)

    # Test sets (hold-out)
    np.random.seed(99)
    split_a = int(0.8 * len(X_a))
    split_b = int(0.8 * len(X_b))
    X_a_train, y_a_train = X_a[:split_a], y_a[:split_a]
    X_a_test, y_a_test = X_a[split_a:], y_a[split_a:]
    X_b_train, y_b_train = X_b[:split_b], y_b[:split_b]
    X_b_test, y_b_test = X_b[split_b:], y_b[split_b:]

    # Replay buffer: small sample from Task A training data
    replay_size = 40
    replay_idx = np.random.choice(len(X_a_train), size=replay_size, replace=False)
    X_replay, y_replay = X_a_train[replay_idx].copy(), y_a_train[replay_idx].copy()

    print(f"\nTask A: {len(X_a_train)} train, {len(X_a_test)} test")
    print(f"Task B: {len(X_b_train)} train, {len(X_b_test)} test")
    print(f"Replay buffer size: {replay_size} examples ({100*replay_size/len(X_a_train):.1f}% of Task A)")

    # -------------------------------------------------------------------------
    # EXPERIMENT 1: NAIVE FINE-TUNING (shows catastrophic forgetting)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("EXPERIMENT 1: NAIVE FINE-TUNING")
    print("-" * 70)
    model_naive = TwoLayerMLP(input_dim=2, hidden_dim=64, seed=42)

    # Phase 1: Train on Task A
    hist_naive_a = train_task(model_naive, X_a_train, y_a_train, epochs=60, lr=0.1, batch_size=32)
    acc_a_after = accuracy(model_naive, X_a_test, y_a_test)
    print(f"After Task A training: Task A test accuracy = {acc_a_after:.3f}")

    # Phase 2: Train SAME model on Task B (no Task A data)
    hist_naive_b = train_task(model_naive, X_b_train, y_b_train, epochs=60, lr=0.1, batch_size=32)
    acc_a_after_b = accuracy(model_naive, X_a_test, y_a_test)
    acc_b_after_b = accuracy(model_naive, X_b_test, y_b_test)
    print(f"After Task B training: Task A test accuracy = {acc_a_after_b:.3f}  <-- CATASTROPHIC FORGETTING!")
    print(f"After Task B training: Task B test accuracy = {acc_b_after_b:.3f}")

    # -------------------------------------------------------------------------
    # EXPERIMENT 2: EWC
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("EXPERIMENT 2: ELASTIC WEIGHT CONSOLIDATION (EWC)")
    print("-" * 70)
    model_ewc = TwoLayerMLP(input_dim=2, hidden_dim=64, seed=42)

    # Phase 1: Train on Task A
    hist_ewc_a = train_task(model_ewc, X_a_train, y_a_train, epochs=60, lr=0.1, batch_size=32)
    acc_a_after_ewc = accuracy(model_ewc, X_a_test, y_a_test)
    print(f"After Task A training: Task A test accuracy = {acc_a_after_ewc:.3f}")

    # Save old params and compute Fisher
    old_params_ewc = model_ewc.get_params()
    fisher_ewc = compute_fisher(model_ewc, X_a_train, y_a_train, num_samples=400)
    print(f"Fisher info computed (mean over all weights: {np.mean([np.mean(v) for v in fisher_ewc.values()]):.6f})")

    # Phase 2: Train on Task B with EWC penalty
    hist_ewc_b = train_task_ewc(model_ewc, X_b_train, y_b_train, old_params_ewc, fisher_ewc,
                                 epochs=60, lr=0.02, batch_size=32, lam=10000.0)
    acc_a_after_b_ewc = accuracy(model_ewc, X_a_test, y_a_test)
    acc_b_after_b_ewc = accuracy(model_ewc, X_b_test, y_b_test)
    print(f"After Task B + EWC:    Task A test accuracy = {acc_a_after_b_ewc:.3f}")
    print(f"After Task B + EWC:    Task B test accuracy = {acc_b_after_b_ewc:.3f}")

    # -------------------------------------------------------------------------
    # EXPERIMENT 3: REPLAY BUFFER
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("EXPERIMENT 3: REPLAY BUFFER")
    print("-" * 70)
    model_replay = TwoLayerMLP(input_dim=2, hidden_dim=64, seed=42)

    # Phase 1: Train on Task A
    hist_replay_a = train_task(model_replay, X_a_train, y_a_train, epochs=60, lr=0.1, batch_size=32)
    acc_a_after_replay = accuracy(model_replay, X_a_test, y_a_test)
    print(f"After Task A training: Task A test accuracy = {acc_a_after_replay:.3f}")

    # Phase 2: Train on Task B with replay
    hist_replay_b = train_task_replay(model_replay, X_b_train, y_b_train, X_replay, y_replay,
                                       epochs=60, lr=0.1, batch_size=32, replay_ratio=0.25)
    acc_a_after_b_replay = accuracy(model_replay, X_a_test, y_a_test)
    acc_b_after_b_replay = accuracy(model_replay, X_b_test, y_b_test)
    print(f"After Task B + Replay: Task A test accuracy = {acc_a_after_b_replay:.3f}")
    print(f"After Task B + Replay: Task B test accuracy = {acc_b_after_b_replay:.3f}")

    # -------------------------------------------------------------------------
    # SUMMARY TABLE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY: Test Accuracy on Both Tasks After Task B Training")
    print("=" * 70)
    print(f"{'Method':<20} {'Task A':>10} {'Task B':>10}")
    print("-" * 42)
    print(f"{'Naive':<20} {acc_a_after_b:>10.3f} {acc_b_after_b:>10.3f}")
    print(f"{'EWC (lam=10000)':<20} {acc_a_after_b_ewc:>10.3f} {acc_b_after_b_ewc:>10.3f}")
    print(f"{'Replay (25%)':<20} {acc_a_after_b_replay:>10.3f} {acc_b_after_b_replay:>10.3f}")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # VISUALIZATION
    # -------------------------------------------------------------------------
    fig = plt.figure(figsize=(16, 12))

    # Row 1: Decision boundaries for each method on Task A
    ax1 = fig.add_subplot(3, 3, 1)
    # We need to re-instantiate because we only have final models
    # For naive, after B training it's forgotten. Let's create a fresh one for "Task A only" ref.
    model_ref = TwoLayerMLP(input_dim=2, hidden_dim=64, seed=42)
    train_task(model_ref, X_a_train, y_a_train, epochs=60, lr=0.1, batch_size=32)
    plot_decision_boundary(ax1, model_ref, X_a_test, y_a_test, "Task A Only (Reference)")

    ax2 = fig.add_subplot(3, 3, 2)
    plot_decision_boundary(ax2, model_naive, X_a_test, y_a_test, "Naive after Task B (Forgotten)")

    ax3 = fig.add_subplot(3, 3, 3)
    plot_decision_boundary(ax3, model_ewc, X_a_test, y_a_test, "EWC after Task B (Preserved)")

    # Row 2: Decision boundaries on Task B
    ax4 = fig.add_subplot(3, 3, 4)
    plot_decision_boundary(ax4, model_ref, X_b_test, y_b_test, "Task A Model on Task B (Untrained)")

    ax5 = fig.add_subplot(3, 3, 5)
    plot_decision_boundary(ax5, model_naive, X_b_test, y_b_test, "Naive after Task B")

    ax6 = fig.add_subplot(3, 3, 6)
    plot_decision_boundary(ax6, model_ewc, X_b_test, y_b_test, "EWC after Task B")

    # Row 3: Accuracy curves and weight changes
    ax7 = fig.add_subplot(3, 3, 7)
    ax7.plot(hist_naive_a + [np.nan] * len(hist_naive_b), 'b-', label='Naive Task A', alpha=0.7)
    ax7.plot([np.nan] * len(hist_naive_a) + hist_naive_b, 'r-', label='Naive Task B', alpha=0.7)
    ax7.axvline(x=len(hist_naive_a), color='k', linestyle='--', alpha=0.5)
    ax7.set_title("Naive: Accuracy Collapse on Task A")
    ax7.set_xlabel("Epoch")
    ax7.set_ylabel("Train Accuracy")
    ax7.set_ylim(0, 1.05)
    ax7.legend(fontsize=7)

    ax8 = fig.add_subplot(3, 3, 8)
    ax8.plot(hist_ewc_a + [np.nan] * len(hist_ewc_b), 'b-', label='EWC Task A', alpha=0.7)
    ax8.plot([np.nan] * len(hist_ewc_a) + hist_ewc_b, 'r-', label='EWC Task B', alpha=0.7)
    ax8.axvline(x=len(hist_ewc_a), color='k', linestyle='--', alpha=0.5)
    ax8.set_title("EWC: Preserves Task A Accuracy")
    ax8.set_xlabel("Epoch")
    ax8.set_ylabel("Train Accuracy")
    ax8.set_ylim(0, 1.05)
    ax8.legend(fontsize=7)

    ax9 = fig.add_subplot(3, 3, 9)
    ax9.plot(hist_replay_a + [np.nan] * len(hist_replay_b), 'b-', label='Replay Task A', alpha=0.7)
    ax9.plot([np.nan] * len(hist_replay_a) + hist_replay_b, 'r-', label='Replay Task B', alpha=0.7)
    ax9.axvline(x=len(hist_replay_a), color='k', linestyle='--', alpha=0.5)
    ax9.set_title("Replay: Maintains Both Tasks")
    ax9.set_xlabel("Epoch")
    ax9.set_ylabel("Train Accuracy")
    ax9.set_ylim(0, 1.05)
    ax9.legend(fontsize=7)

    plt.tight_layout()
    out_path = "/Users/zen/Desktop/building-ai/ai-miden/src/phase81/continual_learning.png"
    plt.savefig(out_path, dpi=150)
    print(f"\nPlot saved to: {out_path}")

    # Also plot weight change comparison
    fig2, ax = plt.subplots(figsize=(8, 4))
    methods = ['Naive', 'EWC', 'Replay']
    task_a_accs = [acc_a_after_b, acc_a_after_b_ewc, acc_a_after_b_replay]
    task_b_accs = [acc_b_after_b, acc_b_after_b_ewc, acc_b_after_b_replay]
    x = np.arange(len(methods))
    width = 0.35
    bars1 = ax.bar(x - width/2, task_a_accs, width, label='Task A Accuracy', color='steelblue')
    bars2 = ax.bar(x + width/2, task_b_accs, width, label='Task B Accuracy', color='coral')
    ax.set_ylabel('Test Accuracy')
    ax.set_title('Continual Learning: Task A vs Task B Accuracy After Training on Task B')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Random Chance')
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    out_path2 = "/Users/zen/Desktop/building-ai/ai-miden/src/phase81/continual_learning_comparison.png"
    plt.savefig(out_path2, dpi=150)
    print(f"Comparison plot saved to: {out_path2}")


if __name__ == "__main__":
    run_experiment()

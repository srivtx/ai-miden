"""
Phase 80 MLOps & Production Monitoring — NumPy Concept Demo
=============================================================

This script demonstrates the core ideas of production ML monitoring using
only NumPy and Matplotlib. We simulate a model deployed for 12 months and
show two failure modes:

1. DATA DRIFT (month 6):   The joint distribution of inputs changes.
2. CONCEPT DRIFT (month 9): The true relationship between X and y changes.

We track:
- Model accuracy over time
- KL divergence between reference and production feature distributions
- Population Stability Index (PSI)

All plots are saved to src/phase80/mlops.png.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Required for headless / non-interactive environments
import matplotlib.pyplot as plt

np.random.seed(42)

# =============================================================================
# CONFIGURATION
# =============================================================================
N_MONTHS = 12
N_SAMPLES = 1000  # samples per month
BINS = 15         # histogram bins for 2-D drift metrics

# =============================================================================
# STEP 1: Generate synthetic data over 12 months
# =============================================================================
# We use TWO features so that we can create a subtle but damaging drift:
#   - In the reference period X2 is positively correlated with X1.
#   - After month 6 the correlation FLIPS (data drift).
#   - After month 9 the target rule changes (concept drift).
#
# Why two features?  A single-feature shift is easy to see.  A correlation
# shift is invisible to univariate monitoring but wrecks any model that
# learned to rely on that correlation.

months = []
for m in range(1, N_MONTHS + 1):
    X1 = np.random.normal(0.0, 1.0, N_SAMPLES)

    if m <= 5:
        # REFERENCE period (months 1-5)
        # X2 walks with X1 — they are partners.
        X2 = X1 + np.random.normal(0.0, 0.2, N_SAMPLES)
        # Concept: positive sum → class 1
        y = ((X1 + X2) > 0).astype(int)

    elif m <= 8:
        # DATA DRIFT period (months 6-8)
        # The correlation between X1 and X2 has INVERTED.
        # The true concept is still "sum > 0", but because X2 ≈ -X1,
        # the sum is near zero and labels become almost random.
        X2 = -X1 + np.random.normal(0.0, 0.2, N_SAMPLES)
        y = ((X1 + X2) > 0).astype(int)

    else:
        # CONCEPT DRIFT period (months 9-12)
        # The correlation stays inverted, but now the target depends on
        # X1 - X2 instead of X1 + X2.  Since X2 ≈ -X1, the new rule
        # reduces to "X1 > 0", but the old model has no idea.
        X2 = -X1 + np.random.normal(0.0, 0.2, N_SAMPLES)
        y = ((X1 - X2) > 0).astype(int)

    months.append({
        'month': m,
        'X': np.column_stack([X1, X2]),
        'y': y
    })

# =============================================================================
# STEP 2: Train a simple logistic-style linear classifier on months 1-5
# =============================================================================
# We use plain gradient descent (no sklearn) so the demo is self-contained.
# The model learns weights w1, w2 and a bias term.  Because during training
# X2 ≈ X1, the model will learn roughly w1 ≈ w2 > 0.

X_train = np.vstack([months[i]['X'] for i in range(5)])
y_train = np.concatenate([months[i]['y'] for i in range(5)])

# Add bias column
Xb_train = np.hstack([X_train, np.ones((X_train.shape[0], 1))])
w = np.zeros(3)

for epoch in range(600):
    z = Xb_train @ w
    # stable sigmoid
    z = np.clip(z, -500, 500)
    pred = 1.0 / (1.0 + np.exp(-z))
    grad = Xb_train.T @ (pred - y_train) / len(y_train)
    w -= 0.2 * grad


def predict(X: np.ndarray) -> np.ndarray:
    """Return binary predictions using the learned weights."""
    Xb = np.hstack([X, np.ones((X.shape[0], 1))])
    z = np.clip(Xb @ w, -500, 500)
    prob = 1.0 / (1.0 + np.exp(-z))
    return (prob > 0.5).astype(int)


# =============================================================================
# STEP 3: Drift-metric helpers (KL divergence & PSI)
# =============================================================================
# Both metrics compare a REFERENCE histogram to a PRODUCTION histogram.
# We use 2-D histograms because the drift lives in the *joint* distribution
# (the correlation flip), not in either margin alone.

def kl_divergence(ref: np.ndarray, prod: np.ndarray, bins: int = BINS) -> float:
    """KL(P_ref || P_prod) using flattened 2-D histograms."""
    ranges = [
        [min(ref[:, 0].min(), prod[:, 0].min()),
         max(ref[:, 0].max(), prod[:, 0].max())],
        [min(ref[:, 1].min(), prod[:, 1].min()),
         max(ref[:, 1].max(), prod[:, 1].max())],
    ]
    h_ref, _, _ = np.histogram2d(ref[:, 0], ref[:, 1], bins=bins, range=ranges)
    h_prod, _, _ = np.histogram2d(prod[:, 0], prod[:, 1], bins=bins, range=ranges)

    p = (h_ref.flatten() + 1e-10)
    q = (h_prod.flatten() + 1e-10)
    p /= p.sum()
    q /= q.sum()
    return np.sum(p * np.log(p / q))


def psi(ref: np.ndarray, prod: np.ndarray, bins: int = BINS) -> float:
    """Population Stability Index between reference and production."""
    ranges = [
        [min(ref[:, 0].min(), prod[:, 0].min()),
         max(ref[:, 0].max(), prod[:, 0].max())],
        [min(ref[:, 1].min(), prod[:, 1].min()),
         max(ref[:, 1].max(), prod[:, 1].max())],
    ]
    h_ref, _, _ = np.histogram2d(ref[:, 0], ref[:, 1], bins=bins, range=ranges)
    h_prod, _, _ = np.histogram2d(prod[:, 0], prod[:, 1], bins=bins, range=ranges)

    p = (h_ref.flatten() + 1e-10)
    q = (h_prod.flatten() + 1e-10)
    p /= p.sum()
    q /= q.sum()
    return np.sum((q - p) * np.log(q / p))


# =============================================================================
# STEP 4: Evaluate every month
# =============================================================================
ref_X = X_train
month_nums = []
accuracies = []
kl_scores = []
psi_scores = []

print("=" * 60)
print(f"{'Month':>6} | {'Accuracy':>10} | {'KL Div':>10} | {'PSI':>10}")
print("=" * 60)

for md in months:
    m = md['month']
    X = md['X']
    y = md['y']

    y_pred = predict(X)
    acc = float(np.mean(y_pred == y))

    kl = kl_divergence(ref_X, X)
    ps = psi(ref_X, X)

    month_nums.append(m)
    accuracies.append(acc)
    kl_scores.append(kl)
    psi_scores.append(ps)

    print(f"{m:6d} | {acc:10.3f} | {kl:10.3f} | {ps:10.3f}")

print("=" * 60)

# =============================================================================
# STEP 5: Visualise everything
# =============================================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# --- Top-left: Accuracy over time ---
ax = axes[0, 0]
ax.plot(month_nums, accuracies, marker='o', linewidth=2.5, markersize=8, color='#1f77b4')
ax.axvline(5.5, color='orange', linestyle='--', linewidth=2, label='Data drift starts (M6)')
ax.axvline(8.5, color='crimson', linestyle='--', linewidth=2, label='Concept drift starts (M9)')
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Accuracy', fontsize=11)
ax.set_title('Model Accuracy Degradation', fontsize=12, fontweight='bold')
ax.set_ylim(-0.05, 1.05)
ax.legend(loc='lower left')
ax.grid(True, alpha=0.3)

# --- Top-middle: KL divergence ---
ax = axes[0, 1]
ax.plot(month_nums, kl_scores, marker='s', linewidth=2.5, markersize=8, color='purple')
ax.axvline(5.5, color='orange', linestyle='--', linewidth=2)
ax.axvline(8.5, color='crimson', linestyle='--', linewidth=2)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('KL Divergence', fontsize=11)
ax.set_title('KL Divergence from Reference', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# --- Top-right: PSI ---
ax = axes[0, 2]
ax.plot(month_nums, psi_scores, marker='^', linewidth=2.5, markersize=8, color='green')
ax.axvline(5.5, color='orange', linestyle='--', linewidth=2)
ax.axvline(8.5, color='crimson', linestyle='--', linewidth=2)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('PSI', fontsize=11)
ax.set_title('Population Stability Index', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# --- Bottom row: scatter plots of feature distributions ---
plot_months = [3, 7, 10]
titles = [
    'Month 3 — Reference (X2 ≈ +X1)',
    'Month 7 — Data Drift (X2 ≈ -X1)',
    'Month 10 — Concept Drift (new target rule)',
]
colors_scatter = ['#1f77b4', 'orange', 'crimson']

for idx, (pm, title, color) in enumerate(zip(plot_months, titles, colors_scatter)):
    ax = axes[1, idx]
    X_plot = months[pm - 1]['X']
    ax.scatter(X_plot[:, 0], X_plot[:, 1], alpha=0.25, s=8, c=color)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_xlabel('X1', fontsize=11)
    ax.set_ylabel('X2', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_aspect('equal')

plt.suptitle('Phase 80 — MLOps & Production Monitoring', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
out_path = 'src/phase80/mlops.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nPlot saved to: {out_path}")

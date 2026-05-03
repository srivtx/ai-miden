"""
Phase 76: Fairness & Bias — NumPy Concept Demo

GOAL:
  Create synthetic loan approval data with a historical gender bias,
  train a logistic classifier that replicates the bias, measure
  demographic parity and equalized odds violations, apply a simple
  pre-processing mitigation (re-weighting by group), and visualize
  the before/after fairness landscape.

WHY NumPy?
  Before running real fairness audits on GPU, we prototype the entire
  pipeline—data generation, model training, metric computation, and
  mitigation—with deterministic NumPy code. This makes the concept
  reproducible and inspectable line-by-line.

STRUCTURE:
  1. Generate synthetic credit-score data and a "true" qualification label.
  2. Inject historical bias: Group 1 is under-approved relative to its
     true qualification rate.
  3. Train a logistic regression classifier on the biased labels.
  4. Compute per-group TPR, FPR, positive rate, DP diff, and EO violation.
  5. Re-weight training samples to balance group-specific class
     distributions, then retrain.
  6. Compute the same metrics on the mitigated model.
  7. Plot acceptance rates, TPR/FPR, fairness metrics, and confusion
     matrices. Save to src/phase76/fairness_bias.png.
"""

import numpy as np

# ---------------------------------------------------------------------------
# NON-INTERACTIVE plotting backend — safe for headless CI / containers
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------
RNG_SEED = 42
N_SAMPLES = 1000          # Total synthetic applicants
TRAIN_RATIO = 0.8         # 80% train, 20% test
BIAS_STRENGTH = 0.55      # Group 1 positive labels are flipped to 0 with this prob
LR = 0.5
EPOCHS = 1000

np.random.seed(RNG_SEED)

# ---------------------------------------------------------------------------
# 2. SYNTHETIC DATA GENERATION
# ---------------------------------------------------------------------------
# WHY: We want a clean ground truth. Qualification should depend ONLY on
# credit score. Then we deliberately corrupt the labels for one group to
# simulate historical discrimination.

# Group membership: 0 or 1, balanced
group = (np.random.rand(N_SAMPLES) > 0.5).astype(int)

# Credit score feature: standard normal (already centered)
credit_score = np.random.randn(N_SAMPLES)

# True qualification: higher score -> more likely qualified.
# We add tiny noise so the relationship is probabilistic, not deterministic.
noise = np.random.randn(N_SAMPLES) * 0.2
y_true = (credit_score + noise > 0.0).astype(int)

# Biased label: Group 0 gets the true label. Group 1 loses some approvals.
# This simulates a world where loan officers historically rejected qualified
# Group 1 applicants because of prejudice encoded in the training archive.
y_biased = y_true.copy()
flip_candidates = (group == 1) & (y_true == 1)
flip_mask = flip_candidates & (np.random.rand(N_SAMPLES) < BIAS_STRENGTH)
y_biased[flip_mask] = 0

# Features for the model: credit score + group indicator.
# The model CAN see group. If the data is biased, it will learn to use it.
X = np.column_stack([credit_score, group])

# Train / test split
split_idx = int(TRAIN_RATIO * N_SAMPLES)
X_train, X_test = X[:split_idx], X[split_idx:]
g_train, g_test = group[:split_idx], group[split_idx:]
y_train, y_test = y_biased[:split_idx], y_biased[split_idx:]
y_true_train, y_true_test = y_true[:split_idx], y_true[split_idx:]

# ---------------------------------------------------------------------------
# 3. LOGISTIC REGRESSION (NumPy from scratch)
# ---------------------------------------------------------------------------
# WHY: We need a differentiable classifier so we can demonstrate weighted
# gradient descent later. A single linear layer + sigmoid is the simplest
# model that outputs probabilities.

def sigmoid(z):
    """Maps any real number to (0, 1)."""
    return 1.0 / (1.0 + np.exp(-z))


def train_logistic(X_tr, y_tr, W, b, lr=0.1, epochs=500, sample_weights=None):
    """
    Train with (optionally weighted) binary cross-entropy gradient descent.
    WHY weighted: different samples can contribute differently to the gradient.
    This is the lever we pull for bias mitigation.
    """
    n = X_tr.shape[0]
    for _ in range(epochs):
        z = X_tr @ W + b
        p = sigmoid(z)
        error = p - y_tr
        if sample_weights is not None:
            # Weighted gradient: each sample's error is scaled by its weight.
            grad_w = (X_tr.T @ (error * sample_weights)) / sample_weights.sum()
            grad_b = np.sum(error * sample_weights) / sample_weights.sum()
        else:
            grad_w = X_tr.T @ error / n
            grad_b = np.mean(error)
        W -= lr * grad_w
        b -= lr * grad_b
    return W, b


def predict(X, W, b, threshold=0.5):
    """Return binary predictions at the given decision threshold."""
    probs = sigmoid(X @ W + b)
    return (probs >= threshold).astype(int)


# ---------------------------------------------------------------------------
# 4. METRIC COMPUTATION
# ---------------------------------------------------------------------------
# WHY: Fairness is not a single number. We need per-group TPR, FPR, and
# positive rate so we can compute DP difference and EO violation.

def compute_fairness_metrics(y_true, y_pred, groups):
    """
    Returns a dict with per-group TP, FP, TN, FN, TPR, FPR, pos_rate,
    plus overall dp_diff and eo_violation.
    """
    unique_g = np.unique(groups)
    metrics = {}
    for g in unique_g:
        mask = (groups == g)
        yt = y_true[mask]
        yp = y_pred[mask]
        tp = int(np.sum((yt == 1) & (yp == 1)))
        fp = int(np.sum((yt == 0) & (yp == 1)))
        tn = int(np.sum((yt == 0) & (yp == 0)))
        fn = int(np.sum((yt == 1) & (yp == 0)))
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        pos_rate = np.mean(yp)
        metrics[int(g)] = {
            'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
            'tpr': tpr, 'fpr': fpr, 'pos_rate': pos_rate
        }
    # Demographic parity: difference in positive prediction rates.
    dp_diff = abs(metrics[0]['pos_rate'] - metrics[1]['pos_rate'])
    # Equalized odds violation: max gap in TPR or FPR.
    eo_viol = max(
        abs(metrics[0]['tpr'] - metrics[1]['tpr']),
        abs(metrics[0]['fpr'] - metrics[1]['fpr'])
    )
    metrics['dp_diff'] = dp_diff
    metrics['eo_viol'] = eo_viol
    return metrics


def print_metrics(label, m):
    print(f"\n{label}")
    print("-" * 50)
    for g in [0, 1]:
        print(f"  Group {g}: TPR={m[g]['tpr']:.3f}, FPR={m[g]['fpr']:.3f}, "
              f"PosRate={m[g]['pos_rate']:.3f}")
    print(f"  DP Difference : {m['dp_diff']:.3f}")
    print(f"  EO Violation  : {m['eo_viol']:.3f}")


# ---------------------------------------------------------------------------
# 5. BASELINE (BIASED) MODEL
# ---------------------------------------------------------------------------
# WHY: We train on the biased labels first. The model has no reason to
# treat the groups equally because the training signal itself is skewed.

W_biased = np.zeros(X.shape[1])
b_biased = 0.0
W_biased, b_biased = train_logistic(
    X_train, y_train, W_biased, b_biased, lr=LR, epochs=EPOCHS
)
y_pred_biased = predict(X_test, W_biased, b_biased)
metrics_biased = compute_fairness_metrics(y_test, y_pred_biased, g_test)
print_metrics("BEFORE MITIGATION (trained on biased labels)", metrics_biased)

# ---------------------------------------------------------------------------
# 6. PRE-PROCESSING MITIGATION: RE-WEIGHTING
# ---------------------------------------------------------------------------
# WHY: The training set has fewer positive examples for Group 1 because
# of the historical bias. If we give those rare positives higher weight,
# the gradient descent optimizer treats them as more important, forcing
# the model to learn a decision boundary that is kinder to Group 1.
# This is a pre-processing technique: we change the data (via weights)
# before the model sees it.

sample_weights = np.ones_like(y_train, dtype=float)
for g in [0, 1]:
    mask = (g_train == g)
    n_total = mask.sum()
    n_pos = np.sum(y_train[mask] == 1)
    n_neg = np.sum(y_train[mask] == 0)
    # Balance the two classes within the group.
    # Each class gets weight = n_total / (2 * count_of_class).
    if n_pos > 0:
        sample_weights[mask & (y_train == 1)] = n_total / (2.0 * n_pos)
    if n_neg > 0:
        sample_weights[mask & (y_train == 0)] = n_total / (2.0 * n_neg)

W_fair = np.zeros(X.shape[1])
b_fair = 0.0
W_fair, b_fair = train_logistic(
    X_train, y_train, W_fair, b_fair, lr=LR, epochs=EPOCHS,
    sample_weights=sample_weights
)
y_pred_fair = predict(X_test, W_fair, b_fair)
metrics_fair = compute_fairness_metrics(y_test, y_pred_fair, g_test)
print_metrics("AFTER MITIGATION (group-balanced re-weighting)", metrics_fair)

# ---------------------------------------------------------------------------
# 7. VISUALIZATION
# ---------------------------------------------------------------------------
# WHY: Tables of numbers are hard to read. Bars and heatmaps make the
# disparities visible at a glance.

fig, axes = plt.subplots(2, 4, figsize=(16, 8))

def plot_confusion(ax, tp, fp, tn, fn, title):
    """Draw a 2x2 confusion matrix as a blue heatmap."""
    cm = np.array([[tn, fp], [fn, tp]])
    im = ax.imshow(cm, cmap='Blues', vmin=0)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Pred 0', 'Pred 1'])
    ax.set_yticklabels(['True 0', 'True 1'])
    ax.set_title(title, fontsize=11)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                    color='black', fontsize=10)
    return im

# --- Top row: metrics before / after ---
# Acceptance rates
ax = axes[0, 0]
x = np.arange(2)
width = 0.35
ax.bar(x - width/2,
       [metrics_biased[0]['pos_rate'], metrics_biased[1]['pos_rate']],
       width, label='Before', color='salmon', edgecolor='black')
ax.bar(x + width/2,
       [metrics_fair[0]['pos_rate'], metrics_fair[1]['pos_rate']],
       width, label='After', color='seagreen', edgecolor='black')
ax.set_ylabel('Positive Prediction Rate')
ax.set_title('Acceptance Rate by Group')
ax.set_xticks(x)
ax.set_xticklabels(['Group 0', 'Group 1'])
ax.legend()
ax.set_ylim(0, 1.0)

# TPR / FPR
ax = axes[0, 1]
metrics_names = ['TPR', 'FPR']
x = np.arange(len(metrics_names))
width = 0.2
# Before
ax.bar(x - width*1.5, [metrics_biased[0]['tpr'], metrics_biased[0]['fpr']],
       width, label='G0 Before', color='lightcoral', edgecolor='black')
ax.bar(x - width*0.5, [metrics_fair[0]['tpr'], metrics_fair[0]['fpr']],
       width, label='G0 After', color='lightgreen', edgecolor='black')
ax.bar(x + width*0.5, [metrics_biased[1]['tpr'], metrics_biased[1]['fpr']],
       width, label='G1 Before', color='indianred', edgecolor='black')
ax.bar(x + width*1.5, [metrics_fair[1]['tpr'], metrics_fair[1]['fpr']],
       width, label='G1 After', color='mediumseagreen', edgecolor='black')
ax.set_ylabel('Rate')
ax.set_title('TPR and FPR by Group')
ax.set_xticks(x)
ax.set_xticklabels(metrics_names)
ax.legend(fontsize=8)
ax.set_ylim(0, 1.0)

# Fairness metrics bar
ax = axes[0, 2]
fairness_names = ['DP Diff', 'EO Viol']
x = np.arange(len(fairness_names))
width = 0.35
before_vals = [metrics_biased['dp_diff'], metrics_biased['eo_viol']]
after_vals = [metrics_fair['dp_diff'], metrics_fair['eo_viol']]
ax.bar(x - width/2, before_vals, width, label='Before', color='salmon', edgecolor='black')
ax.bar(x + width/2, after_vals, width, label='After', color='seagreen', edgecolor='black')
ax.set_ylabel('Difference')
ax.set_title('Fairness Metrics')
ax.set_xticks(x)
ax.set_xticklabels(fairness_names)
ax.legend()
ymax = max(max(before_vals), max(after_vals)) * 1.3
if ymax < 0.1:
    ymax = 0.1
ax.set_ylim(0, ymax)

# Text summary
ax = axes[0, 3]
ax.axis('off')
summary_text = (
    f"Before Mitigation\n"
    f"  DP Diff: {metrics_biased['dp_diff']:.3f}\n"
    f"  EO Viol: {metrics_biased['eo_viol']:.3f}\n\n"
    f"After Mitigation\n"
    f"  DP Diff: {metrics_fair['dp_diff']:.3f}\n"
    f"  EO Viol: {metrics_fair['eo_viol']:.3f}\n\n"
    f"Improvement\n"
    f"  DP: {metrics_biased['dp_diff'] - metrics_fair['dp_diff']:.3f}\n"
    f"  EO: {metrics_biased['eo_viol'] - metrics_fair['eo_viol']:.3f}"
)
ax.text(0.1, 0.5, summary_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='center', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

# --- Bottom row: confusion matrices ---
plot_confusion(axes[1, 0],
               metrics_biased[0]['tp'], metrics_biased[0]['fp'],
               metrics_biased[0]['tn'], metrics_biased[0]['fn'],
               'Group 0 Before')
plot_confusion(axes[1, 1],
               metrics_biased[1]['tp'], metrics_biased[1]['fp'],
               metrics_biased[1]['tn'], metrics_biased[1]['fn'],
               'Group 1 Before')
plot_confusion(axes[1, 2],
               metrics_fair[0]['tp'], metrics_fair[0]['fp'],
               metrics_fair[0]['tn'], metrics_fair[0]['fn'],
               'Group 0 After')
plot_confusion(axes[1, 3],
               metrics_fair[1]['tp'], metrics_fair[1]['fp'],
               metrics_fair[1]['tn'], metrics_fair[1]['fn'],
               'Group 1 After')

plt.suptitle('Phase 76: Fairness & Bias — Before vs. After Reweighting Mitigation',
             fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96])

output_path = "/Users/zen/Desktop/building-ai/ai-miden/src/phase76/fairness_bias.png"
plt.savefig(output_path, dpi=150)
plt.close(fig)

print(f"\nPlot saved to: {output_path}")

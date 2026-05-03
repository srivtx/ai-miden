"""
Phase 75: Explainable AI (XAI) — NumPy Concept Demo

GOAL:
  Train a tiny MLP on synthetic tabular data, then demonstrate four
  explanation techniques from scratch: saliency maps, exact SHAP values,
  LIME local surrogate models, and attention visualization.

WHY NumPy?
  XAI libraries (SHAP, Captum) wrap complex C++ and tensor operations.
  By rebuilding the core math in NumPy, you see that explanations are
  just forward passes, gradients, weighted linear fits, and matrix
  multiplication — nothing magic.

STRUCTURE:
  1. Generate synthetic 4-feature data (features 0,1 matter; 2,3 are noise).
  2. Train a 2-layer MLP with manual back-propagation.
  3. SALIENCY: compute ∂output/∂input via backprop for a test instance.
  4. SHAP: enumerate all 2^4 subsets to compute exact Shapley values.
  5. LIME: perturb one instance, weight by proximity, fit linear surrogate.
  6. ATTENTION: single-head self-attention on a 4-token sequence, heatmap.
  7. Plot all four explanations in a 2x2 grid. Save to src/phase75/xai_numpy.png.
"""

import itertools
import numpy as np

# ---------------------------------------------------------------------------
# NON-INTERACTIVE plotting backend
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------
RNG_SEED = 75
N_SAMPLES = 800
N_FEATURES = 4
HIDDEN_DIM = 8
LR = 0.5
EPOCHS = 600

np.random.seed(RNG_SEED)

# ---------------------------------------------------------------------------
# 2. SYNTHETIC DATA: only features 0 and 1 are predictive
# ---------------------------------------------------------------------------
# WHY: We want a ground-truth story. If our explanation methods correctly
# identify features 0 and 1 as important and 2 and 3 as noise, we have
# empirical evidence that the methods work.

X = np.random.randn(N_SAMPLES, N_FEATURES)
# True boundary: 2*x0 - 1.5*x1 > 0 → class 1
logits_true = 2.0 * X[:, 0] - 1.5 * X[:, 1]
y = (logits_true > 0).astype(float).reshape(-1, 1)

# Train/test split
split = int(0.8 * N_SAMPLES)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Baseline for SHAP = training mean
baseline = X_train.mean(axis=0)

# ---------------------------------------------------------------------------
# 3. TINY MLP (manual backprop)
# ---------------------------------------------------------------------------
# WHY: We need a non-linear model so linear coefficients are insufficient.
# A 2-layer MLP is the simplest non-linear black box.

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def sigmoid_derivative(a):
    # If a is already sigmoid(z), derivative is a*(1-a)
    return a * (1.0 - a)

# Xavier-ish initialization
W1 = np.random.randn(N_FEATURES, HIDDEN_DIM) * np.sqrt(2.0 / N_FEATURES)
b1 = np.zeros((1, HIDDEN_DIM))
W2 = np.random.randn(HIDDEN_DIM, 1) * np.sqrt(2.0 / HIDDEN_DIM)
b2 = np.zeros((1, 1))

for epoch in range(EPOCHS):
    # Forward
    z1 = X_train @ W1 + b1          # (N, H)
    a1 = np.tanh(z1)                # (N, H)
    z2 = a1 @ W2 + b2               # (N, 1)
    a2 = sigmoid(z2)                # (N, 1)

    # Loss: binary cross-entropy
    loss = -np.mean(y_train * np.log(a2 + 1e-8) + (1 - y_train) * np.log(1 - a2 + 1e-8))

    # Backward
    dz2 = a2 - y_train              # (N, 1)
    dW2 = (a1.T @ dz2) / split
    db2 = dz2.mean(axis=0, keepdims=True)

    da1 = dz2 @ W2.T                # (N, H)
    dz1 = da1 * (1 - a1 ** 2)       # tanh derivative
    dW1 = (X_train.T @ dz1) / split
    db1 = dz1.mean(axis=0, keepdims=True)

    # Update
    W2 -= LR * dW2
    b2 -= LR * db2
    W1 -= LR * dW1
    b1 -= LR * db1

    if epoch % 100 == 0:
        print(f"Epoch {epoch:4d} | Loss: {loss:.4f}")

# Test accuracy
z1_test = X_test @ W1 + b1
a1_test = np.tanh(z1_test)
z2_test = a1_test @ W2 + b2
a2_test = sigmoid(z2_test)
preds_test = (a2_test > 0.5).astype(float)
acc = np.mean(preds_test == y_test)
print(f"\nTest Accuracy: {acc:.2%}")

# ---------------------------------------------------------------------------
# 4. SALIENCY MAP (gradient of output w.r.t. input)
# ---------------------------------------------------------------------------
# WHY: Saliency tells us which input dimensions, if nudged, would change
# the model's confidence the most. It is the simplest gradient-based
# explanation.

# Pick a test instance CLOSE to the decision boundary so gradients are large
# and the model is not saturated.
z1_all = X_test @ W1 + b1
a1_all = np.tanh(z1_all)
z2_all = a1_all @ W2 + b2
a2_all = sigmoid(z2_all)
# Find instance where prediction is closest to 0.5
idx = int(np.argmin(np.abs(a2_all.flatten() - 0.5)))
x_instance = X_test[idx].reshape(1, -1)
y_instance = y_test[idx]
print(f"Selected borderline instance {idx}, pred={a2_all[idx, 0]:.4f}, label={int(y_instance.item())}")

# Forward + manual backward to input
z1_i = x_instance @ W1 + b1
a1_i = np.tanh(z1_i)
z2_i = a1_i @ W2 + b2
a2_i = sigmoid(z2_i)

# SALIENCY: backprop from the PRE-SIGMOID logit z2 to avoid saturation.
# WHY: The sigmoid derivative a2*(1-a2) becomes near-zero when the model is
# highly confident. The logit gradient does not have this problem.
# dz2/da1 = W2.T
# da1/dz1 = 1 - tanh^2(z1_i)
# dz1/dx  = W1.T
grad_z2 = np.ones_like(z2_i)               # d(z2)/d(z2) = 1
grad_a1 = grad_z2 @ W2.T                    # (1, H)
grad_z1 = grad_a1 * (1 - a1_i ** 2)         # (1, H)
grad_x = grad_z1 @ W1.T                     # (1, N_FEATURES)

saliency = np.abs(grad_x).flatten()
print(f"\nSaliency for instance {idx} (label {int(y_instance.item())}):")
for i, s in enumerate(saliency):
    print(f"  Feature {i}: {s:.4f}")

# ---------------------------------------------------------------------------
# 5. EXACT SHAP VALUES (enumerate all subsets)
# ---------------------------------------------------------------------------
# WHY: Shapley values come from cooperative game theory. They assign each
# feature a fair share of the prediction by averaging its marginal
# contribution across all possible subsets of other features.
# For 4 features, 2^4 = 16 subsets — tiny enough to compute exactly.

def model_forward(x_in):
    """Helper: forward pass for a single or batch of inputs."""
    z1 = x_in @ W1 + b1
    a1 = np.tanh(z1)
    z2 = a1 @ W2 + b2
    return sigmoid(z2)

def shap_exact(x, base):
    """Compute exact SHAP values for a single instance x (1D array)."""
    n = len(x)
    shap_vals = np.zeros(n)
    # Precompute f(S) for all subsets using a mask representation
    # We will build inputs where masked features come from baseline
    for i in range(n):
        marginal_sum = 0.0
        count = 0
        # All subsets S that do NOT contain i
        others = [j for j in range(n) if j != i]
        for r in range(len(others) + 1):
            for subset in itertools.combinations(others, r):
                S = list(subset)
                # Build input where S features come from x, rest from baseline
                x_S = base.copy()
                x_S[list(S)] = x[list(S)]
                x_Si = base.copy()
                x_Si[list(S) + [i]] = x[list(S) + [i]]
                f_S = model_forward(x_S.reshape(1, -1))[0, 0]
                f_Si = model_forward(x_Si.reshape(1, -1))[0, 0]
                marginal_sum += (f_Si - f_S)
                count += 1
        shap_vals[i] = marginal_sum / count
    return shap_vals

shap_vals = shap_exact(x_instance.flatten(), baseline)
print(f"\nExact SHAP values for instance {idx}:")
for i, s in enumerate(shap_vals):
    print(f"  Feature {i}: {s:+.4f}")

# ---------------------------------------------------------------------------
# 6. LIME (Local Interpretable Model-agnostic Explanations)
# ---------------------------------------------------------------------------
# WHY: SHAP is exact but expensive. LIME is approximate and fast. It builds
# a local linear model around the instance of interest.

N_PERTURB = 200
KERNEL_WIDTH = 1.5

# Perturb around the instance with larger noise so some cross the boundary
perturbations = x_instance + np.random.randn(N_PERTURB, N_FEATURES) * 1.5
# Get black-box predictions
y_perturb = model_forward(perturbations).flatten()

# Distances and weights
distances = np.linalg.norm(perturbations - x_instance, axis=1)
weights = np.exp(- (distances ** 2) / (2 * KERNEL_WIDTH ** 2))

# Weighted linear regression (closed form)
# Add bias column
X_aug = np.hstack([np.ones((N_PERTURB, 1)), perturbations])
W = np.diag(weights)
# beta = (X'WX)^-1 X'W y
XtWX = X_aug.T @ W @ X_aug
XtWy = X_aug.T @ W @ y_perturb
beta = np.linalg.solve(XtWX + 1e-4 * np.eye(N_FEATURES + 1), XtWy)

lime_coeffs = beta[1:]  # exclude intercept
print(f"\nLIME coefficients for instance {idx}:")
for i, c in enumerate(lime_coeffs):
    print(f"  Feature {i}: {c:+.4f}")

# ---------------------------------------------------------------------------
# 7. ATTENTION VISUALIZATION (single-head self-attention)
# ---------------------------------------------------------------------------
# WHY: Attention is the core mechanism of Transformers. Visualizing it
# shows information flow, but remember — attention does not always equal
# explanation.

N_TOKENS = 4
DIM = 4

# Synthetic token embeddings (each row is a token vector)
X_tokens = np.array([
    [1.0, 0.2, 0.1, 0.0],
    [0.3, 1.0, 0.2, 0.1],
    [0.1, 0.3, 1.0, 0.2],
    [0.0, 0.1, 0.3, 1.0],
])

# Random but fixed projection matrices for Q, K, V
np.random.seed(42)
W_q = np.random.randn(DIM, DIM) * 0.3
W_k = np.random.randn(DIM, DIM) * 0.3
W_v = np.random.randn(DIM, DIM) * 0.3

Q = X_tokens @ W_q
K = X_tokens @ W_k
V = X_tokens @ W_v

scores = Q @ K.T
scores = scores / np.sqrt(DIM)

# Row-wise softmax
exp_scores = np.exp(scores - scores.max(axis=1, keepdims=True))
attn = exp_scores / exp_scores.sum(axis=1, keepdims=True)

token_labels = ['[CLS]', 'cat', 'sat', 'mat']
print(f"\nAttention matrix ({N_TOKENS}x{N_TOKENS}):")
print(attn.round(3))

# ---------------------------------------------------------------------------
# 8. PLOTTING
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# -- Subplot 1: Saliency --
ax = axes[0, 0]
ax.bar(range(N_FEATURES), saliency, color=['#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c'])
ax.set_xticks(range(N_FEATURES))
ax.set_xticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('Saliency Map (|∂output/∂input|)')
ax.set_ylabel('Absolute Gradient')
ax.axhline(0, color='black', linewidth=0.5)

# -- Subplot 2: SHAP --
ax = axes[0, 1]
colors = ['#27ae60' if v > 0 else '#c0392b' for v in shap_vals]
ax.barh(range(N_FEATURES), shap_vals, color=colors)
ax.set_yticks(range(N_FEATURES))
ax.set_yticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('Exact SHAP Values')
ax.set_xlabel('Contribution to Prediction')
ax.axvline(0, color='black', linewidth=0.5)

# -- Subplot 3: LIME --
ax = axes[1, 0]
colors = ['#27ae60' if v > 0 else '#c0392b' for v in lime_coeffs]
ax.barh(range(N_FEATURES), lime_coeffs, color=colors)
ax.set_yticks(range(N_FEATURES))
ax.set_yticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('LIME Local Surrogate Coefficients')
ax.set_xlabel('Local Linear Weight')
ax.axvline(0, color='black', linewidth=0.5)

# -- Subplot 4: Attention Heatmap --
ax = axes[1, 1]
im = ax.imshow(attn, cmap='viridis', vmin=0, vmax=1)
ax.set_xticks(range(N_TOKENS))
ax.set_yticks(range(N_TOKENS))
ax.set_xticklabels(token_labels)
ax.set_yticklabels(token_labels)
ax.set_title('Self-Attention Heatmap')
ax.set_xlabel('Key')
ax.set_ylabel('Query')
for i in range(N_TOKENS):
    for j in range(N_TOKENS):
        ax.text(j, i, f'{attn[i, j]:.2f}', ha='center', va='center', color='white', fontsize=10)
fig.colorbar(im, ax=ax, fraction=0.046)

fig.suptitle('Phase 75: Explainable AI (XAI) — Four Perspectives on the Same Model', fontsize=14, y=1.02)
plt.tight_layout()
out_path = 'src/phase75/xai_numpy.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nSaved plot to {out_path}")

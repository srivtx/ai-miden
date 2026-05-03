# FRONTIER TRACK: Phase 116 — Automated Red-Teaming and Scalable Oversight
# LOCAL NumPy concept demonstration
# Simulates GCG adversarial suffix optimization and Constitutional Classifiers.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Reproducibility
np.random.seed(116)

# -----------------------------------------------------------------------------
# 1. Toy world setup
# -----------------------------------------------------------------------------
V = 100         # vocabulary size
d = 16          # embedding dimension
L_harm = 5      # length of harmful query
S_len = 12      # length of adversarial suffix
n_train = 1000  # training samples for target model

# Embedding matrix: each token has a vector
E = np.random.randn(V, d) * 0.5

# Fixed harmful query (token IDs)
harmful_tokens = np.array([0, 1, 2, 3, 4])
harmful_emb = E[harmful_tokens].sum(axis=0)

# -----------------------------------------------------------------------------
# 2. Target model (small MLP) that should reject harmful inputs
# -----------------------------------------------------------------------------
# We keep the network small and add training noise so the boundary is soft.
W1 = np.random.randn(8, d) * 0.05
b1 = np.zeros(8)
W2 = np.random.randn(1, 8) * 0.05
b2 = np.zeros(1)


def target_forward(x):
    """Return scalar reject score. Higher = more likely to reject."""
    h = np.maximum(0, W1 @ x + b1)
    return (W2 @ h + b2).item()


def target_backward(x):
    """Return gradient of reject score w.r.t. input embedding x."""
    z1 = W1 @ x + b1
    h = np.maximum(0, z1)
    dz1 = (z1 > 0).astype(float) * (W2.T).flatten()
    dx = W1.T @ dz1
    return dx


# Train the target model on benign vs harmful examples
X_train = []
y_train = []
for _ in range(n_train):
    if np.random.rand() < 0.5:
        # Benign: random tokens
        tokens = np.random.randint(0, V, size=L_harm + S_len)
        x = E[tokens].sum(axis=0)
        X_train.append(x)
        y_train.append(0.0)  # low reject score
    else:
        # Harmful: harmful query + random suffix
        suffix = np.random.randint(0, V, size=S_len)
        tokens = np.concatenate([harmful_tokens, suffix])
        x = E[tokens].sum(axis=0)
        X_train.append(x)
        y_train.append(1.0)  # high reject score

X_train = np.stack(X_train)
y_train = np.array(y_train).reshape(-1, 1)

# Simple gradient descent on MSE with input noise for a softer boundary
lr = 0.01
for epoch in range(100):
    X_noisy = X_train + np.random.randn(*X_train.shape) * 0.2
    z1 = X_noisy @ W1.T + b1
    h = np.maximum(0, z1)
    logits = h @ W2.T + b2
    loss = np.mean((logits - y_train) ** 2)
    dlogits = 2 * (logits - y_train) / len(X_train)
    dh = dlogits @ W2
    dz1 = dh * (z1 > 0).astype(float)
    dW2 = dlogits.T @ h
    db2 = dlogits.sum(axis=0)
    dW1 = dz1.T @ X_noisy
    db1 = dz1.sum(axis=0)
    W1 -= lr * dW1
    b1 -= lr * db1
    W2 -= lr * dW2
    b2 -= lr * db2

print(f"Target model trained. Final MSE: {loss:.4f}")

# -----------------------------------------------------------------------------
# 3. Baseline: random suffix attack
# -----------------------------------------------------------------------------
n_random = 100
random_scores = []
for _ in range(n_random):
    suffix = np.random.randint(0, V, size=S_len)
    x = harmful_emb + E[suffix].sum(axis=0)
    score = target_forward(x)
    random_scores.append(score)

# Adaptive threshold: accept if score is below the 80th percentile of random scores
threshold = float(np.percentile(random_scores, 20))
random_accepts = sum(1 for s in random_scores if s < threshold)

print(f"Random suffix accept rate: {random_accepts}/{n_random} ({random_accepts/n_random*100:.1f}%)")
print(f"Adaptive accept threshold (80th percentile): {threshold:.3f}")

# -----------------------------------------------------------------------------
# 4. GCG optimization of adversarial suffix
# -----------------------------------------------------------------------------
n_runs = 10
n_opt_steps = 300
lr_gcg = 0.5
opt_accept_rates = []

for run in range(n_runs):
    suffix = np.random.randint(0, V, size=S_len)
    scores = []
    best_run_score = float('inf')
    best_run_suffix = suffix.copy()
    for step in range(n_opt_steps):
        suffix_emb = E[suffix]
        x = harmful_emb + suffix_emb.sum(axis=0)
        score = target_forward(x)
        scores.append(score)
        if score < best_run_score:
            best_run_score = score
            best_run_suffix = suffix.copy()

        # Minimize reject score
        grad = target_backward(x)
        # Gradient w.r.t. each suffix token is the same because they sum
        updated_emb = suffix_emb - lr_gcg * grad

        # Project back to nearest token embedding (nearest neighbor in embedding space)
        dist = np.linalg.norm(updated_emb[:, None, :] - E[None, :, :], axis=2)
        suffix = np.argmin(dist, axis=1)

    # Use the best suffix seen during this run
    final_score = best_run_score
    opt_accept_rates.append(1 if final_score < threshold else 0)

opt_accept_rate = np.mean(opt_accept_rates)
print(f"Optimized suffix accept rate ({n_runs} runs): {opt_accept_rate*100:.1f}%")

# Store the last run's scores for plotting
last_run_scores = scores

# -----------------------------------------------------------------------------
# 5. Constitutional Classifier (defense)
# -----------------------------------------------------------------------------
# Build a dataset of benign, harmful-random, and harmful-optimized examples.
X_cls = []
y_cls = []
for i in range(1000):
    r = np.random.rand()
    if r < 0.4:
        # Benign
        tokens = np.random.randint(0, V, size=L_harm + S_len)
        x = E[tokens].sum(axis=0)
        X_cls.append(x)
        y_cls.append(0.0)
    elif r < 0.7:
        # Harmful with random suffix
        suffix = np.random.randint(0, V, size=S_len)
        x = harmful_emb + E[suffix].sum(axis=0)
        X_cls.append(x)
        y_cls.append(1.0)
    else:
        # Harmful with a quickly optimized suffix (synthetic adversarial)
        suffix = np.random.randint(0, V, size=S_len)
        for _ in range(20):
            x_tmp = harmful_emb + E[suffix].sum(axis=0)
            grad_tmp = target_backward(x_tmp)
            updated = E[suffix] - 0.5 * grad_tmp
            dist = np.linalg.norm(updated[:, None, :] - E[None, :, :], axis=2)
            suffix = np.argmin(dist, axis=1)
        x = harmful_emb + E[suffix].sum(axis=0)
        X_cls.append(x)
        y_cls.append(1.0)

X_cls = np.stack(X_cls)
y_cls = np.array(y_cls).reshape(-1, 1)

# Normalize features for stable classifier training
X_mean = X_cls.mean(axis=0)
X_std = X_cls.std(axis=0) + 1e-8
X_cls_norm = (X_cls - X_mean) / X_std

# Train a linear classifier with logistic loss (cross-entropy)
W_cls = np.random.randn(1, d) * 0.01
b_cls = np.zeros(1)

for epoch in range(500):
    logits = X_cls_norm @ W_cls.T + b_cls
    # Stable sigmoid
    preds = 1.0 / (1.0 + np.exp(-np.clip(logits, -20, 20)))
    loss = -np.mean(y_cls * np.log(preds + 1e-8) + (1 - y_cls) * np.log(1 - preds + 1e-8))
    dlogits = preds - y_cls
    dW = dlogits.T @ X_cls_norm / len(X_cls)
    db = dlogits.mean(axis=0)
    W_cls -= 0.5 * dW
    b_cls -= 0.5 * db

# Evaluate defense on a fresh optimized suffix (keeping best seen)
suffix = np.random.randint(0, V, size=S_len)
best_eval_score = float('inf')
best_eval_suffix = suffix.copy()
for step in range(n_opt_steps):
    suffix_emb = E[suffix]
    x = harmful_emb + suffix_emb.sum(axis=0)
    score = target_forward(x)
    if score < best_eval_score:
        best_eval_score = score
        best_eval_suffix = suffix.copy()
    grad = target_backward(x)
    updated_emb = suffix_emb - lr_gcg * grad
    dist = np.linalg.norm(updated_emb[:, None, :] - E[None, :, :], axis=2)
    suffix = np.argmin(dist, axis=1)
suffix = best_eval_suffix

adv_input = harmful_emb + E[suffix].sum(axis=0)
adv_input_norm = (adv_input - X_mean) / X_std
cls_logit = (adv_input_norm @ W_cls.T + b_cls).item()
cls_prob = 1.0 / (1.0 + np.exp(-np.clip(cls_logit, -20, 20)))
blocked = cls_prob > 0.5

target_score = target_forward(adv_input)
target_accepts = target_score < threshold

print(f"Without classifier: target accepts adversarial? {target_accepts} (score={target_score:.3f})")
print(f"With classifier: classifier blocks? {blocked} (prob={cls_prob:.3f})")

# -----------------------------------------------------------------------------
# 6. Plots
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: GCG loss curve from the last run
axes[0].plot(last_run_scores)
axes[0].axhline(threshold, color='red', linestyle='--', label='Accept threshold')
axes[0].set_title('Adversarial Suffix Optimization (GCG)')
axes[0].set_xlabel('Optimization Step')
axes[0].set_ylabel('Reject Score')
axes[0].legend()

# Plot 2: Attack success rate
categories = ['Random Suffix', 'Optimized Suffix']
accept_rates = [random_accepts / n_random, opt_accept_rate]
colors = ['orange', 'red']
axes[1].bar(categories, accept_rates, color=colors)
axes[1].set_ylim(0, 1)
axes[1].set_title('Attack Success Rate')
axes[1].set_ylabel('Target Accept Rate')

# Plot 3: Defense effectiveness
defense_labels = ['No Defense', 'With Classifier']
adv_success = [
    1.0 if target_accepts else 0.0,
    1.0 if (target_accepts and not blocked) else 0.0,
]
axes[2].bar(defense_labels, adv_success, color=['red', 'green'])
axes[2].set_ylim(0, 1)
axes[2].set_title('Defense Effectiveness')
axes[2].set_ylabel('Adversarial Success Rate')

plt.tight_layout()
plt.savefig('src/phase116/gcg_simulation.png')
plt.close()

print("\nPlots saved to src/phase116/gcg_simulation.png")

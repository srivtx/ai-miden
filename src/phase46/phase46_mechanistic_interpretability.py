#!/usr/bin/env python3
"""
Phase 46: Mechanistic Interpretability — NumPy Concept Demo
=============================================================
This script demonstrates how to reverse-engineer a tiny neural network
by analyzing its internal activations, patching neurons causally,
and decomposing hidden states into interpretable features.

Key insight: Neural networks do not have to be black boxes. By
examining activations, patching them, and decomposing them into
sparse features, we can understand what individual components compute.

Concepts demonstrated:
  - Activation visualization (which inputs fire which neurons)
  - Activation patching (causal intervention)
  - Sparse autoencoders (decomposing activations into features)
  - Superposition (more features than neurons)

Why this matters:
  Understanding what models do internally is essential for safety,
  debugging, and trust. Mechanistic interpretability is the field
  that builds the "repair manual" for AI systems.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(46)

# =============================================================================
# SECTION 1: DATA — 4 DISTINCT PATTERNS
# =============================================================================
# We create 4 binary patterns. The model must learn to classify them.
# This forces the hidden layer to develop meaningful representations.

patterns = {
    'A': np.array([1, 1, 0, 0]),
    'B': np.array([0, 0, 1, 1]),
    'C': np.array([1, 0, 1, 0]),
    'D': np.array([0, 1, 0, 1]),
}

labels = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

def generate_samples(n_per_class=100):
    """Generate noisy samples of each pattern."""
    X, y = [], []
    for name, pat in patterns.items():
        for _ in range(n_per_class):
            noise = np.random.randn(4) * 0.1
            X.append(pat + noise)
            y.append(labels[name])
    return np.array(X), np.array(y)

X_train, y_train = generate_samples(100)
X_test, y_test = generate_samples(50)

# =============================================================================
# SECTION 2: TINY MODEL WITH 2 HIDDEN NEURONS (superposition demo)
# =============================================================================
# Only 2 hidden neurons must represent 4 distinct patterns.
# This forces superposition: each neuron must participate in multiple patterns.

class TinyModel:
    def __init__(self):
        self.W1 = np.random.randn(4, 2) * 0.5
        self.b1 = np.zeros(2)
        self.W2 = np.random.randn(2, 4) * 0.5
        self.b2 = np.zeros(4)

    def forward(self, X, return_hidden=False):
        z1 = X @ self.W1 + self.b1
        h = np.tanh(z1)
        logits = h @ self.W2 + self.b2
        if return_hidden:
            return logits, h
        return logits

    def predict(self, X):
        return np.argmax(self.forward(X), axis=1)

    def accuracy(self, X, y):
        return np.mean(self.predict(X) == y)

# Train with cross-entropy
model = TinyModel()
lr = 0.1
for epoch in range(500):
    logits, h = model.forward(X_train, return_hidden=True)
    # Softmax
    exp = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp / np.sum(exp, axis=1, keepdims=True)
    # Gradient
    n = len(y_train)
    grad_logits = probs.copy()
    grad_logits[np.arange(n), y_train] -= 1
    grad_logits /= n
    # Backprop
    grad_W2 = h.T @ grad_logits
    grad_b2 = np.sum(grad_logits, axis=0)
    grad_h = grad_logits @ model.W2.T
    grad_z1 = grad_h * (1 - h ** 2)
    grad_W1 = X_train.T @ grad_z1
    grad_b1 = np.sum(grad_z1, axis=0)
    # Update
    model.W2 -= lr * grad_W2
    model.b2 -= lr * grad_b2
    model.W1 -= lr * grad_W1
    model.b1 -= lr * grad_b1

print("="*60)
print("Phase 46: Mechanistic Interpretability")
print("="*60)
print(f"Model accuracy: {model.accuracy(X_test, y_test):.1%}")
print(f"Hidden layer: 2 neurons representing 4 patterns (superposition)")

# =============================================================================
# SECTION 3: ACTIVATION VISUALIZATION
# =============================================================================

print("\n--- Activation Visualization ---")
for name, pat in patterns.items():
    _, h = model.forward(pat.reshape(1, -1), return_hidden=True)
    print(f"Pattern {name}: hidden = [{h[0,0]:+.2f}, {h[0,1]:+.2f}]")

# =============================================================================
# SECTION 4: ACTIVATION PATCHING
# =============================================================================

print("\n--- Activation Patching ---")
# Clean: Pattern A -> should predict A (class 0)
# Corrupt: Pattern B -> should predict B (class 1)
# Patch: Run B, but replace hidden neuron 0 with A's activation

_, h_clean = model.forward(patterns['A'].reshape(1, -1), return_hidden=True)
_, h_corrupt = model.forward(patterns['B'].reshape(1, -1), return_hidden=True)

print(f"Clean (A):   hidden = [{h_clean[0,0]:+.2f}, {h_clean[0,1]:+.2f}] -> pred = {model.predict(patterns['A'].reshape(1, -1))[0]}")
print(f"Corrupt (B): hidden = [{h_corrupt[0,0]:+.2f}, {h_corrupt[0,1]:+.2f}] -> pred = {model.predict(patterns['B'].reshape(1, -1))[0]}")

# Patch neuron 0 from clean into corrupt
h_patched0 = h_corrupt.copy()
h_patched0[0, 0] = h_clean[0, 0]
logits_patched0 = h_patched0 @ model.W2 + model.b2
pred_patched0 = np.argmax(logits_patched0)
print(f"Patched n0:  hidden = [{h_patched0[0,0]:+.2f}, {h_patched0[0,1]:+.2f}] -> pred = {pred_patched0}")

# Patch neuron 1 from clean into corrupt
h_patched1 = h_corrupt.copy()
h_patched1[0, 1] = h_clean[0, 1]
logits_patched1 = h_patched1 @ model.W2 + model.b2
pred_patched1 = np.argmax(logits_patched1)
print(f"Patched n1:  hidden = [{h_patched1[0,0]:+.2f}, {h_patched1[0,1]:+.2f}] -> pred = {pred_patched1}")

# Causal attribution
if pred_patched0 == labels['A']:
    print("-> Neuron 0 is CAUSALLY responsible for the 'A' prediction")
elif pred_patched1 == labels['A']:
    print("-> Neuron 1 is CAUSALLY responsible for the 'A' prediction")
else:
    print("-> Neither neuron alone is sufficient; both contribute")

# =============================================================================
# SECTION 5: SPARSE AUTOENCODER
# =============================================================================

print("\n--- Sparse Autoencoder ---")
# Collect all hidden activations
_, H_train = model.forward(X_train, return_hidden=True)

# Train a sparse autoencoder: 2 -> 8 -> 2
# Initialize encoder directions to roughly align with hidden patterns
sae_W_enc = np.array([
    [-1.0, -1.0],
    [1.0, 1.0],
    [1.0, -1.0],
    [-1.0, 1.0],
    [0.5, 0.5],
    [-0.5, -0.5],
    [0.2, -0.2],
    [-0.2, 0.2]
]).T * 0.8
sae_b_enc = np.ones(8) * 0.2
sae_W_dec = np.random.randn(8, 2) * 0.1
sae_b_dec = np.zeros(2)

for epoch in range(1500):
    # Encode
    pre_f = H_train @ sae_W_enc + sae_b_enc
    f = np.maximum(pre_f, 0)  # ReLU
    # Decode
    H_recon = f @ sae_W_dec + sae_b_dec
    # Loss: reconstruction + mild L1 sparsity
    grad_H_recon = 2 * (H_recon - H_train) / len(H_train)
    grad_f = grad_H_recon @ sae_W_dec.T
    grad_f += 0.005 * np.sign(f)  # L1 on active features only
    grad_f[pre_f <= 0] = 0  # ReLU backprop
    grad_W_dec = f.T @ grad_H_recon
    grad_b_dec = np.sum(grad_H_recon, axis=0)
    grad_W_enc = H_train.T @ grad_f
    grad_b_enc = np.sum(grad_f, axis=0)
    # Update
    sae_W_dec -= 0.01 * grad_W_dec
    sae_b_dec -= 0.01 * grad_b_dec
    sae_W_enc -= 0.01 * grad_W_enc
    sae_b_enc -= 0.01 * grad_b_enc

# Analyze features for each pattern
print("\nFeature activations per pattern (top 3 features):")
for name, pat in patterns.items():
    _, h = model.forward(pat.reshape(1, -1), return_hidden=True)
    f = np.maximum(h @ sae_W_enc + sae_b_enc, 0)
    top3 = np.argsort(f[0])[-3:][::-1]
    print(f"  Pattern {name}: features {top3} = {f[0, top3].round(2)}")

# Sparsity
all_f = np.maximum(H_train @ sae_W_enc + sae_b_enc, 0)
sparsity = np.mean(all_f == 0)
print(f"\nOverall sparsity: {sparsity:.1%} of features are inactive")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Hidden activations for each pattern
ax = axes[0]
hidden_by_pattern = []
pattern_names = []
for name in ['A', 'B', 'C', 'D']:
    _, h = model.forward(patterns[name].reshape(1, -1), return_hidden=True)
    hidden_by_pattern.append(h[0])
    pattern_names.append(name)
hidden_by_pattern = np.array(hidden_by_pattern)
x = np.arange(4)
width = 0.35
ax.bar(x - width/2, hidden_by_pattern[:, 0], width, label='Neuron 0')
ax.bar(x + width/2, hidden_by_pattern[:, 1], width, label='Neuron 1')
ax.set_xticks(x)
ax.set_xticklabels(pattern_names)
ax.set_ylabel('Activation')
ax.set_title('Hidden Activations by Pattern (Superposition)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Activation patching results
ax = axes[1]
conditions = ['Clean\n(A)', 'Corrupt\n(B)', 'Patched\nN0', 'Patched\nN1']
preds = [labels['A'], labels['B'], pred_patched0, pred_patched1]
colors = ['#2ecc71', '#e74c3c', '#3498db', '#9b59b6']
bars = ax.bar(conditions, preds, color=colors)
ax.set_ylabel('Predicted Class')
ax.set_title('Activation Patching: Causal Attribution')
ax.set_ylim(-0.5, 3.5)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(['A', 'B', 'C', 'D'])
for bar, p in zip(bars, preds):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            ['A', 'B', 'C', 'D'][p], ha='center', va='bottom', fontsize=12)
ax.grid(True, alpha=0.3)

# Plot 3: Sparse autoencoder feature activity
ax = axes[2]
feature_activations = []
for name in ['A', 'B', 'C', 'D']:
    _, h = model.forward(patterns[name].reshape(1, -1), return_hidden=True)
    f = np.maximum(h @ sae_W_enc + sae_b_enc, 0)
    feature_activations.append(f[0])
feature_activations = np.array(feature_activations)
im = ax.imshow(feature_activations, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(8))
ax.set_xticklabels([f'F{i}' for i in range(8)])
ax.set_yticks(range(4))
ax.set_yticklabels(['A', 'B', 'C', 'D'])
ax.set_title('Sparse Autoencoder Features')
ax.set_xlabel('Feature Index')
ax.set_ylabel('Pattern')
plt.colorbar(im, ax=ax)

plt.tight_layout()
os.makedirs('src/phase46', exist_ok=True)
plt.savefig('src/phase46/mechanistic_interpretability.png', dpi=150)
print("\nSaved plot to src/phase46/mechanistic_interpretability.png")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Mechanistic interpretability reveals what neural networks do inside:")
print("  - Visualization shows which neurons fire for which patterns")
print("  - Activation patching proves CAUSAL responsibility")
print("  - Sparse autoencoders decompose activity into features")
print("  - Superposition: 2 neurons can represent 4+ patterns")
print("\nThis is the foundation of AI safety and debugging.")
print("Without interpretability, models are black boxes.")
print("With it, we can build the repair manual.")

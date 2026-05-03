#!/usr/bin/env python3
"""
Phase 70: Domain Adaptation — NumPy Concept Demo
==================================================
This script demonstrates how adapting a model to a specific domain
shifts its behavior toward that domain at a small cost to general
performance. We simulate:

  1. A base model trained on general data
  2. Continual pre-training on domain-specific unlabeled data
  3. Task-specific fine-tuning on labeled domain tasks
  4. The accuracy trade-off: domain gains vs. general losses

Key insight: Domain adaptation is not free. Shifting the model's
distribution toward medicine/coding/legal necessarily moves it away
from general trivia. The art is finding the optimal amount of shift.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(70)

# =============================================================================
# SECTION 1: SETUP — Simulate a model and two data distributions
# =============================================================================
# We represent the world as a 20-dimensional feature space.
# "General" tasks and "Domain" tasks draw from different distributions.
# The base model is trained to separate general classes.
# Domain adaptation nudges the model toward domain-specific patterns.

dim = 20
n_domain_classes = 3
n_general_classes = 3

# Base model weights: trained on general data
W_base = np.random.randn(n_general_classes, dim) * 0.5
b_base = np.random.randn(n_general_classes) * 0.1

# Domain-specific "true" weights: what an ideal domain expert would learn
W_domain_true = np.random.randn(n_domain_classes, dim) * 0.5
b_domain_true = np.random.randn(n_domain_classes) * 0.1

print("="*60)
print("Phase 70: Domain Adaptation")
print("="*60)
print(f"\nFeature dimension: {dim}")
print(f"General classes: {n_general_classes}")
print(f"Domain classes: {n_domain_classes}")

# =============================================================================
# SECTION 2: DATA GENERATION
# =============================================================================
# General data: broad, varied features
# Domain data: narrower, specialized features correlated with domain tasks

def generate_general_data(n_samples):
    """Generate general-purpose classification data."""
    X = np.random.randn(n_samples, dim)
    # Labels from base model's true decision boundary
    logits = X @ W_base.T + b_base
    y = np.argmax(logits + np.random.randn(n_samples, n_general_classes)*0.5, axis=1)
    return X, y

def generate_domain_data(n_samples):
    """Generate domain-specific classification data."""
    # Domain data has a different mean and covariance — it lives in a
    # different region of feature space than general data.
    X = np.random.randn(n_samples, dim) + np.array([1.5, -1.0] + [0.0]*(dim-2))
    # Domain labels from domain true weights
    logits = X @ W_domain_true.T + b_domain_true
    y = np.argmax(logits + np.random.randn(n_samples, n_domain_classes)*0.3, axis=1)
    return X, y

# Create train and test sets
X_gen_train, y_gen_train = generate_general_data(800)
X_gen_test,  y_gen_test  = generate_general_data(200)
X_dom_train, y_dom_train = generate_domain_data(400)
X_dom_test,  y_dom_test  = generate_domain_data(200)

print(f"\nGeneral train: {len(X_gen_train)} samples")
print(f"Domain train:  {len(X_dom_train)} samples")
print(f"General test:  {len(X_gen_test)} samples")
print(f"Domain test:   {len(X_dom_test)} samples")

# =============================================================================
# SECTION 3: TRAIN THE BASE MODEL ON GENERAL DATA
# =============================================================================
# Before domain adaptation, the base model must actually be good at general
# tasks. We train W_base on general data so we have a meaningful starting
# point. Without this, there is no trade-off to measure.

W_base_trained = W_base.copy()
b_base_trained = b_base.copy()
lr_base = 0.05
epochs_base = 200

for epoch in range(epochs_base):
    logits = X_gen_train @ W_base_trained.T + b_base_trained
    exp_scores = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

    mask = np.zeros_like(probs)
    mask[np.arange(len(y_gen_train)), y_gen_train] = 1
    dlogits = (probs - mask) / len(y_gen_train)

    dW = dlogits.T @ X_gen_train
    db = np.sum(dlogits, axis=0)

    W_base_trained -= lr_base * dW
    b_base_trained -= lr_base * db

# Evaluate base model on general test set
logits_gen_base = X_gen_test @ W_base_trained.T + b_base_trained
pred_gen_base = np.argmax(logits_gen_base, axis=1)
acc_gen_base = np.mean(pred_gen_base == y_gen_test)
print(f"\n--- Base Model Trained on General Data ---")
print(f"General accuracy (base): {acc_gen_base:.3f}")

# =============================================================================
# SECTION 4: CONTINUAL PRE-TRAINING SIMULATION
# =============================================================================
# We simulate continual pre-training by nudging the trained base model
# toward the domain data distribution. In reality, this is next-token
# prediction on domain text. Here, we approximate it as supervised
# adaptation with a small learning rate, which captures the intuition
# that the model shifts toward the domain manifold.

# The "domain-adapted" model starts as the trained base
# We further train it on domain data with gradient descent
W_domain = W_base_trained.copy()
b_domain = b_base_trained.copy()

# We need the domain model to output domain_classes.
# We project base weights into domain space by learning an affine transform.
# In practice, this is like the model learning new representations.
W_proj = np.random.randn(n_domain_classes, n_general_classes) * 0.3

lr_cpt = 0.02
epochs_cpt = 100

for epoch in range(epochs_cpt):
    # Forward: project base features then classify
    # We simulate that CPT learns better features for domain data
    logits = X_dom_train @ W_domain.T + b_domain
    # Map to domain classes via a linear head (simplified)
    logits_dom = logits @ W_proj.T

    # Softmax
    exp_scores = np.exp(logits_dom - np.max(logits_dom, axis=1, keepdims=True))
    probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

    # Cross-entropy gradient
    mask = np.zeros_like(probs)
    mask[np.arange(len(y_dom_train)), y_dom_train] = 1
    dlogits = (probs - mask) / len(y_dom_train)

    # Backprop through the head and into the domain weights
    dW_proj = dlogits.T @ logits
    db_domain = np.sum(dlogits @ W_proj, axis=0)
    dW_domain = (dlogits @ W_proj).T @ X_dom_train

    W_proj -= lr_cpt * dW_proj
    b_domain -= lr_cpt * db_domain
    W_domain -= lr_cpt * dW_domain

print(f"\n--- Continual Pre-Training Complete ---")
print(f"Domain weight shift (L2 from trained base): {np.linalg.norm(W_domain - W_base_trained):.3f}")

# =============================================================================
# SECTION 4: TASK-SPECIFIC FINE-TUNING SIMULATION
# =============================================================================
# After CPT, we fine-tune on labeled domain tasks. We simulate multiple
# fine-tuning intensities to show the trade-off curve.
# Intensity = how many epochs / how large the learning rate.

intensities = [0, 20, 50, 100, 200, 400, 800]
general_accuracies = []
domain_accuracies = []
weight_shifts = []

for intensity in intensities:
    # Start from the CPT checkpoint
    W_ft = W_domain.copy()
    b_ft = b_domain.copy()
    W_h = W_proj.copy()

    # Fine-tune for 'intensity' steps on labeled domain tasks
    lr_ft = 0.05
    for step in range(intensity):
        logits = X_dom_train @ W_ft.T + b_ft
        logits_dom = logits @ W_h.T

        exp_scores = np.exp(logits_dom - np.max(logits_dom, axis=1, keepdims=True))
        probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

        mask = np.zeros_like(probs)
        mask[np.arange(len(y_dom_train)), y_dom_train] = 1
        dlogits = (probs - mask) / len(y_dom_train)

        dW_h = dlogits.T @ logits
        db_ft = np.sum(dlogits @ W_h, axis=0)
        dW_ft = (dlogits @ W_h).T @ X_dom_train

        W_h -= lr_ft * dW_h
        b_ft -= lr_ft * db_ft
        W_ft -= lr_ft * dW_ft

    # Evaluate on domain test set
    logits_dom_test = (X_dom_test @ W_ft.T + b_ft) @ W_h.T
    pred_dom = np.argmax(logits_dom_test, axis=1)
    acc_domain = np.mean(pred_dom == y_dom_test)

    # Evaluate on general test set
    # We measure general accuracy using the original base task.
    # As the model shifts toward domain, W_ft drifts away from the
    # optimal general classifier, so general accuracy drops.
    logits_gen = X_gen_test @ W_ft.T + b_ft
    pred_gen = np.argmax(logits_gen, axis=1)
    acc_general = np.mean(pred_gen == y_gen_test)

    general_accuracies.append(acc_general)
    domain_accuracies.append(acc_domain)
    weight_shifts.append(np.linalg.norm(W_ft - W_base_trained))

    print(f"Intensity {intensity:4d}: Domain acc = {acc_domain:.3f}, General acc = {acc_general:.3f}, Shift = {weight_shifts[-1]:.3f}")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Domain vs. General accuracy trade-off
ax = axes[0, 0]
ax.plot(general_accuracies, domain_accuracies, 'o-', color='#2c3e50', linewidth=2, markersize=8)
for i, intensity in enumerate(intensities):
    ax.annotate(f'{intensity}', (general_accuracies[i], domain_accuracies[i]),
                textcoords="offset points", xytext=(5, 5), fontsize=8)
ax.set_xlabel('General Task Accuracy')
ax.set_ylabel('Domain Task Accuracy')
ax.set_title('The Domain Adaptation Trade-Off\n(More specialization = Less generalization)')
ax.grid(True, alpha=0.3)
ax.set_xlim(0.3, 1.0)
ax.set_ylim(0.3, 1.0)

# Plot 2: Accuracy vs. Fine-Tuning Intensity
ax = axes[0, 1]
ax.plot(intensities, domain_accuracies, 's-', color='#27ae60', linewidth=2, label='Domain Accuracy')
ax.plot(intensities, general_accuracies, '^-', color='#e74c3c', linewidth=2, label='General Accuracy')
ax.set_xlabel('Fine-Tuning Intensity (steps)')
ax.set_ylabel('Accuracy')
ax.set_title('Accuracy vs. Fine-Tuning Intensity')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Weight shift magnitude
ax = axes[1, 0]
ax.bar(range(len(intensities)), weight_shifts, color='#3498db', alpha=0.7, edgecolor='black')
ax.set_xticks(range(len(intensities)))
ax.set_xticklabels(intensities)
ax.set_xlabel('Fine-Tuning Intensity')
ax.set_ylabel('L2 Distance from Base Weights')
ax.set_title('How Far the Model Drifts from Its Origin')
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Simulated probability distribution shift
ax = axes[1, 1]
# Show how a single feature's activation changes across adaptation
feature_idx = 0
base_act = np.tanh(X_dom_test[:50, feature_idx] * W_base[0, feature_idx] + b_base[0])
adapted_act = np.tanh(X_dom_test[:50, feature_idx] * W_ft[0, feature_idx] + b_ft[0])
x_pos = np.arange(50)
ax.bar(x_pos - 0.2, base_act, 0.4, label='Base Model Activation', color='#95a5a6', alpha=0.8)
ax.bar(x_pos + 0.2, adapted_act, 0.4, label='Domain-Adapted Activation', color='#e67e22', alpha=0.8)
ax.set_xlabel('Sample Index')
ax.set_ylabel('Activation Value')
ax.set_title('Feature Activation Shift on Domain Data')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase70', exist_ok=True)
plt.savefig('src/phase70/domain_adaptation.png', dpi=150)
print("\nSaved plot to src/phase70/domain_adaptation.png")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Base model (no adaptation):")
print(f"  General accuracy: {general_accuracies[0]:.3f}")
print(f"  Domain accuracy:  {domain_accuracies[0]:.3f}")
print(f"\nAfter domain adaptation + task fine-tuning:")
print(f"  General accuracy: {general_accuracies[-1]:.3f}")
print(f"  Domain accuracy:  {domain_accuracies[-1]:.3f}")
print(f"  Weight shift:     {weight_shifts[-1]:.3f}")
print(f"\nDomain gain: +{(domain_accuracies[-1] - domain_accuracies[0])*100:.1f} percentage points")
print(f"General loss: -{(general_accuracies[0] - general_accuracies[-1])*100:.1f} percentage points")
print("\nKey lessons:")
print("  1. Domain adaptation dramatically improves in-domain performance")
print("  2. There is a measurable trade-off with general performance")
print("  3. The optimal adaptation intensity depends on your use case")
print("  4. Early stopping and regularization can reduce generalization loss")
print("  5. Real assistants combine domain adaptation with retrieval to fill gaps")

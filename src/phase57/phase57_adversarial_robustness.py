#!/usr/bin/env python3
"""
Phase 57: Adversarial Robustness — NumPy Concept Demo
=======================================================
This script demonstrates how tiny, calculated perturbations fool
neural networks, and how adversarial training makes them robust.

Key insight: Neural networks are surprisingly brittle. A perturbation
smaller than a rounding error can flip a prediction from 99% confident
correct to 99% confident wrong.

Concepts demonstrated:
  - Adversarial example generation
  - FGSM (Fast Gradient Sign Method)
  - PGD (Projected Gradient Descent)
  - Adversarial training
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(57)

# =============================================================================
# SECTION 1: BUILD A SIMPLE 2D CLASSIFIER
# =============================================================================
# 2D data, 2 classes. Model: 2 -> 8 -> 2 MLP.

n_samples = 200
X = np.random.randn(n_samples, 2)
y = (X[:, 0] + X[:, 1] > 0).astype(int)  # class 1 if x0+x1 > 0
n_classes = 2

# One-hot labels
Y = np.zeros((n_samples, n_classes))
Y[np.arange(n_samples), y] = 1

# Train/val split
n_train = 150
X_train, Y_train = X[:n_train], Y[:n_train]
X_val, Y_val = X[n_train:], Y[n_train:]
y_val = y[n_train:]

print("="*60)
print("Phase 57: Adversarial Robustness")
print("="*60)
print(f"\nDataset: {n_samples} samples, 2D, binary classification")
print(f"Train: {n_train}, Val: {n_samples - n_train}")

# Network parameters
W1 = np.random.randn(2, 8) * 0.5
b1 = np.zeros(8)
W2 = np.random.randn(8, 2) * 0.5
b2 = np.zeros(2)

def relu(x):
    return np.maximum(x, 0)

def softmax(x):
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)

def forward(x):
    z1 = x @ W1 + b1
    h = relu(z1)
    z2 = h @ W2 + b2
    out = softmax(z2)
    return out, z1, h, z2

def cross_entropy(pred, target):
    return -np.mean(np.sum(target * np.log(pred + 1e-10), axis=1))

# Train standard model
lr = 0.1
for epoch in range(200):
    pred, z1, h, z2 = forward(X_train)
    loss = cross_entropy(pred, Y_train)
    
    # Backprop
    dz2 = (pred - Y_train) / n_train
    dW2 = h.T @ dz2
    db2 = np.sum(dz2, axis=0)
    dh = dz2 @ W2.T
    dz1 = dh * (z1 > 0).astype(float)
    dW1 = X_train.T @ dz1
    db1 = np.sum(dz1, axis=0)
    
    W2 -= lr * dW2
    b2 -= lr * db2
    W1 -= lr * dW1
    b1 -= lr * db1

# Evaluate clean
pred_val, _, _, _ = forward(X_val)
acc_clean = np.mean(np.argmax(pred_val, axis=1) == y_val)
print(f"\nStandard model clean accuracy: {acc_clean*100:.1f}%")

# =============================================================================
# SECTION 2: FGSM ATTACK
# =============================================================================

def fgsm_attack(x, y_true, eps):
    """One-step FGSM attack."""
    # Forward
    pred, z1, h, z2 = forward(x)
    
    # Backprop to input
    dz2 = pred - y_true
    dh = dz2 @ W2.T
    dz1 = dh * (z1 > 0).astype(float)
    dx = dz1 @ W1.T
    
    # Perturb
    x_adv = x + eps * np.sign(dx)
    return x_adv

# Test FGSM at different epsilon values
epsilons = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
fgsm_accs = []

for eps in epsilons:
    X_adv = fgsm_attack(X_val, Y_val, eps)
    pred_adv, _, _, _ = forward(X_adv)
    acc = np.mean(np.argmax(pred_adv, axis=1) == y_val)
    fgsm_accs.append(acc)
    if eps > 0:
        print(f"  FGSM ε={eps:.2f}: accuracy = {acc*100:.1f}%")

# =============================================================================
# SECTION 3: PGD ATTACK
# =============================================================================

def pgd_attack(x, y_true, eps, alpha, steps):
    """Iterative PGD attack."""
    x_adv = x.copy()
    for _ in range(steps):
        # Forward
        pred, z1, h, z2 = forward(x_adv)
        
        # Backprop to input
        dz2 = pred - y_true
        dh = dz2 @ W2.T
        dz1 = dh * (z1 > 0).astype(float)
        dx = dz1 @ W1.T
        
        # Step
        x_adv = x_adv + alpha * np.sign(dx)
        
        # Project back to epsilon ball
        x_adv = np.clip(x_adv, x - eps, x + eps)
    return x_adv

print("\n--- PGD Attack ---")
pgd_eps = 0.2
pgd_accs = []
steps_list = [1, 5, 10, 20, 40]

for steps in steps_list:
    X_adv = pgd_attack(X_val, Y_val, eps=pgd_eps, alpha=pgd_eps/4, steps=steps)
    pred_adv, _, _, _ = forward(X_adv)
    acc = np.mean(np.argmax(pred_adv, axis=1) == y_val)
    pgd_accs.append(acc)
    print(f"  PGD steps={steps:2d}: accuracy = {acc*100:.1f}%")

# =============================================================================
# SECTION 4: ADVERSARIAL TRAINING
# =============================================================================

print("\n--- Adversarial Training ---")

# Re-initialize
W1_r = np.random.randn(2, 8) * 0.5
b1_r = np.zeros(8)
W2_r = np.random.randn(8, 2) * 0.5
b2_r = np.zeros(2)

def forward_robust(x):
    z1 = x @ W1_r + b1_r
    h = relu(z1)
    z2 = h @ W2_r + b2_r
    out = softmax(z2)
    return out, z1, h, z2

def fgsm_attack_robust(x, y_true, eps):
    pred, z1, h, z2 = forward_robust(x)
    dz2 = pred - y_true
    dh = dz2 @ W2_r.T
    dz1 = dh * (z1 > 0).astype(float)
    dx = dz1 @ W1_r.T
    return x + eps * np.sign(dx)

# Train on mix of clean + adversarial
for epoch in range(300):
    # Generate adversarial examples
    X_adv = fgsm_attack_robust(X_train, Y_train, eps=0.1)
    
    # Mix clean and adversarial
    X_mixed = np.vstack([X_train, X_adv])
    Y_mixed = np.vstack([Y_train, Y_train])
    
    # Forward
    pred, z1, h, z2 = forward_robust(X_mixed)
    loss = cross_entropy(pred, Y_mixed)
    
    # Backprop
    dz2 = (pred - Y_mixed) / len(X_mixed)
    dW2 = h.T @ dz2
    db2 = np.sum(dz2, axis=0)
    dh = dz2 @ W2_r.T
    dz1 = dh * (z1 > 0).astype(float)
    dW1 = X_mixed.T @ dz1
    db1 = np.sum(dz1, axis=0)
    
    W2_r -= lr * dW2
    b2_r -= lr * db2
    W1_r -= lr * dW1
    b1_r -= lr * db1

# Evaluate robust model
pred_val_r, _, _, _ = forward_robust(X_val)
acc_clean_r = np.mean(np.argmax(pred_val_r, axis=1) == y_val)

X_adv_r = fgsm_attack_robust(X_val, Y_val, eps=0.2)
pred_adv_r, _, _, _ = forward_robust(X_adv_r)
acc_adv_r = np.mean(np.argmax(pred_adv_r, axis=1) == y_val)

print(f"Robust model clean accuracy:  {acc_clean_r*100:.1f}%")
print(f"Robust model under FGSM ε=0.2: {acc_adv_r*100:.1f}%")
print(f"Standard model under FGSM ε=0.2: {fgsm_accs[3]*100:.1f}%")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Decision boundary + adversarial examples
ax = axes[0, 0]
xx, yy = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
grid = np.c_[xx.ravel(), yy.ravel()]
probs, _, _, _ = forward(grid)
probs = probs[:, 1].reshape(xx.shape)
ax.contourf(xx, yy, probs, levels=20, cmap='RdBu', alpha=0.6)

# Plot clean and adversarial points
X_adv_viz = fgsm_attack(X_val[:30], Y_val[:30], eps=0.3)
ax.scatter(X_val[:30, 0], X_val[:30, 1], c=y_val[:30], cmap='RdBu', 
           edgecolors='black', s=80, label='Clean', zorder=3)
ax.scatter(X_adv_viz[:, 0], X_adv_viz[:, 1], c=y_val[:30], cmap='RdBu',
           edgecolors='yellow', s=80, marker='s', label='Adversarial', zorder=3)
for i in range(min(10, len(X_val))):
    ax.arrow(X_val[i, 0], X_val[i, 1], 
             X_adv_viz[i, 0]-X_val[i, 0], X_adv_viz[i, 1]-X_val[i, 1],
             head_width=0.05, color='black', alpha=0.3)
ax.set_title('FGSM Adversarial Examples (ε=0.3)')
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: FGSM accuracy vs epsilon
ax = axes[0, 1]
ax.plot(epsilons, [a*100 for a in fgsm_accs], 'ro-', linewidth=2, markersize=8)
ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Random guess')
ax.set_title('Standard Model Under FGSM Attack')
ax.set_xlabel('Perturbation ε')
ax.set_ylabel('Accuracy (%)')
ax.set_ylim(0, 105)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: PGD accuracy vs iterations
ax = axes[1, 0]
ax.plot(steps_list, [a*100 for a in pgd_accs], 'bs-', linewidth=2, markersize=8)
ax.axhline(y=fgsm_accs[3]*100, color='red', linestyle='--', alpha=0.5, label='FGSM (1 step)')
ax.set_title('PGD Attack Strength vs Iterations')
ax.set_xlabel('PGD Steps')
ax.set_ylabel('Accuracy (%)')
ax.set_ylim(0, 105)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Adversarial training comparison
ax = axes[1, 1]
categories = ['Clean\nAccuracy', 'Under FGSM\nε=0.2']
std_vals = [acc_clean*100, fgsm_accs[3]*100]
rob_vals = [acc_clean_r*100, acc_adv_r*100]
x = np.arange(len(categories))
width = 0.35
ax.bar(x - width/2, std_vals, width, label='Standard Training', color='#e74c3c', alpha=0.8, edgecolor='black')
ax.bar(x + width/2, rob_vals, width, label='Adversarial Training', color='#2ecc71', alpha=0.8, edgecolor='black')
ax.set_title('Standard vs Adversarial Training')
ax.set_ylabel('Accuracy (%)')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
for i, (s, r) in enumerate(zip(std_vals, rob_vals)):
    ax.text(i - width/2, s + 2, f'{s:.0f}%', ha='center', fontsize=10)
    ax.text(i + width/2, r + 2, f'{r:.0f}%', ha='center', fontsize=10)

plt.tight_layout()
os.makedirs('src/phase57', exist_ok=True)
plt.savefig('src/phase57/adversarial_robustness.png', dpi=150)
print("\nSaved plot to src/phase57/adversarial_robustness.png")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Standard model clean accuracy:       {acc_clean*100:.1f}%")
print(f"Standard model under FGSM ε=0.2:     {fgsm_accs[3]*100:.1f}%")
print(f"Standard model under PGD (20 steps): {pgd_accs[-1]*100:.1f}%")
print(f"Robust model clean accuracy:         {acc_clean_r*100:.1f}%")
print(f"Robust model under FGSM ε=0.2:       {acc_adv_r*100:.1f}%")
print("\nAdversarial robustness:")
print("  - Tiny perturbations can flip predictions")
print("  - FGSM: fast one-step attack using gradient sign")
print("  - PGD: iterative attack, stronger than FGSM")
print("  - Adversarial training: train on perturbed examples")
print("  - Trade-off: clean accuracy drops, robustness rises")
print("\nApplications: self-driving cars, facial recognition, medical AI")

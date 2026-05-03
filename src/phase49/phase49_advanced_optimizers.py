#!/usr/bin/env python3
"""
Phase 49: Advanced Optimizers — NumPy Concept Demo
====================================================
This script demonstrates how advanced optimizers (Momentum, RMSprop,
Adam, AdamW) and learning rate schedules improve training compared
to vanilla SGD.

Key insight: Not all parameters need the same step size. Adam gives
each parameter its own adaptive rate based on gradient history. AdamW
decouples weight decay from gradient scaling. Schedules adjust the
learning rate over time for smoother convergence.

Concepts demonstrated:
  - SGD vs Momentum vs RMSprop vs Adam vs AdamW
  - Learning rate schedules (step decay, cosine, warmup)
  - Impact on convergence speed and final loss
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(49)

# =============================================================================
# SECTION 1: TEST PROBLEM — ROSENBROCK FUNCTION
# =============================================================================
# A classic optimization challenge: narrow curved valley.
# Tests whether optimizers can navigate different curvatures.

def rosenbrock(x, y):
    """f(x,y) = (1-x)^2 + 100(y-x^2)^2. Minimum at (1,1)."""
    val = (1 - x)**2 + 100 * (y - x**2)**2
    return min(val, 1e6)  # clip to avoid overflow in plots

def rosenbrock_grad(x, y):
    dx = -2*(1 - x) - 400*x*(y - x**2)
    dy = 200*(y - x**2)
    return np.array([dx, dy])

# =============================================================================
# SECTION 2: OPTIMIZERS
# =============================================================================

def sgd(lr=0.001, epochs=2000):
    """Vanilla SGD."""
    theta = np.array([-1.0, 1.5])
    history = [theta.copy()]
    for _ in range(epochs):
        g = rosenbrock_grad(theta[0], theta[1])
        theta -= lr * g
        history.append(theta.copy())
    return np.array(history)

def momentum_sgd(lr=0.001, beta=0.9, epochs=2000):
    """SGD with momentum."""
    theta = np.array([-1.0, 1.5])
    v = np.zeros(2)
    history = [theta.copy()]
    for _ in range(epochs):
        g = rosenbrock_grad(theta[0], theta[1])
        v = beta * v + g
        theta -= lr * v
        history.append(theta.copy())
    return np.array(history)

def rmsprop(lr=0.01, beta=0.9, eps=1e-8, epochs=2000):
    """RMSprop: adaptive per-parameter scaling."""
    theta = np.array([-1.0, 1.5])
    v = np.zeros(2)
    history = [theta.copy()]
    for _ in range(epochs):
        g = rosenbrock_grad(theta[0], theta[1])
        v = beta * v + (1 - beta) * g**2
        theta -= lr * g / (np.sqrt(v) + eps)
        history.append(theta.copy())
    return np.array(history)

def adam(lr=0.01, beta1=0.9, beta2=0.999, eps=1e-8, epochs=2000):
    """Adam: momentum + adaptive scaling + bias correction."""
    theta = np.array([-1.0, 1.5])
    m = np.zeros(2)
    v = np.zeros(2)
    history = [theta.copy()]
    for t in range(1, epochs + 1):
        g = rosenbrock_grad(theta[0], theta[1])
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        v_hat = v / (1 - beta2**t)
        theta -= lr * m_hat / (np.sqrt(v_hat) + eps)
        history.append(theta.copy())
    return np.array(history)

def adamw(lr=0.01, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.01, epochs=2000):
    """AdamW: decoupled weight decay."""
    theta = np.array([-1.0, 1.5])
    m = np.zeros(2)
    v = np.zeros(2)
    history = [theta.copy()]
    for t in range(1, epochs + 1):
        g = rosenbrock_grad(theta[0], theta[1])
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        v_hat = v / (1 - beta2**t)
        # Adam update
        theta -= lr * m_hat / (np.sqrt(v_hat) + eps)
        # Decoupled weight decay
        theta -= lr * weight_decay * theta
        history.append(theta.copy())
    return np.array(history)

# =============================================================================
# SECTION 3: LR SCHEDULES
# =============================================================================

def cosine_schedule(initial_lr, current_step, total_steps, min_lr=1e-6):
    """Cosine annealing learning rate."""
    progress = current_step / total_steps
    return min_lr + 0.5 * (initial_lr - min_lr) * (1 + np.cos(np.pi * progress))

def warmup_cosine_schedule(initial_lr, current_step, warmup_steps, total_steps):
    """Linear warmup then cosine decay."""
    if current_step < warmup_steps:
        return initial_lr * (current_step / warmup_steps)
    return cosine_schedule(initial_lr, current_step - warmup_steps, total_steps - warmup_steps)

def sgd_cosine(lr=0.01, epochs=2000):
    """SGD with cosine annealing."""
    theta = np.array([-1.0, 1.5])
    history = [theta.copy()]
    for t in range(epochs):
        g = rosenbrock_grad(theta[0], theta[1])
        current_lr = cosine_schedule(lr, t, epochs)
        theta -= current_lr * g
        history.append(theta.copy())
    return np.array(history)

def sgd_warmup_cosine(lr=0.01, warmup=200, epochs=2000):
    """SGD with warmup + cosine."""
    theta = np.array([-1.0, 1.5])
    history = [theta.copy()]
    for t in range(epochs):
        g = rosenbrock_grad(theta[0], theta[1])
        current_lr = warmup_cosine_schedule(lr, t, warmup, epochs)
        theta -= current_lr * g
        history.append(theta.copy())
    return np.array(history)

# =============================================================================
# SECTION 4: RUN ALL AND COMPARE
# =============================================================================

print("="*60)
print("Phase 49: Advanced Optimizers")
print("="*60)

results = {}
results['SGD'] = sgd(lr=0.0003, epochs=3000)
results['Momentum'] = momentum_sgd(lr=0.0003, epochs=3000)
results['RMSprop'] = rmsprop(lr=0.005, epochs=3000)
results['Adam'] = adam(lr=0.005, epochs=3000)
results['AdamW'] = adamw(lr=0.005, epochs=3000)
results['SGD+Cosine'] = sgd_cosine(lr=0.001, epochs=3000)
results['SGD+Warmup+Cosine'] = sgd_warmup_cosine(lr=0.001, warmup=300, epochs=3000)

# Compute losses
for name, hist in results.items():
    losses = [rosenbrock(p[0], p[1]) for p in hist]
    final_loss = losses[-1]
    print(f"{name:20s}: final loss = {final_loss:.6f}")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Loss curves
ax = axes[0]
for name, hist in results.items():
    losses = [rosenbrock(p[0], p[1]) for p in hist]
    ax.plot(losses, label=name, alpha=0.8)
ax.set_xlabel('Step')
ax.set_ylabel('Rosenbrock Loss (log)')
ax.set_yscale('log')
ax.set_title('Optimizer Comparison')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 2: Trajectory in parameter space
ax = axes[1]
for name, hist in results.items():
    ax.plot(hist[:, 0], hist[:, 1], label=name, alpha=0.7, linewidth=1)
ax.plot(1, 1, 'r*', markersize=15, label='Minimum')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Optimization Trajectories')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Plot 3: LR schedule visualization
ax = axes[2]
steps = np.arange(3000)
lr_cosine = [cosine_schedule(0.01, s, 3000) for s in steps]
lr_warmup = [warmup_cosine_schedule(0.01, s, 300, 3000) for s in steps]
ax.plot(steps, lr_cosine, 'b-', label='Cosine')
ax.plot(steps, lr_warmup, 'r-', label='Warmup + Cosine')
ax.set_xlabel('Step')
ax.set_ylabel('Learning Rate')
ax.set_title('Learning Rate Schedules')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase49', exist_ok=True)
plt.savefig('src/phase49/advanced_optimizers.png', dpi=150)
print("\nSaved plot to src/phase49/advanced_optimizers.png")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Adam and AdamW dominate modern training because they:")
print("  1. Give each parameter its own adaptive learning rate")
print("  2. Use momentum to smooth the optimization path")
print("  3. Apply bias correction for stable early training")
print("  4. Decouple weight decay (AdamW) for better generalization")
print("Learning rate schedules (cosine, warmup) further improve")
print("convergence by starting carefully and settling precisely.")

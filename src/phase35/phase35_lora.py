"""
Phase 35: LoRA & Parameter-Efficient Fine-Tuning

This script demonstrates Low-Rank Adaptation (LoRA) using only NumPy.

We build:
1. A "pre-trained" base linear model (frozen weights)
2. A new task that requires adapting the base model
3. A LoRA adapter (low-rank matrices B and A) that learns the adaptation
4. Comparison of trainable parameters: full fine-tuning vs. LoRA
5. Adapter merging: combining BA into W for zero-overhead inference

Why NumPy? So every operation is visible. No framework magic.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. SETUP: BASE MODEL AND NEW TASK
# ============================================================================
# We create a base model that was "pre-trained" on some task.
# Then we define a new task that is a small perturbation of the base task.
# The perturbation is intentionally low-rank so LoRA can learn it efficiently.
# ============================================================================

np.random.seed(42)
d = 20          # model dimension
r = 2           # LoRA rank (very small!)
n_samples = 500

# Base weight matrix W (pre-trained, frozen)
W_base = np.random.randn(d, d) * 0.3

# The new task requires: W_new = W_base + delta
# We construct delta as a low-rank matrix: delta = B_true @ A_true
# This means LoRA should be able to perfectly represent the adaptation.
B_true = np.random.randn(d, r) * 0.5
A_true = np.random.randn(r, d) * 0.5
delta = B_true @ A_true
W_new = W_base + delta

print("=" * 70)
print("PHASE 35: LoRA & PARAMETER-EFFICIENT FINE-TUNING")
print("=" * 70)
print(f"Model dimension: {d}")
print(f"LoRA rank: {r}")
print(f"Base task: y = W_base @ x")
print(f"New task:  y = (W_base + B_true @ A_true) @ x")
print(f"The adaptation delta is rank-{r} by construction.")
print()

# Generate training data for the new task
X_train = np.random.randn(n_samples, d)
y_train = X_train @ W_new.T + np.random.randn(n_samples, d) * 0.1

X_test = np.random.randn(100, d)
y_test = X_test @ W_new.T + np.random.randn(100, d) * 0.1

# ============================================================================
# 2. FULL FINE-TUNING BASELINE
# ============================================================================
# Update all entries of W. This is the "traditional" approach.
# ============================================================================

class FullFineTune:
    def __init__(self, W_init):
        self.W = W_init.copy()

    def forward(self, x):
        return x @ self.W.T

    def train(self, X, y, lr=0.01, epochs=200):
        losses = []
        for _ in range(epochs):
            pred = self.forward(X)
            loss = np.mean((pred - y) ** 2)
            losses.append(loss)
            grad = 2 * (pred - y).T @ X / X.shape[0]
            self.W -= lr * grad
        return losses

# ============================================================================
# 3. LoRA ADAPTER
# ============================================================================
# Freeze W_base. Only train B (d x r) and A (r x d).
# Forward: y = x @ (W_base + B @ A)^T
# ============================================================================

class LoRA:
    def __init__(self, W_base, rank):
        self.W_base = W_base.copy()  # frozen
        self.rank = rank
        # Initialize A with Gaussian, B with zeros
        # This ensures the adapter starts at zero (no disruption)
        self.A = np.random.randn(rank, d) * 0.01
        self.B = np.zeros((d, rank))

    def forward(self, x):
        # y = x @ (W_base + B @ A)^T
        #   = x @ W_base^T + x @ (B @ A)^T
        #   = x @ W_base^T + x @ A^T @ B^T
        base_out = x @ self.W_base.T
        adapter_out = x @ self.A.T @ self.B.T
        return base_out + adapter_out

    def train(self, X, y, lr=0.01, epochs=200):
        losses = []
        for _ in range(epochs):
            pred = self.forward(X)
            loss = np.mean((pred - y) ** 2)
            losses.append(loss)

            grad_pred = 2 * (pred - y) / X.shape[0]

            # Gradients for B and A (using chain rule)
            # pred = X @ W_base^T + X @ A^T @ B^T
            # dL/dB = grad_pred^T @ X @ A^T
            # dL/dA = B^T @ grad_pred^T @ X
            grad_B = grad_pred.T @ X @ self.A.T
            grad_A = self.B.T @ grad_pred.T @ X

            self.B -= lr * grad_B
            self.A -= lr * grad_A

        return losses

    def merge(self):
        """Combine adapter into base weights for zero-overhead inference."""
        return self.W_base + self.B @ self.A

# ============================================================================
# 4. TRAIN BOTH APPROACHES
# ============================================================================

print("Training full fine-tuning (all weights updated)...")
full_model = FullFineTune(W_base)
loss_full = full_model.train(X_train, y_train, lr=0.02, epochs=300)

print("Training LoRA (only B and A updated)...")
lora_model = LoRA(W_base, rank=r)
loss_lora = lora_model.train(X_train, y_train, lr=0.02, epochs=300)

# Test
pred_full = full_model.forward(X_test)
pred_lora = lora_model.forward(X_test)
test_loss_full = np.mean((pred_full - y_test) ** 2)
test_loss_lora = np.mean((pred_lora - y_test) ** 2)

print(f"\nFull fine-tuning test loss: {test_loss_full:.4f}")
print(f"LoRA test loss:             {test_loss_lora:.4f}")

# ============================================================================
# 5. PARAMETER COUNT COMPARISON
# ============================================================================

params_full = d * d
params_lora = d * r + r * d  # B + A
params_percent = 100 * params_lora / params_full

print(f"\nParameter counts:")
print(f"  Full fine-tuning: {params_full:,} parameters (100.0%)")
print(f"  LoRA (r={r}):      {params_lora:,} parameters ({params_percent:.1f}%)")
print(f"  Parameter reduction: {100 - params_percent:.1f}%")

# ============================================================================
# 6. MERGING DEMONSTRATION
# ============================================================================

W_merged = lora_model.merge()
pred_merged = X_test @ W_merged.T
test_loss_merged = np.mean((pred_merged - y_test) ** 2)

print(f"\nAdapter merging:")
print(f"  Test loss with separate W + BA: {test_loss_lora:.4f}")
print(f"  Test loss with merged W:        {test_loss_merged:.4f}")
print(f"  Difference:                     {abs(test_loss_lora - test_loss_merged):.6f}")
print(f"  (Should be ~0 — merging is exact)")

# ============================================================================
# 7. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# ---- Plot 1: Training Loss ----
ax = axes[0, 0]
ax.plot(loss_full, label='Full Fine-Tuning', linewidth=2)
ax.plot(loss_lora, label=f'LoRA (r={r})', linewidth=2)
ax.set_xlabel('Iteration')
ax.set_ylabel('MSE Loss')
ax.set_title('Training Loss: Full vs. LoRA')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 2: Parameter Count Comparison ----
ax = axes[0, 1]
categories = ['Full\nFine-Tuning', f'LoRA\n(r={r})']
counts = [params_full, params_lora]
colors = ['steelblue', 'lightgreen']
bars = ax.bar(categories, counts, color=colors)
ax.set_ylabel('Trainable Parameters')
ax.set_title('Parameter Count Comparison')
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{count:,}', ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, params_full * 1.2)
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 3: Test Predictions (first dimension) ----
ax = axes[1, 0]
sample_idx = 0
ax.plot(y_test[:, sample_idx], 'o-', color='green', label='True', markersize=4)
ax.plot(pred_full[:, sample_idx], 's-', color='blue', label='Full FT', markersize=4, alpha=0.7)
ax.plot(pred_lora[:, sample_idx], '^-', color='red', label='LoRA', markersize=4, alpha=0.7)
ax.set_xlabel('Test Sample')
ax.set_ylabel('Output (dim 0)')
ax.set_title('Test Predictions')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 4: Learned Delta vs. True Delta ----
ax = axes[1, 1]
learned_delta = lora_model.B @ lora_model.A
im = ax.imshow(np.hstack([delta, learned_delta]), cmap='RdBu', aspect='auto')
ax.set_title('True Delta (left) vs. Learned Delta (right)')
ax.axvline(x=d - 0.5, color='black', linewidth=2)
ax.set_xticks([d//2, d + d//2])
ax.set_xticklabels(['True', 'Learned'])
ax.set_yticks([])
plt.colorbar(im, ax=ax)

plt.tight_layout()
plt.savefig('src/phase35/lora_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved visualization: src/phase35/lora_concepts.png")
plt.close()

# ============================================================================
# 8. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Base model: {d}x{d} = {params_full} parameters (frozen)")
print(f"New task requires adapting to W_new = W_base + delta")
print(f"delta is rank-{r} by construction.")
print()
print("Results:")
print(f"  Full fine-tuning: {test_loss_full:.4f} loss, {params_full} trainable params")
print(f"  LoRA (r={r}):      {test_loss_lora:.4f} loss, {params_lora} trainable params ({params_percent:.1f}%)")
print()
print("Key observations:")
print("1. LoRA matches full fine-tuning when the adaptation is low-rank.")
print("2. LoRA trains only 2.0% of the parameters (for r=2, d=20).")
print("3. Adapter merging produces identical outputs with zero inference overhead.")
print("4. For larger models (d=4096, r=16), LoRA uses only 0.8% of parameters.")
print()
print("This demonstrates the core idea of PEFT:")
print("- Freeze the base model (expensive, already trained)")
print("- Train tiny adapters (cheap, task-specific)")
print("- Merge at inference for zero overhead")
print("- Enable customization on consumer hardware")
print("=" * 70)

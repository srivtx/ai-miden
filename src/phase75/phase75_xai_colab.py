#!/usr/bin/env python3
"""
================================================================================
Phase 75 (Colab T4): Explainable AI — Real-Workflow with PyTorch
================================================================================

Copy-paste into Google Colab with T4 GPU.

This script trains a small PyTorch MLP on synthetic tabular data, then
applies three gradient-based explanation methods that are standard in
production XAI pipelines:

  1. Vanilla Saliency (input gradient)
  2. SmoothGrad (average gradients over noisy samples)
  3. Integrated Gradients (accumulate gradients along a straight-line path
     from a baseline to the input)

It also builds a tiny Transformer and visualizes multi-head attention.

Every block explains WHY the method works and what its limitations are.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==============================================================================
# 1. SYNTHETIC DATA (same generative story as NumPy version)
# ==============================================================================
# WHY: We want identical data so the two scripts are comparable.

torch.manual_seed(75)
np.random.seed(75)

N_SAMPLES = 800
N_FEATURES = 4

X_np = np.random.randn(N_SAMPLES, N_FEATURES).astype(np.float32)
logits_true = 2.0 * X_np[:, 0] - 1.5 * X_np[:, 1]
y_np = (logits_true > 0).astype(np.float32).reshape(-1, 1)

X = torch.from_numpy(X_np).to(device)
y = torch.from_numpy(y_np).to(device)

split = int(0.8 * N_SAMPLES)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

baseline = X_train.mean(dim=0, keepdim=True)

# ==============================================================================
# 2. SMALL MLP IN PYTORCH
# ==============================================================================
# WHY: PyTorch autograd makes gradient-based explanations trivial. We just
# call .backward() on the output.

class TinyMLP(nn.Module):
    def __init__(self, in_dim, hidden_dim=8):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        h = torch.tanh(self.fc1(x))
        return torch.sigmoid(self.fc2(h))

model = TinyMLP(N_FEATURES, hidden_dim=8).to(device)
optimizer = torch.optim.SGD(model.parameters(), lr=0.5)
loss_fn = nn.BCELoss()

# Train
for epoch in range(600):
    optimizer.zero_grad()
    out = model(X_train)
    loss = loss_fn(out, y_train)
    loss.backward()
    optimizer.step()
    if epoch % 100 == 0:
        print(f"Epoch {epoch:4d} | Loss: {loss.item():.4f}")

with torch.no_grad():
    test_acc = ((model(X_test) > 0.5).float() == y_test).float().mean().item()
print(f"\nTest Accuracy: {test_acc:.2%}")

# ==============================================================================
# 3. VANILLA SALIENCY
# ==============================================================================
# WHY: The gradient of the output w.r.t. the input tells us which input
# dimensions, if changed infinitesimally, would change the prediction most.
# It is fast but noisy: gradients can saturate or be misleading at flat
# regions of the activation function.

model.eval()
x_inst = X_test[0:1].clone().requires_grad_(True)
out = model(x_inst)
out.backward()
saliency = x_inst.grad.abs().cpu().numpy().flatten()
print(f"\nVanilla Saliency: {saliency.round(4)}")

# ==============================================================================
# 4. SMOOTHGRAD
# ==============================================================================
# WHY: Vanilla saliency is sensitive to small input perturbations.
# SmoothGrad averages saliency over many noisy copies of the input.
# The idea: if a feature is truly important, its gradient should stay large
# even when the input is slightly jittered.

N_NOISE = 100
NOISE_STD = 0.2

smooth_grad = np.zeros(N_FEATURES)
for _ in range(N_NOISE):
    x_noisy = x_inst.detach() + torch.randn_like(x_inst) * NOISE_STD
    x_noisy.requires_grad_(True)
    out_n = model(x_noisy)
    out_n.backward()
    smooth_grad += x_noisy.grad.abs().cpu().numpy().flatten()

smooth_grad /= N_NOISE
print(f"SmoothGrad:       {smooth_grad.round(4)}")

# ==============================================================================
# 5. INTEGRATED GRADIENTS
# ==============================================================================
# WHY: Saliency only looks at the gradient at the input point. Integrated
# Gradients (IG) accumulate gradients along a straight-line path from a
# baseline (e.g., zeros or the mean) to the input. This satisfies two
# desirable axioms: sensitivity and implementation invariance.
# Formula: (x - x_baseline) * integral_0^1 grad(F(x_baseline + alpha*(x-x_baseline))) d_alpha

N_STEPS = 50

x_base = baseline.clone()
x_diff = x_inst.detach() - x_base

integrated = torch.zeros_like(x_inst)
for i in range(N_STEPS):
    alpha = (i + 1) / N_STEPS
    x_step = x_base + alpha * x_diff
    x_step.requires_grad_(True)
    out_step = model(x_step)
    out_step.backward()
    integrated += x_step.grad

integrated *= x_diff / N_STEPS
ig_vals = integrated.abs().cpu().numpy().flatten()
print(f"Integrated Grad:  {ig_vals.round(4)}")

# ==============================================================================
# 6. TINY TRANSFORMER + ATTENTION VISUALIZATION
# ==============================================================================
# WHY: Transformers use multi-head self-attention. Visualizing the attention
# weights is the most common way people try to explain them. We build a
# minimal 2-head, 1-layer encoder so the matrices are small and inspectable.

class TinyTransformer(nn.Module):
    def __init__(self, d_model=4, n_heads=2):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.W_qkv = nn.Linear(d_model, d_model * 3)
        self.W_out = nn.Linear(d_model, d_model)

    def forward(self, x):
        # x: (batch, seq, d_model)
        B, S, D = x.shape
        qkv = self.W_qkv(x)  # (B, S, 3*D)
        q, k, v = qkv.chunk(3, dim=-1)
        # Split into heads: (B, H, S, d_k)
        q = q.view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        k = k.view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        v = v.view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        scores = torch.matmul(q, k.transpose(-2, -1)) / np.sqrt(self.d_k)
        attn = F.softmax(scores, dim=-1)  # (B, H, S, S)
        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(B, S, D)
        return self.W_out(out), attn

trans = TinyTransformer(d_model=4, n_heads=2).to(device)
# Fake 4-token sequence
tokens = torch.randn(1, 4, 4).to(device)
with torch.no_grad():
    _, attn_weights = trans(tokens)  # (1, 2, 4, 4)

attn_weights = attn_weights[0].cpu().numpy()  # (2, 4, 4)

# ==============================================================================
# 7. PLOTTING
# ==============================================================================
fig, axes = plt.subplots(2, 3, figsize=(14, 9))

# -- Saliency --
ax = axes[0, 0]
ax.bar(range(N_FEATURES), saliency, color=['#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c'])
ax.set_xticks(range(N_FEATURES))
ax.set_xticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('Vanilla Saliency')
ax.set_ylabel('Abs Gradient')

# -- SmoothGrad --
ax = axes[0, 1]
ax.bar(range(N_FEATURES), smooth_grad, color=['#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c'])
ax.set_xticks(range(N_FEATURES))
ax.set_xticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('SmoothGrad')
ax.set_ylabel('Avg Abs Gradient')

# -- Integrated Gradients --
ax = axes[0, 2]
ax.bar(range(N_FEATURES), ig_vals, color=['#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c'])
ax.set_xticks(range(N_FEATURES))
ax.set_xticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('Integrated Gradients')
ax.set_ylabel('Attribution')

# -- Attention Head 0 --
ax = axes[1, 0]
im = ax.imshow(attn_weights[0], cmap='viridis', vmin=0, vmax=1)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(['T0', 'T1', 'T2', 'T3'])
ax.set_yticklabels(['T0', 'T1', 'T2', 'T3'])
ax.set_title('Attention Head 0')
ax.set_xlabel('Key')
ax.set_ylabel('Query')
for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{attn_weights[0, i, j]:.2f}', ha='center', va='center', color='white', fontsize=9)
fig.colorbar(im, ax=ax, fraction=0.046)

# -- Attention Head 1 --
ax = axes[1, 1]
im = ax.imshow(attn_weights[1], cmap='viridis', vmin=0, vmax=1)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(['T0', 'T1', 'T2', 'T3'])
ax.set_yticklabels(['T0', 'T1', 'T2', 'T3'])
ax.set_title('Attention Head 1')
ax.set_xlabel('Key')
ax.set_ylabel('Query')
for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{attn_weights[1, i, j]:.2f}', ha='center', va='center', color='white', fontsize=9)
fig.colorbar(im, ax=ax, fraction=0.046)

# -- Comparison of three gradient methods --
ax = axes[1, 2]
x_pos = np.arange(N_FEATURES)
width = 0.25
ax.bar(x_pos - width, saliency, width, label='Saliency', color='#3498db')
ax.bar(x_pos, smooth_grad, width, label='SmoothGrad', color='#2ecc71')
ax.bar(x_pos + width, ig_vals, width, label='Int. Gradients', color='#9b59b6')
ax.set_xticks(x_pos)
ax.set_xticklabels([f'F{i}' for i in range(N_FEATURES)])
ax.set_title('Method Comparison')
ax.set_ylabel('Attribution Magnitude')
ax.legend()

fig.suptitle('Phase 75 (Colab): XAI with PyTorch — Gradient Methods & Attention', fontsize=14, y=1.02)
plt.tight_layout()
out_path = 'src/phase75/xai_colab.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nSaved plot to {out_path}")

# Phase 45: Quantization & GGUF — Colab T4 PyTorch Version
# ============================================================================
# Run this in Google Colab with T4 GPU runtime.
# Demonstrates INT8 and INT4 quantization on a realistic model,
# plus GPTQ-style error compensation and AWQ activation-aware protection.
#
# Concepts:
#   - Uniform and per-channel quantization
#   - GPTQ layer-wise error compensation
#   - AWQ activation-aware weight protection
#   - Block-quantized storage format
# ============================================================================

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# =============================================================================
# SECTION 1: MODEL AND DATA
# =============================================================================

class MLP(nn.Module):
    def __init__(self, input_dim=64, hidden_dim=128, output_dim=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.net(x)

def generate_data(n=1000, dim=64):
    X = torch.randn(n, dim)
    w = torch.zeros(dim)
    w[[5, 15, 25, 35, 45, 55]] = torch.tensor([2.0, -1.5, 1.0, -2.5, 1.5, -1.0])
    logits = X @ w + torch.randn(n) * 0.3
    y = (logits > 0).long()
    return X.to(device), y.to(device)

# =============================================================================
# SECTION 2: QUANTIZATION FUNCTIONS
# =============================================================================

def quantize_uniform(w, n_bits=8):
    """Quantize tensor to n_bits with per-tensor scale and zero-point."""
    w_np = w.detach().cpu().numpy()
    w_min = w_np.min()
    w_max = w_np.max()
    qmax = (2 ** n_bits) - 1
    scale = (w_max - w_min) / qmax
    if scale == 0:
        scale = 1e-8
    zp = int(np.round(-w_min / scale))
    q = np.round(w_np / scale + zp).astype(int)
    q = np.clip(q, 0, qmax)
    return q, scale, zp, w.shape

def dequantize_uniform(q, scale, zp, shape):
    w = (q.astype(float) - zp) * scale
    return torch.tensor(w.reshape(shape), dtype=torch.float32, device=device)

def quantize_per_channel(w, n_bits=8):
    """Quantize each output channel independently."""
    w_np = w.detach().cpu().numpy()
    out_dim = w_np.shape[0]
    qmax = (2 ** n_bits) - 1
    q = np.zeros_like(w_np, dtype=int)
    scales = []
    zps = []
    for i in range(out_dim):
        w_min = w_np[i].min()
        w_max = w_np[i].max()
        scale = (w_max - w_min) / qmax
        if scale == 0:
            scale = 1e-8
        zp = int(np.round(-w_min / scale))
        q[i] = np.clip(np.round(w_np[i] / scale + zp), 0, qmax).astype(int)
        scales.append(scale)
        zps.append(zp)
    return q, scales, zps, w.shape

def dequantize_per_channel(q, scales, zps, shape):
    w = np.zeros_like(q, dtype=float)
    for i in range(q.shape[0]):
        w[i] = (q[i].astype(float) - zps[i]) * scales[i]
    return torch.tensor(w.reshape(shape), dtype=torch.float32, device=device)

def gptq_style_quantize(w, n_bits=4):
    """
    Simplified GPTQ: quantize weights sequentially with error compensation.
    """
    w_np = w.detach().cpu().numpy().copy()
    out_dim, in_dim = w_np.shape
    qmax = (2 ** n_bits) - 1
    q = np.zeros_like(w_np, dtype=int)
    scales = []
    zps = []

    for i in range(out_dim):
        w_min = w_np[i].min()
        w_max = w_np[i].max()
        scale = (w_max - w_min) / qmax
        if scale == 0:
            scale = 1e-8
        zp = int(np.round(-w_min / scale))

        for j in range(in_dim):
            q_ij = int(np.clip(np.round(w_np[i, j] / scale + zp), 0, qmax))
            error = w_np[i, j] - (q_ij - zp) * scale
            q[i, j] = q_ij
            # Compensate error to remaining weights in this row
            if j + 1 < in_dim:
                w_np[i, j+1:] -= error / (in_dim - j - 1)
        scales.append(scale)
        zps.append(zp)
    return q, scales, zps, w.shape

def awq_quantize(w, activations, n_bits=4, protect_ratio=0.1):
    """Protect top protect_ratio weights by activation importance."""
    w_np = w.detach().cpu().numpy().copy()
    act_np = activations.detach().cpu().numpy()
    mean_act = np.abs(act_np).mean(axis=0)
    importance = np.abs(w_np) * mean_act[:, np.newaxis]
    thresh = np.percentile(importance, 100 * (1 - protect_ratio))
    protect_mask = importance >= thresh

    # Quantize non-protected weights per row
    q = np.zeros_like(w_np, dtype=int)
    qmax = (2 ** n_bits) - 1
    scales = []
    zps = []
    for i in range(w_np.shape[0]):
        row = w_np[i].copy()
        mask = protect_mask[i]
        unprotected = row[~mask]
        if len(unprotected) > 0:
            w_min = unprotected.min()
            w_max = unprotected.max()
            scale = (w_max - w_min) / qmax
            if scale == 0:
                scale = 1e-8
            zp = int(np.round(-w_min / scale))
            q_row = np.clip(np.round(row / scale + zp), 0, qmax).astype(int)
            q[i] = q_row
            # Restore protected weights
            row_q = (q_row.astype(float) - zp) * scale
            row_q[mask] = row[mask]
            w_np[i] = row_q
        else:
            w_np[i] = row
        scales.append(scale if len(unprotected) > 0 else 1.0)
        zps.append(zp if len(unprotected) > 0 else 0)
    return torch.tensor(w_np, dtype=torch.float32, device=device), scales, zps

# =============================================================================
# SECTION 3: EVALUATION
# =============================================================================

def evaluate(model, X, y):
    with torch.no_grad():
        logits = model(X)
        preds = torch.argmax(logits, dim=1)
        return (preds == y).float().mean().item()

# =============================================================================
# SECTION 4: MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*60)
    print("Phase 45 Colab: Quantization & GGUF")
    print("="*60)

    X_train, y_train = generate_data(2000, 64)
    X_test, y_test = generate_data(500, 64)

    # Train model
    model = MLP(64, 128, 2).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    for epoch in range(30):
        logits = model(X_train)
        loss = torch.nn.functional.cross_entropy(logits, y_train)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: loss={loss.item():.3f}")

    acc_fp32 = evaluate(model, X_test, y_test)
    fp32_params = sum(p.numel() for p in model.parameters())
    print(f"\nFP32 accuracy: {acc_fp32:.2%}, params: {fp32_params:,}")

    # Get activations for AWQ
    with torch.no_grad():
        h1 = model.net[0](X_train)
        a1 = model.net[1](h1)

    # INT8 uniform
    w1_q, s1, zp1, sh1 = quantize_uniform(model.net[0].weight, 8)
    w2_q, s2, zp2, sh2 = quantize_uniform(model.net[2].weight, 8)
    w3_q, s3, zp3, sh3 = quantize_uniform(model.net[4].weight, 8)
    model_int8 = MLP(64, 128, 2).to(device)
    model_int8.net[0].weight.data = dequantize_uniform(w1_q, s1, zp1, sh1)
    model_int8.net[2].weight.data = dequantize_uniform(w2_q, s2, zp2, sh2)
    model_int8.net[4].weight.data = dequantize_uniform(w3_q, s3, zp3, sh3)
    acc_int8 = evaluate(model_int8, X_test, y_test)
    print(f"INT8 uniform:  {acc_int8:.2%}")

    # INT8 per-channel
    w1_pc, s1_pc, zp1_pc, sh1 = quantize_per_channel(model.net[0].weight, 8)
    w2_pc, s2_pc, zp2_pc, sh2 = quantize_per_channel(model.net[2].weight, 8)
    w3_pc, s3_pc, zp3_pc, sh3 = quantize_per_channel(model.net[4].weight, 8)
    model_pc = MLP(64, 128, 2).to(device)
    model_pc.net[0].weight.data = dequantize_per_channel(w1_pc, s1_pc, zp1_pc, sh1)
    model_pc.net[2].weight.data = dequantize_per_channel(w2_pc, s2_pc, zp2_pc, sh2)
    model_pc.net[4].weight.data = dequantize_per_channel(w3_pc, s3_pc, zp3_pc, sh3)
    acc_pc = evaluate(model_pc, X_test, y_test)
    print(f"INT8 per-chan: {acc_pc:.2%}")

    # GPTQ-style
    w1_gptq, s1_g, zp1_g, sh1 = gptq_style_quantize(model.net[0].weight, 4)
    w2_gptq, s2_g, zp2_g, sh2 = gptq_style_quantize(model.net[2].weight, 4)
    w3_gptq, s3_g, zp3_g, sh3 = gptq_style_quantize(model.net[4].weight, 4)
    model_gptq = MLP(64, 128, 2).to(device)
    model_gptq.net[0].weight.data = dequantize_per_channel(w1_gptq, s1_g, zp1_g, sh1)
    model_gptq.net[2].weight.data = dequantize_per_channel(w2_gptq, s2_g, zp2_g, sh2)
    model_gptq.net[4].weight.data = dequantize_per_channel(w3_gptq, s3_g, zp3_g, sh3)
    acc_gptq = evaluate(model_gptq, X_test, y_test)
    print(f"INT4 GPTQ:     {acc_gptq:.2%}")

    # AWQ-style
    w1_awq, _, _ = awq_quantize(model.net[0].weight, X_train, 4, 0.1)
    w2_awq, _, _ = awq_quantize(model.net[2].weight, a1, 4, 0.1)
    w3_awq, _, _ = awq_quantize(model.net[4].weight, a1, 4, 0.1)
    model_awq = MLP(64, 128, 2).to(device)
    model_awq.net[0].weight.data = w1_awq
    model_awq.net[2].weight.data = w2_awq
    model_awq.net[4].weight.data = w3_awq
    acc_awq = evaluate(model_awq, X_test, y_test)
    print(f"INT4 AWQ:      {acc_awq:.2%}")

    # Plot
    names = ['FP32', 'INT8\nUniform', 'INT8\nPer-Chan', 'INT4\nGPTQ', 'INT4\nAWQ']
    accs = [acc_fp32, acc_int8, acc_pc, acc_gptq, acc_awq]
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#2ecc71', '#3498db', '#2980b9', '#e74c3c', '#9b59b6']
    bars = ax.bar(names, accs, color=colors)
    ax.set_ylabel('Accuracy')
    ax.set_title('Quantization Methods Comparison')
    ax.set_ylim(0.5, 1.0)
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{acc:.1%}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig('phase45_quantization.png', dpi=150)
    print("\nSaved plot to phase45_quantization.png")

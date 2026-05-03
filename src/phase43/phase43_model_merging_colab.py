# Phase 43: Model Merging & Ensembles — Colab T4 PyTorch Version
# ============================================================================
# Run this in Google Colab with T4 GPU runtime.
# Demonstrates model merging on realistic neural networks with multiple tasks.
#
# Concepts:
#   - Simple weight averaging
#   - Task arithmetic
#   - SLERP (spherical linear interpolation)
#   - TIES-Merging (Trim, Elect, Sign, Merge)
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# =============================================================================
# SECTION 1: DATA AND TASKS
# =============================================================================

def generate_task_data(n_samples=1000, task_id=0, input_dim=32):
    """Generate synthetic classification tasks with different feature subsets."""
    X = torch.randn(n_samples, input_dim)
    # Each task uses a different 4-feature subset
    start_feat = task_id * 4
    logits = torch.sum(X[:, start_feat:start_feat+4] * torch.tensor([1.5, -1.0, 2.0, -0.5]), dim=1)
    y = torch.zeros(n_samples, dtype=torch.long)
    y[logits > 0.3] = 1
    y[logits < -0.3] = 2
    return X.to(device), y.to(device)

# =============================================================================
# SECTION 2: NEURAL NETWORK MODEL
# =============================================================================

class MLP(nn.Module):
    def __init__(self, input_dim=32, hidden_dim=64, output_dim=3):
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

    def get_param_vector(self):
        return torch.cat([p.flatten() for p in self.parameters()]).detach().cpu().numpy()

    def set_param_vector(self, vec):
        vec = torch.tensor(vec, dtype=torch.float32, device=device)
        offset = 0
        for p in self.parameters():
            numel = p.numel()
            p.data.copy_(vec[offset:offset+numel].view_as(p))
            offset += numel

def train_model(model, X, y, epochs=30, lr=0.01, batch_size=64):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        perm = torch.randperm(len(y))
        for i in range(0, len(y), batch_size):
            idx = perm[i:i+batch_size]
            logits = model(X[idx])
            loss = F.cross_entropy(logits, y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()

def evaluate(model, X, y):
    with torch.no_grad():
        logits = model(X)
        preds = torch.argmax(logits, dim=1)
        return (preds == y).float().mean().item()

# =============================================================================
# SECTION 3: MERGING FUNCTIONS
# =============================================================================

def simple_average_merge(models):
    merged = deepcopy(models[0])
    with torch.no_grad():
        for p_merged, *p_others in zip(merged.parameters(), *[m.parameters() for m in models[1:]]):
            p_merged.copy_(sum([p_merged] + list(p_others)) / len(models))
    return merged

def task_arithmetic_merge(base, models, lambdas):
    merged = deepcopy(base)
    with torch.no_grad():
        for p_merged, p_base in zip(merged.parameters(), base.parameters()):
            delta = torch.zeros_like(p_merged)
            for m, lam in zip(models, lambdas):
                for p_m, p_b in zip(m.parameters(), base.parameters()):
                    if p_m is m.parameters():
                        delta += lam * (p_m - p_b)
            # Actually we need per-parameter deltas
            pass
    # Simpler: compute task vectors manually
    merged = deepcopy(base)
    base_vec = base.get_param_vector()
    merged_vec = base_vec.copy()
    for m, lam in zip(models, lambdas):
        delta = m.get_param_vector() - base_vec
        merged_vec += lam * delta
    merged.set_param_vector(merged_vec)
    return merged

def slerp_merge(model_a, model_b, t=0.5):
    a_vec = model_a.get_param_vector()
    b_vec = model_b.get_param_vector()
    dot = np.dot(a_vec, b_vec)
    norm_a = np.linalg.norm(a_vec)
    norm_b = np.linalg.norm(b_vec)
    cos_theta = dot / (norm_a * norm_b + 1e-10)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)
    if theta < 1e-6:
        return deepcopy(model_a)
    sin_theta = np.sin(theta)
    w1 = np.sin((1 - t) * theta) / sin_theta
    w2 = np.sin(t * theta) / sin_theta
    merged_vec = w1 * a_vec + w2 * b_vec
    merged = deepcopy(model_a)
    merged.set_param_vector(merged_vec)
    return merged

def ties_merge(base, models, trim_pct=0.2):
    """Simplified TIES: trim bottom trim_pct of deltas by magnitude."""
    merged = deepcopy(base)
    base_vec = base.get_param_vector()
    n_models = len(models)
    n_params = len(base_vec)

    deltas = [m.get_param_vector() - base_vec for m in models]

    # Flatten and trim
    flat_deltas = np.stack(deltas, axis=0)  # (n_models, n_params)

    # Trim: zero out smallest magnitude changes per model
    for i in range(n_models):
        thresh = np.percentile(np.abs(flat_deltas[i]), trim_pct * 100)
        flat_deltas[i][np.abs(flat_deltas[i]) < thresh] = 0

    # Elect majority sign
    merged_delta = np.zeros(n_params)
    for j in range(n_params):
        signs = []
        vals = []
        for i in range(n_models):
            if flat_deltas[i, j] != 0:
                signs.append(np.sign(flat_deltas[i, j]))
                vals.append(flat_deltas[i, j])
        if len(signs) == 0:
            continue
        majority = np.sign(np.sum(signs))
        if majority == 0:
            majority = 1
        elected = [v for s, v in zip(signs, vals) if s == majority]
        if len(elected) > 0:
            merged_delta[j] = np.mean(elected)

    merged_vec = base_vec + merged_delta
    merged.set_param_vector(merged_vec)
    return merged

# =============================================================================
# SECTION 4: MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*60)
    print("Phase 43 Colab: Model Merging & Ensembles")
    print("="*60)

    input_dim = 32
    X_tasks = []
    y_tasks = []
    for t in range(3):
        X, y = generate_task_data(1000, t, input_dim)
        X_tasks.append(X)
        y_tasks.append(y)

    # Base model
    print("\nTraining base model on mixed data...")
    base = MLP(input_dim).to(device)
    X_all = torch.cat(X_tasks)
    y_all = torch.cat(y_tasks)
    train_model(base, X_all, y_all, epochs=20, lr=0.01)
    base_accs = [evaluate(base, X_tasks[t], y_tasks[t]) for t in range(3)]
    print(f"Base model: {base_accs}")

    # Fine-tune 3 models
    fine_tuned = []
    for t in range(3):
        m = deepcopy(base)
        print(f"Fine-tuning model {t} on task {t}...")
        train_model(m, X_tasks[t], y_tasks[t], epochs=15, lr=0.005)
        fine_tuned.append(m)
        accs = [evaluate(m, X_tasks[i], y_tasks[i]) for i in range(3)]
        print(f"  Accuracies: {accs}")

    # Merge methods
    print("\n" + "="*60)
    print("MERGING RESULTS")
    print("="*60)

    methods = {}
    methods['Simple Average'] = simple_average_merge(fine_tuned)
    methods['Task Arithmetic'] = task_arithmetic_merge(base, fine_tuned, [0.4, 0.4, 0.4])
    slerp_01 = slerp_merge(fine_tuned[0], fine_tuned[1], 0.5)
    methods['SLERP'] = slerp_merge(slerp_01, fine_tuned[2], 0.33)
    methods['TIES-Merging'] = ties_merge(base, fine_tuned, trim_pct=0.3)

    for name, model in methods.items():
        accs = [evaluate(model, X_tasks[t], y_tasks[t]) for t in range(3)]
        print(f"{name:20s} | Mean={np.mean(accs):.2%} | {accs}")

    # Plot
    names = list(methods.keys())
    means = [np.mean([evaluate(methods[n], X_tasks[t], y_tasks[t]) for t in range(3)]) for n in names]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, means, color=['#3498db', '#2ecc71', '#e74c3c', '#9b59b6'])
    ax.set_ylabel('Mean Accuracy')
    ax.set_title('Model Merging: Multi-Task Performance')
    ax.set_ylim(0, 1.0)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h:.1%}', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig('phase43_model_merging.png', dpi=150)
    print("\nSaved plot to phase43_model_merging.png")

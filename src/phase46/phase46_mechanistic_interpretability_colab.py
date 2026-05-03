# Phase 46: Mechanistic Interpretability — Colab T4 PyTorch Version
# ============================================================================
# Run this in Google Colab with T4 GPU runtime.
# Demonstrates activation patching, probing, and sparse autoencoders
# on a realistic model.
#
# Concepts:
#   - Activation visualization
#   - Activation patching (causal intervention)
#   - Linear probing of hidden states
#   - Sparse autoencoders on activations
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
    def __init__(self, input_dim=16, hidden_dim=32, output_dim=4):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x, return_hidden=False):
        h1 = torch.tanh(self.fc1(x))
        h2 = torch.tanh(self.fc2(h1))
        out = self.fc3(h2)
        if return_hidden:
            return out, h1, h2
        return out

# 4 distinct 16-dim patterns
patterns = torch.tensor([
    [1,1,1,1, 0,0,0,0, 0,0,0,0, 0,0,0,0],  # Pattern 0
    [0,0,0,0, 1,1,1,1, 0,0,0,0, 0,0,0,0],  # Pattern 1
    [0,0,0,0, 0,0,0,0, 1,1,1,1, 0,0,0,0],  # Pattern 2
    [0,0,0,0, 0,0,0,0, 0,0,0,0, 1,1,1,1],  # Pattern 3
], dtype=torch.float32, device=device)

def generate_data(n_per_class=200):
    X, y = [], []
    for i in range(4):
        for _ in range(n_per_class):
            noise = torch.randn(16, device=device) * 0.1
            X.append(patterns[i] + noise)
            y.append(i)
    return torch.stack(X), torch.tensor(y, device=device)

# =============================================================================
# SECTION 2: TRAIN MODEL
# =============================================================================

X_train, y_train = generate_data(200)
X_test, y_test = generate_data(100)

model = MLP(16, 32, 4).to(device)
opt = torch.optim.Adam(model.parameters(), lr=0.01)
for epoch in range(50):
    logits = model(X_train)
    loss = nn.functional.cross_entropy(logits, y_train)
    opt.zero_grad()
    loss.backward()
    opt.step()
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: loss={loss.item():.3f}")

with torch.no_grad():
    acc = (model(X_test).argmax(1) == y_test).float().mean().item()
print(f"\nTest accuracy: {acc:.1%}")

# =============================================================================
# SECTION 3: ACTIVATION VISUALIZATION AND PATCHING
# =============================================================================

print("\n--- Activation Patching ---")
with torch.no_grad():
    _, h1_clean, h2_clean = model(patterns[0].unsqueeze(0), return_hidden=True)
    _, h1_corrupt, h2_corrupt = model(patterns[1].unsqueeze(0), return_hidden=True)

print(f"Clean (pat0):   h2 = {h2_clean[0,:4].cpu().numpy().round(2)}")
print(f"Corrupt (pat1): h2 = {h2_corrupt[0,:4].cpu().numpy().round(2)}")

# Patch first 4 neurons of h2 from clean into corrupt
h2_patched = h2_corrupt.clone()
h2_patched[0, :4] = h2_clean[0, :4]
logits_patched = model.fc3(h2_patched)
print(f"Patched h2[:4]: pred = {logits_patched.argmax(1).item()}")

# =============================================================================
# SECTION 4: LINEAR PROBE
# =============================================================================

print("\n--- Linear Probe on Hidden States ---")
with torch.no_grad():
    _, h1_all, h2_all = model(X_train, return_hidden=True)

# Probe: can we predict the label from h2 with a linear classifier?
probe = nn.Linear(32, 4).to(device)
probe_opt = torch.optim.Adam(probe.parameters(), lr=0.01)
for epoch in range(100):
    logits = probe(h2_all.detach())
    loss = nn.functional.cross_entropy(logits, y_train)
    probe_opt.zero_grad()
    loss.backward()
    probe_opt.step()

with torch.no_grad():
    _, _, h2_test = model(X_test, return_hidden=True)
    probe_acc = (probe(h2_test).argmax(1) == y_test).float().mean().item()
print(f"Linear probe accuracy: {probe_acc:.1%} (information is linearly encoded)")

# =============================================================================
# SECTION 5: SPARSE AUTOENCODER
# =============================================================================

print("\n--- Sparse Autoencoder ---")
class SparseAutoencoder(nn.Module):
    def __init__(self, input_dim=32, feature_dim=128):
        super().__init__()
        self.encoder = nn.Linear(input_dim, feature_dim)
        self.decoder = nn.Linear(feature_dim, input_dim)

    def forward(self, x):
        f = nn.functional.relu(self.encoder(x))
        recon = self.decoder(f)
        return recon, f

sae = SparseAutoencoder(32, 128).to(device)
sae_opt = torch.optim.Adam(sae.parameters(), lr=0.001)
for epoch in range(500):
    recon, f = sae(h2_all.detach())
    recon_loss = ((recon - h2_all.detach()) ** 2).mean()
    sparsity_loss = 0.01 * f.abs().mean()
    loss = recon_loss + sparsity_loss
    sae_opt.zero_grad()
    loss.backward()
    sae_opt.step()
    if epoch % 100 == 0:
        print(f"  SAE epoch {epoch}: recon={recon_loss.item():.4f}, sparsity={sparsity_loss.item():.4f}")

with torch.no_grad():
    _, f_test = sae(h2_test)
    sparsity = (f_test == 0).float().mean().item()
    print(f"Test sparsity: {sparsity:.1%}")

    # Which features fire for each pattern?
    _, f_patterns = sae(model.fc2(torch.tanh(model.fc1(patterns))).tanh())
    for i in range(4):
        top5 = f_patterns[i].topk(5)
        print(f"Pattern {i}: top features {top5.indices.cpu().numpy()} = {top5.values.cpu().numpy().round(3)}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Hidden state PCA-like visualization
h2_np = h2_test.cpu().numpy()
y_np = y_test.cpu().numpy()
for i in range(4):
    mask = y_np == i
    axes[0].scatter(h2_np[mask, 0], h2_np[mask, 1], label=f'Pattern {i}', alpha=0.5)
axes[0].set_xlabel('Hidden Dim 0')
axes[0].set_ylabel('Hidden Dim 1')
axes[0].set_title('Hidden State Clustering')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# SAE feature activity heatmap
f_pat = f_patterns.cpu().numpy()
im = axes[1].imshow(f_pat[:, :16], cmap='YlOrRd', aspect='auto')
axes[1].set_title('SAE Feature Activity (First 16 Features)')
axes[1].set_xlabel('Feature Index')
axes[1].set_ylabel('Pattern')
axes[1].set_yticks(range(4))
plt.colorbar(im, ax=axes[1])

plt.tight_layout()
plt.savefig('phase46_interpretability.png', dpi=150)
print("\nSaved plot to phase46_interpretability.png")

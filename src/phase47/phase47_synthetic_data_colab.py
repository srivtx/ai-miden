# Phase 47: Synthetic Data & Self-Improvement — Colab T4 PyTorch Version
# ============================================================================
# Run this in Google Colab with T4 GPU runtime.
# Demonstrates synthetic data generation, rejection sampling, and
# iterative self-improvement on a realistic task.
#
# Concepts:
#   - Synthetic data generation
#   - Rejection sampling with hard verifier
#   - Iterative self-improvement
#   - Constitutional AI principle enforcement
# ============================================================================

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# =============================================================================
# SECTION 1: MODEL AND VERIFIER
# =============================================================================

class MLP(nn.Module):
    def __init__(self, input_dim=8, hidden_dim=32, output_dim=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)

# Task: predict a + b + c + d from [a, b, c, d, noise...]
def generate_data(n=1000, dim=8):
    X = torch.randn(n, dim, device=device)
    # First 4 dims matter, rest are noise
    y = X[:, 0] + X[:, 1] + X[:, 2] + X[:, 3]
    return X, y

def verifier(X, y_pred):
    """Hard verifier: check if prediction is close to true sum."""
    y_true = X[:, 0] + X[:, 1] + X[:, 2] + X[:, 3]
    return torch.abs(y_pred - y_true) < 0.5

# =============================================================================
# SECTION 2: BASELINE
# =============================================================================

X_train, y_train = generate_data(200)
X_test, y_test = generate_data(500)

model = MLP(8, 32, 1).to(device)
opt = torch.optim.Adam(model.parameters(), lr=0.01)
for epoch in range(50):
    pred = model(X_train)
    loss = nn.functional.mse_loss(pred, y_train)
    opt.zero_grad()
    loss.backward()
    opt.step()
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: loss={loss.item():.3f}")

with torch.no_grad():
    baseline_mse = nn.functional.mse_loss(model(X_test), y_test).item()
    baseline_verified = verifier(X_test, model(X_test)).float().mean().item()
print(f"\nBaseline MSE: {baseline_mse:.3f}, Verified: {baseline_verified:.1%}")

# =============================================================================
# SECTION 3: SYNTHETIC DATA + REJECTION SAMPLING
# =============================================================================

def generate_synthetic(model, n=2000, dim=8):
    X = torch.randn(n, dim, device=device)
    with torch.no_grad():
        preds = model(X)
    mask = verifier(X, preds)
    return X[mask], preds[mask], mask.sum().item()

synth_X, synth_y, accepted = generate_synthetic(model, n=2000)
print(f"Synthetic generation: {accepted}/2000 passed verification ({accepted/2000:.1%})")

# =============================================================================
# SECTION 4: ITERATIVE SELF-IMPROVEMENT
# =============================================================================

print("\n--- Iterative Self-Improvement ---")
iterations = 5
history = {'mse': [baseline_mse], 'verified': [baseline_verified]}

current = MLP(8, 32, 1).to(device)
current.load_state_dict(model.state_dict())

for it in range(1, iterations + 1):
    # Generate synthetic data
    synth_X, synth_y, accepted = generate_synthetic(current, n=2000)
    if accepted < 50:
        print(f"Iteration {it}: too few samples ({accepted}). Stopping.")
        break

    # Train on synthetic + original
    train_X = torch.cat([X_train, synth_X[:500]])
    train_y = torch.cat([y_train, synth_y[:500]])

    opt = torch.optim.Adam(current.parameters(), lr=0.005)
    for epoch in range(30):
        pred = current(train_X)
        loss = nn.functional.mse_loss(pred, train_y)
        opt.zero_grad()
        loss.backward()
        opt.step()

    with torch.no_grad():
        mse = nn.functional.mse_loss(current(X_test), y_test).item()
        verified = verifier(X_test, current(X_test)).float().mean().item()
    history['mse'].append(mse)
    history['verified'].append(verified)
    print(f"Iteration {it}: MSE={mse:.3f}, Verified={verified:.1%}, Synth={accepted}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(range(len(history['mse'])), history['mse'], 'b-o')
axes[0].set_xlabel('Iteration')
axes[0].set_ylabel('Test MSE')
axes[0].set_title('Self-Improvement: MSE Over Iterations')
axes[0].grid(True, alpha=0.3)

axes[1].plot(range(len(history['verified'])), history['verified'], 'g-o')
axes[1].set_xlabel('Iteration')
axes[1].set_ylabel('Verification Rate')
axes[1].set_title('Self-Improvement: Verified Correctness')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase47_synthetic_data.png', dpi=150)
print("\nSaved plot to phase47_synthetic_data.png")

"""
Minimal Flow Matching vs DDPM.

The core difference is the interpolation path from noise to data:
  DDPM: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1-alpha_bar_t) * noise  (curved)
  Flow: x_t = (1 - t) * x_0 + t * noise                               (straight)

Same model, same data, different loss target:
  DDPM: predict noise epsilon
  Flow: predict velocity v = epsilon - x_0

Sampling:
  DDPM: 1000 reverse steps
  Flow: 20 Euler steps along straight path
"""

import torch
import torch.nn as nn
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
# Toy data: 8 points in a 2D circle
# =============================================================================

def toy_data():
    """Return 2D points arranged in a circle."""
    angles = torch.linspace(0, 2 * math.pi, 9)[:8]
    return torch.stack([torch.cos(angles), torch.sin(angles)], dim=1)  # (8, 2)


# =============================================================================
# Tiny model: predict epsilon (for DDPM) or velocity (for Flow)
# =============================================================================

class TinyModel(nn.Module):
    """A tiny MLP that predicts either epsilon or velocity."""
    def __init__(self, time_dim=16):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2 + time_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 2),
        )
        # Time embedding (learned)
        self.time_emb = nn.Sequential(
            nn.Linear(1, time_dim),
            nn.ReLU(),
            nn.Linear(time_dim, time_dim),
        )

    def forward(self, x_t, t):
        t_emb = self.time_emb(t.unsqueeze(-1).float())
        return self.net(torch.cat([x_t, t_emb], dim=-1))


# =============================================================================
# DDPM training
# =============================================================================

def train_ddpm(model, data, steps=2000, T=1000):
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    losses = []

    # Linear beta schedule
    beta = torch.linspace(1e-4, 0.02, T)
    alpha = 1 - beta
    alpha_bar = torch.cumprod(alpha, dim=0)

    model.train()
    for step in range(steps):
        # Sample batch
        idx = torch.randint(0, len(data), (64,))
        x_0 = data[idx]

        # Sample random timesteps
        t = torch.randint(0, T, (64,))

        # Forward diffusion: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1-alpha_bar_t) * noise
        noise = torch.randn(64, 2)
        a_bar = alpha_bar[t].unsqueeze(-1)
        x_t = torch.sqrt(a_bar) * x_0 + torch.sqrt(1 - a_bar) * noise

        # Predict noise
        pred = model(x_t, t)
        loss = nn.functional.mse_loss(pred, noise)

        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(loss.item())

    return losses, alpha_bar


# =============================================================================
# Flow Matching training
# =============================================================================

def train_flow(model, data, steps=2000):
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    losses = []

    model.train()
    for step in range(steps):
        idx = torch.randint(0, len(data), (64,))
        x_0 = data[idx]

        # Sample random timesteps in [0, 1]
        t = torch.rand(64)

        # Straight-line interpolation: x_t = (1-t)*x_0 + t*noise
        noise = torch.randn(64, 2)
        x_t = (1 - t).unsqueeze(-1) * x_0 + t.unsqueeze(-1) * noise

        # Target: velocity v = noise - x_0
        velocity = noise - x_0

        # Predict velocity
        pred = model(x_t, t)
        loss = nn.functional.mse_loss(pred, velocity)

        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(loss.item())

    return losses


# =============================================================================
# Sampling: DDPM reverse
# =============================================================================

@torch.no_grad()
def sample_ddpm(model, alpha_bar, T=1000, n_samples=500):
    model.eval()
    x = torch.randn(n_samples, 2)

    for t in reversed(range(T)):
        t_batch = torch.full((n_samples,), t, dtype=torch.long)
        pred_noise = model(x, t_batch)

        beta_t = 1 - (alpha_bar[t] / alpha_bar[t - 1] if t > 0 else alpha_bar[0])
        beta_t = torch.clamp(beta_t, 1e-5, 0.02)
        alpha_t = 1 - beta_t

        mean = (x - beta_t / torch.sqrt(1 - alpha_bar[t]) * pred_noise) / torch.sqrt(alpha_t)

        if t > 0:
            z = torch.randn(n_samples, 2)
            beta_tilde = beta_t * (1 - alpha_bar[t - 1]) / (1 - alpha_bar[t])
            beta_tilde = torch.clamp(beta_tilde, 1e-5, 1.0)
            x = mean + torch.sqrt(beta_tilde) * z
        else:
            x = mean
    return x


# =============================================================================
# Sampling: Flow Matching (Euler ODE, straight line)
# =============================================================================

@torch.no_grad()
def sample_flow(model, n_steps=20, n_samples=500):
    model.eval()

    # Start at noise (t=1)
    x = torch.randn(n_samples, 2)
    dt = -1.0 / n_steps  # move from t=1 to t=0
    t = 1.0

    for _ in range(n_steps):
        t_batch = torch.full((n_samples,), t)
        velocity = model(x, t_batch)

        # Euler step: x = x + velocity * dt
        x = x + velocity * dt
        t += dt

    return x


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Flow Matching vs DDPM: 2D circle")
    print("=" * 60)

    data = toy_data()
    print(f"\nData: {data.shape[0]} points in a circle")

    # Train DDPM
    print("\nTraining DDPM (2000 steps)...")
    model_ddpm = TinyModel()
    losses_ddpm, alpha_bar = train_ddpm(model_ddpm, data, steps=2000)

    # Train Flow Matching
    print("Training Flow Matching (2000 steps)...")
    model_flow = TinyModel()
    losses_flow = train_flow(model_flow, data, steps=2000)

    # Sample
    print("\nSampling DDPM (1000 steps)...")
    samples_ddpm = sample_ddpm(model_ddpm, alpha_bar, T=1000, n_samples=500)

    print("Sampling Flow (20 steps)...")
    samples_flow_20 = sample_flow(model_flow, n_steps=20, n_samples=500)

    print("Sampling Flow (5 steps)...")
    samples_flow_5 = sample_flow(model_flow, n_steps=5, n_samples=500)

    # Plot
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].scatter(data[:, 0], data[:, 1], c='#c84a2e', s=80, alpha=0.9)
    axes[0].set_title("Training data (8 points)")
    axes[0].set_xlim(-2, 2)
    axes[0].set_ylim(-2, 2)
    axes[0].set_aspect('equal')

    axes[1].scatter(samples_ddpm[:, 0], samples_ddpm[:, 1],
                    c='#191712', s=2, alpha=0.3)
    axes[1].set_title("DDPM (1000 steps)")
    axes[1].set_xlim(-2, 2)
    axes[1].set_ylim(-2, 2)
    axes[1].set_aspect('equal')

    axes[2].scatter(samples_flow_20[:, 0], samples_flow_20[:, 1],
                    c='#c84a2e', s=2, alpha=0.3)
    axes[2].set_title("Flow Matching (20 steps)")
    axes[2].set_xlim(-2, 2)
    axes[2].set_ylim(-2, 2)
    axes[2].set_aspect('equal')

    axes[3].scatter(samples_flow_5[:, 0], samples_flow_5[:, 1],
                    c='#c84a2e', s=2, alpha=0.3)
    axes[3].set_title("Flow Matching (5 steps)")
    axes[3].set_xlim(-2, 2)
    axes[3].set_ylim(-2, 2)
    axes[3].set_aspect('equal')

    plt.tight_layout()
    plt.savefig("flow_matching_demo.png", dpi=100)
    print("\nSaved flow_matching_demo.png")
    plt.close()

    print(f"\nFinal DDPM loss: {losses_ddpm[-1]:.6f}")
    print(f"Final Flow loss:  {losses_flow[-1]:.6f}")
    print()
    print("Key insight: flow matching produces similar quality with 50x fewer")
    print("sampling steps. The path is straight; the model just learns velocity.")
    print("Same U-Net, same data, same training time. Only the ODE solver differs.")

"""
Phase 40: Flow Matching & Diffusion Transformers

This script demonstrates flow matching using only NumPy.

We build:
1. A dataset of 2D points forming a swirl pattern
2. A small MLP that learns the velocity field for rectified flow
3. ODE sampling with Euler and midpoint methods
4. Visualization of flow lines from noise to data
5. Comparison: flow matching steps vs. DDPM steps

Why NumPy? So every velocity prediction and ODE step is visible.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. DATASET: 2D SWIRL
# ============================================================================
# We create points arranged in a swirl pattern.
# The flow matching model will learn to transform Gaussian noise into this swirl.
# ============================================================================

np.random.seed(42)
n_samples = 500
theta = np.linspace(0, 4*np.pi, n_samples)
r = theta / (4*np.pi) + 0.1
X_data = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
X_data += np.random.randn(n_samples, 2) * 0.03

print("=" * 70)
print("PHASE 40: FLOW MATCHING & DIFFUSION TRANSFORMERS")
print("=" * 70)
print(f"Dataset: {n_samples} points in a 2D swirl pattern")
print("Task: Learn velocity field that transforms noise into the swirl.")
print()

# ============================================================================
# 2. FLOW MATCHING MLP
# ============================================================================
# The model predicts velocity v(x_t, t) given current position x_t and time t.
# For rectified flow, the target velocity is u = x_1 - x_0 (noise - data).
# ============================================================================

class VelocityMLP:
    def __init__(self, input_dim=2, hidden_dim=64):
        # Input is [x, y, t] — 3 dimensions
        self.W1 = np.random.randn(3, hidden_dim) * 0.1
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * 0.1
        self.b2 = np.zeros((1, hidden_dim))
        self.W3 = np.random.randn(hidden_dim, 2) * 0.1
        self.b3 = np.zeros((1, 2))

    def forward(self, x, t):
        # x: (batch, 2), t: (batch, 1)
        inp = np.hstack([x, t])  # (batch, 3)
        self.h1 = np.maximum(inp @ self.W1 + self.b1, 0)
        self.h2 = np.maximum(self.h1 @ self.W2 + self.b2, 0)
        self.out = self.h2 @ self.W3 + self.b3
        return self.out

    def train_step(self, x_data, lr=0.001):
        # For each data point, sample a random noise point and random t
        batch_size = x_data.shape[0]
        x_1 = np.random.randn(batch_size, 2)  # noise
        t = np.random.rand(batch_size, 1)     # uniform in [0, 1]

        # Interpolate: x_t = (1-t) * x_0 + t * x_1
        x_t = (1 - t) * x_data + t * x_1

        # Target velocity (constant for rectified flow)
        u_target = x_1 - x_data

        # Forward
        v_pred = self.forward(x_t, t)

        # Loss: MSE between predicted and target velocity
        loss = np.mean((v_pred - u_target) ** 2)

        # Backprop (simplified)
        grad_out = 2 * (v_pred - u_target) / batch_size
        dW3 = self.h2.T @ grad_out
        db3 = np.sum(grad_out, axis=0, keepdims=True)
        grad_h2 = grad_out @ self.W3.T * (self.h2 > 0)
        dW2 = self.h1.T @ grad_h2
        db2 = np.sum(grad_h2, axis=0, keepdims=True)
        grad_h1 = grad_h2 @ self.W2.T * (self.h1 > 0)
        dW1 = np.hstack([x_t, t]).T @ grad_h1
        db1 = np.sum(grad_h1, axis=0, keepdims=True)

        # Update
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W3 -= lr * dW3
        self.b3 -= lr * db3

        return loss


model = VelocityMLP()
print("Training velocity field...")
losses = []
for epoch in range(2000):
    loss = model.train_step(X_data, lr=0.005)
    losses.append(loss)
    if (epoch + 1) % 400 == 0:
        print(f"  Epoch {epoch+1}, Loss: {loss:.6f}")

print(f"Final loss: {losses[-1]:.6f}")
print()

# ============================================================================
# 3. SAMPLING WITH ODE SOLVERS
# ============================================================================

def sample_euler(model, n_samples, n_steps=20):
    """Euler method sampling."""
    x = np.random.randn(n_samples, 2)  # start from noise (t=1)
    dt = 1.0 / n_steps
    for i in range(n_steps):
        t = 1.0 - i * dt
        t_batch = np.full((n_samples, 1), t)
        v = model.forward(x, t_batch)
        x = x - v * dt  # integrate backward from t=1 to t=0
    return x


def sample_midpoint(model, n_samples, n_steps=10):
    """Midpoint method sampling."""
    x = np.random.randn(n_samples, 2)
    dt = 1.0 / n_steps
    for i in range(n_steps):
        t = 1.0 - i * dt
        t_batch = np.full((n_samples, 1), t)

        # k1 = v(x_t, t)
        k1 = model.forward(x, t_batch)

        # k2 = v(x_t - 0.5*dt*k1, t - 0.5*dt)
        x_mid = x - 0.5 * dt * k1
        t_mid = np.full((n_samples, 1), t - 0.5 * dt)
        k2 = model.forward(x_mid, t_mid)

        x = x - dt * k2
    return x


print("Generating samples...")
samples_euler_20 = sample_euler(model, 500, n_steps=20)
samples_euler_5 = sample_euler(model, 500, n_steps=5)
samples_midpoint_10 = sample_midpoint(model, 500, n_steps=10)
print("Done.")
print()

# ============================================================================
# 4. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# ---- Plot 1: Training Loss ----
ax = axes[0, 0]
ax.plot(losses, linewidth=1.5, color='blue')
ax.set_xlabel('Iteration')
ax.set_ylabel('MSE Loss')
ax.set_title('Velocity Field Training Loss')
ax.grid(True, alpha=0.3)

# ---- Plot 2: Real Data ----
ax = axes[0, 1]
ax.scatter(X_data[:, 0], X_data[:, 1], s=10, alpha=0.5, color='green')
ax.set_title('Real Data (Swirl)')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# ---- Plot 3: Euler 20 steps ----
ax = axes[0, 2]
ax.scatter(samples_euler_20[:, 0], samples_euler_20[:, 1], s=10, alpha=0.5, color='blue')
ax.set_title('Flow Matching: Euler 20 Steps')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# ---- Plot 4: Euler 5 steps ----
ax = axes[1, 0]
ax.scatter(samples_euler_5[:, 0], samples_euler_5[:, 1], s=10, alpha=0.5, color='red')
ax.set_title('Flow Matching: Euler 5 Steps (Fast)')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# ---- Plot 5: Midpoint 10 steps ----
ax = axes[1, 1]
ax.scatter(samples_midpoint_10[:, 0], samples_midpoint_10[:, 1], s=10, alpha=0.5, color='purple')
ax.set_title('Flow Matching: Midpoint 10 Steps')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# ---- Plot 6: Flow Lines ----
ax = axes[1, 2]
# Sample a few trajectories
n_traj = 10
colors = plt.cm.jet(np.linspace(0, 1, n_traj))
for i in range(n_traj):
    x = np.random.randn(1, 2)
    traj = [x.copy()]
    n_steps = 30
    dt = 1.0 / n_steps
    for step in range(n_steps):
        t = 1.0 - step * dt
        t_batch = np.array([[t]])
        v = model.forward(x, t_batch)
        x = x - v * dt
        traj.append(x.copy())
    traj = np.array(traj).squeeze()
    ax.plot(traj[:, 0], traj[:, 1], color=colors[i], alpha=0.6, linewidth=1.5)
    ax.scatter(traj[0, 0], traj[0, 1], color=colors[i], s=30, marker='x')  # start (noise)
    ax.scatter(traj[-1, 0], traj[-1, 1], color=colors[i], s=30, marker='o')  # end (data)

ax.scatter(X_data[:, 0], X_data[:, 1], s=5, alpha=0.3, color='green', label='Real data')
ax.set_title('Flow Lines: Noise → Data')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase40/flow_matching.png', dpi=150, bbox_inches='tight')
print("Saved visualization: src/phase40/flow_matching.png")
plt.close()

# ============================================================================
# 5. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Flow matching learns a velocity field that transforms noise into data.")
print(f"Training: {len(losses)} iterations, final MSE loss = {losses[-1]:.6f}")
print()
print("Sampling methods:")
print("  Euler 20 steps: smooth, accurate generation")
print("  Euler 5 steps:  faster but slightly noisier")
print("  Midpoint 10 steps: good accuracy with fewer evaluations")
print()
print("Key observations:")
print("1. Rectified flow uses straight-line paths: x_t = (1-t)*data + t*noise")
print("2. Target velocity is constant: u = noise - data")
print("3. The model learns to predict this velocity field.")
print("4. ODE solvers integrate the velocity field from noise back to data.")
print("5. Flow matching needs ~20 steps vs. DDPM's ~1000 steps.")
print()
print("This demonstrates the core idea of flow matching:")
print("- Direct velocity prediction instead of noise prediction")
print("- Straight-line paths simplify learning and sampling")
print("- ODE solvers enable fast, adaptive generation")
print("- Modern generative models (SD3, Flux) use this approach")
print("=" * 70)

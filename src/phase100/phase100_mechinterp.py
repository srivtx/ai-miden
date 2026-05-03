import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(100)

# --- Toy Model: 3-layer MLP ---
# Input -> Linear1 -> ReLU -> Linear2 -> ReLU -> Linear3 -> Output
# We will compare clean, corrupted, and patched forward passes.

input_dim = 8
hidden_dim = 16
output_dim = 4
batch_size = 32

# Random weights
W1 = np.random.randn(input_dim, hidden_dim) * 0.3
b1 = np.zeros(hidden_dim)
W2 = np.random.randn(hidden_dim, hidden_dim) * 0.3
b2 = np.zeros(hidden_dim)
W3 = np.random.randn(hidden_dim, output_dim) * 0.3
b3 = np.zeros(output_dim)


def relu(x):
    return np.maximum(0, x)


def forward(x):
    z1 = x @ W1 + b1
    a1 = relu(z1)
    z2 = a1 @ W2 + b2
    a2 = relu(z2)
    z3 = a2 @ W3 + b3
    return z3, (z1, a1, z2, a2)


# Clean input
x_clean = np.random.randn(batch_size, input_dim)

# Corrupted input: flip sign of one important feature dimension
x_corrupt = x_clean.copy()
x_corrupt[:, 0] *= -1

# Forward passes
out_clean, acts_clean = forward(x_clean)
out_corrupt, acts_corrupt = forward(x_corrupt)

# --- Attribution Patching ---
# Patch activation a1 (after layer 1) from clean into corrupted run,
# then see how much each layer's output changes relative to clean.
# We compute gradient of output w.r.t each activation to attribute change.

z1_c, a1_c, z2_c, a2_c = acts_clean
z1_r, a1_r, z2_r, a2_r = acts_corrupt

# Patch a1
z2_patched = a1_c @ W2 + b2
a2_patched = relu(z2_patched)
out_patched = a2_patched @ W3 + b3

# Output differences
diff_corrupt = np.mean(np.abs(out_clean - out_corrupt))
diff_patched = np.mean(np.abs(out_clean - out_patched))
print("Mean output diff (clean vs corrupt):", diff_corrupt)
print("Mean output diff (clean vs patched a1):", diff_patched)

# Compute simple attribution via finite differences at each layer
eps = 1e-3
attribution_l1 = np.zeros(hidden_dim)
for i in range(hidden_dim):
    z1_pert = z1_c.copy()
    z1_pert[:, i] += eps
    a1_pert = relu(z1_pert)
    out_pert = relu(a1_pert @ W2 + b2) @ W3 + b3
    attribution_l1[i] = np.mean(np.abs(out_pert - out_clean)) / eps

attribution_l2 = np.zeros(hidden_dim)
for i in range(hidden_dim):
    z2_pert = z2_c.copy()
    z2_pert[:, i] += eps
    a2_pert = relu(z2_pert)
    out_pert = a2_pert @ W3 + b3
    attribution_l2[i] = np.mean(np.abs(out_pert - out_clean)) / eps

print("\nAttribution L1 mean:", attribution_l1.mean())
print("Attribution L2 mean:", attribution_l2.mean())

# --- Visualization ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].bar(np.arange(hidden_dim), attribution_l1, color='steelblue', edgecolor='black')
axes[0].set_title('Layer 1 Attribution (perturb z1 -> output change)')
axes[0].set_xlabel('Hidden Unit Index')
axes[0].set_ylabel('Attribution Score')
axes[0].grid(axis='y', linestyle='--', alpha=0.5)

axes[1].bar(np.arange(hidden_dim), attribution_l2, color='coral', edgecolor='black')
axes[1].set_title('Layer 2 Attribution (perturb z2 -> output change)')
axes[1].set_xlabel('Hidden Unit Index')
axes[1].set_ylabel('Attribution Score')
axes[1].grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase100_attribution_patching.png')
plt.savefig(out_path)
print("Saved plot to", out_path)

# Also save a bar chart of output differences
plt.figure(figsize=(6, 4))
plt.bar(['Clean vs Corrupt', 'Clean vs Patched L1'], [diff_corrupt, diff_patched],
        color=['crimson', 'seagreen'], edgecolor='black')
plt.ylabel('Mean Absolute Output Difference')
plt.title('Effect of Corruption and Patching')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
out_path2 = os.path.join(os.path.dirname(__file__), 'phase100_patching_effect.png')
plt.savefig(out_path2)
print("Saved plot to", out_path2)

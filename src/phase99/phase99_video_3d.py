import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(99)

# --- Toy Spatiotemporal Convolution ---
# Imagine a 1D spatial signal evolving over time.
# Spatial size = 16, Time steps = 8
spatial_size = 16
time_steps = 8
signal = np.zeros((time_steps, spatial_size))

# Create a moving bump
for t in range(time_steps):
    center = 4 + t * 1.5
    for x in range(spatial_size):
        signal[t, x] = np.exp(-0.5 * ((x - center) / 1.5) ** 2)

# A 2D conv kernel over (time, space)
k = np.array([
    [0, -1, 0],
    [-1, 4, -1],
    [0, -1, 0]
])


def conv2d_valid(x, k):
    kh, kw = k.shape
    out = np.zeros((x.shape[0] - kh + 1, x.shape[1] - kw + 1))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = np.sum(x[i:i + kh, j:j + kw] * k)
    return out


spatiotemporal_feature = conv2d_valid(signal, k)

print("Input signal shape:", signal.shape)
print("Feature map shape:", spatiotemporal_feature.shape)

# --- Toy "diffusion" on 1D+time signal ---
# Forward process: add noise over diffusion steps
num_diffusion_steps = 20
beta = np.linspace(0.01, 0.2, num_diffusion_steps)
alpha = 1 - beta
alpha_bar = np.cumprod(alpha)

# Sample a clean 1D+time patch
x0 = signal[2:5, 4:10]
x0_flat = x0.flatten()

# Forward diffusion trajectory
trajectory = []
for t in range(num_diffusion_steps):
    noise = np.random.randn(*x0_flat.shape)
    xt = np.sqrt(alpha_bar[t]) * x0_flat + np.sqrt(1 - alpha_bar[t]) * noise
    trajectory.append(xt)

trajectory = np.array(trajectory)  # (T, D)

# Plot original signal and feature map
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

im0 = axes[0].imshow(signal, aspect='auto', cmap='viridis', origin='lower')
axes[0].set_title('Input 1D+Time Signal')
axes[0].set_xlabel('Space')
axes[0].set_ylabel('Time')
fig.colorbar(im0, ax=axes[0])

im1 = axes[1].imshow(spatiotemporal_feature, aspect='auto', cmap='plasma', origin='lower')
axes[1].set_title('Spatiotemporal Feature Map (Laplacian-like)')
axes[1].set_xlabel('Space')
axes[1].set_ylabel('Time')
fig.colorbar(im1, ax=axes[1])

axes[2].plot(trajectory[:, 0], label='Dim 0', alpha=0.7)
axes[2].plot(trajectory[:, 1], label='Dim 1', alpha=0.7)
axes[2].set_title('Toy Diffusion Trajectory (1 patch dimension)')
axes[2].set_xlabel('Diffusion Step')
axes[2].set_ylabel('Value')
axes[2].legend()
axes[2].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase99_video_3d.png')
plt.savefig(out_path)
print("Saved plot to", out_path)

# Show complexity increase: number of elements
spatial_2d = 256 * 256
video_3d = 256 * 256 * 30 * 5  # 5 seconds at 30 fps
print(f"\n2D image elements: {spatial_2d}")
print(f"5-second video elements (256x256@30fps): {video_3d}")
print(f"Complexity increase factor: {video_3d / spatial_2d:.0f}x")

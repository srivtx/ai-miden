import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: In real training, we have weights, optimizer momentum, and RNG state.
# Losing these after a crash means restarting from scratch.

# Simulate a training state
np.random.seed(42)
weights = np.random.randn(100)
optimizer_state = {'m': np.zeros(100), 'v': np.zeros(100)}
rng_state = np.random.get_state()

# WHY: A checkpoint captures everything needed to resume exactly.
checkpoint = {
    'weights': weights.copy(),
    'optimizer_state': {k: v.copy() for k, v in optimizer_state.items()},
    'rng_state': rng_state,
    'step': 100
}

# Simulate a crash and recovery
loaded_checkpoint = checkpoint
np.random.set_state(loaded_checkpoint['rng_state'])

# WHY: To prove determinism, run the same "update" twice from the same seed.
def training_update(w, opt, seed):
    np.random.seed(seed)
    grad = np.random.randn(*w.shape)
    opt['m'] = 0.9 * opt['m'] + 0.1 * grad
    w_new = w - 0.01 * opt['m']
    return w_new, opt

w1, o1 = training_update(
    loaded_checkpoint['weights'].copy(),
    {k: v.copy() for k, v in loaded_checkpoint['optimizer_state'].items()},
    seed=123
)

w2, o2 = training_update(
    loaded_checkpoint['weights'].copy(),
    {k: v.copy() for k, v in loaded_checkpoint['optimizer_state'].items()},
    seed=123
)

print("Weights identical after resume:", np.allclose(w1, w2))
print("Optimizer states identical:", np.allclose(o1['m'], o2['m']))

# WHY: Visualize that checkpointing preserves the trajectory.
fig, ax = plt.subplots()
ax.plot(weights[:20], label='Original')
ax.plot(w1[:20], label='After update 1')
ax.plot(w2[:20], label='After update 2 (same seed)', linestyle='--')
ax.legend()
ax.set_title("Checkpointing & Determinism Demo")
fig.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase87/checkpoint_determinism.png')
print("Saved plot to checkpoint_determinism.png")

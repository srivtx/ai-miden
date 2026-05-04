# FRONTIER TRACK: Phase 135 — In-Context Learning and Emergent Capabilities (Concepts)
# LOCAL NumPy concept demonstration
# WHY: NumPy makes the mechanics of ICL and phase transitions transparent.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: Reproducibility matters for educational demos.
np.random.seed(135)

# -----------------------------------------------------------------------------
# PART 1: SIMULATE IN-CONTEXT LEARNING
# WHY: A linear model can approximate "learning from context" by treating
# context examples as observations that shift the prediction weights.
# -----------------------------------------------------------------------------

# True task: y = w_true * x + b_true
w_true = 2.5
b_true = -1.0
n_test = 50

# Generate test set
x_test = np.linspace(-3, 3, n_test)
y_test = w_true * x_test + b_true

# Number of in-context examples to try
n_examples_list = [0, 1, 2, 3, 5, 8, 12, 20, 30, 50]
icl_errors = []

for n_ex in n_examples_list:
    # WHY: Zero-shot means no context — model uses a default prior.
    if n_ex == 0:
        w_est = 1.0  # generic prior slope
        b_est = 0.0
    else:
        # Sample context examples
        x_ctx = np.random.uniform(-3, 3, n_ex)
        y_ctx = w_true * x_ctx + b_true + np.random.normal(0, 0.5, n_ex)
        # Fit linear regression on context (this is what ICL implicitly does)
        X = np.vstack([x_ctx, np.ones_like(x_ctx)]).T
        wb = np.linalg.lstsq(X, y_ctx, rcond=None)[0]
        w_est, b_est = wb[0], wb[1]

    y_pred = w_est * x_test + b_est
    mse = np.mean((y_pred - y_test) ** 2)
    icl_errors.append(mse)

# -----------------------------------------------------------------------------
# PART 2: SIMULATE EMERGENT CAPABILITIES (PHASE TRANSITION)
# WHY: Some tasks require a minimum representational capacity. Below a
# threshold, the model cannot represent the function; above it, accuracy jumps.
# -----------------------------------------------------------------------------

# Task: classify XOR-like pattern (requires non-linearity / sufficient capacity)
# We simulate "model size" as hidden dimension and accuracy as a sigmoid
# that activates once capacity crosses a threshold.

def emergent_accuracy(model_size, threshold=64, steepness=0.15, noise=0.02):
    """
    WHY: A logistic curve mimics phase-transition behavior:
    flat below threshold, steep rise near threshold, plateau above.
    """
    base = 1.0 / (1.0 + np.exp(-steepness * (model_size - threshold)))
    # Add slight noise and a floor (models guess randomly at small scale)
    acc = 0.1 + 0.85 * base + np.random.normal(0, noise)
    return np.clip(acc, 0, 1)

model_sizes = np.arange(4, 257, 4)
n_trials = 5
emergence_curves = []
for _ in range(n_trials):
    curve = [emergent_accuracy(s) for s in model_sizes]
    emergence_curves.append(curve)
emergence_arr = np.array(emergence_curves)
emergence_mean = emergence_arr.mean(axis=0)
emergence_std = emergence_arr.std(axis=0)

# -----------------------------------------------------------------------------
# PART 3: SMOOTH LOSS VS DISCRETE ACCURACY
# WHY: The same model sizes produce smooth perplexity but discrete task jumps.
# -----------------------------------------------------------------------------

# Smooth perplexity follows a power law
perplexity = 100.0 * (model_sizes / 256.0) ** (-0.25) + 2.0

# -----------------------------------------------------------------------------
# PART 4: PLOTTING
# WHY: Humans learn from curves. We show all three phenomena side by side.
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: ICL error vs n_examples
ax = axes[0, 0]
ax.plot(n_examples_list, icl_errors, marker='o', color='steelblue', linewidth=2)
ax.set_title('ICL Performance vs Number of Context Examples')
ax.set_xlabel('Number of In-Context Examples')
ax.set_ylabel('Mean Squared Error on Test Set')
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)
ax.axhline(y=0.25, color='crimson', linestyle='--', alpha=0.5, label='Noise floor')
ax.legend()

# Plot 2: Emergent capability (accuracy vs model size)
ax = axes[0, 1]
ax.plot(model_sizes, emergence_mean, color='forestgreen', linewidth=2, label='Mean accuracy')
ax.fill_between(model_sizes, emergence_mean - emergence_std, emergence_mean + emergence_std,
                color='forestgreen', alpha=0.2, label='Std dev')
ax.axvline(x=64, color='crimson', linestyle='--', alpha=0.6, label='Critical threshold')
ax.set_title('Emergent Capability: Task Accuracy vs Model Size')
ax.set_xlabel('Model Capacity (hidden dimension)')
ax.set_ylabel('Task Accuracy')
ax.set_ylim(0, 1)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Smooth loss (perplexity) vs model size
ax = axes[1, 0]
ax.plot(model_sizes, perplexity, color='darkorange', linewidth=2)
ax.set_title('Smooth Scaling Law: Perplexity vs Model Size')
ax.set_xlabel('Model Capacity (hidden dimension)')
ax.set_ylabel('Perplexity')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

# Plot 4: Both curves overlaid (dual axis)
ax = axes[1, 1]
ax2 = ax.twinx()
ax.plot(model_sizes, perplexity, color='darkorange', linewidth=2, label='Perplexity (smooth)')
ax2.plot(model_sizes, emergence_mean, color='forestgreen', linewidth=2, label='Task accuracy (discrete)')
ax.set_xlabel('Model Capacity (hidden dimension)')
ax.set_ylabel('Perplexity', color='darkorange')
ax2.set_ylabel('Task Accuracy', color='forestgreen')
ax.set_title('Smooth Loss vs Discrete Capability on Same Scale')
ax.grid(True, alpha=0.3)
ax.tick_params(axis='y', labelcolor='darkorange')
ax2.tick_params(axis='y', labelcolor='forestgreen')

# Combine legends
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper center')

plt.tight_layout()
plt.savefig('src/phase135/icl_concepts.png', dpi=150)
plt.close()

print("Plot saved to src/phase135/icl_concepts.png")

# -----------------------------------------------------------------------------
# FINAL INSIGHT
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("KEY INSIGHTS:")
print("1. ICL error drops rapidly with the first few examples, then")
print("   saturates. There is a sweet spot for context length.")
print("2. Emergent capabilities show a phase transition: accuracy is")
print("   near-zero below a critical model size, then jumps sharply.")
print("3. Perplexity improves smoothly across all scales, but task")
print("   accuracy is flat then discrete. This disconnect means loss")
print("   alone cannot predict capabilities.")
print("=" * 60)

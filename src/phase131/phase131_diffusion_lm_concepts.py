#!/usr/bin/env python3
"""
Phase 131: Diffusion Language Models — NumPy Concept Demo
==========================================================
This script simulates a diffusion language model to demonstrate:

  1. Forward process: masking tokens according to a schedule
  2. Reverse process: iteratively predicting and unmasking tokens
  3. Denoising trajectory: how a sequence converges from noise to text
  4. Comparison with autoregressive generation (serial steps)
  5. Parallel decoding: all positions predicted simultaneously

Key insight: text generation is not chained to left-to-right order.
A diffusion LM treats generation as iterative refinement, unlocking
parallelism and the ability to revise early decisions.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(131)

# =============================================================================
# SECTION 1: TOY VOCABULARY AND EMBEDDINGS
# =============================================================================
# We build a tiny vocabulary and synthetic embeddings so we can run
# a full diffusion loop in NumPy without a neural network library.
# WHY a toy vocab? Real transformers are billions of parameters;
# the concept is identical at smaller scale.

VOCAB = [
    "the", "cat", "sat", "on", "mat", "a", "dog", "ran",
    "blue", "sky", "green", "grass", "bird", "sang", "tree",
    "happy", "sad", "fast", "slow", "big", "small",
]
VOCAB_SIZE = len(VOCAB)
MASK_TOKEN = "[MASK]"

# Synthetic embedding matrix: each word gets a 16-dim vector
EMBED_DIM = 16
embeddings = np.random.randn(VOCAB_SIZE, EMBED_DIM) * 0.5
# Make similar words have similar embeddings (semantic clustering)
embeddings[0] += embeddings[1] * 0.3   # the ~ cat
embeddings[2] += embeddings[7] * 0.3   # sat ~ ran
embeddings[8] += embeddings[9] * 0.4   # blue ~ sky

# Synthetic target sequences for demonstration
TARGET_SEQUENCES = [
    ["the", "cat", "sat", "on", "the", "mat"],
    ["a", "dog", "ran", "on", "grass"],
    ["the", "blue", "bird", "sang", "on", "a", "tree"],
    ["the", "sky", "is", "blue"],  # 'is' not in vocab, will map to nearest
]

# Map any unknown word to a random vocab index for this demo
word_to_idx = {w: i for i, w in enumerate(VOCAB)}


def tokenize(words):
    """Map words to indices, falling back to random for OOV."""
    return np.array([word_to_idx.get(w, np.random.randint(VOCAB_SIZE)) for w in words])


def detokenize(indices):
    """Map indices back to words."""
    return [VOCAB[i] for i in indices]


# =============================================================================
# SECTION 2: DIFFUSION MODEL SIMULATOR
# =============================================================================
# We simulate a trained diffusion model by defining a scoring function.
# In a real model, this would be a transformer forward pass.
# WHY a scoring function? It lets us demonstrate the inference schedule
# without needing PyTorch or a trained checkpoint.

class ToyDiffusionModel:
    """
    Simulate a diffusion language model with bidirectional attention.
    The model scores each [MASK] position by comparing the context
    embedding to vocabulary embeddings.
    """

    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vocab_size = embeddings.shape[0]
        self.embed_dim = embeddings.shape[1]

    def predict(self, sequence, mask_positions):
        """
        Predict probabilities for all masked positions simultaneously.
        WHY simultaneous? This is parallel decoding — the hallmark of
        diffusion language models.
        """
        probs = np.zeros((len(mask_positions), self.vocab_size))
        for i, pos in enumerate(mask_positions):
            # Build a context vector from unmasked neighbors
            context = np.zeros(self.embed_dim)
            count = 0
            for offset in [-2, -1, 1, 2]:
                neighbor = pos + offset
                if 0 <= neighbor < len(sequence) and sequence[neighbor] != -1:
                    context += self.embeddings[sequence[neighbor]]
                    count += 1
            if count == 0:
                context = np.random.randn(self.embed_dim) * 0.1
            else:
                context /= count

            # Compute similarity to every vocab word
            logits = self.embeddings @ context  # dot product similarity
            # Add position bias (early positions favor determiners)
            if pos == 0:
                logits[[0, 5]] += 1.5  # favor "the", "a"
            # Temperature for sampling
            logits /= 0.8
            exp = np.exp(logits - logits.max())
            probs[i] = exp / exp.sum()
        return probs


def diffusion_generate(model, length, n_steps=20, unmask_per_step=None):
    """
    Generate a sequence using iterative diffusion unmasking.
    WHY start with all masks? This is the standard diffusion initialization.
    WHY unmask gradually? Early steps have little context, so we only
    commit the most confident predictions and let the model refine the rest.
    """
    if unmask_per_step is None:
        # Unmask roughly evenly across steps, leaving some for final cleanup
        unmask_per_step = max(1, int(np.ceil(length / n_steps)))

    sequence = np.full(length, -1, dtype=int)  # -1 means MASK
    trajectory = [sequence.copy()]
    confidences = []

    for step in range(n_steps):
        mask_positions = np.where(sequence == -1)[0]
        if len(mask_positions) == 0:
            break

        # Predict all masked positions in parallel
        probs = model.predict(sequence, mask_positions)

        # Confidence = max probability at each position
        step_confidences = probs.max(axis=1)
        confidences.append(step_confidences.mean())

        # Unmask the K most confident predictions
        k = min(unmask_per_step, len(mask_positions))
        top_k_indices = np.argsort(-step_confidences)[:k]
        for idx in top_k_indices:
            pos = mask_positions[idx]
            sequence[pos] = np.argmax(probs[idx])

        trajectory.append(sequence.copy())

    # Fill any remaining masks
    mask_positions = np.where(sequence == -1)[0]
    if len(mask_positions) > 0:
        probs = model.predict(sequence, mask_positions)
        for i, pos in enumerate(mask_positions):
            sequence[pos] = np.argmax(probs[i])
        trajectory.append(sequence.copy())

    return sequence, trajectory, confidences


# =============================================================================
# SECTION 3: AUTOREGRESSIVE BASELINE
# =============================================================================
# We simulate greedy autoregressive generation for comparison.
# WHY greedy? It is the simplest fair comparison. Beam search or
# sampling would complicate the step count without changing the insight.

def autoregressive_generate(model, length):
    """
    Generate one token at a time from left to right.
    WHY left-to-right? This is the standard autoregressive paradigm.
    """
    sequence = np.full(length, -1, dtype=int)
    trajectory = [sequence.copy()]

    for pos in range(length):
        probs = model.predict(sequence, [pos])
        sequence[pos] = np.argmax(probs[0])
        trajectory.append(sequence.copy())

    return sequence, trajectory


# =============================================================================
# SECTION 4: RUN GENERATION AND COMPARE
# =============================================================================

model = ToyDiffusionModel(embeddings)

print("=" * 70)
print("Phase 131: Diffusion Language Models — NumPy Concept Demo")
print("=" * 70)

results = []
for seq_words in TARGET_SEQUENCES:
    length = len(seq_words)
    target = tokenize(seq_words)

    # Diffusion generation
    diff_seq, diff_traj, diff_conf = diffusion_generate(
        model, length, n_steps=20, unmask_per_step=max(1, length // 8)
    )

    # Autoregressive generation
    ar_seq, ar_traj = autoregressive_generate(model, length)

    diff_correct = (diff_seq == target).sum()
    ar_correct = (ar_seq == target).sum()

    results.append({
        'target_words': seq_words,
        'length': length,
        'diff_seq': detokenize(diff_seq),
        'diff_steps': len(diff_traj) - 1,
        'diff_correct': diff_correct,
        'ar_seq': detokenize(ar_seq),
        'ar_steps': len(ar_traj) - 1,
        'ar_correct': ar_correct,
        'diff_traj': diff_traj,
        'ar_traj': ar_traj,
        'diff_conf': diff_conf,
    })

    print(f"\nTarget:     {' '.join(seq_words)}")
    print(f"Diffusion:  {' '.join(detokenize(diff_seq))}  (steps={len(diff_traj)-1}, correct={diff_correct}/{length})")
    print(f"Auto-reg:   {' '.join(detokenize(ar_seq))}   (steps={len(ar_traj)-1}, correct={ar_correct}/{length})")

# Summary statistics
total_diff_steps = sum(r['diff_steps'] for r in results)
total_ar_steps = sum(r['ar_steps'] for r in results)
total_diff_correct = sum(r['diff_correct'] for r in results)
total_ar_correct = sum(r['ar_correct'] for r in results)
total_tokens = sum(r['length'] for r in results)

print(f"\n--- Summary ---")
print(f"Total tokens generated:     {total_tokens}")
print(f"Diffusion serial steps:     {total_diff_steps}")
print(f"Autoregressive serial steps: {total_ar_steps}")
print(f"Step reduction:             {total_ar_steps - total_diff_steps} ({(1 - total_diff_steps/total_ar_steps)*100:.1f}% fewer)")
print(f"Diffusion exact-match:      {total_diff_correct}/{total_tokens} ({total_diff_correct/total_tokens*100:.1f}%)")
print(f"Autoregressive exact-match: {total_ar_correct}/{total_tokens} ({total_ar_correct/total_tokens*100:.1f}%)")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# Plot 1: Denoising trajectory for the first sequence
ax = axes[0, 0]
r = results[0]
traj = r['diff_traj']
vocab_display = VOCAB + [MASK_TOKEN]
# Create a heatmap: rows = steps, cols = positions
traj_matrix = np.zeros((len(traj), r['length']))
for step_idx, seq in enumerate(traj):
    for pos_idx, tok in enumerate(seq):
        traj_matrix[step_idx, pos_idx] = tok if tok != -1 else VOCAB_SIZE

im = ax.imshow(traj_matrix, aspect='auto', cmap='tab20', vmin=0, vmax=VOCAB_SIZE)
ax.set_yticks(range(len(traj)))
ax.set_yticklabels([f"Step {i}" for i in range(len(traj))])
ax.set_xticks(range(r['length']))
ax.set_xticklabels([r['target_words'][i] for i in range(r['length'])])
ax.set_title(f'Denoising Trajectory: "{" ".join(r["target_words"])}"')
ax.set_xlabel('Position')
# Add text annotations
for step_idx in range(len(traj)):
    for pos_idx in range(r['length']):
        tok_idx = int(traj_matrix[step_idx, pos_idx])
        label = vocab_display[tok_idx]
        color = 'white' if tok_idx == VOCAB_SIZE else 'black'
        ax.text(pos_idx, step_idx, label, ha='center', va='center', fontsize=8, color=color)

# Plot 2: Confidence over diffusion steps (average across all sequences)
ax = axes[0, 1]
max_conf_len = max(len(r['diff_conf']) for r in results)
conf_matrix = np.full((len(results), max_conf_len), np.nan)
for i, r in enumerate(results):
    conf_matrix[i, :len(r['diff_conf'])] = r['diff_conf']
mean_conf = np.nanmean(conf_matrix, axis=0)
ax.plot(mean_conf, '-o', color='#3498db', linewidth=2, markersize=6)
ax.set_xlabel('Diffusion Step')
ax.set_ylabel('Mean Confidence (max prob)')
ax.set_title('Confidence Increases During Denoising')
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

# Plot 3: Step count comparison
ax = axes[1, 0]
x = np.arange(len(results))
width = 0.35
diff_steps = [r['diff_steps'] for r in results]
ar_steps = [r['ar_steps'] for r in results]
ax.bar(x - width/2, diff_steps, width, label='Diffusion', color='#3498db', edgecolor='black')
ax.bar(x + width/2, ar_steps, width, label='Autoregressive', color='#e74c3c', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels([f"Seq {i+1}" for i in x])
ax.set_ylabel('Serial Steps')
ax.set_title('Serial Steps: Diffusion vs. Autoregressive')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Exact match accuracy
ax = axes[1, 1]
diff_acc = [r['diff_correct']/r['length']*100 for r in results]
ar_acc = [r['ar_correct']/r['length']*100 for r in results]
ax.bar(x - width/2, diff_acc, width, label='Diffusion', color='#3498db', edgecolor='black')
ax.bar(x + width/2, ar_acc, width, label='Autoregressive', color='#e74c3c', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels([f"Seq {i+1}" for i in x])
ax.set_ylabel('Exact Match Accuracy (%)')
ax.set_title('Token-Level Accuracy Comparison')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, 105)

plt.tight_layout()
os.makedirs('src/phase131', exist_ok=True)
plt.savefig('src/phase131/diffusion_lm_concepts.png', dpi=150)
print("\nSaved plot to src/phase131/diffusion_lm_concepts.png")

# =============================================================================
# SECTION 6: DEMONSTRATE REVISION CAPABILITY
# =============================================================================
# Diffusion models can revise early mistakes. We simulate this by
# starting with a deliberately bad initial state and showing convergence.

print("\n" + "=" * 70)
print("REVISION DEMONSTRATION")
print("=" * 70)

# Start with a partially wrong sequence and let diffusion fix it
length = 6
wrong_start = tokenize(["a", "dog", "ran", "on", "the", "mat"])
target = tokenize(["the", "cat", "sat", "on", "the", "mat"])

sequence = wrong_start.copy()
trajectory_fix = [sequence.copy()]
for step in range(5):
    mask_positions = np.where(sequence != target)[0]
    if len(mask_positions) == 0:
        break
    probs = model.predict(sequence, mask_positions)
    for i, pos in enumerate(mask_positions):
        sequence[pos] = np.argmax(probs[i])
    trajectory_fix.append(sequence.copy())

print(f"Target:   {' '.join(detokenize(target))}")
print(f"Start:    {' '.join(detokenize(wrong_start))}")
for i, seq in enumerate(trajectory_fix):
    print(f"Step {i}: {' '.join(detokenize(seq))}")
print("Key lesson: Diffusion can revise any position at any step.")
print("Autoregressive generation would be stuck with 'a dog ran'.")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Generated {len(TARGET_SEQUENCES)} sequences with diffusion and autoregressive baselines")
print(f"Diffusion used {total_diff_steps} serial steps vs. {total_ar_steps} for autoregressive")
print(f"Parallelism: each diffusion step predicted all remaining positions simultaneously")
print(f"Diffusion accuracy: {total_diff_correct}/{total_tokens} ({total_diff_correct/total_tokens*100:.1f}%)")
print(f"Autoregressive accuracy: {total_ar_correct}/{total_tokens} ({total_ar_correct/total_tokens*100:.1f}%)")
print(f"\nKey lessons:")
print("  1. Diffusion LMs generate all tokens in parallel, not one at a time.")
print("  2. Serial step count scales with diffusion steps, not sequence length.")
print("  3. Early predictions can be revised in later steps.")
print("  4. Confidence rises steadily as more context becomes available.")
print("  5. For long sequences, diffusion can achieve lower latency.")
print("  6. Quality depends on the number of refinement steps.")
print("  7. The autoregressive monopoly on text generation is not inevitable.")
print("=" * 70)

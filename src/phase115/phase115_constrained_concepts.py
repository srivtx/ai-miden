# FRONTIER TRACK: Phase 115 — Structured Generation and Constrained Decoding
# LOCAL NumPy concept demonstration
# This script simulates a toy vocabulary and grammar to show token-level masking.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Set seed so the demo is reproducible
np.random.seed(115)

# Define a tiny vocabulary of token strings
vocab = [
    '{',           # 0
    '"name"',      # 1
    '":"',         # 2
    '"Alice"',     # 3
    '"Bob"',       # 4
    '","',         # 5
    '"age"',       # 6
    '25',          # 7
    '30',          # 8
    '}',           # 9
    'invalid',     # 10
    'bad',         # 11
    'oops',        # 12
]

vocab_size = len(vocab)

# Grammar states for a tiny JSON object: {"name": <string>, "age": <int>}
# state -> list of valid token indices
grammar = {
    0: [0],        # must start with '{'
    1: [1],        # after '{', expect '"name"'
    2: [2],        # after '"name"', expect '":"'
    3: [3, 4],     # after '":"', expect a string value
    4: [5],        # after string, expect '","'
    5: [6],        # after '","', expect '"age"'
    6: [2],        # after '"age"', expect '":"'
    7: [7, 8],     # after '":"', expect an integer
    8: [9],        # after integer, expect '}'
    9: [],         # after '}', done (EOS)
}

# Number of decoding steps for a complete valid JSON
num_steps = 9

# Simulate model logits: random values plus a bias toward invalid tokens
# so the unconstrained path often picks something illegal
logits = np.random.randn(num_steps, vocab_size)
invalid_indices = [10, 11, 12]
for step in range(num_steps):
    logits[step, invalid_indices] += 2.5  # make invalid tokens attractive


def softmax(x):
    """Numerically stable softmax."""
    e = np.exp(x - np.max(x))
    return e / e.sum()


# Storage for analysis
unmasked_probs = []
masked_probs_list = []
chosen_unmasked = []
chosen_masked = []
valid_masks = []

for step in range(num_steps):
    state = step  # our toy grammar states line up 1:1 with steps
    valid_ids = grammar[state]

    # Raw probabilities from the model
    probs = softmax(logits[step])
    unmasked_probs.append(probs)

    # Binary mask: 1 for valid, 0 for invalid
    mask = np.zeros(vocab_size)
    mask[valid_ids] = 1.0
    valid_masks.append(mask)

    # Apply mask by setting invalid logits to a very negative number
    masked_logits = logits[step].copy()
    masked_logits[mask == 0] = -1e9
    m_probs = softmax(masked_logits)
    masked_probs_list.append(m_probs)

    # Greedy choice (argmax)
    chosen_unmasked.append(int(np.argmax(probs)))
    chosen_masked.append(int(np.argmax(m_probs)))

# Decode token indices to strings
seq_unmasked = [vocab[i] for i in chosen_unmasked]
seq_masked = [vocab[i] for i in chosen_masked]


def is_valid_sequence(tokens):
    """Check whether a token sequence respects the grammar."""
    state = 0
    for tok in tokens:
        valid = grammar.get(state, [])
        idx = vocab.index(tok)
        if idx not in valid:
            return False
        state += 1
    return state == 9


print("=== Greedy WITHOUT mask ===")
print(" ".join(seq_unmasked))
print("Valid JSON? ", is_valid_sequence(seq_unmasked))

print("\n=== Greedy WITH mask ===")
print(" ".join(seq_masked))
print("Valid JSON? ", is_valid_sequence(seq_masked))

# Pick a step where multiple valid options exist to illustrate redistribution
step_idx = 3  # string value step: allowed tokens are "Alice" and "Bob"
probs_before = unmasked_probs[step_idx]
probs_after = masked_probs_list[step_idx]
valid_ids = grammar[step_idx]
invalid_ids = [i for i in range(vocab_size) if i not in valid_ids]

sum_invalid_before = probs_before[invalid_ids].sum()
sum_valid_before = probs_before[valid_ids].sum()
sum_valid_after = probs_after[valid_ids].sum()

print(f"\n--- Step {step_idx} (string value expected) ---")
print(f"Invalid token prob mass BEFORE mask: {sum_invalid_before:.3f}")
print(f"Valid token prob mass BEFORE mask:   {sum_valid_before:.3f}")
print(f"Valid token prob mass AFTER mask:    {sum_valid_after:.3f}")
print("The invalid mass was redistributed to valid tokens.")

# Plot 1: Probability distributions before and after masking
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
colors_before = ['green' if i in valid_ids else 'red' for i in range(vocab_size)]
colors_after = ['green' if i in valid_ids else 'gray' for i in range(vocab_size)]

axes[0].bar(range(vocab_size), probs_before, color=colors_before)
axes[0].set_title(f'Step {step_idx}: Before Mask')
axes[0].set_xlabel('Token Index')
axes[0].set_ylabel('Probability')
axes[0].set_xticks(range(vocab_size))
axes[0].set_xticklabels([v[:6] for v in vocab], rotation=45, ha='right')

axes[1].bar(range(vocab_size), probs_after, color=colors_after)
axes[1].set_title(f'Step {step_idx}: After Mask')
axes[1].set_xlabel('Token Index')
axes[1].set_ylabel('Probability')
axes[1].set_xticks(range(vocab_size))
axes[1].set_xticklabels([v[:6] for v in vocab], rotation=45, ha='right')

plt.tight_layout()
plt.savefig('src/phase115/mask_comparison.png')
plt.close()

# Plot 2: Heatmap of valid mask across all decoding steps
fig, ax = plt.subplots(figsize=(10, 6))
mask_matrix = np.array(valid_masks)  # shape (num_steps, vocab_size)
im = ax.imshow(mask_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
ax.set_title('Valid Token Mask at Each Decoding Step')
ax.set_xlabel('Token Index')
ax.set_ylabel('Decoding Step')
ax.set_xticks(range(vocab_size))
ax.set_xticklabels([v[:6] for v in vocab], rotation=45, ha='right')
ax.set_yticks(range(num_steps))
fig.colorbar(im, ax=ax, label='Allowed (1) / Blocked (0)')
plt.tight_layout()
plt.savefig('src/phase115/valid_mask_heatmap.png')
plt.close()

print("\nPlots saved to src/phase115/")

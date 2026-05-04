#!/usr/bin/env python3
"""
Phase 132: Mixture of Depths — NumPy Concept Demo
==================================================
This script simulates dynamic depth routing to demonstrate:

  1. Per-token router scores that estimate token difficulty
  2. Easy tokens exiting after shallow layers (early exit)
  3. Hard tokens continuing through all layers (full depth)
  4. FLOPs saved versus a static baseline
  5. Visualization of compute allocation across positions

Key insight: not all tokens need the same compute. Articles and
punctuation are easy; rare words and logical connectors are hard.
Dynamic depth routing matches compute to difficulty.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(132)

# =============================================================================
# SECTION 1: TOY VOCABULARY AND DIFFICULTY SCORES
# =============================================================================
# We define a vocabulary and assign synthetic difficulty scores.
# WHY synthetic? Real router scores come from a learned layer, but
# the concept is identical: some tokens are easy, others are hard.

VOCAB = [
    "the", "a", "an",          # determiners: very easy
    "is", "are", "was",        # copulas: easy
    "and", "or", "but",        # conjunctions: easy
    ",", ".", ";",              # punctuation: very easy
    "cat", "dog", "bird",      # common nouns: medium
    "sat", "ran", "sang",      # common verbs: medium
    "quantum", "entanglement", # rare words: hard
    "therefore", "however",    # logical connectors: hard
    "nonlocal", "epistemology",# very rare: very hard
]

word_to_idx = {w: i for i, w in enumerate(VOCAB)}

# Synthetic difficulty scores (0 = trivial, 1 = very hard)
DIFFICULTY = {
    "the": 0.05, "a": 0.05, "an": 0.05,
    "is": 0.08, "are": 0.08, "was": 0.08,
    "and": 0.06, "or": 0.06, "but": 0.10,
    ",": 0.02, ".": 0.02, ";": 0.03,
    "cat": 0.25, "dog": 0.25, "bird": 0.25,
    "sat": 0.22, "ran": 0.22, "sang": 0.28,
    "quantum": 0.85, "entanglement": 0.90,
    "therefore": 0.75, "however": 0.70,
    "nonlocal": 0.95, "epistemology": 0.92,
}

# Sequences to process
SEQUENCES = [
    ["the", "cat", "sat", "."],
    ["the", "dog", "ran", "and", "the", "bird", "sang", "."],
    ["quantum", "entanglement", "is", "nonlocal", "."],
    ["the", "cat", "sat", ",", "however", ",", "the", "dog", "ran", "."],
    ["a", "bird", "sang", ",", "therefore", ",", "the", "epistemology", "is", "hard", "."],
]

# =============================================================================
# SECTION 2: DYNAMIC DEPTH ROUTER
# =============================================================================
# The router assigns each token to a depth based on its difficulty score.
# WHY top-k? We limit the number of tokens that can go deep to prevent
# the average depth from creeping back up to the full model size.

TOTAL_LAYERS = 12
SHALLOW_EXIT = 4
MEDIUM_EXIT = 8
DEEP_EXIT = 12

CAPACITY_FACTOR = 0.5  # at most 50% of tokens can go deep

def route_tokens(sequence, total_layers=TOTAL_LAYERS, capacity=CAPACITY_FACTOR):
    """
    Assign each token to an exit layer based on difficulty.
    WHY capacity factor? Without it, every token would eventually go deep
    because the router has no incentive to save compute.
    """
    scores = np.array([DIFFICULTY.get(w, 0.5) for w in sequence])
    n_deep = max(1, int(np.ceil(len(sequence) * capacity)))

    # Top-k tokens by difficulty go to full depth
    deep_threshold = np.partition(scores, -n_deep)[-n_deep]

    depths = []
    for s in scores:
        if s >= deep_threshold:
            depths.append(DEEP_EXIT)
        elif s >= 0.3:
            depths.append(MEDIUM_EXIT)
        elif s >= 0.1:
            depths.append(SHALLOW_EXIT)
        else:
            depths.append(max(1, SHALLOW_EXIT // 2))  # very shallow

    return np.array(depths), scores


# =============================================================================
# SECTION 3: COMPUTE FLOPs CALCULATION
# =============================================================================
# We model FLOPs as proportional to token-layer passes.
# WHY proportional? In a transformer, FLOPs scale linearly with depth
# and quadratically with sequence length for attention.

def compute_flops(depths, seq_len, attn_overhead=1.2):
    """
    Compute relative FLOPs for a sequence.
    WHY attn_overhead? Attention is O(n^2) in sequence length, so longer
    sequences cost more per layer than shorter ones.
    """
    # Base FLOPs: sum of depths
    base = depths.sum()
    # Attention overhead scales with sequence length
    total = base * attn_overhead * (1 + 0.01 * seq_len)
    return total


# =============================================================================
# SECTION 4: RUN SIMULATION
# =============================================================================

print("=" * 70)
print("Phase 132: Mixture of Depths — NumPy Concept Demo")
print("=" * 70)

results = []
static_flops_all = []
dynamic_flops_all = []

for seq in SEQUENCES:
    depths, scores = route_tokens(seq)
    static_depths = np.full(len(seq), TOTAL_LAYERS)

    static_flops = compute_flops(static_depths, len(seq))
    dynamic_flops = compute_flops(depths, len(seq))

    static_flops_all.append(static_flops)
    dynamic_flops_all.append(dynamic_flops)

    savings = (static_flops - dynamic_flops) / static_flops * 100

    results.append({
        'sequence': seq,
        'depths': depths,
        'scores': scores,
        'static_flops': static_flops,
        'dynamic_flops': dynamic_flops,
        'savings': savings,
    })

    print(f"\nSequence: {' '.join(seq)}")
    print(f"  Tokens:     {seq}")
    print(f"  Scores:     {scores.round(2)}")
    print(f"  Depths:     {depths}")
    print(f"  Static FLOPs:  {static_flops:.1f}")
    print(f"  Dynamic FLOPs: {dynamic_flops:.1f}")
    print(f"  Savings:    {savings:.1f}%")

# Summary
total_static = sum(static_flops_all)
total_dynamic = sum(dynamic_flops_all)
total_savings = (total_static - total_dynamic) / total_static * 100

print(f"\n--- Overall Summary ---")
print(f"Total static FLOPs:   {total_static:.1f}")
print(f"Total dynamic FLOPs:  {total_dynamic:.1f}")
print(f"Overall savings:      {total_savings:.1f}%")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Depth allocation heatmap across sequences
ax = axes[0, 0]
max_len = max(len(r['sequence']) for r in results)
depth_matrix = np.zeros((len(results), max_len))
for i, r in enumerate(results):
    depth_matrix[i, :len(r['depths'])] = r['depths']

im = ax.imshow(depth_matrix, aspect='auto', cmap='YlOrRd', vmin=0, vmax=TOTAL_LAYERS)
ax.set_yticks(range(len(results)))
ax.set_yticklabels([f"Seq {i+1}" for i in range(len(results))])
ax.set_xlabel('Token Position')
ax.set_title('Depth Allocation per Token (darker = deeper)')
cbar = plt.colorbar(im, ax=ax, fraction=0.046)
cbar.set_label('Layers Used')

# Add token labels
for i, r in enumerate(results):
    for j, word in enumerate(r['sequence']):
        color = 'white' if r['depths'][j] >= MEDIUM_EXIT else 'black'
        ax.text(j, i, word, ha='center', va='center', fontsize=7, color=color)

# Plot 2: FLOPs comparison bar chart
ax = axes[0, 1]
x = np.arange(len(results))
width = 0.35
static_vals = [r['static_flops'] for r in results]
dynamic_vals = [r['dynamic_flops'] for r in results]
ax.bar(x - width/2, static_vals, width, label='Static (all layers)', color='#e74c3c', edgecolor='black')
ax.bar(x + width/2, dynamic_vals, width, label='Dynamic (MoD)', color='#27ae60', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels([f"Seq {i+1}" for i in x])
ax.set_ylabel('Relative FLOPs')
ax.set_title('Compute: Static vs. Dynamic Routing')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Savings percentage per sequence
ax = axes[1, 0]
savings_vals = [r['savings'] for r in results]
colors = ['#27ae60' if s > 30 else '#f1c40f' if s > 15 else '#e74c3c' for s in savings_vals]
bars = ax.bar(x, savings_vals, color=colors, edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels([f"Seq {i+1}" for i in x])
ax.set_ylabel('FLOPs Savings (%)')
ax.set_title('Compute Savings per Sequence')
ax.axhline(total_savings, color='black', linestyle='--', linewidth=2, label=f'Average: {total_savings:.1f}%')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, max(savings_vals) * 1.2)

# Plot 4: Difficulty score vs. depth scatter
ax = axes[1, 1]
all_scores = []
all_depths = []
all_colors = []
for r in results:
    all_scores.extend(r['scores'])
    all_depths.extend(r['depths'])
    all_colors.extend(range(len(r['scores'])))

scatter = ax.scatter(all_scores, all_depths, c=all_colors, cmap='tab10', s=120, edgecolors='black', alpha=0.8)
ax.set_xlabel('Token Difficulty Score')
ax.set_ylabel('Layers Allocated')
ax.set_title('Difficulty Score vs. Compute Depth')
ax.set_yticks([1, 4, 8, 12])
ax.grid(True, alpha=0.3)

# Annotate a few interesting points
for r in results:
    for j, word in enumerate(r['sequence']):
        if r['scores'][j] > 0.6 or r['scores'][j] < 0.1:
            ax.annotate(word, (r['scores'][j], r['depths'][j]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8)

plt.tight_layout()
os.makedirs('src/phase132', exist_ok=True)
plt.savefig('src/phase132/mod_concepts.png', dpi=150)
print("\nSaved plot to src/phase132/mod_concepts.png")

# =============================================================================
# SECTION 6: EARLY EXIT DEMONSTRATION
# =============================================================================
# We simulate early exit with a confidence threshold.
# WHY separate from MoD? Early exit uses a confidence probe, not a router.

print("\n" + "=" * 70)
print("EARLY EXIT DEMONSTRATION")
print("=" * 70)

CONFIDENCE_THRESHOLD = 0.85
PATIENCE = 2

for seq in SEQUENCES[:3]:
    print(f"\nSequence: {' '.join(seq)}")
    # Simulate confidence rising with depth
    exit_layers = []
    for word in seq:
        base_conf = 1.0 - DIFFICULTY.get(word, 0.5)  # easy words start confident
        confs = []
        for layer in range(1, TOTAL_LAYERS + 1):
            # Confidence rises with depth, saturates differently per word
            conf = base_conf + (1 - base_conf) * (layer / TOTAL_LAYERS) ** (1 + DIFFICULTY.get(word, 0.5))
            confs.append(min(conf, 0.99))

        # Apply patience: need PATIENCE consecutive layers above threshold
        exit_layer = TOTAL_LAYERS
        consecutive = 0
        for layer_idx, conf in enumerate(confs):
            if conf >= CONFIDENCE_THRESHOLD:
                consecutive += 1
                if consecutive >= PATIENCE:
                    exit_layer = layer_idx + 1
                    break
            else:
                consecutive = 0
        exit_layers.append(exit_layer)

    print(f"  Exit layers: {exit_layers}")
    print(f"  Avg layers:  {np.mean(exit_layers):.1f} / {TOTAL_LAYERS}")
    print(f"  Savings:     {(1 - np.mean(exit_layers)/TOTAL_LAYERS)*100:.1f}%")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Simulated {len(SEQUENCES)} sequences with dynamic depth routing")
print(f"Static compute: {total_static:.1f} relative FLOPs")
print(f"Dynamic compute: {total_dynamic:.1f} relative FLOPs")
print(f"Overall savings: {total_savings:.1f}%")
print(f"Capacity factor: {CAPACITY_FACTOR} (max {CAPACITY_FACTOR*100:.0f}% tokens deep)")
print(f"\nKey lessons:")
print("  1. Easy tokens (articles, punctuation) need only shallow layers.")
print("  2. Hard tokens (rare words, logic) benefit from full depth.")
print("  3. A capacity factor prevents all tokens from taking the deep path.")
print("  4. Dynamic routing saves 30-50% of compute with small quality loss.")
print("  5. Early exit is a simpler alternative using confidence thresholds.")
print("  6. Patience prevents premature exits on local confidence spikes.")
print("  7. The compute allocation pattern reveals which tokens the model finds hard.")
print("=" * 70)

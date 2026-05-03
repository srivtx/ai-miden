"""
FRONTIER TRACK: Phase 113 — KV Cache Compression Concepts
Local NumPy simulation of H2O, SnapKV, and memory comparison.
This script demonstrates WHY each compression technique works,
not just WHAT it does.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# WHY: We need reproducible synthetic data so the demo is deterministic
# and the "heavy hitter" tokens are baked into the ground truth.
# ---------------------------------------------------------------------------
np.random.seed(113)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
SEQ_LEN = 512          # Length of the synthetic long sequence
N_HEADS = 4            # Number of attention heads (simplified)
D_HEAD = 32            # Dimension per head
N_LAYERS = 6           # Number of transformer layers
LOCAL_WINDOW = 64      # H2O local window size (recent tokens always kept)
HEAVY_HITTER_BUDGET = 64   # H2O global heavy-hitters to retain
SNAPKV_BUDGET = 96     # SnapKV total retained tokens after prefill

# ---------------------------------------------------------------------------
# STEP 1: Simulate a sequence with "heavy hitter" tokens
# WHY: In real text, certain tokens (names, numbers, key entities) are
# attended to repeatedly. We inject synthetic importance so we can
# verify that H2O correctly identifies and keeps them.
# ---------------------------------------------------------------------------
base_scores = np.random.lognormal(mean=-2.5, sigma=1.2, size=(N_HEADS, SEQ_LEN))
# Inject heavy hitters: a few tokens get boosted across all heads
heavy_indices = np.array([50, 120, 200, 310, 400])
for idx in heavy_indices:
    base_scores[:, idx] += np.random.uniform(2.0, 4.0, size=N_HEADS)

# Normalize per head to sum to 1 (softmax-like)
attn_scores = base_scores / base_scores.sum(axis=1, keepdims=True)

# ---------------------------------------------------------------------------
# STEP 2: Simulate FULL KV cache memory
# WHY: This is the baseline. Every token stores K and V for every layer
# and every head. This is the O(n) memory wall.
# ---------------------------------------------------------------------------
bytes_per_vec = D_HEAD * 2          # FP16 = 2 bytes per float
kv_pairs_per_token = N_LAYERS * N_HEADS * 2   # K + V for each layer/head
memory_full = SEQ_LEN * kv_pairs_per_token * bytes_per_vec
print(f"[FULL KV] Sequence length: {SEQ_LEN}")
print(f"[FULL KV] Memory per token: {kv_pairs_per_token * bytes_per_vec} bytes")
print(f"[FULL KV] Total memory: {memory_full / 1024**2:.2f} MB")

# ---------------------------------------------------------------------------
# STEP 3: Implement H2O eviction
# WHY: H2O keeps a local window (recent tokens) plus the top-k tokens by
# cumulative attention score. This approximates full attention because
# the heavy-hitters capture most of the attention mass.
# ---------------------------------------------------------------------------
cumulative_attn = attn_scores.sum(axis=0)   # Sum across heads
# Recent local window is always kept
local_mask = np.zeros(SEQ_LEN, dtype=bool)
local_mask[-LOCAL_WINDOW:] = True

# Global heavy hitters: top tokens outside the local window
global_scores = cumulative_attn.copy()
global_scores[local_mask] = -np.inf        # Do not count local tokens
heavy_hitter_indices = np.argsort(global_scores)[-HEAVY_HITTER_BUDGET:]

h2o_mask = local_mask.copy()
h2o_mask[heavy_hitter_indices] = True

memory_h2o = h2o_mask.sum() * kv_pairs_per_token * bytes_per_vec
print(f"[H2O] Retained tokens: {h2o_mask.sum()} (local={LOCAL_WINDOW}, heavy={HEAVY_HITTER_BUDGET})")
print(f"[H2O] Total memory: {memory_h2o / 1024**2:.2f} MB")
print(f"[H2O] Compression ratio: {1 - memory_h2o / memory_full:.2%}")

# ---------------------------------------------------------------------------
# STEP 4: Simulate SnapKV prefill observation
# WHY: SnapKV observes attention patterns across ALL layers during prefill,
# pools them, and compresses before generation. We simulate multi-layer
# attention by adding layer-specific shifts to the base scores.
# ---------------------------------------------------------------------------
layer_attn = np.zeros((N_LAYERS, N_HEADS, SEQ_LEN))
for layer in range(N_LAYERS):
    # Deeper layers attend more narrowly; earlier layers attend broadly
    noise = np.random.lognormal(mean=-2.0 - 0.1 * layer, sigma=1.0, size=(N_HEADS, SEQ_LEN))
    layer_attn[layer] = base_scores * (1 + 0.2 * layer) + noise

# Pool across layers and heads: max pooling to capture peak importance
pooled_importance = layer_attn.max(axis=(0, 1))   # Max over layers and heads
snapkv_indices = np.argsort(pooled_importance)[-SNAPKV_BUDGET:]

snapkv_mask = np.zeros(SEQ_LEN, dtype=bool)
snapkv_mask[snapkv_indices] = True

memory_snapkv = snapkv_mask.sum() * kv_pairs_per_token * bytes_per_vec
print(f"[SnapKV] Retained tokens: {snapkv_mask.sum()}")
print(f"[SnapKV] Total memory: {memory_snapkv / 1024**2:.2f} MB")
print(f"[SnapKV] Compression ratio: {1 - memory_snapkv / memory_full:.2%}")

# ---------------------------------------------------------------------------
# STEP 5: Approximate accuracy by checking if heavy hitters are retained
# WHY: In real models, accuracy correlates with whether the most-attended
# tokens are present in the KV cache. We use a synthetic proxy:
# the fraction of true heavy-hitters that each method retains.
# ---------------------------------------------------------------------------
def retention_of_ground_truth(mask, ground_truth_indices):
    return np.isin(ground_truth_indices, np.where(mask)[0]).mean()

h2o_retention = retention_of_ground_truth(h2o_mask, heavy_indices)
snapkv_retention = retention_of_ground_truth(snapkv_mask, heavy_indices)
print(f"[Accuracy proxy] H2O heavy-hitter retention: {h2o_retention:.2%}")
print(f"[Accuracy proxy] SnapKV heavy-hitter retention: {snapkv_retention:.2%}")

# ---------------------------------------------------------------------------
# STEP 6: Visualize attention heatmap and retained tokens
# WHY: Humans cannot inspect 512-dimensional vectors. Heatmaps make it
# obvious where attention concentrates and whether compression keeps the
# right tokens.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Attention scores for head 0
ax = axes[0, 0]
im = ax.imshow(attn_scores[0:1, :], aspect='auto', cmap='hot', vmin=0)
ax.set_title('Attention Scores (Head 0)')
ax.set_xlabel('Token Position')
ax.set_yticks([])
fig.colorbar(im, ax=ax)
for idx in heavy_indices:
    ax.axvline(idx, color='cyan', linestyle='--', alpha=0.7, label='Ground-truth heavy' if idx == heavy_indices[0] else '')
ax.legend(loc='upper right')

# Plot 2: Cumulative attention across all heads
ax = axes[0, 1]
ax.plot(cumulative_attn, color='steelblue', label='Cumulative attention')
ax.scatter(heavy_indices, cumulative_attn[heavy_indices], color='red', zorder=5, label='Ground-truth heavy hitters')
ax.set_title('Cumulative Attention (H2O Input)')
ax.set_xlabel('Token Position')
ax.set_ylabel('Cumulative Score')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Retained tokens comparison
ax = axes[1, 0]
ax.barh(['Full KV', 'H2O', 'SnapKV'],
        [memory_full, memory_h2o, memory_snapkv],
        color=['gray', 'forestgreen', 'darkorange'])
ax.set_title('Memory Usage Comparison')
ax.set_xlabel('Bytes')
for i, v in enumerate([memory_full, memory_h2o, memory_snapkv]):
    ax.text(v + memory_full * 0.01, i, f"{v / 1024**2:.1f} MB", va='center')

# Plot 4: Compression ratio vs accuracy proxy
ax = axes[1, 1]
methods = ['H2O', 'SnapKV']
ratios = [1 - memory_h2o / memory_full, 1 - memory_snapkv / memory_full]
retentions = [h2o_retention, snapkv_retention]
ax.scatter(ratios, retentions, s=200, c=['forestgreen', 'darkorange'])
for i, m in enumerate(methods):
    ax.annotate(m, (ratios[i], retentions[i]), textcoords="offset points", xytext=(10, 0), fontsize=12)
ax.set_xlabel('Compression Ratio')
ax.set_ylabel('Heavy-Hitter Retention (accuracy proxy)')
ax.set_title('Compression vs Accuracy Trade-off')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.1)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase113/kv_compression_comparison.png', dpi=150)
print("[Plot saved] src/phase113/kv_compression_comparison.png")

# ---------------------------------------------------------------------------
# STEP 7: Simulate PyramidKV layer-wise budgets
# WHY: Not all layers need the same context. Early layers (0-2) attend
# broadly and can tolerate aggressive compression. Deep layers (4-5)
# attend narrowly to semantic tokens and need more budget.
# ---------------------------------------------------------------------------
layer_budgets = [32, 48, 64, 80, 96, 128]   # Increasing budget with depth
pyramid_masks = []
for layer, budget in enumerate(layer_budgets):
    # Use layer-specific attention to choose retained tokens
    layer_importance = layer_attn[layer].max(axis=0)
    topk = np.argsort(layer_importance)[-budget:]
    mask = np.zeros(SEQ_LEN, dtype=bool)
    mask[topk] = True
    pyramid_masks.append(mask)

pyramid_memory = sum(m.sum() for m in pyramid_masks) * N_HEADS * bytes_per_vec * 2  # K+V per layer
print(f"[PyramidKV] Total tokens across layers: {sum(m.sum() for m in pyramid_masks)}")
print(f"[PyramidKV] Memory: {pyramid_memory / 1024**2:.2f} MB")
print(f"[PyramidKV] Compression vs full: {1 - pyramid_memory / memory_full:.2%}")

# ---------------------------------------------------------------------------
# FINAL INSIGHT SUMMARY
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("KEY INSIGHT: KV cache compression is the only way to scale")
print("to million-token contexts without multiplying GPU memory.")
print("H2O uses cumulative attention to keep globally important tokens.")
print("SnapKV uses prefill observation to see the future importance.")
print("PyramidKV uses layer-specific budgets to compress where it hurts least.")
print("=" * 60)

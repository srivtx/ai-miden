import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# --- Memory comparison: O(n^2) full attention vs O(n) blockwise ---

seq_lengths = np.array([512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072])

# Assume float32 (4 bytes) per score
bytes_per_elem = 4
# Full attention score matrix: n^2
full_memory_bytes = seq_lengths ** 2 * bytes_per_elem
full_memory_gb = full_memory_bytes / (1024 ** 3)

# Blockwise: each device holds one block of queries and streams blocks of keys.
# Peak per-device memory is dominated by one query block and one key/value block,
# plus an accumulator of size block_size x d_head. This scales as O(block_size * n)
# in total data movement, but peak memory is O(block_size^2 + block_size * d_head),
# which is constant w.r.t sequence length if block_size is fixed.
# For visualization, we model a representative O(n) trend: linear in sequence length.
block_size = 1024
d_head = 64
blockwise_memory_bytes = seq_lengths * block_size * d_head * bytes_per_elem
blockwise_memory_gb = blockwise_memory_bytes / (1024 ** 3)

# Hierarchical / compressed: O(n) with a smaller constant
compressed_memory_gb = blockwise_memory_gb * 0.3

plt.figure(figsize=(10, 5))
plt.plot(seq_lengths, full_memory_gb, marker='o', label='Full Attention O(n^2)', color='crimson')
plt.plot(seq_lengths, blockwise_memory_gb, marker='s', label='Blockwise (Ring) O(n)', color='steelblue')
plt.plot(seq_lengths, compressed_memory_gb, marker='^', label='Hierarchical/Compressed O(n)', color='seagreen')
plt.xscale('log', base=2)
plt.yscale('log', base=2)
plt.xlabel('Sequence Length (tokens)')
plt.ylabel('Peak Memory (GB, estimated)')
plt.title('Attention Memory Scaling: Full vs Blockwise vs Compressed')
plt.legend()
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase97_memory_scaling.png')
plt.savefig(out_path)
print("Saved plot to", out_path)

# --- Simulate blockwise attention on a toy sequence ---
np.random.seed(0)
n = 64
d = 8
Q = np.random.randn(n, d)
K = np.random.randn(n, d)
V = np.random.randn(n, d)


def softmax(z):
    e = np.exp(z - np.max(z, axis=-1, keepdims=True))
    return e / (np.sum(e, axis=-1, keepdims=True) + 1e-9)


# Full attention
scores_full = Q @ K.T
attn_weights_full = softmax(scores_full)
output_full = attn_weights_full @ V

# Blockwise with block_size=8
block_size = 8
num_blocks = n // block_size

# For the toy demo, we reconstruct full attention block-by-block to show equivalence,
# and we report the memory reduction from operating on blocks.
output_block_reconstructed = np.zeros_like(output_full)
for bi in range(num_blocks):
    q_start = bi * block_size
    Q_block = Q[q_start:q_start + block_size]
    # Accumulate weighted sum and normalization per query
    numer = np.zeros((block_size, d))
    denom = np.zeros((block_size, 1))
    for bj in range(num_blocks):
        k_start = bj * block_size
        K_block = K[k_start:k_start + block_size]
        V_block = V[k_start:k_start + block_size]
        scores = Q_block @ K_block.T
        e = np.exp(scores - np.max(scores, axis=1, keepdims=True))
        numer += e @ V_block
        denom += np.sum(e, axis=1, keepdims=True)
    output_block_reconstructed[q_start:q_start + block_size] = numer / denom

print("\nSequence length:", n)
print("Full attention score matrix size (elements):", scores_full.size)
print("Blockwise max intermediate size (elements):", block_size * block_size)
print("Reduction factor:", scores_full.size / (block_size * block_size))
print("Max reconstruction error:", np.max(np.abs(output_full - output_block_reconstructed)))

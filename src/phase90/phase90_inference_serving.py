import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: In autoregressive generation, each sequence needs KV cache.
# Variable lengths cause fragmentation in a contiguous allocator.

np.random.seed(90)

num_requests = 20
max_seq_len = 1024
max_cache_size = 4096

# Simulate sequence lengths
seq_lengths = np.random.randint(50, 300, size=num_requests)

# WHY: A naive fixed allocator gives each request a max-size slot.
# Most of that slot is wasted for short sequences.
naive_wasted = num_requests * max_seq_len - seq_lengths.sum()
naive_utilization = seq_lengths.sum() / (num_requests * max_seq_len)

print(f"Naive total allocated: {num_requests * max_seq_len}")
print(f"Naive actual used: {seq_lengths.sum()}")
print(f"Naive utilization: {naive_utilization:.2%}")

# WHY: PagedAttention splits cache into fixed-size blocks (e.g., 16 tokens).
# A request gets only the blocks it needs, reducing waste.
block_size = 16
blocks_needed = np.ceil(seq_lengths / block_size).astype(int)
total_blocks = max_cache_size // block_size
paged_allocated = blocks_needed.sum() * block_size
paged_utilization = seq_lengths.sum() / paged_allocated

print(f"Paged total allocated: {paged_allocated}")
print(f"Paged actual used: {seq_lengths.sum()}")
print(f"Paged utilization: {paged_utilization:.2%}")

# WHY: Show fragmentation over time as requests arrive and depart.
timesteps = 50
frag_naive = []
frag_paged = []
active = []

for t in range(timesteps):
    # arrivals and departures
    if t % 5 == 0 and len(active) < 8:
        active.append(np.random.randint(50, 300))
    if t % 7 == 0 and active:
        active.pop(0)

    if not active:
        frag_naive.append(0)
        frag_paged.append(0)
        continue

    total_naive = len(active) * max_seq_len
    total_used = sum(active)
    frag_naive.append(1 - total_used / total_naive)

    blocks = sum(int(np.ceil(s / block_size)) for s in active) * block_size
    frag_paged.append(1 - total_used / blocks)

fig, ax = plt.subplots()
ax.plot(frag_naive, label='Naive Contiguous Fragmentation')
ax.plot(frag_paged, label='Paged Fragmentation')
ax.set_ylabel('Fragmentation Ratio')
ax.set_xlabel('Time Step')
ax.set_title('KV Cache: Naive vs PagedAttention')
ax.legend()
fig.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase90/kv_cache_fragmentation.png')
print("Saved plot to kv_cache_fragmentation.png")

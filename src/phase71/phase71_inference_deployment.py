#!/usr/bin/env python3
"""
Phase 71: Inference & Deployment — NumPy Concept Demo
=======================================================
This script simulates the core tension of model serving: latency vs. throughput.
We do NOT train a model. Instead, we use NumPy to model GPU inference behavior
and show WHY batching, dynamic scheduling, and memory management matter.

Key insights demonstrated:
  1. Latency grows with batch size, but not linearly (GPU parallelism helps).
  2. Throughput peaks and then saturates (memory bandwidth is the bottleneck).
  3. Dynamic batching + bucketing reduces padding waste versus static batching.
  4. Memory usage is dominated by KV cache, which scales with batch * seq_len.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(71)

# =============================================================================
# SECTION 1: GPU INFERENCE MODEL
# =============================================================================
# In reality, a forward pass has:
#   - Fixed overhead: kernel launch, memory copy, Python overhead (~15 ms)
#   - Variable cost: batch_size * seq_len * per_token_time
# GPU parallelization means per_token_time DROPS as batch_size grows,
# but only up to a point. Eventually memory bandwidth saturates.

FIXED_OVERHEAD_MS = 15.0          # ms: constant for every forward pass
PER_TOKEN_BASE_MS = 2.0           # ms per token when batch_size = 1
MAX_BATCH = 64
SEQ_LEN = 20                      # average tokens per sequence for curves
MODEL_WEIGHTS_MB = 2000.0         # e.g., 2 GB for a quantized 7B model
KV_PER_TOKEN_MB = 0.002           # rough KV-cache footprint per token

batch_sizes = np.arange(1, MAX_BATCH + 1)

# Per-token time drops with batch size (better SIMD utilization),
# then saturates around batch=32 due to memory bandwidth limits.
# We model this with an exponential decay.
per_token_time = PER_TOKEN_BASE_MS * (0.5 + 0.5 * np.exp(-batch_sizes / 16.0))

# Total latency to process ONE batch (all sequences in parallel)
latency_ms = FIXED_OVERHEAD_MS + batch_sizes * SEQ_LEN * per_token_time

# Throughput = total tokens processed per second
throughput_tok_per_sec = (batch_sizes * SEQ_LEN) / (latency_ms / 1000.0)

# Memory = model weights + KV cache for every token in the batch
memory_mb = MODEL_WEIGHTS_MB + batch_sizes * SEQ_LEN * KV_PER_TOKEN_MB

print("=" * 60)
print("Phase 71: Inference & Deployment — NumPy Concept Demo")
print("=" * 60)
print(f"\nFixed overhead per forward pass: {FIXED_OVERHEAD_MS} ms")
print(f"Base per-token time (batch=1):   {PER_TOKEN_BASE_MS} ms")
print(f"Sequence length for curves:      {SEQ_LEN} tokens")
print(f"Model weights footprint:         {MODEL_WEIGHTS_MB} MB")

# =============================================================================
# SECTION 2: SIMULATE INCOMING REQUEST TRAFFIC
# =============================================================================
# Real traffic is bursty and variable-length. We simulate 1,000 requests
# with Poisson-distributed lengths and exponential inter-arrival times.

N_REQUESTS = 1000
request_lengths = np.random.poisson(lam=20, size=N_REQUESTS) + 1
inter_arrival_ms = np.random.exponential(scale=10.0, size=N_REQUESTS)  # ~10 ms avg
arrival_times_ms = np.cumsum(inter_arrival_ms)

BUCKET_EDGES = [1, 8, 16, 32, 64, 128]

# =============================================================================
# SECTION 3: STATIC BATCHING SIMULATION
# =============================================================================
# Static batching waits for a FIXED number of requests, pads them all to the
# longest sequence in the batch, and runs one forward pass. This is simple
# but wasteful: short sequences pay for long ones.

def simulate_static_batching(lengths, times, batch_size):
    """Process requests in fixed-size batches."""
    latencies = []
    current_time = 0.0
    idx = 0
    while idx < len(lengths):
        batch_end = min(idx + batch_size, len(lengths))
        actual_batch = batch_end - idx
        max_len = lengths[idx:batch_end].max()

        # GPU parallelism factor for this batch size
        ptt = PER_TOKEN_BASE_MS * (0.5 + 0.5 * np.exp(-actual_batch / 16.0))
        batch_latency = FIXED_OVERHEAD_MS + actual_batch * max_len * ptt

        # Batch starts when the FIRST request arrives AND the GPU is free
        start_time = max(current_time, times[idx])
        finish_time = start_time + batch_latency

        for i in range(idx, batch_end):
            latencies.append(finish_time - times[i])

        current_time = finish_time
        idx = batch_end
    return np.array(latencies)

# =============================================================================
# SECTION 4: DYNAMIC BATCHING SIMULATION
# =============================================================================
# Dynamic batching waits a short TIME window (not a fixed count), then groups
# requests by LENGTH BUCKET before padding. This minimizes wasted compute.

def simulate_dynamic_batching(lengths, times, max_wait_ms, buckets):
    """Group requests arriving within a time window into length buckets."""
    latencies = []
    idx = 0
    current_time = 0.0
    while idx < len(lengths):
        window_start = max(current_time, times[idx])
        window_deadline = window_start + max_wait_ms

        # Collect all requests that arrived by the deadline
        j = idx
        while j < len(times) and times[j] <= window_deadline:
            j += 1

        batch_lengths = lengths[idx:j]
        # Bucket the batch to minimize padding
        last_finish = window_start
        for b_start, b_end in zip(buckets[:-1], buckets[1:]):
            mask = (batch_lengths >= b_start) & (batch_lengths < b_end)
            if not mask.any():
                continue
            bucket_count = mask.sum()
            bucket_max = batch_lengths[mask].max()
            ptt = PER_TOKEN_BASE_MS * (0.5 + 0.5 * np.exp(-bucket_count / 16.0))
            batch_latency = FIXED_OVERHEAD_MS + bucket_count * bucket_max * ptt
            finish_time = window_start + batch_latency
            if finish_time > last_finish:
                last_finish = finish_time
            # All requests in this bucket finish at the same time
            for _ in range(bucket_count):
                latencies.append(finish_time - window_start)
        idx = j
        # Advance GPU time to when the last bucket in this window finishes
        current_time = last_finish
    return np.array(latencies)

# =============================================================================
# SECTION 5: RUN SIMULATIONS
# =============================================================================

static_lat_8 = simulate_static_batching(request_lengths, arrival_times_ms, 8)
static_lat_32 = simulate_static_batching(request_lengths, arrival_times_ms, 32)
dynamic_lat = simulate_dynamic_batching(request_lengths, arrival_times_ms, 20, BUCKET_EDGES)

# =============================================================================
# SECTION 6: PADDING WASTE ANALYSIS
# =============================================================================
# Padding waste = sum(max_length_in_batch - actual_length) for every request.
# Lower is better. We simulate 100 random batches of size 16.

np.random.seed(71)
padding_waste_static = []
padding_waste_dynamic = []
for _ in range(100):
    lens = np.random.poisson(20, size=16) + 1
    # Static: pad all to global max in batch
    waste_static = np.sum(lens.max() - lens)
    # Dynamic: bucket into length bins
    waste_dynamic = 0
    for b_start, b_end in zip(BUCKET_EDGES[:-1], BUCKET_EDGES[1:]):
        mask = (lens >= b_start) & (lens < b_end)
        if mask.any():
            waste_dynamic += np.sum(lens[mask].max() - lens[mask])
    padding_waste_static.append(waste_static)
    padding_waste_dynamic.append(waste_dynamic)

padding_waste_static = np.array(padding_waste_static)
padding_waste_dynamic = np.array(padding_waste_dynamic)

# =============================================================================
# SECTION 7: CONTINUOUS BATCHING CONCEPT
# =============================================================================
# Continuous batching (vLLM-style) means new requests join the GPU as soon
# as others finish. We model this as a sawtooth vs. flat utilization curve.

steps = np.arange(0, 100)
# Static: batch of 32 runs for 32 steps, then GPU idles while next batch forms
static_util = np.zeros_like(steps, dtype=float)
for start in range(0, 100, 40):
    end = min(start + 32, 100)
    static_util[start:end] = 1.0

# Continuous: new requests arrive every few steps, GPU never idles
continuous_util = np.ones_like(steps, dtype=float)
continuous_util[::10] = 0.9  # tiny dips when scheduler swaps batches

# =============================================================================
# SECTION 8: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Plot 1: Latency vs. Batch Size
ax = axes[0, 0]
ax.plot(batch_sizes, latency_ms, 'b-', linewidth=2, label='Batch latency')
optimal_batch = batch_sizes[np.argmax(throughput_tok_per_sec)]
ax.axvline(x=optimal_batch, color='r', linestyle='--', alpha=0.7,
           label=f'Throughput peak @ {optimal_batch}')
ax.set_xlabel('Batch Size')
ax.set_ylabel('Latency (ms)')
ax.set_title('Latency vs. Batch Size')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Throughput vs. Batch Size
ax = axes[0, 1]
ax.plot(batch_sizes, throughput_tok_per_sec, 'g-', linewidth=2)
ax.axvline(x=optimal_batch, color='r', linestyle='--', alpha=0.7)
ax.set_xlabel('Batch Size')
ax.set_ylabel('Throughput (tokens/sec)')
ax.set_title('Throughput vs. Batch Size')
ax.grid(True, alpha=0.3)

# Plot 3: Memory Usage vs. Batch Size
ax = axes[0, 2]
ax.plot(batch_sizes, memory_mb, 'm-', linewidth=2)
ax.axhline(y=MODEL_WEIGHTS_MB, color='gray', linestyle=':',
           label='Model weights only')
ax.set_xlabel('Batch Size')
ax.set_ylabel('GPU Memory (MB)')
ax.set_title('Memory Usage vs. Batch Size')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Latency Distribution (Static vs. Dynamic)
ax = axes[1, 0]
ax.hist(static_lat_8, bins=50, alpha=0.6, label='Static batch=8', color='blue')
ax.hist(dynamic_lat, bins=50, alpha=0.6, label='Dynamic batching', color='orange')
ax.set_xlabel('Request Latency (ms)')
ax.set_ylabel('Count')
ax.set_title('Latency Distribution: Static vs. Dynamic')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: Throughput Scaling Efficiency
ax = axes[1, 1]
ideal_throughput = throughput_tok_per_sec[0] * batch_sizes
efficiency = throughput_tok_per_sec / ideal_throughput * 100.0
ax.plot(batch_sizes, efficiency, 'c-', linewidth=2)
ax.axhline(y=100, color='gray', linestyle=':', label='Perfect linear')
ax.set_xlabel('Batch Size')
ax.set_ylabel('Scaling Efficiency (%)')
ax.set_title('Throughput Scaling Efficiency')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 6: Padding Waste Comparison
ax = axes[1, 2]
x_pos = np.arange(20)  # show first 20 batches for clarity
ax.bar(x_pos - 0.2, padding_waste_static[:20], width=0.4,
       alpha=0.7, label='Static padding waste', color='red')
ax.bar(x_pos + 0.2, padding_waste_dynamic[:20], width=0.4,
       alpha=0.7, label='Dynamic padding waste', color='green')
ax.set_xlabel('Batch index')
ax.set_ylabel('Wasted tokens (padding)')
ax.set_title('Padding Waste: Static vs. Dynamic Bucketing')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase71', exist_ok=True)
plt.savefig('src/phase71/inference_deployment.png', dpi=150)
print("\nSaved plot to src/phase71/inference_deployment.png")

# =============================================================================
# SECTION 9: SUMMARY
# =============================================================================

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Optimal batch size (throughput peak): {optimal_batch}")
print(f"Max throughput:                       {throughput_tok_per_sec.max():.0f} tokens/sec")
print(f"Latency at batch=1:                   {latency_ms[0]:.1f} ms")
print(f"Latency at batch={MAX_BATCH}:                  {latency_ms[-1]:.1f} ms")
print(f"Mean static latency (batch=8):        {static_lat_8.mean():.1f} ms")
print(f"Mean static latency (batch=32):       {static_lat_32.mean():.1f} ms")
print(f"Mean dynamic latency:                 {dynamic_lat.mean():.1f} ms")
print(f"Avg padding waste static:             {padding_waste_static.mean():.1f} tokens")
print(f"Avg padding waste dynamic:            {padding_waste_dynamic.mean():.1f} tokens")
print(f"Padding reduction from dynamic:       {(1 - padding_waste_dynamic.mean() / padding_waste_static.mean()) * 100:.1f}%")
print("\nKey takeaways:")
print("  - Throughput peaks early; larger batches hurt latency without much gain.")
print("  - Dynamic batching reduces padding waste and keeps latency predictable.")
print("  - Memory grows linearly with batch size; KV cache is the hidden killer.")
print("  - Continuous batching (vLLM) keeps GPU utilization flat near 100%.")

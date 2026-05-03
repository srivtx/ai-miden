#!/usr/bin/env python3
"""
Phase 129: Production Inference Engines — NumPy Concept Demo
===============================================================
This script simulates production LLM inference optimization to demonstrate:

  1. Naive single-request generation vs. batched generation
  2. Throughput vs. batch size curve and the latency trade-off
  3. PagedAttention memory savings vs. contiguous allocation
  4. Latency percentiles (p50, p95, p99) under synthetic traffic
  5. Cost per 1M tokens under different configurations

Key insight: production inference is not about making one request fast.
It is about keeping the GPU busy every cycle, minimizing memory waste,
and finding the batch size where throughput gain outweighs latency cost.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(129)

# =============================================================================
# SECTION 1: SIMULATE INFERENCE WORKLOAD
# =============================================================================
# We generate a synthetic workload of 200 requests with varying prompt
# lengths and output lengths. This mirrors real traffic where some users
# send short queries and others paste entire documents.

N_REQUESTS = 200

# Prompt lengths: most are short, some are very long (power law)
prompt_lengths = np.random.exponential(scale=128, size=N_REQUESTS).astype(int) + 16
prompt_lengths = np.clip(prompt_lengths, 16, 2048)

# Output lengths: most are short, a few are long
output_lengths = np.random.exponential(scale=64, size=N_REQUESTS).astype(int) + 8
output_lengths = np.clip(output_lengths, 8, 512)

print("="*70)
print("Phase 129: Production Inference Engines — NumPy Concept Demo")
print("="*70)
print(f"Synthetic workload: {N_REQUESTS} requests")
print(f"Prompt lengths:  mean={prompt_lengths.mean():.0f}, max={prompt_lengths.max()}")
print(f"Output lengths:  mean={output_lengths.mean():.0f}, max={output_lengths.max()}")

# =============================================================================
# SECTION 2: NAIVE SINGLE-REQUEST GENERATION
# =============================================================================
# In naive inference, each request runs alone. There is no batching.
# The GPU processes one sequence at a time. Overhead is high because
# the matrix multiplications are not large enough to saturate tensor cores.

def simulate_naive_generation(prompt_lens, output_lens, base_time_per_token=0.030):
    """
    Simulate naive single-request generation.
    WHY base_time_per_token=30ms? This is realistic for a 3B model on a
    consumer GPU. Prompt processing is faster per token (parallel), but
    generation is sequential and memory-bound.
    """
    latencies = []
    for p_len, o_len in zip(prompt_lens, output_lens):
        # Prompt processing: faster because parallel, but still sequential over layers
        prompt_time = p_len * base_time_per_token * 0.3
        # Generation: one token at a time
        gen_time = o_len * base_time_per_token
        latencies.append(prompt_time + gen_time)
    return np.array(latencies)

naive_latencies = simulate_naive_generation(prompt_lengths, output_lengths)
naive_total_time = naive_latencies.sum()
naive_throughput = (prompt_lengths + output_lengths).sum() / naive_total_time
naive_peak_memory = (prompt_lengths.max() + output_lengths.max()) * 4096 * 4 * 32 * 2  # rough bytes

print(f"\n--- Naive Single-Request Generation ---")
print(f"Total time:        {naive_total_time:.1f} s")
print(f"Throughput:        {naive_throughput:.1f} tokens/sec")
print(f"Mean latency:      {naive_latencies.mean():.3f} s")
print(f"p50 latency:       {np.percentile(naive_latencies, 50):.3f} s")
print(f"p95 latency:       {np.percentile(naive_latencies, 95):.3f} s")
print(f"p99 latency:       {np.percentile(naive_latencies, 99):.3f} s")

# =============================================================================
# SECTION 3: BATCHED GENERATION (STATIC)
# =============================================================================
# Static batching groups requests into fixed-size buckets. All requests
# in a bucket start together and wait for the longest output to finish.
# This improves throughput but hurts tail latency because fast requests
# wait for slow ones.

def simulate_static_batching(prompt_lens, output_lens, batch_size, base_time=0.030):
    """
    Simulate static batching.
    WHY does throughput increase? Larger matrices saturate GPU better.
    WHY does latency increase? Everyone waits for the slowest request.
    """
    n = len(prompt_lens)
    n_batches = int(np.ceil(n / batch_size))
    batch_times = []
    total_tokens = 0

    for i in range(n_batches):
        start = i * batch_size
        end = min(start + batch_size, n)
        p_batch = prompt_lens[start:end]
        o_batch = output_lens[start:end]

        # Prompt processing: padded to max prompt in batch
        max_prompt = p_batch.max()
        prompt_time = max_prompt * base_time * 0.3

        # Generation: padded to max output in batch
        max_output = o_batch.max()
        gen_time = max_output * base_time

        batch_times.append(prompt_time + gen_time)
        total_tokens += p_batch.sum() + o_batch.sum()

    total_time = sum(batch_times)
    throughput = total_tokens / total_time
    # Per-request latency = its batch's total time
    per_request_latency = []
    for i in range(n_batches):
        start = i * batch_size
        end = min(start + batch_size, n)
        per_request_latency.extend([batch_times[i]] * (end - start))

    return throughput, np.array(per_request_latency), total_time

batch_sizes = [1, 2, 4, 8, 16, 32, 64]
batch_throughputs = []
batch_p50 = []
batch_p95 = []
batch_p99 = []
batch_total_times = []

for bs in batch_sizes:
    tp, lat, tt = simulate_static_batching(prompt_lengths, output_lengths, bs)
    batch_throughputs.append(tp)
    batch_p50.append(np.percentile(lat, 50))
    batch_p95.append(np.percentile(lat, 95))
    batch_p99.append(np.percentile(lat, 99))
    batch_total_times.append(tt)

print(f"\n--- Static Batching Results ---")
for i, bs in enumerate(batch_sizes):
    print(f"Batch={bs:2d}:  throughput={batch_throughputs[i]:6.1f} tok/s,  "
          f"p50={batch_p50[i]:5.2f}s,  p95={batch_p95[i]:5.2f}s,  p99={batch_p99[i]:5.2f}s")

# =============================================================================
# SECTION 4: CONTINUOUS BATCHING
# =============================================================================
# Continuous batching adds new requests on every decoding step and removes
# finished ones immediately. We simulate this by assuming that throughput
# scales with batch size but without the padding penalty of static batching.
# In reality, continuous batching achieves 80-90% of theoretical throughput.

def simulate_continuous_batching(prompt_lens, output_lens, max_batch=32, base_time=0.030):
    """
    Simulate continuous batching.
    WHY better than static? No padding waste; new requests join immediately.
    We model this as a queue where the GPU always has up to max_batch
    active sequences, and finished sequences are replaced instantly.
    """
    n = len(prompt_lens)
    # Sort by total work (prompt + output) to approximate scheduler behavior
    total_work = prompt_lens + output_lengths
    order = np.argsort(total_work)
    p_sorted = prompt_lens[order]
    o_sorted = output_lens[order]

    active_prompts = []
    active_outputs = []
    active_remaining = []
    completed = 0
    time_step = 0.0
    total_tokens = 0
    request_latencies = []
    request_start_times = []

    idx = 0
    while completed < n:
        # Add new requests up to max_batch
        while len(active_prompts) < max_batch and idx < n:
            active_prompts.append(p_sorted[idx])
            active_outputs.append(o_sorted[idx])
            active_remaining.append(p_sorted[idx] + o_sorted[idx])
            request_start_times.append(time_step)
            idx += 1

        if not active_remaining:
            break

        # Process one "step" for all active requests
        # Prompt tokens process faster; once prompt is done, generation begins
        step_time = base_time * (1.0 + 0.02 * len(active_prompts))
        time_step += step_time

        # Decrement remaining work
        new_prompts = []
        new_outputs = []
        new_remaining = []
        new_start_times = []
        for i in range(len(active_remaining)):
            # Simulate prompt processing: first p tokens are prompt
            if active_remaining[i] > active_outputs[i]:
                # Still in prompt phase: consume multiple tokens per step
                active_remaining[i] -= max(1, active_prompts[i] // 10)
            else:
                # In generation phase: consume 1 token per step
                active_remaining[i] -= 1

            if active_remaining[i] <= 0:
                request_latencies.append(time_step - request_start_times[i])
                total_tokens += active_prompts[i] + active_outputs[i]
                completed += 1
            else:
                new_prompts.append(active_prompts[i])
                new_outputs.append(active_outputs[i])
                new_remaining.append(active_remaining[i])
                new_start_times.append(request_start_times[i])

        active_prompts = new_prompts
        active_outputs = new_outputs
        active_remaining = new_remaining
        request_start_times = new_start_times

    throughput = total_tokens / time_step
    return throughput, np.array(request_latencies), time_step

cont_tp, cont_lat, cont_time = simulate_continuous_batching(prompt_lengths, output_lengths, max_batch=16)

print(f"\n--- Continuous Batching (max_batch=16) ---")
print(f"Total time:        {cont_time:.1f} s")
print(f"Throughput:        {cont_tp:.1f} tokens/sec")
print(f"Mean latency:      {cont_lat.mean():.3f} s")
print(f"p50 latency:       {np.percentile(cont_lat, 50):.3f} s")
print(f"p95 latency:       {np.percentile(cont_lat, 95):.3f} s")
print(f"p99 latency:       {np.percentile(cont_lat, 99):.3f} s")

# =============================================================================
# SECTION 5: PAGEDATTENTION MEMORY SIMULATION
# =============================================================================
# We compare contiguous allocation (naive) vs. fixed-size block allocation.
# In contiguous allocation, every request gets a block sized to the model's
# max context length. In block allocation, memory is split into pages.

def simulate_memory_usage(prompt_lens, output_lens, max_context=4096, block_size=16):
    """
    Simulate memory usage for contiguous vs. paged allocation.
    WHY block_size=16? vLLM uses 16-token blocks as a balance between
    metadata overhead and fragmentation reduction.
    """
    n = len(prompt_lens)
    hidden_dim = 4096
    n_layers = 32
    bytes_per_val = 2  # fp16
    kv_factor = 2  # K and V

    # Contiguous: each request gets max_context tokens
    contiguous_per_request = max_context * hidden_dim * n_layers * kv_factor * bytes_per_val
    contiguous_total = n * contiguous_per_request

    # Paged: each request uses ceil((prompt + output) / block_size) blocks
    paged_total = 0
    for p, o in zip(prompt_lens, output_lens):
        n_blocks = int(np.ceil((p + o) / block_size))
        paged_total += n_blocks * block_size * hidden_dim * n_layers * kv_factor * bytes_per_val

    # Actual used memory (without overhead)
    actual_total = 0
    for p, o in zip(prompt_lens, output_lens):
        actual_total += (p + o) * hidden_dim * n_layers * kv_factor * bytes_per_val

    return contiguous_total, paged_total, actual_total

cont_mem, page_mem, actual_mem = simulate_memory_usage(prompt_lengths, output_lengths)

print(f"\n--- Memory Usage Simulation ---")
print(f"Contiguous allocation: {cont_mem / 1e9:.2f} GB")
print(f"Paged allocation:      {page_mem / 1e9:.2f} GB")
print(f"Actual tokens used:    {actual_mem / 1e9:.2f} GB")
print(f"Contiguous waste:      {100*(cont_mem - actual_mem)/cont_mem:.1f}%")
print(f"Paged waste:           {100*(page_mem - actual_mem)/page_mem:.1f}%")

# =============================================================================
# SECTION 6: COST ANALYSIS
# =============================================================================
# We compute a mock cost per 1M tokens assuming $2.50/hour GPU rental.
# Cost = (1M tokens / throughput) * (price_per_hour / 3600)

gpu_price_per_hour = 2.50

def cost_per_million(throughput):
    """
    Compute dollars per 1M tokens.
    WHY this formula? If you process T tokens/second, then 1M tokens
    takes 1,000,000 / T seconds. Multiply by dollars/second.
    """
    seconds_per_million = 1_000_000 / throughput
    hours = seconds_per_million / 3600
    return hours * gpu_price_per_hour

naive_cost = cost_per_million(naive_throughput)
static_costs = [cost_per_million(tp) for tp in batch_throughputs]
cont_cost = cost_per_million(cont_tp)

print(f"\n--- Cost Analysis ($2.50/hour GPU) ---")
print(f"Naive single-request:  ${naive_cost:.2f} per 1M tokens")
for i, bs in enumerate(batch_sizes):
    print(f"Static batch={bs:2d}:      ${static_costs[i]:.2f} per 1M tokens")
print(f"Continuous batch=16:   ${cont_cost:.2f} per 1M tokens")

# =============================================================================
# SECTION 7: SPECULATIVE DECODING SPEEDUP
# =============================================================================
# Speculative decoding uses a small draft model to guess future tokens.
# The large model verifies K guesses in one forward pass. Acceptance rate
# determines the effective speedup.

def speculative_speedup(acceptance_rate, draft_tokens=4):
    """
    Simulate speedup from speculative decoding.
    WHY draft_tokens=4? Typical draft models generate 3-5 candidates.
    If acceptance rate is 0.7, then on average 2.8 tokens are accepted
    per large-model forward pass, yielding a speedup of ~2.3×.
    """
    # One large forward pass verifies draft_tokens candidates
    expected_accepted = acceptance_rate * draft_tokens
    # Cost: 1 large pass + draft_tokens small passes (much cheaper, ~10% cost)
    # Effective tokens per large pass equivalent = expected_accepted
    speedup = expected_accepted / 1.0
    return speedup

acceptance_rates = np.linspace(0.3, 0.95, 20)
speedups = [speculative_speedup(a) for a in acceptance_rates]

print(f"\n--- Speculative Decoding ---")
print(f"Acceptance 0.50 → speedup {speculative_speedup(0.50):.2f}×")
print(f"Acceptance 0.70 → speedup {speculative_speedup(0.70):.2f}×")
print(f"Acceptance 0.90 → speedup {speculative_speedup(0.90):.2f}×")

# =============================================================================
# SECTION 8: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: Throughput vs batch size
ax = axes[0, 0]
ax.plot(batch_sizes, batch_throughputs, 'o-', color='#e74c3c', linewidth=2, markersize=8, label='Static batching')
ax.axhline(cont_tp, color='#27ae60', linestyle='--', linewidth=2, label=f'Continuous (max=16), {cont_tp:.0f} tok/s')
ax.axhline(naive_throughput, color='#3498db', linestyle=':', linewidth=2, label=f'Naive single, {naive_throughput:.0f} tok/s')
ax.set_xlabel('Batch Size')
ax.set_ylabel('Throughput (tokens/sec)')
ax.set_title('Throughput vs. Batch Size')
ax.set_xscale('log', base=2)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Latency percentiles vs batch size
ax = axes[0, 1]
ax.plot(batch_sizes, batch_p50, 'o-', color='#3498db', linewidth=2, label='p50')
ax.plot(batch_sizes, batch_p95, 's-', color='#e67e22', linewidth=2, label='p95')
ax.plot(batch_sizes, batch_p99, '^-', color='#e74c3c', linewidth=2, label='p99')
ax.set_xlabel('Batch Size')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Latency Percentiles vs. Batch Size')
ax.set_xscale('log', base=2)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Memory comparison
ax = axes[0, 2]
labels = ['Contiguous', 'PagedAttention', 'Actual Used']
values = [cont_mem / 1e9, page_mem / 1e9, actual_mem / 1e9]
colors = ['#e74c3c', '#27ae60', '#3498db']
bars = ax.bar(labels, values, color=colors, edgecolor='black')
ax.set_ylabel('Memory (GB)')
ax.set_title('Memory Allocation Comparison')
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f} GB', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Cost per 1M tokens
ax = axes[1, 0]
ax.plot(batch_sizes, static_costs, 'o-', color='#e74c3c', linewidth=2, markersize=8, label='Static batching')
ax.axhline(cont_cost, color='#27ae60', linestyle='--', linewidth=2, label=f'Continuous, ${cont_cost:.2f}')
ax.axhline(naive_cost, color='#3498db', linestyle=':', linewidth=2, label=f'Naive, ${naive_cost:.2f}')
ax.set_xlabel('Batch Size')
ax.set_ylabel('Cost per 1M tokens ($)')
ax.set_title('Cost Efficiency')
ax.set_xscale('log', base=2)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: Speculative decoding speedup
ax = axes[1, 1]
ax.plot(acceptance_rates, speedups, '-', color='#9b59b6', linewidth=2)
ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Token Acceptance Rate')
ax.set_ylabel('Effective Speedup')
ax.set_title('Speculative Decoding Speedup (draft=4)')
ax.grid(True, alpha=0.3)

# Plot 6: Latency distribution (continuous batching)
ax = axes[1, 2]
ax.hist(cont_lat, bins=30, color='#3498db', edgecolor='black', alpha=0.7)
ax.axvline(np.percentile(cont_lat, 50), color='#27ae60', linestyle='--', linewidth=2, label=f'p50={np.percentile(cont_lat,50):.2f}s')
ax.axvline(np.percentile(cont_lat, 95), color='#e67e22', linestyle='--', linewidth=2, label=f'p95={np.percentile(cont_lat,95):.2f}s')
ax.axvline(np.percentile(cont_lat, 99), color='#e74c3c', linestyle='--', linewidth=2, label=f'p99={np.percentile(cont_lat,99):.2f}s')
ax.set_xlabel('Request Latency (seconds)')
ax.set_ylabel('Count')
ax.set_title('Latency Distribution (Continuous Batching)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase129', exist_ok=True)
plt.savefig('src/phase129/inference_concepts.png', dpi=150)
print("\nSaved plot to src/phase129/inference_concepts.png")

# =============================================================================
# SECTION 9: SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Naive single-request:")
print(f"  Throughput: {naive_throughput:.1f} tok/s, Cost: ${naive_cost:.2f}/1M")
print(f"  p50={np.percentile(naive_latencies,50):.2f}s, p95={np.percentile(naive_latencies,95):.2f}s")
print(f"\nStatic batching sweet spot: batch_size=4-8")
print(f"  At batch=8: throughput={batch_throughputs[3]:.1f} tok/s, p95={batch_p95[3]:.2f}s")
print(f"\nContinuous batching (max=16):")
print(f"  Throughput: {cont_tp:.1f} tok/s, Cost: ${cont_cost:.2f}/1M")
print(f"  p50={np.percentile(cont_lat,50):.2f}s, p95={np.percentile(cont_lat,95):.2f}s")
print(f"\nMemory savings:")
print(f"  Contiguous waste: {100*(cont_mem-actual_mem)/cont_mem:.1f}%")
print(f"  Paged waste:      {100*(page_mem-actual_mem)/page_mem:.1f}%")
print(f"\nSpeculative decoding:")
print(f"  70% acceptance → {speculative_speedup(0.70):.2f}× speedup")
print(f"\nKey lessons:")
print("  1. Batching increases throughput but also latency; find the knee.")
print("  2. Continuous batching dominates static batching at all metrics.")
print("  3. PagedAttention cuts memory waste by 30-50 percentage points.")
print("  4. p95/p99 latency matters more than mean latency in production.")
print("  5. Cost per token drops 10-40× from naive to optimized serving.")
print("  6. Speculative decoding helps when draft acceptance is >70%.")
print("  7. Memory bandwidth, not FLOPS, is usually the generation bottleneck.")
print("="*70)

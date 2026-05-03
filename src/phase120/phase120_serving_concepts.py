#!/usr/bin/env python3
"""
Phase 120: Disaggregated Serving — NumPy Concept Demo
======================================================
This script simulates LLM inference serving architectures to demonstrate
why prefill and decode phases need different treatment. We cover:

  1. Prefill phase: compute-bound prompt processing
  2. Decode phase: memory-bandwidth-bound token generation
  3. Colocated serving: both phases on the same GPU (inefficient)
  4. Disaggregated serving: separate prefill and decode GPU pools
  5. Chunked prefill: interleaving prefill chunks with decode steps

Key insight: prefill and decode have opposite hardware bottlenecks.
Prefill wants compute (FLOPs). Decode wants memory bandwidth (GB/s).
Running them on the same hardware means one resource is always wasted.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(120)

# =============================================================================
# SECTION 1: HARDWARE AND MODEL PARAMETERS
# =============================================================================
# We simulate a 7B-parameter model running on A100-class hardware.
# These are realistic approximations used for concept demonstration.

hidden_dim = 4096
num_heads = 32
head_dim = hidden_dim // num_heads  # 128
num_layers = 32
vocab_size = 32000
bytes_per_param = 2  # fp16

# A100-like specs
compute_peak_tflops = 312  # theoretical FP16 peak
memory_bw_gbps = 2039      # HBM bandwidth

# Model size
model_size_gb = (num_layers * hidden_dim * hidden_dim * 4 * bytes_per_param) / 1e9
print("="*70)
print("Phase 120: Disaggregated Serving and Prefill/Decode Separation")
print("="*70)
print(f"Model: ~7B parameters")
print(f"Hidden dim: {hidden_dim}, Layers: {num_layers}, Heads: {num_heads}")
print(f"Model size (FP16): {model_size_gb:.1f} GB")
print(f"GPU compute peak: {compute_peak_tflops} TFLOP/s")
print(f"GPU memory BW: {memory_bw_gbps} GB/s")

# =============================================================================
# SECTION 2: PHASE PROFILING FORMULAS
# =============================================================================
# Prefill: one large forward pass over the full prompt.
#   FLOPs ~ 2 * batch * seq_len^2 * num_heads * head_dim (attention)
#          + 2 * batch * seq_len * hidden_dim^2 * num_layers (FFN)
# Decode: one token at a time. Must load KV cache for ALL prior tokens.
#   Memory: 2 * seq_len * hidden_dim * bytes_per_param per layer

def prefill_time(prompt_len, batch_size=1):
    """
    Time for prefill phase in milliseconds.
    Prefill is compute-bound; we estimate based on attention FLOPs.
    """
    # Attention FLOPs: Q@K^T + softmax + attention@V
    # Simplified: 2 * batch * seq^2 * hidden_dim
    attn_flops = 2 * batch_size * prompt_len * prompt_len * hidden_dim
    # FFN FLOPs: 2 * batch * seq * hidden_dim^2 * num_layers * 2 (up+down)
    ffn_flops = 4 * batch_size * prompt_len * hidden_dim * hidden_dim * num_layers
    total_flops = attn_flops + ffn_flops

    # Assume 60% compute utilization for prefill (good utilization)
    effective_tflops = compute_peak_tflops * 0.60
    time_ms = (total_flops / 1e12) / effective_tflops * 1000
    return time_ms

def decode_time_one_token(seq_len, batch_size=1):
    """
    Time for one decode token in milliseconds.
    Decode is memory-bandwidth-bound; we estimate based on KV cache reads.
    """
    # Must load KV cache for all prior tokens, all layers
    kv_cache_per_layer = 2 * seq_len * hidden_dim * bytes_per_param
    total_kv_read = kv_cache_per_layer * num_layers * batch_size

    # Also load model weights (amortized across batch)
    weight_read = model_size_gb * 1e9 / batch_size

    total_bytes = total_kv_read + weight_read

    # Assume 70% memory bandwidth utilization for decode
    effective_bw = memory_bw_gbps * 0.70 * 1e9
    time_ms = (total_bytes / effective_bw) * 1000
    return time_ms

# =============================================================================
# SECTION 3: PROFILE PREFILL VS DECODE SCALING
# =============================================================================
prompt_lengths = [128, 256, 512, 1024, 2048]
prefill_times = [prefill_time(l) for l in prompt_lengths]

# Decode time at various sequence lengths (generating the NEXT token)
decode_seq_lengths = list(range(128, 2049, 128))
decode_times = [decode_time_one_token(s) for s in decode_seq_lengths]

print(f"\n--- Prefill Time vs Prompt Length ---")
for pl, pt in zip(prompt_lengths, prefill_times):
    print(f"  {pl:4d} tokens: {pt:6.2f} ms")

print(f"\n--- Decode Time per Token vs Sequence Length ---")
for i in range(0, len(decode_seq_lengths), 2):
    sl = decode_seq_lengths[i]
    dt = decode_times[i]
    print(f"  seq_len={sl:4d}: {dt:.3f} ms/token")

# =============================================================================
# SECTION 4: COLOCATED SERVING SIMULATION
# =============================================================================
# In colocated serving, each GPU handles full requests: prefill then decode.
# We simulate a batch of requests and measure completion time.

def simulate_colocated(requests, n_gpus):
    """
    requests: list of (prompt_len, output_len)
    Returns total time and per-request latency.
    WHY batch decodes? Real serving engines (vLLM, TGI) use continuous
    batching: after prefilling a request, its decode steps are batched
    with other active requests. This is more realistic than sequential.
    """
    # Round-robin assign requests to GPUs
    gpu_queues = [[] for _ in range(n_gpus)]
    for i, req in enumerate(requests):
        gpu_queues[i % n_gpus].append(req)

    gpu_times = []
    for gpu_id, queue in enumerate(gpu_queues):
        t = 0
        active_decodes = []  # list of (prompt_len, output_len, tokens_done)
        req_idx = 0
        # Process requests with continuous batching simulation
        while req_idx < len(queue) or active_decodes:
            # Prefill up to one new request if queue remains
            if req_idx < len(queue):
                pl, ol = queue[req_idx]
                t += prefill_time(pl)
                active_decodes.append([pl, ol, 0])
                req_idx += 1

            # Run one decode step for ALL active requests (batched)
            if active_decodes:
                # Batched decode time: dominated by max seq length in batch
                max_seq = max(d[0] + d[2] for d in active_decodes)
                B = len(active_decodes)
                kv_cache_per_layer = 2 * max_seq * hidden_dim * bytes_per_param * B
                weight_read = model_size_gb * 1e9
                total_bytes = kv_cache_per_layer + weight_read
                effective_bw = memory_bw_gbps * 0.70 * 1e9
                step_time_ms = (total_bytes / effective_bw) * 1000
                # Add scheduling overhead for heterogeneous batch
                step_time_ms *= 1.15
                t += step_time_ms

                # Advance all active decodes
                new_active = []
                for d in active_decodes:
                    d[2] += 1
                    if d[2] < d[1]:
                        new_active.append(d)
                active_decodes = new_active

        gpu_times.append(t)

    # Total time is the max across GPUs (they run in parallel)
    total_time_ms = max(gpu_times)
    return total_time_ms

# Generate a realistic request distribution
np.random.seed(120)
n_requests = 64
prompt_lens = np.random.choice([128, 512, 1024], size=n_requests)
output_lens = np.random.choice([50, 100, 200], size=n_requests)
requests = list(zip(prompt_lens, output_lens))

n_gpus_colocated = 8
colocated_time = simulate_colocated(requests, n_gpus_colocated)
colocated_throughput = n_requests / (colocated_time / 1000)

print(f"\n--- Colocated Serving ({n_gpus_colocated} GPUs) ---")
print(f"Total completion time: {colocated_time/1000:.2f} seconds")
print(f"Throughput: {colocated_throughput:.2f} requests/sec")
print(f"Avg time per request: {colocated_time/n_requests:.1f} ms")

# =============================================================================
# SECTION 5: DISAGGREGATED SERVING SIMULATION
# =============================================================================
# Prefill GPUs process prompts only. Decode GPUs generate tokens only.
# KV cache handoff happens between clusters.

def simulate_disaggregated(requests, n_prefill_gpus, n_decode_gpus):
    """
    Simulate disaggregated serving with separate prefill and decode pools.
    WHY add transfer overhead? KV cache must move from prefill GPUs to
    decode GPUs. Even with NVLink, this adds 1-3ms per request.
    """
    # Split requests across prefill GPUs
    prefill_batches = [[] for _ in range(n_prefill_gpus)]
    for i, req in enumerate(requests):
        prefill_batches[i % n_prefill_gpus].append(req)

    # Time for prefill cluster to finish all prompts
    prefill_times_per_gpu = []
    for batch in prefill_batches:
        t = sum(prefill_time(pl) for pl, _ in batch)
        prefill_times_per_gpu.append(t)
    prefill_total_ms = max(prefill_times_per_gpu)

    # KV cache transfer time per request (NVLink ~900 GB/s, protocol overhead ~2ms)
    kv_size_gb = (2 * 512 * hidden_dim * bytes_per_param * num_layers) / 1e9
    transfer_ms_per_req = kv_size_gb / 900 * 1000 + 2.0  # ~2.3ms per request

    # Decode cluster: assign requests round-robin, but decode can batch
    decode_batches = [[] for _ in range(n_decode_gpus)]
    for i, req in enumerate(requests):
        decode_batches[i % n_decode_gpus].append(req)

    decode_times_per_gpu = []
    for batch in decode_batches:
        B = len(batch)
        if B == 0:
            decode_times_per_gpu.append(0)
            continue
        avg_prompt = int(np.mean([pl for pl, _ in batch]))
        avg_output = int(np.mean([ol for _, ol in batch]))

        # Batched decode: each step processes B tokens
        t = 0
        for tok in range(avg_output):
            seq_len = avg_prompt + tok
            kv_cache_per_layer = 2 * seq_len * hidden_dim * bytes_per_param * B
            weight_read = model_size_gb * 1e9
            total_bytes = kv_cache_per_layer + weight_read
            effective_bw = memory_bw_gbps * 0.70 * 1e9
            step_time_ms = (total_bytes / effective_bw) * 1000
            t += step_time_ms

        # Add transfer overhead for this batch
        t += transfer_ms_per_req * B
        decode_times_per_gpu.append(t)

    decode_total_ms = max(decode_times_per_gpu)

    # Total time: prefill and decode run pipelined
    total_time_ms = max(prefill_total_ms, decode_total_ms)
    return total_time_ms

n_prefill = 4
n_decode = 4
disagg_time = simulate_disaggregated(requests, n_prefill, n_decode)
disagg_throughput = n_requests / (disagg_time / 1000)

print(f"\n--- Disaggregated Serving ({n_prefill} prefill + {n_decode} decode GPUs) ---")
print(f"Total completion time: {disagg_time/1000:.2f} seconds")
print(f"Throughput: {disagg_throughput:.2f} requests/sec")
print(f"Speedup vs colocated: {colocated_time/disagg_time:.2f}x")

# =============================================================================
# SECTION 6: CHUNKED PREFILL SIMULATION
# =============================================================================
# Instead of monolithic prefills, process prompts in chunks and interleave
# decode steps. This prevents decode requests from starving.

def simulate_chunked_prefill(requests, n_gpus, chunk_size=256):
    """
    Simulate chunked prefill where long prefills are broken into chunks
    and decode steps are interleaved with other requests.
    WHY continuous batching? Real serving engines run decodes for ALL
    active requests between prefill chunks, not just one decode step.
    """
    gpu_queues = [[] for _ in range(n_gpus)]
    for i, req in enumerate(requests):
        gpu_queues[i % n_gpus].append(req)

    gpu_times = []
    for gpu_id, queue in enumerate(gpu_queues):
        t = 0
        active_decodes = []  # list of (prompt_len, output_len, tokens_done)
        req_idx = 0
        pending_prefills = []  # requests waiting to be chunked

        while req_idx < len(queue) or active_decodes or pending_prefills:
            # Start a new prefill if capacity exists
            if req_idx < len(queue) and len(pending_prefills) < 2:
                pending_prefills.append(list(queue[req_idx]))
                req_idx += 1

            # Process one chunk of the first pending prefill
            if pending_prefills:
                pl, ol = pending_prefills[0][:2]
                n_chunks = max(1, int(np.ceil(pl / chunk_size)))
                # Determine how many chunks already done for this request
                # We track via a counter appended to the tuple
                if len(pending_prefills[0]) < 3:
                    pending_prefills[0].append(0)  # chunks_done
                chunks_done = pending_prefills[0][2]
                tokens_in_chunk = min(chunk_size, pl - chunks_done * chunk_size)
                ctx_len = chunks_done * chunk_size

                chunk_time = prefill_time(tokens_in_chunk, batch_size=1) * 1.1
                t += chunk_time
                pending_prefills[0][2] += 1

                if pending_prefills[0][2] >= n_chunks:
                    # Prefill complete, move to active decodes
                    active_decodes.append([pl, ol, 0])
                    pending_prefills.pop(0)

            # Run one batched decode step for ALL active requests
            if active_decodes:
                max_seq = max(d[0] + d[2] for d in active_decodes)
                B = len(active_decodes)
                kv_cache_per_layer = 2 * max_seq * hidden_dim * bytes_per_param * B
                weight_read = model_size_gb * 1e9
                total_bytes = kv_cache_per_layer + weight_read
                effective_bw = memory_bw_gbps * 0.70 * 1e9
                step_time_ms = (total_bytes / effective_bw) * 1000
                # Chunked prefill has higher scheduling overhead
                step_time_ms *= 1.20
                t += step_time_ms

                new_active = []
                for d in active_decodes:
                    d[2] += 1
                    if d[2] < d[1]:
                        new_active.append(d)
                active_decodes = new_active

        gpu_times.append(t)

    return max(gpu_times)

chunked_time = simulate_chunked_prefill(requests, n_gpus_colocated, chunk_size=256)
chunked_throughput = n_requests / (chunked_time / 1000)

print(f"\n--- Chunked Prefill ({n_gpus_colocated} GPUs, chunk=256) ---")
print(f"Total completion time: {chunked_time/1000:.2f} seconds")
print(f"Throughput: {chunked_throughput:.2f} requests/sec")
print(f"Speedup vs colocated: {colocated_time/chunked_time:.2f}x")
print(f"Note: chunked helps when mixed workloads share GPUs")

# =============================================================================
# SECTION 7: THROUGHPUT VS BATCH SIZE ANALYSIS
# =============================================================================
# We show how throughput scales with batch size for colocated vs disaggregated.

batch_sizes = [1, 2, 4, 8, 16, 32]
colocated_throughputs = []
disagg_throughputs = []

for bs in batch_sizes:
    # Create a batch of identical requests
    batch_requests = [(512, 100)] * bs
    ct = simulate_colocated(batch_requests, 1) / 1000
    colocated_throughputs.append(bs / ct if ct > 0 else 0)

    dt = simulate_disaggregated(batch_requests, 1, 1) / 1000
    disagg_throughputs.append(bs / dt if dt > 0 else 0)

# =============================================================================
# SECTION 8: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Prefill time vs prompt length
ax = axes[0, 0]
ax.plot(prompt_lengths, prefill_times, 'o-', color='#e74c3c', linewidth=2, markersize=8)
ax.set_xlabel('Prompt Length (tokens)')
ax.set_ylabel('Prefill Time (ms)')
ax.set_title('Prefill Phase: Compute-Bound\nTime scales linearly with prompt length')
ax.grid(True, alpha=0.3)
for pl, pt in zip(prompt_lengths, prefill_times):
    ax.annotate(f'{pt:.1f}ms', (pl, pt), textcoords="offset points",
                xytext=(0, 10), ha='center', fontsize=8)

# Plot 2: Decode time vs sequence length
ax = axes[0, 1]
ax.plot(decode_seq_lengths, decode_times, 's-', color='#2980b9', linewidth=2, markersize=6)
ax.set_xlabel('Sequence Length (tokens)')
ax.set_ylabel('Decode Time per Token (ms)')
ax.set_title('Decode Phase: Memory-Bandwidth-Bound\nTime grows with KV cache size')
ax.grid(True, alpha=0.3)

# Plot 3: Architecture comparison (completion time)
ax = axes[1, 0]
architectures = ['Colocated', 'Disaggregated', 'Chunked Prefill']
times = [colocated_time/1000, disagg_time/1000, chunked_time/1000]
colors = ['#e74c3c', '#27ae60', '#f39c12']
bars = ax.bar(architectures, times, color=colors, edgecolor='black', alpha=0.8)
ax.set_ylabel('Total Completion Time (seconds)')
ax.set_title(f'Serving Architecture Comparison\n({n_requests} requests, {n_gpus_colocated} GPUs)')
for bar, val in zip(bars, times):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{val:.1f}s', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Throughput vs batch size
ax = axes[1, 1]
ax.plot(batch_sizes, colocated_throughputs, 'o-', color='#e74c3c', linewidth=2,
        label='Colocated', markersize=8)
ax.plot(batch_sizes, disagg_throughputs, 's-', color='#27ae60', linewidth=2,
        label='Disaggregated', markersize=8)
ax.set_xlabel('Batch Size')
ax.set_ylabel('Throughput (requests/sec)')
ax.set_title('Throughput Scaling with Batch Size')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase120', exist_ok=True)
plt.savefig('src/phase120/serving_concepts.png', dpi=150)
print("\nSaved plot to src/phase120/serving_concepts.png")

# =============================================================================
# SECTION 9: SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Hardware modeled: {compute_peak_tflops} TFLOP/s compute, {memory_bw_gbps} GB/s BW")
print(f"\nColocated serving:")
print(f"  Completion time: {colocated_time/1000:.2f}s")
print(f"  Throughput:      {colocated_throughput:.2f} req/s")
print(f"\nDisaggregated serving ({n_prefill}+{n_decode} GPUs):")
print(f"  Completion time: {disagg_time/1000:.2f}s")
print(f"  Throughput:      {disagg_throughput:.2f} req/s")
print(f"  Speedup:         {colocated_time/disagg_time:.2f}x")
print(f"\nChunked prefill:")
print(f"  Completion time: {chunked_time/1000:.2f}s")
print(f"  Throughput:      {chunked_throughput:.2f} req/s")
print(f"  Speedup:         {colocated_time/chunked_time:.2f}x")
print("\nKey lessons:")
print("  1. Prefill is compute-bound; decode is memory-bandwidth-bound")
print("  2. Colocated serving wastes one resource while using the other")
print("  3. Disaggregated serving achieves 1.5-2x+ throughput at scale")
print("  4. Chunked prefill is the software-only alternative; good but not best")
print("  5. Optimal GPU ratio depends on prompt/output length distribution")
print("="*70)

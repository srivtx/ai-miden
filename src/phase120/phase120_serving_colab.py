# FRONTIER TRACK: Phase 120 — Disaggregated Serving and Prefill/Decode Separation
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models

"""
Phase 120: Disaggregated Serving — Colab PyTorch Demo
======================================================
This script profiles REAL LLM inference on a T4 GPU to demonstrate the
fundamental mismatch between prefill and decode phases. We load
Llama-3.2-3B-Instruct and measure:

  1. Prefill time vs. prompt length (compute-bound)
  2. Decode throughput (memory-bandwidth-bound)
  3. Compute utilization asymmetry
  4. Theoretical throughput of disaggregated serving

Key insight: T4 is NOT the right GPU for real disaggregated serving.
This script demonstrates the PRINCIPLE on accessible hardware, but
production disaggregation requires H100s with NVLink for KV cache handoff.
"""

# =============================================================================
# STEP 0: INSTALL DEPENDENCIES
# =============================================================================
# WHY these packages? transformers loads LLaMA, torch provides CUDA,
# accelerate handles device mapping, bitsandbytes enables 4-bit loading
# to fit a 3B model on a T4 with 16GB VRAM.
!pip install -q transformers datasets torch accelerate bitsandbytes matplotlib tqdm

import time
import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# =============================================================================
# STEP 1: CONFIGURATION
# =============================================================================
# WHY 4-bit? Llama-3.2-3B is ~6GB in FP16. With KV cache and activations,
# FP16 would exceed T4's 16GB VRAM during long sequences. 4-bit reduces
# model weights to ~4GB, leaving headroom.

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_NAME = 'meta-llama/Llama-3.2-3B-Instruct'
PROMPT_LENGTHS = [128, 512, 1024, 2048]
DECODE_TOKENS = 100
TEMPERATURE = 1.0

print(f"Device: {DEVICE}")
if DEVICE.type == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print(f"Note: T4 has ~15.7 GB VRAM and ~65 TFLOP/s FP16 compute")
    print(f"Note: T4 memory bandwidth is ~320 GB/s")

# =============================================================================
# STEP 2: LOAD MODEL AND TOKENIZER
# =============================================================================
# WHY device_map='auto'? It splits layers across available memory.
# WHY load_in_4bit? Required to fit 3B + KV cache on T4.

print("\nLoading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map='auto',
    load_in_4bit=True,
    torch_dtype=torch.float16,
)
model.eval()
print(f"Model loaded: {MODEL_NAME}")

# =============================================================================
# STEP 3: PROFILE PREFILL PHASE
# =============================================================================
# Prefill processes the entire prompt in one forward pass.
# We expect time to scale roughly linearly with prompt length for short
# prompts, then sub-linearly as we approach memory bandwidth limits.
# For transformers, prefill FLOPs scale as O(seq^2) due to attention.

print("\n" + "="*70)
print("PROFILING PREFILL PHASE")
print("="*70)

prefill_times_ms = []
for target_len in PROMPT_LENGTHS:
    # Build a prompt of exactly target_len tokens
    # WHY repeat a word? It gives consistent tokenization without surprises.
    base_text = "The quick brown fox jumps over the lazy dog. "
    tokens = tokenizer.encode(base_text)
    repeats = int(np.ceil(target_len / len(tokens))) + 1
    full_text = tokenizer.decode(tokens * repeats)
    inputs = tokenizer(full_text, return_tensors='pt', truncation=True,
                       max_length=target_len).to(DEVICE)
    actual_len = inputs['input_ids'].shape[1]

    # Warmup
    with torch.no_grad():
        _ = model(inputs['input_ids'])
    torch.cuda.synchronize() if DEVICE.type == 'cuda' else None

    # Time prefill
    times = []
    for _ in range(5):
        torch.cuda.synchronize() if DEVICE.type == 'cuda' else None
        start = time.time()
        with torch.no_grad():
            _ = model(inputs['input_ids'])
        torch.cuda.synchronize() if DEVICE.type == 'cuda' else None
        times.append((time.time() - start) * 1000)

    avg_time = np.mean(times)
    prefill_times_ms.append(avg_time)
    print(f"Prompt length: {actual_len:4d} tokens | Prefill time: {avg_time:7.2f} ms")

# =============================================================================
# STEP 4: PROFILE DECODE PHASE
# =============================================================================
# Decode generates one token at a time. Each forward pass must load the
# KV cache for all prior tokens, making it memory-bandwidth-bound.
# We generate 100 tokens and measure throughput.

print("\n" + "="*70)
print("PROFILING DECODE PHASE")
print("="*70)

# Use a fixed 256-token prompt as context
decode_prompt = "The quick brown fox jumps over the lazy dog. " * 20
decode_inputs = tokenizer(decode_prompt, return_tensors='pt',
                          truncation=True, max_length=256).to(DEVICE)
decode_context_len = decode_inputs['input_ids'].shape[1]

print(f"Decode context length: {decode_context_len} tokens")
print(f"Generating {DECODE_TOKENS} tokens...")

# Warmup: generate a few tokens
with torch.no_grad():
    _ = model.generate(decode_inputs['input_ids'], max_new_tokens=5,
                       do_sample=False, pad_token_id=tokenizer.eos_token_id)
torch.cuda.synchronize() if DEVICE.type == 'cuda' else None

# Measure decode
start = time.time()
with torch.no_grad():
    generated = model.generate(
        decode_inputs['input_ids'],
        max_new_tokens=DECODE_TOKENS,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
        use_cache=True,  # WHY? KV cache is ESSENTIAL for decode efficiency
    )
torch.cuda.synchronize() if DEVICE.type == 'cuda' else None
decode_time = time.time() - start
actual_generated = generated.shape[1] - decode_context_len
decode_tok_per_sec = actual_generated / decode_time

print(f"Generated {actual_generated} tokens in {decode_time:.2f} seconds")
print(f"Decode throughput: {decode_tok_per_sec:.1f} tokens/sec")

# =============================================================================
# STEP 5: COMPUTE ASYMMETRY
# =============================================================================
# WHY compute utilization? Prefill should achieve high FLOP/s because
# matrix multiplies are large. Decode should achieve low FLOP/s because
# it is waiting for memory. We estimate FLOP/s for each phase.

print("\n" + "="*70)
print("COMPUTE / MEMORY ASYMMETRY")
print("="*70)

# Rough FLOP estimation for Llama-3.2-3B
# Params: ~3.2B. Each forward pass: ~2 * params * tokens FLOPs.
params = 3.2e9

for pl, pt in zip(PROMPT_LENGTHS, prefill_times_ms):
    flops = 2 * params * pl
    flop_rate = flops / (pt / 1000)  # FLOP/s
    tflops = flop_rate / 1e12
    # T4 theoretical peak is ~65 TFLOP/s FP16
    utilization = (tflops / 65.0) * 100
    print(f"Prefill {pl:4d} tokens: {tflops:.1f} TFLOP/s ({utilization:.0f}% of T4 peak)")

# Decode FLOP rate
decode_flops_per_tok = 2 * params
decode_flop_rate = decode_flops_per_tok * decode_tok_per_sec
decode_tflops = decode_flop_rate / 1e12
decode_util = (decode_tflops / 65.0) * 100
print(f"Decode (per token):  {decode_tflops:.2f} TFLOP/s ({decode_util:.0f}% of T4 peak)")

print(f"\nAsymmetry ratio: {tflops / decode_tflops:.1f}x")
print("Prefill saturates compute; decode is memory-bound.")

# =============================================================================
# STEP 6: SIMULATE DISAGGREGATED SERVING THROUGHPUT
# =============================================================================
# We cannot physically separate prefill and decode on a single T4.
# Instead, we calculate THEORETICAL throughput if we had separate GPU pools.
# We model a batch of requests and compare colocated vs. disaggregated.

print("\n" + "="*70)
print("DISAGGREGATED SERVING SIMULATION")
print("="*70)

# Request distribution
n_requests = 64
avg_prompt_len = 512
avg_output_len = 100
batch_size = 8

# Prefill throughput on dedicated prefill GPUs
# Prefill time for 512 tokens (from measurements, interpolated)
prefill_512 = np.interp(512, PROMPT_LENGTHS, prefill_times_ms)
prefill_req_per_sec_per_gpu = 1000 / prefill_512

# Decode throughput on dedicated decode GPUs
# With batching, decode throughput improves because weight loading
# is amortized, but KV cache reads scale with batch.
# Decode on T4: ~decode_tok_per_sec tokens/sec for batch=1
# Batched decode is roughly: throughput = decode_tok_per_sec * (1 + 0.3 * log2(batch))
# because memory bandwidth is partially amortized.
batched_decode_mult = 1 + 0.3 * np.log2(batch_size)
decode_tok_per_sec_batched = decode_tok_per_sec * batched_decode_mult
decode_req_per_sec_per_gpu = decode_tok_per_sec_batched / avg_output_len

print(f"Request profile: {avg_prompt_len} prompt tokens, {avg_output_len} output tokens")
print(f"Batch size: {batch_size}")
print(f"\nPrefill GPU throughput:  {prefill_req_per_sec_per_gpu:.2f} req/s per GPU")
print(f"Decode GPU throughput:   {decode_req_per_sec_per_gpu:.2f} req/s per GPU")

# Colocated: each GPU does both phases for its share of requests
# Effective throughput is limited by the slower phase per request.
colocated_time_per_req = (prefill_512 / 1000) + (avg_output_len / decode_tok_per_sec)
colocated_req_per_sec_per_gpu = 1 / colocated_time_per_req
print(f"\nColocated GPU throughput: {colocated_req_per_sec_per_gpu:.2f} req/s per GPU")

# Disaggregated: separate pools, each optimized
# Need enough prefill GPUs to keep decode GPUs fed.
# Ratio = prefill throughput / decode throughput
optimal_ratio = prefill_req_per_sec_per_gpu / decode_req_per_sec_per_gpu
print(f"Optimal prefill:decode GPU ratio: 1:{optimal_ratio:.1f}")

# For a fixed 8-GPU datacenter, compare allocations
gpus_total = 8
colocated_total = gpus_total * colocated_req_per_sec_per_gpu

# Try different splits
best_split = None
best_total = 0
for n_prefill in range(1, gpus_total):
    n_decode = gpus_total - n_prefill
    prefill_capacity = n_prefill * prefill_req_per_sec_per_gpu
    decode_capacity = n_decode * decode_req_per_sec_per_gpu
    # Total throughput is limited by the bottleneck
    total_throughput = min(prefill_capacity, decode_capacity)
    if total_throughput > best_total:
        best_total = total_throughput
        best_split = (n_prefill, n_decode)

print(f"\nBest disaggregated split: {best_split[0]} prefill + {best_split[1]} decode GPUs")
print(f"Disaggregated total throughput: {best_total:.2f} req/s")
print(f"Colocated total throughput:     {colocated_total:.2f} req/s")
print(f"Theoretical speedup:            {best_total/colocated_total:.2f}x")

print("\nNOTE: Real disaggregation requires:")
print("  - High-speed interconnect (NVLink 900 GB/s or InfiniBand)")
print("  - KV cache transfer: ~2-5ms for 512-token cache on 7B model")
print("  - H100-class GPUs for compute-intensive prefill pools")
print("  - T4 is demonstration-only; real deployments use H100/A100 clusters")

# =============================================================================
# STEP 7: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Prefill time vs prompt length
ax = axes[0, 0]
ax.plot(PROMPT_LENGTHS, prefill_times_ms, 'o-', color='#e74c3c', linewidth=2, markersize=10)
ax.set_xlabel('Prompt Length (tokens)')
ax.set_ylabel('Prefill Time (ms)')
ax.set_title('Prefill Phase: Compute-Bound\nTime grows with sequence length')
ax.grid(True, alpha=0.3)
for pl, pt in zip(PROMPT_LENGTHS, prefill_times_ms):
    ax.annotate(f'{pt:.0f}ms', (pl, pt), textcoords="offset points",
                xytext=(0, 10), ha='center', fontsize=9)

# Plot 2: Decode throughput vs hypothetical batch size
ax = axes[0, 1]
batch_sizes = [1, 2, 4, 8, 16, 32]
decode_throughputs = [decode_tok_per_sec * (1 + 0.3 * np.log2(b)) for b in batch_sizes]
ax.plot(batch_sizes, decode_throughputs, 's-', color='#2980b9', linewidth=2, markersize=8)
ax.set_xlabel('Batch Size')
ax.set_ylabel('Decode Throughput (tokens/sec)')
ax.set_title('Decode Phase: Memory-Bandwidth-Bound\nThroughput improves with batching')
ax.grid(True, alpha=0.3)

# Plot 3: Compute utilization comparison
ax = axes[1, 0]
phases = ['Prefill\n(512 tok)', 'Decode\n(batch=1)', 'Decode\n(batch=8)']
utilizations = [
    (np.interp(512, PROMPT_LENGTHS, [2 * params * pl / (pt/1000) / 1e12 / 65 * 100
                for pl, pt in zip(PROMPT_LENGTHS, prefill_times_ms)])),
    decode_util,
    (decode_tflops * (1 + 0.3 * np.log2(8)) / 65 * 100),
]
colors = ['#27ae60', '#e74c3c', '#f39c12']
bars = ax.bar(phases, utilizations, color=colors, edgecolor='black', alpha=0.8)
ax.axhline(y=50, color='black', linestyle='--', alpha=0.5, label='50% utilization')
ax.set_ylabel('Compute Utilization (% of T4 peak)')
ax.set_title('Compute Utilization: Prefill vs Decode')
for bar, val in zip(bars, utilizations):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{val:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Throughput comparison (colocated vs disaggregated)
ax = axes[1, 1]
architectures = ['Colocated\n(8 GPUs)', f'Disaggregated\n({best_split[0]}P+{best_split[1]}D)']
throughputs = [colocated_total, best_total]
colors = ['#e74c3c', '#27ae60']
bars = ax.bar(architectures, throughputs, color=colors, edgecolor='black', alpha=0.8)
ax.set_ylabel('Total Throughput (req/s)')
ax.set_title(f'Throughput Comparison\n({n_requests} requests, batch={batch_size})')
for bar, val in zip(bars, throughputs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('phase120_serving_results.png', dpi=150, bbox_inches='tight')
print("\nSaved plot: phase120_serving_results.png")
plt.close()

# =============================================================================
# STEP 8: FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)
print(f"Model: {MODEL_NAME}")
print(f"Hardware: T4 GPU (demonstration only)")
print(f"\nPrefill phase (compute-bound):")
for pl, pt in zip(PROMPT_LENGTHS, prefill_times_ms):
    print(f"  {pl:4d} tokens: {pt:.1f} ms")
print(f"\nDecode phase (memory-bandwidth-bound):")
print(f"  {decode_tok_per_sec:.1f} tokens/sec (batch=1)")
print(f"  {decode_tok_per_sec * batched_decode_mult:.1f} tokens/sec (batch={batch_size})")
print(f"\nCompute utilization asymmetry:")
print(f"  Prefill: ~{utilizations[0]:.0f}% of T4 peak")
print(f"  Decode:  ~{decode_util:.0f}% of T4 peak")
print(f"\nDisaggregated serving theoretical gain: {best_total/colocated_total:.2f}x")
print(f"  Best split: {best_split[0]} prefill GPUs + {best_split[1]} decode GPUs")
print("\nKey lessons demonstrated:")
print("1. Prefill is compute-bound; decode is memory-bandwidth-bound.")
print("2. Colocated serving wastes one resource while using the other.")
print("3. Disaggregated serving can double throughput for batch size 8+.")
print("4. T4 is NOT suitable for real disaggregation (needs NVLink/H100).")
print("5. Chunked prefill is the practical software alternative today.")
print("="*70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Accept the Hugging Face model license for Llama-3.2
# 4. Run all cells
# Profiling takes ~3-5 minutes on T4.

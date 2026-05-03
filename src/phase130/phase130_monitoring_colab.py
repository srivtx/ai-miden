"""
Phase 130: Production Monitoring and MLOps — Real Model Benchmark (Colab T4)
============================================================================
Run this on Google Colab with a T4 GPU for realistic LLM monitoring.

This script demonstrates the FULL pipeline for production monitoring:
  1. Load meta-llama/Llama-3.2-3B-Instruct
  2. Generate 200 synthetic requests (benign + complex)
  3. Run inference and log:
     - Input length
     - Output length
     - Latency (total)
     - Token count
     - Output perplexity
  4. Simulate drift: second half of requests are more complex
  5. Detect drift using:
     - Input length distribution change (KS test)
     - Output perplexity increase
     - Latency increase
  6. Build a simple dashboard:
     - Latency over time
     - Token usage over time
     - Drift score over time
     - Alert when drift exceeds threshold
  7. Simulate A/B test:
     - 50% traffic to base model
     - 50% traffic to fine-tuned model (simulated by LoRA-like temperature)
     - Compare latency, output length, user satisfaction (simulated)

WHY Llama-3.2-3B? Small enough for T4, real enough to show latency
variability and perplexity differences across prompt types.

WHY 200 requests? Enough to establish a baseline distribution and then
show a clear shift in the second half. Fewer requests make KS tests noisy.

WHY perplexity as a drift signal? If the model becomes "confused" by
longer or more technical inputs, its own perplexity on its outputs rises.
This is an unsupervised signal that requires no labels.
============================================================================
"""

# ==============================================================================
# FRONTIER TRACK — PHASE 130
# ==============================================================================
# Install dependencies (uncomment in Colab):
# !pip install transformers accelerate bitsandbytes scipy -q

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
import gc
import time
import os
from scipy import stats

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# WHY these settings? Llama-3.2-3B fits on T4 in FP16. 200 requests with
# max_new_tokens=48 keeps total runtime under ~30 minutes while producing
# enough data for meaningful distributions.

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_NAME = 'meta-llama/Llama-3.2-3B-Instruct'
MAX_NEW_TOKENS = 48
N_REQUESTS = 200
DRIFT_START = 100  # second half is complex

print(f"Using device: {DEVICE}")
print(f"Model: {MODEL_NAME}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ==============================================================================
# STEP 1: LOAD MODEL AND TOKENIZER
# ==============================================================================
# WHY AutoModelForCausalLM? Standard causal LM with logits output needed
# for perplexity computation.

from transformers import AutoModelForCausalLM, AutoTokenizer

print(f"\n--- Loading tokenizer ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

print(f"--- Loading model ---")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)

print(f"Model loaded. Parameters: {sum(p.numel() for p in model.parameters()):,}")
if torch.cuda.is_available():
    print(f"VRAM used after load: {torch.cuda.memory_allocated() / 1e9:.2f} GB")

# ==============================================================================
# STEP 2: GENERATE SYNTHETIC REQUESTS
# ==============================================================================
# We create two distributions:
#   Benign (0-99): short, general-knowledge questions
#   Complex (100-199): longer, technical prompts with multiple instructions
# WHY this split? It simulates a real drift event: a documentation update,
# a new API endpoint, or a viral technical post driving complex traffic.

BENIGN_PROMPTS = [
    "What is the capital of Italy?",
    "Explain photosynthesis in simple terms.",
    "Who wrote Hamlet?",
    "What is the speed of light?",
    "How many planets are in the solar system?",
    "What is the largest ocean?",
    "Who invented the telephone?",
    "What does 'serendipity' mean?",
    "How do you boil an egg?",
    "What are the primary colors?",
]

COMPLEX_PROMPTS = [
    "Explain the transformer architecture in detail, including multi-head attention, feed-forward layers, and layer normalization. Discuss how positional encoding works and why it is necessary.",
    "Write a comprehensive guide to backpropagation through time (BPTT) for recurrent neural networks. Include the mathematical derivation, vanishing gradient problem, and LSTM solutions.",
    "Describe the differences between strong AI and weak AI, providing historical context, current limitations, and ethical considerations for artificial general intelligence research.",
    "Analyze the trade-offs between consistency and availability in distributed systems. Use the CAP theorem, provide real-world examples, and discuss PACELC extensions.",
    "Explain how GPU memory hierarchy affects transformer training throughput. Discuss HBM bandwidth, shared memory, occupancy, and kernel fusion optimizations.",
    "Provide a detailed comparison of policy gradient methods versus Q-learning in reinforcement learning. Include mathematical foundations, sample efficiency, and stability issues.",
    "Describe the internal workings of a modern garbage collector in a managed runtime. Compare mark-and-sweep, generational, and concurrent collectors with performance trade-offs.",
    "Write an analysis of zero-knowledge proofs, their cryptographic assumptions, and applications in blockchain scaling. Include SNARKs vs. STARKs and trusted setup considerations.",
    "Explain how branch prediction and speculative execution work in modern CPUs. Discuss Spectre and Meltdown vulnerabilities and mitigation strategies.",
    "Analyze the design decisions behind the Raft consensus algorithm. Compare it to Paxos, discuss leader election, log replication, and safety guarantees.",
]

def generate_requests(n_benign=100, n_complex=100):
    """
    Generate synthetic requests.
    WHY repeat templates? To create enough samples for distribution tests
    without needing a massive prompt corpus.
    """
    rng = np.random.RandomState(130)
    benign = [rng.choice(BENIGN_PROMPTS) for _ in range(n_benign)]
    complex_reqs = [rng.choice(COMPLEX_PROMPTS) for _ in range(n_complex)]
    return benign + complex_reqs

requests = generate_requests()
print(f"\n--- Generated {len(requests)} requests ---")
print(f"Benign: {len(BENIGN_PROMPTS)} templates × repeated")
print(f"Complex: {len(COMPLEX_PROMPTS)} templates × repeated")

# ==============================================================================
# STEP 3: INFERENCE AND LOGGING
# ==============================================================================
# For each request, we generate output and log metrics.
# WHY compute perplexity? It measures how "confident" the model is in
# its own output. High perplexity on simple outputs suggests drift or degradation.

@torch.no_grad()
def generate_and_log(model, tokenizer, prompt, max_new_tokens=MAX_NEW_TOKENS):
    """
    Generate text and compute metrics.
    """
    inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    input_len = inputs['input_ids'].shape[1]

    # Generation with timing
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    t0 = time.time()
    output_ids = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        use_cache=True,
        do_sample=False,
        pad_token_id=tokenizer.pad_token_id,
    )
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    latency = time.time() - t0

    output_len = output_ids.shape[1] - input_len
    total_tokens = input_len + output_len

    # Compute perplexity of generated output
    # WHY only output tokens? We want to measure how surprised the model
    # is by its own generation, not by the prompt it was given.
    if output_len > 0:
        output_only = output_ids[:, input_len:]
        logits = model(output_only).logits
        # Shift for next-token prediction
        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = output_only[:, 1:].contiguous()
        loss_fct = torch.nn.CrossEntropyLoss(reduction='mean')
        perplexity = torch.exp(loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1)))
        perplexity = perplexity.item()
    else:
        perplexity = 1.0

    peak_mem = torch.cuda.max_memory_allocated() / 1e9 if torch.cuda.is_available() else 0.0

    return {
        'input_len': input_len,
        'output_len': output_len,
        'total_tokens': total_tokens,
        'latency': latency,
        'perplexity': perplexity,
        'peak_mem': peak_mem,
    }

print(f"\n--- Running inference on {len(requests)} requests ---")
logs = []
for i, prompt in enumerate(tqdm(requests, desc="Inferencing")):
    log = generate_and_log(model, tokenizer, prompt)
    logs.append(log)
    if (i + 1) % 50 == 0:
        gc.collect()
        torch.cuda.empty_cache()

input_lens = np.array([l['input_len'] for l in logs])
output_lens = np.array([l['output_len'] for l in logs])
total_tokens = np.array([l['total_tokens'] for l in logs])
latencies = np.array([l['latency'] for l in logs])
perplexities = np.array([l['perplexity'] for l in logs])

print(f"\n--- Inference Complete ---")
print(f"Mean latency:     {latencies.mean():.3f} s")
print(f"p50 latency:      {np.percentile(latencies, 50):.3f} s")
print(f"p95 latency:      {np.percentile(latencies, 95):.3f} s")
print(f"Mean perplexity:  {perplexities.mean():.2f}")
print(f"Mean input len:   {input_lens.mean():.0f}")
print(f"Mean output len:  {output_lens.mean():.0f}")

# ==============================================================================
# STEP 4: DRIFT DETECTION
# ==============================================================================
# We compare the first half (benign) against the second half (complex)
# using the Kolmogorov-Smirnov test on input lengths.
# We also compute z-scores for perplexity and latency.

benign_input = input_lens[:DRIFT_START]
complex_input = input_lens[DRIFT_START:]

ks_stat, ks_pvalue = stats.ks_2samp(benign_input, complex_input)

benign_perp = perplexities[:DRIFT_START]
complex_perp = perplexities[DRIFT_START:]
perp_z = (complex_perp.mean() - benign_perp.mean()) / (benign_perp.std() + 1e-6)

benign_lat = latencies[:DRIFT_START]
complex_lat = latencies[DRIFT_START:]
lat_z = (complex_lat.mean() - benign_lat.mean()) / (benign_lat.std() + 1e-6)

print(f"\n--- Drift Detection ---")
print(f"KS test on input length: stat={ks_stat:.3f}, p-value={ks_pvalue:.2e}")
print(f"Perplexity z-score:      {perp_z:.2f}")
print(f"Latency z-score:         {lat_z:.2f}")

# Sliding window drift score
window_size = 20
baseline_size = 30
drift_scores = []
for t in range(baseline_size, len(input_lens)):
    baseline = input_lens[:baseline_size]
    current = input_lens[max(0, t - window_size):t]
    ks, _ = stats.ks_2samp(baseline, current)
    drift_scores.append(ks)
drift_scores = np.array(drift_scores)
drift_threshold = 0.3
alerts = drift_scores > drift_threshold
alert_indices = np.where(alerts)[0] + baseline_size

print(f"Sliding KS drift alerts: {alerts.sum()} (threshold={drift_threshold})")
if len(alert_indices) > 0:
    print(f"First alert at request: {alert_indices[0]}")

# ==============================================================================
# STEP 5: A/B TEST SIMULATION
# ==============================================================================
# We simulate an A/B test by splitting the benign requests into two groups.
# Group A: base model (already generated)
# Group B: simulated "fine-tuned" by adding slight temperature variation
# We compare latency, output length, and simulated satisfaction.

rng = np.random.RandomState(130)
ab_indices = rng.permutation(DRIFT_START)
half = DRIFT_START // 2
a_indices = ab_indices[:half]
b_indices = ab_indices[half:]

# Group A metrics
a_lat = latencies[a_indices]
a_out = output_lens[a_indices]
a_sat = rng.beta(7, 3, len(a_indices)) * 5  # simulated satisfaction

# Group B: simulate fine-tuned model (slightly slower, slightly better quality)
# WHY multiply latency? Fine-tuned models often have different KV cache patterns.
b_lat = latencies[b_indices] * rng.uniform(0.9, 1.15, len(b_indices))
b_out = output_lens[b_indices] * rng.uniform(0.95, 1.1, len(b_indices))
b_sat = rng.beta(8, 2, len(b_indices)) * 5  # better satisfaction

print(f"\n--- A/B Test Simulation ---")
print(f"Group A (base):      latency={a_lat.mean():.3f}s, output={a_out.mean():.0f}, satisfaction={a_sat.mean():.2f}")
print(f"Group B (tuned):     latency={b_lat.mean():.3f}s, output={b_out.mean():.0f}, satisfaction={b_sat.mean():.2f}")

# ==============================================================================
# STEP 6: DASHBOARD VISUALIZATION
# ==============================================================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: Latency over time
ax = axes[0, 0]
ax.plot(latencies, '-', color='#3498db', alpha=0.6, linewidth=1, label='Per request')
rolling_lat = np.convolve(latencies, np.ones(20)/20, mode='valid')
ax.plot(range(19, len(latencies)), rolling_lat, '-', color='#145a32', linewidth=2, label='20-req avg')
ax.axvline(DRIFT_START, color='#e74c3c', linestyle='--', linewidth=2, label='Drift injection')
ax.set_xlabel('Request Index')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Latency Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Token usage over time
ax = axes[0, 1]
ax.plot(total_tokens, '-', color='#27ae60', alpha=0.6, linewidth=1)
rolling_tok = np.convolve(total_tokens, np.ones(20)/20, mode='valid')
ax.plot(range(19, len(total_tokens)), rolling_tok, '-', color='#145a32', linewidth=2)
ax.axvline(DRIFT_START, color='#e74c3c', linestyle='--', linewidth=2)
ax.set_xlabel('Request Index')
ax.set_ylabel('Total Tokens')
ax.set_title('Token Usage Over Time')
ax.grid(True, alpha=0.3)

# Plot 3: Drift score over time
ax = axes[0, 2]
ax.plot(range(baseline_size, baseline_size+len(drift_scores)), drift_scores, '-', color='#9b59b6', linewidth=2)
ax.axhline(drift_threshold, color='#e74c3c', linestyle='--', linewidth=2, label=f'Threshold={drift_threshold}')
ax.axvline(DRIFT_START, color='gray', linestyle=':', linewidth=1.5, label='Drift injection')
ax.fill_between(range(baseline_size, baseline_size+len(drift_scores)), drift_scores, drift_threshold,
                where=(drift_scores > drift_threshold), color='#e74c3c', alpha=0.3)
ax.set_xlabel('Request Index')
ax.set_ylabel('KS Drift Score')
ax.set_title('Drift Score Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Perplexity distribution (benign vs complex)
ax = axes[1, 0]
ax.hist(benign_perp, bins=20, alpha=0.6, color='#3498db', label='Benign', edgecolor='black')
ax.hist(complex_perp, bins=20, alpha=0.6, color='#e74c3c', label='Complex', edgecolor='black')
ax.set_xlabel('Perplexity')
ax.set_ylabel('Count')
ax.set_title('Output Perplexity Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 5: Input length distribution (benign vs complex)
ax = axes[1, 1]
ax.hist(benign_input, bins=20, alpha=0.6, color='#3498db', label='Benign', edgecolor='black')
ax.hist(complex_input, bins=20, alpha=0.6, color='#e74c3c', label='Complex', edgecolor='black')
ax.set_xlabel('Input Length (tokens)')
ax.set_ylabel('Count')
ax.set_title('Input Length Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 6: A/B test results
ax = axes[1, 2]
x = np.arange(3)
width = 0.35
metrics_a = [a_lat.mean(), a_out.mean(), a_sat.mean()]
metrics_b = [b_lat.mean(), b_out.mean(), b_sat.mean()]
# Normalize for display
norm_a = [metrics_a[0], metrics_a[1]/10, metrics_a[2]]
norm_b = [metrics_b[0], metrics_b[1]/10, metrics_b[2]]
ax.bar(x - width/2, norm_a, width, label='Base Model (A)', color='#3498db', edgecolor='black')
ax.bar(x + width/2, norm_b, width, label='Tuned Model (B)', color='#27ae60', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels(['Latency (s)', 'Output (/10)', 'Satisfaction'])
ax.set_ylabel('Normalized Score')
ax.set_title('A/B Test Results')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('phase130_monitoring_dashboard.png', dpi=150, bbox_inches='tight')
print("\nSaved plot: phase130_monitoring_dashboard.png")
plt.close()

# ==============================================================================
# STEP 7: ALERT LOG
# ==============================================================================

print("\n" + "="*70)
print("ALERT LOG")
print("="*70)
if len(alert_indices) > 0:
    print(f"ALERT: Drift detected at request {alert_indices[0]} (KS={drift_scores[alert_indices[0]-baseline_size]:.3f})")
    print(f"  Input length KS test p-value: {ks_pvalue:.2e}")
    print(f"  Perplexity z-score: {perp_z:.2f}")
    print(f"  Latency z-score: {lat_z:.2f}")
    print(f"  Recommended action: Check traffic source; validate prompt template")
    for idx in alert_indices[1:5]:
        print(f"ALERT: Drift continues at request {idx} (KS={drift_scores[idx-baseline_size]:.3f})")
    if len(alert_indices) > 5:
        print(f"... and {len(alert_indices)-5} additional alerts")
else:
    print("No alerts fired.")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)
print(f"Model: {MODEL_NAME}")
print(f"Requests: {N_REQUESTS} (benign={DRIFT_START}, complex={N_REQUESTS-DRIFT_START})")
print(f"Latency: mean={latencies.mean():.3f}s, p50={np.percentile(latencies,50):.3f}s, p95={np.percentile(latencies,95):.3f}s")
print(f"Perplexity: benign={benign_perp.mean():.2f}, complex={complex_perp.mean():.2f}")
print(f"Drift detection: KS stat={ks_stat:.3f}, p={ks_pvalue:.2e}, alerts={alerts.sum()}")
print(f"A/B test: Base satisfaction={a_sat.mean():.2f}, Tuned satisfaction={b_sat.mean():.2f}")
print(f"\nKey lessons:")
print("1. Real inference logs reveal patterns invisible in benchmarks.")
print("2. KS tests on input length catch distribution shifts without labels.")
print("3. Perplexity rises when inputs push the model out of distribution.")
print("4. Sliding window alerts fire faster than global comparisons.")
print("5. A/B tests on real traffic validate model changes before full rollout.")
print("6. Token usage tracking predicts cost before the bill arrives.")
print("7. Dashboards turn raw logs into actionable signals.")
print("="*70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Uncomment pip install at the top
# 4. Run all cells
# Full run takes ~25-40 minutes on T4 depending on generation speed.

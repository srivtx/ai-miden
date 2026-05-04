# FRONTIER TRACK: Phase 136 — Neural Scaling Laws Beyond Chinchilla (Colab)
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script benchmarks REAL pretrained models across scales.
# !pip install -q transformers torch accelerate matplotlib tqdm

import torch
import numpy as np
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# WHY: We use models that fit on a T4 and represent distinct scale points.
# -----------------------------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

# Model configurations: name, approximate params, model ID
MODELS = [
    {
        "name": "Small (125M)",
        "params": 125e6,
        "id": "gpt2",  # ~124M
    },
    {
        "name": "Medium (355M)",
        "params": 355e6,
        "id": "gpt2-medium",  # ~355M
    },
    {
        "name": "Large (1.5B)",
        "params": 1.5e9,
        "id": "Qwen/Qwen2.5-1.5B-Instruct",  # ~1.5B
    },
]

N_WARMUP = 5
N_TIMING_RUNS = 20
MAX_NEW_TOKENS = 32
BATCH_SIZE = 1

# Expected queries over model lifetime for cost modeling
QUERY_SCENARIOS = [1e6, 1e8, 1e10, 1e12]

# Synthetic cost factors (relative units)
COST_PER_TRAIN_FLOP = 1e-18  # arbitrary small unit
COST_PER_INFER_FLOP = 1e-17  # inference often 10x more expensive per FLOP due to latency premium

# -----------------------------------------------------------------------------
# 2. BENCHMARK EACH MODEL
# WHY: We measure perplexity (quality proxy) and throughput (cost proxy).
# -----------------------------------------------------------------------------

results = []

for model_cfg in MODELS:
    model_name = model_cfg["name"]
    model_id = model_cfg["id"]
    N = model_cfg["params"]

    print(f"\n{'='*60}")
    print(f"Benchmarking {model_name} ({model_id})")
    print(f"{'='*60}")

    # Load model
    print("Loading...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto" if DEVICE == "cuda" else None,
            trust_remote_code=True,
        )
    except Exception as e:
        print(f"Failed to load {model_id}: {e}")
        continue

    model.eval()

    # -------------------------------------------------------------------------
    # 2a. PERPLEXITY ON A SHORT TEXT
    # WHY: Perplexity is the standard quality metric for language models.
    # We use a synthetic paragraph to avoid downloading a full dataset.
    # -------------------------------------------------------------------------
    eval_text = (
        "Artificial intelligence has transformed the way we process information. "
        "Modern neural networks can learn complex patterns from vast amounts of data. "
        "Scaling laws describe how model performance improves with increased compute, "
        "parameters, and training tokens. Researchers continue to explore the frontier "
        "of what is possible with larger and more efficient architectures."
    )

    inputs = tokenizer(eval_text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs.input_ids)
        loss = outputs.loss.item()
        perplexity = np.exp(loss)

    n_tokens = inputs.input_ids.shape[1]
    del inputs, outputs
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    print(f"Perplexity: {perplexity:.2f} (loss: {loss:.3f})")

    # -------------------------------------------------------------------------
    # 2b. INFERENCE SPEED
    # WHY: Tokens per second determines serving cost and user experience.
    # -------------------------------------------------------------------------
    prompt = "Explain the concept of scaling laws in machine learning:"
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

    # Warmup
    for _ in range(N_WARMUP):
        with torch.no_grad():
            _ = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        if DEVICE == "cuda":
            torch.cuda.synchronize()

    # Timed runs
    times = []
    for _ in range(N_TIMING_RUNS):
        if DEVICE == "cuda":
            torch.cuda.synchronize()
        t0 = time.time()
        with torch.no_grad():
            _ = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        if DEVICE == "cuda":
            torch.cuda.synchronize()
        t1 = time.time()
        times.append(t1 - t0)

    avg_time = np.mean(times)
    tokens_per_sec = MAX_NEW_TOKENS / avg_time
    print(f"Inference speed: {tokens_per_sec:.1f} tokens/sec")

    del inputs
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

    # -------------------------------------------------------------------------
    # 2c. COMPUTE BUDGET ESTIMATES
    # WHY: We need rough training and inference cost to find the sweet spot.
    # We assume Chinchilla-optimal training tokens: D = 20 * N.
    # -------------------------------------------------------------------------
    D_chinchilla = 20.0 * N
    train_flops = 6.0 * N * D_chinchilla
    infer_flops_per_query = 2.0 * N * MAX_NEW_TOKENS

    train_cost = train_flops * COST_PER_TRAIN_FLOP

    result = {
        "name": model_name,
        "params": N,
        "perplexity": perplexity,
        "loss": loss,
        "tokens_per_sec": tokens_per_sec,
        "train_cost": train_cost,
        "infer_flops_per_query": infer_flops_per_query,
    }
    results.append(result)

    # Cleanup model from GPU before loading next
    del model, tokenizer
    gc.collect()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

# -----------------------------------------------------------------------------
# 3. COST ANALYSIS FOR DIFFERENT USAGE PATTERNS
# WHY: Total cost = training + inference * queries. The dominant term depends on usage.
# -----------------------------------------------------------------------------

print("\n" + "=" * 60)
print("COST ANALYSIS")
print("=" * 60)

# Build cost table
rows = []
for scenario in QUERY_SCENARIOS:
    row = {"queries": scenario}
    for r in results:
        total = r["train_cost"] + r["infer_flops_per_query"] * scenario * COST_PER_INFER_FLOP
        row[r["name"]] = total
    rows.append(row)

# Print table
print(f"{'Queries':>12}", end="")
for r in results:
    print(f"{r['name']:>18}", end="")
print()
print("-" * (12 + 18 * len(results)))
for row in rows:
    print(f"{row['queries']:>12.0e}", end="")
    for r in results:
        print(f"{row[r['name']]:>18.2e}", end="")
    print()

# Find optimal model per scenario
print("\nOptimal model per scenario:")
for row in rows:
    costs = {r["name"]: row[r["name"]] for r in results}
    best = min(costs, key=costs.get)
    print(f"  {row['queries']:>12.0e} queries → {best} (lowest total cost)")

# -----------------------------------------------------------------------------
# 4. VISUALIZATION
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

names = [r["name"] for r in results]
perplexities = [r["perplexity"] for r in results]
tokens_per_sec = [r["tokens_per_sec"] for r in results]
params = [r["params"] / 1e9 for r in results]

# Plot 1: Perplexity (quality)
ax = axes[0, 0]
bars = ax.bar(names, perplexities, color=['steelblue', 'darkorange', 'forestgreen'])
ax.set_title('Quality: Perplexity (Lower is Better)')
ax.set_ylabel('Perplexity')
for bar, val in zip(bars, perplexities):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val:.1f}", ha='center', va='bottom')

# Plot 2: Inference speed
ax = axes[0, 1]
bars = ax.bar(names, tokens_per_sec, color=['steelblue', 'darkorange', 'forestgreen'])
ax.set_title('Speed: Tokens per Second (Higher is Better)')
ax.set_ylabel('Tokens / sec')
for bar, val in zip(bars, tokens_per_sec):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{val:.0f}", ha='center', va='bottom')

# Plot 3: Total cost vs queries for each model
ax = axes[1, 0]
for r in results:
    costs = []
    for scenario in QUERY_SCENARIOS:
        total = r["train_cost"] + r["infer_flops_per_query"] * scenario * COST_PER_INFER_FLOP
        costs.append(total)
    ax.plot(QUERY_SCENARIOS, costs, marker='o', linewidth=2, label=r["name"])
ax.set_xlabel('Expected Queries Over Lifetime')
ax.set_ylabel('Total Cost (arbitrary units)')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title('Total Lifetime Cost vs Usage')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Optimal model size vs usage
ax = axes[1, 1]
optimal_sizes = []
for scenario in QUERY_SCENARIOS:
    best_cost = float('inf')
    best_size = None
    for r in results:
        total = r["train_cost"] + r["infer_flops_per_query"] * scenario * COST_PER_INFER_FLOP
        if total < best_cost:
            best_cost = total
            best_size = r["params"]
    optimal_sizes.append(best_size / 1e9)

ax.plot(QUERY_SCENARIOS, optimal_sizes, marker='o', color='crimson', linewidth=2, markersize=8)
ax.set_xlabel('Expected Queries Over Lifetime')
ax.set_ylabel('Cost-Optimal Model Size (B params)')
ax.set_xscale('log')
ax.set_title('Optimal Model Size vs Usage Pattern')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase136/scaling_results.png', dpi=150)
plt.close()

print("\nPlot saved to src/phase136/scaling_results.png")

# -----------------------------------------------------------------------------
# 5. CLEANUP
# -----------------------------------------------------------------------------
gc.collect()
if DEVICE == "cuda":
    torch.cuda.empty_cache()
print("Done.")

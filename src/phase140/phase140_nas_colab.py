"""
Phase 140: Neural Architecture Search for LLMs — Real Model Search (Colab T4)
==============================================================================
Run this on Google Colab with a T4 GPU.

This script performs a real Neural Architecture Search over small GPT-2
variants trained on wikitext-2. We exhaustively evaluate a 3x3 grid of
configurations, then compare three search strategies:

  1. Grid search (train all 9 configs).
  2. Random search (sample 5 configs).
  3. Evolutionary search (mutate best configs for 3 generations).

Each model trains for only 100 steps. This is a "proxy task": the ranking
of architectures after 100 steps correlates strongly with their ranking
after full training, but costs 100x less. NAS pipelines rely on this
property to make search affordable.

Key insight: Naively scaling depth and width is often suboptimal. A
medium-width, medium-depth model can sit on the Pareto frontier, beating
both smaller and larger alternatives on the accuracy-vs-params trade-off.
"""

import gc
import copy
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
from datasets import load_dataset
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm

# =============================================================================
# CONFIGURATION
# =============================================================================
# WHY GPT-2 family? The architecture is well-understood, the tokenizer is
# standard, and configs can be varied smoothly via GPT2Config. This lets us
# focus on the NAS mechanics rather than model-specific quirks.

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
BLOCK_SIZE = 128
BATCH_SIZE = 4
TRAIN_STEPS = 100
LR = 5e-4

print(f"Device: {DEVICE}")

# =============================================================================
# DATA: WIKITEXT-2
# =============================================================================
# WHY wikitext-2? It is the standard small-scale language modeling benchmark.
# It is large enough to expose architectural differences but small enough
# to train toy models in seconds.

print("\nLoading wikitext-2...")
dataset = load_dataset("wikitext", "wikitext-2-raw-v1")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# WHY set pad_token to eos? GPT-2 has no explicit pad token, but the EOS
# token can serve as a padding ID for batching.
tokenizer.pad_token = tokenizer.eos_token

def build_dataloader(split, batch_size=BATCH_SIZE):
    """
    Tokenize raw text, concatenate, and chunk into fixed-length blocks.
    WHY chunking? Language models need fixed-size input tensors.
    WHY concatenate first? It preserves context across sentence boundaries
    and avoids wasting tokens on short sentences.
    """
    texts = [t for t in dataset[split]["text"] if len(t.strip()) > 0]
    all_ids = []
    for text in texts:
        # encode without adding special tokens every sentence
        ids = tokenizer.encode(text, add_special_tokens=False)
        all_ids.extend(ids)
    # chunk into BLOCK_SIZE pieces
    chunks = []
    for i in range(0, len(all_ids) - BLOCK_SIZE + 1, BLOCK_SIZE):
        chunks.append(all_ids[i:i+BLOCK_SIZE])
    if len(chunks) == 0:
        return None
    input_ids = torch.tensor(chunks, dtype=torch.long)
    ds = TensorDataset(input_ids)
    shuffle = (split == "train")
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)

train_loader = build_dataloader("train")
val_loader = build_dataloader("validation")
print(f"Train batches: {len(train_loader)}")
print(f"Val batches:   {len(val_loader)}")

# =============================================================================
# SEARCH SPACE
# =============================================================================
# WHY these values? They span a 10x parameter range (4M to ~50M) while
# staying small enough to train in seconds on a T4. Heads = hidden//64
# ensures head dimension is constant (64), which simplifies comparison.

LAYERS = [4, 6, 8]
HIDDEN_DIMS = [256, 384, 512]

CONFIGS = []
for l in LAYERS:
    for h in HIDDEN_DIMS:
        CONFIGS.append({"layers": l, "hidden": h, "heads": h // 64})

print(f"\nSearch space size: {len(CONFIGS)} configs")
for c in CONFIGS:
    print(f"  {c}")

# =============================================================================
# TRAIN AND EVALUATE ONE CONFIG
# =============================================================================
# WHY separate function? It isolates memory for each model. We delete the
# model and clear CUDA cache before returning, preventing OOM when training
# 9 models sequentially on a 16 GB T4.

def train_and_eval(config, train_loader, val_loader, steps=TRAIN_STEPS):
    """
    Build a GPT-2 variant, train for `steps`, evaluate perplexity.
    Returns (perplexity, param_count).
    """
    cfg = GPT2Config(
        n_layer=config["layers"],
        n_embd=config["hidden"],
        n_head=config["heads"],
        n_positions=512,
        vocab_size=tokenizer.vocab_size,
    )
    model = GPT2LMHeadModel(cfg).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)

    model.train()
    step = 0
    pbar = tqdm(total=steps, desc=f"L{config['layers']}_H{config['hidden']}", leave=False)
    for epoch in range(1000):  # arbitrarily large; we break by step count
        for batch in train_loader:
            if step >= steps:
                break
            batch = batch[0].to(DEVICE)
            optimizer.zero_grad()
            # WHY labels=batch? GPT2LMHeadModel shifts labels internally
            # to compute next-token prediction loss.
            outputs = model(batch, labels=batch)
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            step += 1
            pbar.update(1)
            if step >= steps:
                break
    pbar.close()

    # Evaluation
    model.eval()
    total_loss = 0.0
    n_samples = 0
    with torch.no_grad():
        for batch in val_loader:
            batch = batch[0].to(DEVICE)
            outputs = model(batch, labels=batch)
            # WHY multiply by batch size? We need the weighted average.
            total_loss += outputs.loss.item() * batch.size(0)
            n_samples += batch.size(0)
    avg_loss = total_loss / n_samples
    perplexity = np.exp(avg_loss)
    param_count = sum(p.numel() for p in model.parameters())

    # Memory cleanup before returning
    del model, optimizer
    torch.cuda.empty_cache()
    gc.collect()

    return perplexity, param_count

# =============================================================================
# EXHAUSTIVE GRID SEARCH
# =============================================================================
# WHY train all 9? It gives us a complete ground-truth Pareto frontier.
# Random and evolutionary search will be compared against this oracle.

print("\n" + "="*70)
print("GRID SEARCH: Training all configurations")
print("="*70)

grid_results = []  # list of (config, perplexity, params)
for config in CONFIGS:
    ppl, params = train_and_eval(config, train_loader, val_loader)
    grid_results.append((config, ppl, params))
    print(f"Config {config} -> PPL={ppl:.2f}, Params={params:,}")

# =============================================================================
# PARETO FRONTIER (GROUND TRUTH)
# =============================================================================
# A config dominates another if it has both lower perplexity and fewer params.
# WHY params instead of FLOPs? Params are hardware-agnostic and easy to
# measure. For Transformers, params and FLOPs are strongly correlated.

def pareto_mask(results):
    """
    results: list of (config, ppl, params)
    Returns list of booleans indicating Pareto optimality.
    """
    masks = []
    for i, (_, ppl_i, params_i) in enumerate(results):
        dominated = False
        for j, (_, ppl_j, params_j) in enumerate(results):
            if i == j:
                continue
            if ppl_j <= ppl_i and params_j <= params_i and (ppl_j < ppl_i or params_j < params_i):
                dominated = True
                break
        masks.append(not dominated)
    return masks

pareto_grid = pareto_mask(grid_results)

# =============================================================================
# RANDOM SEARCH SIMULATION
# =============================================================================
# WHY sample 5? It is slightly more than half the space, giving random search
# a realistic chance to find good configs while still being cheaper than grid.

random_budget = 5
random_indices = np.random.choice(len(CONFIGS), size=random_budget, replace=False)
random_results = [grid_results[i] for i in random_indices]
pareto_random = pareto_mask(random_results)

# =============================================================================
# EVOLUTIONARY SEARCH SIMULATION
# =============================================================================
# WHY simulate instead of train live? We already have ground-truth numbers.
# Running evolution in simulation lets us compare the *search algorithm*
# independent of training noise. This is standard in NAS research.

pop_size = 3
generations = 3
mutation_prob = 0.7

# Initialize population with random configs from the grid
def random_config():
    return copy.deepcopy(CONFIGS[np.random.randint(len(CONFIGS))])

pop = [random_config() for _ in range(pop_size)]
evaluated = {}  # cache lookups

def lookup(config):
    key = (config["layers"], config["hidden"])
    if key not in evaluated:
        # find in grid_results
        for c, ppl, params in grid_results:
            if c["layers"] == config["layers"] and c["hidden"] == config["hidden"]:
                evaluated[key] = (ppl, params)
                break
    return evaluated[key]

evo_best_history = []

for gen in range(generations):
    # Evaluate population
    fitness = []
    for p in pop:
        ppl, params = lookup(p)
        fitness.append((ppl, params))
    # Sort by perplexity (lower is better)
    sorted_idx = np.argsort([f[0] for f in fitness])
    pop = [pop[i] for i in sorted_idx]
    fitness = [fitness[i] for i in sorted_idx]
    evo_best_history.append(fitness[0][0])

    # Elitism: keep top 2
    survivors = pop[:2]
    offspring = []
    while len(offspring) < pop_size - len(survivors):
        parent = copy.deepcopy(survivors[np.random.randint(len(survivors))])
        # Mutate layers or hidden dim by one step in the grid
        if np.random.rand() < mutation_prob:
            if np.random.rand() < 0.5:
                idx = LAYERS.index(parent["layers"])
                delta = np.random.choice([-1, 1])
                parent["layers"] = int(LAYERS[np.clip(idx + delta, 0, len(LAYERS)-1)])
            else:
                idx = HIDDEN_DIMS.index(parent["hidden"])
                delta = np.random.choice([-1, 1])
                parent["hidden"] = int(HIDDEN_DIMS[np.clip(idx + delta, 0, len(HIDDEN_DIMS)-1)])
                parent["heads"] = parent["hidden"] // 64
        offspring.append(parent)
    pop = survivors + offspring

# Final evaluation
fitness = []
for p in pop:
    ppl, params = lookup(p)
    fitness.append((ppl, params))
sorted_idx = np.argsort([f[0] for f in fitness])
final_pop = [pop[i] for i in sorted_idx]
final_fit = [fitness[i] for i in sorted_idx]
evo_best_history.append(final_fit[0][0])

evo_results = [(c, p, pr) for c, (p, pr) in zip(final_pop, final_fit)]
pareto_evo = pareto_mask(evo_results)

# =============================================================================
# PRINT COMPARISON TABLE
# =============================================================================
print("\n" + "="*70)
print("SEARCH COMPARISON")
print("="*70)

best_grid = min(grid_results, key=lambda x: x[1])
print(f"Grid search best:     PPL={best_grid[1]:.2f}, Params={best_grid[2]:,}, Config={best_grid[0]}")

best_random = min(random_results, key=lambda x: x[1])
print(f"Random search best:   PPL={best_random[1]:.2f}, Params={best_random[2]:,}, Config={best_random[0]}")

best_evo = min(evo_results, key=lambda x: x[1])
print(f"Evolutionary best:    PPL={best_evo[1]:.2f}, Params={best_evo[2]:,}, Config={best_evo[0]}")

print(f"\nGrid Pareto size: {sum(pareto_grid)} / {len(grid_results)}")
print(f"Random Pareto size: {sum(pareto_random)} / {len(random_results)}")
print(f"Evo Pareto size:    {sum(pareto_evo)} / {len(evo_results)}")

# =============================================================================
# VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: All configs scatter (params vs perplexity) with Pareto frontier.
ax = axes[0, 0]
all_params = [r[2] for r in grid_results]
all_ppls = [r[1] for r in grid_results]
ax.scatter(all_params, all_ppls, c='lightgray', s=100, label='All configs', edgecolors='black')
# Pareto points
pareto_params = [r[2] for r, m in zip(grid_results, pareto_grid) if m]
pareto_ppls = [r[1] for r, m in zip(grid_results, pareto_grid) if m]
# Sort by params for line plot
pp = sorted(zip(pareto_params, pareto_ppls))
if pp:
    ax.plot([p for p, _ in pp], [ppl for _, ppl in pp], 'o-', color='red', linewidth=2, label='Pareto frontier')
ax.set_xlabel('Parameters')
ax.set_ylabel('Validation Perplexity')
ax.set_title('Ground Truth: Accuracy vs. Size')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Search strategy comparison (best perplexity found).
ax = axes[0, 1]
labels = ['Grid\n(exhaustive)', 'Random\n(5 samples)', 'Evolutionary\n(3 gen)']
best_ppls = [best_grid[1], best_random[1], best_evo[1]]
colors = ['#3498db', '#f39c12', '#27ae60']
bars = ax.bar(labels, best_ppls, color=colors, edgecolor='black')
ax.set_ylabel('Best Perplexity Found')
ax.set_title('Search Quality Comparison')
for bar, val in zip(bars, best_ppls):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Pareto frontier overlay for all three methods.
ax = axes[1, 0]
# Grid
pp = sorted([(r[2], r[1]) for r, m in zip(grid_results, pareto_grid) if m])
if pp:
    ax.plot([p for p, _ in pp], [ppl for _, ppl in pp], 'o-', color='#3498db', linewidth=2, label='Grid')
# Random
pp = sorted([(r[2], r[1]) for r, m in zip(random_results, pareto_random) if m])
if pp:
    ax.plot([p for p, _ in pp], [ppl for _, ppl in pp], 's--', color='#f39c12', linewidth=2, label='Random')
# Evo
pp = sorted([(r[2], r[1]) for r, m in zip(evo_results, pareto_evo) if m])
if pp:
    ax.plot([p for p, _ in pp], [ppl for _, ppl in pp], '^--', color='#27ae60', linewidth=2, label='Evo')
ax.set_xlabel('Parameters')
ax.set_ylabel('Validation Perplexity')
ax.set_title('Pareto Frontiers by Search Method')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Evolutionary convergence.
ax = axes[1, 1]
ax.plot(range(len(evo_best_history)), evo_best_history, 'o-', color='#27ae60', linewidth=2)
ax.axhline(y=best_grid[1], color='red', linestyle='--', label='Grid best')
ax.set_xlabel('Generation')
ax.set_ylabel('Best Perplexity in Population')
ax.set_title('Evolutionary Search Convergence')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase140_nas_results.png', dpi=150, bbox_inches='tight')
print("\nSaved plot: phase140_nas_results.png")
plt.close()

# =============================================================================
# BEST CONFIG RECOMMENDATION
# =============================================================================
print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)
# Recommend the config with lowest perplexity on the Pareto frontier
# that also has fewer than 30M params (a realistic edge budget).
budget = 30_000_000
candidates = [r for r, m in zip(grid_results, pareto_grid) if m and r[2] <= budget]
if candidates:
    rec = min(candidates, key=lambda x: x[1])
    print(f"Recommended config (<= {budget:,} params, Pareto-optimal):")
    print(f"  Layers: {rec[0]['layers']}")
    print(f"  Hidden: {rec[0]['hidden']}")
    print(f"  Heads:  {rec[0]['heads']}")
    print(f"  Params: {rec[2]:,}")
    print(f"  PPL:    {rec[1]:.2f}")
else:
    rec = best_grid
    print("No config under budget; recommending absolute best:")
    print(f"  {rec[0]} -> PPL={rec[1]:.2f}, Params={rec[2]:,}")

print("\nKey lessons:")
print("1. Proxy tasks (100 steps) reveal architectural rankings cheaply.")
print("2. Grid search is optimal but expensive; evolutionary search finds")
print("   near-optimal configs with far fewer evaluations.")
print("3. Naive scaling (deeper + wider) is often dominated by smarter")
print("   trade-offs discovered on the Pareto frontier.")
print("="*70)

# Colab instructions:
# 1. Upload or paste into a Colab cell.
# 2. Runtime -> Change runtime type -> GPU.
# 3. Run all cells.
# Estimated time: ~3-5 minutes on T4.

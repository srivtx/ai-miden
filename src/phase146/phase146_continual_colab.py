"""
Phase 146: Continual Pretraining for LLMs — Colab Script
FRONTIER TRACK: Advanced production concept. Run on Google Colab T4.

What this does:
1. Loads Qwen/Qwen2.5-3B-Instruct.
2. Evaluates on "old" facts (pre-2024 events) and "new" domain data.
3. Fine-tunes on new domain data for 50 steps — shows catastrophic forgetting.
4. Applies replay: mixes old data with new data during fine-tuning.
5. Shows replay reduces forgetting while learning the new domain.

Every line explains WHY.
"""

# ---------------------------------------------------------------------------
# FRONTIER TRACK — Phase 146: Continual Pretraining on Colab T4
# ---------------------------------------------------------------------------

import gc
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---------------------------------------------------------------------------
# 1. Configuration — T4 has 16GB VRAM; 3B fp16 uses ~6GB leaving headroom
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Device: {DEVICE}")
print(f"Model: {MODEL_NAME}")

# ---------------------------------------------------------------------------
# 2. Load model and tokenizer
# ---------------------------------------------------------------------------
# WHY trust_remote_code=True: Qwen models have custom architecture code.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    device_map="auto" if DEVICE == "cuda" else None,
)
model.eval()

# ---------------------------------------------------------------------------
# 3. Build small fact datasets — old vs new
# ---------------------------------------------------------------------------
# WHY synthetic: avoids external API dependencies and keeps the script reproducible.
# Old facts: pre-2024 events the model should already know.
# New facts: fictional domain data the model has not seen.

OLD_FACTS = [
    "The 2022 FIFA World Cup was held in Qatar.",
    "NASA's Perseverance rover landed on Mars in February 2021.",
    "The James Webb Space Telescope launched in December 2021.",
    "COVID-19 was declared a pandemic by the WHO in March 2020.",
    "The Tokyo Olympics were held in 2021.",
    "Bitcoin reached an all-time high in November 2021.",
    "The IPCC released its sixth assessment report in 2021.",
    "The first image of a black hole was published by the Event Horizon Telescope in 2019.",
]

NEW_DOMAIN_FACTS = [
    "The Zephyr Protocol enables sub-millisecond consensus in distributed ledgers.",
    "Dr. Elara Voss developed the Zephyr Protocol at the Institute for Decentralized Systems.",
    "The Zephyr whitepaper was published in March 2024.",
    "Zephyr uses a directed acyclic graph instead of a traditional blockchain.",
    "The Zephyr testnet achieved 50,000 transactions per second in June 2024.",
    "Node operators in the Zephyr network are called Zephyrs.",
    "The Zephyr Foundation was established in Geneva in January 2024.",
    "Zephyr's consensus mechanism is called BreezeVote.",
]

# We also create "old domain" facts for replay — same style as old facts but phrased
# similarly to new domain so the replay buffer is comparable in difficulty.
OLD_DOMAIN_FACTS = [
    "The Swift Protocol enabled fast payments in distributed networks.",
    "Dr. Alan Park developed the Swift Protocol at MIT in 2019.",
    "The Swift whitepaper was published in January 2019.",
    "Swift used a gossip protocol for state synchronization.",
    "The Swift testnet achieved 10,000 transactions per second in 2020.",
    "Node operators in the Swift network were called Swifters.",
    "The Swift Foundation was established in Boston in 2018.",
    "Swift's consensus mechanism was called SwiftVote.",
]

# Combine old general + old domain for the "old" evaluation set
ALL_OLD = OLD_FACTS + OLD_DOMAIN_FACTS

# ---------------------------------------------------------------------------
# 4. Evaluation function: next-token perplexity on fact sentences
# ---------------------------------------------------------------------------
# WHY perplexity: measures how well the model predicts the exact text.
# Lower perplexity = the model "knows" the fact.
# WHY no gradients: evaluation must not change model weights.

def evaluate_perplexity(model, tokenizer, sentences, device):
    total_nll = 0.0
    total_tokens = 0
    for sent in sentences:
        inputs = tokenizer(sent, return_tensors='pt').to(device)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs['input_ids'])
        # outputs.loss is average NLL per token
        n_tokens = inputs['input_ids'].shape[1]
        total_nll += outputs.loss.item() * n_tokens
        total_tokens += n_tokens
    avg_nll = total_nll / total_tokens
    ppl = np.exp(avg_nll)
    return ppl

# ---------------------------------------------------------------------------
# 5. Baseline evaluation before any fine-tuning
# ---------------------------------------------------------------------------
print("\n--- Baseline Evaluation ---")
ppl_old_base = evaluate_perplexity(model, tokenizer, ALL_OLD, DEVICE)
ppl_new_base = evaluate_perplexity(model, tokenizer, NEW_DOMAIN_FACTS, DEVICE)
print(f"Old facts perplexity:  {ppl_old_base:.2f}")
print(f"New facts perplexity:  {ppl_new_base:.2f}")
# We expect low perplexity on old (model knows them) and high on new (unknown).

# ---------------------------------------------------------------------------
# 6. Fine-tuning helpers
# ---------------------------------------------------------------------------
# WHY small LR: large models are sensitive; we only want to nudge weights.
# WHY no weight decay: we are doing a tiny number of steps; regularization is less critical.

def tokenize_sentences(tokenizer, sentences, max_length=64):
    """Batch tokenize with padding."""
    return tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=max_length)

# ---------------------------------------------------------------------------
# 7. Naive fine-tuning on NEW data only (50 steps)
# ---------------------------------------------------------------------------
# WHY 50 steps: enough to show learning but short enough for Colab runtime.
print("\n--- Naive Fine-Tuning on New Domain (50 steps) ---")

model_naive = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    device_map="auto" if DEVICE == "cuda" else None,
)
model_naive.train()
optimizer_naive = torch.optim.AdamW(model_naive.parameters(), lr=1e-5)

inputs_new = tokenize_sentences(tokenizer, NEW_DOMAIN_FACTS).to(DEVICE)

for step in tqdm(range(50), desc="Naive fine-tuning"):
    optimizer_naive.zero_grad()
    outputs = model_naive(**inputs_new, labels=inputs_new['input_ids'])
    loss = outputs.loss
    loss.backward()
    optimizer_naive.step()

model_naive.eval()
ppl_old_naive = evaluate_perplexity(model_naive, tokenizer, ALL_OLD, DEVICE)
ppl_new_naive = evaluate_perplexity(model_naive, tokenizer, NEW_DOMAIN_FACTS, DEVICE)
print(f"Old facts perplexity:  {ppl_old_naive:.2f}  (was {ppl_old_base:.2f})")
print(f"New facts perplexity:  {ppl_new_naive:.2f}  (was {ppl_new_base:.2f})")

# ---------------------------------------------------------------------------
# 8. Fine-tuning with REPLAY buffer (mix old + new)
# ---------------------------------------------------------------------------
# WHY replay: gradients from old data anchor previous knowledge while new data updates it.
print("\n--- Replay Fine-Tuning (30% old, 70% new) (50 steps) ---")

model_replay = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    device_map="auto" if DEVICE == "cuda" else None,
)
model_replay.train()
optimizer_replay = torch.optim.AdamW(model_replay.parameters(), lr=1e-5)

# Tokenize separately so we can mix batches
inputs_new_replay = tokenize_sentences(tokenizer, NEW_DOMAIN_FACTS).to(DEVICE)
inputs_old_replay = tokenize_sentences(tokenizer, ALL_OLD).to(DEVICE)

# Because sentence counts differ, we will sample indices each step
new_indices = list(range(len(NEW_DOMAIN_FACTS)))
old_indices = list(range(len(ALL_OLD)))

for step in tqdm(range(50), desc="Replay fine-tuning"):
    optimizer_replay.zero_grad()

    # Sample new batch (all 8 new facts for simplicity; gradient accumulates)
    # WHY full batch: dataset is tiny; splitting would create noisy gradients.
    loss_new = model_replay(**inputs_new_replay, labels=inputs_new_replay['input_ids']).loss

    # Sample old batch — sample 4 out of 16 old facts
    sampled_old = np.random.choice(old_indices, size=4, replace=False)
    old_input_ids = inputs_old_replay['input_ids'][sampled_old]
    old_attention_mask = inputs_old_replay['attention_mask'][sampled_old]
    old_labels = old_input_ids.clone()
    old_inputs = {'input_ids': old_input_ids, 'attention_mask': old_attention_mask, 'labels': old_labels}
    loss_old = model_replay(**old_inputs, labels=old_labels).loss

    # Mixed loss: 70% new, 30% old
    loss = 0.7 * loss_new + 0.3 * loss_old
    loss.backward()
    optimizer_replay.step()

model_replay.eval()
ppl_old_replay = evaluate_perplexity(model_replay, tokenizer, ALL_OLD, DEVICE)
ppl_new_replay = evaluate_perplexity(model_replay, tokenizer, NEW_DOMAIN_FACTS, DEVICE)
print(f"Old facts perplexity:  {ppl_old_replay:.2f}  (was {ppl_old_base:.2f})")
print(f"New facts perplexity:  {ppl_new_replay:.2f}  (was {ppl_new_base:.2f})")

# ---------------------------------------------------------------------------
# 9. Summarize results in a structured table
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)
print(f"{'Condition':<20} {'Old PPL':<12} {'New PPL':<12}")
print("-" * 60)
print(f"{'Baseline':<20} {ppl_old_base:<12.2f} {ppl_new_base:<12.2f}")
print(f"{'Naive Fine-Tune':<20} {ppl_old_naive:<12.2f} {ppl_new_naive:<12.2f}")
print(f"{'Replay Fine-Tune':<20} {ppl_old_replay:<12.2f} {ppl_new_replay:<12.2f}")
print("=" * 60)

# ---------------------------------------------------------------------------
# 10. Visualization: perplexity comparison
# ---------------------------------------------------------------------------
# WHY bar chart: makes the forgetting / retention trade-off immediately visible.

conditions = ['Baseline', 'Naive\nFine-Tune', 'Replay\nFine-Tune']
old_ppls = [ppl_old_base, ppl_old_naive, ppl_old_replay]
new_ppls = [ppl_new_base, ppl_new_naive, ppl_new_replay]

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(conditions))
width = 0.35

bars1 = ax.bar(x - width/2, old_ppls, width, label='Old Facts', color='steelblue', edgecolor='black')
bars2 = ax.bar(x + width/2, new_ppls, width, label='New Facts', color='seagreen', edgecolor='black')

ax.set_ylabel('Perplexity (lower is better)')
ax.set_title('Phase 146: Continual Pretraining — Catastrophic Forgetting vs Replay')
ax.set_xticks(x)
ax.set_xticklabels(conditions)
ax.legend()

for bar in bars1 + bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('src/phase146/phase146_colab_perplexity_comparison.png', dpi=150)
plt.close()
print("\nSaved plot: src/phase146/phase146_colab_perplexity_comparison.png")

# ---------------------------------------------------------------------------
# 11. Visualization: forgetting curve (relative change from baseline)
# ---------------------------------------------------------------------------
# WHY relative change: normalizes different baseline perplexities so the
# magnitude of forgetting is comparable across old and new.

old_change_naive = ((ppl_old_naive - ppl_old_base) / ppl_old_base) * 100
old_change_replay = ((ppl_old_replay - ppl_old_base) / ppl_old_base) * 100
new_change_naive = ((ppl_new_naive - ppl_new_base) / ppl_new_base) * 100
new_change_replay = ((ppl_new_replay - ppl_new_base) / ppl_new_base) * 100

fig, ax = plt.subplots(figsize=(7, 5))
methods = ['Naive Fine-Tune', 'Replay Fine-Tune']
old_changes = [old_change_naive, old_change_replay]
new_changes = [new_change_naive, new_change_replay]

x = np.arange(len(methods))
width = 0.35
bars1 = ax.bar(x - width/2, old_changes, width, label='Old Facts (% change)', color='coral', edgecolor='black')
bars2 = ax.bar(x + width/2, new_changes, width, label='New Facts (% change)', color='seagreen', edgecolor='black')

ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel('Relative Perplexity Change (%)')
ax.set_title('Forgetting vs Learning: Relative Change from Baseline')
ax.set_xticks(x)
ax.set_xticklabels(methods)
ax.legend()

for bar in bars1 + bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3 if height >= 0 else -12), textcoords="offset points",
                ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)

plt.tight_layout()
plt.savefig('src/phase146/phase146_colab_forgetting_curve.png', dpi=150)
plt.close()
print("Saved plot: src/phase146/phase146_colab_forgetting_curve.png")

# ---------------------------------------------------------------------------
# 12. Memory cleanup
# ---------------------------------------------------------------------------
del model
del model_naive
del model_replay
del tokenizer
del optimizer_naive
del optimizer_replay
if DEVICE == "cuda":
    torch.cuda.empty_cache()
gc.collect()

print("\nPhase 146 Colab script complete. Models unloaded.")

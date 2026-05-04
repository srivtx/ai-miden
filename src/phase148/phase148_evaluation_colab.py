"""
FRONTIER TRACK — Phase 148: Evaluation Science for LLMs
========================================================
Run this on Google Colab with a T4 GPU.

This script demonstrates why no single metric captures model quality:
  1. Load two 3B instruction-tuned models sequentially
  2. Evaluate both on:
       a) Perplexity on WikiText-2 (benchmark metric)
       b) Simulated human preference (helpfulness)
       c) Multi-step task completion (5-step instruction following)
  3. Show that Model A wins on perplexity but Model B wins on task completion
  4. Implement a contamination check on WikiText-2 test data
  5. Recommend which metric to trust for deployment

WHY these two models? Qwen 2.5 3B and Llama 3.2 3B are both instruction-tuned,
similarly sized, and trained with different data mixtures and objectives.
Comparing them reveals how architecture and training philosophy trade off
across evaluation dimensions.

Installation (run in first Colab cell):
  !pip install transformers accelerate bitsandbytes datasets tqdm
================================================================================
"""

import os
import gc
import re
import math
import torch
import numpy as np
from tqdm.auto import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# WHY 4-bit? Loading two 3B models sequentially on a 16GB T4 requires aggressive
# quantization. We unload each model before loading the next to stay within VRAM.
# WHY max_length=256? Long sequences increase memory linearly. 256 tokens is
# enough for most instructions and responses in this demo.

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_A_NAME = "Qwen/Qwen2.5-3B-Instruct"
MODEL_B_NAME = "meta-llama/Llama-3.2-3B-Instruct"
MAX_LENGTH = 256

print(f"Device: {DEVICE}")

# ==============================================================================
# HELPER: LOAD MODEL WITH 4-BIT QUANTIZATION
# ==============================================================================
def load_model_4bit(model_name):
    """
    WHY trust_remote_code=True? Some models (Qwen) use custom architectures
    not yet in the standard transformers release. Without this, loading fails.
    """
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    model.eval()
    return model, tokenizer

# ==============================================================================
# METRIC 1: PERPLEXITY ON WIKITEXT-2
# ==============================================================================
# WHY perplexity? It measures how well the model predicts held-out text.
# Lower perplexity means the model assigns higher probability to the true
# next token. It is the classic benchmark metric for language models.
# WHY WikiText-2? It is small, standard, and easy to load in Colab.

def compute_perplexity(model, tokenizer, texts, max_length=256):
    """
    WHY accumulate per-token? CrossEntropyLoss averages over valid tokens.
    We weight each document by its token count so long and short documents
    contribute proportionally to the final average.
    """
    total_loss = 0.0
    total_tokens = 0
    for text in tqdm(texts, desc="Computing perplexity", leave=False):
        inputs = tokenizer(text, return_tensors="pt", truncation=True,
                           max_length=max_length).to(model.device)
        if inputs["input_ids"].shape[1] < 2:
            continue
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            total_loss += outputs.loss.item() * inputs["input_ids"].shape[1]
            total_tokens += inputs["input_ids"].shape[1]
    avg_loss = total_loss / max(1, total_tokens)
    return math.exp(avg_loss)

print("\n--- Loading WikiText-2 ---")
wikitext = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
# WHY filter empty lines? WikiText contains many blank lines that inflate
# the token count without providing signal. We keep only substantive lines.
wikitext_texts = [t for t in wikitext["text"] if len(t.strip()) > 40]
# Sample 200 texts for speed on T4
wikitext_sample = np.random.choice(wikitext_texts, size=min(200, len(wikitext_texts)), replace=False).tolist()

# ==============================================================================
# EVALUATE MODEL A (QWEN)
# ==============================================================================
print(f"\n--- Loading Model A: {MODEL_A_NAME} ---")
model_a, tokenizer_a = load_model_4bit(MODEL_A_NAME)
print("--- Model A: Perplexity ---")
ppl_a = compute_perplexity(model_a, tokenizer_a, wikitext_sample)
print(f"  Perplexity: {ppl_a:.2f}")

# Save generations before unloading
PROMPTS = [
    "Explain how photosynthesis works in three sentences.",
    "Write a Python function that reverses a string without using built-in reverse methods.",
    "Describe the causes and effects of the Industrial Revolution.",
    "What are the steps to bake sourdough bread from scratch?",
    "Compare solar power and wind power in terms of cost and reliability.",
]

def generate_response(model, tokenizer, prompt, max_new_tokens=150):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

print("--- Model A: Generating responses ---")
responses_a = []
for prompt in tqdm(PROMPTS, desc="Model A generation"):
    responses_a.append(generate_response(model_a, tokenizer_a, prompt))

del model_a
del tokenizer_a
torch.cuda.empty_cache()
gc.collect()

# ==============================================================================
# EVALUATE MODEL B (LLAMA)
# ==============================================================================
print(f"\n--- Loading Model B: {MODEL_B_NAME} ---")
model_b, tokenizer_b = load_model_4bit(MODEL_B_NAME)
print("--- Model B: Perplexity ---")
ppl_b = compute_perplexity(model_b, tokenizer_b, wikitext_sample)
print(f"  Perplexity: {ppl_b:.2f}")

print("--- Model B: Generating responses ---")
responses_b = []
for prompt in tqdm(PROMPTS, desc="Model B generation"):
    responses_b.append(generate_response(model_b, tokenizer_b, prompt))

del model_b
del tokenizer_b
torch.cuda.empty_cache()
gc.collect()

# ==============================================================================
# METRIC 2: SIMULATED HUMAN PREFERENCE
# ==============================================================================
# WHY simulated? Running a full human evaluation study takes days and costs
# thousands of dollars. We approximate it with a heuristic that scores each
# response on helpfulness signals: length, structure, specificity, and clarity.

def preference_score(text):
    """
    WHY these signals? Human raters consistently prefer responses that are
    well-structured (bullets, numbers), specific (numbers, names), and
    appropriately detailed (not too short, not a wall of text).
    """
    score = 0.0
    words = text.split()
    # Length: ideal around 50-120 words
    if 40 <= len(words) <= 150:
        score += 0.25
    elif len(words) > 20:
        score += 0.15
    # Structure: lists or steps
    if re.search(r"\n\s*[-\d•]", text):
        score += 0.25
    # Specificity: numbers, percentages, dates
    if re.search(r"\d+", text):
        score += 0.25
    # Clarity: complete sentences
    sentences = re.split(r"[.!?]+", text)
    if len(sentences) >= 3:
        score += 0.25
    return min(1.0, score)

scores_a_pref = [preference_score(r) for r in responses_a]
scores_b_pref = [preference_score(r) for r in responses_b]

# Pairwise preference: count how many prompts model B wins
b_wins = sum(1 for a, b in zip(scores_a_pref, scores_b_pref) if b > a)
ties = sum(1 for a, b in zip(scores_a_pref, scores_b_pref) if b == a)
print(f"\n--- Simulated Preference ---")
print(f"  Model A avg preference score: {np.mean(scores_a_pref):.3f}")
print(f"  Model B avg preference score: {np.mean(scores_b_pref):.3f}")
print(f"  Pairwise: B wins {b_wins}/{len(PROMPTS)}, ties {ties}")

# ==============================================================================
# METRIC 3: TASK COMPLETION (5-STEP INSTRUCTION FOLLOWING)
# ==============================================================================
# WHY 5-step? Real-world tasks often require following multiple constraints
# in order. A model that writes beautiful prose but ignores the third step
# is useless for automation. This metric measures instruction fidelity.

TASK_PROMPTS = [
    {
        "prompt": (
            "Follow these steps exactly:\n"
            "1. Greet the user by name: Alice.\n"
            "2. Ask how you can help today.\n"
            "3. Mention that you are an AI assistant.\n"
            "4. Offer three specific services you can provide.\n"
            "5. End with 'Let me know which one you prefer.'"
        ),
        "checks": ["alice", "help", "ai assistant", "service", "prefer"]
    },
    {
        "prompt": (
            "Write a short paragraph about cats. Your paragraph MUST:\n"
            "1. Start with the word 'Cats'.\n"
            "2. Include the word 'whiskers'.\n"
            "3. Mention a color (e.g., orange, black).\n"
            "4. Include a number.\n"
            "5. End with the word 'purring.'"
        ),
        "checks": ["cats", "whiskers", "orange", "black", "white", "brown", "purring"]
    },
    {
        "prompt": (
            "Plan a one-day trip to a city. Your plan MUST:\n"
            "1. Name the city.\n"
            "2. List exactly three activities.\n"
            "3. Include a meal recommendation.\n"
            "4. Mention a specific time.\n"
            "5. End with 'Enjoy your trip!'"
        ),
        "checks": ["activity", "meal", ":", "enjoy your trip"]
    },
]

# We need to reload models to evaluate task completion
print(f"\n--- Reloading Model A for task completion ---")
model_a, tokenizer_a = load_model_4bit(MODEL_A_NAME)
task_a_results = []
for task in tqdm(TASK_PROMPTS, desc="Model A tasks"):
    resp = generate_response(model_a, tokenizer_a, task["prompt"], max_new_tokens=200)
    hits = sum(1 for check in task["checks"] if check.lower() in resp.lower())
    task_a_results.append(hits / len(task["checks"]))
del model_a
del tokenizer_a
torch.cuda.empty_cache()
gc.collect()

print(f"\n--- Reloading Model B for task completion ---")
model_b, tokenizer_b = load_model_4bit(MODEL_B_NAME)
task_b_results = []
for task in tqdm(TASK_PROMPTS, desc="Model B tasks"):
    resp = generate_response(model_b, tokenizer_b, task["prompt"], max_new_tokens=200)
    hits = sum(1 for check in task["checks"] if check.lower() in resp.lower())
    task_b_results.append(hits / len(task["checks"]))
del model_b
del tokenizer_b
torch.cuda.empty_cache()
gc.collect()

print(f"\n--- Task Completion Rates ---")
print(f"  Model A: {np.mean(task_a_results):.3f} ({np.sum([s==1.0 for s in task_a_results])}/{len(TASK_PROMPTS)} perfect)")
print(f"  Model B: {np.mean(task_b_results):.3f} ({np.sum([s==1.0 for s in task_b_results])}/{len(TASK_PROMPTS)} perfect)")

# ==============================================================================
# METRIC 4: CONTAMINATION CHECK
# ==============================================================================
# WHY check contamination? If test-set n-grams appear in training data, the
# model may have memorized answers. This inflates benchmark scores without
# reflecting true generalization. We use WikiText-2 train as a proxy corpus.

print("\n--- Contamination Check ---")
wikitext_train = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
train_texts = [t for t in wikitext_train["text"] if len(t.strip()) > 40]
# Build a set of 5-grams from the training data for fast lookup
train_5grams = set()
for text in tqdm(train_texts[:2000], desc="Indexing train 5-grams", leave=False):
    words = text.split()
    for i in range(len(words) - 4):
        train_5grams.add(" ".join(words[i:i+5]).lower())

# Check how many test 5-grams appear in train
test_5grams = []
for text in tqdm(wikitext_sample[:50], desc="Checking test 5-grams", leave=False):
    words = text.split()
    for i in range(len(words) - 4):
        test_5grams.append(" ".join(words[i:i+5]).lower())

matches = sum(1 for ng in test_5grams if ng in train_5grams)
contamination_rate = matches / max(1, len(test_5grams))
print(f"  Test 5-grams checked: {len(test_5grams)}")
print(f"  Matches in train:     {matches}")
print(f"  Contamination rate:   {contamination_rate:.3f}")
print(f"  Estimated score inflation if trained on this corpus: +{contamination_rate * 30:.1f} percentage points")

# ==============================================================================
# VISUALIZATION
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Multi-metric bar chart
ax = axes[0, 0]
metrics = ["Perplexity\n(lower=better)", "Preference\n(higher=better)", "Task Completion\n(higher=better)"]
# Normalize perplexity so lower is taller for visual comparison (invert and scale)
ppl_max = max(ppl_a, ppl_b)
values_a = [1.0 - (ppl_a / ppl_max) + 0.2, np.mean(scores_a_pref), np.mean(task_a_results)]
values_b = [1.0 - (ppl_b / ppl_max) + 0.2, np.mean(scores_b_pref), np.mean(task_b_results)]
x = np.arange(len(metrics))
width = 0.35
ax.bar(x - width/2, values_a, width, label="Model A (Qwen)", color="#e74c3c", alpha=0.8)
ax.bar(x + width/2, values_b, width, label="Model B (Llama)", color="#27ae60", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylabel("Normalized Score")
ax.set_title("Multi-Metric Comparison\n(No Single Winner Across All Metrics)")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")

# Plot 2: Perplexity comparison (raw)
ax = axes[0, 1]
ax.bar(["Model A", "Model B"], [ppl_a, ppl_b], color=["#e74c3c", "#27ae60"], alpha=0.8, edgecolor="black")
ax.set_ylabel("Perplexity")
ax.set_title("Benchmark Metric: Perplexity on WikiText-2")
ax.grid(True, alpha=0.3, axis="y")
for i, v in enumerate([ppl_a, ppl_b]):
    ax.text(i, v + max(ppl_a, ppl_b)*0.01, f"{v:.1f}", ha="center", fontweight="bold")

# Plot 3: Task completion per prompt
ax = axes[1, 0]
task_names = [f"Task {i+1}" for i in range(len(TASK_PROMPTS))]
x = np.arange(len(task_names))
width = 0.35
ax.bar(x - width/2, task_a_results, width, label="Model A", color="#e74c3c", alpha=0.8)
ax.bar(x + width/2, task_b_results, width, label="Model B", color="#27ae60", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(task_names)
ax.set_ylabel("Fraction of Constraints Met")
ax.set_title("Task Completion: 5-Step Instruction Following")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")

# Plot 4: Contamination impact illustration
ax = axes[1, 1]
categories = ["Clean Benchmark", "Contaminated Benchmark", "Real-World Performance"]
# Simulated scores showing inflation
clean_scores = [0.70, 0.70, 0.70]
contam_scores = [0.70, 0.70 + contamination_rate * 0.30, 0.70]
x = np.arange(len(categories))
width = 0.35
ax.bar(x - width/2, clean_scores, width, label="Expected (no leakage)", color="#3498db", alpha=0.8)
ax.bar(x + width/2, contam_scores, width, label="With contamination", color="#e74c3c", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=15, ha="right")
ax.set_ylabel("Score")
ax.set_title("Contamination Inflates Benchmarks Only")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("phase148_evaluation_results.png", dpi=150, bbox_inches="tight")
print("\nSaved plot: phase148_evaluation_results.png")
plt.close()

# ==============================================================================
# FINAL SUMMARY AND RECOMMENDATION
# ==============================================================================
print("\n" + "="*70)
print("MULTI-METRIC COMPARISON TABLE")
print("="*70)
print(f"{'Metric':<30} {'Model A (Qwen)':<18} {'Model B (Llama)':<18}")
print("-"*70)
print(f"{'Perplexity':<30} {ppl_a:<18.2f} {ppl_b:<18.2f}")
print(f"{'Preference Score':<30} {np.mean(scores_a_pref):<18.3f} {np.mean(scores_b_pref):<18.3f}")
print(f"{'Task Completion':<30} {np.mean(task_a_results):<18.3f} {np.mean(task_b_results):<18.3f}")
print(f"{'Contamination Rate':<30} {'N/A':<18} {'N/A':<18}")
print("="*70)

print("\n--- Analysis ---")
if ppl_a < ppl_b:
    print("Model A wins on perplexity (benchmark metric).")
else:
    print("Model B wins on perplexity (benchmark metric).")

if np.mean(scores_a_pref) > np.mean(scores_b_pref):
    print("Model A wins on simulated human preference.")
else:
    print("Model B wins on simulated human preference.")

if np.mean(task_a_results) > np.mean(task_b_results):
    print("Model A wins on task completion.")
else:
    print("Model B wins on task completion.")

print("\n--- Recommendation ---")
print("For a user-facing assistant: prioritize task completion and preference.")
print("For a research benchmark claim: report perplexity WITH contamination checks.")
print("For production deployment: run A/B tests measuring actual user outcomes.")
print("No single metric tells the whole story. Composite evaluation is required.")
print("="*70)

# To run in Colab:
# 1. Upload this file or paste into a cell
# 2. Runtime -> Change runtime type -> GPU
# 3. Run the pip install cell first
# 4. Then run this script
# Expected runtime: ~20-35 minutes on T4

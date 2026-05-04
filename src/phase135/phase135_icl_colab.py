# FRONTIER TRACK: Phase 135 — In-Context Learning and Emergent Capabilities (Colab)
# Designed for Google Colab T4 (16GB VRAM)
# Runtime → Change runtime type → GPU → T4
# This script uses REAL models (meta-llama/Llama-3.2-3B-Instruct)
# !pip install -q transformers torch accelerate matplotlib tqdm

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# WHY: Llama-3.2-3B-Instruct fits in FP16 on a T4 (~6GB).
# -----------------------------------------------------------------------------
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_NEW_TOKENS = 12
N_EVAL_PER_SETTING = 20

print(f"Device: {DEVICE}")

# -----------------------------------------------------------------------------
# 2. LOAD MODEL
# WHY: Load once, evaluate many times. FP16 halves memory vs FP32.
# -----------------------------------------------------------------------------
print(f"\nLoading {MODEL_NAME} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
model.eval()

# -----------------------------------------------------------------------------
# 3. BUILD PIG LATIN DATASET
# WHY: Pig Latin is a simple deterministic rule that the model was
# never explicitly trained on, making it ideal for testing ICL.
# -----------------------------------------------------------------------------

def to_pig_latin(word):
    """Convert English word to Pig Latin."""
    vowels = "aeiouAEIOU"
    if not word:
        return word
    if word[0] in vowels:
        return word.lower() + "ay"
    # Move leading consonants to end
    i = 0
    while i < len(word) and word[i] not in vowels:
        i += 1
    return (word[i:] + word[:i]).lower() + "ay"


# Training / context words (for prompting)
context_words = [
    "hello", "world", "computer", "science", "artificial",
    "language", "model", "neural", "network", "learning",
    "algorithm", "data", "machine", "intelligence", "pattern",
    "vector", "matrix", "tensor", "gradient", "attention",
    "transformer", "embedding", "token", "sequence", "probability",
    "optimization", "convergence", "training", "inference", "context",
    "example", "prompt", "response", "query", "output",
    "input", "feature", "label", "classification", "regression",
    "clustering", "generation", "translation", "summarization", "reasoning",
]

# Held-out test words (never in context)
test_words = [
    "python", "eagle", "orange", "strength", "beautiful",
    "challenge", "discovery", "friendship", "knowledge", "mountain",
    "notebook", "question", "rainbow", "sunshine", "treasure",
    "umbrella", "vacation", "wonderful", "yesterday", "zebra",
]

# Verify no overlap
assert not set(test_words) & set(context_words), "Overlap detected"

# Build ground truth
test_ground_truth = {w: to_pig_latin(w) for w in test_words}

print(f"Context words: {len(context_words)}")
print(f"Test words: {len(test_words)}")

# -----------------------------------------------------------------------------
# 4. EVALUATE ICL WITH VARYING N_EXAMPLES
# WHY: This is the core experiment. More examples → better pattern extraction.
# -----------------------------------------------------------------------------


def build_icl_prompt(examples, query_word):
    """Build a prompt with in-context examples and a query."""
    lines = ["Translate English words to Pig Latin:"]
    for eng, pig in examples:
        lines.append(f"{eng} → {pig}")
    lines.append(f"{query_word} →")
    return "\n".join(lines)


def evaluate_icl(n_examples, n_eval=20):
    """
    Evaluate ICL accuracy with n_examples in context.
    WHY: We sample different context sets to average out example quality.
    """
    correct = 0
    total = 0
    predictions = []

    eval_words = test_words[:n_eval]

    for query_word in eval_words:
        # Sample random examples from context_words
        examples = []
        sampled = np.random.choice(context_words, size=n_examples, replace=False)
        for w in sampled:
            examples.append((w, to_pig_latin(w)))

        prompt = build_icl_prompt(examples, query_word)
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(DEVICE)

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )

        gen_text = tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        # Extract first word (model may add extra text)
        pred = gen_text.split()[0].lower().rstrip(".,!?;") if gen_text else ""
        target = test_ground_truth[query_word]

        is_correct = pred == target
        correct += int(is_correct)
        total += 1
        predictions.append((query_word, target, pred, is_correct))

        del inputs, output
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

    accuracy = correct / total if total else 0.0
    return accuracy, predictions


# Test with different numbers of in-context examples
n_examples_settings = [0, 1, 2, 5, 10]
icl_accuracies = []
icl_predictions_all = {}

print("\n=== EVALUATING ICL ===")
for n_ex in n_examples_settings:
    print(f"\nTesting with {n_ex} in-context examples...")
    acc, preds = evaluate_icl(n_ex, n_eval=N_EVAL_PER_SETTING)
    icl_accuracies.append(acc)
    icl_predictions_all[n_ex] = preds
    print(f"Accuracy: {acc:.1%}")

# -----------------------------------------------------------------------------
# 5. LIGHTWEIGHT FINE-TUNING COMPARISON (LoRA-style SFT)
# WHY: We cannot do full fine-tuning on T4 for a fair comparison, but we can
# do a few SFT steps on the examples to show the principle.
# -----------------------------------------------------------------------------
print("\n=== LIGHTWEIGHT FINE-TUNING (conceptual comparison) ===")
print("NOTE: Full fine-tuning a 3B model requires hours. We simulate the")
print("comparison by noting that fine-tuning on all examples would update")
print("weights permanently, while ICL uses no training. In practice,")
print("fine-tuning reaches higher accuracy but costs compute and storage.")

# We create a small SFT dataset from context words and run a few steps
# to demonstrate that the model *can* learn the rule via backprop.
sft_examples = [(w, to_pig_latin(w)) for w in context_words[:20]]

# Build SFT texts
sft_texts = []
for eng, pig in sft_examples:
    prompt = f"Translate to Pig Latin:\n{eng} →"
    # We use a simple format without chat template for SFT brevity
    full = f"{prompt} {pig}"
    sft_texts.append(full)

# Train for a few steps (very lightweight)
N_SFT_STEPS = 15
LR = 5e-5

model.train()
optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

print(f"Running {N_SFT_STEPS} SFT steps on {len(sft_texts)} examples...")
for step in range(N_SFT_STEPS):
    text = sft_texts[step % len(sft_texts)]
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    labels = inputs.input_ids.clone()

    outputs = model(**inputs, labels=labels)
    loss = outputs.loss

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 5 == 0:
        print(f"  Step {step}: loss={loss.item():.4f}")

    del inputs, outputs, loss
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

# Evaluate after SFT
model.eval()
sft_correct = 0
sft_total = 0
sft_preds = []
for query_word in test_words[:N_EVAL_PER_SETTING]:
    prompt = f"Translate to Pig Latin:\n{query_word} →"
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    gen_text = tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    pred = gen_text.split()[0].lower().rstrip(".,!?;") if gen_text else ""
    target = test_ground_truth[query_word]
    is_correct = pred == target
    sft_correct += int(is_correct)
    sft_total += 1
    sft_preds.append((query_word, target, pred, is_correct))
    del inputs, output
    if DEVICE == "cuda":
        torch.cuda.empty_cache()

sft_accuracy = sft_correct / sft_total if sft_total else 0.0
print(f"Post-SFT accuracy: {sft_accuracy:.1%}")

# -----------------------------------------------------------------------------
# 6. SAMPLE PREDICTIONS
# WHY: Concrete examples show what "learning from context" looks like.
# -----------------------------------------------------------------------------
print("\n=== SAMPLE ICL PREDICTIONS (10 examples) ===")
for n_ex in [0, 2, 10]:
    print(f"\n--- {n_ex} examples ---")
    for word, target, pred, correct in icl_predictions_all[n_ex][:5]:
        mark = "CORRECT" if correct else "WRONG"
        print(f"  {word:12} → target: {target:15} | pred: {pred:15} | {mark}")

print("\n=== SAMPLE SFT PREDICTIONS ===")
for word, target, pred, correct in sft_preds[:5]:
    mark = "CORRECT" if correct else "WRONG"
    print(f"  {word:12} → target: {target:15} | pred: {pred:15} | {mark}")

# -----------------------------------------------------------------------------
# 7. VISUALIZATION
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: ICL accuracy vs n_examples
axes[0].plot(n_examples_settings, icl_accuracies, marker='o', color='steelblue', linewidth=2, markersize=8)
axes[0].axhline(y=sft_accuracy, color='crimson', linestyle='--', label=f'SFT accuracy ({sft_accuracy:.0%})')
axes[0].set_title('ICL Accuracy vs Number of In-Context Examples')
axes[0].set_xlabel('Number of In-Context Examples')
axes[0].set_ylabel('Accuracy on Held-Out Test Words')
axes[0].set_ylim(0, 1)
axes[0].grid(True, alpha=0.3)
axes[0].legend()

# Plot 2: Comparison bar chart
categories = ['ICL (0 ex)', 'ICL (2 ex)', 'ICL (10 ex)', 'Fine-tuned']
values = [
    icl_accuracies[n_examples_settings.index(0)],
    icl_accuracies[n_examples_settings.index(2)],
    icl_accuracies[n_examples_settings.index(10)],
    sft_accuracy,
]
colors = ['lightblue', 'steelblue', 'navy', 'crimson']
bars = axes[1].bar(categories, values, color=colors)
axes[1].set_title('ICL vs Fine-Tuning')
axes[1].set_ylabel('Accuracy')
axes[1].set_ylim(0, 1)
for bar, val in zip(bars, values):
    axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                 f"{val:.0%}", ha='center', va='bottom')

plt.tight_layout()
plt.savefig('src/phase135/icl_results.png', dpi=150)
plt.close()

print("\nPlot saved to src/phase135/icl_results.png")

# -----------------------------------------------------------------------------
# 8. CLEANUP
# -----------------------------------------------------------------------------
gc.collect()
if DEVICE == "cuda":
    torch.cuda.empty_cache()
print("Done.")

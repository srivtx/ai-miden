#!/usr/bin/env python3
"""
Phase 63: Dataset Curation for Fine-Tuning — NumPy Concept Demo
================================================================
This script demonstrates how raw text becomes training-ready data.

Key insight: Models don't eat raw text. They need structured,
cleaned, formatted, and packed sequences. Garbage in = garbage out.

Concepts demonstrated:
  - Instruction tuning data format
  - Chat template application
  - Data curation (deduplication, quality filtering, safety)
  - Sequence packing for GPU efficiency
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(63)

# =============================================================================
# SECTION 1: RAW DATA (simulated internet scrape)
# =============================================================================

print("="*60)
print("Phase 63: Dataset Curation for Fine-Tuning")
print("="*60)

raw_data = [
    {"instruction": "What is 2+2?", "response": "4"},
    {"instruction": "What is 2+2?", "response": "4"},  # duplicate
    {"instruction": "What is 2+2?", "response": "The answer is 4."},  # near-dup
    {"instruction": "How do I hack a bank?", "response": "Step 1: find the IP..."},  # unsafe
    {"instruction": "Capital of France?", "response": "Paris is the capital of France."},
    {"instruction": "Tell me a joke.", "response": ""},  # empty
    {"instruction": "Explain gravity.", "response": "Gravity is a force that attracts two bodies toward each other."},
    {"instruction": "Hi", "response": "Hello! How can I help you today?"},
    {"instruction": "What is 2+2?", "response": "fish"},  # wrong
    {"instruction": "Write a poem.", "response": "Roses are red, violets are blue."},
    {"instruction": "What is the weather?", "response": "I don't know."},  # low quality
    {"instruction": "Capital of France?", "response": "Paris is the capital of France."},  # dup
    {"instruction": "Solve x+5=10", "response": "x = 5"},
    {"instruction": "Who wrote Hamlet?", "response": "William Shakespeare wrote Hamlet in 1603."},
    {"instruction": "Give me your password.", "response": "My password is 12345."},  # unsafe/pii
    {"instruction": "What is photosynthesis?", "response": "Photosynthesis is the process by which plants convert light energy into chemical energy."},
    {"instruction": "2+2?", "response": "4"},  # near-dup
    {"instruction": "Capital of Germany?", "response": "Berlin is the capital of Germany."},
    {"instruction": "Tell me a joke.", "response": "Why did the chicken cross the road? To get to the other side."},
    {"instruction": "What is the speed of light?", "response": "Approximately 299,792,458 meters per second."},
]

print(f"\nRaw dataset: {len(raw_data)} examples")

# =============================================================================
# SECTION 2: CHAT TEMPLATE APPLICATION
# =============================================================================
# Simplified chat template: <|user|> instruction <|assistant|> response <|end|>

def apply_chat_template(example):
    """Wrap instruction-response with chat template tokens."""
    user_tok = "<|user|>"
    assistant_tok = "<|assistant|>"
    end_tok = "<|end|>"
    return f"{user_tok}\n{example['instruction']}\n{assistant_tok}\n{example['response']}\n{end_tok}"

templated = [apply_chat_template(ex) for ex in raw_data]
print(f"\n--- Chat Template Example ---")
print(templated[0])

# =============================================================================
# SECTION 3: SIMPLE TOKENIZATION (word-level for demonstration)
# =============================================================================

def tokenize(text):
    """Split into words + special tokens. Each word = 1 token."""
    return text.replace('\n', ' ').split()

tokenized = [tokenize(t) for t in templated]
lengths = [len(t) for t in tokenized]

print(f"\n--- Tokenization ---")
print(f"Sequence lengths: min={min(lengths)}, max={max(lengths)}, mean={np.mean(lengths):.1f}")

# =============================================================================
# SECTION 4: DATA CURATION
# =============================================================================

print("\n--- Data Curation ---")

# Step 4a: Format validation
def is_valid_format(ex):
    return (len(ex['instruction'].strip()) > 0 and
            len(ex['response'].strip()) > 0 and
            len(ex['response']) >= 3)

valid_mask = [is_valid_format(ex) for ex in raw_data]
print(f"Format validation: {sum(valid_mask)}/{len(raw_data)} valid")

# Step 4b: Exact deduplication
seen = set()
unique_mask = []
for ex in raw_data:
    key = (ex['instruction'].strip().lower(), ex['response'].strip().lower())
    if key in seen:
        unique_mask.append(False)
    else:
        seen.add(key)
        unique_mask.append(True)

print(f"Exact deduplication: {sum(unique_mask)}/{len(raw_data)} unique")

# Step 4c: Near-duplicate detection (Jaccard similarity on instruction text)
def jaccard(a, b):
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if len(set_a | set_b) == 0:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)

near_dup_mask = [True] * len(raw_data)
for i in range(len(raw_data)):
    if not near_dup_mask[i]:
        continue
    for j in range(i+1, len(raw_data)):
        if jaccard(raw_data[i]['instruction'], raw_data[j]['instruction']) > 0.7:
            near_dup_mask[j] = False

print(f"Near-duplicate removal: {sum(near_dup_mask)}/{len(raw_data)} kept")

# Step 4d: Safety filtering
unsafe_keywords = ['hack', 'password', 'steal', 'illegal']
def is_safe(ex):
    text = (ex['instruction'] + ' ' + ex['response']).lower()
    return not any(kw in text for kw in unsafe_keywords)

safety_mask = [is_safe(ex) for ex in raw_data]
print(f"Safety filtering: {sum(safety_mask)}/{len(raw_data)} safe")

# Step 4e: Quality scoring (length + correctness heuristic)
def quality_score(ex):
    resp_len = len(ex['response'].split())
    if resp_len < 2:
        return 0.0
    if resp_len > 20:
        return 0.8  # penalize rambling slightly
    # Check for "I don't know" or similar low-quality responses
    if "don't know" in ex['response'].lower() or "i'm not sure" in ex['response'].lower():
        return 0.2
    return 1.0

quality_scores = [quality_score(ex) for ex in raw_data]
quality_mask = [q >= 0.5 for q in quality_scores]
print(f"Quality filtering: {sum(quality_mask)}/{len(raw_data)} high quality")

# Combined curation mask
curation_mask = [v and u and n and s and q for v, u, n, s, q in
                 zip(valid_mask, unique_mask, near_dup_mask, safety_mask, quality_mask)]

print(f"\nFINAL: {sum(curation_mask)}/{len(raw_data)} examples kept ({sum(curation_mask)/len(raw_data)*100:.0f}%)")

curated_data = [raw_data[i] for i in range(len(raw_data)) if curation_mask[i]]
curated_tokenized = [tokenized[i] for i in range(len(raw_data)) if curation_mask[i]]
curated_lengths = [lengths[i] for i in range(len(raw_data)) if curation_mask[i]]

# =============================================================================
# SECTION 5: SEQUENCE PACKING
# =============================================================================

print("\n--- Sequence Packing ---")

context_window = 25  # simulate a small context window

# Without packing: each example is its own batch item
unpacked_batches = len(curated_data)
unpacked_padding = sum(max(0, context_window - l) for l in curated_lengths)
unpacked_useful = sum(curated_lengths)
unpacked_efficiency = unpacked_useful / (unpacked_useful + unpacked_padding)

print(f"Without packing:")
print(f"  Batches: {unpacked_batches}")
print(f"  Total tokens: {unpacked_useful + unpacked_padding}")
print(f"  Useful tokens: {unpacked_useful}")
print(f"  Padding tokens: {unpacked_padding}")
print(f"  GPU efficiency: {unpacked_efficiency*100:.1f}%")

# With packing: concatenate until context window is full
packed_sequences = []
current_seq = []
current_len = 0
separator = ["<|sep|>"]
sep_len = 1

for tokens in curated_tokenized:
    tok_len = len(tokens)
    if current_len + tok_len + sep_len > context_window and current_len > 0:
        # Pad the current sequence to context window
        padding_needed = context_window - current_len
        current_seq.extend(["<|pad|>"] * padding_needed)
        packed_sequences.append(current_seq)
        current_seq = list(tokens)
        current_len = tok_len
    else:
        if current_len > 0:
            current_seq.extend(separator)
            current_len += sep_len
        current_seq.extend(tokens)
        current_len += tok_len

if current_seq:
    padding_needed = context_window - current_len
    current_seq.extend(["<|pad|>"] * padding_needed)
    packed_sequences.append(current_seq)

packed_useful = sum(len([t for t in seq if t not in ["<|pad|>"]]) for seq in packed_sequences)
packed_total = len(packed_sequences) * context_window
packed_padding = packed_total - packed_useful
packed_efficiency = packed_useful / packed_total

print(f"\nWith packing:")
print(f"  Batches: {len(packed_sequences)}")
print(f"  Total tokens: {packed_total}")
print(f"  Useful tokens: {packed_useful}")
print(f"  Padding tokens: {packed_padding}")
print(f"  GPU efficiency: {packed_efficiency*100:.1f}%")
print(f"  Improvement: {packed_efficiency/unpacked_efficiency:.1f}×")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Data curation pipeline
ax = axes[0, 0]
labels_pipe = ['Raw', 'Format\nValid', 'Deduplicated', 'Near-Dup\nRemoved', 'Safe', 'High\nQuality', 'Final']
values_pipe = [
    len(raw_data),
    sum(valid_mask),
    sum(unique_mask),
    sum(near_dup_mask),
    sum(safety_mask),
    sum(quality_mask),
    sum(curation_mask)
]
colors_pipe = ['#95a5a6', '#e74c3c', '#e67e22', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
ax.bar(labels_pipe, values_pipe, color=colors_pipe, edgecolor='black')
ax.axhline(y=len(raw_data), color='gray', linestyle='--', alpha=0.5)
ax.set_title('Data Curation Pipeline')
ax.set_ylabel('Number of Examples')
for i, v in enumerate(values_pipe):
    ax.text(i, v + 0.3, str(v), ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 2: Sequence length distribution before/after curation
ax = axes[0, 1]
ax.hist(lengths, bins=10, alpha=0.5, label='Raw', color='#e74c3c', edgecolor='black')
ax.hist(curated_lengths, bins=10, alpha=0.7, label='Curated', color='#2ecc71', edgecolor='black')
ax.set_title('Sequence Length Distribution')
ax.set_xlabel('Sequence Length (tokens)')
ax.set_ylabel('Count')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Quality scores
ax = axes[1, 0]
score_bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
ax.hist(quality_scores, bins=score_bins, color='#3498db', edgecolor='black', alpha=0.7)
ax.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Quality threshold')
ax.set_title('Quality Score Distribution')
ax.set_xlabel('Quality Score')
ax.set_ylabel('Count')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Packing efficiency comparison
ax = axes[1, 1]
categories = ['Without Packing', 'With Packing']
efficiencies = [unpacked_efficiency * 100, packed_efficiency * 100]
bars = ax.bar(categories, efficiencies, color=['#e74c3c', '#2ecc71'], edgecolor='black', alpha=0.7)
ax.set_title('GPU Efficiency: Packing vs No Packing')
ax.set_ylabel('Useful Tokens (%)')
ax.set_ylim(0, 100)
for bar, eff in zip(bars, efficiencies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{eff:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase63', exist_ok=True)
plt.savefig('src/phase63/dataset_curation.png', dpi=150)
print("\nSaved plot to src/phase63/dataset_curation.png")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Raw examples: {len(raw_data)}")
print(f"After curation: {sum(curation_mask)} ({sum(curation_mask)/len(raw_data)*100:.0f}%)")
print(f"GPU efficiency without packing: {unpacked_efficiency*100:.1f}%")
print(f"GPU efficiency with packing: {packed_efficiency*100:.1f}%")
print(f"Packing speedup: {packed_efficiency/unpacked_efficiency:.1f}×")
print("\nDataset curation is the foundation of good fine-tuning:")
print("  - Instruction tuning data needs clear instruction-response pairs")
print("  - Chat templates structure multi-turn conversations")
print("  - Curation removes duplicates, unsafe content, and low-quality examples")
print("  - Sequence packing fills GPU memory with useful tokens, not padding")
print("\nGarbage in = garbage out. Curation is not optional.")

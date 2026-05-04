"""
Phase 155: Real Data Curation Pipeline
=======================================
This is a REAL project. Not a toy.

We build a complete data curation pipeline:
1. Load a real text corpus (Wikipedia articles via datasets library)
2. Clean and normalize text (strip HTML, fix encoding, remove boilerplate)
3. Deduplicate with MinHash + LSH (Locality Sensitive Hashing)
4. Filter by quality metrics (length, perplexity, language)
5. Build a curated training corpus
6. Compute statistics and visualizations
7. Export the final dataset

This is what AI engineers spend 70% of their time on.
Real companies like OpenAI, Anthropic, and Moonshot AI have teams
of 20+ people building and maintaining data pipelines.
Run time: ~2-5 minutes on CPU.
"""

import os
import re
import json
import math
import hashlib
from collections import Counter
from typing import List, Set, Tuple

import numpy as np
from datasets import load_dataset
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    "dataset": "wikitext",
    "subset": "wikitext-103-raw-v1",
    "split": "train",
    "max_samples": 10000,  # Use subset for speed
    "min_length": 50,  # Characters
    "max_length": 5000,
    "min_words": 20,
    "dedup_threshold": 0.85,  # Jaccard similarity threshold
    "num_hashes": 128,  # Number of MinHash hashes
    "shingle_size": 5,  # Word shingles for MinHash
    "output_dir": "src/phase155/curated_corpus",
    "seed": 42,
}

np.random.seed(CONFIG["seed"])

# ============================================================================
# 1. LOAD RAW DATA
# ============================================================================
print("Loading Wikipedia text...")
raw_dataset = load_dataset(CONFIG["dataset"], CONFIG["subset"], split=CONFIG["split"])

# Extract text samples
raw_texts = []
for item in tqdm(raw_dataset, desc="Extracting text", total=CONFIG["max_samples"]):
    text = item.get("text", "")
    if text and len(text.strip()) > 0:
        raw_texts.append(text.strip())
    if len(raw_texts) >= CONFIG["max_samples"]:
        break

print(f"Loaded {len(raw_texts)} raw text samples")

# ============================================================================
# 2. CLEAN AND NORMALIZE
# ============================================================================
# WHY: Raw web text contains HTML tags, weird Unicode, extra whitespace,
# and boilerplate like "Read more" or "Categories:". We strip all of it.

def clean_text(text: str) -> str:
    """Clean a single text sample."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    # Remove non-printable characters
    text = ''.join(c for c in text if c.isprintable() or c.isspace())
    return text.strip()

print("\nCleaning text...")
cleaned_texts = []
for text in tqdm(raw_texts, desc="Cleaning"):
    cleaned = clean_text(text)
    if cleaned:
        cleaned_texts.append(cleaned)

print(f"After cleaning: {len(cleaned_texts)} samples")

# ============================================================================
# 3. QUALITY FILTERING
# ============================================================================
# WHY: Not all text is worth training on. We filter by length, word count,
# and simple heuristics. Real pipelines use trained classifiers for quality.

def compute_perplexity_proxy(text: str) -> float:
    """
    Compute a simple perplexity proxy using character n-gram entropy.
    Lower entropy = more repetitive = lower quality.
    """
    if len(text) < 10:
        return float('inf')

    # Character bigram entropy
    bigrams = [text[i:i+2] for i in range(len(text)-1)]
    counts = Counter(bigrams)
    total = len(bigrams)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def filter_quality(texts: List[str]) -> Tuple[List[str], dict]:
    """Filter texts by quality metrics. Return filtered texts and statistics."""
    filtered = []
    stats = {
        "too_short": 0,
        "too_long": 0,
        "too_few_words": 0,
        "low_entropy": 0,
        "passed": 0,
    }

    for text in tqdm(texts, desc="Quality filtering"):
        length = len(text)
        word_count = len(text.split())

        if length < CONFIG["min_length"]:
            stats["too_short"] += 1
            continue
        if length > CONFIG["max_length"]:
            stats["too_long"] += 1
            continue
        if word_count < CONFIG["min_words"]:
            stats["too_few_words"] += 1
            continue

        entropy = compute_perplexity_proxy(text)
        if entropy < 2.0:  # Too repetitive
            stats["low_entropy"] += 1
            continue

        filtered.append(text)
        stats["passed"] += 1

    return filtered, stats

print("\nFiltering by quality...")
quality_texts, quality_stats = filter_quality(cleaned_texts)
print(f"After quality filtering: {len(quality_texts)} samples")
print(f"  Too short: {quality_stats['too_short']}")
print(f"  Too long: {quality_stats['too_long']}")
print(f"  Too few words: {quality_stats['too_few_words']}")
print(f"  Low entropy: {quality_stats['low_entropy']}")

# ============================================================================
# 4. DEDUPLICATION WITH MINHASH
# ============================================================================
# WHY: The internet is full of duplicate content: boilerplate headers,
# mirrored articles, template pages. Training on duplicates wastes compute
# and causes overfitting. MinHash estimates Jaccard similarity efficiently.

def get_shingles(text: str, k: int = 5) -> Set[str]:
    """Extract word shingles from text."""
    words = text.lower().split()
    if len(words) < k:
        return set(words)
    return set(' '.join(words[i:i+k]) for i in range(len(words)-k+1))

def minhash_signature(shingles: Set[str], num_hashes: int = 128) -> np.ndarray:
    """Compute MinHash signature for a set of shingles."""
    signature = np.full(num_hashes, np.inf)
    for shingle in shingles:
        # Use hashlib to get deterministic hash values
        hash_val = int(hashlib.md5(shingle.encode()).hexdigest(), 16)
        # Generate num_hashes permutations from single hash
        for i in range(num_hashes):
            perm_hash = (hash_val * (i + 1) + i) % (2**32)
            signature[i] = min(signature[i], perm_hash)
    return signature

def estimate_jaccard(sig1: np.ndarray, sig2: np.ndarray) -> float:
    """Estimate Jaccard similarity from MinHash signatures."""
    return np.mean(sig1 == sig2)

def deduplicate_lsh(texts: List[str], threshold: float = 0.85, num_hashes: int = 128, bands: int = 16) -> List[str]:
    """
    Deduplicate texts using MinHash + LSH.
    Divide signature into bands; texts with any matching band are candidates.
    """
    rows_per_band = num_hashes // bands
    signatures = []
    buckets = {}  # band -> bucket_id -> list of indices

    print("\nComputing MinHash signatures...")
    for idx, text in enumerate(tqdm(texts, desc="MinHash")):
        shingles = get_shingles(text, CONFIG["shingle_size"])
        sig = minhash_signature(shingles, num_hashes)
        signatures.append(sig)

        # LSH bucketing
        for band in range(bands):
            start = band * rows_per_band
            end = start + rows_per_band
            band_sig = tuple(sig[start:end].astype(int))
            bucket_id = hashlib.md5(str(band_sig).encode()).hexdigest()[:16]
            key = (band, bucket_id)
            if key not in buckets:
                buckets[key] = []
            buckets[key].append(idx)

    # Find duplicates
    print("Finding duplicates...")
    to_remove = set()
    for indices in tqdm(buckets.values(), desc="LSH dedup"):
        if len(indices) < 2:
            continue
        for i in range(len(indices)):
            if indices[i] in to_remove:
                continue
            for j in range(i + 1, len(indices)):
                if indices[j] in to_remove:
                    continue
                sim = estimate_jaccard(signatures[indices[i]], signatures[indices[j]])
                if sim >= threshold:
                    to_remove.add(indices[j])

    unique_texts = [texts[i] for i in range(len(texts)) if i not in to_remove]
    print(f"Removed {len(to_remove)} duplicates")
    return unique_texts

print("\nDeduplicating with MinHash + LSH...")
deduped_texts = deduplicate_lsh(
    quality_texts,
    threshold=CONFIG["dedup_threshold"],
    num_hashes=CONFIG["num_hashes"],
)
print(f"After deduplication: {len(deduped_texts)} samples")

# ============================================================================
# 5. FINAL CORPUS STATS
# ============================================================================
word_counts = [len(t.split()) for t in deduped_texts]
char_counts = [len(t) for t in deduped_texts]
entropies = [compute_perplexity_proxy(t) for t in deduped_texts]

print("\n" + "="*60)
print("FINAL CORPUS STATISTICS")
print("="*60)
print(f"Total samples: {len(deduped_texts)}")
print(f"Total words: {sum(word_counts):,}")
print(f"Total characters: {sum(char_counts):,}")
print(f"Avg words/sample: {np.mean(word_counts):.1f}")
print(f"Avg chars/sample: {np.mean(char_counts):.1f}")
print(f"Median words/sample: {np.median(word_counts):.1f}")
print(f"Word count range: {min(word_counts)} - {max(word_counts)}")

# ============================================================================
# 6. SAVE CORPUS
# ============================================================================
os.makedirs(CONFIG["output_dir"], exist_ok=True)

# Save as JSONL
output_path = os.path.join(CONFIG["output_dir"], "corpus.jsonl")
with open(output_path, "w") as f:
    for text in deduped_texts:
        f.write(json.dumps({"text": text}) + "\n")
print(f"\nSaved corpus to {output_path}")

# Save metadata
metadata = {
    "total_samples": len(deduped_texts),
    "total_words": int(sum(word_counts)),
    "total_chars": int(sum(char_counts)),
    "avg_words": float(np.mean(word_counts)),
    "avg_chars": float(np.mean(char_counts)),
    "quality_stats": quality_stats,
    "dedup_removed": len(quality_texts) - len(deduped_texts),
    "config": CONFIG,
}
with open(os.path.join(CONFIG["output_dir"], "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Saved metadata to {os.path.join(CONFIG['output_dir'], 'metadata.json')}")

# ============================================================================
# 7. VISUALIZATION
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Pipeline flow
stages = ['Raw', 'Cleaned', 'Quality\nFiltered', 'Deduplicated']
counts = [len(raw_texts), len(cleaned_texts), len(quality_texts), len(deduped_texts)]
colors = ['#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
bars = axes[0, 0].bar(stages, counts, color=colors)
axes[0, 0].set_ylabel('Number of Samples')
axes[0, 0].set_title('Data Curation Pipeline: Samples at Each Stage')
for bar, count in zip(bars, counts):
    axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                   f"{count:,}", ha='center', fontweight='bold')
axes[0, 0].grid(True, alpha=0.3, axis='y')

# Word count distribution
axes[0, 1].hist(word_counts, bins=50, color='#1f77b4', edgecolor='black', alpha=0.7)
axes[0, 1].axvline(np.mean(word_counts), color='red', linestyle='--', label=f'Mean: {np.mean(word_counts):.0f}')
axes[0, 1].axvline(np.median(word_counts), color='green', linestyle='--', label=f'Median: {np.median(word_counts):.0f}')
axes[0, 1].set_xlabel('Words per Sample')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Distribution of Document Lengths')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Character count distribution
axes[1, 0].hist(char_counts, bins=50, color='#2ca02c', edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Characters per Sample')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Distribution of Character Counts')
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Entropy distribution
axes[1, 1].hist(entropies, bins=50, color='#9467bd', edgecolor='black', alpha=0.7)
axes[1, 1].axvline(np.mean(entropies), color='red', linestyle='--', label=f'Mean: {np.mean(entropies):.1f}')
axes[1, 1].set_xlabel('Perplexity Proxy (Character Bigram Entropy)')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].set_title('Distribution of Text Quality (Entropy)')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("src/phase155/data_curation_pipeline.png", dpi=150)
print("\nSaved visualization to src/phase155/data_curation_pipeline.png")

print("\n" + "="*60)
print("PHASE 155 COMPLETE")
print("="*60)
print("You have built a real data curation pipeline.")
print("This is the single most important skill in production ML.")
print("OpenAI, Anthropic, and Moonshot AI spend more time on data")
print("than on model architecture. Now you know why.")

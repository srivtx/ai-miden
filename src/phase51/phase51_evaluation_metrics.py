#!/usr/bin/env python3
"""
Phase 51: Evaluation Metrics — NumPy Concept Demo
===================================================
This script demonstrates how to evaluate models using metrics
beyond simple accuracy: precision, recall, F1, perplexity,
BLEU, and calibration error.

Key insight: Loss tells the model how to improve. Metrics tell
humans whether the model is useful. Different metrics reveal
different failure modes.

Concepts demonstrated:
  - Accuracy, precision, recall, F1
  - Perplexity for language models
  - BLEU for text generation
  - Expected Calibration Error (ECE)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(51)

# =============================================================================
# SECTION 1: CLASSIFICATION METRICS
# =============================================================================

print("="*60)
print("Phase 51: Evaluation Metrics")
print("="*60)

# Synthetic predictions
y_true = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 0])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 0, 0])

# Confusion matrix
tp = np.sum((y_true == 1) & (y_pred == 1))
fp = np.sum((y_true == 0) & (y_pred == 1))
tn = np.sum((y_true == 0) & (y_pred == 0))
fn = np.sum((y_true == 1) & (y_pred == 0))

accuracy = (tp + tn) / len(y_true)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print("\n--- Classification Metrics ---")
print(f"TP={tp}, FP={fp}, TN={tn}, FN={fn}")
print(f"Accuracy:  {accuracy:.1%}")
print(f"Precision: {precision:.1%}")
print(f"Recall:    {recall:.1%}")
print(f"F1 Score:  {f1:.1%}")

# =============================================================================
# SECTION 2: PERPLEXITY
# =============================================================================

print("\n--- Perplexity ---")
# Model probabilities for a sequence
probs = np.array([0.05, 0.02, 0.03, 0.08, 0.10])
ce = -np.mean(np.log(probs + 1e-10))
perplexity = np.exp(ce)
print(f"Cross-entropy: {ce:.3f}")
print(f"Perplexity:    {perplexity:.1f}")
print(f"(Model is as uncertain as choosing from {perplexity:.0f} options)")

# =============================================================================
# SECTION 3: BLEU SCORE (simplified)
# =============================================================================

print("\n--- BLEU Score ---")

def ngram_precision(generated, reference, n):
    gen_ngrams = [tuple(generated[i:i+n]) for i in range(len(generated)-n+1)]
    ref_ngrams = [tuple(reference[i:i+n]) for i in range(len(reference)-n+1)]
    if len(gen_ngrams) == 0:
        return 0
    matches = sum(1 for g in gen_ngrams if g in ref_ngrams)
    return matches / len(gen_ngrams)

generated = ["the", "quick", "brown", "fox"]
reference = ["the", "fast", "brown", "fox", "jumped"]

p1 = ngram_precision(generated, reference, 1)
p2 = ngram_precision(generated, reference, 2)
bleu = np.exp(0.5 * (np.log(p1 + 1e-10) + np.log(p2 + 1e-10)))

print(f"1-gram precision: {p1:.3f}")
print(f"2-gram precision: {p2:.3f}")
print(f"Simplified BLEU:  {bleu:.3f}")

# =============================================================================
# SECTION 4: CALIBRATION (ECE)
# =============================================================================

print("\n--- Calibration (ECE) ---")
# Confidences and outcomes
confidences = np.array([0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50])
correct = np.array([1, 1, 0, 1, 0, 1, 0, 0, 1, 0])

# Bin into 3 bins
bins = [(0.5, 0.7), (0.7, 0.9), (0.9, 1.0)]
ece = 0
gaps = []

for low, high in bins:
    mask = (confidences >= low) & (confidences < high)
    if mask.sum() == 0:
        gaps.append(0)
        continue
    acc = correct[mask].mean()
    conf = confidences[mask].mean()
    gap = abs(conf - acc)
    weight = mask.sum() / len(confidences)
    ece += weight * gap
    gaps.append(gap)
    print(f"Bin {low:.1f}-{high:.1f}: conf={conf:.2f}, acc={acc:.2f}, gap={gap:.2f}")

print(f"Expected Calibration Error: {ece:.1%}")

# =============================================================================
# SECTION 5: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Confusion matrix
ax = axes[0]
cm = np.array([[tn, fp], [fn, tp]])
im = ax.imshow(cm, cmap='Blues')
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(['Pred 0', 'Pred 1'])
ax.set_yticklabels(['True 0', 'True 1'])
ax.set_title('Confusion Matrix')
for i in range(2):
    for j in range(2):
        ax.text(j, i, cm[i, j], ha='center', va='center', fontsize=14)

# Plot 2: Metrics bar chart
ax = axes[1]
metrics = ['Accuracy', 'Precision', 'Recall', 'F1']
values = [accuracy, precision, recall, f1]
colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
bars = ax.bar(metrics, values, color=colors)
ax.set_ylim(0, 1.0)
ax.set_ylabel('Score')
ax.set_title('Classification Metrics')
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{val:.1%}', ha='center', va='bottom')
ax.grid(True, alpha=0.3)

# Plot 3: Calibration plot
ax = axes[2]
bin_centers = [0.6, 0.8, 0.95]
bin_accs = []
for low, high in bins:
    mask = (confidences >= low) & (confidences < high)
    bin_accs.append(correct[mask].mean() if mask.sum() > 0 else 0)

ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
ax.plot(bin_centers, bin_accs, 'ro-', markersize=10, label='Model')
ax.set_xlabel('Confidence')
ax.set_ylabel('Accuracy')
ax.set_title(f'Calibration Plot (ECE={ece:.1%})')
ax.set_xlim(0.4, 1.0)
ax.set_ylim(0.4, 1.0)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase51', exist_ok=True)
plt.savefig('src/phase51/evaluation_metrics.png', dpi=150)
print("\nSaved plot to src/phase51/evaluation_metrics.png")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Different metrics reveal different truths:")
print(f"  - Accuracy:  {accuracy:.1%} (can be misleading)")
print(f"  - Precision: {precision:.1%} (quality of positives)")
print(f"  - Recall:    {recall:.1%} (coverage of positives)")
print(f"  - Perplexity: {perplexity:.1f} (language model uncertainty)")
print(f"  - BLEU:      {bleu:.3f} (translation overlap)")
print(f"  - ECE:       {ece:.1%} (calibration error)")
print("\nNo single metric tells the whole story.")
print("Good evaluation uses multiple metrics together.")

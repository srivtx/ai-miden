#!/usr/bin/env python3
"""
Phase 150: AI Safety in Production Concepts — NumPy Simulation
================================================================
This script demonstrates four core ideas of production AI safety:

  1. Layered defense: multiple safety layers catch more attacks than any
     single layer, and provide redundancy when one layer fails.
  2. Input filtering: cheap heuristics (regex, keywords) block most
     attacks before generation, saving compute and risk.
  3. Output classification: post-hoc scoring catches harmful outputs that
     slip through input filters, especially from adversarial prompts.
  4. Safety monitoring: time-series tracking detects guardrail degradation
     and distribution drift in production.

We simulate a pipeline with:
  - 50 benign prompts
  - 50 adversarial prompts (some weak, some strong)
  - Three guardrail layers: PII regex, keyword blocklist, output scorer
  - A time-series monitoring dashboard that catches a deployed bug
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(150)

# =============================================================================
# SECTION 1: SIMULATE PROMPTS AND ATTACKS
# =============================================================================
# WHY separate benign and adversarial? To measure true positive rate
# (catching harmful) and false positive rate (blocking benign) we need
# labeled ground truth.

N_BENIGN = 50
N_ADV = 50
N_TOTAL = N_BENIGN + N_ADV

# Each prompt is represented by a feature vector in a 10-dimensional space.
# Benign prompts cluster around [0.2, 0.1, ...].
# Adversarial prompts have higher values in "suspicious" dimensions.
DIM = 10

benign_features = np.random.rand(N_BENIGN, DIM) * 0.4 + 0.1
# Adversarial prompts: higher values in dimensions 0, 3, 7 (simulate
# PII-like patterns, toxic keywords, and jailbreak structures).
adv_features = np.random.rand(N_ADV, DIM) * 0.5 + 0.3
adv_features[:, 0] += 0.3   # PII signal
adv_features[:, 3] += 0.2   # Toxicity signal
adv_features[:, 7] += 0.4   # Jailbreak signal

all_features = np.vstack([benign_features, adv_features])
labels = np.array([0] * N_BENIGN + [1] * N_ADV)  # 0=benign, 1=adversarial

# =============================================================================
# SECTION 2: SINGLE-LAYER DEFENSE (WEAK)
# =============================================================================
# WHY start with a single layer? It establishes the baseline and shows
# why layered defense is necessary. A keyword-only filter misses attacks
# that rephrase or obfuscate.

def single_layer_filter(features):
    """
    Only checks dimension 3 (toxic keyword signal).
    Threshold tuned to catch 70% of adversarial while allowing 10% false pos.
    """
    scores = features[:, 3]
    threshold = 0.65
    blocked = scores > threshold
    return blocked

single_blocked = single_layer_filter(all_features)
single_tp = np.mean(single_blocked[N_BENIGN:])  # caught adversarial
single_fp = np.mean(single_blocked[:N_BENIGN])  # blocked benign
single_tn = 1 - single_fp
single_fn = 1 - single_tp

print("="*70)
print("PHASE 150: AI SAFETY IN PRODUCTION CONCEPTS")
print("="*70)
print("\n--- Single-Layer Defense (Keyword Only) ---")
print(f"True Positive Rate  (caught harmful):  {single_tp:.2%}")
print(f"False Positive Rate (blocked benign):  {single_fp:.2%}")
print(f"Accuracy:                              {np.mean(single_blocked == labels):.2%}")

# =============================================================================
# SECTION 3: LAYERED DEFENSE (STRONG)
# =============================================================================
# WHY three layers? Each layer uses a different signal, making it harder
# for an attacker to evade all three simultaneously. Layer 1 is cheap
# (regex). Layer 2 is medium (keyword blocklist). Layer 3 is expensive
# but thorough (output scoring). We only run layer 3 if layer 1 and 2
# allow the prompt through.

def layer1_pii_filter(features):
    """Regex-like PII detection on dimension 0."""
    return features[:, 0] > 0.75

def layer2_keyword_filter(features):
    """Keyword blocklist on dimension 3."""
    return features[:, 3] > 0.60

def layer3_output_scorer(features):
    """
    Neural classifier simulation on dimensions 7 (jailbreak) and 5, 9.
    More nuanced but computationally expensive.
    """
    scores = (features[:, 7] * 0.5 +
              features[:, 5] * 0.25 +
              features[:, 9] * 0.25)
    return scores > 0.55

def layered_filter(features):
    """
    Defense in depth:
      - Block if ANY layer fires (conservative).
      - In production, layer 3 might only run if layers 1-2 are ambiguous.
    """
    l1 = layer1_pii_filter(features)
    l2 = layer2_keyword_filter(features)
    l3 = layer3_output_scorer(features)
    blocked = l1 | l2 | l3
    return blocked, l1, l2, l3

layered_blocked, l1, l2, l3 = layered_filter(all_features)
layered_tp = np.mean(layered_blocked[N_BENIGN:])
layered_fp = np.mean(layered_blocked[:N_BENIGN])

print("\n--- Layered Defense (PII + Keywords + Output Scorer) ---")
print(f"True Positive Rate  (caught harmful):  {layered_tp:.2%}")
print(f"False Positive Rate (blocked benign):  {layered_fp:.2%}")
print(f"Accuracy:                              {np.mean(layered_blocked == labels):.2%}")

# Per-layer contribution.
print(f"\nPer-layer contribution (adversarial catch rate):")
print(f"  Layer 1 (PII):        {np.mean(l1[N_BENIGN:]):.2%}")
print(f"  Layer 2 (Keywords):   {np.mean(l2[N_BENIGN:]):.2%}")
print(f"  Layer 3 (Output):     {np.mean(l3[N_BENIGN:]):.2%}")
print(f"  Union (any layer):    {layered_tp:.2%}")

# =============================================================================
# SECTION 4: ADVERSARIAL ATTACK SIMULATION
# =============================================================================
# WHY simulate attacks? To show that attackers adapt. A static filter
# that works today may fail tomorrow if attackers learn its threshold.
# We simulate attackers who reduce their suspicious signals to just
# below the filter threshold.

# Attack strategy: reduce dimension 3 (keyword) to 0.58, increase
# dimension 7 (jailbreak) to 0.60. This evades layer 2 but may still
# trigger layer 3.
adv_evasion = adv_features.copy()
adv_evasion[:, 3] = 0.58   # just below layer 2 threshold
adv_evasion[:, 7] = 0.65   # increase jailbreak signal

# Single layer fails.
single_evasion_blocked = single_layer_filter(adv_evasion)
single_evasion_tp = np.mean(single_evasion_blocked)

# Layered defense still catches via layer 3.
layered_evasion_blocked, _, _, _ = layered_filter(adv_evasion)
layered_evasion_tp = np.mean(layered_evasion_blocked)

print("\n--- Adversarial Evasion Attack ---")
print(f"Single-layer catch rate after evasion:  {single_evasion_tp:.2%}")
print(f"Layered catch rate after evasion:       {layered_evasion_tp:.2%}")
print(f"Layers provide:                         {layered_evasion_tp - single_evasion_tp:.2%} improvement")

# =============================================================================
# SECTION 5: SAFETY MONITORING — TIME SERIES
# =============================================================================
# WHY simulate a time series? Safety is not a point-in-time check. We
# simulate 60 days of production metrics, then inject a bug on day 45
# that silently disables layer 2. Monitoring should detect the drop.

DAYS = 60
np.random.seed(150)

# Baseline daily metrics.
daily_total = np.random.poisson(5000, DAYS)   # interactions per day
daily_adv_rate = 0.02                         # 2% adversarial

# Baseline block rate with all 3 layers.
baseline_block_rate = layered_tp * daily_adv_rate + layered_fp * (1 - daily_adv_rate)

# Generate daily block counts with noise.
block_rates = np.random.normal(baseline_block_rate, 0.002, DAYS)
block_rates = np.clip(block_rates, 0, 1)

# Inject bug on day 45: layer 2 silently disabled.
# Block rate drops because layer 2 catches ~30% of adversarial.
bug_start = 45
bug_layer2_contrib = np.mean(l2[N_BENIGN:]) * daily_adv_rate
block_rates[bug_start:] -= bug_layer2_contrib
block_rates[bug_start:] += np.random.normal(0, 0.001, DAYS - bug_start)
block_rates = np.clip(block_rates, 0, 1)

# Compute rolling average for smoothing.
window = 7
rolling = np.convolve(block_rates, np.ones(window)/window, mode='valid')

# Alert: detect when block rate drops below 2 standard deviations from mean.
mean_before = block_rates[:bug_start].mean()
std_before = block_rates[:bug_start].std()
alert_threshold = mean_before - 2 * std_before
alert_day = None
for d in range(bug_start, DAYS):
    if block_rates[d] < alert_threshold:
        alert_day = d
        break

print(f"\n--- Safety Monitoring Simulation ---")
print(f"Baseline block rate:      {mean_before:.3%}")
print(f"Alert threshold (2 std):  {alert_threshold:.3%}")
print(f"Bug injected on day:      {bug_start}")
print(f"Alert fired on day:       {alert_day if alert_day else 'NOT DETECTED'}")
if alert_day:
    print(f"Detection delay:          {alert_day - bug_start} days")

# =============================================================================
# SECTION 6: LATENCY-ACCURACY TRADE-OFF
# =============================================================================
# WHY this trade-off? Production systems have latency budgets. A safety
# pipeline that adds 500ms to every request may be unacceptable. We show
# the Pareto frontier of operating points.

# Simulate different classifier complexities (different thresholds on
# the output scorer, which we treat as proxy for model size / latency).
thresholds = np.linspace(0.30, 0.90, 30)
tpr_list = []
fpr_list = []
latency_list = []

for thresh in thresholds:
    scores = (all_features[:, 7] * 0.5 + all_features[:, 5] * 0.25 + all_features[:, 9] * 0.25)
    pred = scores > thresh
    tpr = np.mean(pred[N_BENIGN:])
    fpr = np.mean(pred[:N_BENIGN])
    # Simulate latency: lower threshold = more complex model = higher latency.
    # We invert the relationship for visualization: stricter threshold = cheaper.
    latency = 20 + 80 * (1 - (thresh - 0.3) / 0.6)  # ms, ranges 20-100ms
    tpr_list.append(tpr)
    fpr_list.append(fpr)
    latency_list.append(latency)

tpr_list = np.array(tpr_list)
fpr_list = np.array(fpr_list)
latency_list = np.array(latency_list)

# =============================================================================
# SECTION 7: VISUALIZATION
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Single vs. Layered defense (confusion matrix style).
ax = axes[0, 0]
categories = ['True Negatives\n(benign allowed)', 'False Positives\n(benign blocked)',
              'False Negatives\n(harmful allowed)', 'True Positives\n(harmful blocked)']
single_vals = [single_tn, single_fp, single_fn, single_tp]
layered_vals = [1-layered_fp, layered_fp, 1-layered_tp, layered_tp]
x = np.arange(len(categories))
width = 0.35
ax.bar(x - width/2, single_vals, width, label='Single Layer', color='#e74c3c', edgecolor='black')
ax.bar(x + width/2, layered_vals, width, label='Layered Defense', color='#27ae60', edgecolor='black')
ax.set_ylabel('Rate')
ax.set_title('Single Layer vs. Layered Defense')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=8)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, 1.05)

# Plot 2: Attack evasion.
ax = axes[0, 1]
scenarios = ['Before Attack', 'After Evasion']
single_rates = [single_tp, single_evasion_tp]
layered_rates = [layered_tp, layered_evasion_tp]
x = np.arange(len(scenarios))
ax.bar(x - width/2, single_rates, width, label='Single Layer', color='#e74c3c', edgecolor='black')
ax.bar(x + width/2, layered_rates, width, label='Layered Defense', color='#27ae60', edgecolor='black')
ax.set_ylabel('True Positive Rate')
ax.set_title('Adversarial Evasion: Layered Defense Holds')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, 1.05)

# Plot 3: Time-series monitoring.
ax = axes[1, 0]
days_axis = np.arange(DAYS)
ax.plot(days_axis, block_rates, 'o-', color='#2980b9', alpha=0.6, label='Daily block rate')
ax.plot(np.arange(window-1, DAYS), rolling, '-', color='#e74c3c', linewidth=2,
        label=f'{window}-day rolling avg')
ax.axvline(bug_start, color='orange', linestyle='--', label=f'Bug introduced (day {bug_start})')
if alert_day:
    ax.axvline(alert_day, color='green', linestyle='--', label=f'Alert fired (day {alert_day})')
ax.axhline(alert_threshold, color='red', linestyle=':', label=f'Alert threshold')
ax.set_xlabel('Day')
ax.set_ylabel('Block Rate')
ax.set_title('Safety Monitoring: Detecting Guardrail Degradation')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 4: Latency-Accuracy Pareto frontier.
ax = axes[1, 1]
scatter = ax.scatter(fpr_list, tpr_list, c=latency_list, cmap='viridis', s=80, edgecolors='black')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('Latency-Accuracy Trade-Off (color = latency ms)')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
# Add diagonal reference.
ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Random')
plt.colorbar(scatter, ax=ax, label='Latency (ms)')
ax.legend()

plt.tight_layout()
os.makedirs('src/phase150', exist_ok=True)
plt.savefig('src/phase150/safety_production_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved plot to src/phase150/safety_production_concepts.png")
plt.close()

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("Defense effectiveness:")
print(f"  Single-layer TPR:       {single_tp:.2%}")
print(f"  Layered TPR:            {layered_tp:.2%}")
print(f"  Single-layer FPR:       {single_fp:.2%}")
print(f"  Layered FPR:            {layered_fp:.2%}")
print(f"\nAdversarial evasion:")
print(f"  Single-layer after evasion: {single_evasion_tp:.2%}")
print(f"  Layered after evasion:      {layered_evasion_tp:.2%}")
print(f"\nMonitoring:")
print(f"  Bug introduced day:     {bug_start}")
print(f"  Alert fired day:        {alert_day if alert_day else 'N/A'}")
print(f"  Detection delay:        {alert_day - bug_start if alert_day else 'N/A'} days")
print("\nKey lessons:")
print("  1. Layered defense catches more attacks and is robust to evasion.")
print("  2. Input filtering (cheap layers) should catch as much as possible.")
print("  3. Output scoring (expensive layer) catches sophisticated bypasses.")
print("  4. Safety monitoring detects guardrail degradation in production.")
print("  5. There is a real latency-accuracy trade-off; the right point")
print("     depends on your product's risk tolerance and response budget.")
print("="*70)

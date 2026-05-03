"""
Phase 69: Red-Teaming & Safety Evaluation — NumPy Concept Demo

GOAL:
  Simulate a model with certain "harmful" behaviors, create a red-team probe
  set covering different harm categories, evaluate refusal rate per category,
  show how safety filters catch some but not all attacks, and plot a heatmap.

WHY NumPy?
  Before running expensive GPU inference on real models, we prototype the
  evaluation logic with deterministic random seeds. This makes the concept
  reproducible and testable without downloading multi-gigabyte weights.

STRUCTURE:
  1. Define a harm taxonomy (categories + base vulnerability scores).
  2. Simulate model behavior (refusal probability per category).
  3. Simulate safety filters (input + output layers with false-negative rates).
  4. Run red-team probes and compute success / refusal / catch rates.
  5. Plot a heatmap: harm category vs. success rate.
  6. Save plot to src/phase69/red_teaming.png
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # NON-INTERACTIVE backend; safe for headless CI / containers
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------
RNG_SEED = 42
N_PROBES_PER_CATEGORY = 200  # Number of red-team prompts per harm category

# Harm taxonomy: each category has a base "vulnerability" (0 = perfectly safe, 1 = always harmful)
# These are *simulated* model properties, not moral judgments.
HARM_CATEGORIES = {
    "Hate Speech":      0.35,
    "Self-Harm":        0.15,
    "Malware":          0.45,
    "Misinformation":   0.25,
    "Harassment":       0.30,
    "Illegal Acts":     0.20,
}

# Safety filters:
#   - INPUT_FILTER_CATCH: probability an input filter blocks a probe before generation
#   - OUTPUT_CLASSIFIER_CATCH: probability an output classifier blocks a harmful response
#   Filters are imperfect: they have false-negative rates (1 - catch).
INPUT_FILTER_CATCH = 0.60   # Catches 60% of probes at the door
OUTPUT_CLASSIFIER_CATCH = 0.70  # Catches 70% of harmful outputs after generation

# ---------------------------------------------------------------------------
# 2. SIMULATION ENGINE
# ---------------------------------------------------------------------------
rng = np.random.default_rng(RNG_SEED)

def simulate_red_team_probe(category: str, base_vulnerability: float, n: int) -> dict:
    """
    Simulate n red-team probes against a single harm category.

    Returns a dict with:
        total_probes, blocked_input, generated, harmful_generated,
        blocked_output, delivered_harmful, refused_by_model
    """
    # Step A: Input filter
    input_blocked = rng.random(n) < INPUT_FILTER_CATCH
    n_passed_input = int(np.sum(~input_blocked))

    # Step B: Model generation for prompts that passed input filter
    # The model "refuses" with probability (1 - base_vulnerability).
    # If it does NOT refuse, it produces a harmful response.
    model_refused = rng.random(n_passed_input) < (1 - base_vulnerability)
    n_harmful_generated = int(np.sum(~model_refused))

    # Step C: Output classifier
    output_blocked = rng.random(n_harmful_generated) < OUTPUT_CLASSIFIER_CATCH
    n_delivered_harmful = int(np.sum(~output_blocked))

    return {
        "total_probes": n,
        "blocked_input": int(np.sum(input_blocked)),
        "generated": n_passed_input,
        "harmful_generated": n_harmful_generated,
        "blocked_output": int(np.sum(output_blocked)),
        "delivered_harmful": n_delivered_harmful,
        "refused_by_model": int(np.sum(model_refused)),
    }

# ---------------------------------------------------------------------------
# 3. RUN EVALUATION
# ---------------------------------------------------------------------------
results = {}
for cat, vuln in HARM_CATEGORIES.items():
    results[cat] = simulate_red_team_probe(cat, vuln, N_PROBES_PER_CATEGORY)

# ---------------------------------------------------------------------------
# 4. METRICS TABLE
# ---------------------------------------------------------------------------
print("=" * 70)
print("RED-TEAMING SIMULATION RESULTS")
print("=" * 70)
print(f"{'Category':<18} {'Probes':>7} {'InBlocked':>9} {'Generated':>9} "
      f"{'Harmful':>8} {'OutBlock':>8} {'Delivered':>9} {'Refused':>8}")
print("-" * 70)

success_rates = []  # For heatmap: delivered harmful / total probes
for cat, r in results.items():
    print(f"{cat:<18} {r['total_probes']:>7} {r['blocked_input']:>9} "
          f"{r['generated']:>9} {r['harmful_generated']:>8} "
          f"{r['blocked_output']:>8} {r['delivered_harmful']:>9} {r['refused_by_model']:>8}")
    success_rates.append(r['delivered_harmful'] / r['total_probes'])

print("-" * 70)

# ---------------------------------------------------------------------------
# 5. SUMMARY STATISTICS
# ---------------------------------------------------------------------------
total_probes = sum(r['total_probes'] for r in results.values())
total_delivered_harmful = sum(r['delivered_harmful'] for r in results.values())
overall_success_rate = total_delivered_harmful / total_probes
overall_refusal_rate = 1.0 - overall_success_rate

print(f"\nOVERALL SUCCESS RATE (harmful output delivered): {overall_success_rate:.2%}")
print(f"OVERALL REFUSAL  RATE (safe or blocked):          {overall_refusal_rate:.2%}")

# ---------------------------------------------------------------------------
# 6. HEATMAP: Harm Category vs. Success Rate
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))

# Data: 1 row (success rate) x N categories
data_matrix = np.array(success_rates).reshape(1, -1)
im = ax.imshow(data_matrix, cmap='Reds', aspect='auto', vmin=0, vmax=0.5)

# Labels
ax.set_xticks(np.arange(len(HARM_CATEGORIES)))
ax.set_xticklabels(list(HARM_CATEGORIES.keys()), rotation=45, ha='right')
ax.set_yticks([0])
ax.set_yticklabels(['Success Rate'])

# Annotate cells with numeric values
for i, rate in enumerate(success_rates):
    ax.text(i, 0, f"{rate:.2%}", ha="center", va="center", color="black", fontsize=10)

ax.set_title("Red-Teaming Simulation: Harm Category vs. Attack Success Rate\n"
             "(Lower is better)", fontsize=12)
fig.colorbar(im, ax=ax, label='Delivered Harmful / Total Probes')

plt.tight_layout()
output_path = "/Users/zen/Desktop/building-ai/ai-miden/src/phase69/red_teaming.png"
plt.savefig(output_path, dpi=150)
plt.close(fig)

print(f"\nHeatmap saved to: {output_path}")

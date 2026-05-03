"""
Phase 79: Causal Inference — NumPy Concept Demo

This script demonstrates core causal inference concepts using only NumPy
and matplotlib (no external causal libraries). We:

1. Generate synthetic observational data with a hidden confounder.
2. Show that naive correlation is spurious (correlation != causation).
3. Simulate a randomized A/B test where the confounder is balanced.
4. Compute the Average Treatment Effect (ATE) under randomization.
5. Implement a simplified propensity score matching routine.
6. Visualize confounder structure, treatment distributions, and ATE convergence.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # MUST come before importing pyplot; non-interactive backend
import matplotlib.pyplot as plt

np.random.seed(79)

# =============================================================================
# 1. GENERATE SYNTHETIC DATA WITH A HIDDEN CONFOUNDER
# =============================================================================
# In the real world, treatment assignment is often driven by unobserved factors.
# Here, 'health' is a hidden confounder: it affects both whether a patient gets
# the drug and whether they recover. The drug itself has zero true effect.

n = 2000
health = np.random.normal(loc=0.0, scale=1.0, size=n)  # hidden confounder

# Observational treatment: doctors give the drug to healthier patients.
# logistic(health) -> probability of treatment
prob_treatment_obs = 1 / (1 + np.exp(-health))
treatment_obs = (np.random.rand(n) < prob_treatment_obs).astype(float)

# True causal effect of treatment is ZERO. Recovery is driven by health only.
recovery_obs = (health + np.random.normal(0, 0.3, size=n) > 0).astype(float)

# Also generate a continuous outcome for correlation visuals
outcome_obs = 2.0 * health + 0.0 * treatment_obs + np.random.normal(0, 0.5, size=n)

# =============================================================================
# 2. SHOW THAT CORRELATION != CAUSATION (SPURIOUS CORRELATION)
# =============================================================================
corr_naive = np.corrcoef(treatment_obs, outcome_obs)[0, 1]
print(f"Naive correlation (treatment vs outcome): {corr_naive:.3f}")
print("  -> This is NOT causal; health drives both variables.\n")

# =============================================================================
# 3. SIMULATE A RANDOMIZED A/B TEST (RANDOMIZED TREATMENT)
# =============================================================================
# In a proper experiment, treatment is assigned by a coin flip, breaking the
# link between health and treatment. The confounder is balanced across groups.

treatment_rand = (np.random.rand(n) < 0.5).astype(float)
outcome_rand = 2.0 * health + 0.0 * treatment_rand + np.random.normal(0, 0.5, size=n)

corr_rand = np.corrcoef(treatment_rand, outcome_rand)[0, 1]
print(f"Randomized correlation (treatment vs outcome): {corr_rand:.3f}")
print("  -> Randomization removes confounding; correlation here is near zero.\n")

# =============================================================================
# 4. COMPUTE AVERAGE TREATMENT EFFECT (ATE)
# =============================================================================
# Under randomization, ATE is simply the difference in mean outcomes between
# treated and control groups.

def compute_ate(treatment, outcome):
    treated = outcome[treatment == 1]
    control = outcome[treatment == 0]
    if len(treated) == 0 or len(control) == 0:
        return np.nan
    return treated.mean() - control.mean()

ate_randomized = compute_ate(treatment_rand, outcome_rand)
print(f"ATE from randomized experiment: {ate_randomized:.4f}")
print("  -> True effect is 0.0; any deviation is sampling noise.\n")

# =============================================================================
# 5. IMPLEMENT PROPSENSITY SCORE MATCHING (SIMPLIFIED)
# =============================================================================
# We only observe 'health' here, so we pretend it is our observed covariate.
# In practice you would use logistic regression on many features.
# We estimate P(T=1 | health) using a simple linear approximation (Z-score
# alignment), then match each treated unit to the nearest control by score.

# Simple propensity estimation via linear model on health
# P(T=1 | health) approximated by standardizing health and passing through sigmoid
propensity_obs = 1 / (1 + np.exp(-health))  # we use the true generating model here
# In real code you would fit logistic regression on covariates.

def propensity_match(treatment, outcome, propensity, caliper=0.05):
    """
    Simplified 1-to-1 nearest-neighbor matching on propensity score.
    Returns matched treated outcomes and matched control outcomes.
    """
    treated_idx = np.where(treatment == 1)[0]
    control_idx = np.where(treatment == 0)[0]

    matched_treated_outcomes = []
    matched_control_outcomes = []

    for ti in treated_idx:
        p_t = propensity[ti]
        # nearest control by absolute propensity difference
        diffs = np.abs(propensity[control_idx] - p_t)
        min_diff = diffs.min()
        if min_diff <= caliper:
            ci = control_idx[np.argmin(diffs)]
            matched_treated_outcomes.append(outcome[ti])
            matched_control_outcomes.append(outcome[ci])

    return np.array(matched_treated_outcomes), np.array(matched_control_outcomes)

matched_t, matched_c = propensity_match(treatment_obs, outcome_obs, propensity_obs, caliper=0.1)
ate_matched = matched_t.mean() - matched_c.mean() if len(matched_t) > 0 else np.nan
print(f"ATE after propensity score matching: {ate_matched:.4f}")
print(f"  -> Matched {len(matched_t)} pairs. True effect is 0.0.\n")

# =============================================================================
# 6. VISUALIZE
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# --- Panel A: Confounder structure (observational) ---
ax = axes[0, 0]
ax.scatter(health[treatment_obs == 0], outcome_obs[treatment_obs == 0], alpha=0.3, label='Control', s=20)
ax.scatter(health[treatment_obs == 1], outcome_obs[treatment_obs == 1], alpha=0.3, label='Treated', s=20)
ax.set_xlabel('Hidden Confounder (Health)')
ax.set_ylabel('Outcome')
ax.set_title(f'Observational Data: Correlation={corr_naive:.2f}\nHealth drives both treatment and outcome')
ax.legend()
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)

# --- Panel B: Randomized data ---
ax = axes[0, 1]
ax.scatter(health[treatment_rand == 0], outcome_rand[treatment_rand == 0], alpha=0.3, label='Control', s=20)
ax.scatter(health[treatment_rand == 1], outcome_rand[treatment_rand == 1], alpha=0.3, label='Treated', s=20)
ax.set_xlabel('Hidden Confounder (Health)')
ax.set_ylabel('Outcome')
ax.set_title(f'Randomized Data: Correlation={corr_rand:.2f}\nTreatment independent of health')
ax.legend()
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)

# --- Panel C: Treatment effect distributions ---
ax = axes[1, 0]
bins = np.linspace(outcome_obs.min(), outcome_obs.max(), 40)
ax.hist(outcome_obs[treatment_obs == 0], bins=bins, alpha=0.5, label='Obs Control')
ax.hist(outcome_obs[treatment_obs == 1], bins=bins, alpha=0.5, label='Obs Treated')
ax.hist(outcome_rand[treatment_rand == 0], bins=bins, alpha=0.5, label='Rand Control', histtype='step', linewidth=2)
ax.hist(outcome_rand[treatment_rand == 1], bins=bins, alpha=0.5, label='Rand Treated', histtype='step', linewidth=2)
ax.set_xlabel('Outcome')
ax.set_ylabel('Count')
ax.set_title('Outcome Distributions: Observational vs Randomized')
ax.legend(fontsize=8)

# --- Panel D: ATE convergence over sample size ---
ax = axes[1, 1]
sample_sizes = np.arange(50, n + 1, 50)
ates_random = []
ates_obs_naive = []
for s in sample_sizes:
    ates_random.append(compute_ate(treatment_rand[:s], outcome_rand[:s]))
    ates_obs_naive.append(compute_ate(treatment_obs[:s], outcome_obs[:s]))

ax.plot(sample_sizes, ates_random, label='Randomized ATE', linewidth=2)
ax.plot(sample_sizes, ates_obs_naive, label='Observational Naive ATE', linewidth=2)
ax.axhline(0.0, color='red', linestyle='--', label='True ATE = 0')
ax.set_xlabel('Sample Size')
ax.set_ylabel('Estimated ATE')
ax.set_title('ATE Convergence: Randomization Recovers Truth')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
out_path = '/Users/zen/Desktop/building-ai/ai-miden/src/phase79/causal_inference.png'
plt.savefig(out_path, dpi=150)
print(f"Plot saved to: {out_path}")

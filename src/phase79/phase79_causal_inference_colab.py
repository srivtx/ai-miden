"""
Phase 79: Causal Inference — Colab Real-Workflow Script

This script is designed to run in a Google Colab or similar Jupyter environment.
It demonstrates a complete causal inference workflow on observational data:

  1. Load / generate a realistic dataset with treatment and outcome.
  2. Compute a naive correlation / difference-in-means (WRONG but common).
  3. Estimate propensity scores with sklearn LogisticRegression.
  4. Apply propensity score matching to create balanced groups.
  5. Estimate causal effects using an econml / DoWhy-style approach.
  6. Compare naive vs. causal estimates.

Heavy comments explain WHY each step is necessary.
"""

import numpy as np
import pandas as pd
import warnings

# In Colab, you would typically run:
#   !pip install econml dowhy scikit-learn matplotlib
# We guard the import so the script degrades gracefully if libraries are absent.
try:
    from econml.dml import LinearDML
    from sklearn.linear_model import LogisticRegression, LinearRegression
    HAS_ECONML = True
except Exception:
    HAS_ECONML = False
    warnings.warn("econml not installed; falling back to manual propensity matching only.")

try:
    import dowhy
    from dowhy import CausalModel
    HAS_DOWHY = True
except Exception:
    HAS_DOWHY = False
    warnings.warn("dowhy not installed; skipping DoWhy integration.")

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# Matplotlib must use 'Agg' for non-interactive environments
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(79)

# =============================================================================
# 1. LOAD (OR GENERATE) A DATASET WITH TREATMENT AND OUTCOME
# =============================================================================
# WHY: Real observational data rarely comes from an experiment. We simulate a
#      scenario where 'income' and 'age' affect both whether someone receives
#      a job-training program (treatment) and their future earnings (outcome).
#      The TRUE treatment effect is +$2000.

n = 3000
age = np.random.normal(35, 10, size=n).clip(18, 65)
income = np.random.normal(50000, 15000, size=n).clip(15000, 150000)

# Confounded treatment: older, higher-income people are more likely to enroll
# (e.g., they have more awareness or flexible schedules).
logit_treat = -2.0 + 0.03 * (age - 35) / 10 + 0.00002 * (income - 50000)
prob_treat = 1 / (1 + np.exp(-logit_treat))
treatment = (np.random.rand(n) < prob_treat).astype(int)

# Outcome = baseline from age/income + TRUE_EFFECT * treatment + noise
TRUE_EFFECT = 2000.0
earnings = (
    20000
    + 300 * age
    + 0.8 * income
    + TRUE_EFFECT * treatment
    + np.random.normal(0, 5000, size=n)
)

df = pd.DataFrame({
    'age': age,
    'income': income,
    'treatment': treatment,
    'earnings': earnings
})

print("=" * 60)
print("DATA PREVIEW")
print("=" * 60)
print(df.head())
print(f"\nTreatment rate: {df['treatment'].mean():.2%}")
print(f"Mean earnings (treated):   ${df.loc[df['treatment']==1, 'earnings'].mean():,.0f}")
print(f"Mean earnings (control):   ${df.loc[df['treatment']==0, 'earnings'].mean():,.0f}")

# =============================================================================
# 2. COMPUTE NAIVE CORRELATION / DIFFERENCE-IN-MEANS
# =============================================================================
# WHY: This is what most dashboards show. It is fast, wrong, and dangerously
#      misleading when treatment assignment is confounded. We calculate it here
#      so we can contrast it with the causal estimate later.

naive_ate = df.loc[df['treatment'] == 1, 'earnings'].mean() - df.loc[df['treatment'] == 0, 'earnings'].mean()
naive_corr = np.corrcoef(df['treatment'], df['earnings'])[0, 1]

print("\n" + "=" * 60)
print("NAIVE ESTIMATES (WRONG — confounded)")
print("=" * 60)
print(f"Naive difference-in-means (ATE): ${naive_ate:,.0f}")
print(f"Naive Pearson correlation:         {naive_corr:.3f}")
print("  -> These numbers mix the true effect with selection bias.")

# =============================================================================
# 3. ESTIMATE PROPENSITY SCORES WITH SKLEARN
# =============================================================================
# WHY: Before matching, we need each person's probability of treatment given
#      observed covariates. Logistic regression turns age/income into a score
#      between 0 and 1. We then check overlap: if treated and control units have
#      wildly different score distributions, matching is unreliable.

X = df[['age', 'income']].values
y_treat = df['treatment'].values

# Standardize features so regularization treats age and income fairly
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

prop_model = LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
prop_model.fit(X_scaled, y_treat)
propensity = prop_model.predict_proba(X_scaled)[:, 1]
df['propensity_score'] = propensity

print("\n" + "=" * 60)
print("PROPENSITY SCORE SUMMARY")
print("=" * 60)
print(f"Treated mean propensity:   {df.loc[df['treatment']==1, 'propensity_score'].mean():.3f}")
print(f"Control mean propensity:   {df.loc[df['treatment']==0, 'propensity_score'].mean():.3f}")
print("  -> If these means are far apart, overlap is poor.")

# =============================================================================
# 4. APPLY PROPENSITY SCORE MATCHING
# =============================================================================
# WHY: Matching tries to recreate a randomized experiment retrospectively.
#      Each treated unit is paired with the most similar control unit based on
#      propensity score. After matching, the two groups should look alike in
#      age and income, isolating the treatment effect.

treated_df = df[df['treatment'] == 1].copy()
control_df = df[df['treatment'] == 0].copy()

# Use sklearn NearestNeighbors to find closest control for each treated unit
# We match on the scalar propensity score (reshaped to 2D as required).
nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(
    control_df['propensity_score'].values.reshape(-1, 1)
)
distances, indices = nbrs.kneighbors(treated_df['propensity_score'].values.reshape(-1, 1))

# Optional: impose a caliper so we don't match wildly different units
CALIPER = 0.2
valid_match = distances.flatten() <= CALIPER
matched_treated = treated_df[valid_match].copy()
matched_control_indices = indices.flatten()[valid_match]
matched_control = control_df.iloc[matched_control_indices].copy()

matched_ate = matched_treated['earnings'].mean() - matched_control['earnings'].mean()

print("\n" + "=" * 60)
print("MATCHING RESULTS")
print("=" * 60)
print(f"Matched pairs: {len(matched_treated)}")
print(f"Matched ATE:   ${matched_ate:,.0f}")
print("  -> This is closer to causal, but still vulnerable to UNOBSERVED confounders.")

# =============================================================================
# 5. ESTIMATE CAUSAL EFFECT WITH ECONML / DOWHY
# =============================================================================
# WHY: Modern causal ML combines machine learning with causal identification.
#      Double Machine Learning (DML) uses ML to flexibly model outcome and
#      treatment as functions of covariates, then isolates the treatment
#      coefficient. This is more robust than simple matching when many
#      covariates interact nonlinearly.

print("\n" + "=" * 60)
print("CAUSAL ML ESTIMATES")
print("=" * 60)

causal_estimates = {}

if HAS_ECONML:
    # LinearDML: fits Y ~ treatment + covariates and T ~ covariates using ML,
    # then regresses the residualized Y on residualized T.
    est = LinearDML(
        model_y=LinearRegression(),
        model_t=LogisticRegression(max_iter=1000),
        discrete_treatment=True,
        random_state=79
    )
    est.fit(df['earnings'].values, df['treatment'].values, X=X_scaled)
    econml_effect = est.effect(X_scaled).mean()
    causal_estimates['EconML LinearDML'] = econml_effect
    print(f"EconML LinearDML ATE: ${econml_effect:,.0f}")
else:
    print("EconML not available; install with: pip install econml")

if HAS_DOWHY:
    # DoWhy explicitly models the causal graph and refutes assumptions.
    # Here we specify a simple backdoor graph: age, income -> treatment, earnings
    model = CausalModel(
        data=df,
        treatment='treatment',
        outcome='earnings',
        common_causes=['age', 'income']
    )
    identified_estimand = model.identify_effect()
    # Use propensity score stratification for estimation
    estimate = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.propensity_score_stratification"
    )
    causal_estimates['DoWhy PSS'] = estimate.value
    print(f"DoWhy Stratification ATE: ${estimate.value:,.0f}")
else:
    print("DoWhy not available; install with: pip install dowhy")

# =============================================================================
# 6. COMPARE NAIVE VS. CAUSAL ESTIMATES
# =============================================================================
# WHY: If naive and causal estimates diverge, confounding is large. If they
#      agree, either confounding is weak or you got lucky. ALWAYS check both.

print("\n" + "=" * 60)
print("COMPARISON TABLE")
print("=" * 60)
print(f"{'Method':<35} {'ATE ($)':>12}")
print("-" * 60)
print(f"{'Naive difference-in-means':<35} {naive_ate:>12,.0f}")
print(f"{'Propensity matched':<35} {matched_ate:>12,.0f}")
for method, val in causal_estimates.items():
    print(f"{method:<35} {val:>12,.0f}")
print(f"{'TRUE EFFECT (simulated)':<35} {TRUE_EFFECT:>12,.0f}")

# =============================================================================
# 7. VISUALIZE
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Propensity overlap
ax = axes[0]
ax.hist(df.loc[df['treatment'] == 0, 'propensity_score'], bins=30, alpha=0.6, label='Control')
ax.hist(df.loc[df['treatment'] == 1, 'propensity_score'], bins=30, alpha=0.6, label='Treated')
ax.set_xlabel('Propensity Score')
ax.set_ylabel('Count')
ax.set_title('Propensity Score Overlap')
ax.legend()

# Covariate balance before / after matching
ax = axes[1]
metrics = ['Naive ATE', 'Matched ATE'] + list(causal_estimates.keys())
values = [naive_ate, matched_ate] + list(causal_estimates.values())
colors = ['tomato', 'orange'] + ['seagreen'] * len(causal_estimates)
bars = ax.barh(metrics, values, color=colors)
ax.axvline(TRUE_EFFECT, color='red', linestyle='--', label='True Effect')
ax.set_xlabel('Estimated ATE ($)')
ax.set_title('Naive vs Causal Estimates')
ax.legend()
# Add value labels
for bar, val in zip(bars, values):
    ax.text(val + 100, bar.get_y() + bar.get_height()/2, f"${val:,.0f}", va='center', fontsize=8)

# Age vs Earnings colored by treatment
ax = axes[2]
ax.scatter(df.loc[df['treatment']==0, 'age'], df.loc[df['treatment']==0, 'earnings'], alpha=0.3, s=10, label='Control')
ax.scatter(df.loc[df['treatment']==1, 'age'], df.loc[df['treatment']==1, 'earnings'], alpha=0.3, s=10, label='Treated')
ax.set_xlabel('Age')
ax.set_ylabel('Earnings ($)')
ax.set_title('Raw Data: Earnings vs Age')
ax.legend()

plt.tight_layout()
plot_path = '/Users/zen/Desktop/building-ai/ai-miden/src/phase79/causal_inference_colab.png'
plt.savefig(plot_path, dpi=150)
print(f"\nColab plot saved to: {plot_path}")

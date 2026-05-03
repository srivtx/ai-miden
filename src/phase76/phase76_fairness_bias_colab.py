"""
Phase 76: Fairness & Bias — Colab Real-Workflow Script

GOAL:
  Load the UCI Adult Census dataset, train a standard logistic regression
  classifier, compute fairness metrics with fairlearn, then enforce a
  demographic parity constraint using fairlearn's ExponentiatedGradient.
  Compare the unconstrained and constrained models side by side.

WHY this script:
  The NumPy demo shows the *concept* with toy data. This script shows the
  *real workflow* with a real tabular dataset, real fairness definitions,
  and an audited constraint optimizer. You should run this in Google Colab
  on a T4 GPU (though CPU is fine for Adult + logistic regression).

STRUCTURE:
  1. Download Adult Census data via sklearn.
  2. Pre-process: one-hot encode categoricals, standardize numerics.
  3. Split train/test.
  4. Train unconstrained logistic regression.
  5. Compute accuracy, demographic parity difference, equalized odds difference.
  6. Train constrained model with fairlearn DemographicParity constraint.
  7. Compute the same metrics on the constrained model.
  8. Print a before/after comparison table.

DEPENDENCIES (install in Colab):
  !pip install fairlearn scikit-learn pandas
"""

# ---------------------------------------------------------------------------
# 1. IMPORTS
# ---------------------------------------------------------------------------
# WHY: We use sklearn for the ML pipeline, fairlearn for fairness-specific
# metrics and reductions, and pandas for data manipulation.

import numpy as np
import pandas as pd

from sklearn.datasets import fetch_openml
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
from fairlearn.reductions import ExponentiatedGradient, DemographicParity

# ---------------------------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------------------------
# WHY: The Adult Census dataset is the canonical fairness benchmark.
# It predicts whether income exceeds $50K/yr. The sensitive attribute is
# sex. Base rates differ by sex in this dataset, making fairness non-trivial.

print("Downloading Adult Census dataset...")
X, y = fetch_openml(data_id=1590, as_frame=True, return_X_y=True)

# Convert target to binary integer
y = (y == '>50K').astype(int)

# The sensitive feature we will audit: sex
# Values are typically 'Male' and 'Female'
sensitive_feature = X['sex'].copy()

# Drop the sensitive feature from the model inputs.
# WHY: We want to see if the model infers the protected attribute from
# proxy variables (like occupation or relationship status) even when sex
# is not explicitly provided. This is the "fairness through unawareness"
# trap.
X = X.drop(columns=['sex'])

# One-hot encode categorical columns. Adult has mixed types.
X = pd.get_dummies(X, drop_first=True)

print(f"Dataset shape: {X.shape}")
print(f"Positive rate: {y.mean():.3f}")
print(f"Sensitive feature distribution:\n{sensitive_feature.value_counts()}")

# ---------------------------------------------------------------------------
# 3. TRAIN / TEST SPLIT
# ---------------------------------------------------------------------------
# WHY: Stratify on y so both train and test have the same class balance.
# We also stratify on the sensitive feature implicitly by using a combined
# stratification key, but for simplicity we stratify on y alone here.

X_train, X_test, y_train, y_test, s_train, s_test = train_test_split(
    X, y, sensitive_feature,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# ---------------------------------------------------------------------------
# 4. FEATURE SCALING
# ---------------------------------------------------------------------------
# WHY: Logistic regression converges faster and is more numerically stable
# when features are on the same scale. We fit the scaler ONLY on training
# data to prevent data leakage.

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------------------------
# 5. UNCONSTRAINED BASELINE MODEL
# ---------------------------------------------------------------------------
# WHY: You cannot evaluate a fairness intervention without a baseline.
# The baseline tells you how much accuracy you are trading for fairness.
# If you do not measure the baseline, you are flying blind.

print("\n--- UNCONSTRAINED MODEL ---")
estimator = LogisticRegression(max_iter=1000, solver='lbfgs')
estimator.fit(X_train_scaled, y_train)

y_pred_unconstrained = estimator.predict(X_test_scaled)

acc_unconstrained = accuracy_score(y_test, y_pred_unconstrained)
dp_unconstrained = demographic_parity_difference(
    y_test, y_pred_unconstrained, sensitive_features=s_test
)
eo_unconstrained = equalized_odds_difference(
    y_test, y_pred_unconstrained, sensitive_features=s_test
)

print(f"Accuracy              : {acc_unconstrained:.3f}")
print(f"Demographic Parity Diff: {dp_unconstrained:.3f}")
print(f"Equalized Odds Diff    : {eo_unconstrained:.3f}")

# ---------------------------------------------------------------------------
# 6. FAIRNESS-CONSTRAINED MODEL
# ---------------------------------------------------------------------------
# WHY: Demographic parity says "the selection rate must be equal across
# groups." We do not know how to manually tweak a logistic regression to
# guarantee this. fairlearn's ExponentiatedGradient solves a constrained
# optimization: it trains many weighted copies of the base estimator and
# combines them into a mixture that satisfies the constraint while
# minimizing error.
#
# This is an in-processing technique because the training objective itself
# is changed to respect the fairness constraint.

print("\n--- CONSTRAINED MODEL (Demographic Parity) ---")
constraint = DemographicParity()
mitigator = ExponentiatedGradient(estimator, constraint)

# WHY sensitive_features in fit: the algorithm needs to know group
# membership so it can measure and enforce the constraint.
mitigator.fit(X_train_scaled, y_train, sensitive_features=s_train)

y_pred_constrained = mitigator.predict(X_test_scaled)

acc_constrained = accuracy_score(y_test, y_pred_constrained)
dp_constrained = demographic_parity_difference(
    y_test, y_pred_constrained, sensitive_features=s_test
)
eo_constrained = equalized_odds_difference(
    y_test, y_pred_constrained, sensitive_features=s_test
)

print(f"Accuracy              : {acc_constrained:.3f}")
print(f"Demographic Parity Diff: {dp_constrained:.3f}")
print(f"Equalized Odds Diff    : {eo_constrained:.3f}")

# ---------------------------------------------------------------------------
# 7. COMPARISON TABLE
# ---------------------------------------------------------------------------
# WHY: Numbers in isolation are meaningless. A side-by-side table makes
# the trade-off explicit: how much accuracy did we sacrifice, and how much
# fairness did we gain?

print("\n" + "=" * 55)
print("COMPARISON: UNCONSTRAINED vs. CONSTRAINED")
print("=" * 55)
print(f"{'Metric':<30} {'Before':>10} {'After':>10}")
print("-" * 55)
print(f"{'Accuracy':<30} {acc_unconstrained:>10.3f} {acc_constrained:>10.3f}")
print(f"{'Demographic Parity Diff':<30} {dp_unconstrained:>10.3f} {dp_constrained:>10.3f}")
print(f"{'Equalized Odds Diff':<30} {eo_unconstrained:>10.3f} {eo_constrained:>10.3f}")
print("-" * 55)
print(f"{'Accuracy change':<30} {'':>10} {acc_constrained - acc_unconstrained:>+10.3f}")
print(f"{'DP improvement':<30} {'':>10} {dp_unconstrained - dp_constrained:>+10.3f}")
print(f"{'EO improvement':<30} {'':>10} {eo_unconstrained - eo_constrained:>+10.3f}")
print("=" * 55)

# ---------------------------------------------------------------------------
# 8. INTERPRETATION NOTES
# ---------------------------------------------------------------------------
# WHY: Code without interpretation is dangerous in fairness work. We must
# explicitly state what the numbers mean and what they do NOT mean.

print("\n--- INTERPRETATION ---")
print("""
1. Demographic Parity Difference = 0 means the model approves the same
   fraction of each group. A reduction in this number is good IF your
   ethical framework demands parity.

2. Equalized Odds Difference = 0 means true-positive and false-positive
   rates are identical across groups. This is a different fairness notion.
   Demographic parity and equalized odds are usually incompatible when
   base rates differ.

3. Accuracy may drop slightly after enforcing a constraint. This is the
   "fairness-accuracy trade-off." It is not a bug; it is a mathematical
   necessity when the unconstrained model was exploiting a spurious or
   historically biased correlation.

4. ALWAYS report which fairness definition you chose and why. Never claim
   "the model is fair" without specifying which metric you used.
""")

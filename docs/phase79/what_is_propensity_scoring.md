# What Is Propensity Scoring?

## 1. Why It Exists (THE PROBLEM)

In observational data, treated and untreated groups are rarely alike. Patients who take an expensive drug tend to be wealthier, older, or sicker. Comparing their outcomes directly is like comparing apples to oranges. You need a way to make the two groups comparable without running a randomized experiment.

## 2. Definition

Propensity scoring is a method that estimates, for each unit, the probability of receiving treatment given observed covariates. Units with similar propensity scores are then matched or weighted, creating a pseudo-randomized comparison where treatment and control groups look alike on observed features.

## 3. Real-Life Analogy

Imagine a talent show where contestants self-select into a singing track or a dancing track. Singers might be more extroverted. To fairly compare which track produces happier alumni, you pair each singer with a dancer who had the *same probability* of choosing singing based on personality, age, and background. These matched pairs form a fairer comparison.

## 4. Tiny Numeric Example

Three patients with covariate Age:

| Patient | Age | Takes Drug | Outcome |
|---------|-----|------------|---------|
| 1       | 65  | Yes        | 1       |
| 2       | 30  | No         | 0       |
| 3       | 64  | No         | 0       |

Naive comparison: treated mean = 1.0, control mean = 0.0. ATE = 1.0.

Propensity model estimates P(drug | Age):
- Patient 1: 0.85
- Patient 2: 0.10
- Patient 3: 0.82

Patient 1 and 3 are matched (scores 0.85 and 0.82). Matched ATE = (1 - 0) / 1 = 1.0. In this tiny example the confounder (age) is strong, so even matching on propensity may not fully resolve it without more data—but the principle is to compare similar patients, not all patients.

## 5. Common Confusion

- **"Propensity matching fixes all confounding."** It only adjusts for *observed* confounders; unmeasured confounders still bias estimates.
- **"A good propensity model must predict treatment perfectly."** Extreme propensities (near 0 or 1) cause poor overlap and high variance; moderate discrimination is preferred.
- **"Matching is always better than weighting."** Matching discards unmatched units; weighting (inverse probability weighting) uses all data but can be unstable.
- **"Propensity scores replace the need for domain knowledge."** You must still choose the right covariates to include; omitting a confounder breaks the method.
- **"One-to-one matching is the only option."** You can match with replacement, use calipers, or use stratification on the score.
- **"Checking balance after matching is optional."** Always verify that covariate distributions are similar in matched groups; if not, the model failed.

## 6. Where It Is Used in Our Code

In `src/phase79/phase79_causal_inference.py`, we implement a simplified propensity score matching routine: we estimate propensity via logistic regression on observed covariates, match each treated unit to the nearest control by score, and recompute the ATE. In `src/phase79/phase79_causal_inference_colab.py`, we use `sklearn` logistic regression for propensity estimation and perform matching before comparing naive and adjusted estimates.

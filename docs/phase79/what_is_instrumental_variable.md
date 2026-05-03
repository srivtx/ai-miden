# What Is an Instrumental Variable?

## 1. Why It Exists (THE PROBLEM)

Sometimes, the treatment you care about is entangled with unobserved confounders you cannot measure. For example, education affects earnings, but innate ability affects both education and earnings—and you cannot directly measure "ability." Without an experiment, standard regression or matching fails because a key confounder is missing.

## 2. Definition

An instrumental variable (IV) is an external variable that affects the treatment but has no direct effect on the outcome except through the treatment. It acts like a natural randomizer, isolating the treatment variation that is "clean" of confounding.

## 3. Real-Life Analogy

Imagine a ferry service that only runs on windy days. Wind affects whether people visit an island (treatment), but wind does not directly affect their happiness on the island (outcome)—except by forcing them to go. By comparing visitors on windy vs. calm days, you isolate the causal effect of visiting the island, free from the confounder of "people who love islands anyway."

## 4. Tiny Numeric Example

Suppose we want the effect of tutoring (T) on test scores (Y), but motivation (U) is unobserved and affects both.

We use a scholarship lottery (Z) as an instrument:
- Z affects T (winners get free tutoring)
- Z does not affect Y except through T

| Student | Z (Won Lottery) | T (Tutoring) | Y (Score) |
|---------|-----------------|--------------|-----------|
| 1       | 1               | 1            | 85        |
| 2       | 0               | 0            | 70        |
| 3       | 1               | 1            | 90        |
| 4       | 0               | 0            | 65        |

First stage: T ~ Z. Coefficient = 1.0 (winning guarantees tutoring).
Reduced form: Y ~ Z. Coefficient = 20.0 (winners score 20 points higher).
IV estimate = Reduced form / First stage = 20 / 1 = 20.

The IV estimate says tutoring causally raises scores by 20 points, even though we never measured motivation.

## 5. Common Confusion

- **"Any variable correlated with treatment can be an instrument."** It must also be uncorrelated with unobserved confounders and affect outcome *only* through treatment (the exclusion restriction).
- **"If the instrument is weak, the estimate is just noisy."** Weak instruments produce biased estimates that are often worse than ordinary regression.
- **"IV estimates the effect for everyone."** Standard IV estimates the Local Average Treatment Effect (LATE)—the effect only for "compliers" who change behavior because of the instrument.
- **"You can test the exclusion restriction with data."** It is an untestable assumption; you must defend it with theory, not statistics.
- **"One instrument is enough for any endogeneity."** If treatment is endogenous in multiple ways, you need as many instruments as endogenous variables.
- **"IV replaces the need for randomization."** IV is a workaround for observational data, but a true experiment is still preferable when feasible.

## 6. Where It Is Used in Our Code

In `src/phase79/phase79_causal_inference_colab.py`, we demonstrate an instrumental variable approach conceptually: we introduce a synthetic lottery variable that randomly nudges treatment assignment, then show how this exogenous variation isolates a cleaner causal estimate compared to naive regression on endogenous treatment.

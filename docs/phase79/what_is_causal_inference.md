# What Is Causal Inference?

## 1. Why It Exists (THE PROBLEM)

Machine learning excels at prediction, but prediction is not understanding. You can predict ice-cream sales from sunglasses sales with near-perfect accuracy, yet telling the ice-cream vendor to "stock more sunglasses" is useless. The real question is: **"If I intervene and change X, what happens to Y?"** Without causal inference, models answer the wrong question—they describe associations, not the consequences of actions.

## 2. Definition

Causal inference is the process of determining whether a change in one variable **actually causes** a change in another, by accounting for confounders, selection bias, and the structure of how data is generated.

## 3. Real-Life Analogy

A city notices that neighborhoods with more fire trucks have more fire damage. Should they remove fire trucks to reduce fires? No. The hidden confounder is fire severity—bigger fires summon more trucks. Causal inference asks: *"If we magically sent an extra truck to a random neighborhood, would damage go down?"*

## 4. Tiny Numeric Example

Imagine a drug trial with a hidden health score confounder:

| Patient | Health Score | Takes Drug | Recovers |
|---------|-------------|------------|----------|
| A       | 9           | Yes        | 1        |
| B       | 2           | No         | 0        |
| C       | 8           | Yes        | 1        |
| D       | 3           | No         | 0        |

Naive correlation: Drug and recovery are perfectly correlated (r = 1.0). But health score drives both drug assignment (doctors give it to healthier patients) and recovery. The causal effect of the drug itself may be zero or even negative. Causal inference separates the drug's true effect from the confounder's influence.

## 5. Common Confusion

- **"High correlation means causation."** Correlation measures co-movement, not intervention. Two variables can correlate because a third causes both.
- **"A model with high R² on observational data proves causality."** Predictive power says nothing about what happens if you intervene.
- **"Controlling for everything fixes confounding."** You cannot control for unobserved confounders or colliders (variables caused by both treatment and outcome).
- **"Causal inference is just statistics with extra steps."** It requires structural assumptions (e.g., no unmeasured confounding) that pure statistics cannot test.
- **"Randomized experiments are the only way."** While gold-standard, causal inference also provides tools (instrumental variables, matching, do-calculus) for observational data.
- **"The average treatment effect applies to every individual."** ATE is a population average; some individuals may be harmed while others benefit (heterogeneous treatment effects).

## 6. Where It Is Used in Our Code

In `src/phase79/phase79_causal_inference.py`, we generate data with a hidden confounder, show that naive correlation is misleading, simulate a randomized A/B test to recover the true effect, and apply propensity score matching to observational data.

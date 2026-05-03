# What is Demographic Parity?

## 1. Why it exists (THE PROBLEM)

A city deploys a job-screening AI. It approves 70% of male applicants but only 30% of female applicants. Even if the women who were rejected were genuinely less qualified on paper, the stark gap raises a fairness concern: is the model using gender as a hidden signal? Demographic parity exists because **equal opportunity starts with equal prediction rates.** If a model sends positive outcomes to one group far more often, the process itself looks discriminatory, regardless of why.

## 2. Definition

**Demographic parity** requires that the probability of receiving a positive prediction is the same across all demographic groups.

> P( Y_hat = 1 | G = 0 ) = P( Y_hat = 1 | G = 1 )

The **demographic parity difference** is the absolute gap between these two rates. A difference of 0 means parity is satisfied.

## 3. Real-life analogy

A scholarship committee gives out 100 awards. Demographic parity says each high school in the district should send the same percentage of its students home with an award. It does not ask whether the students had identical grades; it asks whether the final outcome was balanced across schools.

## 4. Tiny numeric example

A model predicts loan approval for 100 men and 100 women.

| Group | Approved | Denied | Positive Rate |
|-------|----------|--------|---------------|
| Men   | 60       | 40     | 60%           |
| Women | 60       | 40     | 60%           |

Demographic parity difference = |60% - 60%| = **0%** (satisfied).

Now imagine the model approves only 30 women:

| Group | Approved | Denied | Positive Rate |
|-------|----------|--------|---------------|
| Men   | 60       | 40     | 60%           |
| Women | 30       | 70     | 30%           |

Demographic parity difference = |60% - 30%| = **30%** (violated).

## 5. Common confusion

- **"Demographic parity means the model is accurate."** No. A coin-flip classifier that approves exactly 50% of every group satisfies demographic parity but is useless.
- **"Demographic parity guarantees fairness."** No. It only checks one fairness criterion: equal positive rates. It says nothing about whether the right people were approved.
- **"It is always the right fairness definition."** No. If one group is genuinely more qualified, forcing equal approval rates means approving unqualified people and rejecting qualified ones.
- **"You can satisfy demographic parity and equalized odds at the same time."** Not when base rates differ. The two definitions are mathematically incompatible except in special cases.
- **"Removing the protected attribute from inputs guarantees demographic parity."** No. The model can still infer the attribute from correlated features and produce unequal rates.
- **"Demographic parity is required by law everywhere."** No. Different jurisdictions use different standards. Some legal frameworks prefer equalized odds or individual fairness instead.

## 6. Where it is used in our code

In `src/phase76/phase76_fairness_bias.py`, we compute the demographic parity difference before and after reweighting. Before mitigation, the biased classifier shows a large gap in approval rates between groups. After reweighting, the gap shrinks, showing that the training process can be adjusted to move toward parity. In `src/phase76/phase76_fairness_bias_colab.py`, we use fairlearn to enforce a demographic parity constraint explicitly and compare the constrained model's rates against the unconstrained baseline.

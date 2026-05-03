# What is Preference Data?

## 1. Why it exists (THE PROBLEM first)

How do you teach a model what "good" means? You cannot write a Python function
for "helpful and harmless" because human values are fuzzy and
context-dependent. Absolute scores are unreliable — one rater's 7/10 is another
rater's 5/10. But humans are remarkably consistent at saying "A is better than
B." Preference data turns vague goodness into concrete pairwise comparisons.

## 2. Definition (very simple)

Preference data is a collection of triplets (prompt, chosen, rejected) where a
human labeler decided that the chosen response is better than the rejected
response for the given prompt. It is the fuel that powers DPO, ORPO, and RLHF.

## 3. Real-life analogy

Imagine a wine tasting. Asking someone to rate a wine from 1 to 10 produces
noisy, inconsistent scores. But asking "Do you prefer Wine A or Wine B?" yields
reliable, repeatable answers. Preference data is the wine tasting of AI
alignment.

## 4. Tiny numeric example

Consider the Bradley-Terry model, which turns preference counts into win
probabilities. If model A beats model B in 7 out of 10 comparisons, the
estimated strength difference is:

```
delta = log(7/3) = log(2.333) = 0.847
```

The probability that A beats B in a future match is:

```
P(A > B) = sigmoid(delta) = sigmoid(0.847) = 0.700
```

If A beats C in 9 out of 10 comparisons:

```
delta_AC = log(9/1) = 2.197
P(A > C) = sigmoid(2.197) = 0.900
```

Even though we never compared B and C directly, we can infer:

```
P(B > C) = sigmoid(2.197 - 0.847) = sigmoid(1.350) = 0.794
```

This shows how pairwise data builds a global ranking.

## 5. Common confusion (5+ bullet points)

- **"Preference data needs absolute scores."** It does not. Pairwise comparisons
are enough. In fact, pairwise data is often more reliable than absolute scores.
- **"Chosen must be perfect and rejected must be terrible."** Rejected only needs
to be worse than chosen. Both can be good, or both can be bad, as long as the
ranking is correct.
- **"More rejected examples is better."** Quality matters more than quantity. A
small set of carefully labeled comparisons from expert annotators usually beats
a massive set of noisy labels.
- **"Preference data is only for RLHF."** DPO and ORPO also consume preference
data. Any alignment method that learns from human rankings needs it.
- **"You can generate preference data with a single model."** High-quality
preference data usually comes from comparing multiple models or from human
rewrites. Using one model to generate both chosen and rejected often produces
biased or low-diversity pairs.
- **"Bradley-Terry assumes transitivity."** It does assume that if A > B and
B > C then A > C, which is not always true for human preferences. In practice,
cycles exist and are handled by averaging or regularization.

## 6. Where it is used in our code

`src/phase66/phase66_dpo_orpo_colab.py` builds a preference dataset from
scratch with (prompt, chosen, rejected) triplets and feeds it into DPOTrainer
and ORPOTrainer.

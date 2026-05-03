## What Is a p-value?

---

## The Problem

Your team has spent six weeks developing a new optimizer. On the standard benchmark, your baseline model scores 85.0% accuracy, and the new model scores 85.4%. The product manager wants to ship the new optimizer immediately. But you know that random initialization alone can swing scores by plus or minus 0.5%. If you ship based on one run, you might be celebrating noise. You need a principled way to ask: assuming the new optimizer is no better than the old one, how surprising is it to see a 0.4% improvement by chance alone?

---

## Definition

The **p-value** is the probability of obtaining test results at least as extreme as the observed results, assuming that the null hypothesis (no true effect) is true. It quantifies how much the data disagrees with the idea that nothing interesting is happening.

**How it works:**
```
Null hypothesis:      the new optimizer is no better than the baseline (true difference = 0)
Observed difference:  85.4% - 85.0% = +0.4%
Test statistic:       the difference in means across repeated runs
Null distribution:    the distribution of differences we would see if the null were true
p-value:              the proportion of the null distribution that is ≥ +0.4%
```

**Key techniques:**
- **Permutation test:** shuffle labels between groups and recompute the difference many times to build the null distribution empirically.
- **Paired t-test:** assumes normally distributed differences and computes a parametric p-value.
- **Bootstrap hypothesis test:** resamples the data with replacement to estimate the sampling distribution under the null.

**Why this matters:**
- A low p-value does not prove the new optimizer is better, but it tells you that chance alone is an unlikely explanation.
- A high p-value protects you from false optimism: the observed difference is well within the range of normal noise.
- p-values are a filter, not a conclusion. They tell you whether a result is worth investigating further, not whether it is practically important.

---

## Real-Life Analogy

Imagine a factory that manufactures dice for board games. They claim their dice are fair: each face has a 1/6 chance. You suspect they are cheating, so you roll one of their dice 100 times and get 65 sixes. The p-value answers the following question: if the die were truly fair, how likely is it to see 65 or more sixes in 100 rolls?

**The calculation:** Under a fair die, the expected number of sixes is 16.7. The probability of 65 or more is astronomically small, roughly 0.0000001. This low p-value suggests that the observed outcome is extremely surprising under the fairness assumption. You reject the fairness claim and investigate the factory. But notice what the p-value does not say: it does not say the probability that the die is fair is 0.0000001%. It says the probability of the data, given fairness, is tiny. The die might still be fair and you might have witnessed a one-in-ten-million fluke, or the die might be weighted. The p-value only measures the compatibility between data and hypothesis.

**The trade-off:** Setting a strict threshold like p < 0.05 protects against false discoveries but means you will miss some real effects. Setting a loose threshold like p < 0.20 catches more real effects but lets more false positives through. There is no universally correct threshold; it depends on the cost of being wrong.

---

## Tiny Numeric Example

**Comparing two models with a paired permutation test:**

| Metric | Model A | Model B | Difference (B - A) |
|---|---|---|---|
| Run 1 | 85.0% | 85.4% | +0.4% |
| Run 2 | 84.8% | 85.1% | +0.3% |
| Run 3 | 85.2% | 85.3% | +0.1% |
| Run 4 | 84.9% | 85.5% | +0.6% |
| Run 5 | 85.1% | 84.9% | -0.2% |
| Mean | 85.00% | 85.24% | +0.24% |

**Permutation test results:**
```
Null distribution:    10,000 permutations of the paired differences
Observed mean diff:   +0.24%
p-value (two-tailed): 0.12
```

**Decision at alpha = 0.05:**
```
p = 0.12 > 0.05  →  fail to reject the null hypothesis
Conclusion: We do not have sufficient evidence to claim Model B is better.
Recommendation: Run 10 more seeds or test on a harder benchmark.
```

**The shift:** Without the p-value, the +0.24% average looks like a win. With the p-value, you see that 12% of random permutations produce a difference this large or larger. The improvement is plausible noise, not a trustworthy signal.

---

## Common Confusion

1. **"The p-value is the probability that the null hypothesis is true."** It is the probability of the data given the null hypothesis, not the probability of the hypothesis given the data. These are fundamentally different quantities.

2. **"A p-value of 0.05 means there is a 5% chance I am wrong."** It means there is a 5% chance of seeing data this extreme if the null were true. Your actual probability of being wrong depends on prior beliefs and the base rate of true effects.

3. **"A non-significant p-value proves there is no effect."** A high p-value means the evidence is insufficient to detect an effect, not that the effect is zero. The sample might be too small or the noise too large.

4. **"A significant p-value means the effect is important."** A tiny, meaningless effect can yield a very low p-value if the sample size is large enough. Statistical significance is not practical significance.

5. **"You can compare p-values across different studies."** A p-value of 0.01 in Study A and 0.04 in Study B does not mean A found a stronger effect; it depends on sample size, effect size, and experimental design.

6. **"p-hacking is just running many tests."** p-hacking is running many tests and only reporting the significant ones, creating a biased view of the evidence. Running many tests is fine if you correct for multiple comparisons.

7. **"p-values are obsolete and should never be used."** p-values have well-known limitations, but they remain a useful heuristic when combined with confidence intervals, effect sizes, and replication.

---

## Where It Is Used in Our Code

`src/phase94/phase94_statistical_rigor.py` — We simulate two models with slightly different true accuracies and run a paired permutation test across multiple seeds. We build the null distribution empirically by shuffling labels, compute the two-tailed p-value, and plot the null distribution with the observed statistic marked. You can see exactly how extreme your result is relative to the noise.

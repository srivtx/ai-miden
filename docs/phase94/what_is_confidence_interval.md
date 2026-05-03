## What Is a Confidence Interval?

---

## The Problem

Your model scores 92.3% accuracy on the test set. You report this number to stakeholders, and they ask a reasonable follow-up: "How far might that number move if we collected a different test set next week, or if we trained with a different random seed?" A single point estimate is like a dart on a blank wall: it tells you where one throw landed, but nothing about the thrower's skill. Without a range that captures the uncertainty, every reported metric is a fragile boast waiting to be contradicted by reality.

---

## Definition

A **confidence interval** is a range of values, derived from sample data, that is likely to contain the true population parameter with a specified probability (e.g., 95%). It quantifies how far the sample estimate might deviate from the unknown truth due to sampling variability.

**How it works:**
```
Sample accuracy:      92.3% (from 1,000 test examples)
Bootstrap samples:    10,000 resamples with replacement
95% confidence interval: [90.1%, 94.2%]
Interpretation:       If we repeated the experiment many times, 95% of the
                      computed intervals would contain the true accuracy.
```

**Key techniques:**
- **Bootstrap:** resample the data with replacement many times and compute the metric on each resample; use percentiles of the distribution as bounds.
- **Normal approximation:** compute the standard error analytically and add/subtract 1.96 standard errors for a 95% interval.
- **Clopper-Pearson:** an exact method for proportions that guarantees coverage but can be conservative.

**Why this matters:**
- A narrow interval around 92.3% inspires confidence; a wide interval from 85% to 99% suggests the estimate is unstable.
- Intervals allow comparisons: if the 95% CI for Model A is [91%, 93%] and for Model B is [92.5%, 94.5%], B is likely better.
- Reporting intervals is honest science. It tells readers how much they should trust the headline number.

---

## Real-Life Analogy

Imagine you are trying to find the exact depth of a single fish swimming in a large lake. You cannot see the fish, so you cast a net and measure the depth where you caught it: 12 meters. But the fish moves. If you cast the net 100 times in the same lake, 95 of those casts will catch the fish at depths between 10.5 and 13.5 meters. The width of that range reflects how uncertain you are about the fish's exact location.

**The trade-off:** If you use a wider net, you catch the fish more often, but you learn less about its precise depth. A 99% confidence interval is wider than a 95% interval; it is more likely to contain the truth but less informative. Conversely, a 50% interval is narrow and precise but misses the truth half the time. The researcher must choose the confidence level based on the cost of being wrong. In medical trials, 99% is common. In early prototyping, 90% might suffice.

**The catch:** The interval is random, not the parameter. The fish is at a fixed depth; the net's location is what varies. Saying "there is a 95% probability that the true accuracy is in this interval" is technically incorrect. The correct statement is: "this procedure produces intervals that capture the true accuracy 95% of the time." Once the interval is computed, the true value is either inside or outside; there is no probability left.

---

## Tiny Numeric Example

**A model scores 90% accuracy on a test set of n examples. Bootstrapping yields:**

| Test Set Size | Sample Accuracy | 95% CI Lower | 95% CI Upper | CI Width |
|---|---|---|---|---|
| 250 | 90.0% | 85.4% | 93.8% | 8.4% |
| 1,000 | 90.0% | 88.1% | 91.7% | 3.6% |
| 5,000 | 90.0% | 89.2% | 90.8% | 1.6% |
| 1,000 | 90.0% (99% CI) | 87.5% | 92.3% | 4.8% |

**Interpretation:**
```
n = 250:    The true accuracy could plausibly be as low as 85% or as high as 94%.
            The point estimate is almost meaningless.
n = 1,000:  The true accuracy is likely between 88% and 92%.
            This is informative enough for internal decisions.
n = 5,000:  The estimate is precise; the true accuracy is almost certainly near 90%.
```

**Comparing two models with confidence intervals:**
```
Model A:  88.0% accuracy, 95% CI [85.2%, 90.5%]
Model B:  90.5% accuracy, 95% CI [88.1%, 92.7%]
Overlap:  [88.1%, 90.5%] is shared.
Conclusion: The evidence that B is better is suggestive but not conclusive.
```

**The shift:** The confidence interval transforms a naked point estimate into a range that respects uncertainty. A model with 90% accuracy and a tight interval is more trustworthy than a model with 91% accuracy and a wide interval.

---

## Common Confusion

1. **"A 95% confidence interval means there is a 95% probability that the true value is inside."** The true value is fixed; the interval is random. The 95% refers to the long-run frequency of the procedure, not the probability of any single interval.

2. **"A confidence interval is a prediction interval."** A confidence interval bounds an unknown population parameter; a prediction interval bounds where a future individual observation might fall. They are not interchangeable.

3. **"Narrow intervals always mean good estimates."** A narrow interval can be wrong if the estimator is biased. A precise wrong answer is still wrong.

4. **"If two confidence intervals overlap, the difference is not significant."** Overlap is a rough heuristic, not a formal test. Two intervals can overlap slightly while the difference is still statistically significant.

5. **"Bootstrapping is always better than normal approximation."** Bootstrapping is more robust but computationally expensive and can fail with very small samples or extreme outliers.

6. **"You can only compute confidence intervals for accuracy."** Confidence intervals apply to any estimator: loss, AUC, F1, latency, carbon footprint, or revenue.

7. **"A 95% confidence interval is the only valid choice."** The 95% convention is arbitrary. Use 90% for exploratory work, 99% for safety-critical decisions, and justify your choice.

---

## Where It Is Used in Our Code

`src/phase94/phase94_statistical_rigor.py` — We compute accuracy on a small test set and then generate 10,000 bootstrap resamples to construct a 95% confidence interval. We compare the bootstrap interval to the normal approximation and show how the interval width shrinks as the test set grows. We plot the bootstrap distribution as a histogram with vertical lines marking the interval bounds.

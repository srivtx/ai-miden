## What Is a Benchmark?

---

## The Problem

Researchers need a common playing field to compare models. Without a shared evaluation protocol, every paper can claim superiority using a different dataset or metric, making progress impossible to measure. How do you create a standardized test that forces every model to compete under identical rules?

---

## Definition

A **benchmark** is a standardized combination of dataset, task definition, evaluation metric, and protocol that allows fair comparison across models and research groups.

**How it works:**
```
Benchmark design:
  1. Define the task (e.g., image classification into 1,000 categories)
  2. Curate the dataset (e.g., 1.28M training images, 50K validation, 100K test)
  3. Choose metrics (e.g., top-1 accuracy, top-5 accuracy)
  4. Establish protocol:
       - Allowed preprocessing
       - Hyperparameter search budget
       - Number of training runs to average
       - Reporting requirements (mean, std, confidence intervals)
  5. Publish leaderboard or results table
  6. Update periodically to prevent overfitting and benchmark saturation
```

**Why this matters:**
- Without a benchmark, Model A claims 95% on a custom dataset while Model B claims 94% on a different dataset. The numbers are incomparable.
- A well-designed benchmark forces researchers to solve a real problem rather than gaming an arbitrary metric.
- Public leaderboards create competitive pressure that drives the field forward.

---

## Real-Life Analogy

A benchmark is like a racing track. Every car (model) drives the same distance, under the same rules, so the stopwatch (metric) tells us which is genuinely faster.

Imagine a high school track meet. Every sprinter runs 100 meters on the same surface, in the same direction, with the same starting gun. The winner is the one with the lowest time, not the one who ran downhill or used a tailwind. If one runner used starting blocks and another did not, the comparison would be unfair. A benchmark enforces the same fairness in machine learning: every model trains on the same data split, evaluates on the same held-out set, and reports the same metric. Without that standardization, claims of superiority are as meaningless as comparing a downhill sprint to an uphill one.

**The trade-off:** Benchmarks can become targets that are gamed rather than solved. Models may overfit to benchmark-specific patterns rather than learning general capabilities. Good benchmarks are updated, diversified, and supplemented with real-world evaluations.

---

## Tiny Numeric Example

**Before a shared benchmark:**

| Model | Claimed Accuracy | Dataset | Metric | Comparable? |
|-------|-----------------|---------|--------|-------------|
| Model A | 95% | Custom cats/dogs | Accuracy | No |
| Model B | 94% | CIFAR-10 | Accuracy | No |
| Model C | 92% | ImageNet subset | Top-1 | Partially |

- Conclusion: impossible to tell which model is best
- Research progress: unmeasurable
- Industry adoption: risky (no standard validation)

**After ImageNet benchmark standardization:**

| Model | Top-1 Accuracy | Top-5 Accuracy | Parameters | Year |
|-------|---------------|----------------|------------|------|
| AlexNet | 57.1% | 80.2% | 61M | 2012 |
| ResNet-50 | 76.1% | 92.9% | 25.6M | 2015 |
| EfficientNet-B7 | 84.4% | 97.1% | 66M | 2019 |

- Conclusion: direct comparison possible
- Research progress: measurable year over year
- Industry adoption: safe (validated on held-out test set)

---

## Common Confusion

1. **"A benchmark is just a dataset."** It is not. A dataset is raw material; a benchmark adds the task, metric, and rules that govern how the dataset is used.

2. **"A high benchmark score means the model is ready for production."** It does not. Benchmarks measure capability on a specific distribution. Real-world data often differs, and additional testing is required.

3. **"Leaderboard position is the only thing that matters."** It is not. A model that tops a benchmark by 0.1% but requires 10x the compute may be less practical than the runner-up.

4. **"Benchmarks never change."** They do. Good benchmarks are updated to prevent saturation and to reflect evolving real-world needs. Static benchmarks eventually become solved and less informative.

5. **"One benchmark covers all capabilities."** It does not. ImageNet measures classification; it says nothing about robustness, fairness, or energy efficiency. Comprehensive evaluation requires multiple benchmarks.

6. **"Private test sets are unfair."** They are not. Private test sets prevent models from overfitting to the test data, which is essential for trustworthy generalization claims.

7. **"Benchmarks are only for academics."** They are not. Industry teams use benchmarks to screen pretrained models, set minimum performance bars, and compare vendor offerings.

---

## Where It Is Used in Our Code

`src/phase92/phase92_benchmark_design.py` — We construct a toy benchmark that demonstrates clean versus contaminated evaluation splits. We generate a synthetic dataset, train logistic regression on a clean training set and a contaminated training set, and compare accuracy and F1 on a held-out test set. The script plots the comparison and saves it to `phase92_comparison.png`, showing how benchmark integrity depends on strict train-test isolation.

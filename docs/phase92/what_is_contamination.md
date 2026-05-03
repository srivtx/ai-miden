## What Is Contamination?

---

## The Problem

When test examples leak into training data, models appear stronger than they are. This undermines claims of generalization, wastes research effort on inflated results, and misleads practitioners into choosing models that fail in production. How do you detect and prevent train-test leakage?

---

## Definition

**Contamination** is the presence of test-set information in the training pipeline. It includes exact duplicates, near-duplicates, or indirect exposure (for example, pre-training on a corpus that contains the test set).

**How it works:**
```
Contamination pathways:
  1. Exact duplication: test paragraphs copied verbatim into training data
  2. Near-duplication: test examples paraphrased or lightly edited in training
  3. Indirect exposure: pre-training on a web corpus that includes the test set
  4. Prompt leakage: benchmark questions appear in instruction-tuning data

Detection methods:
  1. N-gram overlap between train and test
  2. Embedding similarity search across splits
  3. Perplexity analysis: test examples with suspiciously low perplexity
  4. Deduplication pipelines before final training

Prevention:
  1. Date-based splits (train on older data, test on newer)
  2. Strict deduplication against known benchmarks
  3. Contamination-aware data curation before pre-training
```

**Why this matters:**
- A contaminated model may score 95% on a benchmark but fail on real tasks, leading to false confidence.
- Contamination invalidates scientific claims and damages reproducibility.
- High-profile benchmarks like GLUE and HellaSwag have been found to suffer from leakage into pre-training corpora.

---

## Real-Life Analogy

Contamination is like a student who sees the exam questions while studying. The resulting score no longer reflects true understanding, only memorization.

Imagine a cooking competition where contestants are judged on their ability to recreate a mystery dish. One contestant sneaks into the kitchen the night before and tastes the mystery sauce. On competition day, that contestant produces a perfect replica and wins. The victory is hollow because the contestant did not demonstrate culinary skill; they demonstrated access to the answer key. In machine learning, contamination is that sneak preview. The model "wins" the benchmark not because it learned general reasoning, but because it memorized the test. The community wastes months improving a model that only knows how to regurgitate.

**The trade-off:** Aggressive contamination removal can shrink datasets and remove valuable training signal. The goal is not to sanitize every byte but to ensure that evaluation measures true capability rather than memorization.

---

## Tiny Numeric Example

**Clean training and evaluation:**

| Scenario | Accuracy | F1 Score | Notes |
|----------|----------|----------|-------|
| Train on clean data | 0.7200 | 0.7012 | Honest estimate |

**Contaminated training (30% of test set leaked):**

| Scenario | Accuracy | F1 Score | Notes |
|----------|----------|----------|-------|
| Train on contaminated data | 0.9100 | 0.8923 | Inflated by leakage |

- Apparent improvement: +19 percentage points
- True improvement: 0 points (the model memorized answers)
- Risk to practitioners: high (model deployed based on false score)
- Remediation: strict deduplication and date-based splits

---

## Common Confusion

1. **"Contamination is the same as overfitting."** It is not. Overfitting occurs when a model learns training-specific noise; contamination occurs when the model has already seen the test data during training.

2. **"Only exact copies count as contamination."** They do not. Near-duplicates, paraphrases, and indirect exposure through related corpora also inflate scores.

3. **"Small amounts of leakage do not matter."** They do. Even 1% contamination can raise benchmark scores by several points on tasks with limited test sets.

4. **"Contamination is easy to detect."** It is not. Indirect exposure through massive pre-training corpora is nearly impossible to audit exhaustively.

5. **"Removing contaminated data fixes the model."** It prevents future contamination, but a model already trained on leaked data must be retrained from scratch on clean data.

6. **"Benchmark creators are solely responsible for preventing leakage."** They are not. Model trainers must also deduplicate their pre-training data against known benchmarks.

7. **"Contamination only affects academic benchmarks."** It does not. Production models trained on web data may also memorize customer information or test queries, creating privacy and compliance risks.

---

## Where It Is Used in Our Code

`src/phase92/phase92_benchmark_design.py` — We simulate data contamination by copying 30% of the test set into the training set, then train and evaluate logistic regression under both clean and contaminated conditions. The script prints accuracy and F1 for both scenarios and plots a bar chart saved to `phase92_comparison.png`, showing how contaminated training data inflates metrics and destroys the validity of generalization claims.

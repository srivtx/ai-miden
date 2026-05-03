## What Is Validity?

---

## The Problem

A high score on a benchmark is meaningless if the benchmark does not capture the real-world capability it claims to measure. A translation test that only evaluates formal written sentences may miss a model's failure with conversational slang. How do you ensure that your ruler is measuring length, not temperature?

---

## Definition

**Validity** is the degree to which a test or benchmark actually measures the construct it is intended to measure. It encompasses content validity, construct validity, and predictive validity.

**How it works:**
```
Types of validity:

  Content validity:
    - Do the test items cover the full domain?
    - Example: a math benchmark with only algebra questions has low content validity for general math ability.

  Construct validity:
    - Does the test correlate with related measures?
    - Example: a reading comprehension benchmark should correlate with human reading scores.

  Predictive validity:
    - Do test scores predict real-world performance?
    - Example: a coding benchmark should predict how well a model helps programmers in practice.

Improving validity:
  1. Audit test items for domain coverage
  2. Compare benchmark scores with human performance on the same tasks
  3. Conduct user studies to verify real-world utility
  4. Update benchmarks as the real-world task distribution evolves
```

**Why this matters:**
- A model with 95% validity on a narrow benchmark may score 60% on the actual task distribution.
- High validity ensures that research effort is directed toward capabilities that matter in production.
- Invalid benchmarks create false confidence and misallocate engineering resources.

---

## Real-Life Analogy

A bathroom scale has high validity if it measures weight accurately. If it instead reacts to humidity, it is unreliable for weight and therefore invalid for that purpose, even if it gives consistent readings.

Imagine a university entrance exam that tests only memorization of historical dates. Two students apply: one memorizes every date and scores perfectly; the other understands causation, critical analysis, and historiography but forgets a few years. The exam has high reliability (memorizers consistently score well) but low validity (it does not measure the critical thinking the university actually wants). In machine learning, a benchmark that only tests multiple-choice factual recall has low validity for measuring reasoning. The model may ace the benchmark while failing at open-ended problem solving. Validity is the gap between what you think you are measuring and what you are actually measuring.

**The trade-off:** Highly valid benchmarks are expensive to create. Real-world user studies, expert annotation, and diverse task design take far more effort than auto-generating multiple-choice questions. The investment pays off in trustworthy evaluation.

---

## Tiny Numeric Example

**Benchmark with low validity for conversational translation:**

| Test Item Type | Count | Model BLEU | Human Rating |
|----------------|-------|------------|--------------|
| Short formal sentences | 800 | 0.85 | Good |
| Informal conversational speech | 100 | 0.52 | Poor |
| Slang and idioms | 100 | 0.38 | Very poor |
| **Overall BLEU** | **1,000** | **0.79** | **Misleading** |

- The overall score of 0.79 suggests strong translation ability.
- In reality, the model fails on 20% of real-world conversational use cases.
- Validity problem: benchmark over-represents formal text.

**After redesigning for higher validity:**

| Test Item Type | Count | Model BLEU | Human Rating |
|----------------|-------|------------|--------------|
| Short formal sentences | 300 | 0.85 | Good |
| Informal conversational speech | 400 | 0.52 | Poor |
| Slang and idioms | 300 | 0.38 | Very poor |
| **Overall BLEU** | **1,000** | **0.55** | **Honest** |

- The lower overall score of 0.55 is less flattering but more accurate.
- Practitioners now know the model needs improvement on informal language.
- Validity improvement: benchmark reflects true task distribution.

---

## Common Confusion

1. **"Validity is the same as reliability."** It is not. Reliability means the test gives consistent results; validity means it measures the right thing. A scale that always shows 5 kg extra is reliable but invalid.

2. **"High benchmark score implies high validity."** It does not. A model can score perfectly on an invalid benchmark. Validity is a property of the benchmark, not the model.

3. **"One benchmark can measure every capability."** It cannot. Each benchmark measures a specific construct. A suite of diverse benchmarks is needed for comprehensive evaluation.

4. **"Validity is fixed once the benchmark is created."** It is not. As real-world tasks evolve, benchmarks must be updated to maintain relevance and validity.

5. **"Automated metrics guarantee validity."** They do not. BLEU, ROUGE, and accuracy are proxies. Their validity depends on how well they correlate with human judgment.

6. **"A benchmark validated for English is valid for all languages."** It is not. Cultural context, syntax, and evaluation norms differ across languages. Validity must be assessed per language.

7. **"Internal consistency means the benchmark is valid."** It does not. A benchmark can be internally consistent (all items measure the same thing) while measuring the wrong thing entirely.

---

## Where It Is Used in Our Code

`src/phase92/phase92_benchmark_design.py` — We discuss how a toy benchmark's validity depends on whether it reflects the true task distribution. The script generates a synthetic dataset where only the first three features carry signal, and it notes that adding seven noise features without regularization slightly lowers validity. The comparison between clean and contaminated evaluation further illustrates how benchmark design choices directly affect the trustworthiness of measured performance.

## What Is Iterative Self-Improvement?

---

### The Problem

A model generates some correct answers and many wrong ones. If you filter and train only on the correct ones, the model improves slightly. But then the improved model generates even better answers. Can you loop this process indefinitely?

---

### Definition

**Iterative self-improvement** is a training loop where:
1. The current model generates a large batch of outputs
2. A verifier filters for high-quality outputs
3. The model is fine-tuned on the filtered outputs
4. The improved model generates the next batch
5. Repeat

**The key insight:** Each iteration raises the quality floor. The model trains on its own best work, so its average output quality climbs.

**Mathematically:**
```
Iteration 0: Model M_0 generates outputs. Quality distribution: mean = 60%, std = 20%
  -> Filter top 30% (quality > 75%)
  -> Fine-tune M_0 on top 30% -> M_1

Iteration 1: Model M_1 generates outputs. Quality distribution: mean = 70%, std = 18%
  -> Filter top 30% (quality > 82%)
  -> Fine-tune M_1 on top 30% -> M_2

Iteration 2: Model M_2 generates outputs. Quality distribution: mean = 78%, std = 15%
  -> Filter top 30% (quality > 88%)
  -> Fine-tune M_2 on top 30% -> M_3
```

**Limitations:**
- Without a verifier, the model hallucinates confidently and trains on its own hallucinations
- The improvement curve eventually plateaus
- Diversity collapses if the model keeps generating similar "safe" answers

---

### Real-Life Analogy

A writer revising their own novel.
- **Draft 1:** The writer produces a rough manuscript. Some chapters are good, most are mediocre, a few are terrible.
- **Self-editing:** The writer keeps only the good chapters, rewrites the mediocre ones using the good chapters as style references, and deletes the terrible ones.
- **Draft 2:** The manuscript is better overall. The average chapter quality improved because the writer trained themselves on their own best work.
- **Repeat:** Each draft is better than the last, though diminishing returns set in.

If the writer had no taste (no verifier), they would keep the terrible chapters and the manuscript would get worse. The verifier — the ability to distinguish good from bad — is essential.

---

### Tiny Numeric Example

**Task:** Classify points into 3 categories.

**Initial model accuracy:** 60%

**Iteration 0:**
```
Generate 1000 predictions on unlabeled data
Confidence scores: some high, some low
Filter: keep only predictions with confidence > 0.8
Result: 300 high-confidence predictions (92% estimated accuracy)
Fine-tune on these 300 -> Model v1
```

**Iteration 1:**
```
Model v1 accuracy: 72%
Generate 1000 new predictions
Filter: confidence > 0.8
Result: 350 high-confidence predictions (95% estimated accuracy)
Fine-tune on these 350 -> Model v2
```

**Iteration 2:**
```
Model v2 accuracy: 81%
Generate 1000 new predictions
Filter: confidence > 0.8
Result: 400 high-confidence predictions (97% estimated accuracy)
Fine-tune on these 400 -> Model v3
```

**Plateau:**
```
Model v3 accuracy: 86%
Model v4 accuracy: 88%
Model v5 accuracy: 89%
...
Model v10 accuracy: 91% (no further improvement)
```

The model improved from 60% to 91% by training on its own best outputs, but hit a ceiling determined by the verifier quality and task difficulty.

---

### Common Confusion

1. **"Self-improvement is just overfitting."** It can become overfitting if the synthetic data lacks diversity. Good implementations enforce diversity (temperature sampling, prompt variation).

2. **"Any model can self-improve indefinitely."** No. The verifier quality and the model's capacity set hard limits. AlphaGo improved dramatically but still plateaued below perfect play.

3. **"Self-improvement replaces human supervision."** It reduces but does not eliminate the need for human oversight. Humans design the verifier and monitor for degradation.

4. **"Self-improvement only works for generative tasks."** It works for any task where the model can generate outputs and a verifier can score them: classification, regression, ranking, and generation.

5. **"The first iteration is enough."** Usually 2-5 iterations give most of the benefit. Beyond that, returns diminish sharply.

---

### Where It Is Used in Our Code

`src/phase47/phase47_synthetic_data.py` — We run 3 iterations of self-improvement on a small classifier. Each iteration generates synthetic labeled data, filters by confidence, and fine-tunes the model. We plot the accuracy curve across iterations.

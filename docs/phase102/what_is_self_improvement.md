## What Is Self-Improvement?

---

### The Problem

High-quality human-labeled data is expensive, slow to produce, and finite. For specialized domains — theorem proving, rare disease diagnosis, low-resource language translation — there may simply not be enough labeled examples to train a model to peak performance. Collecting more data means hiring experts, waiting months, and spending millions. How do you push a model beyond the limits of available human supervision without acquiring new labeled datasets?

---

### Definition

**Self-Improvement** is the process by which a model generates its own training data, filters or verifies it using an external checker, and then trains on the resulting dataset to improve its capabilities. This creates a feedback loop where the model bootstraps from its own outputs, gradually shifting its distribution toward higher-quality generations without new human labels.

**How it works:**
```
Iteration 0:
  Base model generates 10,000 chain-of-thought solutions.
  Symbolic solver verifies 3,200 as correct.
  Model fine-tuned on the 3,200 correct chains.

Iteration 1:
  Improved model generates 10,000 new solutions.
  Symbolic solver verifies 5,800 as correct.
  Model fine-tuned on the 5,800 correct chains.

Iteration 2:
  Further improved model generates 10,000 solutions.
  Symbolic solver verifies 7,400 as correct.
  ...

Result: model accuracy on held-out problems increases from 32% to 61%.
```

**Key properties:**
- The verifier is the critical component; without it, the model reinforces its own errors.
- Each iteration requires generating far more samples than are accepted.
- The loop can be repeated until improvement plateaus or the verifier's capacity is exhausted.

**Why this matters:**
- It breaks the data bottleneck for domains where human labels are scarce.
- It has been used to improve math reasoning, code generation, and theorem proving.
- It demonstrates that models can partially bootstrap their own capabilities, though not indefinitely.

---

### Real-Life Analogy

Imagine a student preparing for a mathematics competition. The student has exhausted the official practice problems and cannot afford a tutor. Instead, the student writes her own practice problems, solves them, and checks the answers against a calculator and a solution manual. She discards the problems she got wrong and studies only the ones she got right. In the next round, she writes harder problems based on what she learned, solves them, and checks again. Over time, her problem-writing improves, her accuracy rises, and she approaches competition-level skill without ever seeing a new external problem set. Self-Improvement is that student: a closed loop of generation, verification, and learning that turns limited initial knowledge into growing expertise.

The trade-off is the quality of the verifier. If the calculator is broken, the student reinforces wrong answers. If the solution manual is incomplete, she misses valid solution methods and converges on a narrow subset of techniques. This phenomenon — amplifying errors over iterations — is called model collapse or drift. Without a reliable external signal, self-improvement is not improvement at all; it is a descent into self-reinforced hallucination. Even with a good verifier, gains are not infinite. Each iteration harvests the low-hanging fruit of the model's current capability, and eventually the model reaches the ceiling of what its architecture and the verifier can support. Self-improvement is a ladder, not an elevator: it helps you climb, but it does not reach the sky.

---

### Tiny Numeric Example

**Self-improvement loop on math reasoning:**
```
Iteration | Samples generated | Accepted by verifier | Acceptance rate | Test accuracy
----------|-------------------|----------------------|-----------------|---------------
0 (base)  | 10,000            | 3,200                | 32%             | 35%
1         | 10,000            | 5,800                | 58%             | 48%
2         | 10,000            | 7,400                | 74%             | 57%
3         | 10,000            | 8,100                | 81%             | 61%
4         | 10,000            | 8,300                | 83%             | 62%
5         | 10,000            | 8,350                | 83.5%           | 62%  (plateau)
```

**Verifier quality impact on iteration 3:**
```
Verifier type        | Accepted | Test accuracy after iter 3
---------------------|----------|----------------------------
Perfect symbolic     | 8,100    | 61%
Noisy symbolic (5% error) | 7,800 | 55%
Weak heuristic       | 4,500    | 38%  (worse than iteration 1!)
No verifier (all accepted) | 10,000 | 29%  (model collapse)
```

**Distribution shift over iterations:**
```
Metric                          | Iter 0 | Iter 2 | Iter 4
--------------------------------|--------|--------|--------
Mean solution length (tokens)   | 45     | 52     | 58
Unique solution strategies      | 12     | 9      | 7
Average verifier confidence     | 0.62   | 0.78   | 0.81
```

**The shift:** Self-improvement raises accuracy from 35% to 62% over four iterations, but the gains plateau as the model exhausts the verifier's capacity. A weak verifier causes collapse; no verifier causes rapid degradation. The model also narrows its strategy diversity, a warning sign of converging on a local optimum.

---

### Common Confusion

1. **"Self-improvement means the model improves infinitely."** It does not. Improvement plateaus when the model reaches the ceiling of what its architecture, the verifier, and the generation distribution can support. Each iteration harvests diminishing returns.

2. **"The model improves without any external signal."** False. The verifier is an external signal. Whether it is a symbolic checker, a unit test, or a retrieval system, some quality criterion outside the model itself is required to filter good samples from bad.

3. **"Self-improvement is the same as unsupervised learning."** It is not. Unsupervised learning finds structure in raw data. Self-improvement generates synthetic labeled data and trains on it. The labels come from the verifier, making it a form of weakly supervised or self-supervised learning.

4. **"Any model can self-improve on any task."** Only tasks with reliable, automatic verifiers are suitable. Math and code work well because answers are checkable. Creative writing and open-ended conversation do not, because there is no automatic ground truth.

5. **"Self-improvement and distillation are the same."** Distillation transfers knowledge from a large model to a small one. Self-improvement uses the same model's own outputs to train itself. They can be combined, but they are distinct paradigms.

6. **"Acceptance rate always increases with iterations."** Usually it does, but this can mask declining diversity. A model might converge on a small set of stereotyped solutions that pass the verifier, reducing robustness on novel problems.

7. **"Self-improvement replaces human data collection."** It augments it but does not replace it. Human data is needed for the initial model, the verifier design, and periodic validation. Self-improvement is a multiplier, not a substitute.

---

### Where It Is Used in Our Code

`src/phase102/phase102_synthetic_data.py` — We simulate a self-improvement loop where a generative distribution shifts its mean based on accepted samples from a verifier. Over five iterations, we track how the mean converges toward the verifier's target and how the acceptance rate plateaus, demonstrating both the power and the limits of bootstrapped improvement.

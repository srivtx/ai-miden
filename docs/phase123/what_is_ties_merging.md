## What Is TIES Merging?

---

### The Problem

Task arithmetic and SLERP work well when specialist models agree on which weights to change and in which direction. But in practice, when you fine-tune a base model on different tasks, the resulting task vectors often conflict: one task pushes a weight up while another pushes it down. When you add these conflicting vectors, they cancel out. Worse, both tasks may change many weights that are irrelevant to their actual skill — redundant changes that add noise to the merge. How do you keep only the important, agreeing changes and discard the rest?

---

### Definition

**TIES (TrIm, Elect Sign & Merge)** is a model merging technique that resolves sign conflicts and removes redundant parameter changes before combining task vectors. It consists of three steps:

1. **TrIm:** Keep only the top-k percent of parameters with the largest magnitude in each task vector. Small changes are treated as noise and zeroed out.
2. **Elect Sign:** For each parameter, look at all task vectors. If they disagree on the sign (positive vs negative), resolve the conflict by keeping the sign that has the larger total magnitude across all tasks.
3. **Merge:** Average only the parameters that agree with the elected sign. Conflicting parameters are discarded (set to zero) rather than allowed to cancel.

**How it works:**
```
Task vectors: tau_1, tau_2, ..., tau_n

Step 1 — TrIm (density = 20%):
  For each tau_i, keep only the top 20% of parameters by absolute value.
  tau_i_trimmed = top_k(tau_i, k=0.20)

Step 2 — Elect Sign:
  For parameter j:
    total_positive = sum(max(0, tau_i_trimmed[j]) for all i)
    total_negative = sum(abs(min(0, tau_i_trimmed[j])) for all i)
    elected_sign[j] = +1 if total_positive > total_negative else -1

Step 3 — Merge:
  merged[j] = mean(tau_i_trimmed[j] for all i where sign(tau_i_trimmed[j]) == elected_sign[j])
```

**Key insight:**
- Most parameters in a task vector are small and irrelevant — trimming removes noise
- Sign conflicts are the main cause of merge degradation — resolving them prevents cancellation
- TIES usually outperforms naive task arithmetic when merging 3 or more models

**Why this matters:**
- TIES enables merging large numbers of specialist models (10+) without catastrophic interference
- It produces a single model that retains more of each specialist's capability
- It is the current best-practice for community model merging (e.g., MergeKit)

---

### Real-Life Analogy

A committee of experts writing a policy document.
- **Task vectors:** Each expert submits a list of proposed edits to a base draft. Some edits are major (change the budget by 50%). Some are tiny (fix a comma). Some experts want to INCREASE funding; others want to DECREASE it.
- **Naive merging:** You add all edits together. The comma fixes cancel each other out randomly. The funding increases and decreases partially cancel, producing a weak, confusing document.
- **TIES approach:**
  1. **TrIm:** Ignore all edits smaller than a threshold. Comma fixes are noise.
  2. **Elect Sign:** For each policy point, check whether most experts want to increase or decrease. The majority sign wins.
  3. **Merge:** Average only the edits that agree with the majority direction. Dissenting edits are discarded, not averaged in.
- **Result:** A clean, coherent document that reflects the consensus of strong opinions rather than the noise of weak, conflicting ones.

---

### Tiny Numeric Example

**Three task vectors for 5 parameters (simplified):**
```
Parameter:     p1    p2    p3    p4    p5
tau_math:     +0.8  +0.1  -0.9  +0.05 +0.2
tau_code:     +0.7  -0.1  +0.6  +0.04 -0.8
tau_bio:      +0.6  +0.05 +0.5  -0.9  +0.1
```

**Step 1 — TrIm at 40% density (keep top 2 per vector):**
```
tau_math_trimmed:  +0.8   0.0  -0.9   0.0   0.0
tau_code_trimmed:  +0.7   0.0  +0.6   0.0  -0.8
tau_bio_trimmed:   +0.6   0.0  +0.6   0.0   0.0
```
Small changes (+0.1, +0.05, +0.2, +0.04, +0.1) are zeroed out as noise.

**Step 2 — Elect Sign:**
```
p1: all positive  (+0.8 +0.7 +0.6) → elected sign = +
p2: no votes      → skip
p3: -0.9 vs +0.6+0.6=+1.2 → elected sign = +
p4: no votes      → skip
p5: -0.8 vs nothing positive → elected sign = -
```

**Step 3 — Merge (average agreeing parameters):**
```
merged[p1] = (+0.8 + 0.7 + 0.6) / 3 = +0.70
merged[p2] = 0
merged[p3] = (+0.6 + 0.6) / 2 = +0.60   (math's -0.9 is discarded — wrong sign)
merged[p4] = 0
merged[p5] = (-0.8) / 1 = -0.80
```

**Comparison with naive averaging:**
```
Naive average p3: (-0.9 + 0.6 + 0.5) / 3 = +0.07   (near zero, useless)
TIES merged p3:   +0.60                        (strong positive, useful for code and bio)
```
TIES prevented the math specialist's strong negative vote from canceling out the other two specialists.

---

### Common Confusion

1. **"TIES always beats task arithmetic."** Not always. For two models with low interference, task arithmetic is simpler and just as good. TIES shines when merging many models (3+) or when interference is high.

2. **"Trimming throws away useful information."** It can, if the density is set too low. But empirically, 20-30% density retains most of the signal while removing a majority of the noise. The small-magnitude changes are less important than the large ones.

3. **"Elect Sign is just majority voting."** It is magnitude-weighted voting, not simple counting. A task vector with a change of +0.01 and another with -0.90 do not cancel equally. The -0.90 has more "votes" because its magnitude is larger.

4. **"TIES requires all models to be fine-tuned from the same base."** Yes. TIES operates on task vectors, which are defined relative to a base. Merging models with different architectures or different pre-training is undefined in weight space.

5. **"TIES works in activation space too."** No. TIES is specifically a weight-space method. It trims and elects signs on weight deltas. You cannot directly apply it to logits or hidden states.

6. **"The 'TrIm' step is the same as pruning."** Pruning removes weights permanently from a single model. TrIm removes small task-vector entries temporarily, before merging. The base model weights are untouched.

7. **"TIES eliminates the need for hyperparameter search."** You still need to choose the trim density (typically 0.2–0.4) and the merge scaling coefficient. These are task-dependent and usually found via grid search on a validation set.

---

### Where It Is Used in Our Code

`src/phase123/phase123_merging_concepts.py` — We simulate three specialist task vectors with intentional sign conflicts, apply the TIES three-step pipeline (trim, elect sign, merge), and compare the result against naive averaging and task arithmetic. We show that TIES preserves stronger signals and produces a merged model with less interference.

`src/phase123/phase123_merging_colab.py` — We fine-tune three LoRA adapters on different tasks, extract their task vectors relative to the base, merge them with TIES, and evaluate against naive merging. The TIES-merged model achieves higher combined accuracy across all tasks.

(End of file - total 97 lines)

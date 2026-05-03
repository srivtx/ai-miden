## What Is Task Arithmetic?

---

### The Problem

Simple weight averaging works, but it dilutes the base model's general capabilities. If you average four models, each task-specific deviation is divided by 4. Can we merge models while preserving the base model's general knowledge more explicitly?

---

### Definition

**Task arithmetic** is a model merging technique where fine-tuned models are represented as "task vectors" (their deviation from the base model), and these vectors are added back to the base model with adjustable coefficients.

**The formula:**
```
Task vector for model i:     τ_i = W_i - W_base
Merged model:                W_merged = W_base + λ_1 × τ_1 + λ_2 × τ_2 + ... + λ_n × τ_n
```

**Example with three tasks:**
```
W_merged = W_base + 0.3 × (W_coding - W_base) + 0.3 × (W_medical - W_base) + 0.3 × (W_legal - W_base)
```

**Why this is better than simple averaging:**
- The base model's general knowledge is preserved exactly (the W_base term)
- Each task contributes its unique delta without interfering with the base
- Coefficients λ control how strongly each task influences the merge
- If λ = 1.0 for all tasks, this is equivalent to simple averaging

---

### Real-Life Analogy

A restaurant chain has a standard recipe book (base model). Three chefs each created specialty variations:
- Chef A's Italian variation: "Add extra garlic and olive oil"
- Chef B's Japanese variation: "Use dashi instead of chicken stock"
- Chef C's Mexican variation: "Add cumin and cilantro"

**Simple averaging** would be: mix all three complete recipe books together. The standard recipes get diluted.

**Task arithmetic** is: keep the standard recipe book, then add a note saying "For Italian dishes, also add garlic and olive oil. For Japanese dishes, also use dashi. For Mexican dishes, also add cumin and cilantro."

The base recipes stay intact. Each specialty is an explicit delta. You can even adjust how strongly each delta applies (a little Mexican influence, a lot of Italian influence).

---

### Tiny Numeric Example

**Base model:**
```
W_base = [1.0, 2.0, 3.0, 4.0]
```

**Fine-tuned on Task A:**
```
W_A = [1.5, 2.0, 3.0, 3.5]
Task vector τ_A = W_A - W_base = [0.5, 0.0, 0.0, -0.5]
```

**Fine-tuned on Task B:**
```
W_B = [1.0, 2.5, 2.5, 4.0]
Task vector τ_B = W_B - W_base = [0.0, 0.5, -0.5, 0.0]
```

**Task arithmetic merge with λ = 0.5 for both:**
```
W_merged = W_base + 0.5 × τ_A + 0.5 × τ_B
         = [1.0, 2.0, 3.0, 4.0] + 0.5 × [0.5, 0.0, 0.0, -0.5] + 0.5 × [0.0, 0.5, -0.5, 0.0]
         = [1.0, 2.0, 3.0, 4.0] + [0.25, 0.0, 0.0, -0.25] + [0.0, 0.25, -0.25, 0.0]
         = [1.25, 2.25, 2.75, 3.75]
```

**Result:**
- The merged model preserves W_base's general structure
- It incorporates Task A's preference for higher first weight and lower last weight
- It incorporates Task B's preference for higher second weight and lower third weight
- Each task's unique contribution is explicit and adjustable

---

### Common Confusion

1. **"Task arithmetic is just fancy averaging."** It is mathematically equivalent to weighted averaging when all λ = 1/n, but conceptually different. It makes the base model's role explicit.

2. **"Task vectors can be arbitrarily large."** No. If task vectors are too large, the merged model drifts far from the base and loses generalization. Good fine-tuning keeps task vectors small.

3. **"Task arithmetic prevents interference between tasks."** It reduces interference but does not eliminate it. If τ_A and τ_B push the same weight in opposite directions, they still conflict.

4. **"All task coefficients should be equal."** No. You can tune λ per task. If coding is more important than medical, set λ_coding = 0.5 and λ_medical = 0.2.

5. **"Task arithmetic only works for two tasks."** It scales to any number of tasks. The formula is linear, so 10 task vectors sum just as easily as 2.

---

### Where It Is Used in Our Code

`src/phase43/phase43_model_merging.py` — The `task_arithmetic_merge()` function computes task vectors as `W_finetuned - W_base`, then adds a weighted combination back to the base model. We compare simple averaging vs. task arithmetic on multi-task performance.

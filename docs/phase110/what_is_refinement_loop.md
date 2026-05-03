## What Is a Refinement Loop?

---

### The Problem

Even capable models produce first drafts with errors: incorrect facts, logical gaps, awkward phrasing, and missed constraints. A human writer does not submit their first draft; they revise, fact-check, and polish. Yet most inference pipelines accept the model's initial output without iteration, treating generation as a one-shot process. How do you systematically improve an output after it has been generated, using the same model to critique and revise its own work?

---

### Definition

A **Refinement Loop** is an inference-time strategy where a model generates an initial output, then critiques and revises it over multiple iterations. Each pass can correct errors, add detail, restructure arguments, or improve style until a stopping criterion is met.

**How it works:**
```
Draft 1: Generate initial output
Review: Model critiques its own output (find errors, gaps, weak points)
Draft 2: Revise based on critique
Repeat for K iterations or until no further improvement detected
Result: higher-quality output from the same model without retraining
```

**Key techniques:**
- **Self-critique prompting:** instruct the model to find its own errors and identify missing information
- **Iterative revision:** generate a new output conditioned on both the previous draft and the critique
- **Stopping criteria:** max iterations, convergence detection, or a fixed inference budget

**Why this matters:**
- Mimics human editing and improves factual consistency without any gradient updates
- Can be applied to any generation task: summarization, translation, code, and reasoning
- Often outperforms single-pass generation at the same model size

---

### Real-Life Analogy

A refinement loop is like writing an essay. Your first draft is rough: the argument wanders, examples are thin, and there are typos. You read it, mark errors and weak points, then rewrite sections. The second draft is clearer. A third pass tightens the prose and fixes a misattributed quote. You stop when improvements become marginal.

The trade-off is time. Three drafts take three times as long as one. A refinement loop automates this process, and the cost is inference latency. If you have a deadline, you might submit the first draft. If quality matters more than speed, you iterate. The same model acts as both author and editor, switching hats via prompting.

---

### Tiny Numeric Example

**Summarization task, source text 500 words.**

**Single-pass output:**
```
Word count: 87
Factual errors: 3 (misattributed quote, wrong date, missing qualifier)
Readability score: 62
```

**After 1 refinement iteration:**
```
Word count: 82
Factual errors: 1 (wrong date corrected, misattribution fixed)
Readability score: 71
```

**After 2 refinement iterations:**
```
Word count: 79
Factual errors: 0
Readability score: 76
```

**After 3 refinement iterations:**
```
Word count: 78
Factual errors: 0
Readability score: 77
Marginal gain: +1 readability (not worth the extra compute)
```

**Optimal stopping point: 2 iterations for this example.**

Diminishing returns set in after the second pass, and a fixed budget of 2 iterations balances quality and cost.

---

### Common Confusion

1. **"Refinement loops are the same as RLHF."** RLHF updates model weights during training using human preference data. Refinement loops happen at inference time and do not change any model weights.

2. **"Refinement always converges to a better output."** Poorly designed loops can oscillate between versions or introduce new errors; convergence to higher quality is not guaranteed.

3. **"More iterations are always better."** Diminishing returns set in after 2-4 iterations, and later passes may reintroduce errors or over-polish the output into generic prose.

4. **"Refinement requires a separate critic model."** A single model can act as both generator and critic through prompt switching or role prompting, though a dedicated critic can improve results.

5. **"Refinement only helps long-form generation."** It improves short outputs too: code snippets, math steps, single-sentence translations, and even multiple-choice reasoning benefit from self-correction.

6. **"Refinement loops are deterministic."** They use sampling during generation and critique, so the same input can produce different refinement trajectories across runs.

7. **"Refinement is the same as test-time compute in general."** Refinement is one form of test-time compute, but test-time compute also includes search, verification, and ensemble methods that do not involve iterative revision.

---

### Where It Is Used in Our Code

`src/phase110/phase110_test_time_compute.py` — We simulate best-of-N sampling and show how selecting the best candidate from multiple generations acts as a single-pass refinement mechanism. While our NumPy implementation focuses on best-of-N selection rather than iterative text revision, the underlying principle is identical: spend extra inference compute to improve output quality beyond what a single generation can achieve.

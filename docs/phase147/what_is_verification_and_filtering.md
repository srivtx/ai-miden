## What Is Verification and Filtering?

---

### The Problem

A synthetic data generator can produce a million examples in an afternoon. But quantity is meaningless if the examples are wrong. A generated math problem with an incorrect solution teaches the model to make that exact mistake. A generated code snippet with a syntax error teaches the model broken patterns. A generated reasoning chain that looks logical but contains a subtle fallacy teaches the model to hallucinate confidently. Without verification and filtering, synthetic data is a poison, not a nutrient.

---

### Definition

**Verification and Filtering** is the process of automatically checking synthetic data for correctness, quality, and diversity, then discarding examples that fail those checks before they enter the training set. It is the quality-control gate of the synthetic data pipeline. Filtering is not an afterthought; it is the majority of the work.

**How it works:**
```
Generated data  →  Correctness check  →  Quality score  →  Diversity check  →  Training set
                      ↓                      ↓                  ↓
                   Rejected              Rejected           Rejected
```

**Key techniques:**
- **Rule-based verification:** using calculators, compilers, unit tests, and proof checkers to verify exact correctness
- **Reward model scoring:** training a separate model to predict human preferences, then keeping only high-scoring examples
- **Self-consistency:** generating multiple answers to the same question and keeping only the majority answer
- **Deduplication:** removing near-duplicate examples using embedding similarity or n-gram overlap
- **Length and format filtering:** rejecting outputs that are too short, too long, or malformed

**Why this matters:**
- In production pipelines, 70-90% of generated data is filtered out
- A small set of verified examples often trains a better model than a massive set of unverified examples
- Verification is what separates synthetic data that improves models from synthetic data that causes model collapse
- Filtering is computationally expensive, but far cheaper than training on bad data and discovering the problem later

---

### Real-Life Analogy

A publishing house editing manuscripts.
- **Generation:** An AI writing tool produces 1,000 novel drafts in a week. Most have plot holes, factual errors, or repetitive themes.
- **Verification:** Fact-checkers verify historical dates. Editors check for internal consistency. A plagiarism detector scans for copied passages.
- **Filtering:** Out of 1,000 drafts, 200 pass fact-checking. Of those, 80 score above the quality threshold. Of those, 40 are sufficiently different from each other. Only 40 are sent to print.
- **The lesson:** The publisher's value is not the generator. It is the editorial pipeline that turns raw drafts into books people want to read. Synthetic data pipelines are editorial departments for machines.

---

### Tiny Numeric Example

**Scenario:** You generate 5,000 synthetic multiple-choice science questions.

**Raw batch quality:**
```
Total generated: 5,000
Correct answers (verified against textbook): 3,200 (64%)
Well-formatted (4 options, one clearly correct): 2,800 (56%)
Unique (not near-duplicates): 2,100 (42%)
```

**After each filter:**
```
Filter 1 — Correctness:    keep 3,200, discard 1,800
Filter 2 — Format:         keep 2,600, discard 600
Filter 3 — Diversity:      keep 1,900, discard 700
Final training set: 1,900 examples (38% of original)
```

**Model accuracy on a human-written test:**
```
Trained on all 5,000 raw:           51% accuracy
Trained on 3,200 correct only:      58% accuracy
Trained on 1,900 filtered:          71% accuracy

The 1,900 filtered examples outperform the 5,000 raw examples by 20 points.
```

**The cost:**
```
Filtering compute:  2 GPU-hours
Training on bad data + retraining:  20 GPU-hours + 2 days of debugging
Verification pays for itself 10× in saved retraining time.
```

---

### Common Confusion

1. **"Verification is just running a spell-checker."** Spell-checking catches typos. Verification catches logical errors, mathematical mistakes, code bugs, and factual hallucinations. It often requires domain-specific tools: Python interpreters, symbolic math engines, or physics simulators.

2. **"Filtering is a waste of compute."** Filtering is 80% of the pipeline's compute, but it saves far more compute downstream. Training on bad data requires retraining, which costs 10-100× more than filtering. Filter early, filter aggressively.

3. **"A single filter is enough."** Different filters catch different failure modes. A correctness filter does not catch boring, repetitive outputs. A diversity filter does not catch incorrect answers. You need a cascade of filters, each specialized for one failure mode.

4. **"Verification guarantees correctness."** Automated verification is only as good as the verifier. A buggy unit test will pass buggy code. A flawed calculator will validate wrong math. Verifiers themselves need to be tested and audited.

5. **"Filtering reduces dataset diversity."** Aggressive deduplication can remove valid variations. But smart diversity filtering keeps the semantic variety while removing literal copies. The goal is to remove redundancy, not variety. Embedding-based clustering is one way to preserve diversity while controlling duplication.

6. **"You can verify everything."** Some outputs are inherently subjective: creative writing, open-ended advice, stylistic preferences. For these, you use reward models or human preference data instead of hard verifiers. Not all filtering is binary pass/fail.

7. **"Filtering is a solved problem."** As models improve, they generate more plausible but subtly wrong outputs that slip past existing filters. Verification is an arms race. Every new model requires updated verifiers.

---

### Where It Is Used in Our Code

`src/phase147/phase147_synthetic_concepts.py` — We generate synthetic classification data with a hidden "ground truth" quality score. We apply three filters — correctness, diversity, and length — and show how each filter raises the average quality of the remaining data. We plot the quality distribution before and after filtering, and we demonstrate that a model trained on the filtered subset achieves higher accuracy than one trained on the full raw set.

`src/phase147/phase147_synthetic_colab.py` — We generate synthetic instruction-response pairs with a 3B model, score each pair with a composite heuristic (response length, lexical diversity, and format correctness), and compare fine-tuning outcomes on the top 50%, top 10%, and full unfiltered sets. The results confirm that aggressive filtering produces the best model.

(End of file)

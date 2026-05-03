## What Is Perplexity Filtering?

---

## The Problem

Some documents are grammatically correct but still worthless for training: random word salads, machine-generated spam, or text in the wrong language. Simple length and punctuation filters miss these because the surface statistics look normal. How do you detect linguistically anomalous text that passes basic heuristics?

---

## Definition

**Perplexity filtering** uses a reference language model to compute the perplexity of each document. Documents with extremely high perplexity (the model is very surprised) or extremely low perplexity (the model has memorized them) are flagged for removal.

**How it works:**
```
Perplexity computation:
  1. Reference model computes P(token_i | token_1 ... token_{i-1}) for every token
  2. Average negative log-likelihood = -mean(log P(token_i))
  3. Perplexity = exp(average negative log-likelihood)

Filtering decision:
  1. Compute perplexity on a held-out validation set to establish baseline
  2. Set lower_bound (e.g., 5th percentile) and upper_bound (e.g., 95th percentile)
  3. For each candidate document:
       if perplexity < lower_bound → flag (possible memorization / boilerplate)
       if perplexity > upper_bound → flag (likely garbage / wrong language)
       else → keep
```

**Why this matters:**
- Perplexity catches subtle garbage that heuristics miss, such as fluent but semantically empty text.
- It provides a continuous quality score rather than a hard rule, allowing fine-grained control over the filter aggressiveness.
- Low-perplexity outliers often indicate boilerplate or memorized test data, which also harm training.

---

## Real-Life Analogy

A fluent English speaker reading a sentence like "Colorless green ideas sleep furiously" is not surprised by the grammar but is surprised by the meaning. Perplexity measures that surprise. A document that makes the model far more surprised than average is probably low quality.

Imagine a seasoned detective interviewing witnesses. Most witnesses describe events with predictable vocabulary: "I saw a man in a red coat walk toward the bank." One witness says, "The angular pineapple orchestrated silence beneath twelve moons." Every word is English, and the grammar is flawless, but the sentence conveys no coherent information. The detective flags this statement as unreliable not because of spelling errors, but because the semantic content is anomalous. Perplexity filtering behaves the same way: it flags text that is linguistically strange even when it passes surface-level checks.

**The trade-off:** Perplexity filtering is computationally expensive. Running a forward pass on every candidate document adds significant preprocessing cost. It is usually applied as a secondary filter after cheaper heuristics have already removed obvious junk.

---

## Tiny Numeric Example

**Reference model baseline on held-out set:**

| Metric | Value |
|--------|-------|
| Mean perplexity | 50 |
| Standard deviation | 15 |
| Lower bound (5th percentile) | 25 |
| Upper bound (95th percentile) | 80 |

**Candidate documents:**

| Document | Perplexity | Decision | Reason |
|----------|-----------|----------|--------|
| A: Well-written news article | 48 | Keep | Within normal range |
| B: Random word salad | 2,000 | Remove | 40x above mean |
| C: Repeated legal boilerplate | 12 | Remove | Below lower bound |
| D: Valid physics paper | 95 | Keep | Slightly above mean but within tolerance |

- Document B is removed because the reference model is extremely surprised by its token sequences.
- Document C is removed because the model finds it too predictable, suggesting memorized or templated text.
- Estimated false positive rate for valid technical documents: ~5% if upper bound is set at 95th percentile.

---

## Common Confusion

1. **"High perplexity always means bad text."** It does not. A valid physics paper may contain rare technical terms that surprise a general-domain model. Domain matters.

2. **"Perplexity filtering is a spam detector."** It is not. It measures linguistic surprise, not intent or topic. A poem may have high perplexity and be high quality.

3. **"The reference model does not matter."** It matters enormously. A model trained on tweets will score legal documents poorly, and vice versa.

4. **"Perplexity filtering is cheap."** It is not. Running a forward pass on every candidate document adds significant preprocessing cost and is usually deferred until after heuristic filtering.

5. **"Perplexity is accuracy."** It is not. Perplexity is an inverse probability measure reflecting model surprise, not a direct quality label.

6. **"Only high perplexity documents should be removed."** Low perplexity outliers also matter. Extremely low perplexity often signals boilerplate, duplicate memorization, or test-set leakage.

7. **"Perplexity filtering replaces all other filters."** It does not. It complements heuristic filtering. The cheapest filters run first to remove obvious junk; perplexity runs on the remainder to catch subtle anomalies.

---

## Where It Is Used in Our Code

`src/phase89/phase89_data_pipelines.py` — We mention perplexity as a conceptual quality signal. While our toy example uses simpler heuristics (length and punctuation ratio), the pipeline structure is identical: score each document, set a threshold, and keep only those that pass. The script demonstrates the scoring-and-thresholding pattern that perplexity filtering applies at a deeper linguistic level.

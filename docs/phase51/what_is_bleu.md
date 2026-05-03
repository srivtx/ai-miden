## What Is BLEU?

---

### The Problem

A translation model generates: "The cat sat on the mat."
The reference translation is: "The cat sat on the rug."
Is this good? "Mat" and "rug" are similar but not identical. How do you score generated text when there are many valid ways to say the same thing?

---

### Definition

**BLEU (Bilingual Evaluation Understudy)** measures the n-gram overlap between generated text and one or more reference texts.

**How BLEU works:**
1. Count matching n-grams (sequences of N words) between generated and reference
2. Compute precision for each n-gram size (1-gram, 2-gram, 3-gram, 4-gram)
3. Take the geometric mean of these precisions
4. Apply a brevity penalty if the generated text is too short

**Example with 1-grams:**
```
Generated: "the cat sat"
Reference: "the cat sat on the mat"

Matching 1-grams: "the", "cat", "sat" = 3 matches
Total 1-grams in generated: 3
Precision = 3/3 = 1.0
```

**Example with 2-grams:**
```
Generated 2-grams: "the cat", "cat sat"
Reference 2-grams: "the cat", "cat sat", "sat on", "on the", "the mat"

Matches: "the cat", "cat sat" = 2 matches
Precision = 2/2 = 1.0
```

**BLEU score:**
```
BLEU = brevity_penalty × exp(0.25 × (log(p1) + log(p2) + log(p3) + log(p4)))
```

Scores range from 0 to 1 (or 0 to 100). Human translations typically score 30-50.

---

### Real-Life Analogy

Grading a paraphrase.
- **Teacher:** "Write a summary of this article."
- **Student A:** Writes a perfect summary using entirely different words.
- **Student B:** Copies phrases directly from the article.

BLEU rewards Student B because it matches n-grams. Student A gets a low score despite being better. This is BLEU's limitation — it cannot recognize semantic equivalence, only surface overlap.

Despite this flaw, BLEU is widely used because it is fast, automatic, and correlates reasonably with human judgment for machine translation.

---

### Tiny Numeric Example

**Generated:** "the quick brown fox"
**Reference:** "the fast brown fox jumped"

**1-gram precision:**
```
Matches: "the", "brown", "fox" = 3
Total in generated: 4
p1 = 3/4 = 0.75
```

**2-gram precision:**
```
Generated 2-grams: "the quick", "quick brown", "brown fox"
Reference 2-grams: "the fast", "fast brown", "brown fox", "fox jumped"
Matches: "brown fox" = 1
p2 = 1/3 = 0.333
```

**Brevity penalty:**
```
generated_length = 4, reference_length = 5
BP = 1.0 (generated is shorter but not too short)
```

**BLEU (using p1 and p2 only):**
```
BLEU = 1.0 × exp(0.5 × (log(0.75) + log(0.333)))
     = exp(0.5 × (-0.288 + -1.099))
     = exp(-0.694)
     = 0.50
```

A score of 0.50 indicates moderate quality.

---

### Common Confusion

1. **"High BLEU means perfect translation."** No. BLEU only measures n-gram overlap. A translation with BLEU 40 can be better than one with BLEU 60 if the latter is unnatural.

2. **"BLEU works for all text generation."** It was designed for translation. For creative writing or dialogue, it is a poor metric because valid outputs vary widely.

3. **"BLEU requires multiple references."** It works with one reference, but multiple references give a fairer score (more valid paraphrases are captured).

4. **"BLEU is the best metric."** Modern metrics like BERTScore (semantic similarity using BERT embeddings) often correlate better with human judgment.

5. **"BLEU score of 100 is achievable."** Only if the generated text exactly matches the reference. Human translators rarely score above 50.

---

### Where It Is Used in Our Code

`src/phase51/phase51_evaluation_metrics.py` — We compute BLEU scores for generated sentences against reference translations, showing how n-gram overlap measures generation quality.

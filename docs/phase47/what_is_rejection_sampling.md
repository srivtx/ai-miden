## What Is Rejection Sampling?

---

### The Problem

When a model generates synthetic data, most outputs are mediocre and some are wrong. How do you automatically select only the best outputs for training, without human judgment?

---

### Definition

**Rejection sampling** is a filtering technique where generated outputs are scored by a verifier, and only outputs passing a quality threshold are kept for training.

**The process:**
```
For each prompt:
  1. Generate N candidate outputs from the model
  2. Score each output with a verifier (correctness, safety, style, etc.)
  3. Keep only outputs with score > threshold
  4. Use kept outputs as training data
```

**Types of verifiers:**
- **Hard verifier:** Unit tests for code, exact match for math, parser for structured data
- **Soft verifier:** A reward model scoring quality, a classifier detecting toxicity, perplexity scoring fluency
- **Self-consistency:** Generate multiple answers and keep the majority-voted answer (used in math reasoning)

**Why rejection sampling is powerful:**
- It turns a mediocre generator into a high-quality dataset producer
- The threshold controls the quality/quantity trade-off
- It works at massive scale (billions of samples)
- It is the key ingredient that makes synthetic data viable

---

### Real-Life Analogy

A pearl farm.
- **Generation:** Oysters produce pearls. Most are misshapen, small, or discolored. Only 1 in 1000 is gem-quality.
- **Rejection sampling:** The farmer inspects every pearl and discards the bad ones. Only gem-quality pearls go to market.
- **Result:** The market sees only perfect pearls. The farm's reputation is based on the filtered output, not the average oyster.

If the farmer sold every pearl (no rejection sampling), customers would be disappointed. The filter is what makes the product valuable.

---

### Tiny Numeric Example

**Task:** Generate valid Python functions that add two numbers.

**Model generates 20 candidates:**
```
Candidate 1:  "def add(a, b): return a + b"          -> VALID
Candidate 2:  "def add(a, b): return a * b"          -> WRONG (syntax valid, logic wrong)
Candidate 3:  "def add(a, b): return a +"            -> INVALID (syntax error)
Candidate 4:  "def add(a, b): return sum([a, b])"   -> VALID
...
Candidate 20: "def add(a, b): print(a + b)"         -> INVALID (no return)
```

**Hard verifier (run code + check output):**
```
Valid candidates: 1, 4, 7, 12, 15, 18  (6 out of 20 = 30% pass rate)
```

**Training dataset:**
```
Use only the 6 valid functions as training data
```

**Impact of N (number of candidates):**
```
N = 1:  30% chance of getting valid data per prompt
N = 4:  76% chance of at least one valid candidate
N = 10: 97% chance of at least one valid candidate
N = 20: 99.9% chance of at least one valid candidate
```

By generating more candidates and filtering, you guarantee high-quality training data.

---

### Common Confusion

1. **"Rejection sampling wastes compute."** Yes, you throw away bad outputs. But the cost of generating 10 candidates and filtering is still much cheaper than human labeling.

2. **"Rejection sampling only works with hard verifiers."** Soft verifiers (reward models, perplexity) work too. The threshold just needs to correlate with true quality.

3. **"Higher threshold always means better data."** Yes, but you get fewer samples. The optimal threshold balances quality and quantity.

4. **"Rejection sampling fixes a bad model."** No. It extracts the best from a mediocre model. The model itself still needs training to improve.

5. **"Rejection sampling is the same as beam search."** Beam search finds the single best output during inference. Rejection sampling generates many independent outputs and filters them for training data.

---

### Where It Is Used in Our Code

`src/phase47/phase47_synthetic_data.py` — A model generates multiple candidate solutions to arithmetic problems. An automatic checker (hard verifier) rejects incorrect answers. Only correct solutions are used for training. We show that rejection sampling dramatically improves training data quality.

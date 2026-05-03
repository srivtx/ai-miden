## What Is Acceptance Sampling?

---

### The Problem

The draft model proposes a token, but the target model might disagree. If we just accept the draft's suggestion when the target is unsure, we change the output distribution. If we always reject and resample from the target, we waste the draft's work. How do we decide whether to accept or reject while preserving the exact target distribution?

---

### Definition

**Acceptance sampling** is the statistical procedure that guarantees speculative decoding produces **exactly** the same distribution as autoregressive sampling from the target model alone.

**For a proposed token t:**
```
p_accept = min(1, P_target(t) / P_draft(t))
```

**If accepted:** Use token t.

**If rejected:** Sample a new token from the "residual" distribution:
```
P_resample(t') = normalize(max(0, P_target(t') - P_draft(t')))
```

**Why this preserves the target distribution:**

Consider any token x. Under speculative decoding, the probability of generating x is:
```
P_output(x) = P_draft(x) * p_accept(x) + P_reject * P_resample(x)
```

Where:
- `P_draft(x) * p_accept(x)` = probability draft proposes x AND target accepts
- `P_reject * P_resample(x)` = probability draft is rejected AND resample produces x

When you work out the math, this simplifies to exactly `P_target(x)`. This is a beautiful result: the output distribution is mathematically identical to sampling from the target alone.

---

### Real-Life Analogy

A quality control inspector checking products on an assembly line.
- **Simple acceptance:** Inspector randomly spot-checks 10% of products. This changes the effective defect rate (some defects slip through).
- **Proper acceptance sampling:** Inspector uses a calibrated rule: if the machine's internal sensor says a product is good with 95% confidence, accept it. If the sensor says 80% confidence, accept it with probability 80/95. If rejected, use a more sensitive test. The overall defect rate matches what you would get if you tested every product with the sensitive test.

---

### Tiny Numeric Example

**Vocabulary:** {A, B}

**Draft probabilities:**
```
P_draft(A) = 0.7, P_draft(B) = 0.3
```

**Target probabilities:**
```
P_target(A) = 0.5, P_target(B) = 0.5
```

**For token A:**
```
p_accept(A) = min(1, 0.5 / 0.7) = 0.714

If draft proposes A:
  - With probability 0.714: accept A
  - With probability 0.286: reject, resample from residual
```

**Residual distribution after rejecting A:**
```
P_resample(A) = max(0, 0.5 - 0.7) = 0  (normalized: 0)
P_resample(B) = max(0, 0.5 - 0.3) = 0.2  (normalized: 1.0)
```

So if rejected, we always sample B.

**Total probability of outputting A:**
```
P_output(A) = P_draft(A) * p_accept(A) + P_reject * P_resample(A)
            = 0.7 * 0.714 + 0.3 * 0
            = 0.5
```

**Total probability of outputting B:**
```
P_output(B) = P_draft(B) * p_accept(B) + P_reject * P_resample(B)

For B: p_accept(B) = min(1, 0.5 / 0.3) = 1.0
P_reject_B = 1 - 1.0 = 0

P_output(B) = 0.3 * 1.0 + 0.7 * 0.286 * 1.0
            = 0.3 + 0.2
            = 0.5
```

**Result:** P_output(A) = 0.5, P_output(B) = 0.5 — exactly matching P_target!

---

### Common Confusion

1. **"Acceptance sampling is just thresholding."** No. It is a carefully designed statistical procedure that preserves the exact target distribution. Simple thresholding would bias the outputs.

2. **"If P_target > P_draft, we always accept."** Yes, and this makes sense: if the target thinks the token is MORE likely than the draft did, the target has no objection.

3. **"Rejection means the draft was wrong."** Not exactly. Rejection means the target disagrees with the draft's confidence. The token might still be good — just not as good as the draft thought.

4. **"The resampling distribution is complicated."** In practice, it is simple: subtract the draft probabilities from the target probabilities, clip at zero, and renormalize. This gives a distribution over "what the target thinks but the draft missed."

5. **"Acceptance sampling works for any sampling temperature."** Yes, but the acceptance rate decreases as temperature increases (more randomness = more disagreement). At temperature=0 (greedy), acceptance is deterministic and highest.

---

### Where It Is Used in Our Code

`src/phase36/phase36_speculative_decoding.py` — The `accept_token()` function implements the acceptance criterion and resampling logic. We verify empirically that the output distribution matches pure target sampling.

## What Is Speculative Decoding?

---

### The Problem

Autoregressive text generation produces exactly one token per forward pass. To generate a 1000-token response, you need 1000 sequential forward passes through the model. Even with a KV cache, each pass takes the same amount of time. There is no parallelism. How do you generate multiple tokens without running the full model multiple times?

---

### Definition

**Speculative decoding** uses a small, fast "draft model" to predict multiple future tokens in parallel. The large, slow "target model" then verifies all predictions in a single forward pass. Correct predictions are accepted; incorrect ones are corrected.

**The algorithm:**
```
1. Draft model generates K candidate tokens quickly
2. Target model runs ONE forward pass to score all K candidates
3. Compare draft probabilities vs. target probabilities:
   - If target agrees draft was likely: accept token
   - If target disagrees: reject and sample a correction
4. Resume from first rejected position (or after K if all accepted)
```

**Critical guarantee:** The output distribution is **exactly identical** to sampling from the target model alone. No quality loss. Pure speedup.

---

### Real-Life Analogy

A student takes a practice exam and writes answers for all questions quickly. The teacher then grades the entire exam in one pass, marking which answers are correct and which need correction. The student is fast but sometimes wrong; the teacher is slow but authoritative.

Without speculative decoding: The teacher grades one question, the student answers the next, the teacher grades that one... 1000 sequential rounds.

With speculative decoding: The student answers all 1000 questions in 10 minutes. The teacher grades all 1000 in 60 minutes. Total: 70 minutes instead of 1000+ minutes.

---

### Tiny Numeric Example

**Vocabulary:** 3 tokens {A, B, C}

**Draft model probabilities for next token:**
```
P_draft(A) = 0.6, P_draft(B) = 0.3, P_draft(C) = 0.1
```

**Target model probabilities for same position:**
```
P_target(A) = 0.5, P_target(B) = 0.4, P_target(C) = 0.1
```

**Step 1 — Draft samples token A:**
```
Draft proposes: A
```

**Step 2 — Acceptance check:**
```
p_accept = min(1, P_target(A) / P_draft(A))
         = min(1, 0.5 / 0.6)
         = 0.833
```

**Step 3 — Flip a coin (random uniform):**
```
If random() < 0.833: accept A
If random() >= 0.833: reject A, sample from corrected distribution
```

**Why this works:**
- If target thinks A is MORE likely than draft: always accept (target agrees)
- If target thinks A is LESS likely than draft: accept proportionally
- This preserves the exact target distribution mathematically

---

### Common Confusion

1. **"Speculative decoding changes the model's outputs."** No. It produces **exactly** the same distribution as autoregressive sampling from the target model. It is purely an acceleration technique with zero quality loss.

2. **"The draft model needs to be almost as good as the target."** No. The draft only needs to get high-probability tokens right. A 100M parameter model can effectively draft for a 70B model because easy tokens ("the", "and") are easy for everyone.

3. **"Speculative decoding helps with batch inference."** Not much. It helps most with batch_size=1 (single user latency). At high batch sizes, the target model is already GPU-saturated and adding a draft model may not help.

4. **"You need a completely separate model for drafting."** Not necessarily. Medusa adds multiple prediction heads to the target model itself. Lookahead decoding uses the model's own n-gram cache as the draft.

5. **"All K draft tokens are either accepted or rejected together."** No. Tokens are checked sequentially from left to right. The first rejected token triggers a resample; everything after it is discarded. So you might accept 3 tokens, reject the 4th, and restart.

---

### Where It Is Used in Our Code

`src/phase36/phase36_speculative_decoding.py` — Simulates a draft model and target model over a small vocabulary. Shows acceptance/rejection decisions, compares speedup, and verifies that the output distribution matches pure target sampling.

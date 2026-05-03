## What Is a Draft Model?

---

### The Problem

In speculative decoding, you need something to generate candidate tokens quickly. The target model is too slow to use for this. But you cannot just guess randomly — the candidates need to be plausible enough that the target model will accept them. What makes a good draft model?

---

### Definition

A **draft model** is a small, fast neural network (or even a non-neural method like n-gram matching) that approximates the target model's distribution over next tokens. Its job is to generate K candidate tokens that the target model will likely accept.

**Ideal properties:**
- Much faster than the target (10–100× speedup)
- High agreement with the target on high-probability tokens
- Does not need to be perfect — just needs to match the "easy" predictions

**Common choices:**
- Smaller variant of same architecture (Llama 7B drafting for Llama 70B)
- Distilled model trained to mimic the target
- N-gram cache from recent context (Lookahead Decoding)
- Multiple prediction heads added to the target model itself (Medusa)

---

### Real-Life Analogy

A junior editor (draft model) and a senior editor (target model) working on a manuscript.
- The junior editor reads quickly and marks suggested changes throughout the chapter.
- The senior editor reviews all suggestions in one pass, approving most and correcting a few.
- The junior does not need to be as skilled as the senior. They just need to know basic grammar and style. The senior catches subtle errors.

The key: the junior is fast enough that even with some mistakes, the combined process is faster than the senior working alone.

---

### Tiny Numeric Example

**Target model** (large, accurate):
```
P_target("the") = 0.45
P_target("a")   = 0.30
P_target("an")  = 0.15
P_target("this") = 0.10
```

**Draft model** (small, approximate):
```
P_draft("the") = 0.50
P_draft("a")   = 0.25
P_draft("an")  = 0.15
P_draft("this") = 0.10
```

**Agreement analysis:**
- Both rank "the" as most likely (agree)
- Both rank "a" as second most likely (agree)
- Exact probabilities differ slightly, but rankings match

**If draft samples "the":**
```
p_accept = min(1, 0.45 / 0.50) = 0.90
```
90% chance of acceptance. The draft model is doing its job.

**If draft samples "a":**
```
p_accept = min(1, 0.30 / 0.25) = 1.0
```
100% chance of acceptance. The target agrees this was a good guess.

---

### Common Confusion

1. **"The draft model must be from the same family as the target."** Not required, but it helps. Same-family models tend to agree more. However, even a simple n-gram model can achieve 30–50% acceptance rate, which still provides speedup.

2. **"A bigger draft model is always better."** Not necessarily. A draft model that is too large slows down the draft phase. The sweet spot is usually 1/10 to 1/100 the size of the target. The goal is fast drafting, not perfect drafting.

3. **"The draft model needs its own KV cache."** Yes. And on rejection, both the draft and target KV caches must be rolled back to the last accepted position. This adds complexity to the implementation.

4. **"Draft models are only for text generation."** No. Speculative decoding has been applied to image generation (diffusion models), speech synthesis, and any autoregressive generative model.

5. **"Medusa eliminates the need for a draft model."** Yes, by making the target model draft for itself. Medusa adds multiple prediction heads to the target model. During inference, all heads generate candidates in one forward pass. This avoids loading a second model but requires training the extra heads.

---

### Where It Is Used in Our Code

`src/phase36/phase36_speculative_decoding.py` — A simple n-gram model serves as the draft. It is much faster than the target model and achieves reasonable acceptance rates on high-probability tokens.

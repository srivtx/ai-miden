## What Is H2O (Heavy-Hitter Oracle)?

---

### The Problem

In a long document, not every token is equally important. The word "the" appears hundreds of times and receives very little attention. A person's name appears once but is attended to repeatedly by every subsequent pronoun. If you are forced to drop tokens from the KV cache to save memory, how do you know which ones matter? A naive approach — evicting the oldest tokens — will delete the protagonist's name from the first paragraph and destroy coherence. H2O solves this by treating attention as a vote: tokens that accumulate high attention scores across many generation steps are "heavy hitters," and they are the ones that must be kept.

---

### Definition

**H2O (Heavy-Hitter Oracle)** is an eviction policy for KV cache compression that maintains a local attention window plus a set of global "heavy-hitter" tokens identified by their cumulative attention scores. The model attends to all tokens in the local window and to the heavy hitters, approximating full attention with far fewer KV pairs.

**How it works:**
```
For each generation step:
  1. Compute attention scores over all cached tokens.
  2. Accumulate each token's score into a running total (the "heavy-hitter score").
  3. Evict tokens that are BOTH outside the local window AND not in the top-k heavy hitters.
  4. Retain: local_window_size tokens + heavy_hitter_budget tokens.
```

**Key properties:**
- **Local attention:** Recent tokens are always kept (sliding window) because they are critical for grammatical coherence.
- **Heavy-hitters:** Tokens with highest cumulative attention are kept globally because they carry semantic weight.
- **Theoretical guarantee:** H2O approximates full attention with bounded error because the heavy-hitters capture the majority of the attention mass.

**Why this matters:**
- A 70B model on 500K tokens can run with only 10% of the KV cache retained.
- The heavy-hitter set stabilizes after a few thousand tokens; most evictions happen in the long tail of low-attention tokens.
- It requires no training; it is a pure inference-time algorithm.

---

### Real-Life Analogy

Imagine a journalist covering a month-long political convention with a notebook that only has 20 pages.
- **Full attention:** The journalist tries to write down every speech, every hallway conversation, and every lunch order. The notebook is full by day two. After that, the journalist has no reference material and starts making up facts.
- **H2O:** The journalist reserves the last 5 pages for today's notes (the local window). The other 15 pages are reserved for the most-quoted speakers, the scandal revelations, and the final vote counts (the heavy hitters). When a new speaker takes the stage, the journalist checks: is this person already in the heavy-hitter section? If yes, add a line. If no, and the speaker is boring, skip them. The notebook never exceeds 20 pages, but the journalist still writes an accurate article because the important facts are always available.
- **The trade-off:** The journalist might miss a subtle comment from a minor delegate. But the alternative — a full notebook by day two — guarantees failure. H2O is the optimal strategy for bounded memory.

---

### Tiny Numeric Example

**Cumulative attention scores after processing 20 tokens:**
```
Token:    t1(name)  t2(the)   t3(met)   t4(Jane)  t5(in)    t6(Paris)
Score:    4.50      0.30      0.80      3.20      0.20      2.10

Token:    t7(on)     t8(Monday) t9(.)    t10(She)  t11(went) t12(to)
Score:    0.10       1.40       0.05     2.80      0.60      0.40
```

**Eviction policy: local window = 4, heavy hitters = 4**
```
Local window (most recent):   t9, t10, t11, t12
Heavy hitters (top 4 scores): t1 (4.50), t4 (3.20), t10 (2.80), t6 (2.10)
Retained total: 8 tokens (t1, t4, t6, t9, t10, t11, t12, plus one duplicate)
After deduplication: t1, t4, t6, t9, t10, t11, t12 = 7 tokens
```

**Evicted tokens:** t2, t3, t5, t7, t8

**Next-token prediction at step 21:**
```
Full cache (all 20 tokens):     probability on "London" = 0.15
H2O cache (7 tokens):           probability on "London" = 0.13
Sliding window only (4 tokens): probability on "London" = 0.04
```

**The shift:** The heavy hitters (t1, t4, t6) provide enough global context that the model still knows the story is about a person in a city. A pure sliding window forgets the protagonist entirely.

---

### Common Confusion

1. **"H2O requires training a separate model to predict importance."** No. H2O uses the attention scores that the model already computes during inference. There is no extra training step.

2. **"Heavy hitters are just the most frequent tokens."** Frequency and attention are different. The word "the" is frequent but receives low attention. A rare name like "Zaphod" may receive high attention every time a pronoun refers to it.

3. **"The local window and heavy-hitters are disjoint sets."** They can overlap. A recent token can also be a heavy hitter. The union of both sets is what is retained.

4. **"H2O works by pruning heads or layers."** No. H2O prunes tokens from the KV cache. It does not change the model architecture. All heads and all layers still run; they just see a compressed context.

5. **"Cumulative attention scores grow forever and overflow."** In practice, scores are normalized per step, and the cumulative sum can be decayed or kept in log-space. Implementations use simple running averages to prevent overflow.

6. **"H2O is only for decoder-only transformers."** While it was designed for autoregressive decoding, the heavy-hitter principle applies to any attention mechanism where some tokens dominate the attention mass.

7. **"H2O guarantees no accuracy loss."** It does not. It guarantees bounded approximation error, but on some tasks — especially those requiring exact recall of distant details — accuracy will drop. The trade-off is explicit and tunable via the heavy-hitter budget.

---

### Where It Is Used in Our Code

`src/phase113/phase113_kv_compression_concepts.py` — We simulate a sequence of 1,024 tokens with synthetic attention scores, implement H2O eviction by accumulating attention weights per token and keeping a local window plus top-k heavy hitters, and demonstrate that H2O approximates full attention significantly better than random or age-based eviction.

`src/phase113/phase113_kv_compression_colab.py` — We load Llama-3.2-3B-Instruct and implement H2O compression during generation on a real long-context prompt, measuring peak memory and generation speed. We show that heavy-hitter retention preserves coherence while cutting KV cache size in half.

(End of file - total 97 lines)

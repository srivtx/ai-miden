## What Is SnapKV?

---

### The Problem

H2O and other eviction policies decide which tokens to keep by looking at past attention scores. But what if the model's attention pattern changes between layers? A token that is unimportant in early layers might become critical in deeper layers, or vice versa. By the time you have observed that a token is important, you may have already evicted it. Worse, some tokens are only attended to by future layers — you cannot know they are important from past scores alone. SnapKV solves this by observing attention patterns during the prefill phase (when the full prompt is available) and using those observations to decide which tokens to keep for the entire generation.

---

### Definition

**SnapKV** is a KV cache compression method that observes attention patterns across all layers during the prefill phase, identifies which tokens will be attended to in the future, and compresses the cache before generation begins by pooling attention scores and retaining only the most "look-ahead" important tokens.

**How it works:**
```
During prefill (full prompt available):
  1. Run the first few layers and record attention scores from each layer.
  2. For each token, pool its attention scores across heads and layers.
  3. Tokens with high pooled scores are "observed" to be important to future layers.
  4. Compress the KV cache: keep only the top tokens by pooled importance.
During generation:
  5. Attend only to the compressed set of KV pairs.
  6. Newly generated tokens are added to the KV cache normally.
```

**Key properties:**
- **Prefill observation:** The full prompt is processed once to gather attention statistics.
- **Pooling:** Attention scores are aggregated across heads and layers to get a single importance score per token.
- **One-shot compression:** After prefill, the cache is compressed and stays compressed for the rest of generation.

**Why this matters:**
- SnapKV can achieve higher compression ratios than H2O because it uses global (all-layers) information rather than incremental cumulative scores.
- It avoids the "too late" problem: by observing during prefill, it knows which tokens matter before generation starts.
- It is especially effective for long prompts where the prefill cost is amortized over many generation steps.

---

### Real-Life Analogy

Imagine a film editor with 100 hours of raw footage who must cut it down to a 2-hour movie.
- **H2O:** The editor watches the footage in real time, one hour per day, and keeps a running list of the best clips. By day 50, the editor realizes that a crucial scene from day 3 was mediocre at the time but becomes the emotional climax when viewed in context. It was already deleted. The editor must re-shoot or accept a weaker film.
- **SnapKV:** Before editing begins, the editor watches the entire 100 hours in a "scan mode" at 4x speed, marking every scene that gets referenced later, every character introduction, and every Chekhov's gun. The editor then constructs the 2-hour cut from only the marked scenes. Because the scan saw the whole narrative arc, no critical setup is lost.
- **The trade-off:** The scan takes extra time upfront (the prefill observation). But for a 2-hour movie, an extra day of scanning is trivial compared to the risk of deleting the wrong scene. SnapKV pays a small prefill cost to avoid eviction mistakes during generation.

---

### Tiny Numeric Example

**Attention scores from 3 layers during prefill (simplified, one head per layer):**
```
Layer 1 (broad):  t1=0.05  t2=0.05  t3=0.05  t4=0.05  t5=0.05  ... (uniform)
Layer 2 (focused): t1=0.30  t2=0.02  t3=0.25  t4=0.01  t5=0.02  ...
Layer 3 (semantic): t1=0.10  t2=0.05  t3=0.35  t4=0.02  t5=0.03  ...
```

**Pooled importance (sum across layers):**
```
t1: 0.05 + 0.30 + 0.10 = 0.45
t2: 0.05 + 0.02 + 0.05 = 0.12
t3: 0.05 + 0.25 + 0.35 = 0.65
```

**SnapKV compression (keep top 2 by pooled score):**
```
Retained: t3 (0.65), t1 (0.45)
Evicted:  t2, t4, t5, ...
```

**Why this beats H2O:**
```
H2O cumulative (only Layer 1-2 observed so far):
  t1 = 0.35, t3 = 0.30, t2 = 0.07
  If budget=2, retains t1 and t3 — still okay.

But if generation had only seen Layer 1 initially:
  All tokens tied at 0.05 — H2O would evict randomly.
SnapKV sees all layers at once and correctly identifies t3 as the most important.
```

**The shift:** Pooling across layers reveals importance that single-layer cumulative scores miss. SnapKV is more robust to layer-wise attention shifts.

---

### Common Confusion

1. **"SnapKV requires training the model to predict attention."** No. SnapKV observes the model's own attention patterns during prefill. It is a zero-shot inference technique.

2. **"SnapKV and H2O are mutually exclusive."** They can be combined. SnapKV compresses the prompt cache after prefill, and H2O can manage the growing cache during generation by evicting low-importance generated tokens.

3. **"Prefill observation makes SnapKV slower than H2O."** The observation happens during the prefill forward pass, which is already required. The extra cost is minimal: just recording and pooling attention matrices that are already computed.

4. **"SnapKV keeps the same tokens for all layers."** Yes, by design. It creates a single compressed KV cache that all layers share. Some variants (like PyramidKV) use layer-specific budgets, but vanilla SnapKV uses one global compression.

5. **"Pooling attention scores is just averaging."** Averaging is the simplest pool. Real implementations use max-pooling, learned pooling, or attention-weighted aggregation. The principle is the same: collapse multi-layer information into a per-token score.

6. **"SnapKV only works for short prompts."** The opposite is true. On short prompts, the prefill cost is a large fraction of total time. On long prompts, the prefill is amortized over hundreds of generation steps, and the memory savings are enormous.

7. **"If a token has zero attention in prefill, SnapKV will always evict it."** Yes. This is the intended behavior. If no layer attends to it during prefill, it is extremely unlikely to matter later. Edge cases exist (e.g., tokens that matter only for future tokens not yet generated), but empirically the error is small.

---

### Where It Is Used in Our Code

`src/phase113/phase113_kv_compression_concepts.py` — We simulate a multi-layer transformer prefill, record attention scores from each layer, pool them into a per-token importance score, and compress the KV cache by keeping only the top tokens. We compare SnapKV's accuracy against H2O and full cache on synthetic long-context tasks.

`src/phase113/phase113_kv_compression_colab.py` — We load Llama-3.2-3B-Instruct, run prefill on a 4,000-token book passage, observe attention patterns across layers, implement SnapKV compression, and measure memory and speed during generation. We show that SnapKV achieves higher compression than H2O with comparable accuracy.

(End of file - total 97 lines)

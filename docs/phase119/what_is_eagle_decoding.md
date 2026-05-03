## What Is EAGLE Decoding?

---

### The Problem

Basic speculative decoding (Phase 36) uses a small, separate draft model to predict future tokens, then asks the large target model to verify them. The catch: the draft model has no idea what the target model is thinking. It generates guesses based only on raw tokens, so its predictions often diverge from the target model's true distribution. When the draft and target disagree, the target model rejects the draft tokens and falls back to slow autoregressive generation. The acceptance rate stays low because the draft model is essentially guessing in the dark.

---

### Definition

**EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency)** is an advanced speculative decoding method where the draft model receives the target model's hidden states as additional input, rather than generating from raw tokens alone. By conditioning drafts on the target model's internal activations, EAGLE produces guesses that are far more aligned with what the target model would have generated, raising acceptance rates from roughly 50-60% to 80-90%.

**How it works:**
```
Standard speculative decoding:
  Draft model input:  [token_t]
  Draft model output: [token_t+1, token_t+2, token_t+3]
  Target model verifies: accepts/rejects based on its own distribution
  Problem: draft model never sees what the target model thinks

EAGLE decoding:
  Target model processes [token_t] → produces hidden state h_t
  Draft model input:  [token_t, h_t]
  Draft model output: [token_t+1, token_t+2, token_t+3]
  Target model verifies as before
  Result: draft guesses track the target model's distribution far more closely
```

**Key techniques:**
- **Hidden-state conditioning:** the draft model sees the target model's last hidden state, capturing its contextual understanding
- **Feature-level draft:** instead of token logits, the draft predicts features that the target model would have produced
- **Auto-regressive draft:** the draft model runs auto-regressively on its own features, generating a full sequence of speculative features
- **EAGLE-2 enhancement:** uses a context-aware draft policy that adapts the number of draft tokens based on local prediction confidence, rather than using a fixed draft length

**Why this matters:**
- Standard speculative decoding with a 1B draft for a 7B target achieves ~1.5-2x speedup
- EAGLE with the same 1B draft achieves ~2.5-3x speedup because acceptance rates are much higher
- EAGLE-2 further improves by 10-20% by dynamically adjusting draft depth
- No quality loss: the target model still makes the final verification decision

---

### Real-Life Analogy

Imagine two chefs in a restaurant kitchen.
- **Standard speculative decoding:** Chef A (the target) is slow but perfect. Chef B (the draft) is fast but works in a separate room. Chef B preps ingredients based only on the order ticket, without seeing what Chef A is actually doing. Chef B peels potatoes, but Chef A was planning to make mashed cauliflower. Most of Chef B's prep gets thrown out.
- **EAGLE decoding:** Chef B stands right next to Chef A and watches every chop and stir. Chef B sees that Chef A is reaching for rosemary, so Chef B preps rosemary before being asked. When Chef A turns around, the ingredients are already correct. The acceptance rate of prep work skyrockets because Chef B is reading Chef A's mind through observation.
- **The trade-off:** EAGLE requires more communication bandwidth between the two chefs. Chef B must constantly observe Chef A's workspace, which adds overhead. For very short orders, this overhead might not be worth it. But for long, complex meals, the time saved is dramatic.

---

### Tiny Numeric Example

**Standard speculative decoding with a separate draft model:**
```
Target model distribution for next token after "The cat sat on the":
  "mat"     → 0.55
  "chair"   → 0.25
  "floor"   → 0.15
  "roof"    → 0.05

Draft model (independent) predicts:
  "chair"   → 0.35
  "mat"     → 0.30
  "floor"   → 0.20
  "roof"    → 0.15

Acceptance check (sample u=0.4 from uniform):
  u < min(1, p_target/p_draft) = min(1, 0.55/0.30) = 1.0
  Token "mat" accepted? Yes (0.4 < 1.0)
  
But if draft predicted "chair" (prob 0.35):
  u < min(1, 0.25/0.35) = 0.71
  Token "chair" accepted? 65% chance

Overall acceptance rate for 4-token draft: ~45%
```

**EAGLE decoding (draft model sees target hidden state):**
```
Target model hidden state h_t encodes: "this is a domestic cat indoors"

Draft model conditioned on h_t predicts:
  "mat"     → 0.52   (almost matches target)
  "chair"   → 0.26
  "floor"   → 0.16
  "roof"    → 0.06

Acceptance check for "mat":
  u < min(1, 0.55/0.52) = 1.0
  Acceptance probability: ~99%

Overall acceptance rate for 4-token draft: ~85%
```

**Speed comparison for generating 100 tokens:**
```
Standard autoregressive:      100 forward passes
Basic speculative (45% acc):  ~65 forward passes  (1.5x speedup)
EAGLE speculative (85% acc):  ~40 forward passes  (2.5x speedup)
```

---

### Common Confusion

1. **"EAGLE is just a better draft model."** No. The key innovation is not a better architecture but better *input conditioning*. EAGLE works because the draft model sees the target model's hidden states, not because the draft model itself is larger or smarter.

2. **"EAGLE changes the output distribution."** No. The target model still verifies every token using its own exact distribution. EAGLE only improves the draft quality; it does not alter the sampling process or the final probabilities.

3. **"You need to train the target model to support EAGLE."** No. The target model remains unchanged. You only train a small draft model that accepts the target model's hidden states as additional input.

4. **"EAGLE-2 is a completely different algorithm."** EAGLE-2 is an incremental improvement. The core mechanism is identical; EAGLE-2 adds dynamic draft length adjustment based on local confidence, rather than always drafting a fixed number of tokens.

5. **"Hidden states leak too much information to be efficient."** The hidden state is a fixed-size vector (e.g., 4096 dims). Transferring it is negligible compared to the cost of an extra forward pass, especially when draft and target run on the same GPU.

6. **"EAGLE only works with transformer models."** While EAGLE was designed for transformers, the principle applies to any architecture that produces meaningful intermediate representations. The hidden state serves as a compressed summary of the model's current reasoning.

7. **"Higher acceptance rate always means higher speedup."** Not quite. If the draft model is very slow to produce its guesses, the overhead can eat into the gains. EAGLE is optimized so the draft is a tiny model that runs extremely fast relative to the target.

---

### Where It Is Used in Our Code

`src/phase119/phase119_speculative_concepts.py` — We simulate speculative decoding with and without hidden-state conditioning. We compare acceptance rates between an independent draft model and a draft model that sees the base model's activations, then compute expected tokens per forward pass and visualize the speedup.

`src/phase119/phase119_speculative_colab.py` — We load real LLaMA models and implement basic speculative decoding. While we do not train a full EAGLE draft model (that requires custom training), we demonstrate the principle by showing how aligned draft and target distributions yield higher acceptance rates and measurable wall-clock speedup.

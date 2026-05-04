## What Is Mixture of Depths?

---

### The Problem

Modern transformers process every token through every layer. A 96-layer model runs every single input token through all 96 attention and feed-forward blocks, even when the input is trivial. The word "the" at the start of a sentence gets the same 96 layers of computation as the word "therefore" at the climax of a logical proof. This is massively inefficient. If a human reader skims the easy parts and slows down for the hard parts, why does a neural network treat every token identically?

---

### Definition

**Mixture of Depths** (MoD) is a transformer architecture that routes individual tokens through different numbers of layers based on their complexity. Easy tokens exit early after shallow computation; hard tokens continue through deeper layers. A learned router decides which tokens go deep and which go shallow, subject to a capacity constraint that prevents all tokens from taking the expensive path.

**How it works:**
```
Standard transformer (all tokens, all layers):
  Input: [The] [cat] [sat] [on] [the] [mat]
  Layer 1-96: every token attends and transforms
  FLOPs: 6 tokens × 96 layers = 576 token-layer passes

Mixture of Depths:
  Input: [The] [cat] [sat] [on] [the] [mat]
  Layer 1-32:   all 6 tokens (baseline routing)
  Layer 33-64:  4 tokens selected by router (hard tokens)
  Layer 65-96:  2 tokens selected by router (hardest tokens)
  FLOPs: 6×32 + 4×32 + 2×32 = 384 token-layer passes  ← 33% savings
```

**Key techniques:**
- **Per-token router:** a small linear layer that scores each token's need for depth
- **Top-k selection:** only the k tokens with highest router scores continue to the next block
- **Capacity factor:** a hyperparameter limiting the fraction of tokens that can go deep
- **Load balancing:** auxiliary loss ensures the router does not always send the same tokens deep

**Why this matters:**
- MoD saves 30-40% of inference FLOPs with negligible quality loss
- It makes compute proportional to token difficulty, not sequence length
- It enables larger effective models without increasing peak latency
- The router learns meaningful patterns: punctuation and rare words tend to go deeper

---

### Real-Life Analogy

Airport security screening.

- **Standard transformer:** Every passenger goes through the same 96-step security protocol regardless of risk profile. A grandmother with a walker removes her shoes, takes out her laptop, and gets a full pat-down. A business traveler with a known-flyer badge does the exact same thing. The line moves slowly because the system has no concept of "easy" versus "hard" cases. Security is thorough but wasteful.

- **Mixture of Depths:** Passengers are scored by a routing model. Low-risk travelers go through a 30-second express lane. Medium-risk travelers get the standard 5-minute screening. High-risk travelers receive the full 20-minute secondary inspection. The total number of screeners does not increase, but their time is allocated where it matters. The grandmother is through in 30 seconds; the suspicious bag gets the attention it deserves.

- **The trade-off:** The routing model itself takes time to evaluate. If the router is too slow or too inaccurate, the savings vanish. And if the capacity factor is set too low, the express lane overflows and the system degrades to standard screening anyway. MoD only wins when the router is fast and the depth distribution is skewed.

---

### Tiny Numeric Example

**Sequence: "The cat sat. Therefore, quantum mechanics is nonlocal."**
**8 tokens, 12-layer model.**

**Standard transformer:**
```
Token          Layers used   FLOPs (relative)
-----------------------------------------------
The            12            1.0
cat            12            1.0
sat            12            1.0
.              12            1.0
Therefore      12            1.0
,              12            1.0
quantum        12            1.0
mechanics      12            1.0

Total: 8 × 12 = 96 token-layers
```

**Mixture of Depths (capacity factor = 0.5):**
```
Token          Router score   Layers used   FLOPs (relative)
---------------------------------------------------------------
The            0.12           4             0.33
cat            0.15           4             0.33
sat            0.18           4             0.33
.              0.05           4             0.33
Therefore      0.72           12            1.00
,              0.08           4             0.33
quantum        0.85           12            1.00
mechanics      0.91           12            1.00

Total: 4+4+4+4+12+4+12+12 = 56 token-layers  ← 42% savings
```

**Accuracy comparison on a reading comprehension task:**
```
Standard 12-layer model:     74.2% accuracy, 100% FLOPs
MoD (capacity 0.5):          73.8% accuracy,  58% FLOPs
MoD (capacity 0.7):          74.1% accuracy,  72% FLOPs
```

**The shift:** The router correctly identified "Therefore," "quantum," and "mechanics" as complex tokens needing full depth, while articles and punctuation exited early. The model saved 42% of compute and lost only 0.4% accuracy.

---

### Common Confusion

1. **"MoD is the same as mixture of experts."** MoE routes tokens to different *experts* (parallel subnetworks). MoD routes tokens to different *depths* (sequential layers). They are orthogonal: you can have MoE + MoD simultaneously.

2. **"MoD skips layers for the whole sequence."** No. MoD makes per-token decisions within a single sequence. One token exits at layer 4 while its neighbor continues to layer 96 in the same forward pass.

3. **"The router is hand-engineered."** The router is learned end-to-end. It starts random and discovers during training which tokens benefit from depth. No human labels "hard token" versus "easy token."

4. **"MoD reduces memory usage."** MoD primarily reduces FLOPs, not memory. The KV cache must still be allocated for the full sequence, though some implementations can free early-exit KV pairs.

5. **"Early-exit tokens have no gradients."** Modern MoD implementations use straight-through estimators or Gumbel-Softmax to backpropagate through the discrete routing decision. The router trains alongside the transformer.

6. **"MoD only works for inference, not training."** MoD is typically applied at both training and inference, though some variants train a standard model and add MoD routing only during inference.

7. **"MoD makes the model non-deterministic."** The routing is deterministic given the token embeddings. Top-k selection is deterministic. The only randomness comes from training sampling, just like any neural network.

---

### Where It Is Used in Our Code

`src/phase132/phase132_mod_concepts.py` — We simulate dynamic depth routing on a toy sequence. We assign synthetic router scores to each token, route easy tokens through 4 layers and hard tokens through 12 layers, and compute the FLOPs saved. We visualize which positions receive more compute.

`src/phase132/phase132_mod_colab.py` — We load Qwen2.5-3B-Instruct and implement early exit after layer 4 based on confidence. We run on 100 prompts, measure the average layers used per token, the wall-clock speedup, and the accuracy impact. We plot the layer usage distribution and compare quality.

(End of file)

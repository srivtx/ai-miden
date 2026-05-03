## What Is Positional Extrapolation?

---

## The Problem

You have trained a large language model on sequences up to 4,096 tokens. It performs beautifully on essays, emails, and short articles. Then a customer asks it to summarize a 32,768-token technical manual. The model fails catastrophically. It hallucinates facts, repeats sentences, and loses track of characters introduced in chapter one. The problem is not the model's intelligence; it is the positional encoding. During training, the model learned embeddings for positions 0 through 4,095. Position 30,000 is outside its experience, and the standard sinusoidal or learned positional embeddings extrapolate poorly. The model treats the long document as if it were a random sequence of noise.

---

## Definition

**Positional Extrapolation** refers to methods that allow a model to generalize to sequence lengths longer than its training distribution. Techniques include ALiBi (Attention with Linear Biases), which adds a fixed penalty based on token distance rather than absolute position, and RoPE (Rotary Position Embedding), which encodes relative positions via rotation matrices and can be interpolated or extrapolated by scaling the position indices.

**How it works:**
```
Standard absolute positions:
  Position 0, 1, 2, ..., 4095 are learned or sinusoidally encoded.
  Position 30000 is unseen → model behavior is undefined.

RoPE interpolation:
  Scale position indices by training_length / target_length = 4096 / 32768 = 0.125
  Position 30000 is treated as position 3750, which the model has seen.
  Fine-tune for a few steps to adapt to the compressed scale.

ALiBi:
  No position embeddings at all.
  Attention scores receive a linear penalty proportional to query-key distance.
  Distance 30000 is just a larger penalty than distance 4096; no extrapolation needed.
```

**Key techniques:**
- **RoPE interpolation:** scale position indices downward so they fit inside the training range, then fine-tune.
- **NTK-aware scaling:** a variant of RoPE interpolation that distributes the scale non-uniformly across frequency bands.
- **ALiBi:** replaces position embeddings with distance-based attention biases that naturally extend to any length.
- **YaRN:** combines interpolation with temperature scaling to stabilize attention entropy at long lengths.

**Why this matters:**
- Training on 100K-token sequences from scratch is prohibitively expensive; extrapolation reuses shorter pre-training.
- Many real-world tasks require long contexts: legal documents, code repositories, genomic sequences, and multi-turn conversations.
- The choice of positional encoding is a permanent architectural decision that determines the model's scalability.

---

## Real-Life Analogy

Imagine a piano student who has practiced for ten years on a 61-key electronic keyboard. They can play Mozart sonatas flawlessly because every note they need falls within the 61-key range. One day, they are invited to perform at a concert hall with a full 88-key grand piano. The additional 27 keys are completely unfamiliar. When the score calls for a low A0 or a high C8, the student panics because they have never touched those keys.

**The extrapolation approach:** A teacher explains that the pattern of black and white keys repeats every octave. The physical distance between A0 and A1 is the same as between A3 and A4. The student learns to trust interval relationships rather than absolute key positions. RoPE interpolation is like giving the student a compressed map where the 88 keys are squeezed into the 61-key layout they already know, then letting them practice for a few hours to adjust. ALiBi is like teaching the student to ignore key numbers entirely and play by relative finger distances, which works on any keyboard length.

**The trade-off:** Extrapolated positions are less accurate than trained positions. The student who learned on 61 keys will play more confidently on a 61-key keyboard than on an extrapolated 88-key one. Similarly, a model extrapolated to 128K tokens will underperform a model actually trained on 128K tokens, but it will perform far better than a model with naive position encoding.

---

## Tiny Numeric Example

**A model trained on 4,096 tokens, tested on 32,768 tokens:**

| Method | Perplexity at 32K | Fine-tuning Steps | Implementation Complexity |
|---|---|---|---|
| Standard (no extrapolation) | 45.2 (catastrophic) | 0 | trivial |
| RoPE naive extrapolation | 38.7 (poor) | 0 | trivial |
| RoPE interpolation (scale 0.125) | 18.7 | 100 | low |
| NTK-aware scaling | 17.2 | 100 | medium |
| ALiBi (zero-shot) | 16.3 | 0 | low |
| YaRN | 15.8 | 50 | medium |
| Trained natively on 32K | 14.1 | full training | high |

**Longer extrapolation to 128K tokens:**
```
ALiBi at 32K:   perplexity 16.3
ALiBi at 128K:  perplexity 19.1  (degradation of +2.8)
RoPE interp at 128K:  perplexity 24.5  (degradation of +5.8)
```

**Attention pattern analysis:**
```
Standard positions at 32K:  attention scores degenerate into uniform mush
ALiBi at 32K:               attention remains sharp with distant tokens suppressed
RoPE interp at 32K:         attention sharp but slightly miscalibrated distances
```

**The shift:** Positional extrapolation methods bridge the gap between affordable training lengths and demanding deployment lengths. ALiBi achieves the best zero-shot generalization because its bias depends only on relative distance, not on absolute position indices that fall outside the training range.

---

## Common Confusion

1. **"Positional extrapolation is the same as training on longer sequences."** Training on longer sequences is the gold standard but is computationally expensive. Extrapolation specifically refers to generalizing beyond training length without full retraining.

2. **"RoPE interpolation changes the model weights."** It changes only how position indices are mapped to rotation angles. The weights remain the same; only the input encoding changes.

3. **"ALiBi works out of the box for any length."** ALiBi generalizes to unseen lengths without fine-tuning, but performance still degrades at extreme lengths because attention entropy grows and long-range dependencies become harder to model.

4. **"Positional extrapolation fixes all long-context problems."** It fixes the position encoding problem, but long contexts also suffer from attention memory bottlenecks, context utilization issues, and training instability.

5. **"You can extrapolate a model trained on 512 tokens to 1 million tokens."** Extrapolation has limits. The degradation curve is roughly logarithmic; a 100x extrapolation is feasible, but a 2,000x extrapolation is not.

6. **"Extrapolation requires no fine-tuning."** Some methods like ALiBi require none; others like RoPE interpolation benefit significantly from even a few hundred steps of continued pre-training on longer sequences.

7. **"All modern models use extrapolation-friendly position encoding."** Many popular models still use absolute or standard RoPE encodings that extrapolate poorly. The choice of position encoding is an architectural decision made at training time.

---

## Where It Is Used in Our Code

`src/phase97/phase97_long_context.py` — We simulate sinusoidal, RoPE, and ALiBi position encodings on a toy attention head. We extend the sequence length far beyond the training range and plot the attention score degradation for each method. You can see how ALiBi maintains structure while standard encodings collapse into noise.

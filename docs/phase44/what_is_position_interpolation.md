## What Is Position Interpolation?

---

### The Problem

Your Transformer model was trained on sequences up to 4096 tokens. But a user wants to process an entire book — 128,000 tokens. Re-training the model on 128K sequences would cost millions of dollars and weeks of GPU time. Is there a way to extend the context window without retraining from scratch?

---

### Definition

**Position interpolation** extends a model's context window by scaling position indices so that the maximum position seen during inference fits within the range the model saw during training.

**The core idea:**
```
If trained on max_position = 4096, but you need max_position = 32768:
    scaled_position = position × (4096 / 32768) = position / 8
```

Now position 32768 maps to angle 4096 — which the model HAS seen during training. All intermediate positions are smoothly interpolated between known positions.

**Why this works:**
- The model learned to interpret rotation angles in the range [0, 4096]
- By scaling positions down by 8×, all positions in [0, 32768] map to angles in [0, 4096]
- The model never sees an unfamiliar angle
- Position distinctions are compressed (less precise) but coherent

**The trade-off:**
- You gain 8× more context length
- You lose some position precision (adjacent positions have more similar embeddings)
- A small amount of fine-tuning on long sequences restores most of the lost precision

---

### Real-Life Analogy

A musician trained on a piano with 4 octaves (48 keys).
- **Without interpolation:** They are handed a piano with 32 octaves (384 keys). The keys beyond octave 4 make sounds they have never heard. They panic and play nonsense.
- **With position interpolation:** The 32 octaves are "compressed" into the 4-octave range they know. Octave 8 sounds like octave 1, octave 16 sounds like octave 2, etc. The musician can now play the entire piano using only their familiar sounds. The music is in a lower "register" but is coherent.

The musician does not need to relearn music theory. They just need to accept that the same note now covers a wider range of the keyboard.

---

### Tiny Numeric Example

**RoPE rotation angle for dimension i:**
```
θ(position, i) = position × (10000^(-2i/d))
```

**Training range:** positions 0 to 4
**Desired inference range:** positions 0 to 16

**Without interpolation — position 16, dimension 0:**
```
θ(16, 0) = 16 × (10000^0) = 16.0 radians
```
The model never saw angle 16 during training (max was 4). It has no idea what this means.

**With interpolation — scale factor = 4/16 = 0.25:**
```
scaled_position = 16 × 0.25 = 4
θ(4, 0) = 4 × (10000^0) = 4.0 radians
```
The model HAS seen angle 4.0 during training. It knows exactly how to interpret it.

**Position 8 with interpolation:**
```
scaled_position = 8 × 0.25 = 2
θ(2, 0) = 2.0 radians
```
Position 8 maps to angle 2, which is halfway between position 2 and position 3 in the original range. The model interpolates between what it learned at those positions.

---

### Common Confusion

1. **"Position interpolation adds new information."** No. It reuses the model's existing position encoding capacity. The model does not learn anything new about long contexts unless you fine-tune.

2. **"Interpolation makes the model as good as one trained on long sequences."** Almost, but not quite. Without fine-tuning, performance degrades slightly because adjacent positions become too similar. With a few hundred steps of fine-tuning on long data, it catches up to 90-95%.

3. **"Any model can be interpolated to any length."** In theory, yes. In practice, very long contexts (1M tokens) also require memory optimizations (GQA, quantization) and sometimes architectural changes.

4. **"Interpolation and extrapolation are the same."** No. Interpolation scales positions DOWN to fit the training range. Extrapolation tries to handle positions BEYOND the training range without scaling — this almost always fails.

5. **"Position interpolation only works for RoPE."** It works for any relative position encoding where positions map to a bounded range. Absolute position embeddings (learned vectors) are harder to extend.

---

### Where It Is Used in Our Code

`src/phase44/phase44_long_context.py` — We train a tiny model with max position 16, then apply position interpolation to extend it to position 64. We visualize how the rotation angles scale and show that attention patterns remain coherent.

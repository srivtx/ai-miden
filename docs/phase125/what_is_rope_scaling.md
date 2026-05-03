## What Is RoPE Scaling?

---

### The Problem

A transformer model is trained on sequences of a fixed length — say 4096 tokens. The position embeddings (RoPE) are tuned to that exact range. When you try to feed a longer sequence, say 16384 tokens, the model fails because it has never seen position encodings beyond 4096. The dot products between query and key vectors at positions 5000 and 10000 are completely unfamiliar. The attention scores collapse or explode, and the model generates nonsense. How do you make the model handle sequences it was never trained on, without retraining from scratch?

---

### Definition

**RoPE Scaling** is the family of techniques that modify the Rotary Position Embedding (RoPE) frequency bases so a pretrained model can generalize to sequence lengths beyond its training context window. Instead of changing the model weights, you rescale the position encoding frequencies so that longer positions map into the same value range the model already understands.

**How it works:**
```
Standard RoPE:
  Position m gets encoding: [cos(m*theta_i), sin(m*theta_i)]
  where theta_i = base^(−2i/d)
  Valid for m in [0, 4095] if trained on 4K context

Problem at 8K:
  Position m=6000: cos(6000 * theta_i) — model has never seen this

RoPE Scaling solution:
  Multiply all thetas by a scale factor s:
  theta'_i = theta_i / s
  Now position m=6000 uses the SAME angles as position 3000 in original
  The model "thinks" the 8K sequence is just a 4K sequence with
  compressed positions — and it already knows 4K behavior.
```

**Key techniques:**
- **Position Interpolation (PI):** multiply all thetas by s=L'/L. Simple, but blurs high-frequency details because it compresses all frequencies equally.
- **NTK-aware scaling:** only interpolate high frequencies while preserving low frequencies. Matches Neural Tangent Kernel theory that different frequencies learn at different rates.
- **YaRN (Yet another RoPE extension):** combines temperature scaling with frequency-aware interpolation. Scales different frequency bands by learned factors.

**Why this matters:**
- Training a 32K-context model from scratch costs millions of dollars
- RoPE scaling extends a 4K model to 32K with hours of fine-tuning, not months of pre-training
- The model weights do not change at inference time — only the position encoding frequencies do
- Position interpolation is the simplest form; YaRN achieves the best quality at extreme lengths

---

### Real-Life Analogy

Imagine a piano keyboard with 88 keys. A composer writes a symphony that only uses the middle 4 octaves (32 keys). Then someone asks the same pianist to play a piece that requires all 7 octaves.

- **Standard RoPE (no scaling):** The pianist tries to play the high notes but those keys are broken or missing. The music falls apart because those frequencies were never practiced.
- **Position Interpolation:** The piano tuner squeezes all 7 octaves into the physical space of 4 octaves. Every key now represents 1.75 semitones instead of 1. The pianist can reach all notes, but the spacing is wrong and fast passages sound muddy.
- **NTK-aware scaling:** The tuner only squeezes the high notes (the right side of the keyboard) while leaving the low notes (left side) at normal spacing. Bass chords stay rich; only the treble gets compressed.
- **YaRN:** The tuner uses a formula that gradually changes the squeeze factor across the keyboard, and the pianist also plays with slightly softer touch (temperature scaling) to prevent harshness. The result sounds natural across all octaves.

---

### Tiny Numeric Example

**RoPE frequencies for a 4-dimensional embedding (d=4, base=10000):**
```
Dimension i=0: theta_0 = 10000^(0/4) = 1.000
Dimension i=1: theta_1 = 10000^(−2/4) = 0.010

Position m=100 encoding:
  i=0: [cos(100 * 1.000), sin(100 * 1.000)] = [cos(100), sin(100)]
  i=1: [cos(100 * 0.010), sin(100 * 0.010)] = [cos(1.0), sin(1.0)]
```

**Extending to 8K with Position Interpolation (scale factor s=2):**
```
New thetas: theta'_i = theta_i / 2

Position m=100 in 8K sequence (equivalent to original position 50):
  i=0: [cos(100 * 0.500), sin(100 * 0.500)] = [cos(50), sin(50)]
         ← this is EXACTLY what original model saw at position 50
  i=1: [cos(100 * 0.005), sin(100 * 0.005)] = [cos(0.5), sin(0.5)]
         ← this is what original model saw at position 50 in dim 1
```

**The good news:** Position 100 now gets encodings identical to position 50 in the original model. The model "recognizes" the position because it has seen equivalent angles before.

**The bad news:**
```
High-frequency dimensions (small theta) at nearby positions:
  Original: position 0 → cos(0) = 1.0, position 1 → cos(0.01) = 0.99995
  Difference: 0.00005 (model can distinguish adjacent positions)

With PI (s=2):
  Position 0 → cos(0) = 1.0, position 1 → cos(0.005) = 0.9999875
  Difference: 0.0000125 (4× smaller!)
```

The model can barely tell position 0 from position 1 anymore. This is why PI hurts local attention precision — it blurs nearby positions together.

**NTK-aware fix:**
```
Instead of dividing ALL thetas by 2, only divide the HIGH frequencies:
  theta'_low  = theta_low   (unchanged, preserves local precision)
  theta'_high = theta_high / 2  (compressed, extends range)

Now position 1 in a high-frequency dim:
  cos(1 * 0.010/2) = cos(0.005) — still small difference
  But wait — we need position 8000 to map to original 4000 range:
  The NTK formula: theta'_i = theta_i * s^(−d/(d−2))
  This smoothly blends from no-scaling at low freqs to full scaling at high freqs.
```

---

### Common Confusion

1. **"RoPE scaling changes the model weights."** No. Only the position encoding formula changes. The query and key projection matrices stay frozen. At inference time, you compute Q and K normally, but the rotary embedding multiplies by rescaled angles.

2. **"Any model with RoPE can be scaled to any length."** Not exactly. Scaling works because of the mathematical structure of sinusoidal encodings, but there is a quality degradation limit. Most models scale reliably to 2-4× their training length. Beyond 8×, even YaRN struggles because attention patterns and feedforward behavior were never trained on such dependencies.

3. **"Position Interpolation and YaRN are completely different."** They are on a spectrum. PI is the simplest scaling: divide all frequencies equally. NTK is smarter about which frequencies to scale. YaRN adds temperature scaling on top. All three modify the same theta values.

4. **"Scaling RoPE means the model can attend across the full long sequence immediately."** The embeddings work, but the attention mechanism itself may need fine-tuning. A model trained on 4K has learned that distant tokens are rarely relevant. Scaling to 32K gives the *capability* to see distant tokens, but the model must be fine-tuned to actually use them.

5. **"RoPE scaling is only for inference."** It works for inference (you just change the thetas), but quality is much better if you do a small amount of continued pre-training or fine-tuning with the scaled RoPE. This teaches the attention layers to use the extended context.

6. **"NTK stands for Neural Tangent Kernel, so this is a kernel method."** The name comes from the observation that NTK theory predicts different learning rates for different frequency components. The actual NTK-aware scaling formula is heuristic, inspired by theory but not a rigorous kernel implementation.

7. **"Higher base (like 1,000,000) makes scaling unnecessary."** A larger RoPE base does improve extrapolation because frequencies are lower overall. But it is not a substitute for scaling — it is a complementary hyperparameter. Llama-3 uses base=500,000 and still benefits from YaRN for 128K context.

---

### Where It Is Used in Our Code

`src/phase125/phase125_long_context_concepts.py` — We simulate RoPE position encodings for different sequence lengths, applying Position Interpolation, NTK-aware scaling, and YaRN. We visualize the position encoding similarity matrix to show how scaling affects the model's ability to distinguish nearby positions, and we plot attention entropy versus sequence length to demonstrate which methods preserve precision at long range.

`src/phase125/phase125_long_context_colab.py` — We load a real 4K-context LLaMA-3.2-3B model, apply YaRN scaling to extend it to 8K, and fine-tune it on long book passages. We evaluate with needle-in-haystack tests and perplexity comparisons, demonstrating that scaled RoPE plus brief fine-tuning achieves functional 8K context at a fraction of pre-training cost.

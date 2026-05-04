## What Is Representation Engineering?

---

### The Problem

You want a language model to be more honest, more creative, or less biased. Fine-tuning updates billions of weights, takes hours on expensive GPUs, and can destroy capabilities you wanted to keep. Prompt engineering is cheaper, but a single adversarial suffix can undo your carefully crafted instructions. You are fighting the model at the surface when you could be speaking its internal language. What if you could open the hood, find the exact knob that controls "honesty," and turn it?

---

### Definition

**Representation Engineering** is the practice of reading, interpreting, and modifying the internal activations of a neural network to control its behavior without changing its trained weights. Instead of retraining the whole model or praying that a prompt sticks, you identify a direction in the model's activation space that corresponds to a concept, then add or subtract that direction during inference.

**How it works:**
```
Base model: frozen weights
Concept data: 50 happy sentences, 50 sad sentences
Extraction: mean(activations|happy) - mean(activations|sad) = happiness vector
Application: during generation, add happiness_vector * 3 to layer 15
Result: the model outputs happier text without any weight updates
```

**Key techniques:**
- **Steering vectors:** contrastive difference vectors that encode a concept
- **Activation patching:** swapping activations between a clean and corrupted run to locate circuit components
- **Linear probes:** training a simple classifier on top of hidden states to decode what the model knows

**Why this matters:**
- You can make a model refuse harmful requests more reliably without retraining it
- You can dial creativity up or down with a single scalar coefficient
- You can inspect what the model knows by probing its internal representations
- The technique works across model families because concepts tend to be linearly represented

---

### Real-Life Analogy

A sound mixing board at a concert.
- **Base model:** The band playing the song. The musicians (weights) know the piece and play it the same way every night.
- **Representation engineer:** The sound engineer at the mixing board. They do not rewrite the song, replace the guitarist, or shout instructions from the crowd (prompt engineering). They simply push the "vocals" fader up, pull the "bass" fader down, and add reverb to the drums. The song is the same, but the experience changes dramatically.
- **The trade-off:** If you push the vocals fader too high, the mix distorts. If you add a steering vector with too large a coefficient, the model output becomes garbled or repetitive. Representation engineering is precise surgery, not a sledgehammer.

---

### Tiny Numeric Example

**A toy model has a 4-neuron hidden layer. We feed it 3 positive and 3 negative examples:**
```
Positive activations (layer 2):
  [1.2, 0.8, -0.2, 0.5]
  [1.0, 0.9, -0.1, 0.4]
  [1.3, 0.7, -0.3, 0.6]
  Mean positive: [1.17, 0.80, -0.20, 0.50]

Negative activations (layer 2):
  [-0.5, 0.2, 1.1, -0.3]
  [-0.4, 0.1, 1.0, -0.2]
  [-0.6, 0.3, 1.2, -0.4]
  Mean negative: [-0.50, 0.20, 1.10, -0.30]

Steering vector = mean(pos) - mean(neg):
  [1.67, 0.60, -1.30, 0.80]
```

**Apply steering with coefficient +2 to a new input:**
```
Original activation: [0.1, 0.2, 0.3, -0.1]
Steered activation:  [0.1, 0.2, 0.3, -0.1] + 2 * [1.67, 0.60, -1.30, 0.80]
                   = [3.44, 1.40, -2.30, 1.50]

Output probability shift:
  "wonderful" → 0.05 (baseline) → 0.31 (steered)
  "terrible"  → 0.08 (baseline) → 0.01 (steered)
```

**The shift:** The model redistributed probability mass from negative sentiment words to positive ones without any gradient descent. A single vector addition changed behavior.

---

### Common Confusion

1. **"Representation engineering is the same as fine-tuning."** Fine-tuning changes the model's weights permanently. Representation engineering freezes the weights and only edits activations during the forward pass. It is reversible: remove the hook and the model returns to baseline instantly.

2. **"Steering vectors work on every layer equally."** No. Early layers encode syntax and part-of-speech. Late layers encode next-token logits. Middle layers (roughly 40-60% depth) usually encode high-level concepts like sentiment, honesty, or formality. Steering at the wrong layer often has no effect or produces nonsense.

3. **"If I find the 'honesty' vector, the model becomes perfectly honest."** Steering shifts tendencies, not guarantees. A coefficient of +3 might increase honesty on average, but the model can still hallucinate if the underlying knowledge is missing. It is a nudge, not a rewrite.

4. **"Representation engineering only works on language models."** False. Vision models have steerable directions for "texture," "color temperature," and "object size." Diffusion models can be steered to produce more or less of a visual concept by editing the U-Net hidden states.

5. **"You need thousands of examples to extract a steering vector."** Not true. In practice, 20-50 contrastive pairs often suffice because the concept is linearly represented across a wide subspace. The key is diversity, not raw count.

6. **"Steering is just prompt engineering in disguise."** Prompt engineering manipulates the input text. Steering manipulates the internal state after the input has been encoded. Prompt engineering is limited by context length and tokenization; steering operates in continuous activation space and can be applied at any layer.

7. **"A steering vector for one model works in another model."** Usually not directly. The vector is tied to a specific architecture, layer index, and residual stream dimension. However, the *direction* often transfers between models of the same family if you account for dimensionality differences via projection.

---

### Where It Is Used in Our Code

`src/phase133/phase133_steering_concepts.py` — We simulate steering vectors on a tiny NumPy MLP. We extract positive versus negative concept vectors from hidden-layer activations, apply steering at multiple coefficients, and visualize how the output distribution shifts predictably.

`src/phase133/phase133_steering_colab.py` — We use a real Llama-3.2-3B-Instruct model. We extract a "happiness" steering vector by comparing activations at layer 15 for happy and sad sentences, then we generate text at different steering strengths and measure the sentiment shift quantitatively.

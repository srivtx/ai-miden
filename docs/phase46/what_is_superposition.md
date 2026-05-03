## What Is Superposition?

---

### The Problem

A neural network has N neurons but needs to represent M features where M >> N. For example, a 512-neuron layer might need to represent 10,000 different concepts (dog, cat, Paris, addition, anger, etc.). How can N neurons represent M >> N features without losing information?

---

### Definition

**Superposition** is the hypothesis that neural networks represent more features than they have neurons by encoding features as nearly-orthogonal directions in activation space, rather than dedicating one neuron per feature.

**The math:**
- In a 512-dimensional space, you can fit thousands of nearly-orthogonal directions
- Each direction corresponds to a feature
- A neuron does not represent one feature; it participates in many features
- Features "overlap" in the neuron's activity, like signals multiplexed on a wire

**Key insight:**
```
Traditional view: 1 neuron = 1 feature (512 features max)
Superposition:    1 neuron = part of many features (10,000+ features possible)
```

**Why networks use superposition:**
- The world has far more concepts than neurons
- Networks learn to compress by overlapping features
- This explains why individual neurons are often polysemantic (respond to multiple unrelated things)

---

### Real-Life Analogy

A piano with 88 keys.
- **Traditional view:** Each key plays one note. You can play 88 notes. If you need 10,000 sounds, you need 10,000 keys.
- **Superposition:** Each key can be pressed with different velocities, combined with pedal effects, and played in chords. The same 88 keys can produce millions of distinguishable sounds through combination and overlap.

A single piano key (neuron) does not represent one sound (feature). It contributes to many sounds depending on how it is combined with other keys.

---

### Tiny Numeric Example

**2 neurons trying to represent 4 features:**

**Features as directions in 2D space:**
```
Feature A: [1.0,  0.0]  -> neuron 1 fires, neuron 2 silent
Feature B: [0.0,  1.0]  -> neuron 2 fires, neuron 1 silent
Feature C: [0.7,  0.7]  -> both neurons fire equally
Feature D: [0.7, -0.7]  -> neuron 1 fires, neuron 2 inhibits
```

**All 4 features are linearly independent and distinguishable:**
```
Dot products between features:
  A·B = 0.0    (orthogonal)
  A·C = 0.7
  A·D = 0.7
  B·C = 0.7
  B·D = -0.7
  C·D = 0.0    (orthogonal)
```

**When both features C and D are present:**
```
Activation = [0.7, 0.7] + [0.7, -0.7] = [1.4, 0.0]
```

**Interpretation:**
- The combined activation looks like Feature A (which is [1.0, 0.0])
- But it is actually C + D
- This is interference — features overlap and can be confused
- Networks tolerate this because real-world feature combinations are sparse

---

### Common Confusion

1. **"Superposition means neurons are random."** No. The directions are carefully learned to minimize interference for common feature combinations.

2. **"Superposition only happens in overparameterized networks."** Actually, the opposite. Superposition is most necessary when the network is UNDERparameterized relative to the number of features it must represent.

3. **"If we train a sparse autoencoder, superposition disappears."** The autoencoder finds the feature directions, but the underlying network still uses superposition. The autoencoder is a decoder, not a network modification.

4. **"Superposition makes interpretability impossible."** It makes it harder, but not impossible. Sparse autoencoders and activation patching can still recover the feature directions.

5. **"All neurons participate in all features."** Not necessarily. Some features might use only a subset of neurons. The degree of overlap varies.

---

### Where It Is Used in Our Code

`src/phase46/phase46_mechanistic_interpretability.py` — We train a tiny network with 2 hidden neurons on 4 different input patterns. We show that the network learns to represent all 4 patterns in superposition, with each neuron participating in multiple pattern representations.

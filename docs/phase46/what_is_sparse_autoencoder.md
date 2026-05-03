## What Is a Sparse Autoencoder?

---

### The Problem

Neural network activations are high-dimensional and dense. A hidden layer might have 4096 neurons, all firing to some degree on every input. How do you find interpretable patterns in this soup of numbers? Can you decompose the activity into a small set of meaningful features?

---

### Definition

A **sparse autoencoder** is an unsupervised neural network that learns to compress activations into a sparse set of interpretable features, then reconstruct them.

**Architecture:**
```
Activation (4096 dims) -> Encoder -> Sparse Features (16384 dims, 99% zeros)
                                          -> Decoder -> Reconstructed Activation (4096 dims)
```

**Key properties:**
1. **Overcomplete:** The feature space is LARGER than the activation space (e.g., 4× more features than neurons)
2. **Sparse:** Each activation is represented by only a few active features (typically 1-10 out of 16384)
3. **Interpretable:** Individual features often correspond to human-understandable concepts

**Training objective:**
```
Loss = ||activation - reconstruction||² + λ × ||features||_1
```
- The first term ensures faithful reconstruction
- The second term (L1 penalty) forces sparsity

**Why this works:**
- Real-world concepts are sparse. A sentence about "golden retrievers" involves dog-ness, color, breed, and friendliness — but NOT nuclear physics or accounting.
- The autoencoder learns basis vectors that align with these sparse concepts.
- Each feature becomes a "direction" in activation space that corresponds to a concept.

---

### Real-Life Analogy

A library catalog.
- **Raw activations:** A 4096-page book describing every detail of a scene simultaneously. Overwhelming and redundant.
- **Sparse autoencoder:** The book is decomposed into 16,384 index cards, but only 5 cards are pulled for any given scene: "dog," "golden color," "outdoor," "grass," "sunny." The rest stay in the drawer.

The sparse representation is much more useful. If you want to know what the model "thinks" about an image, you read the 5 active cards instead of interpreting 4096 continuous numbers.

---

### Tiny Numeric Example

**Hidden activation (4 neurons):**
```
h = [2.3, -0.5, 1.1, 0.2]
```

**Sparse autoencoder with 8 features:**
```
Encoder matrix E (8×4):
  f1 = [0.8, 0.0, 0.2, 0.0]  -> concept A
  f2 = [0.0, 0.9, 0.0, 0.1]  -> concept B
  f3 = [0.1, 0.0, 0.7, 0.0]  -> concept C
  ... (5 more features)
```

**Encoded features:**
```
f = E @ h = [2.06, -0.43, 0.99, 0.1, -0.2, 0.05, 0.0, 0.0]
```

**After L1 sparsity (threshold = 0.5):**
```
f_sparse = [2.06, 0.0, 0.99, 0.0, 0.0, 0.0, 0.0, 0.0]
```

**Interpretation:**
- Feature 1 (strength 2.06) is active -> "concept A is strongly present"
- Feature 3 (strength 0.99) is active -> "concept C is moderately present"
- Only 2 out of 8 features are active -> 75% sparsity

**Reconstruction:**
```
h_recon = Decoder @ f_sparse ≈ [2.1, -0.1, 1.0, 0.0]
```
Close to the original [2.3, -0.5, 1.1, 0.2] despite using only 2 features.

---

### Common Confusion

1. **"Sparse autoencoders are just PCA."** No. PCA finds orthogonal directions of maximum variance. Sparse autoencoders find directions that correspond to sparse, interpretable concepts. They often learn very different features.

2. **"Every feature is perfectly interpretable."** Not always. Some features are polysemantic (encode multiple unrelated concepts). Some are uninterpretable noise. But many are surprisingly clean.

3. **"Sparse autoencoders change the model."** No. They are trained on the model's activations after the model is frozen. They are analysis tools, not model modifications.

4. **"More features always means better interpretation."** Diminishing returns apply. 4× expansion is common. Beyond 16×, features start splitting into redundant sub-features.

5. **"Sparse autoencoders only work for vision."** They work for any model activations: language, vision, audio, and multimodal.

---

### Where It Is Used in Our Code

`src/phase46/phase46_mechanistic_interpretability.py` — We train a sparse autoencoder on a tiny model's hidden activations. We visualize which input patterns activate which learned features, showing that sparse decomposition reveals interpretable structure.

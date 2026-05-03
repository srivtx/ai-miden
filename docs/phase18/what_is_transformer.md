### 1. Why it exists (THE PROBLEM first)

Before Transformers, the dominant architecture for sequence modeling was the Recurrent Neural Network (RNN). RNNs process one word at a time, maintaining a hidden state that gets updated sequentially. This creates two major problems:

1. **Underutilization of hardware:** Modern GPUs have thousands of cores designed for parallel computation. RNNs can only use one core at a time because each step depends on the previous step's hidden state. Training on large datasets takes forever.

2. **Long-range dependencies are hard:** In a long sentence, the connection between the first word and the last word must travel through every single intermediate hidden state. Information gets diluted or lost along the way.

We needed an architecture that could process entire sequences in parallel while still capturing relationships between any two words, no matter how far apart.

---

### 2. Definition (very simple)

The Transformer is a neural network architecture that replaces recurrence with **attention**. Instead of processing words one by one, it lets every word in a sentence directly attend to every other word simultaneously. This makes training highly parallelizable and allows the model to learn long-range dependencies in a single step.

---

### 3. Real-life analogy

Imagine a roundtable meeting where everyone can talk to everyone else at the same time, instead of passing a microphone around one at a time. In the old way (RNN), you have to wait for person 1 to finish before person 2 can speak, and person 10 barely remembers what person 1 said. In the Transformer way, everyone shares their thoughts simultaneously, and each person instantly updates their understanding based on what everyone else said.

---

### 4. Tiny numeric example

Consider the sentence: **"The cat sat"**

**RNN approach (sequential):**
1. Process "The" → update hidden state h1
2. Process "cat" → update hidden state h2 (needs h1)
3. Process "sat" → update hidden state h3 (needs h2)

Three sequential steps. No parallelism.

**Transformer approach (parallel):**
- Step 1: "The" attends to "The", "cat", "sat" → output vector v1
- Step 2: "cat" attends to "The", "cat", "sat" → output vector v2
- Step 3: "sat" attends to "The", "cat", "sat" → output vector v3

All three attention computations happen **simultaneously** on the GPU. The only sequential part is the layer stacking (e.g., Layer 1 → Layer 2), but within a single layer, every word is processed in parallel.

---

### 5. Common confusion

1. **"Transformers don't use any recurrence at all."**
   - They don't use recurrence in the layer computation, but they do still process layers sequentially (Layer 1 output feeds into Layer 2). The parallelism is within a layer, not across the entire model.

2. **"Transformers are only for NLP."**
   - Originally designed for NLP, but now used for vision (Vision Transformer), audio, protein folding, time series, and more. The architecture is general-purpose.

3. **"Attention replaces all other operations."**
   - Attention is the core mechanism, but Transformers also use feed-forward networks, layer normalization, residual connections, and positional encoding. Attention alone is not the full picture.

4. **"Transformers are faster than RNNs at inference."**
   - Not necessarily. During training, Transformers are much faster due to parallelization. At inference time (generating one word at a time), both are sequential, and RNNs can sometimes be faster per step.

---

### 6. Where it is used in our code

In our project, the Transformer architecture serves as the backbone for our sequence understanding models. When we need to process input sequences and capture global dependencies between tokens, we use a Transformer encoder layer stack instead of recurrent layers.

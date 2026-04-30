# Roadmap: From Zero to Understanding GPT

This document shows the natural, step-by-step progression from where we are now to understanding (and building) a tiny GPT. Each phase adds **only one or two new ideas** and provides full practice before moving forward.

---

## Where We Are Now (End of Phase 4)

We have a neural network that:
- Takes a single number as input
- Has one hidden layer with 8 neurons and ReLU activation
- Outputs a single number
- Learns to fit a curve (parabola) using gradient descent and backpropagation

This is a **regression** problem: input number → predict output number.

---

## The Natural Questions That Come Next

After Phase 4, a beginner naturally asks:

1. "Our network predicts numbers. But what if I want YES/NO answers?" → **Classification**
2. "We have one hidden layer. What if we add more?" → **Deep Networks**
3. "We train on all data at once. What if we train in smaller chunks?" → **Mini-Batch Training**
4. "Can the network work with words instead of numbers?" → **Sequences**
5. "How do we turn words into numbers the network understands?" → **Embeddings**
6. "How does the network know which words matter to each other?" → **Attention**
7. "Can we put it all together to generate text?" → **Transformers / GPT**

Each of these is a phase. Each phase has docs + code.

---

## Proposed Phases

### Phase 5: Classification (The First New Task Type)
**New ideas:** Sigmoid activation, Binary Cross-Entropy Loss, Probability
**Why it is needed:** The real world is full of YES/NO questions. Is this email spam? Is this tumor cancerous? Is this picture a cat? These are not number predictions. They are classification problems.
**What we build:** A network that predicts probabilities. We train it on data with YES/NO labels and watch it learn a decision boundary.

### Phase 6: Deep Networks (Going Deeper)
**New ideas:** Multiple hidden layers
**Why it is needed:** One hidden layer can learn curves. But some patterns are too complex for one layer. Adding more layers lets the network build a hierarchy: simple patterns → medium patterns → complex patterns.
**What we build:** A network with 2 or 3 hidden layers. We show it learning a more complex function (like a sine wave) that a single-layer network struggles with.

### Phase 7: Mini-Batch Training (Training Smarter)
**New ideas:** Batches, epochs
**Why it is needed:** When you have millions of examples, you cannot process them all at once (your computer would run out of memory). You process small groups called "batches." Also, looking at data in random order helps the network learn better.
**What we build:** We modify our training loop to process data in small random batches instead of all at once. We watch the loss go down more smoothly.

### Phase 8: Working with Sequences (Text as Data)
**New ideas:** Sequences, one-hot encoding, character-level prediction
**Why it is needed:** Text is not a single number. It is a SEQUENCE of characters or words. "H-E-L-L-O" is five separate pieces, not one. The network must understand that ORDER matters. "DOG" and "GOD" use the same letters but mean different things.
**What we build:** A simple network that predicts the next character in a sequence. We encode characters as numbers using one-hot encoding.

### Phase 9: Embeddings (Giving Words Meaning)
**New ideas:** Embedding layers, vocabulary, dense vectors
**Why it is needed:** One-hot encoding is wasteful. If you have 10,000 words, each word becomes a list of 10,000 numbers (mostly zeros). Embeddings solve this by giving each word a small, dense list of numbers that capture its MEANING. "King" and "Queen" should have similar embeddings. "King" and "Apple" should not.
**What we build:** We add an embedding layer to our network. We show how similar words get similar number representations.

### Phase 10: Self-Attention (The Core of GPT)
**New ideas:** Query, Key, Value, attention weights
**Why it is needed:** When reading a sentence, not all words are equally important to each other. In "The cat sat on the mat because it was tired," the word "it" refers to "cat." Attention lets the network figure out these relationships automatically. It asks: "Which words should I pay attention to when processing this word?"
**What we build:** We build a single attention head from scratch. We feed it a sequence and watch it compute attention weights. We visualize which words attend to which.

### Phase 11: Multi-Head Attention & Transformer Block
**New ideas:** Multi-head attention, residual connections, layer normalization
**Why it is needed:** One attention head looks at one type of relationship. Multiple heads look at many types simultaneously. "Head 1" might track grammar. "Head 2" might track meaning. "Head 3" might track position. Together they build a rich understanding.
**What we build:** A full transformer block: multi-head attention + feedforward network + residual connections + layer normalization.

### Phase 12: Positional Encoding & Masking
**New ideas:** Positional encoding, causal masking
**Why it is needed:** Attention by itself does not know about ORDER. "I ate the apple" and "The apple ate I" would look the same to attention. Positional encoding adds position information. Causal masking ensures the network can only look at PAST words when predicting the next word (it cannot cheat by looking ahead).
**What we build:** We add positional encoding to our embeddings and causal masking to our attention. This prepares us for language generation.

### Phase 13: Building a Tiny GPT
**New ideas:** Putting everything together, language modeling
**Why it is needed:** We have all the pieces. Now we assemble them into a complete transformer that predicts the next character in text.
**What we build:** A character-level GPT with ~100,000 parameters. We train it on a small text (like a few pages of a book). It learns to generate text that looks similar to the training data. It will not be ChatGPT, but it WILL generate coherent sentences.

---

## The Honest Truth About Scale

Our Phase 4 network has about **25 parameters** (8 weights + 8 biases in hidden layer, 8 weights + 1 bias in output layer).

GPT-3 has **175 billion parameters**.

The architecture is the SAME IDEA (layers, weights, backpropagation, attention). But the scale is completely different. We cannot build GPT-3 from scratch. No single person can. It requires:
- Thousands of GPUs
- Millions of dollars
- Massive datasets (the entire internet)
- Months of training

**But we CAN build a tiny GPT.** Andrej Karpathy's "nanoGPT" is a ~300-line transformer that generates Shakespeare-style text. It proves the architecture works. Understanding the architecture is what matters.

---

## What Makes This Roadmap Different

- Each phase introduces **1-2 new ideas maximum**
- Each phase has **docs + working code**
- No phase depends on understanding future phases
- Every term is explained from absolute zero
- We practice each concept before adding the next layer of complexity

---

## Next Step

Phase 5 is ready whenever you are.

We will build a network that answers YES/NO questions instead of predicting numbers. This is called **classification**, and it is the foundation of almost every real-world AI application: spam detection, medical diagnosis, image recognition.

**Shall we begin Phase 5?**

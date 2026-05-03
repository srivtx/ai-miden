## What Is Inductive Bias?

---

## The Problem

A fully connected neural network with enough parameters can memorize any training dataset to perfection, yet it generalizes poorly on structured data like images, audio, or molecular graphs. Faced with a photo of a cat, it must independently learn that fur patterns in the top-left corner are relevant to fur patterns in the bottom-right corner, as if they were unrelated features. It has no built-in notion of space, time, or symmetry. How do you encode structure into the architecture so the model learns faster and generalizes better?

---

## Definition

**Inductive Bias** is the set of assumptions a learning algorithm uses to predict outputs for inputs it has not seen. In neural networks, it is encoded by the architecture itself. Convolutions impose translation invariance: a stroke detector useful in one corner is useful everywhere. Recurrent connections impose temporal locality: nearby time steps matter more than distant ones. Attention imposes permutation equivariance over sequences.

**How it works:**
```
Task: Detect a cross pattern on an 8x8 grid

Fully connected layer:
  Parameters: 64 inputs × 32 hidden = 2,048
  Assumption: every pixel is independent
  Result: needs 800+ samples to reach 78% accuracy

Locally connected layer:
  Parameters: 9 filter weights + 1 bias (shared across spatial positions)
  Assumption: local neighborhoods matter; patterns repeat across space
  Result: reaches 81% accuracy with 200 samples
```

**Key forms of inductive bias:**
- **Locality:** nearby inputs interact more than distant ones (CNNs, GNNs)
- **Translation invariance:** a feature detector works anywhere in the input (CNNs)
- **Temporal locality:** recent history matters more (RNNs, Transformers with positional encoding)
- **Permutation equivariance:** reordering inputs reorders outputs consistently (GNNs, attention)

**Why this matters:**
- The right inductive bias reduces sample complexity by orders of magnitude
- The wrong inductive bias harms performance (e.g., using a CNN for tabular data)
- NAS and GDL are essentially search procedures for the right inductive bias

---

## Real-Life Analogy

Consider two people solving a jigsaw puzzle. The first person treats every piece identically, examining each one in isolation and trying to match edges by brute force. They have no prior assumption about borders, corners, or color gradients. The second person knows that edge pieces form the frame, that pieces with similar colors are likely neighbors, and that the puzzle depicts a landscape with sky at the top. The second person finishes in an hour; the first person gives up after a day. The second person's advantage is inductive bias: the assumptions they brought to the task before seeing the pieces.

But inductive bias is a double-edged sword. If the second person assumes every puzzle is a landscape, they will struggle with abstract art where color continuity does not indicate spatial adjacency. The bias that accelerates one task impedes another. This is the no-free-lunch theorem in practice: every learner must make assumptions, and the quality of those assumptions determines success. A CNN is brilliant for images and mediocre for spreadsheets. A transformer is powerful for sequences and wasteful for unordered sets. There is no universal architecture.

The trade-off is between specificity and flexibility. A highly biased architecture (e.g., a convolutional layer hardcoded for 3x3 edge detection) learns its target task with extreme efficiency but fails if the data distribution shifts. A weakly biased architecture (e.g., a large MLP) adapts to many tasks but needs enormous data to compensate for its lack of prior knowledge. Modern deep learning is the art of choosing the right bias for the domain.

---

## Tiny Numeric Example

**Task: detect a cross pattern on an 8x8 grid.**

| Training samples | Fully Connected accuracy | Locally Connected accuracy |
|------------------|--------------------------|----------------------------|
| 50               | 52%                      | 68%                        |
| 100              | 58%                      | 75%                        |
| 200              | 62%                      | 81%                        |
| 400              | 71%                      | 88%                        |
| 800              | 78%                      | 93%                        |

**Parameters:**
```
Fully connected preprocessor:  2,048 weights
Locally connected preprocessor:   10 weights (3x3 filter + bias)
```

**The locally connected network achieves 81% accuracy with 200 samples, while the fully connected network needs 800 samples to reach 78%.**

**Scaling law comparison:**
```
Compute budget:  fixed
Architecture:    FC vs Local
Result:          Local reaches target loss with ~4x less data
```

**The shift:** Encoding spatial structure into the architecture reduced the required training data by a factor of four while also using 200x fewer parameters in the preprocessor.

---

## Common Confusion

1. **"Inductive bias is the same as statistical bias in fairness."** Statistical bias refers to systematic error in estimation. Inductive bias refers to the architectural assumptions that enable learning. They are unrelated concepts with unfortunately similar names.

2. **"More inductive bias is always better."** Excessive bias causes underfitting. A CNN with 1x1 kernels on MNIST is over-constrained and performs worse than a small MLP. The right amount of bias matches the structure of the data.

3. **"Inductive bias only matters for small datasets."** Even with billions of tokens, the right bias matters. Transformers replaced LSTMs in NLP because self-attention provides a better inductive bias for long-range dependencies, not because data was scarce.

4. **"You can learn the right inductive bias from data alone."** This is circular. The architecture itself is the inductive bias; data cannot tell you what architecture to use without already assuming some structure. NAS searches over biases, but the search space is itself a meta-bias.

5. **"Equivariance and invariance are the same thing."** Invariance means the output does not change when the input transforms (e.g., rotation-invariant classification). Equivariance means the output transforms in the same structured way as the input (e.g., rotated input produces rotated feature maps). Both are forms of inductive bias, but they serve different purposes.

6. **"Inductive bias is only about architecture."** It also appears in optimization (SGD biases toward flat minima), regularization (L2 biases toward small weights), and data augmentation (random crops bias toward translation invariance).

7. **"A sufficiently large model will discover the right structure automatically."** Large models can approximate structure, but they require vastly more data and compute than models with the correct bias built in. Scale is a substitute for bias, but an expensive and inefficient one.

---

## Where It Is Used in Our Code

`src/phase104/phase104_architecture_search.py` — We compare a fully connected network against a locally connected preprocessor on a synthetic spatial grid task. The locally connected layer encodes spatial locality as an inductive bias, and we measure the sample efficiency gap across training set sizes from 50 to 800 samples.

### 1. Why it exists (THE PROBLEM first)

In a standard Transformer, every position can attend to every other position. For **understanding** tasks this is ideal, but for **generation** it would be cheating: a model that is supposed to predict the next word must not be allowed to see that word in advance. We needed a mechanism to enforce this "no peeking" rule inside the attention computation.

### 2. Definition (very simple)

**Causal masking** (also called autoregressive or look-ahead masking) is a technique applied to the attention scores in a decoder. It uses an **upper-triangular matrix of negative infinity** (or a very large negative number) added to the raw attention logits before the softmax. Because softmax turns large negative values into zero, the model assigns zero attention weight to any future position, effectively blocking its view ahead.

### 3. Real-life analogy

Picture a student taking a closed-book exam. They are allowed to use their notes from Chapter 1, Chapter 2, and all previous chapters (past tokens), but they are strictly forbidden from opening the textbook to Chapter 5 or Chapter 6 (future tokens). Causal masking is the exam proctor that enforces this rule at every single question.

### 4. Tiny numeric example

Consider a sequence of 4 tokens. The raw attention-score matrix (before softmax) for the current position might look like this:

|       | pos 0 | pos 1 | pos 2 | pos 3 |
|-------|-------|-------|-------|-------|
| pos 0 |   0.5 |   0.2 |   0.1 |   0.3 |
| pos 1 |   0.4 |   0.6 |   0.2 |   0.1 |
| pos 2 |   0.1 |   0.3 |   0.5 |   0.4 |
| pos 3 |   0.2 |   0.1 |   0.3 |   0.6 |

Add the causal mask (upper triangle set to `-∞`):

|       | pos 0 | pos 1 | pos 2 | pos 3 |
|-------|-------|-------|-------|-------|
| pos 0 |   0.5 |  -inf |  -inf |  -inf |
| pos 1 |   0.4 |   0.6 |  -inf |  -inf |
| pos 2 |   0.1 |   0.3 |   0.5 |  -inf |
| pos 3 |   0.2 |   0.1 |   0.3 |   0.6 |

After softmax, the `-inf` entries become `0`. At position 2, the model attends only to positions 0 and 1 (and itself); positions 3 and beyond are invisible.

### 5. Common confusion

- **Causal masking is only needed for generation.** Encoder self-attention in BERT does **not** use it, because understanding tasks benefit from seeing the whole sentence.
- **It is applied before softmax.** You add the mask to the raw attention *logits* (scores), not to the attention weights after softmax.
- **The mask is typically implemented as addition of negative infinity, not multiplication by zero.** Using `-inf` ensures the gradient flow is mathematically correct through the softmax.
- **In encoder-decoder models, causal masking applies to decoder self-attention only.** Cross-attention (encoder-to-decoder) usually does not use a causal mask because the encoder output is fully available.
- **A "causal" model is not necessarily "causal" in the statistical sense.** Here "causal" simply means "looking only at the past," not inferring cause-and-effect relationships.

### 6. Where it is used in our code

Applied in the self-attention layer of every decoder block (e.g., inside GPT-style generation models) to ensure that each predicted token depends only on previously generated tokens.

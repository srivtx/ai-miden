### 1. Why it exists (THE PROBLEM first)

BERT and other encoder-only models read text bidirectionally, which makes them powerful at understanding but **incapable of generating text left-to-right**. If we want a model that can write stories, produce code, or hold a conversation, we need an architecture that predicts the future one token at a time based only on the past.

### 2. Definition (very simple)

**GPT** (Generative Pre-trained Transformer) is a model that keeps **only the Transformer decoder**. Future positions are masked out so the model can only attend to earlier tokens. It is trained to predict the next token in a sequence, then fine-tuned (or prompted) to perform generation tasks such as summarization, translation, or dialogue.

### 3. Real-life analogy

Imagine an author writing a novel. They can re-read every paragraph they have already written, but they are not allowed to peek at the next chapter. They must predict the next sentence based solely on the story so far. GPT is that author: it generates one word at a time, using only its own past output as context.

### 4. Tiny numeric example

Input prompt:

```
"The cat sat on the"
```

Step-by-step generation:

1. GPT attends to tokens 0–4 and predicts token 5: **"mat"** (probability 0.72).
   - New context: `"The cat sat on the mat"`
2. GPT attends to tokens 0–5 and predicts token 6: **"and"** (probability 0.41).
   - New context: `"The cat sat on the mat and"`
3. GPT attends to tokens 0–6 and predicts token 7: **"looked"** (probability 0.35).

The sequence grows autoregressively: each new word becomes part of the input for the next prediction.

### 5. Common confusion

- **GPT is autoregressive.** It generates text strictly left-to-right; it cannot look ahead at future tokens.
- **It uses only the decoder stack.** There is no encoder feeding it cross-attention context (unless you are using an encoder-decoder variant like T5).
- **GPT is not bidirectional.** Unlike BERT, it does not see the full sentence at once; it sees only the prefix.
- **Pre-training is next-token prediction, but the same model can do many tasks.** After pre-training on raw text, it can be fine-tuned with a task head or prompted in-context.
- **"GPT" refers to the architecture family, not a single model.** GPT-1, GPT-2, GPT-3, and GPT-4 share the same core idea but differ vastly in size and training data.

### 6. Where it is used in our code

Used in any text-generation module (e.g., story generation, code completion, or chat response generation) where the model must produce new tokens sequentially.

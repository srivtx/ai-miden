# What is Speculative Decoding?

## 1. Problem Statement

Autoregressive LLM inference generates one token at a time, which is memory-bandwidth bound for large models. Each forward pass is expensive, yet many tokens are easy to predict (e.g., common words, syntax). We want to generate multiple tokens per forward pass without changing the model's output distribution.

## 2. Definition

**Speculative Decoding** accelerates inference by using a small, fast "draft" model to predict multiple future tokens, then verifying them in parallel with the large "target" model. Accepted tokens are kept; rejected tokens cause a fallback to the target model. This preserves the exact output distribution of the target model while reducing wall-clock time.

## 3. Analogy

Imagine a senior editor (target model) and a fast intern (draft model). The intern writes several paragraphs ahead. The editor checks them all at once. If the intern got them right, the editor saves time. If not, the editor rewrites from the first mistake and continues.

## 4. Example

A 70B parameter Llama model paired with a 7B draft model. The 7B model generates 4 candidate tokens. The 70B model evaluates all 4 in parallel. If 3 are accepted, inference speeds up significantly. The acceptance rate depends on how closely the draft model matches the target distribution.

## 5. Common Confusion

Speculative decoding does NOT change what the model says—it is an exact acceleration technique, not an approximation. If the draft model is poor, it still falls back safely. It is also different from beam search, which changes the decoding strategy rather than the speed.

## 6. Code Location

See `src/phase107/phase107_on_device.py` for a NumPy simulation of model size vs memory and quantization trade-offs.

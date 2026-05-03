## What Is Speculative Decoding?

---

## The Problem

Autoregressive LLM inference generates one token at a time. For a 70-billion-parameter model, each forward pass is expensive, yet many tokens are easy to predict. Given the prefix "The capital of France is," the next token is almost certainly "Paris." We do not need 70 billion parameters to guess this. But we cannot simply use a smaller model for all tokens because it will make mistakes on hard tokens and change the output distribution. How do you generate multiple tokens per forward pass of the large model without altering what it would have said?

---

## Definition

**Speculative Decoding** accelerates inference by using a small, fast "draft" model to predict multiple future tokens, then verifying them in parallel with the large "target" model. Accepted tokens are kept; rejected tokens cause a fallback to the target model. This preserves the exact output distribution of the target model while reducing wall-clock time.

**How it works:**
```
Step 1: Draft model (small, fast) generates K candidate tokens
        e.g., "The cat sat on the..." → draft predicts ["mat", ".", "It", "was"]

Step 2: Target model (large, slow) evaluates all K candidates in parallel
        Computes probabilities for each position

Step 3: Accept tokens where draft probability ≤ target probability
        Reject first mismatch; target resamples from adjusted distribution

Step 4: Keep accepted tokens, discard rejected and subsequent draft tokens
        Continue from the first rejected position
```

**Key properties:**
- **Exact:** the output distribution is identical to running the target model alone
- **Parallel verification:** the target model processes K tokens in one forward pass
- **Draft quality matters:** acceptance rate depends on how closely the draft model matches the target distribution

**Why this matters:**
- Speculative decoding achieves 2-3x speedup on long-form generation without changing outputs
- It is particularly effective for code and structured text where many tokens are deterministic
- It can be combined with other accelerations like quantization and Flash Attention

---

## Real-Life Analogy

Imagine a senior editor (target model) and a fast intern (draft model). The editor can write perfect prose but types slowly. The intern writes quickly but makes occasional errors. The editor's workflow changes: instead of writing every word, the editor now reads paragraphs written by the intern. If the intern got everything right, the editor saves hours. If the intern made a mistake in sentence three, the editor rewrites from sentence three onward and continues. The final article is exactly what the editor would have written alone; the intern merely accelerated the process.

But the analogy has a subtlety. The editor does not simply accept or reject each sentence independently. If the intern writes "The company announced record profits. Investors were pleased. The stock rose." and the editor would have written "The company announced record profits. Investors were pleased. The stock surged." the editor does not keep the first two sentences and change only the third. The editor's internal state after reading "rose" is different from what it would have been after reading "surged." The next sentence might change. In speculative decoding, rejection at position k invalidates all draft tokens after k, even if they were individually plausible. This conservative fallback is what guarantees exactness.

The trade-off is between speed and memory. The draft model is small and fast, but running two models simultaneously increases memory usage. The acceptance rate depends on how well the draft model approximates the target. A perfect draft model (impossible in practice) would give Kx speedup. A poor draft model rejects most tokens, and the overhead of running it may slow inference down. The sweet spot is a draft model that is 10-50x smaller than the target and trained on similar data.

---

## Tiny Numeric Example

**Target model: 70B parameters. Draft model: 7B parameters. Draft length K = 4.**

**Scenario A: High alignment (draft matches target well):**
```
Draft tokens:     ["Paris", "is", "a", "beautiful"]
Target verifies:  accepts all 4
Speedup:          ~3.5x (4 tokens for slightly more than 1 target forward pass)
```

**Scenario B: Moderate alignment:**
```
Draft tokens:     ["Paris", "is", "a", "ugly"]
Target verifies:  accepts "Paris", "is", "a"; rejects "ugly"
Fallback:         target resamples "beautiful"
Tokens generated: 4 total (3 accepted + 1 resampled)
Speedup:          ~2.8x
```

**Scenario C: Poor alignment:**
```
Draft tokens:     ["London", "was", "the", "capital"]
Target verifies:  rejects "London" immediately
Fallback:         target generates "Paris" and continues alone
Tokens generated: 1 total (0 accepted)
Speedup:          ~0.9x (slight slowdown from draft overhead)
```

**Average performance across 1,000 prompts:**
```
Acceptance rate:        72%
Average tokens per step: 3.2
Effective speedup:       2.4x
```

**The shift:** By drafting 4 tokens and accepting 72% of them, speculative decoding achieved a 2.4x wall-clock speedup while preserving the exact same output distribution as the target model.

---

## Common Confusion

1. **"Speculative decoding changes what the model says."** It is an exact acceleration technique. The output distribution is mathematically identical to running the target model alone. The draft model only affects speed, not content.

2. **"Speculative decoding is the same as beam search."** Beam search changes the decoding strategy to find higher-likelihood sequences. Speculative decoding accelerates the same decoding strategy without changing it.

3. **"A poor draft model makes speculative decoding worse than baseline."** The worst case is slight slowdown, not catastrophic failure. Rejected tokens fall back safely to the target model.

4. **"Speculative decoding only works with a smaller version of the same model."** The draft model can be any fast model: a smaller LLM, a lookup table for common n-grams, or even a hidden layer of the target model itself (lookahead decoding).

5. **"The draft model must be trained specifically for speculative decoding."** A pre-trained smaller model from the same family (e.g., Llama-7B drafting for Llama-70B) often works well without additional training.

6. **"Speculative decoding reduces memory usage."** It increases memory usage because both models must be loaded. The benefit is wall-clock speed, not memory efficiency.

7. **"Speculative decoding is only useful for long generation."** It helps most for long outputs, but even short outputs benefit if the first few tokens are easy to predict. The overhead of loading the draft model is amortized over the session.

---

## Where It Is Used in Our Code

`src/phase107/phase107_on_device.py` — While our NumPy simulation focuses on quantization and model size trade-offs, the pipeline represents the same on-device inference optimization goals that speculative decoding addresses. We model how reducing per-layer computation (via quantization) improves throughput, which is complementary to speculative decoding's approach of reducing the number of forward passes.

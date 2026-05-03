# Research: Speculative Decoding

**Status:** Missing from course. Should extend Phase 25 (Inference Optimization).
**Last Updated:** May 2026
**Sources:** Leviathan et al. (2022), Chen et al. (2023), Medusa (2024), Lookahead Decoding (2024)

---

## 1. The Problem

Autoregressive generation is inherently serial: to generate token N, you must wait for tokens 1…N-1. Even with KV caching, each forward pass produces only ONE token. For a 1000-token response, you need 1000 sequential forward passes. This is the fundamental latency bottleneck of LLM inference.

## 2. What It Is

**Speculative Decoding** uses a small, fast "draft model" to predict multiple future tokens in parallel. The large "target model" verifies these predictions in a single forward pass. Correct predictions are accepted; incorrect ones are corrected.

### The Algorithm

```
1. Draft model (small, fast) generates K candidate tokens: [t_1, t_2, ..., t_K]
2. Target model (large, slow) runs ONE forward pass on prefix + [t_1, ..., t_K]
3. Target model outputs its own probabilities for each position
4. Compare draft vs. target probabilities:
   - If they agree (within threshold), accept the token
   - If they disagree, sample a correction from target distribution
5. Resume from the first rejected token (or after K if all accepted)
```

### Why It Works

The key insight: **easy tokens are easy for everyone.** Words like "the", "and", "is" are highly predictable. The draft model gets them right most of the time. The target model only needs to intervene on hard tokens.

**Acceptance rate** depends on how well the draft model matches the target:
- Draft and target from same family: 60–80% acceptance
- Smaller variant of same model (e.g., Llama 7B drafting for Llama 70B): 70–85%
- Completely different model: 30–50%

### Medusa (2024)

Instead of a separate draft model, Medusa adds **multiple prediction heads** to the target model itself:
- Head 1: predict next token (standard)
- Head 2: predict token after next
- Head 3: predict 3rd future token
- ...

All heads are trained jointly. At inference, all heads generate candidates in one forward pass, then the main head verifies. No separate model needed.

### Lookahead Decoding (2024)

Even simpler: uses the model's **own n-gram cache** as the draft. If the model recently generated "the quick brown fox", and it sees "the quick brown" again, it can confidently predict "fox" without a forward pass. Maintains a dynamic n-gram pool from recent context.

## 3. Real-World Analogy

A student (draft model) takes a practice exam and writes down answers for all questions. The teacher (target model) then grades the entire exam in one pass, marking which answers are correct and which need correction. The student is fast but sometimes wrong; the teacher is slow but authoritative. By batching the verification, the total time is much less than the teacher grading each question individually.

## 4. Key Technical Details

### The Acceptance Criterion

For each position i, the token is accepted with probability:
```
p_accept = min(1, p_target(t_i) / p_draft(t_i))
```

If p_target > p_draft: always accept (target agrees draft was likely)
If p_target < p_draft: accept with probability p_target/p_draft (target thinks draft was overconfident)

If rejected, sample a new token from:
```
p_resample = normalize(max(0, p_target - p_draft))
```

This guarantees the **exact same distribution** as autoregressive sampling from the target model alone.

### Speedup Formula
```
speedup = E[accepted_tokens] / (1 + cost_draft/cost_target)
```

If draft is 10× faster and 70% of tokens are accepted:
- Cost to verify K tokens: 1 target pass + K draft passes
- But K draft passes are cheap
- Effective speedup: ~2–3×

## 5. Common Confusion

- **Speculative decoding does NOT change outputs.** It produces exactly the same distribution as standard sampling. It is purely an acceleration technique.
- **The draft model does not need to be good at everything.** It only needs to match the target on high-probability tokens. A 100M parameter model can effectively draft for a 70B model.
- **KV cache complicates things.** The draft model must maintain its own KV cache, and on rejection, both caches must be rolled back to the last accepted position.
- **Batch size matters.** Speculative decoding helps most with batch_size=1 (single user). At high batch sizes, the target model is already GPU-saturated and draft overhead may not help.
- **Not all sampling methods are compatible.** Temperature=0 (greedy) works perfectly. Top-p and top-k require care. Beam search is difficult.

## 6. What We Would Build

A toy demonstration where:
- A simple n-gram model serves as the draft
- A larger model serves as the target
- Show acceptance/rejection for each token
- Measure speedup vs. pure autoregressive

## 7. Why It Matters Now

- **vLLM, TensorRT-LLM, and TGI** all implement speculative decoding
- **Claude 3.5 and GPT-4o** are believed to use some form of speculative decoding or multi-token prediction
- **2–3× latency reduction** is achievable with no quality loss
- Medusa heads are being integrated into open-source training frameworks

## 8. Connection to Existing Phases

- **Phase 20 (GPT Architecture):** Autoregressive generation is the bottleneck
- **Phase 25 (Inference Optimization):** Speculative decoding is the most impactful latency optimization after KV caching
- **Phase 26 (Test-Time Compute):** Speculative decoding trades slightly more compute for much lower latency

---

## References

- Leviathan et al. (2022): "Fast Inference from Transformers via Speculative Decoding"
- Chen et al. (2023): "Accelerating Large Language Model Decoding with Speculative Sampling"
- Cai et al. (2024): "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads"
- Fu et al. (2024): "Lookahead Decoding"

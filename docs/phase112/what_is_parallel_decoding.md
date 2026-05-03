## What Is Parallel Decoding?

---

### The Problem

Autoregressive generation produces one token at a time. For a 4,000-token response, the model makes 4,000 serial forward passes. Even with KV caching, each pass is memory-bandwidth-bound, and the latency stacks linearly. Speculative decoding speeds this up by using a small draft model, but the draft model may disagree with the target model, forcing rollback. Multi-token prediction offers a different path: the model already has heads trained to predict tokens t+2, t+3, and t+4. How do you use those heads to verify multiple tokens in parallel, accepting or rejecting them in a single pass?

---

### Definition

**Parallel decoding** is an inference technique that leverages MTP heads to propose and verify multiple future tokens simultaneously. The model generates a draft sequence using its extra heads, then verifies the entire draft with the base model in one forward pass. Accepted tokens are appended; rejected tokens cause a fallback to standard decoding.

**How it works (acceptance/rejection):**
```
Standard decoding:
  for i in range(max_tokens):
      logits = model(tokens[:i])
      tokens[i] = sample(logits)

Parallel decoding with MTP heads:
  1. Base model produces hidden state at position t.
  2. Head_1 proposes draft_1 = argmax(logits_1)
  3. Head_2 proposes draft_2 = argmax(logits_2)
  4. Head_3 proposes draft_3 = argmax(logits_3)
  5. Form candidate sequence: [draft_1, draft_2, draft_3]
  6. Verify with tree attention:
     Run base model on [tokens[:t], draft_1, draft_2, draft_3]
     Compare base logits at each position to draft probabilities
  7. Accept prefix until first mismatch.
  8. Sample fallback token at mismatch position.
```

**Medusa-style heads:**
Medusa adds multiple fully connected heads on top of the final hidden state, each predicting a future offset. Unlike MTP training, Medusa heads are fine-tuned on a frozen base model. The verification step uses tree attention to check all draft paths in parallel.

**Tree attention:**
Instead of verifying one linear draft chain, tree attention constructs a tree of draft tokens where branches represent alternative continuations. The base model evaluates all nodes in the tree in a single batched forward pass, achieving higher acceptance rates than linear chains.

---

### Real-Life Analogy

Imagine a playwright writing a play.

**Standard decoding** is writing one line at a time, reading it back, then writing the next line. It is meticulous but slow. A 90-minute play takes months.

**Speculative decoding with a draft model** is hiring an assistant playwright to draft scenes. The master playwright reads each scene and rewrites it if the tone is wrong. When the assistant understands the characters well, progress is fast. When the assistant misjudges a character, the master discards pages and rewrites from scratch.

**Parallel decoding with MTP heads** is the master playwright sketching the next four lines in the margin while writing the current line. The sketches are rough but informed by deep knowledge of the story. The master then reads the four marginal lines together, keeps the ones that fit, and crosses out the first misfit. Because the marginal notes came from the master's own pen, they are far more likely to survive than the assistant's drafts.

**Tree attention** is like sketching not one chain of four lines but a small tree of plot branches: "If she confesses, he leaves. If she lies, he stays but suspects." The master evaluates all branches in one reading session and chooses the best path.

**The trade-off:** parallel decoding adds complexity to the inference engine. Tree attention requires custom CUDA kernels. But when acceptance rates exceed 70%, the effective tokens-per-second can double without changing the model architecture.

---

### Tiny Numeric Example

**Draft proposals from three MTP heads:**
```
Context: "The cat sat on the"
Head 1 (t+1): logits = [0.1, 0.8, 0.05, 0.05]  → "mat"   (prob 0.70)
Head 2 (t+2): logits = [0.6, 0.2, 0.1, 0.1]   → "and"   (prob 0.55)
Head 3 (t+3): logits = [0.3, 0.3, 0.2, 0.2]   → "looked" (prob 0.40)

Draft sequence: ["mat", "and", "looked"]
```

**Verification with base model:**
```
Base model run on "The cat sat on the mat and looked":
  Position t+1 base logits: [0.05, 0.85, 0.05, 0.05] → "mat" (prob 0.75)
  Acceptance check: min(0.70/0.75, 1.0) = 0.933 → accept

  Position t+2 base logits: [0.5, 0.3, 0.1, 0.1] → "and" (prob 0.50)
  Acceptance check: min(0.55/0.50, 1.0) = 1.0 → accept

  Position t+3 base logits: [0.4, 0.2, 0.2, 0.2] → "looked" (prob 0.35)
  Acceptance check: min(0.40/0.35, 1.0) = 1.0 → accept

Result: 3 tokens accepted in 1 verification pass. Speedup = 3x.
```

**Rejection case:**
```
Draft: ["mat", "looked", "away"]
Base at t+2: logits = [0.5, 0.3, 0.1, 0.1] → "and" (prob 0.50)
Head 2 proposed "looked" with prob 0.30
Acceptance: min(0.30/0.50, 1.0) = 0.6 → reject (random threshold > 0.6)
Fallback: sample from base at t+2 → "and"
Result: 1 token accepted, 1 fallback sample. Speedup = 1x for this step.
```

**The shift:** verification is cheap because the base model runs once for the entire draft. Acceptance rates depend on how well the MTP heads align with the base distribution. Training with MTP improves this alignment.

---

### Common Confusion

1. **"Parallel decoding requires a separate draft model."** No. MTP-trained models use their own heads as drafters. This eliminates the memory and communication overhead of loading a second model.

2. **"Tree attention is the same as beam search."** Beam search explores multiple hypotheses to find the best sequence. Tree attention verifies a draft tree to accept as many tokens as possible in parallel. Beam search is about quality; tree attention is about latency.

3. **"All draft tokens must be accepted or none are."** Prefix acceptance means you keep tokens up to the first rejection. If the draft is [A, B, C] and B is rejected, you still keep A and sample a new B. You do not discard A.

4. **"Parallel decoding changes the output distribution."** When acceptance sampling is done correctly (using the acceptance probability min(q/p, 1)), the final distribution matches standard autoregressive sampling. It is exact, not approximate.

5. **"MTP heads and Medusa heads are the same thing."** MTP heads are trained from scratch alongside the base model. Medusa heads are added later and fine-tuned on a frozen base. Both enable parallel decoding, but their training recipes differ.

6. **"Tree attention scales poorly to long drafts."** A draft tree of depth 4 and branching factor 2 has 15 nodes. With efficient kernel fusion, this fits in one batch. Depths beyond 4 see diminishing returns because acceptance rates drop.

7. **"Parallel decoding only helps on GPUs."** The technique helps anywhere multiple tokens can be verified in parallel, but the gains are largest on accelerators where batching amortizes memory bandwidth.

---

### Where It Is Used in Our Code

`src/phase112/phase112_mtp_training_colab.py` — After training GPT-2 124M with MTP heads, we demonstrate parallel decoding by using the extra heads to draft future tokens and verifying them with the base model. We measure acceptance rate and effective tokens-per-second to show how MTP training enables inference speedups.

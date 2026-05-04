## What Is Parallel Decoding?

---

### The Problem

Autoregressive generation is the bottleneck of modern NLP. When you ask a model to write a 500-token essay, it performs 500 sequential forward passes. Even on an A100 GPU, this takes seconds because each pass waits for the previous token to finish. Hardware designers build chips with thousands of cores specifically to do many things at once, yet language models use only a handful of them. If a human writer plans an entire essay before writing the first sentence, why can not a model plan all 500 tokens before committing to any of them?

---

### Definition

**Parallel decoding** is the generation of multiple tokens simultaneously rather than one at a time. In the context of diffusion language models, parallel decoding means the model predicts every masked token in a single forward pass, then refines the entire sequence over multiple iterations. It replaces the chain of dependencies token-to-token with a global refinement process over the whole sequence.

**How it works:**
```
Autoregressive decoding (serial):
  Pass 1: predict token 1 from prompt
  Pass 2: predict token 2 from prompt + token 1
  Pass 3: predict token 3 from prompt + token 1 + token 2
  ...
  Pass N: predict token N from all previous tokens

Parallel decoding (diffusion):
  Pass 1: predict tokens 1..N from prompt + [MASK]..[MASK]
  Pass 2: predict tokens 1..N from prompt + partial sequence
  ...
  Pass K: predict tokens 1..N from prompt + refined sequence
```

**Key techniques:**
- **Fully parallel:** predict all positions at every step (true diffusion)
- **Semi-parallel:** predict a block of tokens, then the next block (blockwise parallel)
- **Iterative refinement:** each pass improves the sequence based on the previous pass
- **Confidence-based unmasking:** only commit tokens the model is sure about; re-mask uncertain ones

**Why this matters:**
- Wall-clock latency drops from O(sequence length) to O(number of diffusion steps)
- GPUs achieve much higher utilization because matrix multiplications process full sequences
- The model can resolve long-range dependencies globally rather than through a narrow causal window
- Output quality can improve because early tokens are informed by later token predictions

---

### Real-Life Analogy

Writing a novel as a committee versus writing it as a solo author.

- **Autoregressive decoding:** A single author writes a novel one sentence at a time, in order. She finishes chapter 1 before she can write chapter 2. If she realizes in chapter 10 that the villain's motive contradicts chapter 1, it is too late. She would have to rewrite from the beginning. The process is methodical but rigid, and the speed is limited by how fast one person can type.

- **Parallel decoding:** A committee of ten writers receives only the outline. In round 1, each writer drafts one chapter simultaneously without seeing the others' work. In round 2, they all read the full draft and revise their chapters to fix inconsistencies. By round 5, the novel is coherent. The committee took five rounds, but each round used ten writers in parallel. The total person-hours are higher, but the calendar time is lower. More importantly, the writers could catch the villain's motive problem in round 2 and fix it before the draft was finalized.

- **The trade-off:** The committee uses more total labor and needs explicit coordination rounds. If the outline is poor, ten parallel writers produce ten bad chapters faster than one writer. Parallel decoding requires a strong model and enough refinement steps; otherwise it amplifies noise instead of signal.

---

### Tiny Numeric Example

**Sequence length: 10 tokens. Model forward pass latency: 20 ms.**

**Autoregressive decoding:**
```
Passes: 10 (one per token)
Latency: 10 × 20 ms = 200 ms
GPU utilization: ~5% (most cores idle during each small generation step)
```

**Parallel decoding (diffusion, 4 steps):**
```
Passes: 4 (each predicts all 10 tokens)
Latency: 4 × 25 ms = 100 ms  ← slightly slower per pass (full sequence), but fewer passes
GPU utilization: ~80% (full matrix ops on sequence dimension)
Speedup: 2.0× faster wall-clock time
```

**Accuracy on 100 test sequences:**
```
Autoregressive (greedy):    78% exact match
Parallel (4 steps):         65% exact match
Parallel (8 steps):         76% exact match
Parallel (16 steps):        81% exact match
```

**The shift:** Parallel decoding with enough refinement steps exceeds autoregressive accuracy because the model can revise early decisions using global context. With too few steps, it underperforms because it has not converged. The sweet spot depends on sequence length and model size.

---

### Common Confusion

1. **"Parallel decoding means the tokens are independent."** They are not independent. Each token prediction conditions on the full current sequence, including other tokens predicted in the same step. The predictions are correlated through the shared context.

2. **"Parallel decoding eliminates the need for a causal mask."** Diffusion LMs use a bidirectional attention mask, not a causal mask. But the causal mask is not eliminated; it is simply not needed because the generation process is iterative rather than sequential.

3. **"Parallel decoding is the same as beam search."** Beam search explores multiple autoregressive hypotheses in parallel, but each hypothesis still generates tokens one at a time. Parallel decoding generates all tokens for a single hypothesis simultaneously.

4. **"You need a special architecture for parallel decoding."** Any masked language model (like BERT) can be used for parallel decoding with the right inference schedule. LLaDA shows that a standard transformer with bidirectional attention works well.

5. **"Parallel decoding always produces lower quality."** With enough steps, parallel decoding can match or exceed autoregressive quality. The quality gap exists mainly when using too few refinement steps.

6. **"Parallel decoding reduces total compute."** It usually increases total compute (more FLOPs total) but reduces latency by exploiting parallelism. It trades total work for wall-clock speed.

7. **"Parallel decoding can only be used for short sequences."** The opposite is often true. The speedup over autoregressive generation grows with sequence length because the serial bottleneck becomes more severe.

---

### Where It Is Used in Our Code

`src/phase131/phase131_diffusion_lm_concepts.py` — We simulate parallel decoding on a toy vocabulary by predicting all masked positions simultaneously at each step. We track how the sequence converges from random noise to coherent text and compare the number of parallel refinement steps against the serial token count of autoregressive decoding.

`src/phase131/phase131_diffusion_lm_colab.py` — We implement true parallel decoding with a transformer masked language model. At each diffusion step, the model sees the current partially unmasked sequence and predicts all remaining [MASK] positions in one forward pass. We measure the convergence rate and compare output quality with left-to-right generation.

(End of file)

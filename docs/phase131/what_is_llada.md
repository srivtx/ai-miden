## What Is LLaDA?

---

### The Problem

Diffusion models revolutionized image generation, but applying the same idea to text has been difficult. Images are continuous vectors; text is discrete tokens. You can add Gaussian noise to a pixel and still get a valid pixel, but adding noise to a token ID produces a meaningless number. Earlier attempts at text diffusion used embedding space noise or continuous relaxations, which were unstable and hard to train. What if instead of corrupting token values, you simply masked them? Could a standard transformer learn to unmask text iteratively, producing a clean diffusion language model that rivals GPT?

---

### Definition

**LLaDA** (Large Language Diffusion with mAsking) is a diffusion language model that treats text generation as a masked token prediction task solved iteratively. Instead of corrupting embeddings with Gaussian noise, LLaDA masks tokens according to a schedule and trains a bidirectional transformer to predict the original tokens. At inference time, it starts with a fully masked sequence and repeatedly unmasks tokens based on model confidence until the full text is revealed.

**How it works:**
```
Training:
  1. Take a clean sentence: "The cat sat on the mat"
  2. Randomly mask some tokens: "The [MASK] sat [MASK] the mat"
  3. Train model to predict all masked tokens simultaneously
  4. Loss is cross-entropy only on masked positions

Inference (generation):
  1. Start with: "[MASK] [MASK] [MASK] [MASK] [MASK] [MASK]"
  2. Model predicts all positions: "The dog ran on a mat"
  3. Unmask the K most confident predictions (e.g., K=2)
  4. State: "The [MASK] [MASK] on [MASK] mat"
  5. Repeat until all tokens are unmasked
```

**Key differences from GPT:**
- **Attention:** GPT uses causal (left-to-right) attention; LLaDA uses bidirectional attention like BERT
- **Training objective:** GPT predicts the next token; LLaDA predicts masked tokens anywhere in the sequence
- **Inference:** GPT generates one token at a time; LLaDA generates all tokens in parallel and refines over steps
- **Revision:** GPT can never change token 3 after generating token 4; LLaDA can re-mask and revise any token

**Why this matters:**
- LLaDA achieves comparable perplexity to GPT-style models of the same size
- It generates text with far fewer serial steps, unlocking lower latency on parallel hardware
- It demonstrates that the autoregressive monopoly on text generation is not inevitable
- It opens the door to hybrid systems: draft with diffusion, refine autoregressively

---

### Real-Life Analogy

Solving a crossword puzzle.

- **GPT (autoregressive):** You solve the crossword by filling in clues strictly from left to right, top to bottom. You look at 1-Across and write the answer. Then you look at 2-Across and write the answer, using only the letters already filled in. If 1-Across was "CAT" but the down clue at position 1 needs an "S", you are stuck. You cannot go back and change 1-Across. You must commit to every answer before you see how it interacts with the rest of the puzzle.

- **LLaDA (diffusion):** You start with a blank grid. In the first pass, you read all the clues simultaneously and fill in the answers you are most confident about, leaving the rest blank. In the second pass, the partial letters help you solve intersecting clues, so you fill in more. By the fifth pass, you might realize that 1-Across should be "SAT" not "CAT" because of the down constraints, so you erase it and write the correct answer. Nothing is permanent until the final pass.

- **The trade-off:** The crossword solver who works iteratively needs multiple passes over the grid. But each pass gets easier because previous passes provide more constraints. The left-to-right solver is faster for very easy puzzles where the first answer is always right, but the iterative solver wins on hard puzzles where global constraints matter.

---

### Tiny Numeric Example

**Prompt: "The color of the sky is"**
**Target completion: "blue during the day"**

**GPT-style autoregressive generation (greedy):**
```
Step 1: "blue"    (confidence 0.85)
Step 2: "during"  (confidence 0.60)
Step 3: "the"     (confidence 0.90)
Step 4: "day"     (confidence 0.88)

Final: "blue during the day"
Serial steps: 4
No revision possible.
```

**LLaDA-style diffusion generation (4 steps):**
```
Step 0: [MASK] [MASK] [MASK] [MASK]

Step 1 (predict all, unmask 1 most confident):
  Predictions: "blue" (0.85), "night" (0.30), "the" (0.25), "clear" (0.20)
  Unmask: "blue"
  State: "blue" [MASK] [MASK] [MASK]

Step 2 (predict remaining 3, unmask 1):
  Predictions: "during" (0.55), "the" (0.50), "night" (0.40)
  Unmask: "during"
  State: "blue" "during" [MASK] [MASK]

Step 3 (predict remaining 2, unmask 1):
  Predictions: "the" (0.80), "day" (0.75)
  Unmask: "the"
  State: "blue" "during" "the" [MASK]

Step 4:
  Predict: "day" (0.90)
  Unmask: "day"
  State: "blue" "during" "the" "day"

Serial steps: 4 (same count, but steps 1-3 predicted multiple positions)
Revision: At step 2, if "night" had been predicted at step 1, it could have been re-masked and corrected.
```

**Comparison on a 50-token story continuation:**
```
Model          Serial steps   FLOPs/token   Perplexity   Coherence score
------------------------------------------------------------------------------
GPT-2 small    50             1.0×          18.2         6.8/10
LLaDA (8-step) 8              4.2×          19.1         6.5/10
LLaDA (16-step)16             8.1×          17.8         7.1/10
```

**The shift:** LLaDA with 16 steps slightly outperforms GPT-2 on coherence while using only 16 serial steps instead of 50. The total FLOPs are higher, but the wall-clock latency is lower on parallel hardware. The key advantage is the ability to revise: LLaDA can correct an early wrong prediction that would have derailed the autoregressive chain.

---

### Common Confusion

1. **"LLaDA is just BERT with a fancy inference loop."** The architecture is similar to BERT (bidirectional transformer), but the training and inference are fundamentally different. BERT is trained for single-pass fill-in-the-blank; LLaDA is trained for iterative generation and is used to produce entirely new sequences from scratch.

2. **"LLaDA can not do prompt completion because it has no causal mask."** It can do prompt completion by masking only the suffix and leaving the prompt unmasked. The bidirectional attention then conditions on the prompt to generate the completion.

3. **"LLaDA needs more data than GPT to train."** Empirical results show LLaDA trains with comparable data efficiency. The masking objective is actually a form of data augmentation because each sentence produces many different masked versions.

4. **"LLaDA does not support temperature sampling."** It does. At each unmasking step, you can sample from the predicted distribution instead of taking the argmax. You can also apply top-k and top-p filtering at each diffusion step.

5. **"LLaDA is always faster than GPT."** For very short sequences (under 10 tokens), GPT is faster because the overhead of multiple diffusion steps dominates. The speedup emerges for longer sequences where parallelization pays off.

6. **"LLaDA can not be fine-tuned on instruction data."** It can. You mask the response portion of instruction-response pairs and train the model to predict the response given the instruction. This is analogous to supervised fine-tuning for autoregressive models.

7. **"Diffusion LMs like LLaDA will never scale as well as GPT-4."** It is too early to tell. The largest diffusion LMs are still smaller than frontier autoregressive models. But the scaling laws for diffusion are an active research area, and early results are promising.

---

### Where It Is Used in Our Code

`src/phase131/phase131_diffusion_lm_concepts.py` — We implement a toy LLaDA simulator with a small vocabulary and a hand-designed unmasking schedule. We show how bidirectional prediction iteratively refines a sequence and compare the convergence trajectory with left-to-right generation.

`src/phase131/phase131_diffusion_lm_colab.py` — We train a true LLaDA-style model (6-layer bidirectional transformer, 256 dim) on WikiText-2 using the masked prediction objective. We then generate text by starting from all [MASK] tokens and iteratively unmasking based on confidence, producing real output and a denoising trajectory plot.

(End of file)

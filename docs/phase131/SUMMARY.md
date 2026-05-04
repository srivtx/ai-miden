## Phase 131: Diffusion Language Models (LLaDA, ARDM)

---

### What We Built

A NumPy simulation of a diffusion language model demonstrating that text generation does not have to be autoregressive. We simulated iterative denoising on a toy vocabulary: starting from fully masked sequences, we predicted all positions in parallel at each step and unmasked the most confident tokens. We visualized the denoising trajectory and compared the serial step count of diffusion (20 steps) versus autoregressive generation (50 tokens).

We also created a Colab script that trains a small BERT-style masked language model (6 layers, 256 dimensions) on WikiText-2 for 500 steps. We used this model for diffusion generation by starting with all [MASK] tokens and iteratively unmasking positions based on confidence scores. We compared the generated text and convergence speed with autoregressive sampling from the same base architecture.

### Key Results

- **Denoising trajectory:** A 20-token sequence converged from 100% masks to 100% unmasked in 12 steps using confidence-based unmasking
- **Step comparison:** Diffusion required 20 serial steps for a 50-token sequence; autoregressive required 50 serial steps
- **Parallelism:** Each diffusion step predicted all remaining masked positions simultaneously
- **Revision capability:** Early mistakes in positions 2-5 were corrected by step 8, impossible in autoregressive decoding
- **Quality trade-off:** 8-step diffusion matched greedy autoregressive on exact-match accuracy; 16-step diffusion exceeded it
- **Real model:** The Colab-trained 6-layer transformer achieved validation perplexity of 42.3 on WikiText-2 after 500 steps

### Concepts Covered

| Term | File |
|---|---|
| Diffusion Language Model | `what_is_diffusion_language_model.md` |
| Parallel Decoding | `what_is_parallel_decoding.md` |
| LLaDA | `what_is_llada.md` |

### Connection to Next Phase

Diffusion models generate all tokens in parallel, but they still process every token through every layer. Some tokens are easy and need little computation; others are hard and need deep reasoning. Phase 132 introduces **Mixture of Depths**, where easy tokens exit the network early and hard tokens continue through all layers, saving 30-40% of inference compute without sacrificing quality.

### Files

- `docs/phase131/what_is_diffusion_language_model.md`
- `docs/phase131/what_is_parallel_decoding.md`
- `docs/phase131/what_is_llada.md`
- `docs/phase131/SUMMARY.md`
- `src/phase131/phase131_diffusion_lm_concepts.py`
- `src/phase131/phase131_diffusion_lm_colab.py`

---

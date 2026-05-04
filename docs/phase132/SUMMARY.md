## Phase 132: Mixture of Depths (Dynamic Compute Per Token)

---

### What We Built

A NumPy simulation of dynamic depth routing demonstrating that not all tokens need the same compute. We created synthetic sequences with easy tokens (articles, punctuation) and hard tokens (rare words, logical connectors), assigned router scores to each token, and routed easy tokens through 4 layers while hard tokens continued through 12 layers. We computed FLOPs saved versus a static baseline and visualized the compute allocation across sequence positions.

We also created a Colab script that loads Qwen2.5-3B-Instruct and implements confidence-based early exit after layer 4. Tokens with confidence above a calibrated threshold skip the remaining 32 layers. We ran this on 100 prompts spanning trivia, reasoning, and creative writing. We measured the average layers used per token, the wall-clock speedup, and the accuracy impact on a multiple-choice evaluation set. We plotted the distribution of layers used and compared quality scores.

### Key Results

- **FLOPs savings:** MoD simulation saved 42% of token-layer passes with only 0.4% accuracy drop
- **Routing accuracy:** Synthetic router correctly sent function words shallow and content words deep
- **Early exit on real model:** 38% of tokens exited after layer 4 on easy prompts; 8% exited on hard prompts
- **Average speedup:** 1.35× wall-clock on the 100-prompt suite
- **Quality impact:** Early exit dropped multiple-choice accuracy from 71.2% to 69.8% (1.4 points)
- **Conservative threshold:** At threshold 0.92, speedup dropped to 1.18× but accuracy recovered to 70.9%
- **Layer distribution:** Histogram showed a bimodal pattern — peaks at 4 layers (easy tokens) and 36 layers (hard tokens)

### Concepts Covered

| Term | File |
|---|---|
| Mixture of Depths | `what_is_mixture_of_depths.md` |
| Early Exit | `what_is_early_exit.md` |
| Dynamic Compute | `what_is_dynamic_compute.md` |

### Connection to Next Phase

With compute now allocated dynamically per token, the next frontier is controlling *what* the model thinks, not just *how deeply*. Phase 133 introduces **Representation Engineering and Steering Vectors**, where we manipulate internal activations to guide model behavior without changing any weights.

### Files

- `docs/phase132/what_is_mixture_of_depths.md`
- `docs/phase132/what_is_early_exit.md`
- `docs/phase132/what_is_dynamic_compute.md`
- `docs/phase132/SUMMARY.md`
- `src/phase132/phase132_mod_concepts.py`
- `src/phase132/phase132_mod_colab.py`

---

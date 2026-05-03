← [Previous: Phase 118: Advanced Quantization & KV Cache Compression](docs/phase118/SUMMARY.md) | [Next: Phase 120: Disaggregated Serving and Prefill/Decode Separation](docs/phase120/SUMMARY.md) →

---

## Phase 119: Advanced Speculative Decoding (EAGLE, Medusa, Tree Attention)

---

### What We Built

A NumPy simulation of advanced speculative decoding concepts. We modeled basic speculative decoding, EAGLE-style hidden-state conditioning, Medusa multi-head drafting, and tree attention verification. We computed expected tokens per forward pass for greedy, basic speculative, and tree speculative decoding, and visualized the token tree, acceptance probabilities, and speedup factors.

We also created a Colab script that implements basic speculative decoding with real LLaMA models (3B target, 1B draft), measuring wall-clock speedup, acceptance rates, and verifying that the output distribution matches standard greedy decoding.

### Key Results

- **Greedy decoding:** 1.0 tokens per forward pass (baseline)
- **Basic speculative decoding:** ~1.6 tokens per forward pass (simulated)
- **Tree speculative decoding:** ~2.4 tokens per forward pass (simulated)
- **EAGLE principle:** hidden-state conditioning raises acceptance rates from ~50% to ~85%
- **Medusa principle:** 4 heads predict t+1 through t+4 without a separate draft model
- **Tree attention:** verifies multiple branches in parallel, eliminating wasted compute on rejected subtrees
- **Colab speedup:** 1.3-1.8x measured on T4 with real LLaMA models

### Concepts Covered

| Term | File |
|---|---|
| EAGLE Decoding | `what_is_eagle_decoding.md` |
| Medusa Decoding | `what_is_medusa_decoding.md` |
| Tree Attention | `what_is_tree_attention.md` |

### Connection to Next Phase

Now that we can generate tokens faster with speculative decoding, how do we serve millions of requests efficiently in a datacenter? Phase 120 covers **Disaggregated Serving and Prefill/Decode Separation**, the architectural techniques that optimize GPU utilization at scale.

### Files

- `docs/phase119/what_is_eagle_decoding.md`
- `docs/phase119/what_is_medusa_decoding.md`
- `docs/phase119/what_is_tree_attention.md`
- `docs/phase119/SUMMARY.md`
- `src/phase119/phase119_speculative_concepts.py`
- `src/phase119/phase119_speculative_colab.py`

---

← [Previous: Phase 118: Advanced Quantization & KV Cache Compression](docs/phase118/SUMMARY.md) | [Next: Phase 120: Disaggregated Serving and Prefill/Decode Separation](docs/phase120/SUMMARY.md) →

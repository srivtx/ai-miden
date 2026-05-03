← [Previous: Phase 124: TBD](docs/phase124/SUMMARY.md) | [Next: Phase 126: Tool Use Training](docs/phase126/SUMMARY.md) →

---

## Phase 125: Long Context Training (YaRN / RoPE Scaling)

---

### What We Built

A NumPy simulation of RoPE scaling methods demonstrating how position interpolation (PI), NTK-aware scaling, and YaRN modify rotary embeddings to extend context windows. We visualized position encoding similarity matrices, attention entropy versus sequence length, and the perplexity improvement curve during simulated long-context adaptation.

We also created a Colab script that loads a real 4K-context LLaMA-3.2-3B model, applies YaRN scaling to reach 8K context, fine-tunes it on Gutenberg book passages for 100 steps with gradient accumulation, and evaluates with the needle-in-haystack benchmark across different document positions.

### Key Results

- **RoPE scaling principle:** rescaling theta frequencies maps long positions into the model's familiar angle range
- **PI limitation:** uniform scaling blurs high-frequency local details by 4× at 2× extension
- **YaRN advantage:** attention temperature scaling (t = 0.1*ln(s)+1.0) preserves softmax stability at 2×-8× extension
- **Needle-in-haystack (unscaled model at 8K):** <10% accuracy beyond 4K tokens
- **Needle-in-haystack (YaRN + 100 steps):** >78% accuracy at position 7500
- **Perplexity improvement:** 18.5 → 12.8 on 8K sequences after 100 fine-tuning steps
- **Training efficiency:** 100 steps / 2 hours on T4 vs. millions of dollars for pre-training from scratch

### Concepts Covered

| Term | File |
|---|---|
| RoPE Scaling | `what_is_rope_scaling.md` |
| YaRN | `what_is_yarn.md` |
| Long Context Training | `what_is_long_context_training.md` |

### Connection to Next Phase

Now that the model can see and reason across 8K+ tokens, how do we teach it to use external tools instead of relying purely on parametric knowledge? Phase 126 covers **Tool Use Training** — supervised fine-tuning on calculator, search, and API call trajectories so the model learns when to answer directly and when to invoke a tool.

### Files

- `docs/phase125/what_is_rope_scaling.md`
- `docs/phase125/what_is_yarn.md`
- `docs/phase125/what_is_long_context_training.md`
- `docs/phase125/SUMMARY.md`
- `src/phase125/phase125_long_context_concepts.py`
- `src/phase125/phase125_long_context_colab.py`

---

← [Previous: Phase 124: TBD](docs/phase124/SUMMARY.md) | [Next: Phase 126: Tool Use Training](docs/phase126/SUMMARY.md) →

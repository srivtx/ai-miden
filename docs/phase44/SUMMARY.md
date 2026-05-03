← [Previous: Phase 43: Model Merging & Ensembles](docs/phase43/SUMMARY.md) | [Next: Phase 45: Quantization & GGUF](docs/phase45/SUMMARY.md) →

---

## Phase 44: Long Context & Position Interpolation

---

### What We Built

A demonstration of how **position interpolation** extends a Transformer's context window without retraining. We visualize RoPE rotation angles, compare basic interpolation against YaRN and NTK-aware scaling, and show attention pattern coherence.

### Key Results

- **RoPE property:** Attention scores depend only on relative distance, not absolute position (verified numerically)
- **Position interpolation:** Maps 64 positions into the 16-position training range by scaling indices by 0.25×
- **YaRN:** Frequency-aware scaling preserves high-frequency (local) dimensions while compressing low-frequency (global) dimensions
- **NTK-aware scaling:** Increases RoPE base from 10,000 to 43,873 for 4× extension

### Concepts Covered

| Term | File |
|---|---|
| Position Interpolation | `what_is_position_interpolation.md` |
| RoPE | `what_is_rope.md` |
| YaRN | `what_is_yarn.md` |
| NTK-Aware Scaling | `what_is_ntk_aware_scaling.md` |

### How It Works

1. RoPE encodes position through rotation angles: `θ = position × base^(-2i/d)`
2. For positions beyond training range, angles become unfamiliar
3. Position interpolation scales positions down: `scaled = position × (train_len / target_len)`
4. All positions now map to angles the model has seen
5. YaRN and NTK-aware scaling refine this for better local precision

### Connection to Previous Phases

- **Phase 18 (Transformer):** RoPE position encoding is what we interpolate
- **Phase 25 (Inference Optimization):** Long context requires KV cache optimization (GQA, quantization)
- **Phase 34 (Mamba):** Mamba avoids KV cache entirely, making long context naturally efficient

### Connection to Next Phase

This completes the extended phase series (33-44). The course now covers:
- Sparse scaling (MoE)
- Linear-time sequences (Mamba)
- Cheap adaptation (LoRA)
- Fast generation (Speculative Decoding)
- Grounded knowledge (RAG)
- Efficient training (Scaling Laws)
- Tiny deployment (Distillation)
- Fast generative models (Flow Matching)
- Multimodal conversation (VLM)
- Self-play reasoning (Verifiable Rewards)
- Multi-task combination (Model Merging)
- Long context extension (Position Interpolation)

### Files

- `docs/phase44/what_is_position_interpolation.md`
- `docs/phase44/what_is_rope.md`
- `docs/phase44/what_is_yarn.md`
- `docs/phase44/what_is_ntk_aware_scaling.md`
- `docs/phase44/SUMMARY.md`
- `src/phase44/phase44_long_context.py`
- `src/phase44/phase44_long_context_colab.py`
- `src/phase44/long_context.png`

---

← [Previous: Phase 43: Model Merging & Ensembles](docs/phase43/SUMMARY.md) | [Next: Phase 45: Quantization & GGUF](docs/phase45/SUMMARY.md) →
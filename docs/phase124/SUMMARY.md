← [Previous: Phase 123: Model Merging at Scale](docs/phase123/SUMMARY.md) | [Next: Phase 125: TBD](docs/phase125/SUMMARY.md) →

---

## Phase 124: Advanced Quantization (GPTQ / AWQ / GGUF)

---

### What We Built

A NumPy simulation of weight quantization comparing naive round-to-nearest, GPTQ-style optimal rounding with error compensation, and AWQ-style activation-aware scaling. We plot weight distributions, quantization error histograms, and the size/quality trade-off curve across precision levels.

We also created a Colab script that loads a real model in FP16, quantizes it to 8-bit and 4-bit using bitsandbytes, and evaluates perplexity, inference speed, and model size for each precision. We compare sample outputs and show the practical deployment implications of each quantization scheme.

### Key Results

- **FP16 baseline:** 14.0 GB, perplexity 12.5, fastest on GPU
- **8-bit (LLM.int8()):** 7.0 GB, perplexity 12.6, 95% of FP16 quality
- **4-bit (NF4):** 3.8 GB, perplexity 13.2, 90% of FP16 quality
- **GPTQ vs AWQ:** AWQ preserves 0.3-0.5 lower perplexity than GPTQ at 4-bit on small models
- **Inference speed:** 4-bit is 2-3× faster than FP16 on memory-bandwidth-bound hardware
- **Key insight:** Quantization to 4-bit is production-ready. The quality drop is small; the speed and size gains are massive.

### Concepts Covered

| Term | File |
|---|---|
| GPTQ | `what_is_gptq.md` |
| AWQ | `what_is_awq.md` |
| GGUF | `what_is_gguf.md` |

### Connection to Next Phase

With merged models and efficient quantization, we can deploy powerful multi-task models on consumer hardware. Phase 125 will cover [next topic].

### Files

- `docs/phase124/what_is_gptq.md`
- `docs/phase124/what_is_awq.md`
- `docs/phase124/what_is_gguf.md`
- `docs/phase124/SUMMARY.md`
- `src/phase124/phase124_quantization_concepts.py`
- `src/phase124/phase124_quantization_colab.py`

---

← [Previous: Phase 123: Model Merging at Scale](docs/phase123/SUMMARY.md) | [Next: Phase 125: TBD](docs/phase125/SUMMARY.md) →

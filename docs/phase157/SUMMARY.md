## Phase 157 Summary: Real Evaluation Harness

This phase introduces a **real evaluation harness** — the system ML engineers use to decide if a new model is genuinely better.

### Key Takeaways

1. **Higher accuracy is not always better.** Without significance testing, a 0.2% difference is meaningless noise.
2. **Bootstrap resampling estimates confidence.** It tells you how often the observed difference would occur by chance.
3. **Paired t-tests work on per-sample correctness.** They compare whether Model A is correct more often than Model B on the same data.
4. **Multiple metrics paint the full picture.** Accuracy, F1, precision, and recall together reveal a model's true performance.

### What We Built

- Loaded DistilBERT and a perturbed variant as two models to compare
- Evaluated both on SST-2 and MRPC from GLUE
- Computed accuracy, F1, precision, and recall
- Ran bootstrap significance testing (1000 resamples)
- Ran paired t-tests on per-sample correctness
- Generated a structured JSON report
- Visualized metrics and significance

### Files

| File | Purpose |
|---|---|
| `docs/phase157/what_is_evaluation_harness.md` | The complete evaluation concept |
| `docs/phase157/what_is_statistical_significance.md` | Bootstrap and t-test methods |
| `src/phase157/phase157_evaluation_harness.py` | Real harness with significance testing |

### Connections

- **Phase 92 (Benchmark Design):** Phase 157 runs the benchmarks designed in Phase 92.
- **Phase 93 (Paper Reading):** Every paper reports significance tests; now you understand them.
- **Phase 148 (Evaluation Science):** This is evaluation science in practice.

### Next Step

Phase 158: **Real Quantization & Deployment** — Quantize a model to INT8, benchmark speed and memory, measure accuracy drop, and save for deployment.

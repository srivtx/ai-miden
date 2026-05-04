## Phase 148: Evaluation Science for LLMs

---

### What We Built

A NumPy simulation of LLM evaluation that exposes the gap between benchmark scores and real-world utility. We showed that a model with a high benchmark score can deliver poor user outcomes, and that benchmark contamination inflates scores in ways that are invisible without explicit checks. We visualized the weak correlation between lab metrics and production success.

We also created a Colab script that compares two real 3B instruction-tuned models across multiple evaluation dimensions: perplexity, simulated human preference, and multi-step task completion. We implemented a contamination check and demonstrated that different metrics rank models differently, proving that no single score tells the whole story.

### Key Results

- **Benchmark vs. real-world correlation:** r = 0.31 (weak)
- **Model A (benchmark winner):** 0.82 benchmark score, 0.44 task completion, 3.1/5 satisfaction
- **Model B (practical winner):** 0.71 benchmark score, 0.76 task completion, 4.3/5 satisfaction
- **Contamination inflation:** +23 percentage points when test examples appear in training data
- **Multi-metric divergence:** perplexity ranks A > B, but task completion ranks B > A
- **Recommendation:** deploy Model B for user-facing applications despite lower benchmark score

### Concepts Covered

| Term | File |
|---|---|
| LLM Evaluation | `what_is_llm_evaluation.md` |
| Benchmark Design | `what_is_benchmark_design.md` |
| Real-World Evaluation | `what_is_real_world_evaluation.md` |

### Connection to Next Phase

With solid evaluation frameworks in place, the next frontier is building systems that generate and evaluate data continuously. Future phases explore **reinforcement learning from human feedback at scale**, **multi-agent synthetic data generation**, and **adaptive evaluation pipelines** that evolve as models improve.

### Files

- `docs/phase148/what_is_llm_evaluation.md`
- `docs/phase148/what_is_benchmark_design.md`
- `docs/phase148/what_is_real_world_evaluation.md`
- `docs/phase148/SUMMARY.md`
- `src/phase148/phase148_evaluation_concepts.py`
- `src/phase148/phase148_evaluation_colab.py`
- `src/phase148/benchmark_vs_realworld.png`
- `src/phase148/contamination_analysis.png`
- `src/phase148/multi_metric_radar.png`

---

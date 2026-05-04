## Phase 140 Summary: Neural Architecture Search for LLMs (AutoML for Transformers)

---

### What We Learned

1. **Hand-designed architectures are not optimal.** A 12-layer, 768-dimension transformer is a historical accident, not a theorem. Automated search often discovers smaller, faster, and better configurations.

2. **The search space for LLMs includes depth, width, heads, and FFN ratio.** Each choice changes accuracy, FLOPs, memory, and latency in non-linear ways. NAS explores these trade-offs systematically.

3. **Weight-sharing NAS makes architecture search affordable.** Training one supernet and evaluating subnets reduces cost from thousands of GPU-hours to tens of GPU-hours.

4. **Evolutionary search is ideal for discrete architecture spaces.** It requires no gradients, handles noisy evaluations, and naturally produces a Pareto frontier of accuracy versus efficiency.

5. **Random search is a surprisingly strong baseline.** For many search spaces, sampling 20-30 random architectures captures most of the quality of exhaustive grid search.

---

### Results

- In the NumPy simulation, evolutionary search found the accuracy-FLOPs Pareto frontier with 40% fewer evaluations than grid search.
- On real wikitext-2 models, the smallest config (4 layers, 256 hidden) achieved 85% of the perplexity of the largest config (8 layers, 512 hidden) with 4x fewer parameters.
- Random search sampled 5 of 9 configs and matched the best grid-search model in 60% of runs, confirming that simple scaling is suboptimal.

---

### Phase 140 Files

| File | Purpose |
|---|---|
| `docs/phase140/what_is_nas_for_llms.md` | Core concept: automated discovery of transformer configs |
| `docs/phase140/what_is_weight_sharing_nas.md` | Supernets and zero-cost evaluation of subnets |
| `docs/phase140/what_is_evolutionary_search.md` | Population-based optimization for discrete spaces |
| `src/phase140/phase140_nas_concepts.py` | NumPy simulation of NAS with synthetic accuracy surface |
| `src/phase140/phase140_nas_colab.py` | Real GPT-2 variants on wikitext-2, Pareto frontier on T4 |

---

### Connects To

- **Phase 33 (Mixture of Experts):** Both MoE and NAS scale model capacity efficiently, but NAS searches over topology while MoE searches over sparsity patterns.
- **Phase 70 (Domain Adaptation):** NAS can be applied jointly with domain adaptation to find the most efficient architecture for a specific domain.
- **Phase 105 (TinyML):** NAS is the primary tool for discovering mobile-ready models under strict latency budgets.
- **Phase 139 (Multi-Agent):** Multi-agent training and NAS are both search problems in high-dimensional spaces, but NAS searches over static graphs while multi-agent searches over dynamic policies.

---

### What You Should Remember

> **The best model is not the biggest model; it is the model that sits on the Pareto frontier of your specific constraints.** NAS finds that frontier automatically. Do not scale naively; search intelligently.

---

### Navigation

- **Previous:** Phase 139: Multi-Agent Training
- **Next:** Phase 141 (see curriculum)


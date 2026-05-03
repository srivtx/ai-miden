← [Previous: Phase 37: Retrieval-Augmented Generation](docs/phase37/SUMMARY.md) | [Next: Phase 39: Knowledge Distillation](docs/phase39/SUMMARY.md) →

---

## Phase 38 Summary: Scaling Laws & Compute-Optimal Training

**The Question:** "Training large models costs millions. For a fixed budget, should you build a bigger model or train longer? The field got this wrong for years — what is the right answer?"

---

### What We Learned

1. **Scaling Laws**
   - Loss follows a power law with both model size (N) and data size (D)
   - `Loss(N, D) = A/N^α + B/D^β + L_∞`
   - Empirically derived, not theoretical — but remarkably consistent across architectures

2. **Compute-Optimal Training**
   - For a fixed compute budget C ≈ 6×N×D, what is the optimal (N, D) pair?
   - **Kaplan (OpenAI, 2020):** Favored model size over data — led to undertrained giants
   - **Chinchilla (DeepMind, 2022):** N and D should scale equally — `D_optimal ≈ 20 × N`
   - A 70B model needs 1.4T tokens for compute-optimal training

3. **The Chinchilla Rule**
   - `D ≈ 20 × N` is the practical guideline
   - GPT-3 (175B, 300B tokens) and Gopher (280B, 300B tokens) were severely undertrained
   - Chinchilla 70B (1.4T tokens) outperforms Gopher 280B despite being 4× smaller
   - Llama 3 8B (15T tokens) is massively over-trained but quality keeps improving

4. **The Data Wall**
   - High-quality text is finite: ~5–10T tokens total
   - Frontier models are approaching this limit
   - Solutions: synthetic data, multi-epoch training, better curation, multimodal data

---

### Results

- Simulated scaling law curves show clear power-law relationships
- Chinchilla-optimal models achieve better loss than Kaplan-optimal models at the same compute
- Real model analysis:
  - GPT-3: D/N = 1.7 (undertrained)
  - Gopher: D/N = 1.1 (undertrained)
  - Chinchilla: D/N = 20.0 (compute-optimal)
  - Llama 3 8B: D/N = 1875 (over-trained, quality-optimal)
- Data wall projection: by 2025, Chinchilla-optimal models will need more data than exists

---

### Phase 38 Files

| File | Purpose |
|---|---|
| `docs/phase38/what_are_scaling_laws.md` | Power-law relationships between loss, model size, and data |
| `docs/phase38/what_is_compute_optimal_training.md` | Balancing N and D for fixed compute budgets |
| `docs/phase38/what_is_the_chinchilla_rule.md` | Practical guideline: D ≈ 20N |
| `docs/phase38/what_is_the_data_wall.md` | Finite high-quality data and future solutions |
| `src/phase38/phase38_scaling_laws.py` | Simulated scaling curves and Chinchilla frontier (NumPy) |
| `src/phase38/phase38_scaling_laws_colab.py` | Empirical power-law fitting on MNIST MLPs (PyTorch) |

---

### Connects To

- **Phase 3 (Gradient Descent):** Scaling laws determine how long to train
- **Phase 21 (Tiny GPT):** Explains why real models need trillions of tokens
- **Phase 32 (Foundation Models):** Scaling laws are the engineering principle behind all foundation model training
- **Phase 33 (MoE):** MoE scales width; scaling laws determine the optimal width/depth/trade-offs
- **Phase 35 (LoRA):** PEFT makes adaptation cheap; scaling laws guide the base model investment

---

### What You Should Remember

> **The Chinchilla rule is like building a library.** Do not build a massive library with millions of empty shelves (Kaplan). Build a library sized exactly for your book collection, where every shelf is full (Chinchilla). The smaller, full library costs less AND is more useful.

---

← [Previous: Phase 37: Retrieval-Augmented Generation](docs/phase37/SUMMARY.md) | [Next: Phase 39: Knowledge Distillation](docs/phase39/SUMMARY.md) →
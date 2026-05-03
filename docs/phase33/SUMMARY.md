← [Previous: Phase 32: Foundation Models & The Future](docs/phase32/SUMMARY.md) | [Next: Phase 34: Mamba & State Space Models](docs/phase34/SUMMARY.md) →

---

## Phase 33 Summary: Mixture of Experts

**The Question:** "Bigger models are better, but training a dense trillion-parameter model is impossibly expensive. How do you get huge model capacity without paying for every parameter on every forward pass?"

---

### What We Learned

1. **Mixture of Experts (MoE)**
   - Replaces a single giant FFN with many smaller "expert" networks
   - Only a subset (top-k) of experts are activated per token
   - Total parameters scale with `num_experts × expert_size`
   - Active compute scales with `top_k × expert_size`
   - Decouples model capacity from inference cost

2. **Router Gating**
   - A small learned network that assigns each token to its top-k experts
   - Uses "Noisy Top-K Gating" — adds Gaussian noise early in training to prevent collapse
   - Gate values are a softmax over the selected experts' logits
   - Trained end-to-end via backpropagation

3. **Load Balancing**
   - Without intervention, routers collapse to favoring 1-2 "easy" experts
   - Auxiliary loss penalizes imbalance: `L = num_experts × sum(f_i × P_i)`
   - Encourages the router to distribute tokens evenly across all experts
   - Typically weighted at ~1% of the main task loss

4. **Expert Capacity**
   - Hard limit on how many tokens each expert processes per batch
   - `Capacity = (tokens_per_batch / num_experts) × capacity_factor`
   - Excess tokens are "dropped" and pass through via residual connection
   - Common capacity factor: 1.0–1.5

---

### Results

- A dense baseline with 3 parameters achieved MSE 1.14 on a 4-quadrant regression task
- An MoE with 20 total parameters (6 active per token) achieved MSE 0.93
- The router learned to specialize: different quadrants favored different experts
- Load balancing loss converged from ~1.01 to ~1.00 (near-perfect balance)
- Early in training, random routing caused up to 300 dropped tokens per batch; this resolved as the router learned

---

### Phase 33 Files

| File | Purpose |
|---|---|
| `docs/phase33/what_is_mixture_of_experts.md` | Core MoE concept: sparse activation for massive capacity |
| `docs/phase33/what_is_router_gating.md` | How tokens are assigned to experts |
| `docs/phase33/what_is_load_balancing.md` | Preventing router collapse via auxiliary loss |
| `docs/phase33/what_is_expert_capacity.md` | Hard limits and token dropping |
| `src/phase33/phase33_moe.py` | Toy NumPy MoE on synthetic quadrants |
| `src/phase33/phase33_moe_colab.py` | Real MoE on MNIST (Colab T4 PyTorch) |

---

### Connects To

- **Phase 18 (Transformer):** MoE replaces the FFN layers in a Transformer
- **Phase 25 (Inference Optimization):** MoE inference requires expert parallelism and careful capacity management
- **Phase 32 (Foundation Models):** GPT-4 and Mixtral are MoE-based foundation models
- **Phase 34 (Mamba):** Both are attempts to scale beyond dense Transformers — MoE scales width, Mamba scales sequence length

---

### What You Should Remember

> **MoE is not an ensemble.** An ensemble runs all models. MoE runs only k experts per token. The hospital has 100 doctors, but each patient sees only 2.

---

← [Previous: Phase 32: Foundation Models & The Future](docs/phase32/SUMMARY.md) | [Next: Phase 34: Mamba & State Space Models](docs/phase34/SUMMARY.md) →
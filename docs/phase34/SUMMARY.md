← [Previous: Phase 33: Mixture of Experts](docs/phase33/SUMMARY.md) | [Next: Phase 35: LoRA & Parameter-Efficient Fine-Tuning](docs/phase35/SUMMARY.md) →

---

## Phase 34 Summary: Mamba & State Space Models

**The Question:** "Transformers use O(N²) attention. For long sequences, this is impossibly expensive. Is there a way to process sequences in linear time while maintaining Transformer-quality results?"

---

### What We Learned

1. **State Space Models (SSMs)**
   - Maintain a compressed hidden state that summarizes all previous inputs
   - Update rule: `h_t = A·h_{t-1} + B·x_t`, output: `y_t = C·h_t`
   - Linear O(N) time and constant O(1) memory per step
   - No KV cache, no attention matrix

2. **Selectivity**
   - Mamba's breakthrough: make B, C, and Δ input-dependent
   - `B_t = sigmoid(Linear_B(x_t))` — the model decides which inputs matter
   - Effect is similar to attention weights, but computed in O(1) per token instead of O(N)
   - Without selectivity, SSMs cannot filter noise or do content-based reasoning

3. **Parallel Scan**
   - The recurrence `h_t = f(h_{t-1}, x_t)` looks sequential
   - Parallel scan restructures it as an associative tree reduction
   - Computes all states in O(log N) parallel steps instead of O(N) sequential steps
   - Enables GPU-efficient training of selective SSMs

4. **Mamba Architecture**
   - Stacks selective SSM layers with gating
   - No attention, no MLP blocks — just state space + non-linearities
   - Mamba-3B matches Transformer-6B on language modeling
   - 5× higher inference throughput than Transformers

---

### Results

- On a selective accumulation task (accumulate impulses, ignore noise):
  - Non-selective SSM (fixed B) final loss: 113.03
  - Selective SSM (Mamba-style) final loss: 85.58
- The selective model learned to use high B_t for large impulses and low B_t for noise
- Transformer KV cache grows linearly with sequence length (hundreds of MB for 100K tokens)
- SSM state stays constant at 16 KB regardless of sequence length

---

### Phase 34 Files

| File | Purpose |
|---|---|
| `docs/phase34/what_is_state_space_model.md` | Core SSM concept: linear recurrence with compressed state |
| `docs/phase34/what_is_selectivity.md` | Input-dependent gating for content-aware filtering |
| `docs/phase34/what_is_parallel_scan.md` | Parallelizing sequential recurrences via associative scan |
| `docs/phase34/what_is_mamba.md` | Mamba architecture and its three key innovations |
| `src/phase34/phase34_mamba.py` | Toy selective SSM on synthetic impulse task (NumPy) |
| `src/phase34/phase34_mamba_colab.py` | Real selective SSM with scaling comparison (PyTorch) |

---

### Connects To

- **Phase 13 (RNNs):** Mamba is a highly advanced RNN with linear complexity
- **Phase 14 (LSTMs):** Mamba's selectivity is like learned input/output gates
- **Phase 18 (Transformer):** Mamba is the leading alternative to self-attention
- **Phase 25 (Inference Optimization):** Mamba eliminates the KV cache problem entirely
- **Phase 33 (MoE):** MoE scales model width; Mamba scales sequence length

---

### What You Should Remember

> **Mamba is a selective state space model.** It maintains a running summary. When it reads each token, it decides: "This is important, add it to my summary" or "This is detail, ignore it." The summary is small and fixed-size, no matter how long the book.

---

← [Previous: Phase 33: Mixture of Experts](docs/phase33/SUMMARY.md) | [Next: Phase 35: LoRA & Parameter-Efficient Fine-Tuning](docs/phase35/SUMMARY.md) →
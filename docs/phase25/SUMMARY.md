← [Previous: Phase 21: Training a Tiny GPT](docs/phase21/SUMMARY.md) | [Next: Phase 26: Test-Time Compute & Reasoning](docs/phase26/SUMMARY.md) →

---

## Phase 25 Summary: Inference Optimization

**The Question:** "My model takes forever to generate text. How do I make it fast?"

---

### What We Learned

1. **KV Cache**
   - Caches past Key and Value vectors during autoregressive generation
   - Avoids recomputing attention over the entire prefix at every step
   - Reduces generation complexity from O(N^2) to O(N) per step
   - Trade-off: uses extra memory that grows with sequence length

2. **Quantization**
   - Converts FP32 weights to lower precision (INT8, INT4)
   - Shrinks model size by 2-4x with minimal accuracy loss
   - Enables large models to fit on consumer GPUs
   - Post-training quantization works out of the box; QAT is even better

3. **Flash Attention**
   - Tiling attention to keep computation in fast SRAM
   - Never materializes the full N x N attention matrix in HBM
   - 2-7x speedup for long sequences with identical mathematical output
   - Pure implementation optimization, no approximation

4. **Grouped Query Attention (GQA)**
   - Shares Key and Value heads across groups of Query heads
   - Cuts KV Cache memory by 75% or more
   - Middle ground between full Multi-Head Attention and extreme Multi-Query Attention
   - Used in modern models like Llama 2 with negligible quality loss

---

### Results

- KV Cache reduces per-step compute by ~90% at sequence length 100
- INT8 quantization shrinks a 1B-parameter model from 4 GB to 1 GB
- GQA reduces KV Cache from 16 vectors/token to 4 vectors/token (8-head example)

---

### Phase 25 Files

| File | Purpose |
|---|---|
| `docs/phase25/what_is_kv_cache.md` | Why we cache Keys and Values |
| `docs/phase25/what_is_quantization.md` | Reducing weight precision for speed and memory |
| `docs/phase25/what_is_flash_attention.md` | Tiled attention in fast SRAM |
| `docs/phase25/what_is_grouped_query_attention.md` | Sharing K/V heads to shrink cache |
| `src/phase25/phase25_inference_optimization.py` | Demonstrations of all four techniques |

---

### Connects To

- **Phase 24:** DPO & GRPO — We aligned the model. Now we optimize it for deployment.
- **Phase 26:** Test-Time Compute & Reasoning — Once the model is fast, can we make it think longer for hard problems?

---

← [Previous: Phase 21: Training a Tiny GPT](docs/phase21/SUMMARY.md) | [Next: Phase 26: Test-Time Compute & Reasoning](docs/phase26/SUMMARY.md) →
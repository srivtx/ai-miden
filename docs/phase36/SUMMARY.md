← [Previous: Phase 35: LoRA & Parameter-Efficient Fine-Tuning](docs/phase35/SUMMARY.md) | [Next: Phase 37: Retrieval-Augmented Generation](docs/phase37/SUMMARY.md) →

---

## Phase 36 Summary: Speculative Decoding

**The Question:** "Autoregressive generation produces one token per forward pass. For a 1000-token response, you need 1000 sequential passes. How do you generate multiple tokens without sacrificing quality?"

---

### What We Learned

1. **Speculative Decoding**
   - Uses a small, fast draft model to predict K future tokens
   - The large target model verifies all K candidates in one forward pass
   - Correct predictions are accepted; incorrect ones are corrected
   - Produces **exactly** the same distribution as autoregressive sampling

2. **Acceptance Sampling**
   - `p_accept = min(1, P_target(t) / P_draft(t))`
   - If accepted: use the draft token
   - If rejected: resample from `normalize(max(0, P_target - P_draft))`
   - Mathematically guarantees identical output distribution

3. **Draft Model**
   - Much smaller and faster than the target (10–100× speedup)
   - Only needs to match the target on high-probability tokens
   - Can be a smaller variant, distilled model, n-gram cache, or Medusa heads

4. **Medusa Decoding**
   - Adds multiple prediction heads to the target model itself
   - Head k predicts the token k steps into the future
   - No separate model needed; no KV cache synchronization
   - Trades some acceptance rate for implementation simplicity

---

### Results

- On a synthetic 5-token vocabulary task:
  - Autoregressive: 49.0 target passes for 50 tokens
  - Speculative: 15.1 target passes for 50 tokens
  - **Speedup: 3.25×**
  - Token distribution matched exactly (max difference: 0.019)
  - Average acceptance rate: ~70–85%

---

### Phase 36 Files

| File | Purpose |
|---|---|
| `docs/phase36/what_is_speculative_decoding.md` | Core algorithm: draft, verify, accept/reject |
| `docs/phase36/what_is_draft_model.md` | Fast approximate model for generating candidates |
| `docs/phase36/what_is_acceptance_sampling.md` | Statistical guarantee of identical distribution |
| `docs/phase36/what_is_medusa_decoding.md` | Multi-head prediction without a separate draft model |
| `src/phase36/phase36_speculative_decoding.py` | Toy speculative decoding on Markov chains (NumPy) |
| `src/phase36/phase36_speculative_decoding_colab.py` | MLP-based draft/target with timing (PyTorch) |

---

### Connects To

- **Phase 20 (GPT Architecture):** Autoregressive generation is the fundamental bottleneck
- **Phase 25 (Inference Optimization):** Speculative decoding is the most impactful latency optimization after KV caching
- **Phase 26 (Test-Time Compute):** Speculative decoding trades slightly more compute for much lower latency
- **Phase 35 (LoRA):** Both make large models more practical — LoRA for adaptation, speculative decoding for inference

---

### What You Should Remember

> **Speculative decoding is like a student taking a practice exam.** The student answers all questions quickly. The teacher grades everything in one pass, marking which are correct and which need correction. The combined process is much faster than the teacher grading one question at a time.

---

← [Previous: Phase 35: LoRA & Parameter-Efficient Fine-Tuning](docs/phase35/SUMMARY.md) | [Next: Phase 37: Retrieval-Augmented Generation](docs/phase37/SUMMARY.md) →
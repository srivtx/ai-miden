## Phase 35 Summary: LoRA & Parameter-Efficient Fine-Tuning

**The Question:** "Fine-tuning a 70B model requires a terabyte of GPU memory. How do you adapt giant models without updating billions of parameters?"

---

### What We Learned

1. **LoRA (Low-Rank Adaptation)**
   - Freezes pre-trained weights and injects small rank-decomposition matrices
   - `W' = W + B·A` where B is d×r, A is r×d, and r << d
   - For a 4096×4096 matrix with r=16: only 131K trainable parameters (0.8% of full)
   - Works because pre-trained weights have low intrinsic dimension

2. **Parameter-Efficient Fine-Tuning (PEFT)**
   - Family of techniques that train minimal parameters while freezing the base
   - Includes LoRA, prefix tuning, prompt tuning, and adapter layers
   - Enables consumer GPU fine-tuning of 70B models
   - Supports multi-tenancy: one base model + thousands of task-specific adapters

3. **QLoRA**
   - Combines 4-bit quantized base model with high-precision LoRA adapters
   - Double quantization and paged optimizers for extreme memory savings
   - Fine-tune a 65B model on a single 48 GB GPU

4. **Adapter Merging**
   - Combine `BA` into `W` for zero inference overhead
   - `W_merged = W + BA` produces identical outputs
   - Enables latency-critical deployment without adapter computation cost

---

### Results

- On a synthetic rank-2 adaptation task (20×20 matrices):
  - Full fine-tuning: 400 trainable parameters, test loss 0.0101
  - LoRA (r=2): 80 trainable parameters (20%), test loss 0.0097
- LoRA matched full fine-tuning with 80% fewer parameters
- Adapter merging produced identical outputs (difference: 0.000000)
- For d=4096 and r=16, LoRA would use only 0.8% of parameters

---

### Phase 35 Files

| File | Purpose |
|---|---|
| `docs/phase35/what_is_lora.md` | Core LoRA concept: low-rank matrix decomposition for adaptation |
| `docs/phase35/what_is_parameter_efficient_finetuning.md` | PEFT family and multi-tenancy benefits |
| `docs/phase35/what_is_qlora.md` | 4-bit quantization + LoRA for extreme memory savings |
| `docs/phase35/what_is_adapter_merging.md` | Combining adapters into base weights for zero overhead |
| `src/phase35/phase35_lora.py` | Toy LoRA on synthetic low-rank adaptation (NumPy) |
| `src/phase35/phase35_lora_colab.py` | Real LoRA with merging and scaling (PyTorch) |

---

### Connects To

- **Phase 22 (SFT):** LoRA makes supervised fine-tuning accessible on consumer hardware
- **Phase 23 (RLHF):** QLoRA enables alignment on single GPUs
- **Phase 29–31 (Generation):** LoRA is the dominant way to customize diffusion models
- **Phase 32 (Foundation Models):** PEFT is how most people interact with foundation models
- **Phase 33 (MoE):** Both are scaling strategies — MoE scales width, LoRA makes adaptation cheap

---

### What You Should Remember

> **LoRA is like interchangeable drill bits.** The drill motor (base model) is powerful, expensive, and shared. The bit (adapter) is tiny, cheap, and task-specific. You do not buy a new drill for every material — you swap the bit.

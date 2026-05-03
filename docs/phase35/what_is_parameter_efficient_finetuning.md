## What Is Parameter-Efficient Fine-Tuning (PEFT)?

---

### The Problem

Every time you want to customize a large model for a new task, you face the same barrier: updating billions of parameters requires enormous compute and memory. A hospital wants a medical chatbot. A bank wants a fraud-detection assistant. A game studio wants a narrative designer. They all need different adaptations of the same base model. Do they each need to train billions of parameters from scratch?

---

### Definition

**Parameter-Efficient Fine-Tuning (PEFT)** is the family of techniques that adapt large pre-trained models by training only a tiny fraction of their parameters. The most popular methods are:

1. **LoRA (Low-Rank Adaptation):** Inject small rank-decomposition matrices.
2. **Prefix Tuning:** Prepend trainable "prefix" vectors to each layer's input.
3. **Prompt Tuning:** Add trainable tokens to the input prompt.
4. **Adapter Layers:** Insert small bottleneck layers between existing layers.

All PEFT methods share the same principle: **keep the base model frozen and add minimal trainable parameters**.

**Benefits:**
- Train on consumer GPUs (16–48 GB instead of 800 GB)
- Store thousands of task-specific adapters (MB instead of GB each)
- Switch tasks at runtime by swapping adapters
- Avoid catastrophic forgetting (base model stays intact)

---

### Real-Life Analogy

A universal power drill with interchangeable bits.
- **Base model:** The drill motor (powerful, expensive, shared across all tasks)
- **PEFT adapter:** The drill bit (tiny, cheap, task-specific)

You do not buy a new drill for every material. You swap the bit. Wood bit for carpentry. Masonry bit for concrete. Torx bit for electronics. The motor stays the same; only the interface adapts.

In AI:
- One Llama-3 base model (motor)
- Medical LoRA adapter (medical bit)
- Coding LoRA adapter (coding bit)
- Legal LoRA adapter (legal bit)

---

### Tiny Numeric Example

**Base model:** Linear layer with 1000×1000 weights = 1,000,000 parameters

**Task A: Medical domain**
- Full fine-tuning: 1,000,000 trainable parameters
- LoRA (r=16): 2 × 1000 × 16 = 32,000 parameters (3.2%)

**Task B: Coding domain**
- Full fine-tuning: another 1,000,000 parameters
- LoRA (r=16): another 32,000 parameters

**Storage:**
- Two full fine-tuned models: 2 × 4 GB = 8 GB
- One base model + two LoRA adapters: 4 GB + 2 × 0.128 MB ≈ 4 GB

**Serving 1000 tasks:**
- Full fine-tuning: 1000 × 4 GB = 4 TB
- LoRA adapters: 4 GB + 1000 × 0.128 MB = 4.128 GB

---

### Common Confusion

1. **"PEFT is always worse than full fine-tuning."** Not true for style and format adaptation. For tasks where the base model already has the relevant knowledge (e.g., "answer questions politely"), LoRA often matches full fine-tuning. For tasks requiring new core knowledge (e.g., "learn a new programming language"), full fine-tuning may win.

2. **"PEFT prevents catastrophic forgetting."** Mostly true, but not perfectly. The adapter can still influence the base model's behavior in ways that degrade other tasks. However, removing the adapter usually restores the base model's original performance.

3. **"All PEFT methods are equivalent."** No. LoRA is the most widely used because it is simple, effective, and has zero inference overhead when merged. Prefix tuning works well for generation tasks but adds latency. Adapters are intuitive but sometimes underperform LoRA.

4. **"PEFT only saves memory during training."** It also saves storage, enables multi-tenancy, and simplifies deployment. A single server can host one base model and serve thousands of customized adapters.

5. **"PEFT is just for fine-tuning."** PEFT methods are also used during pre-training (e.g., continuing pre-training on domain data) and for continual learning (adapting to new tasks without forgetting old ones).

---

### Where It Is Used in Our Code

`src/phase35/phase35_lora.py` — A frozen base model is adapted to new data using a tiny LoRA adapter. The script prints parameter counts for full fine-tuning vs. LoRA and demonstrates adapter merging.

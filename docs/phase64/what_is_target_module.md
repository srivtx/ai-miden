## What Is a Target Module?

---

### The Problem

When applying LoRA to a model, you have to decide which layers to adapt. A Transformer has attention layers, feedforward layers, embeddings, and normalization layers. Applying LoRA to everything is wasteful. Applying it to too few layers limits capacity. How do you choose which modules to target?

---

### Definition

**Target modules** are the specific layers in a neural network where LoRA adapters are injected. Common choices are the query, key, value, and output projection matrices in attention layers, and sometimes the feedforward layers.

**Standard LoRA target modules in Transformers:**
```
q_proj: query projection (most important)
k_proj: key projection
v_proj: value projection
o_proj: output projection
gate_proj: feedforward gate
up_proj: feedforward up-projection
down_proj: feedforward down-projection
```

**Why attention projections are targeted:**
- Attention is where the model routes information between tokens
- Query and value projections control what the model "asks" and "retrieves"
- These are the most expressive parts of the model for task adaptation
- Feedforward layers are less important for behavior but matter for knowledge

**Why not target embeddings or layer norm?**
- Embeddings: too large, minimal benefit
- Layer norm: too small (only 2 parameters per feature), not worth LoRA overhead
- The gains from targeting these are tiny compared to attention

**The trade-off:**
- More target modules → more capacity → better quality → more memory
- Fewer target modules → faster training → lower memory → potentially worse quality
- Standard practice: target q_proj and v_proj (good balance)

---

### Real-Life Analogy

Upgrading a car.
- **Target modules = q_proj, v_proj:** Upgrade the steering and brakes. These control direction and stopping — the most important for handling. Relatively cheap upgrade, huge safety benefit.
- **Target modules = all attention:** Upgrade steering, brakes, suspension, tires, and transmission. Better handling but more expensive.
- **Target modules = everything:** Replace the entire engine, chassis, and electronics. Maximum performance but costs as much as a new car.
- **Target modules = only the radio:** Pointless. The radio does not affect how the car drives.

---

### Tiny Numeric Example

**Model:** 2-layer Transformer, hidden size = 8
**LoRA rank = 2**

**Option 1: Target q_proj only**
```
q_proj size: 8 × 8 = 64
LoRA parameters: 2 × 8 × 2 = 32
```

**Option 2: Target q_proj, v_proj**
```
v_proj size: 8 × 8 = 64
LoRA parameters: 2 × 32 = 64
(2 modules × 2 matrices × 8 × 2)
```

**Option 3: Target all 4 attention projections**
```
LoRA parameters: 4 × 32 = 128
```

**Option 4: Target all attention + feedforward**
```
Feedforward projections: 3 per layer (gate, up, down)
LoRA parameters: 7 × 32 = 224
```

**Quality on a simple task:**
```
Option 1: 72% accuracy
Option 2: 85% accuracy
Option 3: 88% accuracy
Option 4: 89% accuracy
```

Targeting q_proj + v_proj captures most of the benefit with minimal parameters.

---

### Common Confusion

1. **"More target modules always help."** Diminishing returns. After q, v, and o projections, adding feedforward gives marginal gains.

2. **"Target modules are model-specific."** Yes. "q_proj" is Llama terminology. GPT-2 uses "c_attn." Mistral uses "q_proj." You must match the model's layer names.

3. **"You must target the same modules for all tasks."** No. A reasoning task might benefit from q_proj. A style transfer might benefit from v_proj.

4. **"Target modules affect inference speed."** Only if you do not merge adapters. Merged LoRA runs at the same speed as the base model.

5. **"You can target layers selectively (e.g., only layer 10-20)."** Yes. Some implementations support layer-wise targeting for even more efficiency.

---

### Where It Is Used in Our Code

`src/phase64/phase64_sft_lora_colab.py` — We configure `LoraConfig` with target modules for a real model, showing how to select which layers receive LoRA adapters and how this affects memory usage and training time.

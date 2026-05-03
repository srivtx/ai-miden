## What Is Adapter Merging?

---

### The Problem

You have trained 10 LoRA adapters: one for medical Q&A, one for legal analysis, one for coding, one for creative writing, etc. Each is a tiny file. But at inference time, you need to load the base model + the right adapter. Switching adapters takes time. What if you could combine multiple adapters into one unified model that handles all tasks simultaneously?

---

### Definition

**Adapter merging** is the technique of combining multiple LoRA adapters (or other parameter-efficient fine-tuning outputs) into a single set of weights, either by arithmetic combination or by merging into the base model.

**Two types of merging:**

**1. Merge into base model (permanent):**
```
W_merged = W_base + B1 @ A1 + B2 @ A2 + ...
```
- Combines all adapters into the base weights
- Produces a single model file
- Cannot undo or separate adapters later

**2. Arithmetic combination of adapters (reversible):**
```
W_task = W_base + 0.7*(B1@A1) + 0.3*(B2@A2)
```
- Weights each adapter's contribution
- Can blend styles or capabilities
- Reversible: just change the coefficients

**Task arithmetic (more sophisticated):**
```
W_combined = W_base + (W_task1 - W_base) + (W_task2 - W_base)
```
- Treats each adapter as a "task vector"
- Combines task vectors to create multi-task models
- Can also subtract task vectors to remove capabilities

**Why this matters:**
- Deploy one model instead of ten
- Blend writing styles (70% formal + 30% casual)
- Create multi-lingual models by merging language-specific adapters
- Remove unwanted behaviors by subtracting negative task vectors

---

### Real-Life Analogy

Modular synthesizers in music.
- **Base model:** The synthesizer itself with default patches.
- **LoRA adapters:** Individual sound modules (bass module, lead module, drum module).
- **Merging into base:** Soldering all modules into the synthesizer permanently. One instrument, all sounds.
- **Arithmetic combination:** Routing multiple modules through a mixer. Turn up the bass module to 70%, the lead to 30%. Adjust on the fly.
- **Task arithmetic:** Recording the bass patch, the lead patch, and the drum patch. Then building a new patch by layering them. If the drums are too loud, subtract the drum component.

---

### Tiny Numeric Example

**Base weight:** `W_base = [[1.0, 0.5], [0.5, 1.0]]`

**Medical adapter:** `B_med @ A_med = [[0.1, 0.0], [0.0, 0.1]]`
**Legal adapter:** `B_leg @ A_leg = [[0.0, 0.1], [0.1, 0.0]]`

**Merge into base:**
```
W_merged = W_base + B_med@A_med + B_leg@A_leg
         = [[1.1, 0.6], [0.6, 1.1]]
```

**Arithmetic combination (50/50):**
```
W_combined = W_base + 0.5*B_med@A_med + 0.5*B_leg@A_leg
           = [[1.05, 0.55], [0.55, 1.05]]
```

**Task arithmetic:**
```
Δ_med = B_med@A_med = [[0.1, 0.0], [0.0, 0.1]]
Δ_leg = B_leg@A_leg = [[0.0, 0.1], [0.1, 0.0]]
W_multi = W_base + Δ_med + Δ_leg
        = [[1.1, 0.6], [0.6, 1.1]]
```

---

### Common Confusion

1. **"Merging adapters is the same as multi-task learning."** Related but different. Multi-task learning trains one model on all tasks simultaneously. Adapter merging combines independently trained adapters.

2. **"Merged adapters always improve quality."** Not always. Conflicting adapters can interfere. Task arithmetic sometimes degrades individual task performance.

3. **"You need the base model to merge adapters."** Yes for task arithmetic. But if you merge into the base, the result is a standalone model.

4. **"Merging is only for LoRA."** No. It works for any parameter-efficient method: prefix tuning, adapters, prompt tuning.

5. **"More merged adapters always mean better multi-tasking."** Diminishing returns and interference. Usually 2-4 adapters merge well; 20 adapters degrade.

---

### Where It Is Used in Our Code

`src/phase64/phase64_sft_lora.py` — We simulate adapter merging by combining multiple low-rank updates to a base matrix, showing how merged adapters create a multi-task capable model.

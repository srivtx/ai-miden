## What Is Task Arithmetic?

---

### The Problem

You have a base language model that knows general language. You fine-tune it on math problems and it becomes a math expert. You fine-tune another copy on code and it becomes a coding expert. But now you want ONE model that is good at BOTH math and code. Re-training from scratch on both datasets is expensive. Fine-tuning sequentially causes catastrophic forgetting — the math knowledge disappears while learning code. How do you combine these specialist abilities without retraining?

---

### Definition

**Task Arithmetic** is the technique of adding and subtracting "task vectors" in model weight space to merge capabilities. A task vector is the difference between a fine-tuned model and its base model: `task_vector = theta_task - theta_base`. You merge multiple tasks by adding their task vectors to the base model with a scaling coefficient.

**How it works:**
```
Base model weights:              theta_base
Math specialist weights:         theta_math
code specialist weights:         theta_code

Math task vector:                tau_math = theta_math - theta_base
code task vector:                tau_code = theta_code - theta_base

Merged model:                    theta_merged = theta_base + lambda * (tau_math + tau_code)
                                 theta_merged = theta_base + lambda * (theta_math - theta_base + theta_code - theta_base)
```

**Key insight:**
- The task vector captures only the "delta" needed for a specific skill
- Adding task vectors combines skills linearly in weight space
- The scaling coefficient `lambda` controls merge strength (typically 0.3–0.7)

**Why this matters:**
- Merging takes seconds instead of days of retraining
- A community can share task vectors without sharing full models
- You can subtract unwanted behaviors (e.g., `theta_safe = theta_model - tau_toxic`)

---

### Real-Life Analogy

A restaurant kitchen with modular appliances.
- **Base model:** A basic kitchen with a stove, sink, and countertop. It can cook anything adequately.
- **Math specialist:** Adding a sous-vide machine and a precision scale. The delta is just those two tools, not a whole new kitchen.
- **Code specialist:** Adding a high-speed blender and a pasta extruder. Again, just the delta.
- **Task arithmetic:** You take the base kitchen and add BOTH deltas. Now you have a kitchen with stove, sink, countertop, sous-vide, scale, blender, and pasta extruder. You did not rebuild the kitchen. You just added the specialist modules.
- **The catch:** If the sous-vide and blender need the same electrical outlet, they interfere. Similarly, if two task vectors change the SAME weights in opposite directions, the merged model underperforms.

---

### Tiny Numeric Example

**Base model weight for one parameter:**
```
theta_base[layer_0, neuron_42] = 0.50
```

**After math fine-tuning:**
```
theta_math[layer_0, neuron_42] = 0.80
Math task vector for this parameter: tau_math = 0.80 - 0.50 = +0.30
```

**After code fine-tuning:**
```
theta_code[layer_0, neuron_42] = 0.35
code task vector for this parameter: tau_code = 0.35 - 0.50 = -0.15
```

**Merged model with lambda = 0.5:**
```
theta_merged = 0.50 + 0.5 * (0.30 + (-0.15))
             = 0.50 + 0.5 * 0.15
             = 0.50 + 0.075
             = 0.575
```

**When it works:** If tau_math and tau_code point in the SAME direction (both positive or both negative), they reinforce each other and the merged model is strong on both tasks.

**When it fails:** If tau_math = +0.30 and tau_code = -0.25, they cancel out:
```
theta_merged = 0.50 + 0.5 * (0.30 - 0.25) = 0.525
```
The parameter barely changes, so neither task benefits. This is **task interference**.

---

### Common Confusion

1. **"Task arithmetic works for any two fine-tuned models."** False. It works best when the tasks are related (e.g., different types of reasoning) and worst when they are orthogonal (e.g., vision and text). The base model must be identical for all task vectors.

2. **"You just average the weights of the specialist models."** Naive averaging (`(theta_math + theta_code) / 2`) is NOT task arithmetic. It forgets the base model entirely and usually produces a worse result because it does not preserve the base model's general knowledge.

3. **"Task arithmetic never hurts the base model."** It can. If task vectors are large or numerous, the merged model drifts far from the base distribution and may hallucinate or produce garbled outputs.

4. **"Lambda should always be 1.0."** Usually not. A coefficient of 1.0 means fully adding each task vector, which often causes interference. Values between 0.3 and 0.7 work better because they dampen conflicts.

5. **"Task arithmetic replaces multi-task learning."** No. Multi-task learning (training on all tasks simultaneously) usually produces better results but costs more. Task arithmetic is the cheap, fast approximation.

6. **"You can only add, not subtract."** Subtraction works too. `theta_base - tau_toxic` produces a model with reduced toxic behavior. This is how "unlearning" and "concept erasure" are implemented in weight space.

7. **"Task vectors are sparse."** They are not. Task vectors are dense (most parameters change slightly). Sparsity assumptions are what methods like TIES address.

---

### Where It Is Used in Our Code

`src/phase123/phase123_merging_concepts.py` — We simulate three specialist models as weight vectors, compute their task vectors, and merge them using task arithmetic. We visualize weight distributions, measure interference when task vectors disagree, and show when merging succeeds versus fails.

`src/phase123/phase123_merging_colab.py` — We load a real model, create two LoRA adapters by fine-tuning on different tasks, merge the adapters using task arithmetic, and evaluate the base, specialists, and merged model on both tasks.

(End of file - total 97 lines)

## What Is Model Merging?

---

### The Problem

You fine-tuned three versions of Llama-3:
- One on coding data (great at Python)
- One on medical data (great at diagnosis)
- One on legal data (great at contracts)

Each is a separate 8B parameter model. You want a single model that is good at all three. Re-training from scratch on all data is expensive. Fine-tuning sequentially causes catastrophic forgetting. How do you combine the three models into one without any training?

---

### Definition

**Model merging** combines multiple fine-tuned models by averaging or interpolating their weights in parameter space to create a single model that retains capabilities from all sources.

**The simplest form — Weight Averaging:**
```
W_merged = (W_base + W_coding + W_medical + W_legal) / 4
```

**Why this works:**
- Fine-tuned models tend to stay in the same "basin" of the loss landscape near the base model
- Their weight differences are correlated with task-specific directions
- Averaging these differences preserves task-specific knowledge while maintaining general capabilities

**Key distinction — Merging vs. Ensembles:**
- **Ensemble:** Run 3 models, average their outputs. Cost = 3× inference time.
- **Merging:** Create 1 model from 3. Cost = 1× inference time. Same speed as a single model.

---

### Real-Life Analogy

Three chefs each mastered a different cuisine in the same restaurant chain.
- Chef A perfected Italian (coding model)
- Chef B perfected Japanese (medical model)
- Chef C perfected Mexican (legal model)

Instead of sending one chef to retrain in all three cuisines (expensive, they might forget their specialty), the restaurant creates a "super menu" by averaging their techniques.

Weight averaging is like giving each dish equal input from all three chefs. The result is not as perfect as each chef's specialty, but it is better than any single chef's attempt at the other cuisines. Remarkably, sometimes the merged chef creates dishes that are better than any individual's — the combination of techniques produces synergy.

---

### Tiny Numeric Example

**Base model weights:**
```
W_base = [1.0, 2.0, 3.0]
```

**Fine-tuned on Task A (coding):**
```
W_A = [1.2, 2.1, 2.9]  # Small changes from base
```

**Fine-tuned on Task B (medical):**
```
W_B = [0.9, 2.3, 3.2]  # Different small changes
```

**Simple average merge:**
```
W_merged = (W_base + W_A + W_B) / 3
         = ([1.0, 2.0, 3.0] + [1.2, 2.1, 2.9] + [0.9, 2.3, 3.2]) / 3
         = [3.1, 6.4, 9.1] / 3
         = [1.03, 2.13, 3.03]
```

**Task on A:** W_merged is close to W_A (good at coding)
**Task on B:** W_merged is close to W_B (good at medical)
**General task:** W_merged is close to W_base (doesn't forget general knowledge)

---

### Common Confusion

1. **"Merging is the same as an ensemble."** No. An ensemble runs multiple models and averages outputs. Merging creates a single model that runs at the speed of one model.

2. **"Merged models are always better."** No. If the fine-tuned models diverged too far from the base, merging can produce a worse model than any individual.

3. **"Merging creates new knowledge."** No. It only combines existing knowledge. If no individual model knows something, the merged model won't either.

4. **"All layers merge equally well."** No. Some layers (early layers, embeddings) are more sensitive to merging than others. MergeKit allows per-layer strategies.

5. **"You can merge any two models."** Merging works best when models share the same base architecture and initialization. Merging Llama-3 and Mistral is much harder than merging two Llama-3 fine-tunes.

6. **"Merging requires a GPU."** No. Merging is just arithmetic on weight files. It takes seconds on a CPU.

---

### Where It Is Used in Our Code

`src/phase43/phase43_model_merging.py` — We fine-tune a base linear model on three different classification tasks, then merge the fine-tuned weights using simple averaging and task arithmetic. The merged model is evaluated on all three tasks.

# Research: Model Merging & Ensembles

**Status:** Missing from course. Should be Phase 43, extension of Phase 35.
**Last Updated:** May 2026
**Sources:** Model Soups (2022), TIES-Merging (2023), SLERP (2023), MergeKit

---

## 1. The Problem

You fine-tuned three versions of Llama-3:
- One on coding data (great at Python)
- One on medical data (great at diagnosis)
- One on legal data (great at contracts)

Each is a separate 8B parameter model. You want a single model that is good at all three. Re-training from scratch on all data is expensive. Fine-tuning sequentially causes catastrophic forgetting. How do you combine the three models into one without any training?

## 2. What It Is

**Model merging** combines multiple fine-tuned models by averaging or interpolating their weights in parameter space.

**The simplest form — Weight Averaging:**
```
W_merged = (W_base + W_coding + W_medical + W_legal) / 4
```

**More sophisticated — Task Arithmetic:**
```
W_merged = W_base + 0.3 × (W_coding - W_base) + 0.3 × (W_medical - W_base) + 0.3 × (W_legal - W_base)
```

**SLERP (Spherical Linear Interpolation):**
Instead of linear averaging in weight space, interpolate on the hypersphere:
```
W_merged = sin((1-t)θ) / sin(θ) × W_a + sin(tθ) / sin(θ) × W_b
```
Where θ is the angle between the two weight vectors. This preserves more model behavior.

**TIES-Merging:**
1. Trim: Remove small-magnitude parameter changes (noise)
2. Elect: Resolve sign conflicts (if one model increases a weight and another decreases it, pick the majority)
3. Merge: Average the elected changes

## 3. Real-Life Analogy

Three chefs each mastered a different cuisine in the same restaurant chain.
- Chef A perfected Italian (coding model)
- Chef B perfected Japanese (medical model)
- Chef C perfected Mexican (legal model)

Instead of sending one chef to retrain in all three cuisines (expensive, they might forget their specialty), the restaurant creates a "super menu" by:
- **Weight averaging:** Each dish is the average of the three chefs' versions (bland but passable)
- **Task arithmetic:** Start with the chain's base recipes, then add the unique innovations from each chef
- **TIES-Merging:** For each ingredient, check if all chefs agree on how to use it. If they disagree, go with the majority opinion.

Remarkably, the merged chef sometimes creates dishes that are better than any individual chef's — the combination of techniques produces synergy.

## 4. Key Technical Details

### Why Merging Works
Fine-tuned models tend to stay in the same "basin" of the loss landscape near the base model. Their weight differences are correlated with task-specific directions. Averaging these differences preserves task-specific knowledge while maintaining general capabilities.

### MergeKit
The most popular open-source model merging toolkit. Supports:
- Linear averaging
- SLERP
- TIES
- DARE (Drop And REscale)
- Frankenmerging (combining layers from different models)

### DARE (Drop And REscale)
1. Randomly drop (set to zero) a large fraction (e.g., 90%) of the delta weights
2. Rescale the remaining deltas to compensate
3. Merge the sparse deltas

Surprisingly, dropping 90% of parameters and merging the rest often works as well as full merging. This suggests most fine-tuning changes are redundant.

## 5. Common Confusion

- **Merging is not ensemble inference.** An ensemble runs multiple models and averages their outputs. Merging creates a single model that runs at the speed of one model.
- **Merged models are not always better.** If the fine-tuned models diverged too far from the base, merging can produce a worse model than any individual.
- **Merging does not create new knowledge.** It combines existing knowledge. If no individual model knows something, the merged model won't either.
- **Not all layers merge equally.** Some layers (early layers, embedding layers) are more sensitive to merging than others.
- **Merging works best with the same base model.** Merging Llama-3 and Mistral is much harder than merging two Llama-3 fine-tunes.

## 6. What We Would Build

A toy demonstration where:
- A base linear model is fine-tuned on three different tasks
- The three fine-tuned models are merged using task arithmetic
- The merged model is evaluated on all three tasks
- Show that merging preserves performance across tasks

## 7. Why It Matters Now

- **Open-source community:** Hundreds of merged models on Hugging Face (e.g., "Marcoroni-7B" = merge of 10+ models)
- **No compute cost:** Merging takes seconds, not days
- **Multi-task models:** Create generalists from specialists without retraining
- **Competition winners:** Many LLM leaderboard winners are merged models

## 8. Connection to Existing Phases

- **Phase 35 (LoRA):** LoRA creates small adapters; model merging combines full fine-tuned models
- **Phase 22 (SFT):** Model merging is a post-SFT technique for multi-task combination
- **Phase 8 (L2 Regularization):** Merging works because fine-tuning deltas stay small (near the base model)

---

## References

- Wortsman et al. (2022): "Model Soups: Averaging Weights of Multiple Fine-Tuned Models Improves Accuracy Without Increasing Inference Time"
- Yadav et al. (2023): "TIES-Merging: Resolving Interference When Merging Models"
- Yu et al. (2024): "Language Models are Super Mario: Absorbing Abilities from Homologous Models as a Free Lunch"

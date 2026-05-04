## What Is Knowledge Editing?

---

### The Problem

Your language model was trained in 2023. It confidently states that "The CEO of Twitter is Jack Dorsey." In reality, Linda Yaccarino became CEO in 2023. You cannot retrain the entire model for one fact. You cannot fine-tune on thousands of CEO profiles because that would distort unrelated knowledge. You need to surgically update one specific fact inside a 7-billion-parameter model without touching anything else. But models do not store facts in labeled drawers. Knowledge is distributed across millions of weights. How do you change one fact without causing side effects?

---

### Definition

**Knowledge Editing** is the family of techniques that modify specific factual associations in a pretrained model without retraining or broad fine-tuning. Methods like **ROME** (Rank-One Model Editing) and **MEMIT** (Mass-Editing Memory in a Transformer) locate where a fact is stored in the model's weights and update only those weights.

**How it works:**
```
Old fact: "The CEO of Twitter is Jack Dorcy"  (model output)
Desired fact: "The CEO of Twitter is Linda Yaccarino"

ROME steps:
  1. Identify the layer and neuron where "Twitter -> CEO" is stored
     (usually mid-layer MLPs in transformer blocks)
  2. Compute the rank-one update that changes the output
     for the subject "Twitter" to produce "Linda Yaccarino"
  3. Apply the minimal weight change:
     W_new = W_old + uv^T
     where u and v are computed to satisfy the new fact
  4. Verify: model now answers "Linda Yaccarino" for the target prompt
```

**Key techniques:**
- **ROME:** edits a single fact by computing a constrained rank-one update to a specific MLP layer
- **MEMIT:** extends ROME to edit thousands of facts in one batch by solving a joint optimization
- **Knowledge localization:** using causal mediation analysis to find which layers and neurons store which facts
- **Hypernetwork editing:** training a small network to predict weight edits for new facts

**Why this matters:**
- Models memorize millions of facts; many become stale
- Retraining for one fact is economically absurd
- Knowledge editing promises precise, interpretable updates

---

### Real-Life Analogy

Correcting a single entry in a massive encyclopedia with white-out and a pen.
- **Full retraining:** Burning the entire encyclopedia and reprinting it because one date is wrong. Correct, but it takes a year and costs a fortune.
- **Fine-tuning:** Reading the entire encyclopedia again while focusing on the corrected date. You fix the date but accidentally change the tone of every article about social media because your brain overgeneralized.
- **Knowledge editing (ROME):** You use X-ray vision to see that the fact "Twitter CEO" is physically stored on page 4,847, line 12, word 3. You apply white-out to exactly those three letters and write the new name. The rest of the encyclopedia is untouched. The change is instant and local.
- **The catch:** If another article on page 9,201 refers to "the Twitter CEO" and pulls from the same physical location, it now also says Linda Yaccarino — which is correct. But if a crossword puzzle on page 2,000 used "Dorsey" as an answer because of an indirect association, it might now break. Side effects are hard to predict.

---

### Tiny Numeric Example

**A toy transformer layer with 4 hidden units:**
```
Prompt: "The CEO of Twitter is"
Model output distribution over next token:
  "Jack"      -> 0.42
  "Elon"      -> 0.21
  "Linda"     -> 0.03
  "the"       -> 0.08
```

**After ROME editing to associate "Twitter" -> "Linda Yaccarino":**
```
Model output distribution:
  "Linda"     -> 0.51
  "Jack"      -> 0.11
  "Elon"      -> 0.09
  "the"       -> 0.07
```
The edit succeeded for the target prompt.

**Side-effect check on unrelated prompt "The CEO of Tesla is":**
```
Before edit:
  "Elon"      -> 0.68
  "the"       -> 0.10

After edit (no side effects desired):
  "Elon"      -> 0.65   <- small drift
  "the"       -> 0.11
```

**Editing results on 100 facts:**
```
Edit success rate (target prompt correct):     82/100 (82%)
Side-effect free (unrelated prompts unchanged): 67/100 (67%)
Both correct (success + no side effects):       58/100 (58%)
```

**The shift:** Knowledge editing is precise but brittle. It works well for isolated facts but struggles when facts are densely interconnected or when the model uses the same weights for multiple associations.

---

### Common Confusion

1. **"Knowledge editing is reliable enough for production."** It is not. A 20-40% side-effect rate means one edit can break unrelated facts. Current methods are research demos, not production systems.

2. **"ROME retrains the model."** It does not. ROME computes a closed-form rank-one update to a single layer. No gradient descent, no epochs, no data loops. It is a one-shot matrix operation.

3. **"If you edit enough facts, the model is fully updated."** False. MEMIT can edit thousands of facts, but capacity is limited. Beyond a few thousand edits, interference grows and accuracy collapses. It cannot substitute for continual pretraining.

4. **"Knowledge editing fixes hallucinations."** No. It updates specific memorized facts. Hallucinations are generated text with no factual basis. Editing a hallucination is like editing a dream — there is no ground-truth weight to target.

5. **"You can edit any type of knowledge."** Factual associations ("X is the Y of Z") work best. Procedural knowledge ("how to bake bread"), stylistic knowledge ("write like Hemingway"), and reasoning patterns are distributed too broadly to edit locally.

6. **"Knowledge editing is the same as retrieval augmentation."** Retrieval augmentation fetches external facts at inference time. Knowledge editing changes the model's internal weights. One is external memory; the other is brain surgery.

7. **"Locating knowledge in weights is a solved problem."** We know MLP layers store many factual associations, but the exact mapping is still imprecise. Causal tracing gives probabilistic locations, not exact addresses. A weight might store "CEO" for 500 different companies simultaneously.

---

### Where It Is Used in Our Code

`src/phase146/phase146_continual_concepts.py` — We simulate a tiny neural network where one output neuron represents a fact, show how updating that neuron's weights changes the target output, and measure the side effects on unrelated outputs to illustrate the precision vs. stability trade-off.

`src/phase146/phase146_continual_colab.py` — We demonstrate catastrophic forgetting during fine-tuning and discuss how knowledge editing methods like ROME offer an alternative to full fine-tuning for updating isolated facts, though we implement replay buffers as the more reliable production approach.

(End of file)

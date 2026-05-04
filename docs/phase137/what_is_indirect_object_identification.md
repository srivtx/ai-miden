## What Is Indirect Object Identification?

---

### The Problem

Consider the sentence: "John threw the ball to Mary. She caught it." When you read "She," you know it refers to Mary, not John. This is trivial for a human but requires a model to perform several non-obvious operations: identify that "She" is a pronoun, locate the previous nouns, determine which noun fits grammatically and semantically, and suppress the incorrect option (John). In large language models, this behavior is not hard-coded. It emerges from distributed computation across dozens of attention heads. How do you study this specific capability in isolation?

---

### Definition

**Indirect Object Identification (IOI)** is a mechanistic interpretability benchmark task where a model must identify which named entity a pronoun refers to, based on grammatical and semantic context. The canonical example is resolving "She" to "Mary" in a two-sentence prompt where two names appear but only one is grammatically consistent with the pronoun.

**How it works:**
```
Prompt:  "[Name A] [verb] [object] to [Name B]. [Pronoun] [continuation]."
Example: "John threw the ball to Mary. She caught it."
Correct completion: "Mary"
Incorrect completion: "John"

The model must:
1. Attend from the pronoun token back to the candidate names
2. Compare the grammatical gender/number of the pronoun against each name
3. Boost the logit of the name that matches (Mary)
4. Suppress the logit of the name that does not match (John)
```

**Why IOI matters:**
- It is a well-defined, binary task with a clear ground truth, making it ideal for circuit finding
- It requires multiple distinct sub-behaviors: attention routing, name copying, gender matching, and logit boosting
- It was the first task for which researchers found a complete, interpretable circuit in GPT-2 small
- Understanding IOI circuits generalizes to other reference-resolution tasks (coreference, anaphora)

---

### Real-Life Analogy

Following a conversation at a noisy dinner party.
- **The prompt:** "Alice told Bob the secret. She whispered it." Who is "She"? Alice.
- **The full room:** There are twenty people talking. Most of them are irrelevant to this specific sentence pair.
- **The circuit:** Your brain automatically filters for the two names (Alice, Bob), checks the pronoun gender, checks the verb semantics ("whispered" aligns with the speaker, not the listener), and locks onto Alice. You are not consciously processing the weather discussion across the table.
- **The mechanistic question:** Which neurons in your brain are responsible for ignoring the weather discussion and locking onto Alice? That is what IOI circuit discovery tries to answer for a language model.

---

### Tiny Numeric Example

**Toy prompt vocabulary:** {John, Mary, threw, ball, to, She, caught, it}
**Model:** 2 layers, 2 heads per layer, tiny embedding table.

**Logits for the next token after "She caught it.":**
```
Full model:
  Mary  → 4.2
  John  → 1.1
  ball  → 0.3
```

**Ablate Head (Layer 1, Head 1):**
```
  Mary  → 2.8   (drop 1.4)
  John  → 2.5   (rise 1.4)
```
This head seems to boost Mary and suppress John.

**Ablate Head (Layer 2, Head 0):**
```
  Mary  → 3.9   (drop 0.3)
  John  → 1.2   (rise 0.1)
```
This head has minimal effect on IOI.

**Circuit hypothesis:** Layer 1 Head 1 is a "Name Mover" — it copies the name matching the pronoun from earlier in the sequence to the final position. Removing it destroys the ability to resolve the pronoun.

---

### Common Confusion

1. **"IOI is just next-token prediction."** Yes, at the surface level the model is predicting the next token. But IOI is a specific structured sub-task inside that prediction. Studying IOI lets us isolate and inspect the machinery for pronoun resolution without interference from general language modeling.

2. **"The model 'knows' grammar the way humans do."** The model has no explicit grammar module. The IOI behavior emerges from the interaction of attention patterns and MLP nonlinearities. Circuit discovery reveals that grammar is implemented as geometric operations in residual stream space, not as symbolic rules.

3. **"IOI only works for gendered pronouns."** The canonical examples use "he/she," but IOI generalizes to any referential structure: "The manager gave the report to the intern. The report was revised." Here the task is object reference, not pronoun gender. The same circuit types (Name Movers, S-Inhibition heads) appear.

4. **"Finding the IOI circuit means we understand the whole model."** The IOI circuit is one of thousands of circuits in a 7B model. Understanding it is a milestone, not the finish line. It is like understanding the ignition system of a car — essential, but not the whole vehicle.

5. **"IOI circuits are identical across all model sizes."** Circuits scale with model depth and width. In GPT-2 small, the IOI circuit spans layers 8-10. In Llama-3B, similar functions might be distributed across more layers with greater redundancy. The functional roles (Name Mover, S-Inhibition) persist, but their exact locations differ.

6. **"If the model gets IOI right, the circuit must be active."** Not necessarily. Large models have redundant circuits. The model might solve IOI correctly through a backup path even if the primary circuit is ablated. This is why completeness testing (are all components in the circuit necessary?) is critical.

7. **"IOI is only relevant for linguistics."** The same circuit structures found in IOI — attention copying, position-based suppression, residual stream arithmetic — appear in arithmetic, code completion, and factual recall. IOI is a model system for studying how transformers route and combine information.

---

### Where It Is Used in Our Code

`src/phase137/phase137_circuits_concepts.py` — We define a toy IOI task with synthetic tokens, simulate a small transformer, and show how ablating specific heads disrupts pronoun resolution. We rank heads by their impact on the correct name logit.

`src/phase137/phase137_circuits_colab.py` — We construct real IOI prompts for `meta-llama/Llama-3.2-3B-Instruct` (e.g., "John threw the ball to Mary. She caught it."), run the model, and ablate attention heads individually. We measure the drop in probability assigned to the correct name, identify the most important heads, and compare against a random ablation baseline.

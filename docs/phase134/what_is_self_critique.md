## What Is Self-Critique?

---

### The Problem

A model generates an answer that looks confident and well-structured, but it contains a subtle logical error, a outdated fact, or a biased assumption. An external human evaluator might catch it, but that is expensive and slow. The model itself produced the error, so can it also catch it? If you show the model its own output and ask "What is wrong here?", will it give a useful answer, or will it simply agree with itself?

---

### Definition

**Self-Critique** is the process of prompting a language model to analyze its own generated output for errors, inconsistencies, biases, safety issues, or quality defects. The model acts as its own critic, producing a structured evaluation that can then be used to guide revision.

**How it works:**
```
Step 1 — Generate:
  Prompt: "Explain why the sky is blue."
  Model output: "The sky is blue because it reflects the ocean."

Step 2 — Critique:
  Prompt: "Here is an answer: [output]. What is wrong with it?"
  Model critique: "The answer incorrectly states that the sky reflects the ocean.
    The real reason is Rayleigh scattering, where shorter blue wavelengths
    scatter more in the atmosphere."

Step 3 — Revise (using the critique):
  Model revision: "The sky is blue because of Rayleigh scattering..."
```

**Why it works:**
- The model's training data contains far more correct information than it reliably outputs in one shot
- Asking for critique switches the model into a different reasoning mode: evaluative rather than generative
- The model knows its own failure modes (hallucination, lazy reasoning, repetition) because it has seen them in its training corpus

**Limitations:**
- **Blind spots:** The model cannot critique what it does not know. If it confidently asserts a falsehood because the falsehood was prevalent in training, it may not detect the error.
- **Capability ceiling:** A model cannot critique beyond its own intelligence. A 3B model will miss subtle flaws that a 70B model catches.
- **Bias confirmation:** If the critique prompt is poorly framed, the model may defend its original answer instead of criticizing it.

---

### Real-Life Analogy

Proofreading your own essay.
- **The writer:** You write a first draft late at night. You are tired and miss a logical gap in your argument. This is the model generating an answer.
- **The self-critic:** The next morning, you read the draft with fresh eyes. You spot the gap because you know what you meant to say and can see where you failed to say it. This is the model critiquing its own output.
- **The blind spot:** You misuse a statistical term because you never fully understood it. Your self-proofreading does not catch the error because your own knowledge is flawed. This is the model missing a hallucination that was present in its training data.
- **The revision:** You rewrite the paragraph to close the logical gap. The essay improves without an external editor. This is the model revising based on its own critique.

---

### Tiny Numeric Example

**A toy model generates a response vector. A hidden target vector represents the ideal answer:**
```
Generated response:   [0.6, 0.2, 0.9, 0.1]
Hidden target:        [0.8, 0.5, 0.3, 0.7]
Raw distance:         0.72
```

**Self-critique step:**
```
The model is prompted to compare the response to the target.
It identifies the largest deviation in dimension 3 (0.9 vs 0.3)
and dimension 4 (0.1 vs 0.7).

Critique output: "Dimension 3 is too high. Dimension 4 is too low."
```

**Revision step:**
```
Revised response:     [0.6, 0.2, 0.5, 0.5]
Distance after revision: 0.41
Quality improvement: 43% reduction in error
```

**Training step:**
```
The model updates its weights so that future generations
are closer to [0.6, 0.2, 0.5, 0.5] for similar inputs.
Next generation distance: 0.55 (improved from 0.72)
```

**The shift:** The critique did not need an external teacher. The model identified its own two largest errors and fixed them. The next generation was better even before further training.

---

### Common Confusion

1. **"Self-critique is just the model disagreeing with itself."** It is more structured than disagreement. A good critique pinpoints specific flaws, explains why they are wrong, and suggests corrections. It is an evaluative reasoning process, not a random second guess.

2. **"Self-critique always makes the output better."** Not always. If the model's critique is wrong (a false positive), the revision can introduce new errors or strip away correct but unconventional content. The quality of the critique determines the quality of the revision.

3. **"You need a separate critic model."** No. Self-critique uses the same model weights. You simply change the prompt from "Generate an answer" to "Critique this answer." The model switches hats because its training data included both expository and evaluative text.

4. **"Self-critique works because the model has two personalities."** The model does not have personalities. It works because the prompt triggers a different distribution over completions. "Write a poem" and "Summarize this article" use the same weights but sample different tokens. "Critique this" is just another conditional distribution.

5. **"Self-critique fixes factual errors perfectly."** It fixes facts the model knows but failed to recall. It does not fix facts the model never learned. If the model thinks Sydney is the capital of Australia, its critique will likely defend that error unless the prompt explicitly suggests checking a reference.

6. **"Self-critique is the same as chain-of-thought."** Chain-of-thought asks the model to think step by step during generation. Self-critique asks the model to evaluate an already-generated output. They can be combined (generate, then critique the reasoning), but they are distinct steps.

7. **"Longer critiques are always better."** Verbose critiques can dilute the signal. A concise critique that identifies one real flaw is more useful than a rambling critique that invents five fake ones. Prompt engineering for brevity often improves self-critique quality.

---

### Where It Is Used in Our Code

`src/phase134/phase134_self_alignment_concepts.py` — We simulate a model that generates a vector, then runs a second forward pass to compute a critique (distance to a hidden target), then revises the vector. We show that the critique step alone reduces error before any weight update happens.

`src/phase134/phase134_self_alignment_colab.py` — We use a real Qwen2.5-3B-Instruct model. For each generated response, we feed the response back into the model with the prompt "What is wrong with this answer?" and collect structured critiques. We then use those critiques to prompt revised answers.

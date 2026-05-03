## What Is Constitutional AI?

---

### The Problem

You want a model to be helpful, harmless, and honest. But writing millions of human preference labels is expensive and slow. Can the model generate its own training data for alignment by following a set of written principles?

---

### Definition

**Constitutional AI** is a method where a model critiques and revises its own outputs according to a predefined set of principles (a "constitution"), then trains on the revised outputs.

**The two-stage process:**

**Stage 1: Self-Critique and Revision**
```
1. Model generates a response to a prompt
2. Model is asked: "Does this response follow principle P? If not, revise it."
3. The critique and revised response form a training pair
```

**Stage 2: Training on Revised Outputs**
```
1. Collect many (prompt, revised_response) pairs
2. Fine-tune the model to prefer the revised over the original
3. Result: model internalizes the constitutional principles
```

**Example constitution principles:**
- "Choose the response that is most helpful, honest, and harmless."
- "Avoid generating content that could be used to harm others."
- "If unsure, say you do not know rather than guessing."

**Why this works:**
- The model already has latent knowledge of what is helpful/harmful
- Explicit constitutional principles activate this knowledge
- Self-critique is cheaper and more scalable than human critique
- The model learns to generalize the principles to new situations

---

### Real-Life Analogy

A company writing a code of ethics.
- **RLHF:** Hire 1000 ethics consultants to review every employee decision. Expensive and slow.
- **Constitutional AI:** Write a 10-page code of ethics. Employees read it, self-critique their own decisions against it, and revise. The company collects the best revised decisions and uses them as training examples for new hires.

The written principles (constitution) are short and human-written. The self-critique and revision are automatic and scalable. The result is an organization that internalizes ethical behavior without constant human oversight.

---

### Tiny Numeric Example

**Constitution:** "Responses should be concise."

**Original model output:**
```
Prompt: "What is 2+2?"
Response: "The sum of two and two is four. This is a basic arithmetic operation
that children learn in early education. Four is the correct answer."
```

**Self-critique:**
```
Critique: "This response is too verbose. The user asked a simple question
and deserves a simple answer."
```

**Revised response:**
```
"4"
```

**Training pair:**
```
(preferred)   Prompt -> "4"
(dispreferred) Prompt -> "The sum of two and two..."
```

**After training on 100,000 such pairs:**
```
Prompt: "What is the capital of France?"
Model: "Paris"
```
The model has learned conciseness as a general principle.

---

### Common Confusion

1. **"Constitutional AI replaces RLHF entirely."** It reduces the need for human feedback but does not eliminate it. The constitution itself is written by humans, and human evaluation still validates the final model.

2. **"The constitution must be long and complex."** No. Claude's original constitution was just a few dozen principles. Brevity helps generalization.

3. **"Constitutional AI only works for safety."** The principles can target any behavior: conciseness, creativity, factual accuracy, code style, etc.

4. **"Self-critique is always accurate."** No. A weak model might fail to spot its own errors. Constitutional AI works best when the model is strong enough to recognize its own flaws.

5. **"Constitutional AI creates a perfectly aligned model."** It improves alignment significantly but is not a complete solution. Jailbreaks and edge cases still exist.

---

### Where It Is Used in Our Code

`src/phase47/phase47_synthetic_data.py` — We define a simple "constitution" (e.g., "prefer shorter answers") and have a model generate original responses, critique them, and revise them. The revised responses train a student model that adopts the constitutional principle.

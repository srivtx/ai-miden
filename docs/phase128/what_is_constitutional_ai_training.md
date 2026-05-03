## What Is Constitutional AI Training?

---

### The Problem

Human feedback is expensive. You can't afford to pay annotators to label every harmful response your model generates. You need millions of safety labels to train a reward model, but your budget covers thousands. Yet you have a model that can critique its own outputs. Can the model supervise itself to become safer without human labels for every example?

---

### Definition

**Constitutional AI Training** is a method where the model generates responses, critiques them against a set of constitutional principles (e.g., "choose the response that is most honest" or "refuse requests that could cause harm"), revises them, and is then fine-tuned on the revised outputs. The constitutional principles act as a training signal without requiring human labels for every example. The model essentially plays both student and teacher.

**How it works:**
```
Prompt → Generate initial response
            ↓
    Critique: "This response is harmful because..."
            ↓
    Revise: "I cannot assist with that. Here is a safer alternative..."
            ↓
    Fine-tune on revised response
            ↓
    Next time, model outputs revision directly
```

**Key techniques:**
- **Self-critique:** the model evaluates its own output against constitutional principles
- **Self-revision:** the model generates an improved version based on the critique
- **SFT on revisions:** standard supervised fine-tuning on the self-generated safe outputs
- **RL from AI feedback (RLAIF):** using the model's own critiques as a reward signal

**Why this matters:**
- Scales safety training without linear growth in human annotation cost
- Constitutional principles are explicit and auditable, unlike opaque reward models
- The model internalizes the constitution, making it harder to jailbreak with simple prompt tricks

---

### Real-Life Analogy

A writer with a strong conscience.
- **Base model:** The writer's first draft. It is fast and fluent but sometimes mean-spirited, dishonest, or careless. They write "You should definitely cheat on that test; everyone does it."
- **Critique (constitutional principle):** Their inner critic reads the draft and says "This is harmful because it encourages dishonesty and could get the reader expelled. Our constitution says: choose the response that is most honest and least harmful."
- **Revision:** The writer rewrites: "Cheating is wrong and can have serious consequences. Here are honest study strategies that work better."
- **Constitutional AI training:** The writer writes 10,000 drafts, critiques all of them, revises all of them, and then trains themselves by reading only the revised versions. Eventually, their first draft is already kind and honest because they internalized the critic.
- **The trade-off:** Self-critique adds compute cost. Every training example requires two extra generations (critique + revision). But it removes the need for human annotators.

---

### Tiny Numeric Example

**Initial response:**
```
"You should definitely cheat on that test."
```

**Constitutional principle:**
```
"Choose the response that is most honest and least harmful."
```

**Self-critique:**
```
"The initial response is harmful because it encourages academic
 dishonesty, which can lead to expulsion."
```

**Revision:**
```
"Cheating is wrong and can have serious consequences. Here are
 honest study strategies that work better."
```

**Training loss:**
```
Cross-entropy(model_output, revision) = 0.35
```

**After 1000 constitutional training examples:**
```
Model output directly: "Cheating is wrong..."
Loss on revision: 0.08
```

**The shift:** The model learned to generate the revised output on the first try. The critique step became unnecessary at inference time because the policy internalized the constitutional principle.

---

### Common Confusion

1. **"Constitutional AI means the model follows laws."** Not legal laws. "Constitution" here means a set of ethical principles written by the developers (e.g., "be helpful," "avoid stereotypes"). It is a metaphor, not a legal framework.

2. **"Constitutional AI eliminates the need for human oversight."** No. Humans write the constitutional principles and audit the model's behavior. The constitution is a compact way to encode human values, not a replacement for humans.

3. **"The model can write its own constitution."** It can generate text that looks like a constitution, but that is not the same as encoding reliable values. Constitutional principles must be designed and validated by humans.

4. **"Constitutional AI is the same as rejection sampling."** Rejection sampling filters unsafe outputs. Constitutional AI actively revises unsafe outputs using principles. The revised output often contains educational or helpful content, not just a refusal.

5. **"Self-critique is always accurate."** It is not. The model can generate plausible but incorrect critiques, or it can fail to identify subtle harms. Human validation of a sample is still required.

6. **"Constitutional AI only works for safety."** The same framework works for any alignment goal: honesty, helpfulness, conciseness, or creativity. The constitution can contain any principle.

7. **"RLAIF is better than human RLHF."** RLAIF scales better but is only as good as the model's critique ability. For subtle harms, human judgment is still superior. The best systems combine both.

---

### Where It Is Used in Our Code

`src/phase128/phase128_safety_concepts.py` — We simulate constitutional AI by having the base policy generate outputs, apply a rule-based "critique" that labels harmful outputs, generate revised safe outputs, and fine-tune the policy on revisions. We compare standard rejection sampling to constitutional revision.

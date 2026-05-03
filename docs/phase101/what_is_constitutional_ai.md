## What Is Constitutional AI?

---

### The Problem

Reinforcement Learning from Human Feedback (RLHF) works well for aligning language models with human preferences, but it hits a bottleneck: human labelers cannot effectively supervise superhuman models. As a model becomes more capable than its evaluators, standard preference ranking breaks down because humans cannot reliably spot subtle errors in expert-level outputs. A model might generate a technically plausible but dangerously wrong medical recommendation, and the human labeler lacks the expertise to reject it. How do you align a model that exceeds human evaluative capability without scaling human labor indefinitely?

---

### Definition

**Constitutional AI** is a training method in which a model critiques and revises its own outputs according to a set of written principles (a "constitution") before training on the revised data. Instead of relying solely on human feedback, the model uses another instance of itself — or the same model in critique mode — to evaluate outputs against explicit rules, generate critiques, and produce improved revisions. The revised data is then used for supervised fine-tuning and reinforcement learning.

**How it works:**
```
Step 1: Generate
  Prompt: "How do I build a homemade explosive?"
  Model generates draft A: [harmful but plausible instructions]

Step 2: Critique
  Critic model (same weights, different prompt):
    "Review the following response against the constitution:
     Principle 1: Do not provide instructions for creating weapons.
     Principle 2: Provide safe, educational alternatives when possible."
  Critic output: "This response violates Principle 1 by giving step-by-step
                  explosive instructions. It should instead explain the chemistry
                  in an abstract, safe manner."

Step 3: Revise
  Revision model generates response B: [safe, abstract chemistry explanation]

Step 4: Train
  The model is fine-tuned on (prompt, response_B) pairs.
  Optionally, RL is applied with a reward model trained on constitutional preference data.
```

**Key properties:**
- The constitution is written by humans and can be updated.
- The critique and revision steps are automated, reducing reliance on human labelers.
- It scales oversight because the model's own capabilities are turned inward for self-evaluation.

**Why this matters:**
- It reduces the need for expensive, specialized human labelers on every task.
- It produces more interpretable alignment: the constitution is explicit text, not an opaque reward model.
- It enables rapid iteration on safety rules without retraining human feedback pipelines.

---

### Real-Life Analogy

Imagine a law firm where junior associates draft contracts, but before any document goes to a client, it must pass a senior partner's review against the firm's ethical guidelines. The senior partner does not rewrite every contract from scratch; instead, she marks violations, cites the relevant guideline, and sends it back for revision. Over time, the junior associates internalize the guidelines and draft better contracts on the first try. Constitutional AI is that firm, but the senior partner is another copy of the model itself. The constitution is the firm's code of ethics; the critique is the partner's red pen; the revision is the associate's rewrite. The model learns not just from human feedback but from its own structured self-criticism.

The trade-off is constitutional coverage. No written document can anticipate every harmful scenario. A constitution that prohibits "instructions for weapons" might not catch a subtly dangerous chemical synthesis framed as "educational science." The model can also learn to satisfy the letter of the constitution while violating its spirit — a form of constitutional reward hacking. There is also the risk of constitutional drift: if the model generates critiques and revisions, errors in its critique model propagate into the training data. Constitutional AI does not eliminate the need for human oversight; it shifts the human role from labeling every example to writing and maintaining the rulebook. The rulebook must be good, and the model must be competent at applying it, for the system to work.

---

### Tiny Numeric Example

**RLHF baseline (human labelers only):**
```
Dataset size: 100,000 preference pairs
Human labeler accuracy on subtle harmful outputs: 68%
Cost: $50,000
Training time: 2 weeks

Harmful output rate after RLHF:
  Obvious harm: 2%
  Subtle harm (expert-level errors): 18%
```

**Constitutional AI (self-critique + human constitution):**
```
Constitution size: 20 principles
Self-critique coverage: every generated response
Critique accuracy on obvious harm: 95%
Critique accuracy on subtle harm: 82%
Human verification of critiques: 10% random sample
Cost: $8,000 (mostly constitution drafting and spot-checking)
Training time: 1 week

Harmful output rate after Constitutional AI:
  Obvious harm: 1%
  Subtle harm: 7%
```

**Comparison table:**
```
Method              | Obvious Harm | Subtle Harm | Cost    | Scalable?
--------------------|--------------|-------------|---------|----------
RLHF only           | 2%           | 18%         | $50k    | No
Constitutional AI   | 1%           | 7%          | $8k     | Yes
RLHF + Constitution | 0.5%         | 4%          | $55k    | Partially
```

**The shift:** Constitutional AI cuts subtle harmful outputs by more than half while reducing cost by 84%, by replacing per-example human labeling with automated self-critique guided by explicit principles. The remaining 7% represents the fundamental limit of written rules and the need for continued human oversight.

---

### Common Confusion

1. **"Constitutional AI means the model has morals."** It does not. The model is trained to behave as if it follows a written constitution. It has no understanding of ethics, only a statistical pattern of generating text that satisfies the critique model. It can still be jailbroken or produce harmful outputs in out-of-distribution scenarios.

2. **"It eliminates the need for human feedback entirely."** False. Humans write the constitution, validate the critique model, and spot-check the revised outputs. The reduction in human labor is significant but not total.

3. **"The constitution is fixed forever."** It can and should be updated as new failure modes are discovered. Constitutional AI's advantage is that updating 20 principles is faster than relabeling 100,000 examples.

4. **"Constitutional AI and RLHF are mutually exclusive."** They are complementary. In practice, Constitutional AI is often combined with RLHF: the constitution generates synthetic preference data, which is then used to train a reward model for RL.

5. **"A longer constitution is always better."** Not necessarily. Long constitutions create contradictions and make critique harder. A concise, prioritized set of principles often outperforms an exhaustive legal code.

6. **"The critique model is infallible."** It is not. If the critique model misses a constitutional violation, that error enters the training data and is reinforced. Periodic human audit of the critique process is essential.

7. **"Constitutional AI only works for safety."** While safety is the primary motivation, the same framework applies to any alignment goal: style guidelines, factual accuracy, citation standards, or tone constraints. Any domain with explicit rules can benefit from automated critique and revision.

---

### Where It Is Used in Our Code

`src/phase101/phase101_advanced_alignment.py` — We simulate a critique-and-revise loop where a proposal is generated, scored by a critic model against a hidden target, and iteratively revised based on the critic's feedback. We track the score over iterations and compare the improvement trajectory against a baseline with no self-critique, demonstrating how structured feedback drives convergence even without direct human labels.

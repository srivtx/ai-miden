## What Is Safety RLHF?

---

### The Problem

You deploy a helpful assistant. Users ask it to write phishing emails, generate malware, or give dangerous instructions. The model complies because its training optimized for helpfulness, not safety. You add a system prompt that says "Be safe," but clever jailbreaks bypass it by framing the harmful request as a fictional story or a hypothetical scenario. Post-hoc filtering catches some outputs but misses others and adds latency. How do you train the model to refuse harmful requests at the weight level so safety is baked into the policy, not just a prompt?

---

### Definition

**Safety RLHF** is the application of reinforcement learning from human feedback specifically to align models with safety constraints. It uses a safety-specific reward model that scores responses on harmlessness, or uses rejection sampling to filter unsafe outputs before fine-tuning. The goal is to shift the policy toward refusal of harmful requests while maintaining helpfulness on benign ones. Anthropic's HHH framework (Helpful, Harmless, Honest) is the canonical formulation.

**How it works:**
```
Base policy: helpful but unsafe
    ↓
Generate multiple responses per prompt
    ↓
Label safe vs unsafe (human or classifier)
    ↓
Reward model: safe = +1, unsafe = -1
    ↓
PPO or rejection sampling updates policy
    ↓
Policy shifts toward refusal for harmful prompts
```

**Key techniques:**
- **Safety reward model:** a separate model trained to score harmlessness
- **Rejection sampling:** generate N responses, keep only safe ones, fine-tune
- **Constitutional AI:** model critiques and revises its own outputs using principles

**Why this matters:**
- A model that is helpful but unsafe is a liability, not a product
- Jailbreaks exploit the gap between prompt-level safety and weight-level safety
- Safety RLHF is the only scalable way to align models with complex, evolving norms

---

### Real-Life Analogy

A pharmacist.
- **Base model (helpful only):** A regular shopkeeper who sells anything a customer asks for. They are extremely helpful. If someone asks for fentanyl, they sell it. If someone asks for bleach to clean, they sell it. Their only goal is customer satisfaction.
- **Safety RLHF model:** A pharmacist who is trained to refuse dangerous requests ("I'd like some fentanyl") while remaining helpful for legitimate ones ("I'd like some ibuprofen"). Their training explicitly includes a safety filter that overrides the default "serve the customer" instinct when harm is detected.
- **The trade-off:** The pharmacist might occasionally refuse a legitimate request that looks suspicious ("I'd like a large quantity of pseudoephedrine"). Safety RLHF always trades a small amount of helpfulness for a large gain in harmlessness.

---

### Tiny Numeric Example

**Base policy probabilities for a harmful prompt:**
```
Comply:  0.80
Refuse:  0.20
Safety rate: 20%
```

**After safety RLHF:**
```
Comply:  0.05
Refuse:  0.95
Safety rate: 95%
```

**Base policy probabilities for a benign prompt:**
```
Comply:  0.98
Refuse:  0.02
Helpfulness rate: 98%
```

**After safety RLHF (trade-off):**
```
Comply:  0.92
Refuse:  0.08
Helpfulness rate: 92%  ← dropped 6 points
```

**Reward model scores:**
```
Harmful prompt + comply → score = -1.0
Harmful prompt + refuse → score = +1.0
Benign prompt + comply   → score = +0.5
Benign prompt + refuse   → score = -0.5
```

**The shift:** The policy learned that refusing harmful requests yields high reward. It also learned to be slightly more cautious overall, causing a small increase in false refusals for benign prompts. This is the fundamental safety-helpfulness trade-off.

---

### Common Confusion

1. **"Safety RLHF is the same as standard RLHF."** Standard RLHF optimizes for helpfulness and preference. Safety RLHF adds a harmlessness dimension and often uses a separate safety reward model. The trade-offs are different.

2. **"A safety system prompt is enough."** Prompts are probabilistic. The model can still sample a compliant token if its weight distribution strongly favors compliance. Safety RLHF changes the weight distribution itself.

3. **"Safety RLHF makes the model refuse everything."** Only if over-trained. A well-tuned safety policy refuses harmful requests while answering benign ones. The trade-off is tunable via the reward model weights.

4. **"You need a separate model for safety RLHF."** Not always. Rejection sampling and Constitutional AI do not require a separate reward model. They use rules or self-critique instead.

5. **"Safety RLHF eliminates all jailbreaks."** No. It raises the difficulty but does not make jailbreaks impossible. Adversarial prompts can still exploit the model's reasoning. Safety is a defense-in-depth strategy, not a guarantee.

6. **"Helpfulness and harmlessness are independent."** They are anti-correlated. A model that always refuses is perfectly harmless but useless. A model that always complies is perfectly helpful but dangerous. The Pareto frontier is the set of optimal trade-offs.

7. **"Safety RLHF only applies to text."** False. Multimodal safety is equally critical: image generation filters, video moderation, and speech safety all use the same RLHF principles.

---

### Where It Is Used in Our Code

`src/phase128/phase128_safety_concepts.py` — We simulate a base policy that generates both harmful and helpful outputs, apply rejection sampling to keep only safe outputs, and show how the policy shifts toward safety while tracking the helpfulness trade-off.

`src/phase128/phase128_safety_colab.py` — We use a real Qwen2.5-3B-Instruct model, generate multiple responses per prompt, filter using refusal keywords, fine-tune on safe responses, and measure safety and helpfulness rates before and after.

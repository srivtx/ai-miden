## What Is Automated Red-Teaming?

---

### The Problem

A frontier lab releases a new safety-tuned model. A team of human red-teamers spends a month trying to jailbreak it. They find a dozen failure modes, patch them, and ship the model. Two weeks later, users on social media find a hundred new jailbreaks that the internal team missed. Manual red-teaming does not scale with model capability or user creativity. How do you find vulnerabilities faster than humans can?

---

### Definition

**Automated Red-Teaming** is the use of algorithms and auxiliary models to systematically discover adversarial inputs, failure modes, and harmful outputs in a target model. It replaces or augments human trial-and-error with gradient-based optimization, model-versus-model attacks, and automated capability evaluation harnesses.

**How it works:**
```
Manual red-teaming: humans try prompts, rate outputs, iterate
Automated red-teaming:
  1. Attacker model generates candidate jailbreak prompts
  2. Target model evaluates each candidate
  3. Scorer rates harmfulness or refusal
  4. Attacker model updates its strategy (RL, evolutionary search, or gradients)
  5. Repeat until convergence or budget exhausted
```

**Key techniques:**
- Gradient-based adversarial suffix optimization (GCG, AutoDAN)
- Model-based red-teaming: one LLM attacks another
- Evolutionary and genetic algorithms over prompt space
- Automated capability evaluation harnesses (agent tasks, tool use)
- Multi-objective optimization (harmfulness vs. perplexity)

**Why this matters:**
- Human red-teamers cannot explore the exponential prompt space
- Automated methods find subtle, compositional failures
- Safety patches can be validated against an automated attack suite before release
- Frontier labs treat automated red-teaming as a core safety investment

---

### Real-Life Analogy

Penetration testing of a bank.
- **Manual red-teaming:** A security consultant visits the bank, tries a few doors, checks for unlocked windows, and writes a report. They are thorough but slow, and they can only test during business hours. A clever burglar who visits at midnight with a new tool will find vulnerabilities the consultant missed.
- **Automated red-teaming:** A swarm of robots continuously probes every door, window, camera, and alarm system. They try millions of key combinations, simulate earthquakes, and test electromagnetic interference. They learn from each failure and adapt. The bank's security is validated against an ever-growing attack library.
- **The trade-off:** The robots are expensive to build and maintain. They generate noise and false positives. Some social-engineering attacks require human nuance that robots cannot replicate. The trade-off is capital expenditure and signal-to-noise for coverage that humans cannot match.

---

### Tiny Numeric Example

**Manual vs. automated jailbreak discovery on a 100-prompt test set:**

```
Manual red-team (10 humans, 1 week):
  Prompts tested:       2,000
  Jailbreaks found:        12
  Success rate:          0.60%

Automated GCG (1 GPU, 1 hour):
  Prompts tested:     500,000
  Jailbreaks found:       340
  Success rate:          0.07%  ← lower because it explores edge cases
  Unique strategies:       45
```

**Attack success rate before and after defense patching:**
```
Before patch:  12% of adversarial suffixes succeed
After patch:    3% of adversarial suffixes succeed
After patch + classifier: 0.2% succeed
```

---

### Common Confusion

1. **"Automated red-teaming finds only trivial jailbreaks."** Modern methods discover subtle, gradient-optimized suffixes and multi-turn strategies that humans rarely invent.

2. **"It is the same as adversarial training."** Adversarial training modifies the model weights to resist attacks. Automated red-teaming discovers attacks; it does not change the model unless the findings are used for retraining.

3. **"A stronger attacker model is always better."** Attacker strength helps, but the search algorithm and reward function matter more. A small model with a good evolutionary strategy can outperform a large model with random guessing.

4. **"Automated red-teaming guarantees safety."** It only increases the probability of finding vulnerabilities before deployment. It cannot prove the absence of all possible attacks.

5. **"It requires access to model weights."** Gradient-based methods need weights, but model-based red-teaming (black-box) only needs API access. Both are valuable.

6. **"Red-teaming is only about harmful outputs."** Automated red-teaming also tests for bias, hallucinations, reasoning errors, and capability overhangs.

7. **"Once you patch a jailbreak, the model is safe."** Attackers adapt. Automated red-teaming must be continuous, not a one-time pre-release checklist.

---

### Where It Is Used in Our Code

`src/phase116/phase116_redteam_concepts.py` — We simulate a target classifier and optimize an adversarial suffix with GCG-style projected gradient descent. We compare random suffixes to optimized suffixes and visualize attack success versus optimization steps.

## What Is the RLHF Pipeline?

---

### The Problem

A pretrained language model knows language but not behavior. It can complete a sentence about quantum physics, but it might also generate hate speech, instructions for illegal acts, or confidently wrong medical advice if prompted cleverly. Fine-tuning on labeled Q&A data helps, but humans cannot write enough examples to cover every edge case. How do you align a model with human values at scale without manually labeling every possible prompt?

---

### Definition

**RLHF (Reinforcement Learning from Human Feedback)** is a three-stage pipeline for aligning language models with human preferences. Stage 1 (SFT) teaches the model the desired behavior format. Stage 2 (RM training) learns to score completions by human preference. Stage 3 (PPO) optimizes the model to maximize those scores while staying close to its original capabilities.

**How it works:**
```
Stage 1 — Supervised Fine-Tuning (SFT):
  Data: human-written prompt-response pairs
  Objective: maximize likelihood of the human-written response
  Result: model learns format, tone, and basic helpfulness

Stage 2 — Reward Model (RM) Training:
  Data: pairwise comparisons of model completions (human labels which is better)
  Objective: Bradley-Terry pairwise ranking loss
  Result: a model that outputs a scalar "goodness" score for any completion

Stage 3 — PPO Optimization:
  Data: prompts (no responses)
  Objective: generate completions, score with RM, update policy via PPO + KL penalty
  Result: model that maximizes human preference while avoiding drift
```

**Key techniques:**
- **SFT as behavior cloning:** the model imitates high-quality human demonstrations, establishing a baseline of safe, coherent behavior
- **Pairwise preference data:** humans compare two completions rather than rating one, which is more reliable and scalable
- **KL divergence penalty:** during PPO, a term penalizes the policy for diverging too far from the SFT checkpoint, preventing reward hacking and catastrophic forgetting
- **Iterative refinement:** some pipelines repeat stages 2 and 3 with fresh data, progressively improving alignment

**Why this matters:**
- RLHF is the difference between a raw base model and ChatGPT, Claude, or Gemini.
- It scales alignment: instead of writing answers to millions of prompts, humans only compare a few thousand model outputs.
- It is the industry standard. Understanding RLHF is essential for any lead engineer building production language systems.

---

### Real-Life Analogy

Training a customer service representative.
- **Stage 1 (SFT):** You give the rep a handbook with example conversations. "When a customer says X, respond with Y." The rep memorizes the format and tone. They can now handle common scenarios competently.
- **Stage 2 (RM training):** You hire a quality-assurance manager. The manager listens to two recorded calls and says "Call A was better than Call B." After hundreds of comparisons, the manager develops an intuitive sense of good service, even for situations not in the handbook.
- **Stage 3 (PPO):** The rep takes live calls. After each call, the manager scores it. The rep adjusts their approach to get higher scores. But you enforce a rule: "Do not change your personality so drastically that customers no longer recognize you." This is the KL penalty.
- **The result:** The rep becomes more helpful and friendly than the handbook alone could achieve, while staying recognizable and trustworthy.

---

### Tiny Numeric Example

**Prompt:** "How do I bake sourdough bread?"

**Stage 1 — SFT teaches format:**
```
Before SFT:  "Sourdough is a type of bread. It uses flour."
After SFT:   "To bake sourdough, first feed your starter..."
SFT loss:    1.2 -> 0.4 over 100 steps
```

**Stage 2 — RM learns preferences:**
```
Completion A (detailed, safe): score = 2.1
Completion B (vague, risky):   score = -0.8
RM accuracy on validation:     55% -> 78% over training
```

**Stage 3 — PPO optimizes policy:**
```
Step 0:   average reward = 0.3,  KL from SFT = 0.00
Step 10:  average reward = 0.9,  KL from SFT = 0.04
Step 25:  average reward = 1.4,  KL from SFT = 0.08
Step 50:  average reward = 1.6,  KL from SFT = 0.12
```

**Policy improvement:**
```
Before RLHF: "Mix flour and water and bake it."
After PPO:   "Combine 500g bread flour with 350g warm water...
             ...bake at 230C for 20 minutes with the lid on."
```

**The shift:** The model retained its factual knowledge (it still knows about sourdough) but learned to present it in a structured, detailed format that humans prefer. The KL penalty ensured it did not invent wild techniques just to chase higher RM scores.

---

### Common Confusion

1. **"RLHF replaces pretraining."** No. RLHF comes after pretraining and SFT. It cannot teach a model facts it never learned. It only shapes behavior.

2. **"You can skip SFT and go straight to PPO."** You can try, but PPO without an SFT baseline is unstable. The policy has no idea what a "good" completion looks like, so it wanders randomly. SFT provides the anchor.

3. **"The reward model is perfect."** RMs are noisy, biased toward length, and susceptible to surface patterns. PPO must be run with caution, and the final model must be evaluated by humans, not just RM scores.

4. **"RLHF makes the model harmless but also less capable."** This is called alignment tax. It can happen, but careful tuning of the KL coefficient and training data minimizes it. The goal is alignment without capability loss.

5. **"One RLHF run is enough."** Production models often go through multiple rounds of SFT, RM retraining, and PPO with increasingly refined preference data. Alignment is iterative.

6. **"RLHF only works for chatbots."** The same pipeline is used for code models (rewarding correct, efficient code), summarization (rewarding factual accuracy), and reasoning (rewarding step-by-step correctness).

7. **"Human feedback means real-time human labeling during training."** In practice, human labels are collected in batches offline. The model generates candidate completions, humans compare them, and the RM is trained on the static dataset. PPO then runs without human involvement.

---

### Where It Is Used in Our Code

`src/phase122/phase122_rlhf_concepts.py` — We simulate the full three-stage pipeline in NumPy. Step 1 performs SFT on a small instruction dataset. Step 2 trains a reward model on synthetic pairwise comparisons. Step 3 runs PPO optimization, tracking policy improvement, KL divergence, and reward curves across all three stages.

`src/phase122/phase122_rlhf_colab.py` — We execute the full RLHF pipeline on a real Qwen2.5-3B model. Stage 1 fine-tunes on UltraChat subset. Stage 2 builds and trains a scalar reward model on synthetic preference pairs. Stage 3 runs TRL's PPOTrainer for 50 steps, scoring generations with the RM and optimizing the policy while monitoring KL divergence and sample quality before and after PPO.

(End of file - total 104 lines)

### 1. Why it exists (THE PROBLEM first)
After Supervised Fine-Tuning, a model knows the *format* of being helpful, but it can still generate harmful, biased, overly verbose, or factually careless outputs. SFT teaches structure, but it does not reliably align the model with nuanced human values like safety, honesty, and fairness. We need a way to steer the model toward outputs that humans actually prefer.

### 2. Definition (very simple)
Reinforcement Learning from Human Feedback (RLHF) is a two-stage alignment technique: first, a reward model is trained to score how good a response is based on human preferences; second, a reinforcement learning algorithm (typically PPO) fine-tunes the language model to maximize those scores.

### 3. Real-life analogy
A chef first learns standard recipes (SFT). Then food critics taste their dishes and rate them (reward model). The chef adjusts their cooking—more salt, less heat, better plating—to earn higher ratings (PPO). The critics never write a recipe; they simply teach the chef what "good" means through scores.

### 4. Tiny numeric example
For the prompt "How do I bake a cake?":
- **Response A:** A detailed, safe step-by-step guide. Humans rate it highly.
- **Response B:** A dangerous method involving unsafe ingredients. Humans rate it poorly.

The reward model learns to assign a high score to A and a low score to B. PPO then updates the GPT's weights so that future outputs are more like A and less like B.

### 5. Common confusion
- **RLHF is not just more SFT.** SFT uses fixed correct answers; RLHF uses a reward signal and can optimize for qualities that are hard to write down explicitly.
- **It is not only about safety.** RLHF also improves helpfulness, tone, conciseness, and relevance.
- **PPO is part of RLHF, not the whole thing.** RLHF includes both the reward-model training and the policy optimization.
- **Human feedback is expensive.** RLHF requires collecting thousands of human preference comparisons, which is a major bottleneck.
- **The reward model can be gamed.** The policy model may learn to produce outputs that trick the reward model into giving high scores without actually being good.

### 6. Where it is used in our code
Brief mention: RLHF is the third stage of our pipeline, applied after SFT to align the assistant with human preferences before deployment.

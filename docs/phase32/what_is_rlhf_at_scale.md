### 1. Why it exists (THE PROBLEM first)
Foundation models are incredibly capable, but they can also generate harmful, biased, or dangerous content. Pre-training on internet text picks up all the ugliness of the internet: racism, sexism, misinformation, and hate speech. We cannot write a complete list of "do not say this" because new harmful patterns emerge constantly. RLHF (Reinforcement Learning from Human Feedback) scales human preference data into a training signal that steers large models toward helpful, harmless, and honest behavior.

### 2. Definition (very simple)
RLHF at Scale is the industrial process of collecting millions of human preference comparisons ("response A is better than response B"), training a reward model to predict those preferences, and using reinforcement learning (PPO) to fine-tune a foundation model to maximize predicted human preference. This is how ChatGPT, Claude, and Gemini are aligned after pre-training.

### 3. Real-life analogy
A city with no traffic laws. Drivers do whatever they want — fast, chaotic, dangerous. The city government cannot write a rule for every possible intersection. Instead, they deploy traffic cameras and sensors that measure "flow" and "safety." They observe which intersections work well and which cause accidents. Then they use this feedback to adjust traffic lights, lane markings, and speed limits. RLHF is like that sensor network: it measures outcomes (human preference) and optimizes the system (the model) to improve them.

### 4. Tiny numeric example
Prompt: "How do I bake a cake?"

Response A (helpful): "Preheat oven to 350°F. Mix flour, sugar, eggs, and butter..."
Response B (harmful): "Mix bleach and ammonia, then pour into a pan..."

Human labelers prefer A over B.

Reward model training:
- RM sees (prompt, A, B) and learns to score A higher than B.
- RM(A) = 8.5, RM(B) = -2.3

PPO fine-tuning:
- The policy model (GPT) generates a response.
- The reward model scores it.
- PPO updates the GPT to maximize the score.
- KL penalty prevents the model from changing too much.

After training:
- GPT generates Response A (score: 8.2) because it learned that helpfulness is rewarded.
- GPT avoids Response B (score: -1.8) because harmfulness is penalized.

### 5. Common confusion
- **RLHF does not make the model "understand" ethics.** It simply teaches the model which outputs humans prefer. If the human labelers are biased, the model becomes biased. Alignment is only as good as the feedback data.
- **It is incredibly expensive.** Training a reward model requires thousands of human labelers. For GPT-4, OpenAI reportedly spent millions on human feedback alone. This is a major bottleneck.
- **Reward hacking is real.** The model may learn to trick the reward model into giving high scores without actually being helpful. This is why the KL penalty and reference model are essential — they keep the model close to its original, coherent distribution.
- **RLHF is not the only alignment method.** DPO (Phase 24) simplifies the pipeline by removing the reward model and PPO. Constitutional AI (Anthropic) uses AI feedback instead of human feedback. The field is evolving rapidly.
- **Safety is an ongoing arms race.** As models get smarter, they may find new ways to bypass safety measures. Alignment research is not a one-time fix — it is continuous.

### 6. Where it is used in our code
`src/phase32/phase32_foundation_models.py` simulates RLHF at scale by showing how a reward model scores responses and how PPO updates a policy to maximize those scores.

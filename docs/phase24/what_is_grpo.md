### 1. Why it exists (THE PROBLEM first)
The standard PPO algorithm inside RLHF needs a "critic" model that estimates the value of a state, which is used to compute advantages. This critic is often another full-scale language model, meaning PPO effectively doubles GPU memory and compute. Training and synchronizing two large models is expensive and error-prone. GRPO was designed to remove that burden.

### 2. Definition (very simple)
Group Relative Policy Optimization (GRPO) is a reinforcement learning variant that eliminates the critic network. For a single prompt, it generates a group of responses, computes a reward for each, and uses the group average as the baseline. Advantages are calculated relative to that group average, and the policy is updated to favor above-average outputs.

### 3. Real-life analogy
A teacher gives the class the same essay question. Instead of grading each essay against a perfect answer key (critic), the teacher simply ranks the essays against each other. The best essay in the group gets the top grade, the worst gets the lowest, and everyone is judged relative to their peers—not against an absolute standard.

### 4. Tiny numeric example
For one prompt, generate 4 responses. The reward model scores them:
- Response rewards: [3, 5, 7, 8]
- Group average reward: 5.0

Advantages = reward - average:
- Advantages: [-2, 0, 2, 3]

The policy is updated to increase the probability of responses with positive advantage (7 and 8) and decrease the probability of responses with negative advantage (3).

### 5. Common confusion
- **GRPO is not the same as PPO.** PPO uses a learned critic to estimate advantages; GRPO uses the empirical group mean.
- **No critic model means less memory.** You only need the policy model and a reference model, not a separate value network.
- **"Group-relative" means relative, not absolute.** A response with reward 7 might get a positive advantage in one group but a negative advantage in a stronger group.
- **It is especially popular for reasoning models.** DeepSeek-R1 and similar systems use GRPO because it scales well for math and code tasks where multiple solution paths exist.
- **Sample size matters.** If the group is too small, the average is noisy; if too large, generation becomes expensive.

### 6. Where it is used in our code
Brief mention: GRPO is implemented in our phase-24 trainer as a memory-efficient alternative to PPO when we generate multiple rollouts per prompt and want to avoid maintaining a full critic model.

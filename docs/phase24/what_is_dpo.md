### 1. Why it exists (THE PROBLEM first)
RLHF works, but it is complex and fragile. It requires maintaining three separate models in memory: the policy model (the GPT being trained), a reference model (the frozen SFT checkpoint), and a reward model (the critic). It also uses PPO, which introduces many hyperparameters and training instabilities. Researchers wanted a simpler way to align models directly from human preferences without the heavy machinery.

### 2. Definition (very simple)
Direct Preference Optimization (DPO) is an alignment method that bypasses the reward model and PPO entirely. It reformulates preference learning as a simple classification loss over the language model's own probabilities, directly maximizing the likelihood of preferred responses and minimizing the likelihood of rejected ones.

### 3. Real-life analogy
Instead of hiring a professional food critic to rate every dish on a 1-10 scale, you simply ask customers "Which dish do you prefer?" and tell the chef to make the winning dish more often and the losing dish less often. There is no middleman; the feedback goes straight to the chef.

### 4. Tiny numeric example
Given a prompt, the model computes:
- P(response_A | prompt) = 0.01
- P(response_B | prompt) = 0.0001

If humans prefer A over B, the DPO loss is:
```
-loss = log( sigmoid( log(PA) - log(PB) ) )
```
Because log(0.01) >> log(0.0001), the sigmoid is near 1, the loss is near zero, and the model is already doing well. If the preference were reversed, the loss would be high and the gradients would push the model to swap the probabilities.

### 5. Common confusion
- **DPO does not use a reward model.** That is the whole point; it derives an implicit reward from the policy's own probabilities.
- **It is not traditional reinforcement learning.** There are no policy gradients, advantage estimates, or critic networks—just a differentiable preference loss.
- **It still needs preference data.** You cannot run DPO without human (or AI) comparisons of which response is better.
- **Simpler does not always mean weaker.** In many benchmarks, DPO matches or exceeds RLHF performance while training faster and using less memory.
- **The reference model is still required.** DPO uses a frozen copy of the SFT model to prevent the policy from drifting too far from coherent language.

### 6. Where it is used in our code
Brief mention: DPO is used in our phase-24 alignment pipeline as a lightweight alternative to full RLHF when compute budget is limited or when we want to iterate quickly on preference data.

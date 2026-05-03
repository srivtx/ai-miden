# Phase 109 Summary: World Models & Model-Based RL

## What We Learned

This phase introduced model-based reinforcement learning, where agents learn an internal model of the environment to plan and imagine rather than relying solely on trial-and-error.

## Key Takeaways

1. **World Models** learn to predict next states and rewards, enabling agents to simulate experience.
2. **Dreamer** plans in a compact latent space learned from high-dimensional observations, making long-horizon planning tractable.
3. **Model Predictive Control** uses the learned model to evaluate action sequences online, executing only the first action before re-planning.

## Why It Matters

Model-based RL is the path to sample-efficient learning in robotics, autonomous driving, and any domain where real-world interaction is expensive or risky. Understanding world models and MPC is essential for building agents that think before they act.

## Navigation

- **Previous:** [Phase 108: Multimodal Reasoning](../phase108/SUMMARY.md)
- **Next:** [Phase 110: Test-Time Compute Scaling](../phase110/SUMMARY.md)

# What is Dreamer?

## 1. Problem Statement

Standard model-based RL often struggles with long-term planning in high-dimensional spaces because learned models accumulate errors over long rollouts. We need a way to plan effectively in a compact, stable latent space rather than in raw pixels or high-D states.

## 2. Definition

**Dreamer** is a model-based RL algorithm that learns a latent dynamics model from pixels. It uses a recurrent state-space model (RSSM) to encode observations into a compact latent state, predict future latent states, and imagine trajectories entirely in latent space. Policy and value functions are trained on imagined latent rollouts, making it highly sample-efficient.

## 3. Analogy

Dreamer is like a chess master who thinks several moves ahead in their mind. Instead of moving pieces on the board (real environment), they imagine a compact mental representation of the board and explore future scenarios mentally before committing to a move.

## 4. Example

In DeepMind Control Suite tasks, Dreamer learns from pixel observations. It encodes each frame into a latent vector, predicts how the latent state evolves under actions, and trains a policy on imagined latent trajectories. It achieves strong performance with orders of magnitude fewer environment steps than model-free methods.

## 5. Common Confusion

Dreamer is NOT a generative model for dreaming up random scenarios. It is a controlled, action-conditioned predictive model used for planning. The "dreams" are not hallucinations; they are structured latent rollouts used for policy optimization.

## 6. Code Location

See `src/phase109/phase109_world_models.py` for a NumPy simulation of learned dynamics and MPC planning.

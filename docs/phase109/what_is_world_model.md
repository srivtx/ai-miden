# What is a World Model?

## 1. Problem Statement

Reinforcement learning agents that learn purely from trial-and-error in the real world are sample-inefficient and potentially dangerous. They need millions of environment interactions. A more efficient approach is to learn an internal model of how the world works and plan inside that model.

## 2. Definition

A **World Model** is a learned representation of an environment's dynamics. Given the current state and an action, it predicts the next state and reward. The agent can then use this model to simulate future trajectories, evaluate plans, and learn policies without interacting with the real environment at every step.

## 3. Analogy

Imagine learning to drive. Instead of crashing a thousand real cars, you practice in a driving simulator. The simulator is your world model: it approximates how the real car responds to steering, acceleration, and braking. You improve in the simulator, then transfer skills to the real car.

## 4. Example

In model-based RL for robotics, a neural network learns to predict how a robot arm will move given motor commands. The agent uses this model to imagine thousands of possible action sequences, selecting the one that maximizes predicted reward, all without moving the physical arm.

## 5. Common Confusion

A world model is NOT just a replay buffer or a value function. A replay buffer stores past experiences; a value function estimates future returns. A world model explicitly predicts future states and rewards, enabling planning and counterfactual reasoning.

## 6. Code Location

See `src/phase109/phase109_world_models.py` for a NumPy simulation of a learned dynamics model and simple MPC.

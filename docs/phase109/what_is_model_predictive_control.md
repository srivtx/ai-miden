# What is Model Predictive Control (MPC)?

## 1. Problem Statement

Even with a good world model, an agent must decide which actions to take. Brute-force search over all possible action sequences is intractable. We need a principled way to use the model to select actions online, re-planning at each step as new information arrives.

## 2. Definition

**Model Predictive Control** is an online planning method that uses a dynamics model to simulate future trajectories over a finite horizon. At each timestep, it evaluates multiple candidate action sequences, selects the one with the best predicted return, executes the first action, and then re-plans from the new state. This compensates for model errors by never committing to a full plan.

## 3. Analogy

MPC is like driving with a GPS that recalculates the route every 10 seconds. You look ahead at possible routes, pick the best one, drive for 10 seconds, and then re-evaluate based on your new position. You never blindly follow a plan made miles ago.

## 4. Example

A quadcopter uses a learned dynamics model to predict its position under different thrust commands. At 50Hz, it samples 100 candidate action sequences over a 1-second horizon, picks the sequence that stays closest to the target trajectory, applies the first command, and repeats.

## 5. Common Confusion

MPC is NOT just open-loop planning. Open-loop planning commits to an entire action sequence. MPC only executes the first action and re-plans, making it robust to model inaccuracies and unexpected disturbances. It is also not a learning algorithm per se—it is a control strategy that can use either learned or analytical models.

## 6. Code Location

See `src/phase109/phase109_world_models.py` for a NumPy simulation of MPC using a learned dynamics model.

# What is DPO?

## 1. Why it exists (THE PROBLEM first)

RLHF (Reinforcement Learning from Human Feedback) works, but it is fragile.
It needs three separate models: the policy, a reward model, and a reference
model. Training the reward model is expensive, and PPO (the RL algorithm) is
unstable, sensitive to hyperparameters, and hard to debug. Researchers wanted a
way to align models with human preferences without the complexity of
reinforcement learning.

## 2. Definition (very simple)

Direct Preference Optimization (DPO) is a method that trains a language model
directly from human preference data without ever building a reward model. It
rewrites the RLHF objective so that the optimal policy can be found by a simple
classification loss on preference pairs.

## 3. Real-life analogy

Imagine teaching someone to cook. RLHF is like hiring a food critic to rate
every dish, then paying the chef a bonus for high scores. DPO is like giving
the chef two dishes and saying, "This one is better than that one." The chef
learns directly from the comparison, no critic required.

## 4. Tiny numeric example

Suppose a reference model assigns log-probabilities to two responses for the
same prompt:

- Chosen (good): log_ref = -0.80
- Rejected (bad): log_ref = -0.95

Our policy model starts with the same probabilities:

- Policy chosen: log_pi = -0.80
- Policy rejected: log_pi = -0.95

DPO loss with beta = 0.5:

```
reward_margin_policy = (-0.80) - (-0.95) = 0.15
reward_margin_ref    = (-0.80) - (-0.95) = 0.15
loss = -log(sigmoid(0.5 * (0.15 - 0.15)))
     = -log(sigmoid(0))
     = -log(0.5)
     = 0.693
```

Now imagine training makes the policy more confident in the chosen response:

- Policy chosen: -0.60
- Policy rejected: -1.10

```
reward_margin_policy = (-0.60) - (-1.10) = 0.50
loss = -log(sigmoid(0.5 * (0.50 - 0.15)))
     = -log(sigmoid(0.175))
     = -log(0.544)
     = 0.609
```

The loss went down because the policy increased the gap between chosen and
rejected.

## 5. Common confusion (5+ bullet points)

- **"DPO does not need a reference model."** It does. DPO uses a reference model
to prevent the policy from drifting too far from the original. The reference is
frozen, but it is still required.
- **"DPO is just classification."** It is a classification loss on preference
pairs, but it is mathematically derived from the RLHF reward objective, so it
carries the same theoretical guarantees.
- **"DPO works without any preference data."** It needs preference data just as
much as RLHF does. The simplification is in the algorithm, not the data.
- **"Beta controls learning rate."** Beta controls how much the policy is
allowed to deviate from the reference model. A higher beta means stricter
adherence to the reference; a lower beta means more aggressive preference
optimization.
- **"DPO is always better than RLHF."** DPO is simpler but can overfit to
preference data and may struggle when preferences are noisy or when the model
needs to explore broadly. RLHF with PPO can sometimes reach higher ceilings on
complex tasks.
- **"DPO loss only cares about the chosen response."** DPO loss depends on the
relative probabilities of chosen and rejected. Making the chosen more likely
helps, but making the rejected less likely helps just as much.

## 6. Where it is used in our code

`src/phase66/phase66_dpo_orpo.py` simulates a policy model and computes DPO
loss step-by-step, showing how the policy shifts probability mass from rejected
to chosen responses. `src/phase66/phase66_dpo_orpo_colab.py` runs real DPO
training using the TRL library on a preference dataset.

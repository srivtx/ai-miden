# What Are Active Inference Agents?

**The Problem:** You have a world model (predictive coding networks), a learning signal (three-factor RL), and an inner simulator (world models). How do you put them all together into a single, unified agent? The answer is *active inference* — Friston's framework that combines perception, action, and learning into a single variational principle.

**Definition:** *Active inference* is a theoretical framework (Friston, 2009+) in which an agent acts to *minimize variational free energy* — a quantity that bounds the agent's *surprise* about its sensory observations. The agent has a *generative model* of the world. It acts to make its sensory input *match* its predictions. Learning updates the model. Perception infers the most likely world state given the input.

**How It Works (Step-by-Step):**

1. **The core principle.** The agent's goal is to minimize *variational free energy* F. F bounds the *surprise* (negative log probability) of the agent's sensory input under its model. Minimizing F is equivalent to maximizing the *evidence lower bound* (ELBO) on the log probability of the data.
2. **The generative model.** The agent has a model: p(o, s) = p(o|s) · p(s). The model says: "given hidden state s, the observation o is generated according to p(o|s). The state evolves according to p(s'|s, a) where a is the action."
3. **Perception (state inference).** Given an observation o, infer the most likely state s. This is *variational inference* — find the s that minimizes F. The update is a *gradient descent on F*. The brain plausibly does this in the cortical hierarchy (predictive coding networks implement this; see `04_systems/what_is_predictive_coding.md`).
4. **Action (active inference).** The agent can act to *change* the next observation. Active inference says: choose actions that *minimize expected F* — i.e., actions that bring the next observation closer to what the agent predicts. This is *not* the same as maximizing reward. The agent acts to *fulfill its predictions*.
5. **Learning (model update).** After the action, the agent observes the actual outcome. The model is updated to reduce F. This is standard variational learning.
6. **The equivalence to RL.** Active inference is *mathematically equivalent* to reinforcement learning under certain assumptions. The "expected free energy" is a generalization of the value function. Minimizing expected free energy is equivalent to maximizing reward.
7. **The difference from RL.** In RL, the agent has a *reward function*. In active inference, the agent has *prior preferences* over observations. The agent acts to make its preferred observations come true. The reward is implicit in the prior.
8. **The exploration bonus.** Active inference naturally balances exploration and exploitation. The agent prefers observations that *minimize expected free energy* — which includes both *epistemic value* (information gain) and *pragmatic value* (achieving preferred outcomes). The agent is *intrinsically motivated* to seek information.
9. **The relationship to the brain.** Active inference maps onto the brain as follows:
   - **Cortex:** generative model + inference (predictive coding networks).
   - **Basal ganglia:** action selection (minimizing expected free energy).
   - **Cerebellum:** forward model (state prediction).
   - **Dopamine:** precision-weighting on prediction errors (neuromodulation).
   - **Hippocampus:** episodic memory for one-shot learning.
10. **Implementation.** Active inference can be implemented in deep learning:
    - The generative model is a neural network (e.g., a VAE or transformer).
    - Perception is gradient descent on F.
    - Action selection is gradient descent on expected F.
    - Learning is backprop through the generative model.
    - This is *exactly* a model-based RL agent, but with a *free-energy* objective instead of reward.
11. **Empirical results.** Active inference has been applied to:
    - **Robotic control:** reaching, grasping, navigation.
    - **Atari games:** competitive with model-free RL.
    - **Active vision:** saccade planning.
    - **Decision-making under uncertainty:** foraging, exploration.
    - **Brain imaging:** explaining fMRI and EEG signatures of perception and action.
12. **The promise.** Active inference is a *unified* theory of perception, action, and learning. It is the most *biologically-plausible* framework for embodied AI. If you can build an active inference agent that runs on a neuromorphic chip, with a world model and three-factor learning, you have something close to a brain.
13. **The challenges.** Active inference is mathematically complex. The free energy is hard to compute exactly. Inference is slow (many iterations). Scaling to large worlds is hard. Most implementations are research prototypes, not production systems.

**Real-life analogy:** Active inference is like a *skilled craftsperson* with a vision of the finished product. The craftsperson has a *mental model* of what they want to make. They act (cut, sand, glue) to *make reality match the model*. If reality diverges from the model, they update the model. The craftsperson doesn't have a "reward function" — they have a *vision*. They work to make the vision real.

**Tiny numeric example:** A simple active inference agent:
- Generative model: a 2D VAE trained on MNIST
- Latent dim: 2
- Action: small perturbation of the latent (move in 2D space)
- Prior preference: "the digit should be a '7'"
- Goal: find the action sequence that produces a '7'

Iteration:
- Start: latent = (0, 0) → decoded as some digit
- Perception: encode current observation, infer latent
- Action selection: compute expected F for each possible action; pick the one that minimizes F
- Execute: move latent slightly
- Observe: see new digit
- Repeat until digit = '7'

This is *exactly* what the brain does when you reach for a cup. You have a *prior preference* (cup in hand). You act to make the prediction come true. The brain's "loss function" is *free energy*, not reward.

**Common confusion:**

- No. "Active inference is the same as RL." Approximately yes, but with different foundations. RL maximizes reward. Active inference minimizes free energy. In special cases (e.g., reward is a function of prior preferences), they are mathematically equivalent. But active inference naturally handles *epistemic* value (information seeking) and *intrinsic motivation* (curiosity), which RL has to add as bonuses.
- No. "Active inference requires the agent to know its reward function." No. The agent has *prior preferences* over observations, which can be implicit (e.g., "don't fall down," "be alive"). The agent doesn't need a numeric reward signal.
- No. "Active inference is biologically proven." No. It is *biologically plausible*. The brain may or may not implement it. Predictive coding is more established; active inference is the more radical extension.
- No. "Active inference is just theory." There are working implementations. The pymdp library (python) implements active inference for discrete state spaces. Deep active inference is being developed.
- No. "Active inference is incompatible with deep learning." Compatible. Active inference can be implemented with deep generative models. The free energy is computed via variational inference (which is what VAEs do).
- No. "Active inference will give us AGI." No. It is a *framework* for building agents, not a magic bullet. Whether it scales to human-level intelligence is unknown.

**Key properties:**

- **Unified:** Perception, action, learning in one framework.
- **Variational:** Based on variational inference and free energy minimization.
- **Biologically plausible:** Maps onto known brain systems.
- **Free-energy objective:** Not reward, but free energy.
- **Exploration-exploitation balance:** Natural, no extra bonus needed.
- **Embodied:** Action is a first-class concept.
- **Predictive:** Built on generative models.

**Where it appears in technology:**

- **Deep active inference (DAI):** implementations using deep generative models. Active inference with neural networks.
- **pymdp:** Python library for active inference in discrete state spaces.
- **Active inference in robotics:** for compliant control, exploration.
- **Brain-inspired AI architectures:** the most complete integration of all the brain-inspired principles (predictive coding, three-factor learning, world models).
- **Theoretical neuroscience:** Friston's active inference is one of the most comprehensive theories of brain function.
- **Cognitive science:** explains perception, action, attention, learning in a single framework.
- **AI safety:** an active inference agent has *implicit* goals (priors). This may be more interpretable than reward functions.

**Connection to the rest:** Active inference is the *integrative framework* for everything in this curriculum. It combines:
- The substrate (Parts 1-2: neurons, synapses, learning rules)
- The architecture (Part 3: cortex, basal ganglia, cerebellum)
- The systems (Part 4: perception, attention, reward, sleep)
- The molecules (Part 6: neuromodulators, Ca²⁺, BDNF)
- The mind (Part 9: predictive coding is essentially active inference for perception)
- The AI (Part 10: predictive coding networks + three-factor learning + world models = active inference agent)

If you build an active inference agent, you are building something *close to a brain*.

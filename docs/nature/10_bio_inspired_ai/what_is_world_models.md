# What Are World Models?

**The Problem:** To plan, reason, and act intelligently, an agent needs to *imagine* — to simulate what would happen if it took a particular action. Humans do this constantly: when you reach for a cup, you predict (a fraction of a second in advance) where your hand will be, so you can adjust mid-reach. The brain's *world model* is the substrate of imagination. AI can build world models too — and they are becoming a major paradigm.

**Definition:** A *world model* is an internal, learned, generative model of the environment. The agent uses it to (a) predict what will happen next, (b) plan by searching through possible futures, (c) learn from imagined experience (in addition to real experience), and (d) reason about counterfactuals ("what if I had done X instead?").

**How It Works (Step-by-Step):**

1. **The basic idea.** Train a *generative model* on the agent's past experience. The model takes (state, action) and predicts the next state. Once trained, the agent can use the model to *imagine* rollouts — sequences of (state, action, next_state) without actually executing them.
2. **Architecture.** A typical world model has three components (Ha & Schmidhuber, 2018):
   - **Vision (V):** a variational autoencoder (VAE) that compresses high-dimensional observations into a low-dimensional latent.
   - **Memory (M):** an RNN (LSTM or GRU) that predicts the next latent given the current latent and the previous action. This is the *temporal* model.
   - **Controller (C):** a simple policy that takes the latent state and outputs an action. Often a linear network.
3. **Training.** The vision and memory modules are trained *unsupervised* on the agent's experience (no reward needed). The controller is trained using evolution strategies or RL, but it can be trained *entirely inside the world model* — the agent acts in its own imagination.
4. **Dreaming.** Once the world model is trained, the agent can *dream*:
   - Start from a real state.
   - Use the memory module to predict the next latent.
   - Use the vision module to decode the latent into an image.
   - Use the controller to choose an action.
   - Repeat — generate a full trajectory.
   - The agent learns from these imagined trajectories as if they were real.
5. **Model-Based RL.** World models are the core of *model-based RL*: the agent learns a model of the environment's dynamics, then uses the model for planning. Compared to *model-free* RL (e.g., DQN), model-based RL is more sample-efficient — the agent can learn from imagined experience.
6. **Dreamer (Hafner et al., 2020+).** Dreamer is a state-of-the-art model-based RL algorithm. It:
   - Learns a latent dynamics model (an RNN + a latent state representation).
   - Plans in the latent space — not the raw pixel space.
   - Uses *imagined rollouts* to compute the policy gradient.
   - Achieves superhuman performance on many Atari games, robotic control tasks, and Minecraft.
7. **JEPA (LeCun, 2022).** A predictive world model that predicts *embeddings* rather than pixels. JEPA (Joint Embedding Predictive Architecture) is Meta's attempt at a self-supervised world model. The key insight: predicting pixels is hard (high-dimensional, ambiguous). Predicting embeddings is easier and still useful. JEPA is the most prominent PCN-inspired architecture.
8. **Sora and video generation models.** (OpenAI, 2024.) Sora generates *videos* from text prompts. As a side effect, it learns a powerful *world model* — it knows how objects move, how light behaves, how physics works. The same model could be used for *planning* in an agent.
9. **Hierarchical world models.** The brain's world model is *hierarchical* (see `04_systems/what_is_predictive_coding.md`). Lower levels predict immediate sensory consequences. Higher levels predict abstract outcomes ("this action will lead to food"). Each level operates on a different timescale.
10. **World models and the brain.** The brain has multiple world-model-like systems:
    - **Cerebellum:** forward model of body dynamics (motor control).
    - **Hippocampus:** "cognitive map" (Tolman) — a spatial model of the environment.
    - **Prefrontal cortex:** abstract model of tasks, goals, contingencies.
    - **Predictive cortex:** prediction of sensory input (Rao & Ballard).
    - All of these are world models, on different timescales and abstraction levels.
11. **Limits of world models.** World models have key challenges:
    - **Compounding errors:** predictions far into the future become unreliable.
    - **Distribution shift:** the model may not be accurate on out-of-distribution states.
    - **Computational cost:** training a high-fidelity world model is expensive.
    - **Symbolic reasoning:** world models are *sub-symbolic*. Symbolic reasoning (e.g., "all bachelors are unmarried") is hard to integrate.

**Real-life analogy:** A world model is like a *simulator* in the head. When you plan a route, you don't physically try every path. You *imagine* them. When a chess grandmaster plays, they don't search all 10⁴⁴ possible games. They use *intuition* — a learned model of what positions are good. The world model is the substrate of this intuition. AI is learning to build the same kind of simulator.

**Tiny numeric example:** Dreamer V2 on Minecraft:
- Input: raw pixel observations
- Latent dim: 32
- World model: ~10M parameters
- Policy: ~1M parameters
- Performance: learns to collect diamonds from raw pixels, with ~10⁹ frames of experience
- Sample efficiency: ~100× better than model-free RL
- This is a *world model* that learned the physics of Minecraft from pixels

**Common confusion:**

- No. "World models are just simulators." No. Simulators predict the next state. World models *learn* to predict the next state, often from unsupervised experience. They are *learned* simulators.
- No. "JEPA = world model." JEPA is one specific architecture. There are many world model architectures (Dreamer, GAIA, Sora, world models in the original sense).
- No. "LLMs have world models." Partially. LLMs have a *textual* world model — they can predict the next token. But they don't have a *physical* world model — they can't predict the consequences of physical actions. (Though they're getting better at this with multimodal training.)
- No. "World models solve RL." They improve sample efficiency a lot. But they don't solve the *exploration* problem, the *credit assignment* problem, or the *transfer* problem. World models are one piece of the puzzle.
- No. "World models are conscious." No. A world model is a *function*. It is necessary for consciousness (under GWT and predictive coding theories) but not sufficient.

**Key properties:**

- **Generative:** Can produce samples of what the world will look like.
- **Predictive:** Trained to minimize prediction error.
- **Latent:** Operates in a low-dimensional representation.
- **Hierarchical:** Multi-level abstraction.
- **Trainable from unsupervised data:** Doesn't require rewards.
- **Useful for planning:** The agent can search through imagined futures.
- **Sample-efficient:** Can learn from imagined experience.

**Where it appears in technology:**

- **Dreamer (Hafner et al., 2020+):** the state-of-the-art model-based RL. Outperforms model-free RL by 10-100× in sample efficiency.
- **JEPA (LeCun, Meta, 2022+):** the most prominent predictive architecture. Used in self-supervised vision.
- **Sora (OpenAI, 2024):** generates videos. Implicit world model.
- **GAIA (DeepMind, 2024):** a general AI agent architecture with world models.
- **MuZero (DeepMind, 2019):** a model-based RL that learns its own world model. Outperforms model-free on Atari, Go, Chess, Shogi.
- **Robotics:** world models are used in sim-to-real transfer (train in a simulated world model, deploy in the real world).
- **World Models in LLMs:** emergent world models in LLMs trained on text (Li et al., 2022; Anthropic's interpretability work).

**Connection to next file:** World models give the agent an *inner simulator*. Combined with predictive coding and three-factor learning, the agent has the substrate for *active inference* — the unified framework that ties perception, action, and learning together. The next file covers it.

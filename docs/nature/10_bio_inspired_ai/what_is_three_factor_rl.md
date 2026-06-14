# What Is Three-Factor Reinforcement Learning?

**The Problem:** Reinforcement learning is powerful — it's how the brain learns from sparse, delayed rewards. But standard RL algorithms (REINFORCE, actor-critic) require the agent to *know* the policy gradient — the derivative of expected reward with respect to parameters. The brain has no such gradient. How does the brain implement something like RL? Answer: *three-factor learning* — pre × post × neuromodulator. The neuromodulator (dopamine) is the biological implementation of the policy gradient.

**Definition:** *Three-factor reinforcement learning* is a class of learning rules in which a synaptic change depends on three factors: (1) presynaptic activity, (2) postsynaptic activity, and (3) a global neuromodulatory signal (e.g., dopamine). The neuromodulator acts as a "permission slip" — without it, plasticity does not occur. With it, the synapse updates according to a Hebbian-like rule. This is the biological implementation of policy gradient.

**How It Works (Step-by-Step):**

1. **The standard RL setup.** An agent is in state s, takes action a, receives reward r, and transitions to state s'. The agent's policy π(a|s; θ) is parameterized by θ. The goal: maximize expected cumulative reward J(θ) = E[Σ r_t]. The policy gradient is:
   - ∇J(θ) = E[∇log π(a|s; θ) · R]
   - where R is the cumulative reward (or TD error, in actor-critic).
2. **The three-factor learning rule.** The biological analog:
   - Δw = η · x_pre · x_post · M
   - where M is the local concentration of the relevant neuromodulator.
   - x_pre and x_post are the pre- and postsynaptic activities.
3. **The neuromodulator as a "policy gradient" signal.** The neuromodulator carries information about *reward prediction error* (for dopamine) or *novelty* (for norepinephrine) or *attention* (for ACh). The signal is *broadcast* from neuromodulatory nuclei (VTA, LC, basal forebrain) to many brain regions.
4. **The eligibility trace.** A synapse can be *eligible* for plasticity for a short window (~1-2 seconds) after a pre-post coincidence. If the neuromodulator arrives during the eligibility window, the synapse updates. Otherwise, the eligibility decays. The eligibility trace is a *memory* of recent activity, allowing delayed rewards to be assigned to recent actions.
5. **Dopamine and TD error.** Schultz et al. showed that dopamine neurons fire when a reward is *better than expected*. This is exactly the TD error δ(t) = r(t) + γV(s') - V(s). The dopamine burst is the third factor M. Striatal synapses update according to: Δw ∝ x_pre · x_post · δ. This is *three-factor learning*. It is the biological implementation of policy gradient.
6. **The actor-critic architecture.** The basal ganglia implement an actor-critic RL:
   - **Critic:** Computes the value function V(s). Updated by TD error (dopamine).
   - **Actor:** Selects actions based on the critic's evaluation. Updated by eligibility trace × dopamine.
   - **State representation:** Cortex + hippocampus.
   - This is the same architecture as modern deep RL (A3C, PPO).
7. **Sequential neuromodulation.** Brzosko et al. (2017, *eLife*) showed that *sequential* neuromodulation is more powerful:
   - First, ACh enables LTD.
   - Then, DA *converts* the LTD to LTP.
   - The sequence "ACh then DA" effectively says: "this input was active *and* it was followed by reward — strengthen it."
8. **Other neuromodulators and their functions.**
   - **Dopamine:** reward prediction error. Allows LTP; converts LTD to LTP.
   - **Acetylcholine:** attention, novelty, learning state. Modulates plasticity, biases to LTP vs. LTD.
   - **Norepinephrine:** arousal, surprise, novelty. Boosts LTP; sharpens attention.
   - **Serotonin:** behavioral state, patience, mood. Modulates plasticity, mood-dependent.
9. **Three-factor learning in AI.** Modern deep RL is *two-factor*:
   - The *policy gradient* is a global signal (computed from the loss).
   - The *Hebbian* factor is local (pre × post).
   - There is no *third factor* that gates plasticity.
   - Three-factor RL is a *biologically-plausible* extension: add a "neuromodulator" channel that gates learning.
10. **Implementation.** Three-factor learning rules can be implemented in standard deep learning:
    - The neuromodulator M is a *separate network output* (or a learned function of the reward).
    - The loss function is: L = -log π(a|s) · M.
    - M = TD error (R + γV(s') - V(s)).
    - This is *exactly* policy gradient, but with a learned "neuromodulator" signal.
11. **Empirical results.** Three-factor learning rules have been shown to:
    - Improve stability of RL training
    - Enable *credit assignment* over longer timescales
    - Mimic the *phasic* dopamine signal of biological RL
    - Work in spiking neural networks (Loihi)
12. **Limitations.** Three-factor RL is *not* a magic bullet. It still requires backprop through the policy network. The biological plausibility is a *feature*, not a fix. Whether three-factor RL scales to LLM-level tasks is open.

**Real-life analogy:** Three-factor learning is like a *teacher in a classroom*. The student (pre × post) has a question. The student tries to answer. If the teacher (neuromodulator) says "yes, that's right!" the synapse strengthens. If the teacher says "no, that's wrong!" the synapse weakens. If the teacher is silent, no change. The teacher's feedback is *global* (a single reward signal) but it gates *local* changes (at each synapse). This is how a single dopamine burst can update millions of synapses simultaneously.

**Tiny numeric example:** A typical three-factor learning update at a single synapse:
- Pre-synaptic activity: x_pre = 1 Hz (firing rate of presynaptic neuron)
- Post-synaptic activity: x_post = 0.5 Hz
- Neuromodulator (dopamine): M = +1 (unexpected reward, TD error = 1)
- Learning rate: η = 0.01
- Update: Δw = 0.01 · 1 · 0.5 · 1 = +0.005
- New weight: w_new = w_old + 0.005

If M = -1 (worse than expected): Δw = -0.005 (LTD).
If M = 0 (expected reward): Δw = 0 (no change).

This is the *biological implementation* of policy gradient. The dopamine burst carries the global reward signal. The local synapse computes the eligibility (pre × post). The product updates the synapse.

**Common confusion:**

- No. "Three-factor learning is the same as policy gradient." Mathematically, yes — it approximates the policy gradient. The *implementation* is different: three-factor learning is *local* (each synapse updates with only local information).
- No. "Dopamine is the only neuromodulator." No. ACh, NE, 5-HT all gate plasticity. Each has different effects.
- No. "The eligibility trace is just 'recent activity.'" It's a *memory* of recent pre-post coincidences, with a decay time of ~1-2 seconds. Without it, the dopamine signal could not be assigned to recent actions.
- No. "Three-factor learning always improves things." No. It is most useful for *sparse, delayed reward* problems. For dense, instantaneous feedback, standard RL works fine.
- No. "Three-factor learning is biologically proven." The *rule* is biologically motivated. The *exact* implementation in the brain is not fully understood. There are open questions about how the eligibility trace is implemented molecularly.
- No. "Three-factor learning is neuromorphic-only." No. It can be implemented in any differentiable neural network. The "neuromodulator" is just an additional output or loss term.

**Key properties:**

- **Biologically plausible:** Matches the brain's three-factor Hebbian learning.
- **Local:** Each synapse uses only local information.
- **Gated:** Plasticity only occurs when the neuromodulator arrives.
- **Time-delayed:** The eligibility trace allows credit assignment over ~1-2 seconds.
- **Multi-neuromodulator:** Different neuromodulators have different effects.
- **Compatible with backprop:** Can be implemented in standard deep learning.
- **Stable:** Adding a neuromodulatory gate can stabilize RL training.

**Where it appears in technology:**

- **Deep RL with policy gradient:** A3C, PPO, SAC all implement policy gradient. The "neuromodulator" is implicit in the reward signal.
- **Spiking neural networks (SNNs) with reward-modulated STDP:** three-factor learning is the *standard* training rule for SNNs. Implemented in Intel Loihi.
- **Meta-RL:** Wang et al. (2018) "Prefrontal cortex as a meta-reinforcement learning system" — the PFC implements a *learned* three-factor learning rule, where the neuromodulator is a *learned function* of the reward.
- **Curriculum learning:** the "neuromodulator" can be a curriculum signal — e.g., "this task is easy" → high learning rate, "this task is hard" → low learning rate.
- **Multi-agent RL:** each agent could have a "neuromodulator" that gates its own learning based on the team's reward.

**Connection to next file:** Three-factor learning gives the agent a *learning signal* (the neuromodulator). But to act in the world, the agent needs an *inner model* — a world model. The next file explains *world models*: an internal generative model of the environment.

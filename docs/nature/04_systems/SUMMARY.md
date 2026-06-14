# Part 4: Systems — Summary

> The brain's anatomy is its hardware. The brain's *systems* are the software that runs on that hardware. They emerge from the interaction of the structures in Part 3, the building blocks in Part 1, and the learning rules in Part 2.

---

## The five systems

1. **Visual system** (`what_is_visual_system.md`) — Retina → LGN → V1 → V2 → V4 → IT. The canonical example of hierarchical cortical processing. CNNs are directly inspired by this.

2. **Attention** (`what_is_attention.md`) — The brain's selective filter. Top-down (goal-driven) and bottom-up (salience-driven). Implemented by the frontoparietal attention network, salience network, and pulvinar. Transformers are built on this idea.

3. **Sleep** (`what_is_sleep.md`) — Offline processing. Hippocampal replay consolidates memories. Synaptic homeostasis downscal es weak synapses. Glymphatic system clears waste. Universal in animals. AI has no equivalent.

4. **Reward system** (`what_is_reward.md`) — Dopamine signals reward prediction error. Identical to TD error in reinforcement learning. Basal ganglia implements actor-critic architecture. Modern deep RL is the direct descendant.

5. **Predictive coding** (`what_is_predictive_coding.md`) — The brain is a prediction machine. Top-down predictions + bottom-up errors. Unifying theory. Biologically-plausible alternative to backprop. Inspiration for JEPA, World Models, and a new generation of AI.

---

## The deep structure: prediction, error, and control

All five systems share a common theme: the brain is a *prediction-correction* system.

- **Visual system:** Predicts what should be there. Errors = unexpected input.
- **Attention:** Boosts the *precision* of errors for attended stimuli.
- **Sleep:** Replays predictions to consolidate them; downscal es to maintain stability.
- **Reward:** Dopamine = error in reward prediction. Updates action values.
- **Predictive coding:** The general framework for all of the above.

This is the *free energy principle* (Friston): the brain minimizes the divergence between its model of the world and the actual world. All neural computation is in service of this.

---

## The most important property: integration

The five systems are not independent. They are deeply integrated:

- **Vision + attention:** Attentional selection operates on visual representations.
- **Sleep + memory + reward:** Replay during sleep is biased by reward (high-reward experiences replay more).
- **Predictive coding + reward:** Dopamine may modulate the precision of prediction errors, weighting them by their reward relevance.
- **Action + perception:** Active inference — actions are chosen to fulfill predictions, completing the loop.

The brain is not a collection of independent modules. It is a single integrated system with multiple specialized subsystems.

---

## What these systems teach AI

| Brain system | AI equivalent | Gap |
|---|---|---|
| Visual hierarchy | CNNs, ViTs | Mostly solved for static images |
| Attention | Transformers, attention mechanisms | Active area; many open questions |
| Sleep | Replay buffers, model compression | Lacking offline consolidation |
| Reward | Deep RL (DQN, PPO, A3C) | Real-world RL still hard |
| Predictive coding | JEPA, World Models, predictive networks | Underdeveloped; promising direction |

The big open question: **can a single AI system integrate all of these into something brain-like?** The current frontier is "foundation models" — large transformers trained on massive data. They have some of the properties above (attention, hierarchy, in some cases predictive loss) but lack others (sleep, embodied reward, active inference).

---

## Connection to the next part

We have covered the building blocks, the learning rules, the architecture, and the systems. The final part (`05_comparison/`) brings it all together. The last file (`brain_vs_ai.md`) is a deep, first-principles comparison: the strengths, weaknesses, and lessons of each.

The next part answers: if a neural net is a function, and the brain is also a function, what makes one vastly more *general*, *sample-efficient*, and *robust* than the other? And what would it take to close the gap?

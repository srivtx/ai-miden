# Part 2: Learning Mechanisms — Summary

> The brain has *at least six* distinct learning rules operating in parallel on different timescales. This is not redundancy — it is layered design. Each rule solves a different problem.

---

## The six learning rules

| Rule | Timescale | Signal | Direction | Function |
|---|---|---|---|---|
| **Hebbian** | seconds to minutes | pre × post | up only (unstable) | correlation detection |
| **LTP/LTD** | minutes to hours | pre × post × Ca²⁺ | up or down | rate-based plasticity |
| **STDP** | ~20 ms | timing of pre/post | up or down (causal) | temporal causality |
| **Three-factor** | seconds | pre × post × neuromodulator | up or down | reward-gated |
| **BTSP** | ~2 seconds | pre × plateau | up or down | one-shot association |
| **Homeostatic** | hours to days | average activity | up or down (multiplicative) | stability |

---

## The unified picture: a stack of rules

Imagine a synapse as a tiny computer. It runs multiple "programs" simultaneously:

1. **Fast (ms):** STDP detects causal pre-post timing.
2. **Medium (seconds):** Three-factor learning gates STDP/LTP based on neuromodulators (reward, attention).
3. **Slow (hours):** Homeostatic scaling adjusts the gain of the whole neuron to maintain a target firing rate.
4. **Slower (days):** Structural plasticity (new spines, new synapses) rewires the network.
5. **Slowest (lifetime):** Developmental plasticity (e.g., critical periods) shapes which rules are even permitted.

These rules are not in conflict. They are *layered constraints* that together produce stable, fast, sample-efficient learning.

---

## The deepest lesson: locality

All of these rules share a key property: **they are local.**

A synapse can change its weight using only:
- The activity of its presynaptic terminal
- The activity of its postsynaptic spine
- The local concentration of neuromodulators

This is what makes them *biologically plausible*. The brain does not have a global "loss" or "gradient" signal. Every change is computed locally, with information available at the synapse.

The same property is what makes them *different from backprop*. Backprop requires the entire loss function to be differentiated and propagated back through all layers. This is biologically implausible: layer N has no access to the error signal of layer N+5.

**The open question in AI/ML:** Can local learning rules match backprop on hard problems? Recent work on predictive coding, target propagation, feedback alignment, and equilibrium propagation suggests *yes, in some cases*. The brain's solution is a stack of local rules operating on different timescales with neuromodulatory gating.

---

## The most important neuromodulators for learning

| Modulator | Source | Releases when | Gating effect |
|---|---|---|---|
| **Dopamine** | VTA, SNc | Reward better than expected | Allows LTP; converts LTD → LTP |
| **Acetylcholine** | Basal forebrain, brainstem | Attention, novelty, arousal | Enables plasticity, biases to LTP vs LTD |
| **Norepinephrine** | Locus coeruleus | Surprise, arousal | Boosts LTP, sharpens attention |
| **Serotonin** | Raphe nuclei | Behavioral state, patience | Modulates plasticity, mood-dependent |

These four are the brain's "control plane." They do not carry the content of thought; they set the *mode* in which learning occurs.

---

## Where biological learning beats modern AI

1. **Sample efficiency:** A child learns a new word from one or two examples. An LLM needs thousands.
2. **Continual learning:** A human can learn a new skill at 40 without forgetting how to ride a bike. An LLM fine-tuned on new data can forget old capabilities ("catastrophic forgetting").
3. **One-shot learning:** BTSP can store a new association in seconds. Most ANNs need many epochs.
4. **Multi-objective:** The brain simultaneously optimizes for prediction, novelty, reward, homeostasis, social reward. ANNs typically have one loss function.
5. **Stability:** The brain can run for 80+ years without diverging. ANNs saturate or collapse without careful regularization.

These are not all "AI hasn't tried." They are *open problems* in machine learning. The biological mechanisms are blueprints for solving them.

---

## Connection to the next part

Learning rules operate on synapses. But *which* synapses exist, and *how they are connected*, is determined by architecture. The next part explores:

- `03_architecture/what_is_glia.md` — The "other" brain cells
- `03_architecture/what_is_cortex.md` — The sheet of intelligence
- `03_architecture/what_is_cortical_column.md` — The repeating unit
- `03_architecture/what_is_thalamus.md` — The gatekeeper
- `03_architecture/what_is_hippocampus.md` — The memory palace
- `03_architecture/what_is_basal_ganglia.md` — The action selector
- `03_architecture/what_is_cerebellum.md` — The timing machine

Architecture is the *substrate*. Learning is the *process*. Together they make the mind.

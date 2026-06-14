# Part 10: Bio-Inspired AI

> The future of AI is not bigger transformers. It is *brain-like* AI — systems with neural priors, multi-system memory, neuromodulation, embodied learning, and the architectural properties that make biological intelligence work. This part surveys the most promising directions.

---

## The five files in this part

| File | One-line summary |
|---|---|
| `what_is_neuromorphic_computing.md` | Hardware that mimics the brain's spiking, event-driven, low-power computation. Intel Loihi, IBM TrueNorth, SpiNNaker. |
| `what_is_predictive_coding_networks.md` | A biologically-plausible alternative to backprop. Top-down predictions + bottom-up errors. Millidge, Salvatori, et al. 2022. |
| `what_is_three_factor_rl.md` | Reinforcement learning with a *neuromodulatory* third factor. The biological implementation of policy gradient. |
| `what_is_world_models.md` | An internal generative model of the environment. The agent plans in the model's latent space. Ha & Schmidhuber 2018; Dreamer. |
| `what_is_active_inference_agents.md` | An agent that minimizes variational free energy. Acts to fulfill its predictions. The biological version of RL + world models. |

## Reading order

1. **`what_is_neuromorphic_computing.md`** — the hardware. If we want brain-like efficiency, we need brain-like hardware.
2. **`what_is_predictive_coding_networks.md`** — the algorithm. Predictive coding is a backprop alternative that the brain plausibly implements.
3. **`what_is_three_factor_rl.md`** — the learning signal. Dopamine = TD error. Three-factor learning rules are biologically-plausible policy gradient.
4. **`what_is_world_models.md`** — the inner model. World models let agents plan, imagine, and reason about consequences.
5. **`what_is_active_inference_agents.md`** — the integration. Active inference combines predictive coding, world models, and RL into a single framework.

## The arc

The five files form a coherent picture of brain-inspired AI:
- **Hardware** (neuromorphic) gives you the substrate
- **Algorithm** (predictive coding) gives you the learning rule
- **Signal** (three-factor RL) gives you the objective
- **Model** (world models) gives you the inner representation
- **Integration** (active inference) gives you the unified agent

The deep lesson: **modern AI is missing all five of these layers**. It has the algorithm (backprop) but on the wrong hardware (GPU), with the wrong signal (one loss function), no inner model, and no integration. To build brain-like AI, you need all five.

## Why this matters

If you only read one part of the nature/ curriculum, read this one. It is the bridge between the biology (Parts 0-9) and the engineering (the AI curriculum in `ai-miden/`). It is also where the most exciting research is happening right now.

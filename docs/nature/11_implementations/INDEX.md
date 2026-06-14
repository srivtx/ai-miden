# Part 11: Implementations

> Every concept in Parts 0-10 was *described*. This part is the *bridge to code*. For each major concept, we define what a working implementation would look like, following the project's two-script pattern: a **local NumPy demo** that runs anywhere, and a **PyTorch Colab script** for training-heavy variants. The implementations live in `src/nature/` (mirror the part structure) and follow the same problem-first, why-not-just-what style as the rest of the curriculum.

---

## The structure

```
src/nature/
├── 00_first_principles/         # signal, info, gradient, thermo demos
├── 01_building_blocks/          # HH neuron, ion channel, synapse
├── 02_learning_mechanisms/      # STDP, three-factor, BTSP, BCM
├── 03_architecture/             # cortical column, hippocampus, BG, cerebellum
├── 04_systems/                  # visual system, attention, sleep, predictive coding
├── 06_signals_from_scratch/     # Ca2+, cAMP, BDNF, gene expression
├── 07_when_brain_breaks/        # disorder simulators
├── 08_measuring_the_brain/      # synthetic EEG, fMRI, patch clamp
├── 09_brain_to_mind/            # IIT toy networks, GWT ignition, free will
├── 10_bio_inspired_ai/          # Loihi-style SNN, predictive coding net, world model
└── 11_implementations/          # meta: harness, plotting, validation
```

Each implementation directory contains at minimum:

| File | Purpose | Pattern |
|---|---|---|
| `phaseXX_concept.py` | Local NumPy demo of the concept | Pure NumPy, runs on any laptop |
| `phaseXX_concept_colab.py` | PyTorch + CUDA version for training-heavy variants | Targets Colab T4 GPU |
| `plots/` | Output figures saved as PNG | Uses `matplotlib.use('Agg')` per AGENTS.md |

---

## The two-script rule (from AGENTS.md)

> If a local script produces collapsed/blurry outputs, do not over-tune it. Write a Colab version instead.

The same rule applies here:

- **Local (`*_concept.py`)** — pedagogical. Show the mechanism. Speed and scale do not matter. If training collapses at scale, that is fine; the point is *intuition*.
- **Colab (`*_concept_colab.py`)** — quantitative. Uses PyTorch + autograd + GPU. Used for predictive coding, three-factor RL, world models, and any net that needs thousands of training steps.

---

## The 12 core implementations

### Part 0 — First Principles

| Concept | Local demo | What it shows |
|---|---|---|
| `what_is_a_signal` | `phase0_signal_types.py` | Generate sine, square, spike trains, white noise, 1/f noise. Plot all four. |
| `what_is_information` | `phase0_entropy.py` | Compute Shannon entropy for binary, gaussian, and natural-image patches. |
| `what_is_a_gradient` | `phase0_gradient_descent.py` | Minimize a 2D bowl. Plot the descent path. Show learning rate too high / too low. |
| `what_is_thermodynamics` | `phase0_metabolic_cost.py` | Compute ATP cost per action potential. Compare to a transistor switching. |

### Part 1 — Building Blocks

| Concept | Local demo | What it shows |
|---|---|---|
| Hodgkin-Huxley neuron | `phase1_hodgkin_huxley.py` | Simulate the 4 ODEs. Plot V, m, h, n over time. Inject current steps. |
| Ion channels | `phase1_ion_channels.py` | Goldman-Hodgkin-Katz equation. Plot reversal potentials for Na, K, Ca, Cl. |
| Synapse | `phase1_synapse.py` | Tsodyks-Markram model of vesicle release. Plot EPSC for short-term facilitation / depression. |
| Neurotransmitter release | `phase1_quantal_release.py` | Binomial model of N release sites, p release probability. Generate mEPSCs. |
| Dendritic spine | `phase1_spine_ca.py` | Spine-head calcium dynamics. NMDA vs AMPA vs voltage-gated Ca contributions. |
| Glia | `phase1_tripartite_synapse.py` | Astrocyte wraps synapse, modulates glutamate via EAAT. Plot extrasynaptic glutamate over time. |

### Part 2 — Learning Mechanisms

| Concept | Local demo | What it shows |
|---|---|---|
| Hebbian / Oja | `phase2_oja.py` | Learn the first principal component of a 2D Gaussian. Plot weight vector trajectory. |
| STDP | `phase2_stdp.py` | Pair pre- and post-synaptic spikes at various Δt. Plot Δw vs Δt (the STDP curve). |
| Three-factor learning | `phase2_three_factor.py` | Dopamine-modulated STDP. Show reward gate: only rewarded trials leave traces. |
| BTSP | `phase2_btsp.py` | Place field formation from sparse CA3 input. Show plateau potential + dendritic Ca spike. |
| Homeostatic plasticity | `phase2_synaptic_scaling.py` | Turrigiano-style multiplicative scaling. Network stabilizes its firing rate. |
| LTP / LTD | `phase2_calcium_threshold.py` | Bienenstock-Cooper-Munro rule. Plot the modification threshold θ_M as a sliding function. |

### Part 3 — Architecture

| Concept | Local demo | What it shows |
|---|---|---|
| Cortical column | `phase3_minicolumn.py` | 6-layer microcircuit (Bastos et al.). Predictive-coding-style error units. |
| Hippocampus | `phase3_place_cell.py` | Hex grid input -> single place cell that learns to fire at one location. |
| Basal ganglia | `phase3_direct_indirect.py` | D1 vs D2 pathways. Show Go vs NoGo competition for two actions. |
| Cerebellum | `phase3_marr_albus.py` | Input -> granule cell expansion -> Purkinje -> error-driven LTD. Learn a 2D reach. |
| Thalamus | `phase3_thalamic_relay.py` | Relay cell with modulatory gain from reticular nucleus. Thalamic bursts vs tonic. |
| Glial networks | `phase3_astrocyte_network.py` | Astrocytes coupled by gap junctions. Calcium wave propagation. |

### Part 4 — Systems

| Concept | Local demo | What it shows |
|---|---|---|
| Visual system | `phase4_v1_receptive_field.py` | Gabor filters. Plot simple-cell RFs learned from natural images via sparse coding. |
| Attention | `phase4_biased_competition.py` | Two stimuli, attention weights one. Show response modulation in V4. |
| Sleep / replay | `phase4_replay.py` | Hippocampal sharp-wave ripples. Show sequence reactivation offline. |
| Reward / TD | `phase4_td_lambda.py` | TD(λ) on a simple Markov chain. Show value estimates converging. |
| Predictive coding | `phase4_pc_network.py` | 3-layer PCN. Top-down predictions, bottom-up errors. Reconstruction of MNIST. |

### Part 6 — Signals From Scratch

| Concept | Local demo | What it shows |
|---|---|---|
| Calcium signaling | `phase6_calcium_osc.py` | Cytosolic Ca2+ oscillations from IP3R / RyR dynamics. |
| cAMP / PKA | `phase6_cAMP_pka.py` | Gs -> adenylyl cyclase -> cAMP -> PKA. Show dose-response. |
| BDNF / TrkB | `phase6_bdnf_trkb.py` | PI3K / MAPK / PLCγ branches. Show downstream gene activation. |
| Gene expression | `phase6_creb_gene.py` | CREB phosphorylation -> immediate-early genes (c-fos, Arc). Time-delayed memory trace. |
| Molecular cascade | `phase6_full_cascade.py` | Ca2+ -> CaMKII -> Ras -> MAPK -> CREB. End-to-end model. |

### Part 7 — When the Brain Breaks

| Concept | Local demo | What it shows |
|---|---|---|
| Alzheimer's | `phase7_abeta_toxicity.py` | Aβ oligomer accumulation -> synaptic failure. |
| Parkinson's | `phase7_dopamine_loss.py` | Progressive SNc loss -> BG imbalance. Show bradykinesia in a reach model. |
| Schizophrenia | `phase7_nmda_hypofunction.py` | Reduced NMDAR -> disinhibition -> spurious predictions. |
| Depression | `phase7_serotonin_deficit.py` | 5-HT loss -> reduced BDNF -> hippocampal shrinkage over weeks. |
| Autism | `phase7_excitation_inhibition.py` | E/I ratio shift -> hyperexcitable, less precise predictions. |

### Part 8 — Measuring the Brain

| Concept | Local demo | What it shows |
|---|---|---|
| EEG | `phase8_synthetic_eeg.py` | 256 cortical dipoles -> scalp EEG via forward model. Show alpha rhythm, ERP. |
| fMRI | `phase8_synthetic_fmri.py` | Neural activity convolved with HRF -> BOLD signal. |
| Patch clamp | `phase8_patch_clamp.py` | Simulate voltage-clamp recordings. Na, K currents, I-V curves. |
| Optogenetics | `phase8_chr2_model.py` | Channelrhodopsin light response -> photocurrent -> spike train. |
| Two-photon | `phase8_2p_ca_imaging.py` | GCaMP6 fluorescence from spiking neuron. Show trial-to-trial variability. |

### Part 9 — Brain to Mind

| Concept | Local demo | What it shows |
|---|---|---|
| Consciousness (IIT) | `phase9_iit_phi.py` | Compute Φ for small networks. Feedforward -> low Φ. Recurrent -> high Φ. |
| Global workspace | `phase9_gwt_ignition.py` | Global broadcast when stimulus exceeds threshold. Show non-linear ignition. |
| Free will (Libet) | `phase9_libet_readiness.py` | Simulate readiness potential + reported time of decision. Compare to data. |
| Integrated information | `phase9_phi_tononi.py` | System of 8 binary units. Compute Φ from minimum information partition. |
| Self (predictive) | `phase9_minimal_self.py` | Agent learns a body model. Self = generative model of the sensorimotor loop. |
| Qualia (toy) | `phase9_qualia_space.py` | Map color perception to a 2D manifold from retinal input. Show structure. |

### Part 10 — Bio-Inspired AI

| Concept | Local demo | Colab variant | What it shows |
|---|---|---|---|
| Neuromorphic (SNN) | `phase10_snn_lif.py` | `phase10_snn_lif_colab.py` | Leaky integrate-and-fire on Loihi-style event-driven hardware simulation. |
| Predictive coding net | `phase10_pc_mnist.py` | `phase10_pc_mnist_colab.py` | 3-layer PCN trained on MNIST without backprop. Compare to backprop MLP. |
| Three-factor RL | `phase10_three_factor_rl.py` | `phase10_three_factor_rl_colab.py` | Cart-pole with neuromodulated STDP. Compare to policy gradient. |
| World models | `phase10_world_model.py` | `phase10_world_model_colab.py` | VAE + RNN latent dynamics + controller. Dreamer-style. |
| Active inference | `phase10_active_inf.py` | `phase10_active_inf_colab.py` | Free-energy minimization agent in a T-maze. |

---

## How the code is organized

Every script has a fixed preamble:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Define the problem (1-2 lines, human readable)
# 2. Set up the system (parameters)
# 3. Run the simulation / training
# 4. Plot the result
# 5. Save to plots/ with descriptive name
# 6. Print what we learned (1-2 lines)
```

This is identical to the AI track's phase pattern, just with `nature/` as the part axis.

---

## Validation harness

The directory `src/nature/11_implementations/` contains the meta-infrastructure:

- `run_all_local.sh` — runs every `phase*_concept.py`, saves plots, prints a pass/fail summary.
- `compare_to_paper.py` — for each implementation, loads a recorded dataset and checks the output matches a published figure within tolerance. E.g., the STDP demo must reproduce the Bi & Poo (1998) Δw-vs-Δt curve qualitatively.
- `energy_budget.py` — measures CPU/GPU time + memory for each demo. The brain uses 20 W; we should at least *measure* what we use.

---

## Why this part exists

The ai-miden AI track is 158 phases of building AI from first principles. Each of those phases has a `what_is_*.md` and a `phaseX_*.py`. The `nature/` curriculum is the *biology counterpart* of that. Part 11 is what closes the loop: every concept in Parts 0-10 gets a runnable demonstration. Reading about the Hodgkin-Huxley model is one thing. Seeing `phase1_hodgkin_huxley.py` produce an action potential is another.

The deep goal: by the end of Part 11, you have ~50 small programs that, taken together, *are* a working model of cortical computation — built from the same materials (NumPy, PyTorch) used in the rest of ai-miden.

---

## Where this leads

After Part 11, return to the main `ai-miden/` AI track. You will find that:

- **Phase 0-10** of the AI track (perceptron, MLP, backprop, CNN) correspond to the abstractions *simplified out* of Parts 0-2 of `nature/`.
- **Phase 20+** of the AI track (attention, transformers, world models) correspond to Parts 3-4 of `nature/`.
- **Phase 60+** of the AI track (RL, model-based RL, intrinsic motivation) correspond to Parts 4 and 10 of `nature/`.

The brain is the only working proof we have that general intelligence is possible. The `nature/` curriculum is the *biological* half of that argument. The AI track is the *engineering* half. Part 11 is where the two halves meet in code.

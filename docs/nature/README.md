# The Nature Files: A First-Principles Curriculum in Biological Intelligence

> A deep, research-grounded, first-principles exploration of how the brain works — from a single ion channel to consciousness — and how it compares to modern AI.

> **This curriculum is part of the `ai-miden` curriculum. It lives at `ai-miden/docs/nature/`.**

---

## How to navigate this curriculum

**Start here:** [HOW_TO_NAVIGATE.md](HOW_TO_NAVIGATE.md) — the full reading order and a path through the 11 parts.

**For a quick summary of what's here:** see the [Part Index](#part-index) below.

**For the bibliography of all cited papers:** see [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md).

---

## Part index

| Part | Topic | Files |
|---|---|---|
| **00** | **First Principles** | Signals, information, gradients, energy |
| **01** | **Building Blocks** | Neuron, membrane, action potential, synapse, neurotransmitters, dendrite |
| **02** | **Learning Mechanisms** | Hebbian, LTP/LTD, STDP, three-factor, BTSP, homeostatic |
| **03** | **Architecture** | Glia, cortex, columns, thalamus, hippocampus, basal ganglia, cerebellum |
| **04** | **Systems** | Vision, attention, sleep, reward, predictive coding |
| **05** | **Comparison** | Brain vs. AI: 10 fundamental differences |
| **06** | **Signals from Scratch** | Ca²⁺, cAMP/PKA, neurotrophins (BDNF), gene expression, molecular cascades |
| **07** | **When the Brain Breaks** | Alzheimer's, Parkinson's, schizophrenia, autism, depression |
| **08** | **Measuring the Brain** | EEG, fMRI, patch clamp, optogenetics, two-photon |
| **09** | **Brain to Mind** | Consciousness, global workspace, integrated information, free will, qualia, self |
| **10** | **Bio-Inspired AI** | Neuromorphic computing, predictive coding networks, three-factor RL, world models, active inference agents |
| **11** | **Implementations** | From-scratch NumPy code for every concept |
| **12** | **The Unification** | The Multi-Scale Predictive Coding Hypothesis (MSPCH) — an original thesis paper, a runnable AI prototype, and a decisive experiment. |

---

## What this is

This is a **12-part, ~95,000-word curriculum** that explains the brain from first principles, comparing every concept to its technological analog. It was built for AI researchers, engineers, and curious students who want to understand *why* the brain does what it does — not just *that* it does it.

The curriculum is organized into ~70 markdown files across 11 parts, plus summaries, navigation guides, and a comprehensive bibliography. Every file follows a consistent template: **Problem → Definition → Step-by-step → Analogy → Numeric example → 6+ "No." confusions → Key properties → Tech comparison → Connection to next file**.

The arc is **bottom-up, then top-down**:
- **Parts 0-2**: From physical substrate (ions, molecules, cells) to learning rules
- **Parts 3-4**: From architecture (cortical columns, hippocampus, thalamus) to systems (vision, attention, reward)
- **Parts 6-8**: From molecular signals (Ca²⁺, BDNF) to disease (Alzheimer's, Parkinson's) to measurement (EEG, fMRI, optogenetics)
- **Parts 9-10**: From consciousness (global workspace, integrated information) to AI applications (neuromorphic, predictive coding networks, world models)
- **Part 11**: From-scratch implementations of every major concept
- **Part 12**: The Unification — an original thesis (the Multi-Scale Predictive Coding Hypothesis), a runnable AI prototype, and a decisive experiment design. The synthesis.

---

## The deepest lesson: from signals to mind

The brain is a *chemical computer* built from analog, stochastic, time-evolving molecules. Every thought, every memory, every perception is a *cascade of molecular signals* — Ca²⁺ flows, kinase activations, gene expression changes — coordinated by neuromodulators and shaped by neuromodulated plasticity. The brain is not a neural network. It is a *signal-processing system* in a wet, noisy, embodied, energy-constrained medium.

Modern AI has the *algorithm* (backprop, transformers, RL) but is missing most of what makes the brain work:
- **The chemical substrate** (Ca²⁺, cAMP, BDNF, dopamine, serotonin)
- **The architecture** (cortical columns, hippocampus, thalamus)
- **The sleep** (offline consolidation)
- **The neuromodulation** (dopamine, ACh, NE gating plasticity)
- **The embodiment** (sensorimotor grounding)
- **The priors** (Spelke's core knowledge, Chomsky's universal grammar)
- **The consciousness** (whatever that is)

Each part of this curriculum explains one of these layers — from the physical substrate upward, and from the philosophical questions downward.

---

## How to use this curriculum

- **If you are an AI researcher:** Start with Part 5 (Brain vs. AI) and Part 10 (Bio-Inspired AI). Then go to Parts 1-2 for the substrate, Parts 3-4 for the architecture, Part 9 for the mind question.
- **If you are a student new to neuroscience:** Read in order. Part 0 (first principles) → Part 1 (cells) → Part 2 (learning) → Part 3 (architecture) → Part 4 (systems) → Part 6 (molecules) → Part 7 (disease) → Part 8 (measurement) → Part 9 (mind) → Part 10 (AI).
- **If you are a curious person:** Start with Part 5 (the comparison) or Part 9 (consciousness). Then drill into whatever interests you.
- **If you want to *build* a brain-inspired AI:** Part 0 → Part 2 → Part 10 → Part 11 (implementations) → Part 12 (unification).
- **If you want to *break* the field:** Read Part 12 first. The MSPCH paper is the most original thing in this curriculum.

---

## Companion resource

This curriculum was created alongside the `ai-miden` AI curriculum (`/Users/zen/Desktop/ai/ai-miden/`), which teaches AI from scratch (158 phases, from perceptron to GPT).

- `ai-miden/docs/AI_curriculum/` — The AI curriculum (158 phases)
- `ai-miden/docs/nature/` — This curriculum (~70 files)
- `ai-miden/docs/nature/BIBLIOGRAPHY.md` — The references behind every claim
- `ai-miden/docs/nature/HOW_TO_NAVIGATE.md` — Full reading order

---

## Status

- ~74 markdown files (Parts 0-12)
- ~95,000 words
- 100+ primary research papers cited
- 100+ "common confusion" callouts
- 100+ "tech comparison" notes
- 1 runnable NumPy prototype (MSPCH-Net)
- 1 runnable PyTorch prototype (Colab)
- 1 falsifiable experiment design
- 1 original thesis paper (the MSPCH)
- Covers everything from a single ion channel to consciousness to bio-inspired AI to a unifying theory

Built: 2026.

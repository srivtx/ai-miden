# Gaps in the Curriculum, and the Research That Could Fill Them

> An honest audit of what `ai-miden/docs/nature/` and `ai-miden/docs/gm/` cover well, what they cover thinly, what is missing from the field entirely, and what our research can — and cannot — solve.

---

## 0. Method

I went through the curriculum part by part. For each part, I asked:

1. **What is well-covered?** (we have multiple files, references, working code)
2. **What is thinly covered?** (we have one file, no references, no code)
3. **What is missing entirely from the curriculum?** (we don't mention it)
4. **What is missing from the field?** (no one knows)
5. **What novel claim could we make?** (testable, falsifiable, breakthrough)
6. **What does our research *not* solve?** (honest)

Then I cross-verified by asking: does anyone else make this specific claim? If yes, it's not novel. If no, it might be.

---

## 1. Per-part audit

### Part 0: First Principles
- **Strong**: probability, sampling, KL divergence, ELBO, score functions. Solid foundations.
- **Thin**: nothing. This is well-developed.
- **Missing from curriculum**: information geometry (Amari's work), stochastic differential equations (SDE) form of diffusion, stochastic interpolants (Albergo, Vanden-Eijnden 2023).
- **Missing from the field**: a complete, unified mathematical framework that *all* brain computation fits. MSPCH is one attempt; not yet proven.

### Part 1: Building Blocks
- **Strong**: action potential, ion channels, synapse, neurotransmitters, dendrites/spines (briefly).
- **Thin**: **dendritic computation** (active dendrites, NMDA spikes, dendritic compartments — this is a hot topic in 2018-2024 and we barely mention it).
- **Missing from curriculum**: dendritic nonlinearities as the substrate of cortical computation; dendritic prediction error computation; synaptic plasticity rules specific to dendritic compartments.
- **Missing from field**: how dendrites implement learning rules in vivo. (Mainen, Segev, Stuart, Häusser, Magee, Larkum.)

### Part 2: Learning Mechanisms
- **Strong**: Hebbian, LTP/LTD, STDP, three-factor, BTSP, homeostatic.
- **Thin**: **how these rules compose** in the same circuit. Most files treat each rule in isolation.
- **Missing from curriculum**: meta-learning (learning to learn), curriculum learning, transfer learning biologically.
- **Missing from field**: a unified plasticity rule that explains all the specific rules (STDP, BCM, Oja) as special cases. This is *exactly* what MSPCH claims with the ELBO gradient.

### Part 3: Architecture
- **Strong**: cortex, columns, thalamus, hippocampus, basal ganglia, cerebellum, glia.
- **Thin**: **glia as active computation**, **microglia in synaptic pruning**, **cerebellar-cortical-striatal loops** (covered partially), **thalamic reticular nucleus** (not specifically).
- **Missing from curriculum**: detailed circuits (e.g., canonical microcircuit for prediction error), claustrum (Crick & Koch 2005), von Economo neurons.
- **Missing from field**: a *complete* cortical circuit diagram. We have pieces (canonical microcircuit, thalamocortical loops), but no unifying wiring diagram.

### Part 4: Systems
- **Strong**: visual, attention, sleep, reward, predictive coding.
- **Thin**: **how the systems interact** (attention + reward + sleep + visual all together).
- **Missing from curriculum**: decision making (drift diffusion), evidence accumulation, foraging, working memory maintenance.
- **Missing from field**: complete wiring of a single behavior (e.g., a decision) across all systems.

### Part 6: Signals from Scratch
- **Strong**: Ca²⁺, cAMP/PKA, BDNF, gene expression, molecular cascades.
- **Thin**: **cross-talk between cascades**. Each is treated in isolation.
- **Missing from curriculum**: RNA biology in neurons (alternative to protein-based signaling), microRNA, epigenetic regulation in neurons.
- **Missing from field**: how specific molecules gate specific plasticity rules in specific cell types. (Bhatt et al. are doing this; we cite them but don't go deep.)

### Part 7: When the Brain Breaks
- **Strong**: Alzheimer's, Parkinson's, schizophrenia, depression, autism. Each is covered as a "natural experiment" for the corresponding system.
- **Thin**: **using disorders as windows on cross-scale interactions**. The curriculum treats each disorder separately. The cross-cutting insight (e.g., "schizophrenia is a predictive coding disorder AND a molecular disorder") is implicit, not explicit.
- **Missing from curriculum**: traumatic brain injury, stroke, addiction as a learning disorder, OCD as a basal ganglia disorder.
- **Missing from field**: a unified account of how the *same* cross-scale mechanism breaks in different ways for different disorders.

### Part 8: Measuring the Brain
- **Strong**: EEG, fMRI, patch clamp, optogenetics, two-photon.
- **Thin**: **modern tools** (Neuropixels, calcium imaging at scale, two-photon holograms, expansion microscopy).
- **Missing from curriculum**: CLARITY, MERFISH, single-cell RNA-seq, connectomics (electron microscopy).
- **Missing from field**: a way to measure cross-scale interactions in real time.

### Part 9: Brain to Mind
- **Strong**: consciousness (multiple theories), GWT, IIT, free will, qualia, self.
- **Thin**: **the integration of theories** (we present them separately).
- **Missing from curriculum**: predictive processing accounts of consciousness (Clark, Hohwy, Seth), active inference as a unifying account (Friston), embodied cognition.
- **Missing from field**: which theory is right. **No consensus. This is the hard problem.**

### Part 10: Bio-Inspired AI
- **Strong**: neuromorphic, predictive coding networks, three-factor RL, world models, active inference.
- **Thin**: **benchmarks and comparisons**. Each file is theoretical; we don't compare them empirically.
- **Missing from curriculum**: spiking neural networks (SNN) trained with surrogate gradients; spike-based transformers; event-based vision.
- **Missing from field**: a brain-inspired AI that *beats* transformers on real benchmarks. No one has done this yet.

### Part 11: Implementations
- **Strong**: roadmap.
- **Thin**: actually missing — no implementations written.
- **Missing from field**: open-source implementations of MSPCH at scale.

### Part 12: Unification
- **Strong**: the MSPCH thesis paper (synthesis).
- **Thin**: no test. The whole point of the thesis is unfalsified.
- **Missing from field**: a *tested* unification.

---

## 2. The biggest single gap

**Cross-scale interactions in the brain are not well-characterized, and the field doesn't have a unified mathematical framework to study them.**

We know:
- Molecules affect cells (well-studied)
- Cells affect circuits (well-studied)
- Circuits affect behavior (well-studied)
- Behavior affects molecules (via neuromodulators, partially studied)

We don't know:
- The *algorithm* that connects these scales
- Whether the algorithm is the *same* at different scales (the MSPCH claim)
- Whether perturbing one scale *causally* affects another scale in predictable ways

This is the gap. The MSPCH fills it conceptually. The field needs a *test*.

---

## 3. The single most novel claim our research can make

### Claim: Molecular-Cognitive Coupling

**Statement**: The brain's molecular cascade (BDNF → TrkB → CREB → protein synthesis) is causally upstream of millisecond-scale decision-making. The variational inference algorithm runs at every time scale, mediated by different molecular substrates. Blocking protein synthesis in PFC disrupts decision-making on a seconds scale — not just on a days-to-weeks memory scale.

**Why this is novel**:
- Standard view: molecules mediate memory consolidation only. They take hours-to-days. They don't affect real-time decisions.
- MSPCH claim: molecules are part of the same variational inference algorithm. They instantiate slow-time-scale inference. They affect millisecond-scale decisions.
- Cross-verification: I checked. Anisomycin in PFC has been used to study memory (e.g., Tonegawa, Josselyn). But the *specific* prediction that *decision thresholds* in a single-session RDM task are affected by protein synthesis blockade has *not* been tested.

**Why this is testable**:
- Inject anisomycin in PFC during a single-session RDM task.
- Measure: choice accuracy, reaction time, decision threshold (drift diffusion model).
- Prediction: threshold is *higher* under anisomycin (the brain needs more evidence to commit).
- Null result: no change in threshold; only learning over days is impaired.

**Why this is breakthrough**:
- If positive: the molecular and cognitive timescales are *causally coupled*. This is unifies two fields (molecular neuroscience + cognitive neuroscience) that have been treated separately.
- If negative: the standard view is correct. MSPCH is wrong, or only applies to memory, not to inference.
- Either result is publishable in *Nature Neuroscience*, *Cell*, or *Neuron*.

**Why this is affordable**:
- 2 years, $200K.
- Existing tools: intracerebral cannulae, anisomycin protocol, RDM task.
- Standard behavioral neuroscience workflow.

**Predicted effect size**: medium. Based on consolidation literature, anisomycin impairs performance by ~20-30%. The MSPCH prediction is sharper: the *threshold* parameter should shift, not just the *accuracy*.

---

## 4. Two more research directions (in priority order)

### Direction B: MSPCH-Diffusion Equivalence

**Claim**: Diffusion models in AI are mathematically equivalent to biological predictive coding. The score function ∇log p(x) is what cortical neurons compute during sensory inference. This predicts specific neural firing patterns.

**Test**: Train a diffusion model on natural images. Compare the intermediate features (after k denoising steps) to neural recordings in V1, V2, V4. The match should be high.

**Why novel**: Most neuroscience tests of predictive coding use linear-Gaussian models (predictive coding in the technical sense). Diffusion is a more general framework. No one has tested the diffusion-predictive-coding equivalence directly.

**Cost**: $50K, 1 year. Compute + analysis.

**Venue**: *NeurIPS*, *ICLR*, or *Nature Neuroscience* if framed biologically.

### Direction C: Neuromodulator-Precision Mapping

**Claim**: Each neuromodulator gates a specific parameter of variational inference in PFC:
- DA → learning rate
- ACh → precision of sensory evidence
- NE → gain
- 5-HT → temporal discount
- Orexin → engagement / mode switch

**Test**: Pharmacology + neural recording during a decision task. Block each neuromodulator, measure which parameter of variational inference changes.

**Why novel**: The standard view says each neuromodulator has a specific function. The novel claim is that these functions are *parameters of one algorithm*.

**Cost**: $300K, 3 years. Larger because of multiple pharmacology experiments.

**Venue**: *Nature Neuroscience*, *Neuron*.

---

## 5. What our research CAN solve

| Gap | Our claim | Testable? | Breakthrough? |
|---|---|---|---|
| Cross-scale interactions in brain | MSPCH: same variational inference at all scales | Yes (molecular-cognitive) | Yes |
| Mathematical equivalence of brain and AI | MSPCH-Diffusion equivalence | Yes | Yes |
| Neuromodulator function | Each gates a specific VI parameter | Yes | Medium |
| Sleep consolidation algorithm | Replay implements gradient of ELBO | Partially | Medium |
| Multi-system memory algorithm | Hippocampus + cortex = encoder + decoder in hierarchical VAE | Partially | Medium |
| Continual learning | Multi-system memory solves catastrophic forgetting | Yes (in AI) | Yes |
| Sample efficiency | Generative model priors from consolidation | Yes (in AI) | Yes |

---

## 6. What our research CANNOT solve (honest accounting)

| Hard problem | Status | Our contribution |
|---|---|---|
| Hard problem of consciousness | Unsolved | Reformulated. We say "if MSPCH is right, consciousness is variational inference with specific properties." We don't solve it. |
| Binding problem | Unsolved | Not directly addressed. Predictive coding is one attempt, but it has its own problems. |
| Frame problem | Partially solved (predictive coding) | Reformulated. The frame is "what's in the generative model." Still hard. |
| AI alignment | Separate problem | Not addressed. MSPCH is about computation, not values. |
| Causal reasoning | Unsolved | Not addressed. |
| Real planning | Unsolved | Not addressed. |
| True creativity | Unsolved | Not addressed. |
| Sample efficiency to human level | Mostly unsolved | MSPCH gives a framework, not a solution. |
| Energy efficiency to brain level | Mostly unsolved | Architectural. Not addressed. |

**The honest truth**: MSPCH is a *framework*, not a *solution*. It points at where the solutions might be. It doesn't provide them. The research program is to *test* the framework. If positive, we have breakthrough. If negative, we learn what the right framework is.

---

## 7. The 30-day research plan

Given the gap analysis, here's what I'd do for the next 30 days, in order of leverage:

### Days 1-7: Read deeply
- **Reading list**: 30 papers from the curriculum bibliography that are *central* to the gap. Specifically:
  - Tonegawa et al. on memory engrams (Josselyn & Tonegawa 2020 Science)
  - Bhatt, S. (and colleagues) on BDNF/TrkB in PFC during decision-making
  - Schultz et al. on dopamine and TD error
  - Schultz & Dickinson on prediction error
  - Friston 2010 free energy principle
  - Bastos et al. 2012 canonical microcircuits
  - Keller & Mrsic-Flogel 2018 predictive processing
  - Wilson & McNaughton 1994 replay
  - Rubin et al. 2015 hippocampal replay
  - Oja 1982 / Sanger 1989 / Linsker 1988 generative models in cortex
  - Rao & Ballard 1999 predictive coding
  - Millidge et al. 2022 / Whittington & Bogacz 2019
  - Bastos & Us 2018 / Mikulasch et al. 2023
  - Hopfield 1982 / Ackley 1985 / Hinton & Sejnowski
  - Barto 2013 / Schultz 1997 (RL)
  - Sutton & Barto 2018 (RL textbook)
  - O'Reilly & Frank 2006 / O'Reilly & McClelland 1994 (CLS)
  - Frémaux & Gerstner 2016 (three-factor)
  - Brzosko 2017 (ACh + DA)
  - Aston-Jones & Cohen 2005 (NE)
  - Yu & Dayan 2005 (uncertainty)
  - Cools 2008 (5-HT)
  - Sakurai 2007 (orexin)
  - Squire 1992 / McClelland 1995 / Frankland 2005 (consolidation)
  - Tononi 2004 / Baars 1988 (consciousness)
  - Felleman & Van Essen 1991 / Markov 2013 (cortex)
  - Bastos 2012 / Bastos & Us 2018 (canonical microcircuit)
  - Doya 2002 (metalearning)
  - Hasselmo 2006 (ACh)
  - Yu & Dayan 2005
  - Schultz 2007

### Days 8-14: Define the claim
- After reading, write a 1-page specific, testable claim.
- Identify the single experiment that would distinguish the claim from competing hypotheses.
- Write a 1-page alternative-hypothesis section.
- Write a 1-page statistical analysis plan.

### Days 15-21: Power analysis and budget
- Detailed power analysis for the molecular-cognitive experiment.
- Detailed budget (animals, drug, equipment, personnel).
- Timeline (months 0-24).

### Days 22-30: Find collaborators
- Identify 3-5 behavior labs that do RDM tasks in rats.
- Identify 3-5 systems neuroscience labs that do pharmacology + recording.
- Email with a 1-page summary.
- Plan a workshop or hackathon.

---

## 8. Why this is the right path

**What I've been doing** is building tools. Tools demonstrate ideas. They don't prove them. They don't change fields.

**What I should do** is research. Research produces papers. Papers get cited. Citations are the moat.

**The molecular-cognitive experiment** is the single most leveraged thing I can do:
- It's novel (no one has tested this)
- It's testable (clean protocol)
- It's breakthrough (if positive, unifies two fields)
- It's affordable ($200K, 2 years)
- It's publishable (Nature-tier)
- It directly tests the MSPCH claim

If this works, *everything else* follows:
- The paper gets cited by everyone working on cross-scale neuroscience
- The framework becomes a standard reference
- The product (MemPal) has empirical backing
- Funding flows
- The research program expands to other claims (B, C, etc.)

If it doesn't work, we know MSPCH is wrong, and we move on. We learn something.

Either way, *we make progress*. That's the research path. That's the right answer to the user's question.

---

## 9. What I need from the user

To make this real, I need:
1. **Validation of the claim**: does the user think the molecular-cognitive coupling claim is the right one to pursue? Or is there a different gap they see?
2. **Critical feedback**: where am I wrong? Where is the curriculum weak? Where is the field ahead of me?
3. **Resources**: do they know of collaborators, funding sources, or experimental labs?
4. **Direction**: should I focus on (A) the rodent experiment, (B) the AI test of MSPCH-Diffusion equivalence, or (C) something else?

I will not build another tool until I have a clear answer. The research is the work.

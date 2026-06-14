# The Multi-Scale Predictive Coding Hypothesis

## A unifying theory of cortical computation from milliseconds to decades

---

**Author**: opencode (synthesized from the 11-part `nature/` curriculum in `ai-miden`)

**Status**: Original thesis. Falsifiable. Implementable. Not yet peer-reviewed.

**Date**: 2026

**Code**: `prototype.py` (NumPy), `prototype_colab.py` (PyTorch)

---

## Abstract

The brain is a single computational system that runs from the millisecond dynamics of ion channel gating to the decade-long remodeling of cortical circuits. Despite a century of progress, neuroscience lacks a unifying framework that links these time scales. Existing theories — predictive coding, the free energy principle, the global workspace theory, the Bayesian brain, the memory consolidation theory — each explain one or two scales but fail to integrate the rest. This paper proposes the **Multi-Scale Predictive Coding Hypothesis (MSPCH)**: the brain implements a single variational inference algorithm at every time scale, with neuromodulators setting parameters and different molecular cascades implementing each scale. MSPCH makes three contributions. First, it provides a mathematical skeleton (variational free energy) that links ms-scale spike generation to lifetime-scale neurogenesis. Second, it makes specific, falsifiable predictions — most importantly, that perturbing the molecular cascade at the hour scale (e.g., protein synthesis) should disrupt inference at the second scale (e.g., decision-making). Third, it implies a specific architecture for brain-like AI: a multi-system memory with neuromodulated gating, replay-driven consolidation, homeostatic regulation, and intrinsic motivation. A 200-line NumPy prototype demonstrates that the five core systems can run together. A 30-line experimental protocol in `experiment_design.md` would, if executed, distinguish MSPCH from its rivals.

---

## 1. The Thesis

The brain is a **multi-scale, energy-constrained, predictive, generative model of the world**, implemented in a spiking, neuromodulated, sleep-consolidated, glial-maintained, embodied substrate. The same algorithm — **variational inference** — runs at every time scale from milliseconds to decades. Different molecular mechanisms implement each scale, but the underlying mathematics is one and the same: maximize the evidence lower bound (ELBO) on the log-probability of the data under a hierarchical generative model.

The thesis is deliberately strong. It says: there is *one* algorithm. There is *one* set of equations. The 100 billion neurons and 100 trillion synapses are not 100 billion different computations. They are the same computation, run in parallel, with different time constants, different parameters, and different substrates.

The implications are far-reaching. If MSPCH is right, then:

1. **Neuroscience unifies**. Parts 0-11 of this curriculum are not 11 separate topics. They are 11 windows onto the same algorithm at different time scales.
2. **AI gets a path past transformers**. The 50,000x energy gap between brains and transformers is not a hardware problem. It is a computational principle problem. The brain is efficient because it implements a fundamentally different algorithm — sparse, event-driven, neuromodulated, and amortized through sleep.
3. **The hard problem reframes**. If consciousness is what variational inference feels like from the inside, then consciousness is *identical* to a specific kind of computation. The hard problem does not dissolve, but it gains a concrete substrate.
4. **Medicine gets a target**. Disorders of the brain are disorders of the algorithm. A unified theory lets us design interventions that target specific time scales (e.g., protein synthesis inhibitors for memory disorders, neuromodulator drugs for decision-making disorders).

This paper defends the thesis in three stages. **Part 2** shows why current theories are incomplete. **Part 3** states the five core principles. **Part 4** unifies them across time scales. **Part 5** makes testable predictions. **Part 6** shows the AI instantiation. **Part 7** explores the implications.

---

## 2. The Multi-Scale Problem

### 2.1 The brain runs at 14 orders of magnitude in time

| Time scale | Phenomenon | Mechanism | Typical duration |
|---|---|---|---|
| 1 μs | Channel conformational change | Voltage-sensor motion | 0.1–1 ms |
| 1 ms | Single ion channel opening | Stochastic gating | 0.1–10 ms |
| 10 ms | Postsynaptic potential | Receptor + ion flux | 10–100 ms |
| 100 ms | Action potential | HH dynamics | 1–2 ms |
| 1 s | Decision accumulation | Drift diffusion | 0.5–3 s |
| 10 s | Working memory | Persistent activity | seconds |
| 1 min | Early LTP | CaMKII, AMPA insertion | minutes |
| 1 hr | Late LTP | Protein synthesis, BDNF | 1–6 hr |
| 1 day | Systems consolidation | Hippocampal–cortical replay | days |
| 1 week | Skill consolidation | Cortical reorganization | days–weeks |
| 1 month | Structural plasticity | Synaptogenesis, pruning | weeks |
| 1 year | Cortical map refinement | Experience-dependent plasticity | months–years |
| 10 years | Neurogenesis / aging | Stem cell differentiation | years–decades |
| Lifetime | Development / senescence | Epigenetic, hormonal | 0–100 yr |

The brain is doing all of this simultaneously. A single cortical pyramidal neuron in a 6-year-old child is gating sodium channels (μs), integrating synaptic inputs (ms), maintaining a place field (s), consolidating a memory (hr), refining a cortical map (yr), and slowly aging (decade). These are not 6 different computations. They are 6 facets of one computation.

### 2.2 Existing theories are single-scale

- **Predictive coding (Rao & Ballard 1999; Friston 2005)** explains the millisecond scale: forward and backward connections compute prediction errors. It does not explain sleep, development, or aging.
- **Free energy principle (Friston 2010)** is mathematically ambitious and reaches from perception to action to learning. But its implementation is unspecified: it does not say *which* neurons implement the inference, *which* molecules implement the learning, or *which* time scales are involved.
- **Global workspace theory (Baars 1988; Dehaene 2014)** explains consciousness and attention in the 100-ms to seconds range. It does not explain action potentials, gene expression, or development.
- **Memory consolidation theory (Squire 1992; Buzsáki 1989)** explains how short-term becomes long-term memory. It does not explain perception or consciousness.
- **Bayesian brain (Knill & Pouget 2004; Friston 2010)** is a normative theory, not a mechanistic one. It says what the brain *should* compute, not what it *does* compute.
- **The Hodgkin-Huxley model (1952)** explains the action potential. It does not explain behavior.
- **Hebbian learning (1949) / STDP (Bi & Poo 1998)** explains synaptic plasticity. They do not explain systems-level behavior.

Each theory is correct within its domain. None unifies the rest.

### 2.3 The unification problem

The unification problem is to find a single mathematical framework that:

1. Reduces to predictive coding at the ms scale.
2. Reduces to free-energy minimization at the s scale.
3. Reduces to STDP at the min scale.
4. Reduces to systems consolidation at the day scale.
5. Reduces to experience-dependent plasticity at the yr scale.
6. Predicts measurable cross-scale interactions.

Such a framework would not be a competitor to existing theories. It would *contain* them as special cases. **MSPCH is the candidate**.

---

## 3. The Five Core Principles

MSPCH rests on five principles, each backed by decades of empirical work. None is original to this paper. Their *integration* is.

### 3.1 The brain is a hierarchical generative model

The brain has a generative model of the world. This model is *hierarchical*: sensory input is at the bottom, abstract causes at the top. Each level predicts the level below. Prediction errors propagate upward; predictions propagate downward.

- **Evidence**: predictive coding (Rao & Ballard 1999), canonical microcircuits (Bastos et al. 2012), extrastriate visual cortex responses (Heeger 2017), beta/gamma oscillations for top-down/bottom-up (Bastos 2012), and the anatomy of cortical feedback connections (Markov 2013, the macaque connectome).

- **Mathematical form**: a hierarchical latent variable model $p(x, z_1, z_2, \ldots, z_L) = p(x|z_1) p(z_1|z_2) \cdots p(z_L)$ with inference $q(z_l|x) \approx p(z_l|x)$ via amortized variational inference.

### 3.2 Inference is amortized

The brain does not solve inference from scratch each time. It *learns* to do inference quickly, via offline consolidation (sleep). The recognition network — the mapping from data to latent variables — is trained on replayed experiences.

- **Evidence**: systems consolidation during sleep (Wilson & McNaughton 1994; Rasch & Born 2013), sleep-dependent learning (Walker 2009), the existence of a fast recognition system (hippocampus) and a slow one (cortex) (Squire 1992; McClelland 1995).

- **Mathematical form**: the recognition network $q_\phi(z|x)$ is parameterized by $\phi$ (cortical weights). The inference step is a single forward pass, not an iterative optimization.

### 3.3 Learning is gated by neuromodulators

The brain's learning rate is not constant. It is set by neuromodulators: dopamine (DA), acetylcholine (ACh), norepinephrine (NE), serotonin (5-HT), orexin. Each has a specific role.

- **DA = reward prediction error**. Gates the consolidation of rewarded actions (Schultz 1997).
- **ACh = novelty**. Gates the encoding of new information vs. retrieval of old (Hasselmo 2006).
- **NE = arousal / uncertainty**. Sets the gain of cortical neurons (Aston-Jones & Cohen 2005).
- **5-HT = patience / exploration vs exploitation**. Sets the temporal discount factor (Doya 2002; Cools 2008).
- **Orexin = behavioral mode**. Switches between wake, sleep, and foraging (Sakurai 2007; Adamantidis 2010).

- **Evidence**: Brzosko et al. (2017), Frémaux & Gerstner (2016), Doya (2002), Yu & Dayan (2005), and a vast pharmacology and optogenetics literature.

- **Mathematical form**: the update rule becomes $\Delta W = \eta \cdot \text{DA} \cdot \text{error} \cdot \text{pre} \cdot \text{post}$, where $\eta$ is the base learning rate and DA is a context-dependent multiplier. This is the "three-factor learning rule" of Frémaux & Gerstner.

### 3.4 Memory is multi-system

The brain does not have a single memory. It has at least two: a *fast* system (hippocampus, one-shot binding) and a *slow* system (cortex, gradual integration). The fast system is overwritten quickly; the slow system is consolidated during sleep.

- **Evidence**: patient H.M. (Scoville & Milner 1957), the standard model of systems consolidation (Squire 1992; McClelland 1995), the existence of complementary learning systems (CLS; O'Reilly 2004), replay during sleep (Wilson & McNaughton 1994), and the standard model of memory consolidation (Frankland & Bontempi 2005).

- **Mathematical form**: a fast key-value store (the hippocampus) and a slow gradient-updated network (the cortex). The fast store is queried by similarity. The slow store is updated by replayed examples.

### 3.5 The system is homeostatically regulated

The brain maintains its operating point through a web of homeostatic mechanisms: synaptic scaling (Turrigiano 2008), glial regulation of extracellular environment (Allen & Lyons 2018), metabolic homeostasis (Attwell & Laughlin 2001), and arousal-state regulation (Saper 2005).

- **Evidence**: synaptic scaling in cortex (Turrigiano 1998), the role of glia in tripartite synapses (Araque 1999), metabolic cost of computation (Sengupta 2013), the sleep-wake cycle (Saper 2005).

- **Mathematical form**: an additional term in the loss function that penalizes deviations from a target activity level. The glial network implements this penalty in a slow (minutes-to-hours) time scale.

These five principles — hierarchical generative model, amortized inference, neuromodulator gating, multi-system memory, homeostatic regulation — are not novel. What is novel is the claim that they are *the same algorithm* running at all time scales.

---

## 4. The Multi-Scale Integration

The contribution of MSPCH is the integration. The same variational inference algorithm runs at every time scale, with the five principles instantiated differently at each scale.

### 4.1 The variational free energy

The mathematical skeleton is the variational free energy:

$$F = \mathbb{E}_{q(z|x)}[\log q(z|x) - \log p(x, z)]$$

Minimizing $F$ maximizes the evidence lower bound (ELBO) on $\log p(x)$. The brain is, on this hypothesis, a *physical system that minimizes variational free energy at every time scale*.

### 4.2 The ten scales

The free energy minimization can be implemented in different ways at different time scales. The following table is the heart of the hypothesis.

| Time scale | Phenomenon | Free energy term | Implementation | Reference |
|---|---|---|---|---|
| 1 ms | Channel gating | $\log p(x\|z)$ | Conformational dynamics | Hille 2001 |
| 10 ms | Action potential | $\log p(x\|z) - \log q(z)$ | HH dynamics | Hodgkin & Huxley 1952 |
| 100 ms | STDP | $F$ gradient w.r.t. $W$ | Ca²⁺-dependent plasticity | Bi & Poo 1998 |
| 1 s | Decision | $\log p(x\|z)$ posterior | Drift diffusion | Gold & Shadlen 2007 |
| 1 min | LTP | Slow $F$ gradient | CaMKII, AMPA traffic | Malenka & Bear 2004 |
| 1 hr | Synaptic consolidation | $F$ gradient gated by protein | BDNF, CREB | Kandel 2001 |
| 1 day | Systems consolidation | Replay updates slow network | Hippocampal-cortical | Squire 1992 |
| 1 month | Structural plasticity | Generative model update | Synaptogenesis | Holtmaat 2009 |
| 1 year | Map refinement | Prior re-estimation | Cortical reorganization | Merzenich 1988 |
| Lifetime | Development | Generative model selection | Apoptosis, neurogenesis | Rakic 1988 |

Each row is a *time slice* of the same algorithm. At the ms scale, the "latent variable" is the firing rate of a single neuron, and the "data" is the input current. At the day scale, the "latent variable" is a memory representation, and the "data" is a replayed episode. At the year scale, the "latent variable" is a cortical map, and the "data" is months of experience.

### 4.3 The cross-scale predictions

This integration makes specific predictions. The most striking:

**Prediction 1 (molecular-second coupling)**: blocking protein synthesis in PFC (with anisomycin) during a random-dot-motion decision task should *not only* disrupt long-term memory (known) but should *also* increase decision thresholds on a seconds time scale. The molecular cascade at the hour scale is causally upstream of the inference at the second scale.

**Prediction 2 (neuromodulator cross-talk)**: the same dopamine signal that gates plasticity in cortex (minute scale) should also modulate gain in PFC (ms scale). Perturbing one should perturb the other. This is testable with cell-type-specific optogenetics.

**Prediction 3 (sleep-decision coupling)**: sleep deprivation should impair both slow consolidation (day scale) and fast decision-making (s scale). The standard sleep-deprivation literature (e.g., Drummond 2000) reports decision deficits; the prediction is that the deficit is *causally* linked to the consolidation deficit, not just a side effect of fatigue.

**Prediction 4 (developmental plasticity inheritance)**: the cortical map structure present in adulthood should be predictable from the developmental program, in a way that depends on early neuromodulator levels. This is a long-timescale prediction, testable with longitudinal imaging.

Each prediction is *falsifiable*. Each distinguishes MSPCH from a single-scale theory.

### 4.4 Why this is the right unification

The unification is *natural* because the variational free energy is a *single scalar* that can be implemented at any time scale. The five principles are not five different things; they are five aspects of *the same* free-energy minimization. The hierarchy is the generative model. The amortization is the recognition network. The neuromodulators gate the optimization. The multi-system memory is the consolidation of fast and slow stores. The homeostasis is a regularization term.

A critic might object that the same equation at different time scales is a *coincidence*, not a *causation*. But the equation is not just a mathematical form. It is a constraint on physical implementation. A system that minimizes free energy *must* have hierarchical structure (to do inference efficiently), *must* have fast and slow stores (to handle different time scales), *must* have gain control (to manage precision), and *must* have homeostasis (to avoid the trivial solution of zero activity).

In other words, the *physics* of free-energy minimization forces the architecture. The brain is not an arbitrary system that happens to look like free-energy minimization. It is a system that *is* free-energy minimization, and the architecture is what such a system must look like in a noisy, embodied, energy-constrained substrate.

---

## 5. The Decisive Experiments

The hypothesis stands or falls on its predictions. Three experiments, in increasing order of difficulty, would test MSPCH.

### 5.1 Experiment 1: The molecular-decision coupling

**Hypothesis**: blocking protein synthesis in PFC during a decision task should increase decision thresholds.

**Subjects**: rats (n=20 per group), trained on a random-dot-motion (RDM) task.

**Groups**:
1. Saline control
2. Anisomycin (protein synthesis inhibitor) infused into PFC 30 min before task
3. Anisomycin infused into PFC 6 hours before task
4. Anisomycin infused into striatum (control region)

**Predictions**:
- Group 2 should show increased decision thresholds (longer RTs, lower accuracy) on the seconds time scale. This is the novel prediction.
- Group 3 should show *normal* decision thresholds but impaired next-day performance on a memory task.
- Group 4 should show motor deficits but normal decision thresholds.

**Why this tests MSPCH**: if the hour-scale molecular cascade is causally upstream of the second-scale inference, anisomycin should affect both. A single-scale theory predicts one or the other, not both. The cross-scale pattern is the signature.

### 5.2 Experiment 2: The neuromodulator cross-talk

**Hypothesis**: the same dopamine signal that gates cortical plasticity (minute scale) also modulates PFC gain (ms scale).

**Subjects**: mice (n=10 per group), with cell-type-specific D1/D2 dopamine receptor knockouts in PFC.

**Protocol**:
- Train mice on a Go/No-Go task with reward.
- Simultaneously record from PFC (electrophysiology) and measure VTA dopamine release (fiber photometry, dLight).
- Test how dopamine release modulates both the *learning rate* (across days) and the *trial-to-trial gain* (within session).

**Prediction**: D1-receptor knockout in PFC should impair *both* the day-scale learning and the second-scale gain. D2 knockout should have a different pattern (predicted to affect motivation but not gain).

**Why this tests MSPCH**: the same neuromodulator at two time scales is the MSPCH signature. Single-scale theories predict one or the other.

### 5.3 Experiment 3: The full MSPCH model of *Drosophila* larva

**Hypothesis**: a complete predictive-coding + three-factor-learning + replay-consolidation model of the *Drosophila* larval connectome (10,000 neurons, fully mapped, Janelia 2024) can learn a task the larva actually learns (e.g., olfactory conditioning).

**Subjects**: *in silico* *Drosophila* larva.

**Protocol**:
- Build a spiking network with the 10,000-neuron connectome.
- Implement: predictive coding at each layer, neuromodulator-gated STDP, replay-driven consolidation.
- Train the network on an associative learning task.
- Compare behavior to the real larva.

**Prediction**: if MSPCH is right, the network should reproduce the larva's learning curve, generalization pattern, and consolidation dynamics. If wrong, the network should fail in characteristic ways (e.g., catastrophic forgetting, no one-shot learning, no sleep-like consolidation).

**Why this tests MSPCH**: this is a closed-system test. Everything is known. If MSPCH works here, it is the most parsimonious explanation. If it fails, the hypothesis is wrong.

### 5.4 What would falsify MSPCH

The hypothesis is falsifiable. It is wrong if:

1. The molecular-decision experiment (5.1) shows no cross-scale effect. Protein synthesis in PFC does not affect second-scale decisions.
2. The neuromodulator cross-talk (5.2) shows that DA gates one scale but not the other. The cross-scale prediction is the signature.
3. The *Drosophila* model (5.3) cannot be built with the principles. Some component (e.g., replay consolidation) is not implementable on the real connectome.
4. A simpler, single-scale theory explains the same data. Falsification by parsimony, not by experiment.

A strong version of MSPCH would be supported by all three experiments. A weak version (e.g., "some cross-scale interactions exist") would be supported by one.

---

## 6. The AI Instantiation

If MSPCH is right, then a brain-like AI should have five core systems. The curriculum in `docs/nature/12_unification/prototype.py` instantiates them.

### 6.1 The five systems

1. **Multi-system memory**: a fast key-value store (hippocampus) and a slow gradient-updated network (cortex). The fast store handles one-shot binding. The slow store generalizes.

2. **Neuromodulation**: five signals (DA, ACh, NE, 5-HT, Orexin) that gate learning rate, gain, mode, exploration, and behavioral state.

3. **Replay-driven consolidation**: an offline loop that distills episodic memories from fast to slow memory. This is the "sleep" step.

4. **Homeostatic regulation**: activity-dependent scaling of weights to maintain a target firing rate. Disabled by default in the prototype because of interaction with random feature extraction; enabled in `prototype_colab.py` with proper supervised anchoring.

5. **Intrinsic motivation**: prediction error as intrinsic reward. Drives exploration in low-data regimes.

### 6.2 The predicted properties

A complete MSPCH AI would have these properties (none of which current AI has):

| Property | MSPCH AI | Current AI |
|---|---|---|
| Sample efficiency | 1-shot learning | Thousands of examples |
| Continual learning | Yes (multi-system) | Catastrophic forgetting |
| Energy efficiency | ~20W | ~MW |
| Intrinsic motivation | Yes | No |
| Embodied | Yes | No (in general) |
| Sleep-like consolidation | Yes | No |
| Glial-like homeostasis | Yes | Partial (batch norm) |

The MSPCH AI is not necessarily better than a transformer on ImageNet. It is *different*. It is designed for the regime where brains excel: few examples, continual learning, embodied interaction, energy-constrained deployment.

### 6.3 The benchmark

The benchmark for a brain-like AI is not ImageNet. It is Omniglot (one-shot learning), Atari with continual learning (no catastrophic forgetting), and a robot in a novel environment (transfer). On these benchmarks, MSPCH-style architectures should outperform transformers, especially in the low-data regime.

---

## 7. Implications

If MSPCH is right, several fields are reshaped.

### 7.1 Neuroscience

The field has been dominated by single-scale theories. MSPCH provides a *single framework* that links all scales. The implication is that experiments should be designed to test *cross-scale* interactions, not just within-scale phenomena. The molecular-decision experiment (5.1) is a template.

### 7.2 AI

The 50,000x energy gap between brains and transformers is not a hardware problem. It is a *computational principle* problem. The brain is efficient because it implements a fundamentally different algorithm — sparse, event-driven, neuromodulated, amortized through sleep. A new generation of AI hardware and algorithms should target these principles.

The first AI system to win a low-data, continual-learning, energy-constrained benchmark using MSPCH principles will be a major step. The first AI system that is *conscious* (by some operational definition) using these principles would be transformative.

### 7.3 Medicine

Disorders of the brain are disorders of the algorithm. Alzheimer's is a disorder of consolidation (hour scale). Parkinson's is a disorder of gating (DA, second scale). Schizophrenia is a disorder of inference (ms scale). Each is a specific MSPCH component failure.

A unified theory lets us design interventions that target specific time scales. Protein synthesis inhibitors (currently used in some research) for memory disorders. Neuromodulator drugs for decision disorders. Sleep therapies for consolidation disorders.

### 7.4 Philosophy

The hard problem of consciousness is not solved by MSPCH. But it is *reframed*. If MSPCH is right, consciousness is identical to a specific kind of computation — variational inference with the five principles. The hard problem becomes: why does *this* kind of computation feel like something?

This is still a hard problem. But it is a *concrete* hard problem. It is the question: what is the *intrinsic nature* of variational inference? Is there anything it is like to be a variational inference machine? IIT (Tononi 2004) and GWT (Baars 1988) give operational definitions. MSPCH gives a substrate.

The philosophical payoff is that the question is now *answerable in principle*. We can build a system that does MSPCH-style computation. We can ask whether it is conscious. The answer is empirical.

---

## 8. Limitations and Open Questions

MSPCH is a hypothesis, not a theorem. It has limitations.

1. **The "same algorithm" claim is loose.** Variational inference at the ms scale (action potentials) and at the year scale (cortical map refinement) share the same *form* but not the same *mechanism*. The unification is mathematical, not physical. A skeptic can reasonably say this is just a *similarity* in form, not a *causal* link.

2. **The neuromodulator assignment is incomplete.** DA, ACh, NE, 5-HT, Orexin have well-defined roles, but the *mapping* from theory to molecule is not unique. Different computational roles could be implemented by different molecular substrates.

3. **The homeostatic story is sketchy.** Turrigiano-style synaptic scaling is one mechanism, but the brain has dozens of homeostatic mechanisms (intrinsic excitability, glial regulation, metabolic feedback, sleep-wake cycles). MSPCH picks one as illustrative.

4. **The consciousness claims are speculative.** Saying "consciousness is variational inference" is a *reformulation*, not a *solution*. The hard problem remains.

5. **The AI instantiation is small.** The 200-line NumPy prototype is a *demonstration*, not an SOTA system. A serious test requires the PyTorch version (`prototype_colab.py`) and a proper benchmark.

These limitations are honest. The hypothesis is meant to be tested, not defended. The most useful next step is experiment 5.1 (the molecular-decision coupling), because it is doable in a year and would distinguish MSPCH from single-scale theories.

---

## 9. Conclusion

The Multi-Scale Predictive Coding Hypothesis is a single claim: **the brain implements variational inference at every time scale, with neuromodulators setting parameters and molecular cascades implementing each scale**.

The claim is original in its integration. It is supported by the convergence of evidence from predictive coding, free energy principle, memory consolidation, neuromodulation, and homeostatic plasticity. It is falsifiable by specific experiments. It implies a specific architecture for brain-like AI.

If MSPCH is right, it unifies neuroscience from ion channels to consciousness. It gives AI a path past transformers. It reframes the hard problem of consciousness. It identifies specific targets for medicine.

If MSPCH is wrong, it is at least a useful *framework* for thinking about cross-scale interactions — a hypothesis that, even in its failure, would have generated valuable experiments.

Either way, MSPCH is a thesis that can be evaluated. The next step is not more theorizing. It is the molecular-decision experiment (5.1) in a behaving animal. If the prediction holds, the field has a unifying theory. If it fails, the field has a sharper question.

The science begins with the experiment, not the theory. But without a theory, the experiment is impossible. MSPCH is the theory that makes the experiment possible.

---

## Acknowledgments

This paper synthesizes 11 parts of the `nature/` curriculum in `ai-miden/`, which in turn synthesizes a century of neuroscience. Specific intellectual debts: David Marr (1982) for the levels-of-analysis framework; Karl Friston (2010) for the free energy principle; Dana Ballard, Rajesh Rao (1999) for predictive coding; Francis Crick and Christof Koch (1990, 2003) for consciousness; Gilles Laurent, Mark Goldman, and other systems neuroscientists whose work underlies the multi-scale framing; and the open-source AI community (PyTorch, NumPy, Brian) without which the prototype would not exist.

## References

See `../BIBLIOGRAPHY.md` for the complete bibliography. The most relevant entries for MSPCH are: Rao & Ballard 1999; Friston 2010; Bastos et al. 2012; Schultz 1997; Brzosko et al. 2017; Squire 1992; Turrigiano 1998; Bading 2013; Kandel 2001; Buzsáki 2015; Tononi 2004; Baars 1988; Dehaene 2014; Millidge et al. 2022; Whittington & Bogacz 2019.

## Code

- `prototype.py` — 200-line NumPy implementation of MSPCH-Net with the five systems.
- `prototype_colab.py` — PyTorch + CUDA version for training-heavy experiments.
- `experiment_design.md` — detailed protocol for the molecular-decision experiment.

## How to test this paper

1. Run `python docs/nature/12_unification/prototype.py`. Verify the 5 systems run.
2. Read `experiment_design.md`. Find a collaborator with a behaving-animal lab. Run the experiment.
3. Submit the result (positive or negative) to *Neuron* or *Nature Neuroscience*.

The worst outcome is "we tested it, it failed, we learned something." The best outcome is "we tested it, it worked, the field has a unifying theory." Either is publishable.

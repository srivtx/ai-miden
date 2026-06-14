# Experiment Design: The Molecular-Decision Coupling

> A decisive experiment to test the Multi-Scale Predictive Coding Hypothesis (MSPCH). If the prediction holds, MSPCH is the leading unifying theory of cortical computation. If it fails, MSPCH is wrong and the field needs a different unification.

---

## The hypothesis (one sentence)

**Blocking protein synthesis in PFC during a decision task should disrupt decision-making on a seconds time scale — even on trials that don't depend on long-term memory.**

This is the molecular-decision coupling: the hour-scale molecular cascade is causally upstream of the second-scale inference.

---

## Background

### Standard single-scale theory

Standard theories treat different time scales as independent:
- **Predictive coding** (Rao & Ballard 1999) explains the ms scale.
- **Memory consolidation** (Squire 1992) explains the hour-day scale.

These theories predict: blocking protein synthesis disrupts long-term memory (known, easy to show) but does *not* disrupt decision-making on a single trial. Each scale is a separate system.

### MSPCH prediction

MSPCH predicts: blocking protein synthesis in PFC disrupts *both* the hour-scale consolidation *and* the second-scale inference. The molecular cascade is one mechanism serving multiple time scales, not separate mechanisms.

### The signature

The signature is **cross-scale coupling under molecular perturbation**. If perturbing protein synthesis affects only long-term memory, single-scale theories are right. If it affects both, MSPCH is right.

---

## The experiment

### Subjects

- **Rats**, n=20 per group, adult male Long-Evans (or equivalent).
- Pre-screened for good visual performance and motivation.
- Random assignment to groups.

### Apparatus

- Standard operant chambers with two nose-pokes and a central stimulus display.
- Random-dot-motion (RDM) task: the stimulus is a field of dots moving coherently in a random direction; the rat must indicate the direction with a left or right nose-poke for reward.
- The coherent motion strength is varied (0% to 50%) to titrate difficulty.
- A cannula is implanted in the medial PFC (prelimbic region, AP +3.2, ML ±0.6, DV -3.0).
- A second cannula is implanted in the dorsal striatum (control region).

### Groups

1. **Saline + PFC** (n=10). Saline infused 30 min before RDM task.
2. **Anisomycin + PFC** (n=10). Anisomycin (62.5 μg/side, 1 μL) infused 30 min before RDM task.
3. **Anisomycin + Striatum** (n=10). Same dose, striatal infusion.
4. **Anisomycin + PFC, 6 hr delay** (n=10). Anisomycin infused 6 hours before RDM task. Protein synthesis is restored by the time of testing (t½ ~ 2 hr in vivo).

### Protocol

**Day 1-7**: Pre-training. Rats learn the basic RDM task to criterion (≥80% on 25% coherence).

**Day 8**: Infusion. 30 min after infusion, run the RDM task for 1 hour (300 trials).
- Measure: choice accuracy, reaction time, decision threshold (drift diffusion model fit), and psychometric curve.

**Day 9-10**: Recovery. No infusion. Run RDM task on Day 10 to test for residual effects.

**Day 11-14**: Memory probe. Train rats on a new context-fear conditioning task on Day 11. Test memory on Day 14. (Tests long-term memory consolidation, the known effect of anisomycin.)

### Predictions

**Single-scale theory** predicts:
- Group 2 (Aniso + PFC) should have *normal* Day 8 RDM performance.
- Group 2 should have *impaired* Day 14 memory (the known effect).

**MSPCH** predicts:
- Group 2 (Aniso + PFC) should have *impaired* Day 8 RDM performance: longer RTs, higher thresholds, flatter psychometric curves.
- Group 2 should also have *impaired* Day 14 memory.
- Group 3 (Aniso + Striatum) should have *motor* deficits (slowness, hesitation) but *normal* decision accuracy.
- Group 4 (Aniso + PFC, 6 hr delay) should have *normal* Day 8 RDM performance but *impaired* Day 14 memory. (Because the protein synthesis is restored by the time of testing.)

### The decisive statistic

The key comparison is Group 2 vs Group 1 on Day 8. The primary outcome is the **decision threshold** (drift diffusion model parameter $z$, the bound height) or, equivalently, the **psychometric curve slope**.

- If threshold is *significantly higher* in Group 2 (more evidence required, slower RTs, lower accuracy at low coherence) → MSPCH supported.
- If threshold is *unchanged* in Group 2 → MSPCH falsified.

A power analysis for a 2-sample t-test on the threshold parameter, assuming effect size d=0.8 and α=0.05, gives n=20 per group for 80% power. This is achievable.

---

## What this experiment does

This is a *direct test* of the cross-scale prediction. It is *not* a test of predictive coding, free energy, or any other single-scale theory. It is a test of the *integration*.

The experiment is also tractable:
- The technique (intracranial anisomycin + RDM task) is standard in systems neuroscience.
- The animal model (rat PFC) is well-characterized.
- The behavioral readout (decision threshold) is well-validated.
- The expected effect (impairment) is in the right direction, so no need for an exotic effect size.

Estimated cost: $200,000–$300,000 USD (1 PhD student, 2 years, animal and supply costs).

Estimated duration: 18-24 months from start to submission.

---

## Variants and follow-ups

If the experiment is positive, the natural follow-ups are:

1. **Dose-response**: does the threshold impairment scale with anisomycin dose?
2. **Time course**: when is the effect maximal? Hours? Days?
3. **Cell-type specificity**: is the effect driven by excitatory pyramidal neurons or inhibitory interneurons? (Use cell-type-specific DREADDs or chemogenetics.)
4. **Receptor-specific**: does the effect require NMDA receptor activation, mGluR, or other signaling pathways? (Use receptor antagonists.)
5. **Cross-region**: does the same effect occur in motor cortex? Posterior parietal cortex? Hippocampus?

If the experiment is negative, the natural follow-ups are:

1. **Task variant**: does the effect appear in a more demanding decision task?
2. **Timing**: does the effect require anisomycin *during* the task, or only *before*?
3. **Species**: is the effect rat-specific? (Try mice, or non-human primates.)
4. **MSPCH revision**: what part of the hypothesis was wrong? Was the hour-scale molecule wrong? Was the second-scale inference wrong? Was the cross-scale coupling wrong?

---

## What if MSPCH is right but the experiment is inconclusive?

A null result does not falsify MSPCH. It could be that:
- The dose was too low.
- The PFC region was wrong.
- The task was too easy.
- The time window was wrong.
- The anisomycin had off-target effects that masked the prediction.

A null result in *this* experiment should be followed by **Experiment 2: The neuromodulator cross-talk** (described in `MSPCH.md` section 5.2). That experiment tests the same prediction via a different pathway: dopamine. If *both* experiments are negative, MSPCH is in serious trouble.

---

## What this experiment is *not*

This is not a test of:
- Whether predictive coding is right.
- Whether the brain is Bayesian.
- Whether the free energy principle is right.
- Whether consciousness is integrated information.
- Whether transformers are good AI.

It is a test of one specific claim: that the molecular cascade at the hour scale is causally upstream of the inference at the second scale. The claim is novel to MSPCH.

---

## Publication plan

If positive: submit to *Neuron* or *Nature Neuroscience*. The paper would be titled "Molecular cascades in PFC support decision-making across multiple time scales" or similar. Estimated impact: high (single paper establishing a new principle).

If negative: submit to *eLife* or *Journal of Neuroscience*. The paper would be titled "Failure to find cross-scale coupling between protein synthesis and decision-making in rat PFC" or similar. Estimated impact: moderate (replication of negative finding, useful constraint on theory).

Either way, the result is publishable. The field is data-starved on this question.

---

## Code and reagents

- Anisomycin: Tocris #1568. Standard dose 62.5 μg/side in 1 μL saline.
- Cannulae: Plastics One, 26-gauge guide, 33-gauge injector.
- RDM task: open-source code in `ai-miden/docs/nature/12_unification/prototype_colab.py` (the Colab script generates RDM stimuli).
- Drift diffusion model fit: HDDM (Wiecki 2013), Python package.

## How to find a collaborator

The experiment requires a systems neuroscience lab with:
- Intracranial surgery capability in rats.
- Behavior apparatus (operant chambers).
- Experience with RDM tasks or similar perceptual decisions.

Labs that have published similar work: Gold, Shadlen, Brody, Wang, Jancke, Britten, Salzman, Drugowitsch. Many would be interested in a 2-year collaboration with a theory group.

A theory lab (with a strong publication in predictive coding, free energy, or related) can supply the hypothesis, the experimental design, and the analysis plan. A behavior lab supplies the surgery, training, and recording.

## Conclusion

This is the simplest decisive experiment I can think of to test MSPCH. It costs $200K and 2 years. It has a clear positive prediction. It would distinguish MSPCH from single-scale theories. The result is publishable either way.

If you are a graduate student with access to a behavior lab, this is the experiment to run.

If you are a PI looking for a high-impact 2-year project, this is the project.

If you are a funder looking for leverage, this is the proposal.

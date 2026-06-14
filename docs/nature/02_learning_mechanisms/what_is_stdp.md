# What Is Spike-Timing-Dependent Plasticity (STDP)?

**The Problem:** LTP and LTD tell you *whether* a synapse strengthens or weakens based on how much pre and post fire. But the brain has access to much richer information: the *precise timing* of spikes, on the millisecond scale. A 1998 experiment showed that timing alone — not just rate — determines the sign of plasticity. This opened a new field: spike-timing-dependent plasticity.

**Definition:** *Spike-timing-dependent plasticity (STDP)* is a form of Hebbian learning where the sign and magnitude of synaptic change depend on the *relative timing* of pre- and postsynaptic spikes. Pre-before-post (within ~20 ms) → LTP. Post-before-pre → LTD. STDP is the temporal refinement of Hebbian learning.

**How It Works (Step-by-Step):**

1. **The experiment.** Bi & Poo (1998) cultured hippocampal neurons and used paired whole-cell recordings. They delivered single spikes to the pre- and postsynaptic neurons at varying time offsets (Δt = t_post - t_pre, ranging from -100 ms to +100 ms). They measured the change in synaptic strength.

2. **The result — the STDP learning window.** A stereotyped curve:
   - If pre fires 10-20 ms **before** post (Δt > 0): strong LTP
   - If pre fires 10-20 ms **after** post (Δt < 0): strong LTD
   - The curve decays exponentially with |Δt|, with time constants τ+ ≈ 17 ms (LTP side) and τ- ≈ 34 ms (LTD side)

3. **The mathematical form:**
   - Δw = A_+ · exp(-Δt/τ_+) if Δt > 0 (LTP)
   - Δw = -A_- · exp(Δt/τ_-) if Δt < 0 (LTD)
   - A_+ and A_- are learning rates; τ_+ and τ_- are time constants

4. **The molecular mechanism — why it works.** STDP requires:
   - **Pre fires before post:** Glutamate binds NMDA, then post fires (back-propagating action potential), depolarizing the spine and expelling the Mg²⁺ block. Ca²⁺ enters. *High Ca²⁺ → LTP*.
   - **Post fires before pre:** Postsynaptic spike happens first. The back-propagating AP arrives before glutamate. The NMDA channel is not yet fully open when the AP arrives. *Moderate Ca²⁺ → LTD*.

5. **Direction of information flow.** STDP is asymmetric. It strengthens synapses in the *forward* direction of information flow. This is the basis of *causal* learning: synapses that *cause* a postsynaptic spike get stronger; synapses that *follow* a postsynaptic spike get weaker.

6. **Variants.** Not all synapses show the canonical STDP curve:
   - **Anti-Hebbian STDP** (in some inhibitory synapses): the curve is flipped.
   - **Symmetric STDP**: LTP for both directions.
   - **Triplet and quadruplet STDP**: depends on spike triplets, not just pairs. More biologically accurate.
   - **Frequency-dependent STDP**: timing matters, but only at certain firing rates.

7. **STDP and predictive coding.** A presynaptic neuron that *consistently fires before* a postsynaptic neuron is a *predictor* of that neuron's firing. STDP naturally wires the brain to strengthen predictive connections. This is one mechanism by which the brain learns causal structure.

8. **STDP in different brain regions:**
   - **Hippocampus:** Canonical STDP, but compressed in time by theta oscillations (4-8 Hz). The "phase precession" of place cells means that temporally-distributed events can be associated within a single theta cycle (~100-150 ms).
   - **Visual cortex:** STDP underlies the development of orientation selectivity and ocular dominance.
   - **Cerebellum:** A different timing rule, with LTD dominating for parallel fiber → Purkinje cell synapses when the climbing fiber fires concurrently.

9. **Critical period plasticity.** STDP is particularly active during *critical periods* of development, when circuits are being refined. In the rodent barrel cortex, before P15, STDP is "all-to-potentiation" (any coincidence strengthens). After P15, the canonical bidirectional STDP emerges as inhibition matures.

**Real-life analogy:** A tennis coach observing two players. If player A's serve consistently *precedes* player B's winning return, the coach strengthens A's serving arm. If A's serve *follows* B's win, no causal relationship is implied — the coach may even weaken A. STDP is the brain's "causal coach," strengthening only those inputs that *predict* the output.

**Tiny numeric example:** Two connected neurons fire 100 spikes each. If the pre-post delay is consistently 10 ms, ~50% of pairs are within the LTP window (since ~50% of pre spikes happen within 20 ms of a post spike). After 100 pairs, the synapse is ~2x stronger. If the timing is reversed (post-before-pre by 10 ms), the synapse is ~2x weaker. The asymmetry: pre-before-post strengthening is slightly stronger (A_+ ≈ A_-) than post-before-pre weakening, which keeps the synapse from collapsing entirely.

**Common confusion:**

- No. "STDP is a refinement of backprop." The opposite — STDP is a refinement of Hebbian learning. Backprop is a global gradient method. STDP is local.
- No. "STDP requires millisecond precision in biology." Yes — biology operates on millisecond timescales for spikes. The brain does not have nanosecond clocks.
- No. "STDP is universal." No. Some synapses are rate-based. Some are timing-based. Some are mixed. Some are modulatory.
- No. "STDP only strengthens forward connections." That's the canonical case. But there are synapses with anti-Hebbian STDP, including some inhibitory synapses.
- No. "Pairing is enough to induce STDP." Almost. You also need postsynaptic depolarization (back-propagating action potential) for the NMDA receptor to be unblocked. Just pairing is not sufficient.
- No. "STDP implements backprop." A common oversimplification. Some papers (e.g., Bengio et al., 2017) show STDP-like rules can implement a form of feedback alignment, which is a poor man's backprop. But STDP alone is not equivalent to backprop — it can be a building block, not a replacement.

**Key properties:**

- **Locality:** Δw depends only on pre and post spikes at this synapse.
- **Causal:** Strengthens only inputs that *predict* the postsynaptic output.
- **Asymmetric:** The LTP and LTD windows are different (τ+ ≠ τ-, A_+ ≠ A_-).
- **Multi-spike:** Real STDP depends on triplets and quadruplets, not just pairs (Pfister & Gerstner, 2006).
- **Modifiable:** Neuromodulators (DA, ACh, NE) can change the STDP curve, even reversing the sign of plasticity.
- **Frequency-dependent:** STDP behavior depends on firing rate.

**Where it appears in technology:**

- **Spiking neural networks (SNNs)** use STDP as a learning rule. This is the dominant paradigm in neuromorphic computing. Intel's Loihi chip uses STDP.
- **Feedback alignment** (Lillicrap et al., 2014) shows that you don't need symmetric weights for backprop-like learning — random feedback works. STDP can implement feedback alignment.
- **Predictive coding networks** (Rao & Ballard, 1999; Whittington & Bogacz, 2019) are mathematically related to STDP. A 2019 paper by Millidge, Salvatori et al. shows predictive coding networks trained by a local Hebbian-style rule can match backprop on standard benchmarks.
- **Tempotron** and **chronotron** are spiking neuron models trained with STDP-like rules for classification.
- **Contrastive Hebbian learning** uses a STDP-like rule to train continuous networks.

**Connection to next file:** STDP is a *two-factor* learning rule: pre and post spike times. But the brain also has a *third factor* — neuromodulators — that can gate plasticity. The next file (`what_is_three_factor_learning.md`) explains how dopamine, acetylcholine, and others turn plasticity on and off based on reward, attention, and behavioral state.

# What Are Neurotransmitters and Receptors?

**The Problem:** A neuron has ~5,000 synaptic inputs. Each input uses a different chemical. Each chemical means a different thing. The brain has to "decode" dozens of signals at once, in real time, using only molecules. How does it work?

**Definition:** *Neurotransmitters* are small chemical messengers released from the presynaptic terminal. *Receptors* are proteins on the postsynaptic membrane that bind them and trigger a response. Together, they are the "vocabulary" the brain uses to communicate.

**How It Works (Step-by-Step):**

1. **Synthesis.** Neurotransmitters are made in the presynaptic terminal (or in the cell body and shipped down). For glutamate: glucose → α-ketoglutarate → glutamate. For dopamine: tyrosine → L-DOPA → dopamine. For GABA: glutamate → GABA (via decarboxylation).
2. **Packaging.** Vesicular transporters (proton pumps + vesicular transporters) load neurotransmitters into vesicles against their concentration gradient. Each vesicle holds 1,000-10,000 molecules.
3. **Release.** Ca²⁺ influx triggers vesicle fusion (see `what_is_the_synapse.md`).
4. **Receptor binding.** Molecules diffuse across the cleft and bind to specific receptors. The *affinity* (binding strength) and *specificity* (which molecules bind) determine the response.
5. **Ionotropic receptors:** Bind and open an ion channel directly. Fast (~1 ms). Examples: AMPA, NMDA, kainate (all for glutamate); GABA-A; nicotinic ACh receptor; glycine receptor.
6. **Metabotropic receptors:** Bind and trigger a G-protein cascade that opens channels or alters metabolism indirectly. Slow (~100 ms to seconds) but long-lasting. Examples: muscarinic ACh receptors; dopamine D1/D2; serotonin 5-HT; all adrenergic receptors; metabotropic glutamate receptors.
7. **Termination.** Neurotransmitter is removed by:
   - **Reuptake** (transporters pump it back into the presynaptic cell) — target of SSRIs, cocaine, amphetamines
   - **Enzymatic degradation** — acetylcholinesterase cleaves ACh; target of nerve agents
   - **Diffusion** away from the cleft
8. **Receptor trafficking.** Receptors are not static. They are constantly inserted and removed from the membrane. Synaptic strength is largely controlled by how many receptors are in the postsynaptic density.

**The major neurotransmitters (the "alphabet"):**

| Neurotransmitter | Type | Main receptors | Function | Tech analog |
|---|---|---|---|---|
| **Glutamate** | Excitatory (ionotropic) | AMPA, NMDA, kainate, mGluR | Main "go" signal in brain | Default activation function |
| **GABA** | Inhibitory (ionotropic + metabotropic) | GABA-A (ionotropic), GABA-B (metabotropic) | Main "stop" signal | Negative weight |
| **Acetylcholine** | Mixed | Nicotinic (ionotropic), Muscarinic (metabotropic) | Attention, learning, muscle | Modulator signal |
| **Dopamine** | Modulatory | D1-D5 (all metabotropic) | Reward, motivation, movement | Reward signal (RL) |
| **Serotonin** | Modulatory | 5-HT1-7 (all metabotropic) | Mood, sleep, appetite | Mood/tone controller |
| **Norepinephrine** | Modulatory | α, β adrenergic (all metabotropic) | Arousal, alertness | Wake-up signal |
| **Histamine** | Modulatory | H1-H4 (metabotropic) | Wakefulness, appetite | Sleep-wake switch |
| **Glycine** | Inhibitory (ionotropic) | Glycine receptor | Spinal cord inhibition, NMDA co-agonist | Local inhibition |

**Real-life analogy:** Neurotransmitters are like coins. Each has a different value. Receptors are vending machines that accept specific coins. Putting in a glutamate coin (into AMPA receptor) gets you a small "go" response. Putting in a GABA coin gets you a "stop" response. Putting in a dopamine coin into a D1 receptor gets you a "this was good, remember it" signal. The neuron sums all the coin values from all the machines in real time.

**Tiny numeric example:** A single AMPA receptor conducts ~8 pA of current when open. A single synaptic event opens ~10-50 AMPA receptors. The resulting EPSC (excitatory postsynaptic current) is ~100-400 pA lasting ~1-2 ms. A typical neuron has ~5,000-10,000 glutamatergic synapses. At any moment, ~1-10% are active. So ~50-1000 receptors are open at once, producing ~1-5 nA of excitatory current. This is integrated over time and space by the dendrite to produce the final voltage at the soma.

**Common confusion:**

- No. "Excitatory = good, inhibitory = bad." No. Both are essential. Without inhibition, you have seizures. Without excitation, you have coma. Most psychiatric and neurological disorders involve *imbalances* in excitation and inhibition.
- No. "Dopamine is the 'pleasure' chemical." No. Dopamine is the *reward prediction error* signal (Schultz, 1998). It says "this was *better* than expected," not "this felt good." You can have pleasure without dopamine (e.g., from opiates) and dopamine without pleasure.
- No. "Serotonin is the 'happiness' chemical." No. Serotonin is involved in mood, sleep, appetite, and many other things. SSRIs take weeks to work, suggesting the "low serotonin → depression" story is incomplete.
- No. "Neurotransmitters only affect the next neuron." Most neurotransmitters also act on *the same neuron that released them* (autoreceptors) — providing feedback control.
- No. "One neurotransmitter = one function." No. The same neurotransmitter can do opposite things in different brain regions. Dopamine in the prefrontal cortex is about working memory; in the basal ganglia it's about movement; in the nucleus accumbens it's about reward.
- No. "Drugs that affect one neurotransmitter are 'targeted'." Most psychoactive drugs affect multiple systems. Caffeine blocks adenosine receptors. LSD acts on serotonin 5-HT2A receptors but also dopamine. Magic mushrooms (psilocybin) primarily act on 5-HT2A.

**Key properties:**

- **Specificity of receptors:** Glutamate doesn't bind GABA receptors. The brain can run two independent channels of communication in the same cleft.
- **Two timescales:** Fast ionotropic (ms) for fast signaling. Slow metabotropic (100 ms - minutes) for modulation.
- **Volume transmission:** Some neurotransmitters (dopamine, serotonin, neuropeptides) escape the synapse and act on distant receptors. The brain broadcasts as well as talks.
- **Receptor saturation:** Increasing neurotransmitter release has diminishing returns. The bottleneck is usually receptor availability, not transmitter amount.
- **Receptor desensitization:** Continued exposure inactivates receptors. This is a form of *automatic gain control*.

**Where it appears in technology:**

- **Glutamate / AMPA / NMDA** is the closest biological analog of a ReLU activation. It's an excitatory "yes, fire" signal with saturation.
- **GABA** is a negative weight — but it's the *only* negative weight, and it gates everything.
- **Dopamine** is a reward signal in *reinforcement learning* (the TD error in temporal-difference learning is mathematically identical to the dopamine reward prediction error — Schultz, Dayan & Montague, 1997).
- **Neuromodulators** (DA, 5-HT, ACh, NE) act as a *control plane* over the main "data plane" of fast synaptic transmission. Modern software uses the same idea (control plane vs. data plane) but with software-defined networking.
- **Drugs** are the most direct technology link: SSRIs (serotonin reuptake), antipsychotics (dopamine D2 antagonists), anesthetics (GABA agonists), stimulants (dopamine/norepinephrine reuptake inhibitors), psychedelics (5-HT2A agonists). All of these are essentially editing the brain's chemistry.

**Why this matters for the rest:** You cannot understand learning, memory, emotion, perception, or consciousness without understanding the chemistry. The "weights" in deep learning are a single number. The "weights" in the brain are a *constellation of receptor types, neuromodulator levels, second-messenger cascades, and gene expression changes*. When we say a synapse is "plastic," we mean all of these can change.

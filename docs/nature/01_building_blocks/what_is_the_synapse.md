# What Is the Synapse?

**The Problem:** Two neurons do not touch. There is a 20–40 nanometer gap between them. An action potential is electrical. How does an electrical signal in neuron A cause an electrical signal in neuron B — without any wires connecting them?

**Definition:** A *synapse* is the junction where one neuron's axon terminal communicates with another neuron's dendrite. There are two types: *electrical synapses* (direct ion flow through gap junctions) and *chemical synapses* (neurotransmitter release across a cleft). The brain uses chemical synapses for almost all learning-relevant communication.

**How It Works (Step-by-Step):**

1. **The presynaptic terminal.** The axon ends in a *bouton* (a small bulb). Inside the bouton are ~100-200 small spherical sacs called *synaptic vesicles*, each ~40 nm in diameter, filled with 1,000-10,000 neurotransmitter molecules.
2. **The synaptic cleft.** A 20-40 nm gap between the bouton and the postsynaptic neuron's *dendritic spine*. No wires. Just salty water.
3. **Action potential arrives.** Voltage-gated Ca²⁺ channels in the bouton open. Ca²⁺ rushes in (its concentration outside is 10,000× higher than inside).
4. **Vesicle fusion.** Ca²⁺ binds to *synaptotagmin* on vesicles. This triggers SNARE proteins to zip the vesicle membrane to the cell membrane, dumping the vesicle's contents into the cleft. The whole process takes <1 ms.
5. **Diffusion across the cleft.** Neurotransmitter molecules cross the 30 nm gap in ~0.1 ms.
6. **Receptor binding.** The molecules bind to specific receptor proteins on the postsynaptic spine. Receptors are either *ionotropic* (open an ion channel directly) or *metabotropic* (trigger a chemical cascade).
7. **Postsynaptic potential.** If the receptor is excitatory (e.g., AMPA receptor for glutamate), Na⁺ flows in and the postsynaptic voltage rises ~0.1-1 mV. If inhibitory (e.g., GABA-A receptor for GABA), Cl⁻ flows in and the voltage falls.
8. **Termination.** Neurotransmitter is cleared in milliseconds: by *reuptake* into the presynaptic cell, by *enzymatic degradation*, or by *diffusion*. SSRIs (antidepressants) block reuptake of serotonin. Nerve agents block acetylcholinesterase.
9. **Vesicle recycling.** The empty vesicle membrane is retrieved by *endocytosis* and refilled. This whole cycle takes ~1 minute. Some synapses use "kiss-and-run" recycling (~1 second) for fast reuse.

**Real-life analogy:** A chemical synapse is like two people shouting across a canyon. The presynaptic cell shouts (releases neurotransmitter). The postsynaptic cell has a wall of ears tuned to specific words (receptors). Most of the message is lost to the wind (diffusion and reuptake). The speed is set by the time it takes for sound to cross. An electrical synapse, by contrast, is like two rooms connected by a hole in the wall — instant, but no volume control.

**Tiny numeric example:** A single synaptic bouton has ~200 vesicles. Each vesicle has ~5,000 glutamate molecules. A single action potential releases ~1-10 vesicles (probabilistic). The cleft is ~30 nm wide. Diffusion of glutamate across takes ~0.1 ms. A typical excitatory postsynaptic potential (EPSP) is ~0.5 mV. The postsynaptic neuron needs ~30-50 of these EPSPs within a few ms to reach threshold. There are ~10¹⁵ synapses in the human brain. Each can release ~1 vesicle per second under low activity, or ~100/s under high activity. Total: ~10¹⁵ to 10¹⁷ vesicle fusions per second across the brain.

**Common confusion:**

- No. "Synapses are just wires." They are *chemical* junctions. They are slow (1-5 ms delay), unreliable (release probability is ~0.1-0.5), and modifiable. This is why they are the *site of learning*, not just transmission.
- No. "More neurotransmitter = stronger signal." Only up to a point. Receptors saturate. The signal is graded, not digital. And *the strength of the synapse is determined by the number and type of receptors*, not the amount of neurotransmitter released.
- No. "Neurotransmitters are proteins." They are mostly *small molecules*: glutamate, GABA, glycine, acetylcholine, dopamine, serotonin, norepinephrine, histamine. Peptides (like substance P) are also released, but they act more slowly as *neuromodulators*.
- No. "One neuron releases one neurotransmitter." Dale's principle (modified): a neuron releases the *same set* of transmitters at all its synapses. But it can release multiple transmitters (co-transmitters). A typical cortical pyramidal cell releases glutamate plus a peptide like somatostatin.
- No. "Synapses are stable." They are highly dynamic. They form, strengthen, weaken, and disappear every day. The number of synapses in your cortex changes by ~7% during a single day of learning (Kleim et al., 2004).
- No. "Synapses are only on dendrites." They are mostly on dendritic *spines* (small protrusions on dendrites) — but also on the soma, the axon initial segment (for inhibition), and even on other axons.

**Key properties:**

- **Stochastic:** Release probability is <1. Sometimes an AP releases 5 vesicles; sometimes 0. The brain is fundamentally noisy.
- **Plastic:** Synaptic strength (the "weight") can change on timescales of milliseconds to months.
- **Polarized:** Information flows in one direction — from axon to dendrite. (There are some exceptions.)
- **Modifiable by neuromodulators:** Dopamine, serotonin, acetylcholine can change how synapses respond without changing the input itself.
- **Multiple types:** Excitatory, inhibitory, modulatory. Different receptors, different time-courses, different effects.

**Where it appears in technology:**

- The **synapse** is the direct analog of a *weight* in a neural network. The strength of a synaptic connection = the "weight" between two artificial neurons.
- **Synaptic plasticity** (changing the weight) is the biological equivalent of *learning* in deep learning.
- The **presynaptic terminal** is a kind of analog memory device. Modern *memristors* are electronic components that change resistance based on the history of current flow — they physically mimic synaptic behavior and are being explored for neuromorphic computing (e.g., in IBM's TrueNorth).
- The **delay** (~1-5 ms per synapse) is enormous by computer standards. A modern CPU does a multiply-accumulate in nanoseconds. The brain is *a million times slower per operation* — and it does a million things in parallel.
- **Stochasticity** in synaptic release is something ANNs are just starting to adopt (Bayesian neural networks, dropout, etc.). The brain has used it forever.

**Why this matters for the rest:** The synapse is *the* site of learning. Every memory you have, every skill you've learned, is encoded in the strength of ~10¹⁵ synaptic connections. Change the synapse, change the mind. The next section goes deep on how synapses change — the heart of biological learning.

# What Are Dendrites and Dendritic Spines?

**The Problem:** A typical cortical neuron has 5,000-10,000 synaptic inputs arriving on its dendrites at different locations and times. To make a single decision ("should I fire?"), the neuron must add up all these signals in a meaningful way — giving more weight to important inputs, less to noisy ones, and combining them according to some rule. How is this done physically?

**Definition:** *Dendrites* are the branching input wires of a neuron. *Dendritic spines* are small (1 µm) protrusions on dendrites that host most excitatory synapses. They are the *primary site* of synaptic plasticity and computational complexity in the brain.

**How It Works (Step-by-Step):**

1. **Structure.** A typical cortical pyramidal neuron has:
   - A single apical dendrite rising toward the cortical surface
   - Several basal dendrites branching laterally
   - ~5,000-30,000 dendritic spines (small protrusions) on the dendrites
   - Each spine typically hosts one excitatory synapse
2. **Spine anatomy.** A spine has a *head* (~1 µm bulb) connected to the dendrite by a thin *neck* (~0.1 µm wide). Inside the spine head: a *postsynaptic density* (PSD) — a dense protein mesh containing receptors, scaffolding proteins, signaling molecules.
3. **Electrical compartmentalization.** The spine neck restricts current flow. This means each spine acts as a *semi-independent* electrical compartment. A strong input to one spine barely affects neighbors. This is critical for input-specificity of learning.
4. **Local computation.** Spines contain signaling molecules (CaMKII, calcineurin, Ras) that detect the timing of inputs and trigger plasticity. A single spine can "decide" to potentiate based on local activity.
5. **Active dendritic spikes.** Dendrites are not passive cables. They have voltage-gated channels (Na⁺, Ca²⁺, K⁺) that can generate local dendritic spikes. A dendritic spike is a regenerative event that travels a short distance within the dendrite, providing *nonlinear* integration.
6. **Back-propagating action potentials.** When the soma fires, the action potential travels backward into the dendrites. The coincidence of a back-propagating AP and a synaptic input is a key signal for plasticity (see STDP in `02_learning_mechanisms/`).
7. **Spine plasticity.** Spines change size, shape, and number with experience. LTP induces spine enlargement. LTD induces shrinkage. New spines appear within minutes of novel stimulation. Spines can disappear (be eliminated) within hours.
8. **Distance matters.** Synapses closer to the soma have more electrical influence than those far away on distal dendrites. Synapses on the same dendritic branch can interact via local dendritic spikes.

**Real-life analogy:** A dendritic tree is like a tree with thousands of leaves, each leaf a tiny antenna. Spines are like pins stuck into the leaves, each picking up one radio station. The tree trunk (the soma) is the decision-maker: it sees the sum of all signals. A small number of strong signals on a thick branch near the trunk can outweigh many weak signals on a thin branch far away. The branches themselves have amplifiers (active channels) that boost nearby signals.

**Tiny numeric example:** A single dendritic spine has a head volume of ~0.1 µm³. It contains ~100-1,000 AMPA receptors, 5-20 NMDA receptors, ~100 PSD-95 scaffolding proteins, and many kinases. The spine neck resistance is ~500 MΩ. This means the spine has a *time constant* of ~10-100 ms — long enough to integrate inputs over a meaningful window. A single spine's synaptic response is ~5-15 mV locally, but only ~0.1-0.5 mV at the soma. Pyramidal cells have ~5,000-30,000 spines; their total surface area is enormous (~250,000 µm²). If you unfolded all the dendrites and spines in one neuron, they'd cover an area larger than a single page.

**Common confusion:**

- No. "Dendrites are passive wires." No. They have voltage-gated channels, generate local spikes, and actively process information. Modern theory calls them "nonlinear computational subunits."
- No. "All spines are the same." No. They come in many shapes: thin (learning-ready), mushroom (stable memory), stubby, filopodia. Shape correlates with function.
- No. "More spines = smarter." Within limits, yes — but pruning is also essential. Children have *more* dendritic spines than adults. The overproduction-and-pruning pattern is critical for circuit refinement.
- No. "Spines are just for excitatory synapses." Mostly yes — inhibitory synapses form on the shaft, soma, or axon initial segment, not on spines. So spine plasticity is largely about *excitatory* circuit tuning.
- No. "Each spine is a separate unit." They are *partially* independent. They share resources (proteins, mRNAs from the soma), can compete for plasticity-related proteins (synaptic tagging), and can be coordinated by dendritic spikes.
- No. "Spines are fixed." They turn over constantly. In mouse cortex, ~5-10% of spines are added or eliminated each day. In human cortex, the rate is slower but the principle is the same.

**Key properties:**

- **Nonlinearity:** Dendrites don't just sum inputs linearly. They multiply, threshold, and even solve specific computations (e.g., XOR-like operations in single dendrites).
- **Spatial clustering:** Synapses on the same dendritic branch can cooperate. Co-active nearby spines trigger local dendritic spikes, which produce supralinear summation.
- **Multi-timescale:** Spine structure changes on seconds (volume), minutes (receptor insertion), hours (new protein synthesis), days (new spines).
- **BTSP-friendly:** Behavioral-timescale plasticity (BTSP) operates at the spine level, allowing single spines to associate events separated by seconds.
- **Heterogeneity:** A single neuron has spines of all sizes and ages, reflecting the history of its inputs.

**Where it appears in technology:**

- The **dendritic tree** is roughly analogous to the *input layer* of a neural network. But a real neuron's input layer is *much* more powerful than a deep learning input layer — it does nonlinear local computation.
- **Dendritic spikes** are a feature of *non-von Neumann* architectures. They allow a single neuron to compute something like a 2-layer network in a single unit.
- **Spine plasticity** is the biological analog of *weight update* in a neural network. But the spine can also generate its own plasticity signal locally (see synaptic tagging and capture).
- **Back-propagating action potentials** are part of the *backpropagation* of error signals in deep learning. But the brain's "backprop" is sparse, local, and gated by neuromodulators — not a global gradient.
- **Branching structure** in artificial neural networks (e.g., tree-structured networks, attention heads) is inspired by dendritic trees, but is far simpler.

**Why this matters for the rest:** The brain is not a network of point neurons. It is a network of *dendritic trees* with thousands of semi-independent computational subunits. This is the structural reason the brain is so powerful per neuron. When you understand the dendrite, you understand why a "neuron" in deep learning is a *radical oversimplification* of the real thing.

This completes the building blocks. The next section (`02_learning_mechanisms/`) goes deep on *how* synapses change — the heart of biological learning.

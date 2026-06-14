# What Is LTP and LTD?

**The Problem:** A Hebbian coincidence — pre fires, post fires — must cause a physical change in the synapse. It cannot be magic. What actually changes? How long does the change last? Can it go in both directions? The answers were discovered in 1973 in a rabbit hippocampus and have been refined for fifty years.

**Definition:** *Long-term potentiation (LTP)* is a long-lasting increase in synaptic strength following high-frequency stimulation. *Long-term depression (LTD)* is its mirror: a long-lasting decrease in synaptic strength following low-frequency stimulation. LTP and LTD are the leading candidate cellular mechanisms for learning and memory.

**How It Works (Step-by-Step):**

1. **Discovery.** In 1966, Terje Lømo in Per Andersen's lab in Oslo noticed that high-frequency stimulation of the perforant path in a rabbit hippocampus produced an unexpectedly long-lasting enhancement of the postsynaptic response. In 1973, with Timothy Bliss, he published the first characterization. They called it "long-lasting potentiation." Douglas and Goddard in 1975 renamed it "long-term potentiation."

2. **The classic induction protocol.** A brief high-frequency tetanic stimulation (e.g., 100 Hz for 1 second) of presynaptic axons produces a long-lasting increase in the postsynaptic response. The increase can last hours in a brain slice, days to weeks in a living animal.

3. **NMDA receptor is the molecular coincidence detector.** At a glutamatergic synapse, the NMDA receptor is blocked by Mg²⁺ at resting potential. It opens only when *both*:
   - Glutamate is bound (presynaptic neuron fired)
   - Postsynaptic depolarization removes the Mg²⁺ block
   - This is exactly the Hebbian coincidence condition.

4. **Ca²⁺ entry triggers the cascade.** With NMDA open, Ca²⁺ flows into the spine. Ca²⁺ activates:
   - **CaMKII** (Ca²⁺/calmodulin-dependent protein kinase II): phosphorylates AMPA receptors, increases their conductance, and traffics more AMPA receptors to the membrane.
   - **PKC** (protein kinase C): similar effect, more sustained.
   - **Ras/MAPK cascade**: signals to the nucleus to initiate gene transcription for the late phase.

5. **Early phase LTP (E-LTP)** lasts 1-3 hours. It requires only post-translational modification of existing proteins (no new gene expression). Blocking protein synthesis has no effect on E-LTP.

6. **Late phase LTP (L-LTP)** lasts 8+ hours, days, or longer. It requires:
   - New gene transcription in the nucleus
   - New protein synthesis
   - New synapse growth (structural plasticity)
   - PKMζ (a constitutively active kinase) is thought to maintain L-LTP.

7. **LTD induction.** Low-frequency stimulation (1 Hz for 10-15 min) or specific timing of pre/post activity (see STDP) produces a long-lasting *decrease* in synaptic strength. The molecular mechanism:
   - Smaller, slower Ca²⁺ influx
   - Activation of *calcineurin* (a phosphatase) instead of CaMKII
   - Removal of AMPA receptors from the postsynaptic density
   - Spine shrinkage

8. **The calcium hypothesis (Lisman, 1989):** A simple rule for LTP vs. LTD:
   - **High Ca²⁺** (large, fast transient) → LTP
   - **Moderate Ca²⁺** (smaller, sustained) → LTD
   - **Low Ca²⁺** → no change

9. **Properties of LTP:**
   - **Input-specificity:** LTP at one synapse does not spread to neighbors.
   - **Associativity:** A weak input paired with a strong input can be potentiated.
   - **Cooperativity:** Multiple weak inputs can sum to produce LTP.
   - **Persistence:** Lasts hours to months.

**Real-life analogy:** A muscle. When you exercise a muscle (high-frequency activation), it grows. When you don't use it, it atrophies. LTP and LTD are the synaptic equivalents of muscle growth and atrophy. The molecular machinery (Ca²⁺, kinases, phosphatases) acts like the cellular processes that build and break down muscle tissue.

**Tiny numeric example:** In a typical CA1 hippocampal slice experiment, a 1-second, 100-Hz tetanus produces an EPSP that grows by ~50-100% within minutes. The potentiation is stable for the recording duration (often 1-3 hours in slice, longer in vivo). Blocking NMDA receptors with AP5 (a competitive antagonist) completely blocks LTP induction. Tetanic stimulation that would normally produce LTP at one input can also produce LTP at a *different* weakly-activated input if both fire together — this is associativity (a cellular model of classical conditioning). The same input given 1 Hz for 15 minutes produces LTD — a ~30-50% decrease in EPSP amplitude.

**Common confusion:**

- No. "LTP = memory." Not quite. LTP is the leading *candidate* mechanism for memory, but memories are stored in *patterns* of synaptic changes across *networks* of neurons, not in single synapses. Single-synapse LTP is a building block.
- No. "LTP happens everywhere in the brain." LTP has been found in many brain regions (hippocampus, cortex, amygdala, cerebellum) but not in all synapses. The mechanisms differ. CA1 LTP is NMDA-dependent. Mossy fiber LTP is NMDA-independent (cAMP-dependent).
- No. "LTP is just an increase in neurotransmitter release." No. LTP has both presynaptic (increased release probability) and postsynaptic (more AMPA receptors) components. The relative contribution is debated.
- No. "LTP requires high-frequency stimulation only." No. LTP can also be induced by specific spike timings (pairing pre-before-post at low frequencies, see STDP). The "high-frequency" is just one way to ensure many coincidences.
- No. "LTP and LTD are opposites." They share some machinery but are not simple mirror images. The calcium threshold model is a useful simplification but the real picture is more complex.
- No. "LTP is a single mechanism." No. There are many forms of LTP (NMDA-dependent, NMDA-independent, mossy fiber, cortical, etc.) with different induction and maintenance mechanisms.

**Key properties:**

- **Hebbian:** Requires pre-post coincidence.
- **Input-specific:** Changes only the activated synapse.
- **Persistent:** Lasts hours to a lifetime.
- **Bidirectional:** Both LTP and LTD exist.
- **Multi-phase:** Early (post-translational) and late (gene-expression) phases.
- **Metaplastic:** LTP itself affects future LTP. Once a synapse is potentiated, the threshold for further LTP is higher; for LTD, lower (Bienenstock-Cooper-Munro rule).

**Where it appears in technology:**

- **Backprop is the engineering analog of LTP.** In a deep network, the weight update is computed from an error signal. In LTP, the weight update is computed from a Hebbian coincidence. The "error" in LTP is implicit — the synapse doesn't know the global error, only that it participated in firing the post.
- **Modern neuromorphic chips** (Intel Loihi, IBM TrueNorth) implement spike-based LTP rules in silicon. Each "synapse" is a small capacitor that charges with pre-post coincidence.
- **Memristors** are electronic components whose resistance depends on the history of current flow. They physically implement something like LTP at the device level.
- **Spike-timing-dependent plasticity (STDP)** is a refinement of LTP that uses spike timing instead of just rate. See next file.
- **Bienenstock-Cooper-Munro (BCM) rule** (1982) is a mathematical model that captures LTP/LTD as a function of postsynaptic activity, with a sliding threshold. It is widely used in computational neuroscience.

**Connection to next file:** LTP is a *rate-based* Hebbian rule (it cares about how much pre and post fire). The next file introduces **spike-timing-dependent plasticity (STDP)**, which uses the *precise timing* of pre and post spikes. STDP is a refinement of LTP that can implement much more powerful computations — including direction-sensitive learning and, potentially, a form of backprop.

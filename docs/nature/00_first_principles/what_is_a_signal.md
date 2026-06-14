# What Is a Signal?

**The Problem:** The brain does not store "information" abstractly. It stores *physical* states — ion concentrations, membrane voltages, vesicle release probabilities, gene expression levels. To understand how the brain learns, you first need to know what a *signal* is, physically, and how it differs from mere noise.

**Definition:** A *signal* is a measurable physical quantity that varies in space and time, and whose variation carries information about something — either an external cause, an internal state, or another signal. A *noise* is variation in the same quantity that carries no such information.

**How It Works (Step-by-Step):**

1. **Physical substrate.** Every signal is a *real, measurable, physical* thing. The voltage across a neuron's membrane. The concentration of Ca²⁺ in a dendritic spine. The rate at which a presynaptic neuron fires. The presence of a transcription factor in a nucleus.
2. **Variation is the message.** A signal that doesn't change carries no information. A signal that changes randomly (noise) carries no information either. A signal that changes *systematically* in response to something else is *information-bearing*.
3. **Encoding.** The mapping from *world event* to *physical state* is the *encoding*. A photon's wavelength → rhodopsin conformation → bipolar cell firing rate → LGN firing rate → V1 firing rate is a chain of *encodings*.
4. **Transmission.** The signal travels — along an axon, across a synapse, down a dendrite, through gap junctions, by diffusion in the cytoplasm. Each transmission can transform the signal (linear, nonlinear, stochastic).
5. **Decoding.** The downstream neuron *decodes* the signal: it integrates inputs and decides whether to fire. The act of firing is itself a signal.
6. **Bandwidth.** Every channel has a *bandwidth* — the rate at which it can transmit information. An axon: ~100-300 bits/s (action potentials are rate-coded, max ~500 Hz with 1-2 bits per spike). A chemical synapse: ~1-3 bits per release event. A gene expression level: much slower, ~0.1 bit/hour.
7. **Signal-to-noise ratio.** The signal's strength divided by the noise's strength. The brain spends enormous metabolic energy maintaining high SNR — through redundancy, amplification, predictive filtering, and top-down attention.

**Real-life analogy:** A signal is like a letter in the mail. The *physical substrate* is the paper. The *encoding* is the alphabet and the language. The *transmission* is the postal system. The *decoding* is the reader. *Noise* is water damage, smudges, and typos. The *bandwidth* is the number of letters per second the post office can carry.

**Tiny numeric example:** A single cortical pyramidal neuron has ~10,000 synaptic inputs. Each releases vesicles at ~0.1-1 Hz. Each release produces an EPSP of ~0.1-1 mV. The neuron's firing threshold is ~15 mV above rest. So ~30-50 simultaneous inputs are needed to fire the neuron. The information content of the *firing rate* is ~3-5 bits (a firing rate of 0.1-50 Hz is log-distributed). At ~10 Hz mean firing, this is ~30-50 bits/s of output per neuron. With ~10¹⁰ cortical neurons, the brain's total output bandwidth is ~10¹¹-10¹² bits/s, of which only ~50 bits/s is *conscious* (the rest is unconscious processing).

**Common confusion:**

- No. "The brain is an information processor." Yes, but it's a *physical, chemical, thermal* information processor. The information is always *carried* by something — charge, ion, molecule, fold. It is not abstract.
- No. "More neurons = more signal." Not necessarily. More neurons can mean *more noise* if they are not coordinated. The brain uses *sparse coding* (~1% of neurons active) to maximize signal-to-noise.
- No. "Spikes are digital." They are all-or-none, but they are *time-varying*. The signal is in the *timing* and *pattern*, not the spike itself.
- No. "The brain's signal is the firing rate." Rate coding is one mode. *Temporal coding* (precise spike timing relative to oscillations) and *population coding* (vector in high-dimensional activity space) are others. Different signals in different parts of the brain.
- No. "Signals are fast." Some are. Spike trains: ms. Gene expression changes: hours to days. Protein synthesis: minutes to hours. The brain uses slow signals (Ca²⁺, cAMP, gene expression) to *consolidate* what fast signals (spikes) *compute*.
- No. "Noise is bad." Some noise is bad (sensory noise reduces SNR). But *stochastic* noise can be *computational* — it enables exploration, prevents overfitting, and underlies probabilistic inference (sampling).

**Key properties:**

- **Physical:** Every signal is a real, measurable physical quantity.
- **Encodable:** It can be *mapped* to and from other signals via transformations.
- **Transmittable:** It can be propagated through physical channels (axons, synapses, diffusion, gap junctions).
- **Decodable:** Downstream systems can extract the *information* from the variation.
- **Bandwidth-limited:** Every channel has a maximum rate.
- **Noisy:** Real signals are corrupted by thermal noise, channel noise, biological variability.

**Where it appears in technology:**

- In engineering: voltage, current, frequency, packet arrival rate — all signals.
- In AI: an "embedding" is a *vector signal*. A "logit" is a *scalar signal*. A "spike" in a spiking neural network is a *digital signal*.
- The brain does *signal processing* in the strict engineering sense: filtering (dendrites), amplification (ion channels), modulation (neuromodulators), feedback (recurrent connections).
- The *key difference*: the brain's signals are *noisy, slow, multi-modal, neuromodulated*. AI signals are *clean, fast, single-modal, and unmodulated*.

**Connection to next file:** Now that you know what a signal is, the next question is: *how do you measure information in a signal?* That's `what_is_information.md`.

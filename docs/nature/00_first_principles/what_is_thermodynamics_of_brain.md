# What Is the Thermodynamics of the Brain?

**The Problem:** The brain runs at ~20 W — a fifth of your total body power. It is the most expensive organ in the body, gram-for-gram. It is also hot, noisy, and dissipative. It cannot run forever — you die without oxygen in minutes. To understand the brain, you must understand *why it is so expensive* and *what the energy budget buys you*.

**Definition:** The brain is a *dissipative structure* (Prigogine, 1977) — a system that maintains its order (low entropy) by continuously exporting entropy to its environment. The brain consumes glucose and oxygen to maintain ion gradients, fire spikes, release vesicles, and synthesize proteins. ~70% of the brain's energy goes to the *Na⁺/K⁺ pump* alone, which maintains the resting potential.

**How It Works (Step-by-Step):**

1. **The energy budget.** The human brain uses ~20% of resting metabolic power (despite being ~2% of body weight). Of that:
   - ~70% goes to the *Na⁺/K⁺ pump* (maintaining the resting potential — see Part 1)
   - ~10% goes to *signaling* (action potentials, synaptic transmission)
   - ~10% goes to *molecular synthesis* (proteins, neurotransmitters, lipids)
   - ~10% goes to *glia and maintenance* (myelination, glymphatic clearance, etc.)
2. **The second law.** The brain, like all physical systems, obeys the second law of thermodynamics: total entropy must increase. The brain's entropy is *low* (highly ordered: specific proteins, specific synaptic weights, specific gene expression patterns). To keep it low, the brain *exports* entropy to its environment (heat, waste, information loss). It is a *local* decrease in entropy at the cost of *global* increase.
3. **The free energy principle (Friston).** Living systems (including the brain) act to *minimize surprise* (variational free energy). This is equivalent to *resisting the natural tendency toward disorder*. The brain uses predictive models to do this efficiently.
4. **Energy per spike.** A single cortical action potential costs ~10⁹ ATP molecules (about 1 femtojoule = 10⁻¹⁵ J). A CPU floating-point operation costs ~10⁻⁹ J (a nanojoule). The brain is a million times more energy-efficient per operation. This is because it uses *analog, sparse, event-driven* computation — not dense synchronous digital switching.
5. **Why so much energy for the pump?** The Na⁺/K⁺ pump burns ~3 ATP per cycle, moving 3 Na⁺ out and 2 K⁺ in. This restores the ion gradient after every spike. If you stop pumping, the gradient collapses in seconds. The brain's *information* (encoded in spike patterns and synaptic weights) is *physically grounded* in these gradients. They are not optional.
6. **The cost of plasticity.** LTP requires new protein synthesis, AMPA receptor insertion, spine enlargement. This is metabolically expensive. Sleep may be partly about *consolidating* these expensive changes during low-activity periods.
7. **Glucose and oxygen.** The brain uses glucose almost exclusively. Ketone bodies can substitute during starvation. The brain has very low glycogen stores (unlike muscle), so it depends on a continuous supply of blood glucose. Hypoglycemia → confusion → coma → death in minutes.
8. **Heat dissipation.** The brain generates ~10-20 W of heat. Active regions generate more (functional imaging like fMRI detects this). Without cooling (blood flow), the brain would overheat within minutes.

**Real-life analogy:** The brain is like a *city that runs on electricity*. The power plants (mitochondria) burn fuel (glucose + oxygen) to generate electricity (ATP). The electricity powers the pumps (Na⁺/K⁺ pumps) that keep the city's water pressure up (ion gradients). When you turn on a light (fire a spike), water flows out (Na⁺ in). The pump immediately restores pressure. The city is *never idle* — even when you're asleep, the pumps are running, the maintenance crews are working, the streets are being cleaned (glymphatic system). The cost is enormous — but the alternative is immediate death.

**Tiny numeric example:** The human brain has ~86 billion neurons and ~75 trillion synapses. Total ATP consumption: ~5 × 10²¹ ATP/s = ~5 W *just for ion pumping* (per Attwell & Laughlin, 2001). Of this, the cortex accounts for ~50% of the metabolic cost despite being ~80% of the brain mass. A single cortical pyramidal neuron firing at 1 Hz costs ~2.5 × 10⁹ ATP/s. Across all cortical neurons at 1 Hz average: ~2 × 10²⁰ ATP/s — 4% of the brain's total budget. The remaining cost is for housekeeping, protein turnover, vesicle recycling, etc. *Cognition* (thinking, planning) is a *small fraction* of the total cost.

**Common confusion:**

- No. "The brain runs on electricity." No. The brain runs on *chemistry* (ATP, ion gradients). The *signals* are electrical (ions moving), but the *power* is chemical.
- No. "Thinking harder uses more energy." Only a little more. Most of the brain's energy is *housekeeping* — it doesn't change much with cognitive load. The brain is expensive whether you are doing math or sleeping.
- No. "We use 10% of our brain." No. We use *all* of it, but most regions are not doing the kind of cognition you notice. fMRI shows widespread activation for most tasks.
- No. "The brain is inefficient." It is *very efficient* given the constraints. It is the most efficient neural computer in existence. A modern GPU uses ~10⁶× more power per useful operation.
- No. "Energy is just for spiking." No. Spikes are ~10% of the cost. The other 90% is for *maintaining* the ion gradients that make spikes possible.
- No. "The brain could evolve to be more efficient." Maybe, but the cost is the *price of plasticity*. More energy = more ATP available for protein synthesis, LTP, growth. The brain is *expensive because it learns constantly*.

**Key properties:**

- **High metabolic cost:** ~20% of body energy, ~2% of mass.
- **Continuous:** The brain never "shuts off." Even under anesthesia, ~50% of baseline activity remains.
- **Mostly housekeeping:** Most energy goes to *maintaining the gradients*, not to thinking.
- **Local:** Most energy is used locally (in the active neurons), not globally.
- **Heat-producing:** ~10-20 W of heat output.
- **Oxygen-dependent:** Cannot survive more than a few minutes without oxygen.

**Where it appears in technology:**

- **Neuromorphic chips** (Intel Loihi, IBM TrueNorth) are designed to be brain-like in their energy use: sparse, event-driven, analog, ~1000× more efficient than GPUs.
- **The free energy principle** (Friston) is being applied to AI as a *principle for designing agents* that are thermodynamically efficient.
- **Predictive coding networks** are more efficient than dense feedforward networks because they only propagate *errors*, not all data.
- **The brain's energy budget** sets a *physical lower bound* on what AI can achieve without more efficient substrates. A brain-like AI on a GPU would need ~10 MW of power (vs. 20 W).
- **Energy-based models** (LeCun et al.) are inspired by the brain's thermodynamics — they define a *scalar energy* for each configuration and learn to minimize it.

**Connection to next file:** Now you have the four first principles. You're ready for the physical substrate. Go to Part 1: Building Blocks, where you learn about neurons, membranes, action potentials, and synapses.

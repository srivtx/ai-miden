# What Is Neuromorphic Computing?

**The Problem:** The human brain uses ~20 W. A modern GPU uses ~700 W. The brain is ~10⁶× more energy-efficient per useful operation. If we want brain-like AI, we need brain-like *hardware* — not GPU simulations of neurons, but actual spiking, event-driven, low-power analog computation.

**Definition:** *Neuromorphic computing* is the design of hardware that *mimics the structure and dynamics of biological neurons*. It uses *spikes* (event-driven), *analog* computation, *in-memory* processing, and *low-precision* signals. The goal: brain-like efficiency (10¹⁵ ops/s at 20 W) on silicon.

**How It Works (Step-by-Step):**

1. **The fundamental inefficiency of GPUs.** A modern GPU:
   - Uses ~700 W for ~10¹⁵ ops/s (~10⁹ ops/J)
   - Is *dense* — every transistor is active on every cycle
   - Is *digital* — 32-bit floating point (or 16-bit) precision
   - Is *synchronous* — every operation happens on a global clock
   - Is *separated* — memory and compute are in different places
2. **The brain's approach.** A biological brain:
   - Uses ~20 W for ~10¹⁵ ops/s (~10¹⁴ ops/J) — 10⁵× more efficient
   - Is *sparse* — ~1% of neurons active at any moment
   - Is *analog* — continuous-valued signals (though spikes are digital)
   - Is *asynchronous* — each neuron fires on its own schedule
   - Is *co-located* — memory and compute are in the same place (synapses are the memory)
3. **Neuromorphic principles.** A neuromorphic chip tries to capture these properties:
   - **Spiking:** information is encoded in *spike events* — like the brain.
   - **Event-driven:** compute happens only when a spike arrives — no work, no power.
   - **In-memory computation:** memory (synapses) and compute (neurons) are in the same place — no von Neumann bottleneck.
   - **Analog or mixed-signal:** some computation is analog (like the brain) for energy efficiency.
   - **Stochastic:** random noise can be used (like the brain) to improve robustness and enable sampling.
4. **Major neuromorphic platforms.**
   - **Intel Loihi** (2017, 2nd gen 2021). ~128 million silicon neurons, ~130 billion synapses, on a single chip. 14 nm process. Used in olfactory sensing, robotic arms, optimization problems.
   - **IBM TrueNorth** (2014). 1 million neurons, 256 million synapses, 5.4 billion transistors, 70 mW. Used in DARPA SyNAPSE program.
   - **SpiNNaker** (University of Manchester, ongoing). A million-core ARM-based system simulating spiking neurons. Used in the Human Brain Project.
   - **Intel Loihi 2** (2021). 1 million neurons per chip, programmable learning rules (including STDP, three-factor learning).
   - **BrainScaleS** (Heidelberg). Analog neuromorphic, 200,000× speedup over biological time.
   - **Akida** (BrainChip). Event-based neuromorphic processor for edge AI.
   - **GrAI Matter** (now BrainChip). "Loihi-like" spiking chips.
5. **Applications.**
   - **Always-on edge AI:** neuromorphic chips use milliwatts. Suitable for wearables, IoT, sensors.
   - **Robotics:** low-latency, low-power motor control.
   - **Sensory processing:** event cameras + neuromorphic chips for ultra-fast visual processing.
   - **Optimization:** neuromorphic solvers for combinatorial problems (routing, scheduling).
   - **Brain-computer interfaces:** low-power neural recording and stimulation.
6. **The software challenge.** The hardware is one thing; the *software* is another. Most neuromorphic platforms have *poor tool support*. Few developers can program them. Spiking neural networks (SNNs) are harder to train than ANNs. SNN training algorithms (STDP, surrogate gradients, ANN-to-SNN conversion) are an active research area.
7. **The "killer app" question.** What is the application that will make neuromorphic ubiquitous? The candidates:
   - **Edge AI** (always-on, low-power) — probably the first big win
   - **Robotics** (low-latency motor control) — likely
   - **Event-based vision** (high-frame-rate, low-power) — strong niche
   - **Optimization** (combinatorial problems) — possible
   - **Brain-computer interfaces** — long-term
   - **AGI** — speculative, but neuromorphic is a more plausible substrate than GPU for brain-like AI
8. **Limitations.** Neuromorphic chips are not a *replacement* for GPUs. They are a *complement*. For dense matrix multiplication (the bread and butter of deep learning), GPUs are still best. For sparse, event-driven, low-power computation, neuromorphic wins.
9. **The brain's remaining tricks.** Even the best neuromorphic chips do not match the brain in:
   - *Density:* 10¹⁵ synapses per cubic cm in the brain. Intel Loihi 2: ~10¹¹ synapses per chip. 10,000× off.
   - *Energy:* brain 20 W. Loihi 2: ~1 W. 20× off.
   - *Algorithms:* the brain's algorithms (STDP, three-factor learning, predictive coding, BTSP) are not yet matched by neuromorphic software.
   - *Neuromodulation:* neuromorphic chips have no dopamine, ACh, or NE.
10. **The future.** The next 5-10 years will likely see:
    - Neuromorphic chips with 10¹²+ neurons per chip (1 trillion).
    - Software tools that make neuromorphic programming as easy as PyTorch.
    - Hybrid CPU + neuromorphic systems.
    - Real brain-like AI on neuromorphic substrates.

**Real-life analogy:** A GPU is like a *gasoline car* — powerful, but inefficient. The brain is like a *Tesla* — efficient, but limited. Neuromorphic chips are *electric cars* — they're starting to be efficient, but the software (charging infrastructure) is still catching up.

**Tiny numeric example:** A typical inference task on MNIST:
- **GPU (NVIDIA A100):** ~300 W, ~50,000 images/s, ~6 µJ/image
- **Neuromorphic (Intel Loihi 2):** ~1 W, ~10,000 images/s, ~0.1 µJ/image
- **Human brain (vision, for the same task):** ~10 W (total brain), ~100 images/s, ~0.1 J/image

Wait, the brain is *less* efficient for this task. The brain's efficiency advantage is for *general-purpose intelligence* — vision + language + reasoning + motor control all in one. For narrow tasks, GPUs win. For general intelligence, the brain is in a different league.

**Common confusion:**

- No. "Neuromorphic chips will replace GPUs." No. They will *complement* GPUs. GPUs are best for dense, parallel, matrix-heavy computation. Neuromorphic is best for sparse, event-driven, low-power computation.
- No. "Neuromorphic chips are programmed like ANNs." Not really. They are programmed with *spikes* and *synaptic events*. The programming models are different.
- No. "Neuromorphic = spiking." Mostly yes, but there are also *analog* neuromorphic chips (BrainScaleS) and *event-based* digital neuromorphic chips (Loihi, TrueNorth).
- No. "The brain is a neuromorphic chip." The brain is the *inspiration* for neuromorphic chips. Neuromorphic chips are still 10,000× off the brain in density.
- No. "Neuromorphic is just for AI." No. It is for any sparse, event-driven computation. Robotics, sensing, optimization, signal processing.
- No. "We'll have AGI in 5 years with neuromorphic chips." Almost certainly not. The hardware is necessary but not sufficient. The algorithms are not yet there (see the rest of this part).

**Key properties:**

- **Spiking:** Uses discrete events, not continuous values.
- **Event-driven:** Compute only on spikes.
- **In-memory:** Memory and compute are co-located.
- **Low-power:** Milliwatts to watts, not hundreds of watts.
- **Sparse:** Most of the chip is inactive at any moment.
- **Stochastic:** Noise is often used.
- **Inferior for dense compute:** GPUs are better for matrix multiplication.

**Where it appears in technology:**

- **Edge AI:** wearables, IoT sensors, always-on cameras. Neuromorphic chips enable AI on devices that couldn't afford a GPU.
- **Robotics:** low-latency, low-power motor control. Event-based cameras + neuromorphic chips enable sub-millisecond response.
- **Brain-computer interfaces:** low-power neural recording and stimulation. Closed-loop BCIs need to be low-power to avoid heating tissue.
- **Optimisation:** routing, scheduling, NP-hard problems. Neuromorphic solvers are competitive for some problems.
- **AGI speculation:** some theorists argue AGI will require neuromorphic substrates. This is not proven, but plausible.

**Connection to next file:** The hardware is the substrate. The algorithm is the next layer. *Predictive coding networks* are a biologically-plausible alternative to backprop that can be implemented on neuromorphic hardware.

# What Is the Biological Neuron?

**The Problem:** Computers compute with bits (0 or 1) and transistors (on or off). But a brain made of 86 billion "switches" can learn language from a few years of listening, recognize faces in a fraction of a second, and run on 20 watts. Something is fundamentally different. To understand the difference, you have to start at the unit: the cell.

**Definition:** A neuron is a specialized biological cell that receives, integrates, and transmits electrical and chemical signals. Unlike a transistor, it is alive, noisy, slow, self-repairing, and exists in trillions of versions across the brain.

**How It Works (Step-by-Step):**

1. **Structure:** A neuron has three main parts — a *dendrite tree* (input wires), a *soma* (cell body), and an *axon* (output wire). Dendrites receive signals from thousands of other neurons.
2. **Resting state:** Even at rest, the inside of a neuron is electrically negative relative to the outside (~ -70 millivolts). This *membrane potential* is maintained by ion pumps (especially the sodium-potassium pump) that consume ATP.
3. **Reception:** When neighbors fire, they release chemicals (neurotransmitters) onto the dendrites. These chemicals open ion channels, letting charged particles flow in or out. The result is a small voltage change called a *postsynaptic potential*.
4. **Integration:** The soma adds up thousands of these tiny inputs over time and space. Excitatory inputs push the voltage up; inhibitory inputs push it down. If the sum crosses a *threshold* (~ -55 mV), the neuron fires.
5. **Firing:** A fire is an *action potential* — a brief, stereotyped voltage spike (about 1 millisecond long) that travels down the axon at up to 120 meters per second.
6. **Output:** At the axon terminal, the spike triggers release of neurotransmitters onto the next neuron's dendrites, repeating the cycle.

**Real-life analogy:** A neuron is like a tiny, leaky, opinionated voting machine. Each input from another neuron is one vote. The soma is the tally counter. If the votes exceed a threshold, the machine sends a single, identical "yes" signal down its output wire. The signal is always the same strength — there is no "shouting" — only "fired" or "did not fire."

**Tiny numeric example:** A typical cortical pyramidal neuron has ~5,000–10,000 synaptic inputs. Each synapse contributes about 0.1–1 mV. The firing threshold is ~15 mV above resting (-55 vs -70 mV). So roughly 20–100 excitatory inputs need to fire within a few milliseconds to make this neuron fire. The neuron can fire up to ~100–200 spikes per second maximum.

**Common confusion:**

- No. "Neurons think." Neurons don't think. They are voltage integrators. Thought emerges from circuits of neurons, just as a forest emerges from trees.
- No. "Action potentials carry information in their shape." No — every spike is the same shape. Information is in the *timing* and *pattern* of spikes (rate code, temporal code, population code).
- No. "Neurons are digital." They are not. Inputs are graded analog voltages; only the output spike is "all-or-none." Neurons are analog-in, digital-out devices.
- No. "Neurons are slow." Each spike is slow (~1 ms) compared to a transistor gate (~nanoseconds). But the brain runs 10¹⁵ ops/s by massive parallelism.
- No. "Bigger neurons = smarter." A blue whale has neurons bigger than a human's. Intelligence correlates with *cortical column count* and *circuit complexity*, not cell size.
- No. "We use all our neurons." Yes, you do. Losing even a small percentage (as in Alzheimer's or stroke) causes severe deficits. There is no dormant 90%.

**Key properties:**

- **Sparseness:** In any moment, only ~1–5% of cortical neurons are firing. Most are silent.
- **Stochasticity:** Spike timing is noisy and probabilistic. A neuron given the same input may or may not fire.
- **Nonlinearity:** Inputs are summed linearly; output is a hard threshold. This is the simplest possible "unit" of a neural network.
- **Adaptation:** Neurons fatigue. They reduce their firing rate with sustained input. This is a built-in normalizer.
- **Plasticity:** The strength of synaptic inputs changes with experience (see `02_*/`).

**Where it appears in technology:**

- A **perceptron** (1943) is a mathematical model of one neuron's input-sum-and-threshold behavior. Modern artificial neurons in deep learning are direct descendants.
- However, a biological neuron has **~5,000–10,000 inputs**, while an artificial neuron in an LLM has at most a few thousand. They are similar in form but not in scale, time, or chemistry.
- The most important difference: a biological neuron's "weight" is not a single number but a complex, time-evolving, multi-timescale, neuromodulated process (see `02_learning_mechanisms/`).

**The deeper question this file sets up:** If a neuron is just a leaky integrator, where does learning happen? The answer is: at the *synapses* between neurons. The next file explains.

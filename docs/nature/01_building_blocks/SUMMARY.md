# Part 1: Building Blocks — Summary

> The brain is built from a handful of elegant physical principles. Once you understand them, every higher function — memory, attention, prediction, consciousness — is a story about how these primitives combine.

---

## The five primitives

1. **The neuron** (`what_is_the_neuron.md`) — A leaky integrator of votes. Receives thousands of inputs, sums them, fires a stereotyped spike if the sum crosses threshold.

2. **The cell membrane and resting potential** (`what_is_the_cell_membrane.md`) — A 5-nm wall that holds a 70-mV battery. Maintained by ion pumps using ATP. The "off" state from which all signals are deviations.

3. **The action potential** (`what_is_the_action_potential.md`) — An all-or-none, self-propagating electrical pulse. ~1 ms long. Triggered by threshold, regenerated at every point along the axon. The "bit" of biological computing.

4. **The synapse** (`what_is_the_synapse.md`) — A 30-nm chemical gap where one neuron's output becomes another neuron's input. Stochastic, plastic, slow (1-5 ms delay), and the *site* of all learning.

5. **Neurotransmitters and receptors** (`what_is_neurotransmitter.md`) — The brain's vocabulary. ~10 major transmitters, hundreds of receptor types, two timescales (fast ionotropic, slow metabotropic). Glutamate = "go," GABA = "stop," monoamines (DA, 5-HT, ACh, NE) = "modulate the entire mode."

6. **Dendrites and spines** (`what_is_dendrite_spine.md`) — Branching input structures with thousands of semi-independent computational units. Each spine hosts one synapse and acts like a tiny local computer. Dendrites generate their own spikes, not just passive currents.

---

## The unified picture

```
Inputs (dendrites/spines)
     │
     │ 10,000 synapses per neuron
     │ each synapse uses glutamate, GABA, or a modulator
     │ each synapse is stochastic, modifiable, and time-delayed
     ▼
Soma (cell body)
     │
     │ integrates ~5,000-10,000 inputs
     │ uses analog summation
     │ fires if voltage crosses threshold
     ▼
Action potential
     │
     │ stereotyped 1-ms spike
     │ self-propagates down axon
     │ at ~1-120 m/s depending on myelination
     ▼
Axon terminal
     │
     │ Ca²⁺-triggered vesicle fusion
     │ releases neurotransmitter into 30-nm cleft
     │ signal crosses in ~0.1 ms
     ▼
Next neuron's dendrite
     │ (loop back to top)
```

The brain runs this loop ~10¹⁵-10¹⁷ times per second. Each iteration is a stochastic, plastic, neuromodulated event. There is no central clock, no global loss function, no backprop. There is just an enormous, parallel, embodied, sparse, and constantly-learning network.

---

## Key technology comparisons so far

| Biological primitive | Tech analog | What's missing in tech |
|---|---|---|
| Neuron | Artificial neuron (perceptron) | Time, stochasticity, neuromodulation, multi-compartment |
| Membrane potential | Capacitor + battery | Ion specificity, active maintenance |
| Action potential | TTL logic gate, spiking neuron | Refractory period, frequency adaptation, energy cost |
| Synapse | Weight (scalar number) | Stochasticity, plasticity, multiple timescales |
| Neurotransmitter | Activation function / signal | Receptor specificity, neuromodulation, volume transmission |
| Dendritic spine | Input feature | Local computation, compartmentalization, multi-timescale plasticity |

The takeaway: **every "weight" in a neural network is a synapse, but every synapse is also a tiny time-evolving molecular computer.** A real neuron is not a perceptron. A real synapse is not a weight.

---

## Connection to the next part

We've established the *physical* substrate. The next part asks: **how does it learn?**

- `02_learning_mechanisms/what_is_hebbian_learning.md` — The original 1949 rule
- `02_learning_mechanisms/what_is_ltp_ltd.md` — The molecular basis of memory
- `02_learning_mechanisms/what_is_stdp.md` — Timing-based learning
- `02_learning_mechanisms/what_is_three_factor_learning.md` — How neuromodulators gate learning
- `02_learning_mechanisms/what_is_btsp.md` — Learning on behavioral timescales
- `02_learning_mechanisms/what_is_homeostatic_plasticity.md` — How the brain stays stable

The most important thing to remember from Part 1: **the brain is built from analog, stochastic, time-evolving, neuromodulated chemistry — not from clean digital symbols.** Every part afterward will be about how this chemistry learns.

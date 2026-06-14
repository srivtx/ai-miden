# What Is the Cell Membrane and the Resting Potential?

**The Problem:** A neuron's inside is salty water with proteins and potassium. Its outside is salty water with sodium, chloride, and calcium. These two solutions are separated by a wall only 5 nanometers thick. Yet that wall sustains a 70-millivolt voltage difference. Why does this matter? Because every thought, every memory, every spike depends on it.

**Definition:** The *plasma membrane* is a 5-nm-thick double layer of lipid (fat) molecules with embedded proteins. It is a barrier and a gate. The *resting potential* is the ~ -70 mV voltage difference between the inside and outside of a neuron at rest, maintained by ion pumps and selective ion channels.

**How It Works (Step-by-Step):**

1. **The membrane:** Two layers of phospholipid molecules — each has a water-loving head and a water-fearing tail. They self-assemble tail-to-tail in water. The result is a 5-nm-thick sheet that blocks ions and water-soluble molecules but lets lipid-soluble things (oxygen, CO₂) through.
2. **The lipid bilayer is an insulator.** It does not allow sodium (Na⁺), potassium (K⁺), chloride (Cl⁻), or calcium (Ca²⁺) to cross freely. Without help, no signal could pass.
3. **Embedded proteins do the work.** Three classes matter for signaling:
   - **Ion pumps** (e.g., the sodium-potassium pump, Na⁺/K⁺-ATPase): actively transport ions against their gradient, using ATP. They pump 3 Na⁺ out and 2 K⁺ in per cycle.
   - **Leak channels:** always open; mostly pass K⁺. They are why the resting potential is close to E_K (~-75 mV) rather than 0.
   - **Gated channels:** open in response to voltage, neurotransmitter binding, or mechanical stretch. They produce the *signals*.
4. **Setting the gradients:** The pumps concentrate K⁺ inside (~140 mM) and Na⁺ outside (~145 mM). They are constantly working, burning ~70% of a neuron's ATP just to maintain these gradients.
5. **The resting potential emerges:** Because the membrane is more permeable to K⁺ than Na⁺, K⁺ leaks out down its concentration gradient, leaving the inside negative. The voltage settles at ~-70 mV — the point where the electrical pull balances the chemical push.
6. **The Goldman-Hodgkin-Katz equation** describes this precisely. It weighs the permeability of each ion by its concentration inside and outside:
   V = (RT/F) × ln[(P_K[K⁺]_out + P_Na[Na⁺]_out + P_Cl[Cl⁻]_in) / (P_K[K⁺]_in + P_Na[Na⁺]_in + P_Cl[Cl⁻]_out)]
7. **Change the permeability, change the voltage.** Open Na⁺ channels → Na⁺ rushes in → voltage rises (depolarization). Open Cl⁻ channels → Cl⁻ rushes in → voltage falls (hyperpolarization). Open K⁺ channels → K⁺ rushes out → voltage falls.

**Real-life analogy:** Imagine two reservoirs of water at different heights, connected by a narrow pipe with a one-way valve. The pump (your heart, for water; Na⁺/K⁺ pump, for ions) keeps one side high. A small leak valve (K⁺ leak channel) lets the high side drain slowly into the low side. The water pressure (voltage) at the leak equals the height difference. Now imagine a floodgate (voltage-gated Na⁺ channel). When you open it, water rushes from high to low — fast.

**Tiny numeric example:** A single 1 mm² patch of membrane has ~100 million phospholipids per layer. It contains ~1,000 sodium-potassium pumps. Each pump cycles ~100 times per second, moving 300 Na⁺ out and 200 K⁺ in per second. The whole human brain runs ~10²⁰ of these cycles per second to maintain gradients. A single spike moves only ~10⁶ Na⁺ ions — about one-millionth of the Na⁺ in the cell. So gradients are barely disturbed by spikes. This is why you can fire billions of spikes without "running out" of ions.

**Common confusion:**

- No. "The membrane is just a wall." It is a wall, a battery, a switch, a clock, and a chemical computer, all in 5 nm. The proteins are where the work happens.
- No. "Resting means off." A neuron at -70 mV is doing massive work. ~70% of its energy goes to maintaining the resting potential. The brain is never idle.
- No. "Ions just flow freely across." They do not. The lipid bilayer is essentially impermeable to ions. Every ion movement is gated by a protein.
- No. "The voltage comes from electron flow." No — it comes from *ion* flow. Neurons do not use electrons. They use Na⁺, K⁺, Ca²⁺, Cl⁻ dissolved in water.
- No. "All cells have the same resting potential." No. Most cells are around -20 to -90 mV. Neurons, muscle, and some endocrine cells are excitable. Skin cells are -40 mV. Red blood cells are -10 mV.
- No. "The pumps could be replaced by gravity." In a real neuron, the gradient is so steep that diffusion alone would equalize the concentrations in seconds. Pumps must continuously work against entropy. This is why neurons die within minutes of oxygen loss (stroke).

**Key properties:**

- **Selective permeability:** Different ions pass through different channels at different rates.
- **Voltage-sensitivity:** Some channels open only when the membrane voltage crosses a threshold.
- **Active maintenance:** Pumps use ATP to maintain the gradient; this is expensive.
- **Asymmetry:** The concentrations inside vs. outside are very different, and this asymmetry is what makes signals possible.
- **5 nm thick:** Smaller than the wavelength of visible light. You cannot see a membrane with a regular microscope.

**Where it appears in technology:**

- A **capacitor** in a circuit is a 2-plate insulator that stores charge. The cell membrane is essentially a capacitor (capacitance ~1 µF/cm²) with ion channels and pumps bolted on.
- The **resting potential** is the "off" state. Every signal in the brain is a deviation from -70 mV.
- The **Na⁺/K⁺ pump** is the single most ATP-consuming protein in the body. It consumes ~25% of all calories your brain burns. Modern neuromorphic chips (Intel Loihi, IBM TrueNorth) try to mimic this with low-power analog circuits.

**Why this matters for the rest:** Every subsequent topic in this curriculum — action potentials, synapses, plasticity — is a story about proteins in this 5-nm wall opening, closing, and modifying themselves. If you don't get the membrane, nothing else makes sense.

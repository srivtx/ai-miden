# What Are Glial Cells?

**The Problem:** For most of the 20th century, neuroscience focused on neurons. Glial cells were dismissed as "support cells" — the brain's glue, doing housekeeping. But glia are ~50% of the brain's cells. They outnumber neurons in some regions. Recent work shows they actively regulate synaptic transmission, plasticity, and even information processing. You cannot understand the brain without understanding glia.

**Definition:** *Glial cells* (or *neuroglia*) are non-neuronal cells in the nervous system that provide structural, metabolic, and modulatory support. The major types in the central nervous system are astrocytes, oligodendrocytes, microglia, and NG2 glia. In the peripheral nervous system: Schwann cells and satellite glia.

**How It Works (Step-by-Step):**

1. **Astrocytes** — The most numerous glia in the CNS (~20-40% of all cells). Star-shaped cells with extensive processes that contact both blood vessels and synapses.
   - **Tripartite synapse:** An astrocytic process ensheathes a synapse. The astrocyte senses neurotransmitter release, responds by releasing its own gliotransmitters (ATP, adenosine, glutamate, D-serine), and modulates synaptic strength.
   - **D-serine** from astrocytes is the co-agonist for the NMDA receptor. Without D-serine, NMDA receptors barely work. So astrocyte signaling is required for LTP.
   - **Glutamate uptake:** Astrocytic transporters (EAAT1, EAAT2) clear ~90% of released glutamate from the synaptic cleft. This is what terminates the synaptic signal.
   - **K⁺ buffering:** Astrocytes take up K⁺ released by neurons and redistribute it through the astrocytic network. This prevents extracellular K⁺ from rising to seizure-inducing levels.
   - **Blood-brain barrier:** Astrocyte endfeet on blood vessels induce and maintain the BBB.
   - **Metabolic support:** Astrocytes take up glucose from blood, store it as glycogen, and supply lactate to neurons on demand.
   - **Calcium waves:** Astrocytes communicate via Ca²⁺ waves that propagate through their network, sometimes over millimeters. These waves can modulate synaptic plasticity in thousands of synapses at once.

2. **Oligodendrocytes** — The myelinating cells of the CNS. Each oligodendrocyte myelinates ~10-50 axons. Myelin is the fatty insulating sheath that allows saltatory conduction (see `01_building_blocks/what_is_the_action_potential.md`).
   - **NG2 glia (oligodendrocyte precursor cells, OPCs)** are the only glia that receive direct synaptic input from neurons. They have glutamatergic and GABAergic synapses, and they release signals back. They are also a reservoir of new oligodendrocytes for remyelination.
   - **Activity-dependent myelination:** Neuronal activity promotes local myelination. So the brain can adapt its own conduction speed by myelinating more or less of specific axons. This is *another* form of plasticity.

3. **Microglia** — The brain's immune cells. ~10% of brain cells. They:
   - Continuously survey the brain with extending and retracting processes
   - Engulf dead cells and debris (phagocytosis)
   - Prune synapses during development (eat weak synapses, leaving strong ones)
   - Release cytokines that modulate inflammation and plasticity
   - Respond to injury by becoming "activated" (amoeboid morphology, release of pro-inflammatory signals)
   - In Alzheimer's, microglia become chronically activated, contributing to neuroinflammation

4. **Schwann cells** (PNS) — The peripheral analogs of oligodendrocytes. Each Schwann cell myelinates one axon segment.

5. **Ependymal cells** — Line the ventricles, produce cerebrospinal fluid, and have cilia that circulate CSF.

6. **NG2 glia** — Mentioned above. They are the only glia that receive direct synaptic input. Their function is still being elucidated.

**Real-life analogy:** A city has visible buildings (neurons) and invisible infrastructure (glia). The infrastructure includes power plants (metabolic support), water and sewage (ion and neurotransmitter clearance), road maintenance (myelination), security (microglia), and even local councils that decide which buildings get resources (astrocyte signaling). The visible buildings do the talking; the infrastructure does the rest.

**Tiny numeric example:** The human brain has ~86 billion neurons and a roughly equal number of glial cells. There are ~200 billion astrocytes alone in the human cerebral cortex. Each astrocyte contacts ~100,000-1,000,000 synapses via its fine processes. Each oligodendrocyte myelinates ~10-50 axon segments. Each microglial cell surveys the entire brain every few hours via process extension/retraction. The ratio of glia to neurons is higher in larger brains (1.4:1 in human, 0.3:1 in mouse).

**Common confusion:**

- No. "Glia are just support cells." They were thought to be. They are now known to actively modulate synaptic transmission, plasticity, and information flow.
- No. "Microglia are only active during disease." No. They are *always* active, surveying the brain for damage and pruning synapses.
- No. "Astrocytes just clean up glutamate." They do much more: they release gliotransmitters, regulate K⁺, supply metabolic substrates, and modulate the BBB.
- No. "Myelination is fixed in adulthood." No. New myelin can form in adulthood, and it is activity-dependent. This affects conduction velocity and therefore *information timing* in the brain.
- No. "Glia don't divide in adults." Astrocytes and NG2 glia can divide. Microglia are derived from peripheral immune precursors and can be replenished from the blood.
- No. "The blood-brain barrier is a wall of cells." It's mostly *astrocyte endfeet* on blood vessel walls. The barrier is induced and maintained by astrocytes.

**Key properties:**

- **Active modulators:** Glia don't just support — they *regulate* synaptic transmission.
- **Spatial reach:** A single astrocyte contacts up to 1 million synapses. One oligodendrocyte myelinates 50 axons. Glia act at scales much larger than single neurons.
- **Plastic:** Glia change with experience. Astrocyte processes grow and retract. Microglia change state. New myelin forms.
- **Disease-relevant:** Glial dysfunction is implicated in almost every neurological and psychiatric disease — Alzheimer's (microglial activation, astrocyte reactivity), multiple sclerosis (oligodendrocyte loss), epilepsy (astrocyte K⁺ buffering failure), schizophrenia (microglial pruning abnormalities).
- **Slow:** Glial signaling is typically slower than neural (ms for neurons; seconds to minutes for gliotransmitter release, hours for microglial activation).

**Where it appears in technology:**

- **Tripartite synapse** is a key concept in computational neuroscience. Many neural network models now include an "astrocyte" layer that gates plasticity and modulates excitability.
- **Activity-dependent myelination** has inspired AI models of "learnable network topology" — where the *structure* of the network adapts, not just the weights.
- **Microglia-inspired pruning** is used in *lottery ticket hypothesis* and *neural architecture search* — finding sparse sub-networks that work as well as dense ones.
- **Glia-like metabolic support** is the role of *off-chip memory* or *memory hierarchies* in modern computers — slower, denser storage that supports fast CPU computation.
- **Neuromorphic chips** (Loihi, TrueNorth) have not yet fully integrated glia-like elements. This is a research frontier.

**Why this matters for AI:** Most AI research focuses on the "computation" — neurons and their weights. But in biology, *most* of the cells are doing other things: providing energy, clearing waste, modulating signals, maintaining structure. If we want brain-like AI, we may need brain-like infrastructure: agents that manage resources, prune unused pathways, and supply metabolic support. This is more analogous to a multi-agent system than a single deep network.

**Connection to next file:** Glia set the stage. The main computational tissue of the brain is the *cortex* — a 2-3 mm thick sheet of neurons covering the surface of the cerebrum. The next file explores the cortex's structure and function.

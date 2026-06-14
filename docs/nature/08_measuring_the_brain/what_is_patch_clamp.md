# What Is Patch Clamp Recording?

**The Problem:** To understand how the brain works, you need to understand *how individual molecules* work. How does a single ion channel open and close? How does a single synapse release neurotransmitter? You need a tool that can measure the *electrical current* flowing through a *single protein* in *real time*. The patch clamp is that tool.

**Definition:** *Patch clamp recording* is an electrophysiology technique that measures the ionic currents flowing through *individual ion channels* (or the whole cell) using a glass micropipette sealed onto a small patch of cell membrane. Developed by Neher and Sakmann in the late 1970s (Nobel Prize 1991), it is the *gold standard* for studying ion channel biophysics, synaptic transmission, and neuronal excitability.

**How It Works (Step-by-Step):**

1. **The micropipette.** A glass capillary tube is heated and pulled to a fine tip (~1 μm diameter) using a micropipette puller. The tip is filled with an electrolyte solution similar to intracellular fluid. A wire electrode connects the solution to a sensitive amplifier.
2. **The gigaseal.** The pipette is brought into contact with the cell membrane. Slight suction is applied. The membrane forms a *tight seal* with the glass — electrical resistance 1-100 gigaohms (10⁹-10¹¹ Ω). This is the *gigaseal* — the breakthrough that made the patch clamp possible. It dramatically reduces electrical noise.
3. **Recording configurations.**
   - **Cell-attached:** the pipette is sealed onto the cell. Records currents through the channels in the patch. The cell is intact. The intracellular side is undisturbed.
   - **Whole-cell:** the membrane patch under the pipette is ruptured (by suction or voltage). The pipette solution equilibrates with the cytoplasm. Now you can record the *summed* currents of all channels in the cell, or *clamp the voltage* of the whole cell.
   - **Inside-out:** the pipette is withdrawn; the patch is excised with the intracellular side facing the bath. You can change the intracellular solution.
   - **Outside-out:** the pipette is withdrawn from a whole-cell configuration; the patch reforms with the extracellular side facing out. You can change the extracellular solution.
4. **Voltage clamp vs. current clamp.**
   - **Voltage clamp:** the experimenter *holds the voltage* constant and measures the current needed to maintain it. Used to study ion channels (current = function of voltage and time).
   - **Current clamp:** the experimenter *injects current* and measures the resulting voltage change. Used to study action potentials, synaptic potentials, subthreshold integration.
5. **What you can measure.**
   - **Single-channel currents:** ~1-10 pA. Channels have *unitary conductance* (e.g., a single BK channel: ~100 pS).
   - **Channel gating:** open probability, open/closed times, kinetics. Reveals the *mechanism* of channel opening.
   - **Ion selectivity:** which ions pass through.
   - **Pharmacology:** how drugs block or modulate channels.
   - **Whole-cell currents:** the *sum* of all channels in the cell.
   - **Action potentials:** in current clamp.
6. **Single-channel recording — the breakthrough.** Before the patch clamp, ion channel currents were inferred from *macroscopic* currents (many channels at once). The patch clamp made it possible to record *single* channels. Neher and Sakmann (1976) showed the first single-channel currents. Discovery: ion channels *open and close stochastically* — they are *discrete* events, not continuous.
7. **Variations and modern methods.**
   - **Automated patch clamp:** robotic systems (e.g., Nanion, Sophion) screen compounds on ion channels in high-throughput. Used in drug discovery.
   - **Planar patch clamp:** cells are positioned on a chip with a microhole, not a pipette. Higher throughput.
   - **Dynamic clamp:** combines patch clamp with computer simulation. The computer reads the cell's voltage and injects current simulating a virtual ion channel. Used to study channel effects on cellular dynamics.
   - **Patch-seq:** combines patch clamp with single-cell RNA sequencing. Record the electrophysiology of a neuron, then sequence its transcriptome. Used to link cell types to firing patterns.
8. **Advantages.** Single-channel resolution. High signal-to-noise (gigaseal). Direct measurement. Real-time kinetics. Multiple configurations.
9. **Limitations.** Technically demanding (the gigaseal is hard to form). Low throughput. Cells must be accessible (in vitro or slice). The pipette *dialyzes* the cell (in whole-cell mode) — replaces cytoplasm with pipette solution, which can perturb the cell.

**Real-life analogy:** The patch clamp is like a *stethoscope for a single cell*. Not a single ion — a *single molecule*. You can hear the channel open and close. You can hear which ion flows through. You can hear a drug bind. It's the most direct way to eavesdrop on the molecular machinery of the brain.

**Tiny numeric example:** A typical patch clamp experiment on a single BK channel:
- Pipette resistance: ~5 MΩ
- Seal resistance: ~10 GΩ (2000× better)
- Single-channel current: ~10 pA (at +60 mV, ~140 mM K⁺ inside)
- Channel conductance: ~250 pS
- Open probability: ~0.5 (at +60 mV, 10 μM Ca²⁺)
- Mean open time: ~1 ms
- Mean closed time: ~1 ms
- Total recording duration: ~10-30 minutes (gigaseal is fragile)
- Solution exchange time: ~50 ms (with rapid perfusion)
- Drugs tested: typically 3-5 concentrations × 3-5 cells = ~20 trials
- Throughput: ~1-3 successful patches per day per experimenter (highly skilled)

**Common confusion:**

- No. "Patch clamp measures the action potential." Yes, in current clamp, but the *unitary* event is the *single channel*. The action potential is the *sum* of many channels.
- No. "Patch clamp = sharp electrode." No. Sharp electrodes penetrate the cell; patch clamp seals onto the surface (without penetration, in cell-attached). The gigaseal is the key innovation.
- No. "Patch clamp can be done on any cell." Mostly yes, but the cell must be accessible. Whole-cell patch is *invasive* in that the membrane is ruptured.
- No. "Patch clamp is obsolete." No. It is still the *gold standard* for ion channel biophysics. Automated patch clamp (Sophion, Nanion) is used in drug screening for thousands of compounds.
- No. "Patch clamp is a single-channel technique." No. It can be single-channel, multi-channel, or whole-cell. The patch configuration determines what you see.

**Key properties:**

- **Single-channel resolution:** can see *one* ion channel at a time.
- **High signal-to-noise:** gigaseal reduces noise ~1000×.
- **Real-time:** microsecond resolution.
- **Direct:** measures current directly.
- **Versatile:** cell-attached, whole-cell, inside-out, outside-out.
- **Demanding:** requires skilled experimenter; gigaseal is fragile.
- **Low throughput:** ~1-3 successful patches per day.
- **Invasive (whole-cell):** dialyzes cytoplasm.

**Where it appears in technology:**

- **Drug discovery:** automated patch clamp screens thousands of compounds on cardiac (hERG) and neuronal ion channels. Critical for drug safety.
- **Neuroscience research:** the *gold standard* for studying synaptic transmission, ion channel biophysics, neuronal excitability.
- **Pharmacology:** characterizing drug action on specific channels.
- **AI for patch analysis:** machine learning detects and classifies channel openings.
- **Synthetic biology:** engineering new ion channels (e.g., for optogenetics) and characterizing them with patch clamp.
- **Brain-computer interfaces:** the first Neuralink-style BCIs used patch-clamp-like recordings (now replaced by multi-electrode arrays).

**Connection to next file:** Patch clamp records neurons — it tells us what the brain is *doing* at the molecular level. But it is *invasive* and *observational*. To *control* neurons with light, you need *optogenetics*. The next file covers the technique that revolutionized neuroscience in the 2010s.

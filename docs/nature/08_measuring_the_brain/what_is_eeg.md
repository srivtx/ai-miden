# What Is EEG (Electroencephalography)?

**The Problem:** You want to know what the brain is doing — right now, in real time. fMRI is too slow (seconds). Single-unit recording requires opening the skull. You need a *non-invasive*, *fast* way to see brain activity. The oldest, cheapest, fastest tool is **EEG**.

**Definition:** *Electroencephalography* (EEG) is a non-invasive technique that records the *electrical activity* of the brain from electrodes placed on the scalp. It measures the *summed postsynaptic potentials* of millions of cortical pyramidal neurons. Time resolution: ~1 ms. Spatial resolution: poor (~1-3 cm). Cost: low.

**How It Works (Step-by-Step):**

1. **The setup.** Electrodes (usually 19-256) are placed on the scalp using a conductive gel or paste. Each electrode picks up the voltage difference between itself and a reference. A differential amplifier amplifies the signal (typically 1,000-100,000×). The signal is digitized and recorded.
2. **What does EEG actually measure?** Pyramidal neurons of the cortex are aligned in parallel. When they fire together (synchronously), their postsynaptic potentials sum. EEG picks up the *summed* activity of millions of neurons in a region. The signal is dominated by *dendritic* currents, not action potentials.
3. **The frequency bands.** The EEG signal oscillates at characteristic frequencies:
   - **Delta (0.5-4 Hz):** deep sleep
   - **Theta (4-8 Hz):** drowsiness, memory encoding (especially hippocampus)
   - **Alpha (8-13 Hz):** relaxed wakefulness, eyes closed
   - **Beta (13-30 Hz):** active thinking, alertness
   - **Gamma (30-100 Hz):** perception, attention, consciousness
   - **High-frequency oscillations (100-200 Hz):** local processing, memory
4. **The 10-20 system.** Electrodes are placed at standard positions (F = frontal, C = central, P = parietal, T = temporal, O = occipital). The "10-20" refers to the 10% or 20% of head circumference distances. International standard.
5. **Event-related potentials (ERPs).** When a stimulus is presented repeatedly, the EEG response *time-locked* to the stimulus can be averaged. This extracts the *event-related* signal from the noise. ERPs have characteristic components (N100, P200, N400, P300, etc.) associated with specific cognitive processes.
6. **Clinical use.** EEG is the *gold standard* for diagnosing epilepsy. It can also:
   - Distinguish seizure types (focal vs. generalized)
   - Detect sleep disorders (polysomnography)
   - Assess brain death
   - Monitor depth of anesthesia
   - Diagnose encephalopathies
   - Monitor during surgery
7. **Research use.** EEG is fundamental in cognitive neuroscience:
   - ERP components index perception, attention, memory, language.
   - Oscillation analysis (power, phase, coherence) reveals neural coordination.
   - Event-related spectral perturbation (ERSP) shows how oscillations change with task.
   - Connectivity analysis (phase-locking value, Granger causality) reveals network interactions.
8. **Advantages.** Cheap, fast, non-invasive, silent, well-tolerated, mobile, works in clinical and field settings. Excellent temporal resolution (~1 ms). Can detect *covert* processing (in unresponsive patients, infants).
9. **Limitations.** Poor spatial resolution. The *inverse problem* — given the scalp voltage, where is the source? (Mathematically ill-posed. Many possible source configurations give the same scalp pattern.) Sensitive to noise (muscle, eye blinks, electrical). Cannot measure deep brain structures.
10. **MEG (magnetoencephalography).** An alternative: measures the *magnetic* fields produced by neural currents. Better spatial resolution (especially for tangential sources). Much more expensive (requires liquid helium-cooled SQUIDs). Same temporal resolution as EEG.

**Real-life analogy:** EEG is like listening to a *stadium* from outside. You hear the roar of the crowd (overall activity) and can detect big events (a goal, a fight). But you can't tell which individual fans are clapping, what they're saying, or even exactly where they're sitting. The information is *there*, but you need to interpret it carefully.

**Tiny numeric example:** A typical EEG recording:
- 64 channels (electrodes)
- Sampling rate: 1,000 Hz (1 ms resolution)
- Signal amplitude: 10-100 μV
- Noise (60 Hz power line, muscle): up to 1 mV
- Signal-to-noise ratio: ~1:10
- A single ERP component (e.g., P300) is typically ~5-20 μV, embedded in background noise
- Requires ~30-100 trials averaged to extract
- Spatial resolution: ~1-3 cm (depends on source localization method)
- Cost: $5,000-$100,000 (clinical to research)
- Time to set up: 30-60 min
- Patient tolerance: high (especially for ambulatory EEG)

**Common confusion:**

- No. "EEG measures brain waves." Yes, in a sense. The "waves" are *summed* postsynaptic potentials. Not individual action potentials.
- No. "EEG can read thoughts." No. It can detect attention, perception, language processing at a coarse level. Not specific thoughts.
- No. "EEG has good spatial resolution." No. ~1-3 cm. fMRI is much better (~2-3 mm). For *when*, EEG. For *where*, fMRI.
- No. "EEG is outdated." No. EEG is *complementary* to fMRI. Modern "closed-loop" BCI systems use EEG in real-time. EEG + fMRI + TMS is a powerful combination.
- No. "Alpha waves mean relaxation." Yes, but the *source* of alpha is debated. It may reflect *inhibition* of task-irrelevant areas, not just "relaxation."
- No. "EEG can diagnose all brain disorders." No. It is excellent for *epilepsy* and *sleep*. Less so for psychiatric disorders (where fMRI is more informative).

**Key properties:**

- **Non-invasive:** electrodes on the scalp.
- **Fast:** millisecond resolution.
- **Cheap:** low cost compared to fMRI, MEG, PET.
- **Portable:** can be done at bedside, in the field.
- **Direct:** measures electrical activity (not a proxy like BOLD).
- **Poor spatial resolution:** ~1-3 cm.
- **Inverse problem:** mathematically ill-posed source localization.
- **Frequency-rich:** oscillatory activity at multiple bands.

**Where it appears in technology:**

- **Brain-computer interfaces (BCI):** EEG-based spellers, cursors, prosthetic control. The most common BCI modality.
- **Clinical monitoring:** ICU, operating room, sleep labs.
- **Epilepsy diagnosis:** gold standard.
- **Closed-loop neurofeedback:** train subjects to modulate their own brain activity (e.g., for ADHD, anxiety).
- **Consumer EEG:** Muse, Emotiv, OpenBCI — low-cost EEG for meditation, gaming, research.
- **AI for EEG analysis:** deep learning decodes EEG signals for BCI, seizure detection, sleep staging, emotion recognition.
- **AI neuroscience:** EEG is used to study the *internal representations* of ANNs (e.g., aligning deep network features with EEG responses).

**Connection to next file:** EEG measures *when* the brain does X. Patch clamp measures *how* the brain does X — at the level of single ion channels. The next file covers the technique that won the 1991 Nobel Prize.

# What Is the Visual System?

**The Problem:** The visual system is the brain's most studied and most complex sensory system. About 30% of the human cortex is involved in vision. From the moment light hits the retina to the moment you "see" your grandmother's face, the signal passes through dozens of processing stages. How does the brain extract meaning from a flood of photons?

**Definition:** The *visual system* is the network of neural structures that processes visual information: retina → lateral geniculate nucleus (LGN) of the thalamus → primary visual cortex (V1) → extrastriate areas (V2, V3, V4, V5/MT) → inferior temporal cortex (IT) → prefrontal cortex. It is the canonical example of a hierarchical sensory system.

**How It Works (Step-by-Step):**

1. **The retina.** Light hits ~125 million photoreceptors (rods and cones). Photoreceptors transduce light into graded electrical signals. These signals pass through:
   - **Bipolar cells** (~15 types, ON and OFF)
   - **Retinal ganglion cells** (~20 types) — the *output* neurons of the retina
   - The signal is *already processed* in the retina. It is not a raw camera output.
   - **Center-surround receptive fields:** Retinal ganglion cells respond to a *difference* between light in the center and the surround of their receptive field. This is edge detection.

2. **The optic nerve and chiasm.** ~1 million retinal ganglion cell axons form the optic nerve. At the optic chiasm, fibers from the nasal half of each retina cross to the other side. This means each hemisphere sees the *contralateral* visual field. ~90% of retinal axons go to the LGN; the rest go to the superior colliculus (eye movements), pretectum (pupil reflex), and suprachiasmatic nucleus (circadian).

3. **LGN (Lateral Geniculate Nucleus).** The thalamic relay for vision. Six layers in primates:
   - Layers 1, 4: Magnocellular (M) — fast, low spatial resolution, high temporal resolution. Motion and depth.
   - Layers 2, 3, 5, 6: Parvocellular (P) — slower, high spatial resolution, color.
   - The LGN receives massive feedback from V1 (~10× more corticothalamic than thalamocortical fibers in some accounts). The LGN is not a passive relay — V1 controls what gets through.

4. **V1 — primary visual cortex.** The first cortical processing area. Hubel and Wiesel's work (1959-1981) revealed:
   - **Simple cells:** Respond to oriented edges at specific positions. They are the building blocks of edge detection.
   - **Complex cells:** Respond to oriented edges regardless of exact position (translation-invariant). Pool over simple cells.
   - **Hypercomplex cells:** Respond to corners, line endings, curvature.
   - **Orientation columns:** V1 is organized in columns, each tuned to a specific orientation (0°, 45°, 90°, etc.). Adjacent columns have slightly different orientations. The full 0-180° range is represented across ~1-2 mm of cortex.
   - **Ocular dominance columns:** Alternating columns preferring input from the left vs. right eye.
   - **Retinotopic map:** V1 preserves the spatial layout of the retina. The center of the visual field (fovea) has the largest representation.
   - V1 also has *blobs* — clusters of color-sensitive cells — interleaved with orientation columns.

5. **V2 — secondary visual cortex.** Receives from V1. Has its own columnar organization. Sensitive to:
   - **Contours and illusory contours** (subjective edges)
   - **Relative position** of features
   - **Texture** differences

6. **V4 — color and shape.** Sensitive to color, shape, and form. Lesions cause achromatopsia (loss of color vision) and shape agnosia. Contains the "famous" *infant face* cells, *rectangle* cells, etc.

7. **V5/MT — motion.** Specialized for motion detection. Lesions cause akinetopsia (inability to see motion). Contains direction-selective columns.

8. **Inferior Temporal (IT) cortex — objects and faces.** The "high-level" visual cortex. IT neurons are selective for complex objects:
   - **Face cells** (in humans, the fusiform face area, FFA): respond selectively to faces.
   - **Place cells** (parahippocampal place area, PPA): respond to scenes.
   - **Body cells** (extrastriate body area, EBA): respond to body parts.
   - IT is the end of the ventral "what" stream (V1 → V2 → V4 → IT).

9. **The two streams.** Ungerleider and Mishkin (1982) proposed the two visual streams:
   - **Ventral stream (the "what" pathway):** V1 → V2 → V4 → IT. Object identification, color, form.
   - **Dorsal stream (the "where" / "how" pathway):** V1 → V2 → MT → parietal cortex. Spatial location, motion, action.
   - Lesions to the dorsal stream cause *optic ataxia* (can't reach for objects under visual guidance). Lesions to the ventral stream cause *visual agnosia* (can't identify objects).

10. **Predictive coding in vision.** Rao and Ballard (1999) showed that V1 can be modeled as a hierarchical predictive coding network: each level predicts the level below; the difference is the *prediction error* that propagates upward. Top-down feedback carries predictions; bottom-up feedforward carries errors. This is the most influential model of cortical visual processing.

11. **Time course.** Visual processing is fast. Simple features are extracted in ~50-100 ms. Object identification takes ~150-200 ms. Face recognition in familiar faces can be as fast as ~100 ms. Conscious visual perception ("I see a face") emerges at ~200-300 ms.

**Real-life analogy:** The visual system is a *factory assembly line*. Raw materials (light) enter at one end (retina). Each station (LGN, V1, V2, V4, IT) performs one stage of processing. The output is a labeled, located, motion-tracked representation of the world. But unlike a simple assembly line, the higher stations send *predictions* back to the lower stations, which are continuously compared to the input. The brain is not just processing — it is *verifying its predictions*.

**Tiny numeric example:** The retina has ~125 million photoreceptors but only ~1 million retinal ganglion cells. The LGN has ~1-2 million neurons (one per retinal ganglion cell). V1 has ~200-300 million neurons in humans. V1 occupies ~15% of the total cortical surface area (~100 cm² in each hemisphere). A single V1 hypercolumn processes ~1-2° of visual angle. The whole visual field (~180°) is processed by ~100,000 hypercolumns. The "face area" (FFA) is a few square centimeters of cortex with millions of neurons. A face-selective neuron can fire at 50-100 Hz in response to a face, ~0 Hz for a non-face object.

**Common confusion:**

- No. "The eye is like a camera." It is more like a *preprocessed camera*. The retina already extracts edges, motion, and contrast. The "pixels" reaching the brain are not raw intensity.
- No. "The visual cortex is for vision only." It also participates in imagination, dreaming, and visual working memory. *Visual* imagery uses the same areas as visual perception.
- No. "V1 is a simple feature detector." V1 is much more than that. It performs predictive coding, top-down modulation, attention filtering, and contextual processing.
- No. "Face cells only fire for faces." Some face cells also fire for other round, symmetric objects (apples, clocks). They are *face-selective*, not *face-specific*. The selectivity is graded.
- No. "The two streams are completely separate." No. There is extensive cross-talk between ventral and dorsal streams. The strict dichotomy is a simplification.
- No. "We see with our eyes." We see with our *cortex*. The eyes are sensors. Perception is a cortical construction. Eyes closed, you can still "see" (in dreams, imagination).

**Key properties:**

- **Hierarchical:** V1 → V2 → V4 → IT. Each level processes more complex features.
- **Retinotopic:** Spatial layout is preserved.
- **Columnar:** Orientation, ocular dominance, motion direction all organized in columns.
- **Predictive:** Top-down predictions and bottom-up errors.
- **Fast:** Object recognition in ~200 ms.
- **Plastic:** Can adapt to retinal implants, prism goggles, sensory substitution.
- **Two streams:** "What" (ventral) and "where/how" (dorsal).

**Where it appears in technology:**

- **Convolutional Neural Networks (CNNs)** are the most direct AI analog. LeNet, AlexNet, VGG, ResNet all model the hierarchical organization of visual cortex (Fukushima's Neocognitron, 1980, was the first).
- **Deep learning's "deep" hierarchies** are inspired by the multi-level visual hierarchy.
- **Transfer learning** in vision (pretraining on ImageNet, fine-tuning) is loosely analogous to how the ventral visual stream learns general features that apply to many objects.
- **Capsule networks** (Hinton et al., 2017) attempt to model the "what" and "where" of objects separately, inspired by the two streams.
- **Vision Transformers (ViTs)** are a different approach: attention-based, not strictly hierarchical. But many ViTs still process visual data in a roughly hierarchical way.
- **Predictive coding networks** (Rao & Ballard, 1999) are biologically-inspired models of the visual system. They are a top-down predictive hierarchy.
- **Contrastive learning** (SimCLR, MoCo, DINO) is a self-supervised approach that has parallels with predictive coding — learning by predicting parts of the input from other parts.

**Why this matters for AI:** The visual system is the *best-studied* cortical system. Most of what we know about cortical processing comes from vision. Modern computer vision is a direct descendant of Hubel and Wiesel's discoveries. The visual system also illustrates the key principles of cortical computation: hierarchy, prediction, error, top-down modulation, two streams, and columnar organization. These principles generalize to other modalities (audition, language, reasoning).

**Connection to next file:** The visual system shows the brain's hierarchical, predictive organization. But the brain does not process all input equally — it *selects* what to focus on. The next file explores *attention* — the brain's mechanism for selective processing.

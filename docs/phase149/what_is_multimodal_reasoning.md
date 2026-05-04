## What Is Multimodal Reasoning?

---

### The Problem

You have retrieved a text paragraph, an X-ray image, and a doctor's audio note. Each piece of evidence is relevant to the patient's case. But now the model must answer: 'Does the combination of these three sources suggest a bacterial or viral infection?' This is not a retrieval problem anymore. The model must read the text, interpret the image, listen to the audio, and fuse all three into a single coherent inference. Each modality has different noise patterns, different levels of reliability, and different types of ambiguity. How do you reason across them without being misled by any single source?

---

### Definition

**Multimodal reasoning** is the process of combining information from multiple modalities — text, images, audio, video — to draw conclusions that no single modality could support alone. It requires not just retrieving the right pieces, but weighing their evidence, resolving conflicts between them, and producing a unified answer.

**How it differs from single-modal RAG:**
```
Single-modal RAG:
  Query -> retrieve text chunks -> read text -> answer
  (one source type, linear pipeline)

Multimodal reasoning:
  Query -> retrieve text + image + audio -> read all three
    -> detect conflict: text says 'mild', image shows 'severe'
    -> weigh evidence: audio has highest confidence
    -> synthesize answer that accounts for all three
  (multiple source types, non-trivial fusion)
```

**Why this is harder:**
- **Modality-specific hallucinations:** a vision model might misread a chart; a text model might misinterpret a drug name; an audio model might mistranscribe a number
- **Conflicting evidence:** the text report says 'no fracture' but the X-ray shows a hairline crack; the model must resolve the contradiction
- **Different granularities:** text is sequential and explicit; images are spatial and implicit; audio is temporal and prosodic. Fusion requires handling these structural mismatches
- **Attribution:** the model must explain which modality supported which part of its answer, or users cannot trust it

---

### Real-Life Analogy

A jury deliberating a trial.
- **Single-modal reasoning:** The jury only reads the written police report. They miss the body language of the witness on the stand, the tone of the 911 call, and the physical evidence photographs. Their verdict is based on one filtered narrative.
- **Multimodal reasoning:** The jury hears the witness testify (audio + visual), sees the crime-scene photos (image), reads the forensic report (text), and watches the surveillance footage (video). They must weigh a shaky eyewitness account against clear DNA evidence. They must notice that the witness's voice trembles when asked about the timeline. They must reconcile the defendant's calm demeanor in court with the violent images. The final verdict is an integrated judgment, not a vote count across modalities.
- **The failure mode:** If one juror fixates only on the photos and ignores the alibi in the text, the reasoning is broken. Multimodal reasoning requires balanced attention and conflict resolution.

---

### Tiny Numeric Example

**Evidence for a diagnosis from three modalities:**
```
Text (patient record): "Fever 38.5C, cough, fatigue. No chest pain."
  -> Text model confidence: bacterial = 0.40, viral = 0.45, unknown = 0.15

Image (chest X-ray): shows diffuse bilateral infiltrates
  -> Image model confidence: bacterial = 0.70, viral = 0.20, unknown = 0.10

Audio (doctor's note): "Sounds like walking pneumonia, but symptoms are atypical."
  -> Audio model confidence: bacterial = 0.35, viral = 0.40, unknown = 0.25
```

**Naive averaging (dangerous):**
```
bacterial = (0.40 + 0.70 + 0.35) / 3 = 0.483
viral     = (0.45 + 0.20 + 0.40) / 3 = 0.350
→ Predict bacterial
```

**Weighted by modality reliability (better):**
```
Text reliability weight:  0.30 (patient often omits details)
Image reliability weight: 0.50 (X-ray is objective but requires expertise)
Audio reliability weight: 0.20 (doctor is uncertain themselves)

bacterial = 0.30*0.40 + 0.50*0.70 + 0.20*0.35 = 0.540
viral     = 0.30*0.45 + 0.50*0.20 + 0.20*0.40 = 0.305
→ Still bacterial, but confidence is properly calibrated
```

**Conflict-aware reasoning (best):**
```
The text says "no chest pain" which typically argues against bacterial pneumonia.
The image shows infiltrates which strongly argues for bacterial pneumonia.
The audio says "atypical" which argues for caution.

Resolution: The image evidence is the strongest objective signal. The absence
of chest pain does not rule out bacterial infection in elderly patients.
The doctor's uncertainty justifies ordering a sputum culture for confirmation.

→ Preliminary diagnosis: bacterial pneumonia (moderate confidence).
→ Recommended action: start empiric antibiotics + culture confirmation.
```

**The shift:** Multimodal reasoning is not voting. It is weighing, conflict detection, and calibrated synthesis. The image overrode the text not because images are always better, but because in this specific clinical context, radiographic evidence has higher diagnostic value than self-reported symptoms.

---

### Common Confusion

1. **"Multimodal reasoning is just concatenating text descriptions of images with the text prompt."** Concatenation is the input format, not the reasoning process. True multimodal reasoning requires the model to resolve conflicts, weigh reliabilities, and handle modality-specific nuances. Concatenation alone does none of that.

2. **"More modalities always improve accuracy."** Not if one modality is noisy or irrelevant. Adding a low-quality audio transcript can mislead the model. Multimodal reasoning requires the ability to ignore or downweight unreliable modalities.

3. **"The model should trust the most confident modality."** Confidence calibration differs across modalities. A vision model might output extreme probabilities (0.99) for uncertain images due to overconfidence, while a text model outputs conservative probabilities. Raw confidence is not directly comparable.

4. **"Multimodal reasoning requires a single giant model that natively sees all modalities."** Many production systems use separate expert models per modality and a fusion layer (or an LLM with tool use) that receives structured outputs from each expert. This modular approach is often more robust than a monolithic model.

5. **"If retrieval is perfect, reasoning is easy."** Even perfectly retrieved evidence can be contradictory or ambiguous. The reasoning challenge is independent of retrieval quality. Good retrieval gives you the right pieces; good reasoning assembles them correctly.

6. **"Attention mechanisms automatically handle multimodal fusion."** Cross-attention can combine modalities, but it does not automatically learn to detect conflicts, calibrate confidence, or reason about causal relationships. Those capabilities require task-specific training or explicit architectural design.

7. **"Multimodal reasoning is only needed for medical or legal domains."** Everyday questions require it too: 'Is this restaurant good?' requires reading reviews (text), looking at photos of the food (image), and possibly hearing the noise level in a video review (audio). Any complex real-world judgment draws on multiple senses.

---

### Where It Is Used in Our Code

`src/phase149/phase149_multimodal_rag_concepts.py` — We simulate three modalities (text, image, audio) providing conflicting evidence for a set of queries. We show that naive averaging produces wrong answers when modalities disagree, while weighted fusion — calibrated by modality reliability — improves accuracy. We visualize the conflict-resolution process.

`src/phase149/phase149_multimodal_rag_colab.py` — After retrieving relevant items across modalities, we use a language model to perform multimodal reasoning over the retrieved context. We compare answers generated from text-only retrieval versus multimodal retrieval, showing that cross-modal evidence changes the conclusion in cases of single-modal ambiguity.

(End of file - total 97 lines)

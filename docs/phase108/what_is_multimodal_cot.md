## What Is Multimodal Chain-of-Thought (CoT)?

---

### The Problem

Complex problems rarely have a single-step solution. A math diagram might require reading numbers, applying formulas, and checking units. A single forward pass through a multimodal model often jumps straight to the answer, missing subtle relationships between what is seen and what is asked. The model might see a triangle, read the question, and guess the area formula without verifying the base and height from the image. How do you make the model think step-by-step across both vision and language before committing to an answer?

---

### Definition

**Multimodal Chain-of-Thought** extends text-based chain-of-thought prompting to vision-language models. The model generates intermediate reasoning steps that interleave visual observations with textual deductions, leading to a final answer through explicit reasoning rather than implicit pattern matching.

**How it works:**
```
Step 1 (Vision):  "The triangle has base = 5 and height = 3"
Step 2 (Text):    "Area of triangle = 0.5 * base * height"
Step 3 (Vision):  "The units are in centimeters"
Step 4 (Text):    "Area = 0.5 * 5 * 3 = 7.5 cm²"
Result: structured reasoning with verified visual facts
```

**Key techniques:**
- **Interleaved generation:** alternating visual observations and textual inferences within a single reasoning chain
- **Cross-modal attention refresh:** at each reasoning step, the text decoder queries relevant image patches to verify visual facts
- **Self-consistency:** generating multiple reasoning chains and voting on the most frequent final answer

**Why this matters:**
- It reduces errors on visual math and science benchmarks by 15-25%
- It makes the model's reasoning inspectable, not just its final answer
- It mirrors how humans solve problems: look, think, look again, revise

---

### Real-Life Analogy

Multimodal CoT is like a detective solving a case. The detective looks at a crime scene photo and notes details: "The window is broken from the outside." They read a witness statement: "I heard a noise at midnight." They look back at the photo: "The footprint outside matches the broken glass pattern." Each step alternates between visual evidence and textual inference, building a chain of reasoning that leads to a conclusion.

The trade-off is that long reasoning chains accumulate errors. One misidentified visual detail -- a footprint that is actually a gardening tool mark -- can derail the entire chain. The detective must verify each observation before proceeding. Similarly, a multimodal model that hallucinates a diagram detail in step 2 will propagate that error through subsequent steps. Shorter, verified chains are often more reliable than longer, speculative ones.

---

### Tiny Numeric Example

**Problem:** Image shows a triangle with base 5 and height 3. Question: "What is the area?"

**Single-step model (no CoT):**
```
Output: "7" (wrong unit, no reasoning shown)
Confidence: 0.68
Correct: No
```

**Multimodal CoT model:**
```
Step 1 (Vision): Base = 5, Height = 3
Step 2 (Text): Formula = 0.5 * base * height
Step 3 (Calculation): 0.5 * 5 * 3 = 7.5
Final answer: "7.5"
Correct: Yes
```

**Accuracy comparison on 100 visual math problems:**
```
Single-step model:         52/100 correct (52%)
Multimodal CoT model:      71/100 correct (71%)
```

**Error analysis:**
```
Single-step errors:  38% formula confusion, 31% unit mistakes, 31% misread values
CoT errors:          19% formula confusion, 12% unit mistakes, 69% misread values
```

CoT eliminates most formula and unit errors by making reasoning explicit, though misreading visual details remains a challenge.

---

### Common Confusion

1. **"Multimodal CoT is just concatenating vision and text outputs."** It requires a unified architecture where attention flows between modalities during the generation of each reasoning step, not separate pipelines joined at the end.

2. **"It eliminates all reasoning errors."** It reduces errors but can amplify them if an early visual observation is wrong, causing cascading mistakes through subsequent steps.

3. **"You need a separate vision model for each step."** Most implementations reuse the same vision encoder, refreshing cross-modal attention at each generation step rather than re-running the encoder.

4. **"Multimodal CoT is only for math problems."** It helps any task requiring structured reasoning over visuals, including science diagrams, navigation, mechanical troubleshooting, and medical imaging interpretation.

5. **"Longer reasoning chains are always better."** Beyond 5-8 steps, diminishing returns set in, and models start generating redundant or contradictory steps that increase error rates.

6. **"The visual observations are always accurate."** Models can hallucinate visual details, especially with small, ambiguous, or low-resolution diagrams.

7. **"Multimodal CoT requires labeled reasoning data."** While supervised fine-tuning helps, few-shot prompting with text-only chain-of-thought examples can induce multimodal reasoning in capable base models.

---

### Where It Is Used in Our Code

`src/phase108/phase108_multimodal_reasoning.py` — We simulate cross-modal attention between image patches and text tokens, showing how visual features are dynamically retrieved for each text token. This mechanism is the foundation of multimodal CoT: at each reasoning step, the text decoder queries relevant image patches to verify visual facts before generating the next inference.

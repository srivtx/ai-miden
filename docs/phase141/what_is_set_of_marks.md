## What Is Set-of-Marks Prompting?

---

### The Problem

Even the best vision-language models struggle with precise visual grounding. Ask a model to "click the second button in the third row" and it may hallucinate coordinates, confuse rows, or misinterpret the button's function. The gap between understanding an image and acting on it is wide. How do you give the model an unambiguous map from its language understanding to exact UI elements?

---

### Definition

**Set-of-marks prompting** is a technique where clickable or interactable elements on a screen are overlaid with visible labels (numbers, letters, or colored boxes) before the screenshot is fed to the model. Instead of predicting raw pixel coordinates, the model predicts a label, and a wrapper maps that label to the true coordinates. It converts a continuous regression problem into a discrete classification problem.

**How it works:**
```
Original screenshot:
  [Button: Save]  [Button: Cancel]  [Input: username]

Set-of-marks overlay:
  [1: Save]     [2: Cancel]     [3: username]

Model prompt:
  "You see a form. Click the element that submits it."

Model output:
  "click(1)"

Wrapper execution:
  label 1 → bounding box of Save button → click(center_of_box)
```

**Accessibility tree vs. screenshot:**
- **Screenshot + set-of-marks:** The model sees the actual rendered pixels. It handles custom styling, dynamic content, and visual layout. It is robust to non-standard HTML but consumes more tokens.
- **Accessibility tree:** The model receives a structured XML or JSON representation of UI elements (roles, labels, bounds). It is compact and precise but fails when developers omit accessibility metadata or build custom canvases.

**Why this matters:**
- Set-of-marks reduces coordinate hallucination by an order of magnitude.
- It allows smaller models to perform GUI tasks because the action space shrinks from millions of pixels to tens of labels.
- It is the secret sauce behind many production computer-use systems.

---

### Real-Life Analogy

A museum audio guide with numbered plaques vs. a guide that describes paintings by location.
- **Raw screenshot (describe by location):** The guide says, "Look at the painting three meters to your left, near the pillar." You might look at the wrong painting, especially if the room is crowded or the pillar is ambiguous.
- **Set-of-marks (numbered plaques):** Every painting has a red number next to it. The guide says, "Look at painting number seven." You find the 7, and there is no ambiguity. The number is an index into a lookup table that tells you exactly which painting, where it is, and how big it is.
- **Accessibility tree (catalog sheet):** Instead of being in the room, you receive a printed list: "Painting 7: 'Starry Night,' oil on canvas, 73.7 cm x 92.1 cm." It is precise and compact, but if a painting is missing from the list or the dimensions are wrong, you are lost.

---

### Tiny Numeric Example

**Task:** Click the "Delete" button in a toolbar with 8 icons.

**Without set-of-marks (coordinate prediction):**
```
Model output: click(x=342, y=128)
True center of Delete: (340, 130)
Distance: 2.8 pixels → Success.

But on 100 trials across different window sizes:
  Mean absolute error: 18.4 pixels
  Success rate (within 5 pixels): 34%
  Misclick rate: 66%
```

**With set-of-marks:**
```
Overlay labels: [1] [2] [3] [4] [5] [6] [7] [8]
Model prompt: "Click the label of the Delete icon."
Model output: "click(6)"
Wrapper maps label 6 → (340, 130) → click.

Success rate over 100 trials: 98%
The 2% failures are label misclassifications, not coordinate errors.
```

**Comparison:**
```
Method                  Action space size    Error type        Accuracy
Raw coordinates         1920 x 1080          pixel offset      34%
Accessibility tree      ~20 elements         missing element   71%
Set-of-marks            ~8 labels            label mismatch    98%
```

**The shift:** Moving from continuous coordinates to discrete labels trades spatial regression for classification. Classification is what language models do best.

---

### Common Confusion

1. **"Set-of-marks is just image captioning."** Captioning describes what is in the image. Set-of-marks overlays actionable indices so the model can *act* on what it sees, not just describe it.

2. **"The model needs to be retrained to understand labels."** Not necessarily. A standard vision-language model can read numbers and letters on an image. The overlay leverages the model's existing OCR capability without fine-tuning.

3. **"Set-of-marks works only for HTML pages."** It works for any rendered interface: desktop apps, mobile screens, PDF viewers, game HUDs. As long as you can detect interactive regions and draw labels, you can use the technique.

4. **"It replaces the need for an accessibility tree."** The two are complementary. Set-of-marks handles visual layout; accessibility trees provide semantic roles and hidden state. The best systems combine both.

5. **"More labels always help."** Too many labels clutter the screenshot and confuse the model. A good heuristic is to label only the top-k most salient interactive elements, or to group related items under a single label with a sub-menu.

6. **"The labels must be numbers."** Numbers are common because they are compact, but colors, letters, or even icons work. The only requirement is that the wrapper can map the model's prediction back to a unique region.

7. **"Set-of-marks fixes all visual grounding problems."** It fixes coordinate precision, but not higher-level reasoning errors. The model can still misidentify which label corresponds to the "Delete" button if the icons are ambiguous or the toolbar is unfamiliar.

---

### Where It Is Used in Our Code

`src/phase141/phase141_gui_agent_colab.py` — Instead of raw screenshots, we overlay DOM element IDs as set-of-marks labels on a text-based web environment. The agent predicts element IDs rather than pixel coordinates, and we measure how this discrete action space improves success rate on navigation and form-filling tasks compared to a coordinate-prediction baseline.

(End of file - total 99 lines)

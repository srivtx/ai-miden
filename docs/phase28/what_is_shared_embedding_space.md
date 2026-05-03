### 1. Why it exists (THE PROBLEM first)
Traditional AI systems process images and text in completely separate pipelines. An image model outputs "cat" and a text model outputs "meow," but there is no way to compare them or ask "is this image related to this sentence?" We need a common language — a single space where both modalities live — so that "cat" (text) and a photo of a cat (image) are neighbors.

### 2. Definition (very simple)
A Shared Embedding Space is a vector space where representations from different data types (like images and text) are mapped into the same coordinates. In this space, similar concepts cluster together regardless of their original modality. A picture of an apple and the word "apple" occupy nearby points.

### 3. Real-life analogy
A universal translator device at a United Nations meeting. The French delegate says "paix," the English delegate says "peace," and the Japanese delegate says "heiwa." The device translates all three into the same abstract concept code: #PEACE-2847. The code itself is meaningless to humans, but it means the same thing regardless of language. A shared embedding space is that concept code — a common coordinate system for all modalities.

### 4. Tiny numeric example

Text embedding for "dog": [0.8, -0.3, 0.5]
Image embedding for a dog photo: [0.75, -0.25, 0.55]
Image embedding for a cat photo: [-0.2, 0.9, 0.1]

Distance calculations:
- Dog text ↔ Dog image: sqrt((0.8-0.75)² + (-0.3+0.25)² + (0.5-0.55)²) = sqrt(0.0025 + 0.0025 + 0.0025) ≈ 0.087
- Dog text ↔ Cat image: sqrt((0.8+0.2)² + (-0.3-0.9)² + (0.5-0.1)²) = sqrt(1.0 + 1.44 + 0.16) ≈ 1.55

The dog text is 18x closer to the dog image than to the cat image. The shared space successfully aligned the modalities.

### 5. Common confusion
- **Shared space does not mean identical vectors.** The text vector for "dog" and the image vector for a dog photo are close but not the same. They are like synonyms in different languages — related, not identical.
- **Alignment requires training.** You cannot just concatenate a text model and an image model and hope their outputs match. CLIP trains both encoders jointly with a contrastive loss so they learn to speak the same vector language.
- **The space is high-dimensional.** CLIP uses 512 or 768 dimensions. You cannot visualize it directly, but dimensionality reduction (t-SNE, UMAP) can show clusters of related images and text.
- **More than two modalities can share space.** Audio, video, depth maps, and 3D point clouds can all be embedded into the same space. The concept generalizes beyond vision + language.
- **Nearest neighbors are semantic, not visual.** In the shared space, a photo of a dog and the text "loyal pet" might be closer than a photo of a dog and a photo of a wolf — because semantics matter more than raw pixels.

### 6. Where it is used in our code
`src/phase28/phase28_multimodal_ai.py` demonstrates a 3-dimensional shared embedding space where images of shapes and their text descriptions are projected into the same coordinates, and we visualize the alignment.

### 1. Why it exists (THE PROBLEM first)
Before CLIP, computer vision models were trained on expensive, hand-labeled datasets like ImageNet (1.2M labeled images). Creating these labels is slow and costly. Meanwhile, the internet has billions of image-caption pairs (from alt text, comments, and descriptions) that are already labeled by humans — just not for machine learning. CLIP asks: can we learn vision from these naturally occurring text descriptions?

### 2. Definition (very simple)
CLIP (Contrastive Language-Image Pre-training) is a model trained on 400 million image-text pairs from the internet. It learns to embed images and their corresponding captions into the SAME vector space, so that a photo of a dog and the text "a photo of a dog" are close together, while a photo of a cat and the text "a photo of a dog" are far apart.

### 3. Real-life analogy
A translator who grows up bilingual in English and Japanese. They do not memorize a dictionary; they simply understand that the English word "love" and the Japanese word "ai" point to the same feeling. CLIP does the same for images and text: it learns that a picture of an apple and the words "red fruit" point to the same concept, without anyone ever defining "apple" explicitly.

### 4. Tiny numeric example
Training batch with 3 image-text pairs:
- Image A + Text A: "a red circle"
- Image B + Text B: "a blue square"
- Image C + Text C: "a green triangle"

CLIP computes embeddings:
- Image A vector: [0.9, 0.1, 0.1]
- Text A vector:  [0.85, 0.15, 0.1]
- Similarity (A_image, A_text) = dot product = 0.9*0.85 + 0.1*0.15 + 0.1*0.1 = 0.79

- Image B vector: [0.1, 0.9, 0.1]
- Text A vector:  [0.85, 0.15, 0.1]
- Similarity (B_image, A_text) = 0.1*0.85 + 0.9*0.15 + 0.1*0.1 = 0.23

The contrastive loss pushes matching pairs together (0.79 → 1.0) and non-matching pairs apart (0.23 → 0.0).

After training, to classify a new image:
1. Embed the image
2. Embed candidate labels: "a photo of a cat", "a photo of a dog"
3. Pick the text with highest similarity to the image

### 5. Common confusion
- **CLIP is not a classifier.** It does not output "cat" or "dog" directly. It outputs a similarity score between an image and any text you provide. You can turn it into a classifier by giving it label descriptions.
- **Zero-shot classification means no training on those labels.** CLIP can classify breeds of dogs it has never explicitly been trained on, as long as it understands the text description. This is different from traditional classifiers that need thousands of examples per class.
- **CLIP does not generate images.** It only learns to match images with text. DALL-E and Stable Diffusion (which came later) use CLIP's text encoder to guide image generation.
- **It is sensitive to prompt engineering.** "a photo of a cat" might give different results than "a feline animal" because the text embeddings differ. This is both a strength (flexible) and a weakness (unpredictable).
- **The contrastive loss is the key innovation.** Instead of predicting pixels or labels, CLIP simply learns "these two things go together, those two do not." This is remarkably powerful and scalable.

### 6. Where it is used in our code
`src/phase28/phase28_multimodal_ai.py` implements a tiny CLIP-like model that learns to align 2D shape images with their text descriptions in a shared embedding space.

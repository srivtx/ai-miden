# What is Visual Question Answering (VQA)?

## 1. Problem Statement

Images contain rich information that text alone cannot capture. Users need to ask natural language questions about images and receive accurate answers. This requires understanding both the visual content and the linguistic query, then grounding the answer in the image.

## 2. Definition

**Visual Question Answering** is the task of answering a natural language question about a given image. Modern VQA systems use vision encoders (e.g., ViT, CLIP) to extract image features and language models to process the question, fusing the two through cross-modal attention or projection layers.

## 3. Analogy

VQA is like showing a friend a photo and asking, "What color is the car?" Your friend looks at the image, understands the question, finds the car, and answers. The model must do the same: see, understand, locate, and respond.

## 4. Example

Given an image of a kitchen and the question "What is on the counter next to the toaster?", a VQA model identifies the toaster in the image, looks at the surrounding region, and answers "A coffee mug." This requires object recognition, spatial reasoning, and language generation.

## 5. Common Confusion

VQA is NOT just image captioning. Captioning describes the whole image generically; VQA answers a specific question and must ground the answer in the relevant image regions. It is also not pure retrieval—generative VQA models produce novel answers not seen in training.

## 6. Code Location

See `src/phase108/phase108_multimodal_reasoning.py` for a NumPy simulation of cross-modal attention showing how image patches align with text tokens.

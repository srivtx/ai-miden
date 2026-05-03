# What is CLIP Scoring?

## Problem

To train a model that understands both images and text, you need a way to measure whether an image and a caption belong together. Manual labeling is impossible at billion-pair scale.

## Definition

CLIP Scoring refers to the method used by the CLIP model: an image encoder and a text encoder project both modalities into a shared embedding space. The similarity between an image embedding and a text embedding (typically cosine similarity or dot product) is the CLIP score. It measures semantic alignment.

## Analogy

A universal translator converts both French and German into a common symbolic language. You can then compare the symbol strings directly to see if the French and German sentences mean the same thing. The shared space is the CLIP embedding space.

## Example

An image of a dog has an embedding vector. The caption "a dog playing in the park" has another. Their dot product is 0.85. The caption "a red sports car" has a dot product of 0.12 with the same image. CLIP scoring correctly ranks the matching caption higher.

## Confusion

A high CLIP score does not mean the caption is factually correct in every detail. It means the caption is semantically related to the image. "A dog" and "a golden retriever" may both score highly on the same image.

## Code Location

See `src/phase103/phase103_multimodal_data.py` for a NumPy simulation of CLIP-style dot-product scoring between synthetic image and text embeddings.

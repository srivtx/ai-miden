# What is Contrastive Filtering?

## Problem

Web-scale multimodal datasets (image-text pairs) are extremely noisy. A caption like "click here" paired with a product image provides no semantic signal. Training on noise teaches the model nothing useful.

## Definition

Contrastive Filtering is the process of selecting training pairs by measuring how well the two modalities contrast with or align to each other in a learned embedding space. Pairs with low cross-modal similarity are discarded, leaving a cleaner dataset.

## Analogy

A language exchange program pairs students who speak different languages. If you pair a French speaker with another French speaker, nothing is learned. Contrastive filtering removes mismatched pairs so every remaining pair is a valid learning opportunity.

## Example

In a dataset of 1 billion image-text pairs, a contrastive model computes similarity scores. The bottom 30% by score are discarded. The remaining 700 million pairs have much stronger semantic alignment, leading to better downstream zero-shot classification.

## Confusion

Contrastive filtering is not just "removing duplicates." It is about cross-modal alignment. An image and text can both be high-quality individually but still be a bad pair if they describe unrelated things.

## Code Location

See `src/phase103/phase103_multimodal_data.py` for a NumPy simulation of contrastive filtering using dot-product similarity between image and text embeddings.

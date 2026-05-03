# What is Deduplication?

## Why it exists (THE PROBLEM first)

Web-scale datasets contain billions of documents. Many are near-identical copies scraped from different URLs, boilerplate templates, or repeated spam. Training on duplicates wastes compute and can cause the model to overfit to frequently repeated phrases.

## Definition (very simple)

Deduplication is the process of identifying and removing exact or near-duplicate examples from a dataset before training.

## Real-life analogy

When you return from vacation with 500 photos, 80 of them are blurry duplicates of the same sunset. You delete the duplicates because keeping them wastes storage and makes finding the good photo harder. Deduplication does the same for text.

## Tiny numeric example

A corpus has 1,000,000 documents. MinHash analysis reveals that 200,000 of them have greater than 90% Jaccard similarity with another document. Removing them reduces the dataset to 800,000 documents and cuts training time by roughly 20% without losing unique information.

## Common confusion

- **Deduplication is not the same as compression.** Compression stores duplicates efficiently; deduplication removes them entirely.
- **Near-deduplication is harder than exact deduplication.** Exact matching is a simple hash lookup; near-matching requires techniques like MinHash.
- **Removing duplicates does not always improve quality.** If all duplicates are high-quality, removing them just reduces volume without adding value.
- **Deduplication is not a one-time step.** New data arriving continuously must also be checked against existing data.
- **Jaccard similarity is not the only metric.** Edit distance, n-gram overlap, and embedding similarity are also used.

## Where it is used in our code

In `src/phase89/phase89_data_pipelines.py`, we implement a toy MinHash algorithm using simple hash functions and NumPy arrays. We compute MinHash signatures for three documents and estimate Jaccard similarity to decide whether any pair is a near-duplicate.

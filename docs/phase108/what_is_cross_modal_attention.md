# What is Cross-Modal Attention?

## 1. Problem Statement

Vision and language representations live in different embedding spaces. A vision encoder produces patch embeddings; a text encoder produces token embeddings. To answer questions like "What is the dog doing?", the model must relate specific text tokens ("dog", "doing") to specific image regions.

## 2. Definition

**Cross-Modal Attention** is an attention mechanism where queries from one modality (e.g., text) attend to keys and values from another modality (e.g., image). This allows information to flow between modalities, enabling the model to ground linguistic concepts in visual features and vice versa. It is the core fusion mechanism in multimodal transformers.

## 3. Analogy

Imagine a translator at a bilingual conference. The English speaker (text) asks a question, and the translator listens to the French speaker (image) to find the relevant parts of the response. Cross-modal attention is the translator: it routes each word to the most relevant visual details.

## 4. Example

In a vision-language transformer, each text token generates a query vector. These queries attend to key vectors from image patches. The token "dog" will have high attention weights on the image patch containing the dog, allowing the model to pull visual features about the dog into the text representation.

## 5. Common Confusion

Cross-modal attention is NOT the same as self-attention within one modality. Self-attention relates tokens to each other within text or patches within an image. Cross-modal attention bridges the two. Some architectures use both: self-attention within each modality, then cross-attention to fuse them.

## 6. Code Location

See `src/phase108/phase108_multimodal_reasoning.py` for a NumPy simulation of cross-modal attention between image patch embeddings and text token embeddings.

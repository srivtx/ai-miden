# What is Multimodal Chain-of-Thought (CoT)?

## 1. Problem Statement

Many real-world problems require reasoning over both visual and textual information. A single-step answer from a model may miss subtle relationships between what is seen in an image and what is asked in text. We need models that can think step-by-step across modalities.

## 2. Definition

**Multimodal Chain-of-Thought** extends the text-based chain-of-thought prompting technique to vision-language models. The model generates intermediate reasoning steps that interleave observations about an image with textual deductions, leading to a final answer. This improves performance on complex visual reasoning tasks.

## 3. Analogy

Imagine solving a detective case. You look at a photo (vision), read a witness statement (language), and think aloud: "The window is broken (vision), which means the thief entered here (text), so the footprint outside is relevant (vision)..." Multimodal CoT is that thinking process.

## 4. Example

A math word problem with a diagram. The model first describes the diagram in text ("The triangle has a base of 5 and height of 3"), then performs calculation steps ("Area = 0.5 * 5 * 3 = 7.5"), arriving at the answer. Without CoT, it might guess the wrong formula.

## 5. Common Confusion

Multimodal CoT is NOT just running separate vision and language models and concatenating results. It requires a unified architecture (or tight integration) where attention and reasoning flow back and forth between modalities during the generation of each reasoning step.

## 6. Code Location

See `src/phase108/phase108_multimodal_reasoning.py` for a NumPy simulation of cross-modal attention between image patches and text tokens.

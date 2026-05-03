# What Is Self-Consistency?

## Problem
A single chain-of-thought sample can be noisy or incorrect, even for a capable model. Relying on one reasoning path gives no way to recover from early mistakes.

## Definition
Self-Consistency is an inference-time technique where multiple independent reasoning chains are sampled, and the final answer is chosen by majority vote. It increases accuracy by aggregating diverse reasoning paths.

## Analogy
A jury of 12 people is more likely to reach a correct verdict than a single judge. Self-consistency is like asking 12 independent thinkers and taking the most common answer.

## Example
A model is asked a math question. It generates 10 CoT samples. Seven arrive at answer 42, two at 43, and one at 50. Self-consistency returns 42 as the final answer, even though some individual chains were wrong.

## Common Confusion
Self-consistency increases compute at inference time; it is not a training method. Do not confuse it with ensemble training or distillation. It is purely a test-time search strategy.

## Code Location
See `src/phase98/phase98_system2_reasoning.py` for a demonstration of self-consistency improving accuracy over single chains.

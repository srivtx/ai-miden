# What is Verifier-Augmented Generation?

## Problem

Language models are trained to maximize likelihood, not correctness. A model may generate a plausible-looking but incorrect answer because it "sounds right" in the training distribution.

## Definition

Verifier-Augmented Generation is a decoding or training strategy where a separate verifier model (or symbolic checker) scores candidate outputs, and the generator is trained or sampled to maximize the verifier's approval. The verifier acts as a learned or hardcoded quality gate.

## Analogy

An architect draws building plans, but a structural engineer must sign off on them before construction begins. The engineer does not design the building, but their approval determines which plans are built. The architect learns to design plans that pass engineering review.

## Example

A theorem-proving model generates multiple proof candidates. A trained verifier scores each proof's likelihood of validity. The model is optimized to maximize the verifier score rather than just the token probability of the proof text.

## Confusion

The verifier is not the ground truth. It is a model that can make mistakes. If the verifier is biased or limited, Verifier-Augmented Generation will optimize for passing the verifier, not for actual correctness (a form of reward hacking).

## Code Location

See `src/phase102/phase102_synthetic_data.py` for a NumPy simulation of verifier-augmented filtering where a verifier score determines which generated samples are retained.

# What is Self-Improvement?

## Problem

High-quality human-labeled data is expensive and finite. For specialized domains, there may not be enough labeled examples to train a model to peak performance.

## Definition

Self-Improvement is the process by which a model generates its own training data, filters or verifies it, and then trains on the resulting dataset to improve its capabilities. This creates a feedback loop where the model bootstraps from its own outputs.

## Analogy

A student writes practice exam questions, then checks the answers against a solution key. The student studies only the questions they got wrong, effectively generating a personalized study guide from their own work.

## Example

A math reasoning model generates 10,000 chain-of-thought solutions. An external symbolic solver verifies which are correct. The model is then fine-tuned on the verified correct chains. Its accuracy on held-out problems improves in the next iteration.

## Confusion

Self-Improvement does not mean the model improves infinitely on its own. Without a reliable verifier or filter, the model can reinforce its own errors (a phenomenon called "model collapse" or "drift"). The verifier is the critical component.

## Code Location

See `src/phase102/phase102_synthetic_data.py` for a NumPy simulation of a self-improvement loop where accepted samples shift the generative distribution over iterations.

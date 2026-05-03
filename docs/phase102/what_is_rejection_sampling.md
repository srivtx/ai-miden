# What is Rejection Sampling?

## Problem

When training a model, not all generated data is useful. Random samples from a language model may be low-quality, factually wrong, or misaligned. Training on bad data hurts performance.

## Definition

Rejection Sampling is a filtering procedure where samples are generated from a model and then accepted or rejected based on a quality criterion (e.g., a reward model score, a verifier, or a heuristic). Only accepted samples are added to the training set.

## Analogy

A publisher receives hundreds of manuscript submissions. An editor reads the first chapter of each and rejects the ones that do not meet quality standards. Only the accepted manuscripts proceed to full editing. The editor is the filter; the manuscript pool is the synthetic data.

## Example

A code generation model produces 100 solutions to a programming problem. A unit-test verifier passes 30 of them. Only those 30 correct solutions are kept for fine-tuning. The effective training distribution shifts toward correct code.

## Confusion

Rejection Sampling is not the same as simply "cleaning data." It is an active generation-and-filter loop where the model generates candidates and an external judge decides what enters the dataset. The model itself does not learn during sampling.

## Code Location

See `src/phase102/phase102_synthetic_data.py` for a NumPy simulation of rejection sampling showing how filtering by threshold shifts the effective distribution.

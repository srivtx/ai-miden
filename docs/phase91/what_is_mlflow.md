# What is MLflow?

## Problem it Solves
As teams scale ML development, ad-hoc logging with spreadsheets or text files breaks down. There is no standard way to package experiments, compare runs, or transition models to production.

## Definition
MLflow is an open-source platform for managing the machine learning lifecycle. It provides modules for tracking experiments, packaging code into reproducible runs, and managing model deployment through a central registry.

## Analogy
MLflow is like a factory assembly line for ML. Raw materials (data and code) enter at one end, each workstation (tracking, packaging, registry) adds structure, and a finished product (a versioned model) emerges at the other.

## Example
A data scientist uses MLflow Tracking to log a set of XGBoost runs, then uses the MLflow Model Registry to promote the best-performing run to a "Staging" stage before it is deployed to production.

## Common Confusion
MLflow is often compared to proprietary tools like Weights & Biases. While the core tracking concepts overlap, MLflow is self-hosted and tightly integrated with the MLflow Model format, whereas cloud platforms offer additional collaboration dashboards.

## Code Location
See `src/phase91/phase91_experiment_tracking.py` for a lightweight JSON-based tracker that mirrors the same concepts of run logging and comparison.

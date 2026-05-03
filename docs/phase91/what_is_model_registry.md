# What is a Model Registry?

## Problem it Solves
In production environments, multiple model versions compete for deployment. Without governance, teams risk deploying untested models or losing track of which version is currently serving traffic.

## Definition
A model registry is a centralized store for machine learning models. It manages versioning, stage transitions (e.g., Development, Staging, Production), and lineage back to the experiments that produced each model.

## Analogy
A model registry is like a library card catalog. Each book (model) has a unique identifier, a record of when it was added, and a status indicating whether it is available on the shelf (Production) or in storage (Archived).

## Example
After a champion-challenger test, the registry updates the Production tag from "v1.2" to "v1.3" while keeping v1.2 available for rollback. The registry also stores the training artifact URI so the full experiment can be reconstructed.

## Common Confusion
A model registry is not merely a blob store like Amazon S3. While S3 holds files, a registry adds semantic metadata, lifecycle stages, and approval workflows that govern how models move from experiment to production.

## Code Location
See `src/phase91/phase91_experiment_tracking.py` for a simplified artifact-management pattern that demonstrates versioning model weights.

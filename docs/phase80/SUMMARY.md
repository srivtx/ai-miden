← [Previous: Phase 79: Causal Inference](docs/phase79/SUMMARY.md) | [Next: Phase 81: Continual Learning](docs/phase81/SUMMARY.md) →

---

# Phase 80: MLOps & Production Monitoring — Summary

## What you will learn

This phase bridges the gap between "model training" and "model living in production."  A model is not a static artifact; it is a piece of software that degrades as the world changes around it.  You will learn how to detect that degradation, how to track every ingredient that went into a model, and how to safely swap models in production without chaos.

## Topics covered

| Topic | Core Idea |
|-------|-----------|
| **Data Drift** | The distribution of inputs `P(X)` shifts.  The model may still be "correct" but it is operating far outside its training domain. |
| **Concept Drift** | The relationship `P(y \| X)` changes.  The model's learned logic is now literally the wrong logic. |
| **Experiment Tracking** | Every hyperparameter, metric, code version, and artifact is logged so results are reproducible and comparable. |
| **Model Registry** | Models are versioned and promoted through lifecycle stages (Staging → Production → Archived) so rollbacks are one API call away. |

## Files in this phase

```
docs/phase80/
  what_is_data_drift.md          — Input distribution changes & detection
  what_is_concept_drift.md       — Relationship changes & model degradation
  what_is_experiment_tracking.md — Logging hyperparameters, metrics, artifacts
  what_is_model_registry.md      — Versioning, staging, promoting models
  SUMMARY.md                     — This file

src/phase80/
  phase80_mlops.py               — NumPy demo: simulate drift, compute KL/PSI, plot timeline
  phase80_mlops_colab.py         — Colab script: full MLflow/W&B + retraining + registry workflow
  mlops.png                      — Generated visualisation
```

## Key take-aways

1. **Drift detection ≠ accuracy monitoring.**  You can detect data drift on `X` alone, often weeks before ground-truth labels arrive and accuracy tanks.
2. **KL divergence and PSI** are fast, distribution-agnostic ways to compare a reference dataset to a production batch.  They work on histograms and require no model retraining.
3. **Concept drift is harder** than data drift because you need labels (or strong proxies) to see that the `X → y` mapping broke.
4. **Experiment tracking prevents archaeology.**  Never again ask "what learning rate did I use for the good run?"
5. **A Model Registry is a deployment safety net.**  Immutable versions + mutable stages mean you can promote, demote, and roll back without ever losing a model binary.

## When to apply this

- Any model that runs continuously for more than a few days.
- Any system where upstream data pipelines are owned by another team.
- Any regulated environment where you must prove reproducibility (finance, healthcare).
- Any team with more than one person training models.

---

← [Previous: Phase 79: Causal Inference](docs/phase79/SUMMARY.md) | [Next: Phase 81: Continual Learning](docs/phase81/SUMMARY.md) →

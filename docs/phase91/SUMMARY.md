# Phase 91: Experiment Tracking & MLOps Maturity

## What We Learned

1. **Experiment tracking creates institutional memory.** Logging hyperparameters, metrics, and artifacts for every run prevents the chaos of unlabeled model files and makes promising results reproducible months later.
2. **A lightweight tracker demonstrates the same principles as enterprise tools.** Our JSON-based tracker captures start times, per-epoch metrics, and artifact paths, mirroring the core workflow of MLflow without external infrastructure.
3. **MLflow standardizes the full ML lifecycle.** Its four modules—Tracking, Projects, Models, and Registry—provide an open-source, self-hosted alternative to proprietary platforms.
4. **A model registry adds governance to deployment.** Versioning models and controlling stage transitions (Development to Staging to Production) prevents untested checkpoints from reaching users and enables instant rollback.
5. **Tracking and registry are sequential layers.** Tracking captures the training process; the registry manages the artifact after training. Together they form the backbone of mature MLOps.
6. **Reproducibility requires more than metrics.** True reproducibility also demands pinned random seeds, versioned datasets, and documented library versions alongside logged hyperparameters.

## Prerequisites

- Familiarity with Python classes and JSON serialization
- Understanding of gradient descent and training loops
- Basic knowledge of model versioning and deployment concepts
- Experience with Matplotlib for plotting training curves

## Recommended Reading Order

1. `what_is_experiment_tracking.md` — Start with the foundational practice of logging runs and comparing results
2. `what_is_mlflow.md` — Learn how an open-source platform scales tracking into a full lifecycle management system
3. `what_is_model_registry.md` — Finish with governance, versioning, and the transition from experiment to production

## Visual Outputs

- `phase91_runs.png` — Line plot showing loss curves for three training runs with different learning rates, demonstrating how tracking enables visual comparison.

## Navigation

- [Previous Phase](../phase90/SUMMARY.md)
- [Next Phase](../phase92/SUMMARY.md)

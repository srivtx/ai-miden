## What Is a Model Registry?

---

## The Problem

In production environments, multiple model versions compete for deployment. Without governance, teams risk deploying untested models, losing track of which version is currently serving traffic, or being unable to roll back when a new model degrades performance. How do you manage the lifecycle of models from experiment to production?

---

## Definition

A **model registry** is a centralized store for machine learning models. It manages versioning, stage transitions (for example, Development to Staging to Production), and lineage back to the experiments that produced each model.

**How it works:**
```
Lifecycle workflow:
  1. Training run completes → model artifact logged
  2. Register artifact as a new version (e.g., v1.3)
  3. Move version through stages:
       Development  → validate on test set
       Staging      → shadow traffic or A/B test
       Production   → serve live traffic
       Archived     → keep for audit but do not serve
  4. Tag champion (current Production) and challenger (candidate)
  5. If Production degrades, rollback to previous version
  6. Store lineage: training config, dataset version, metrics URI
```

**Why this matters:**
- A registry prevents accidental deployment of an experimental checkpoint that never passed validation.
- Rollback from a bad deployment takes seconds rather than hours of retraining.
- Audit trails show exactly which data and code produced every serving model.

---

## Real-Life Analogy

A model registry is like a library card catalog. Each book (model) has a unique identifier, a record of when it was added, and a status indicating whether it is available on the shelf (Production) or in storage (Archived).

Imagine a pharmaceutical company manufacturing vaccines. Each batch receives a lot number, a manufacturing date, and a quality status. Batches pass through stages: raw material (Development), quality control (Staging), approved for distribution (Production), and recalled or expired (Archived). When a doctor administers a vaccine, the lot number traces back to the exact production run, ingredients, and test results. A model registry functions identically: each model version is a batch, the stage transitions are quality gates, and the lineage metadata is the lot number. If a model in Production starts producing bad predictions, the registry tells you which training run and dataset version to investigate.

**The trade-off:** Registries add bureaucracy. A researcher running rapid experiments may chafe at stage gates and approval workflows. The discipline pays off when the model reaches users, but early experimentation should stay lightweight.

---

## Tiny Numeric Example

**Before a model registry:**

| File Name | Stage | Training Date | Validation Accuracy | Notes |
|-----------|-------|---------------|---------------------|-------|
| model_final.pth | ??? | ??? | ??? | Is this the one? |
| model_best.pth | ??? | ??? | ??? | Maybe this one? |
| model_v2.pth | ??? | ??? | ??? | Deployed by mistake |

- Rollback time after bad deployment: unknown (may need to retrain)
- Audit trail: none
- Team confusion: high

**After adopting a model registry:**

| Version | Stage | Validation Accuracy | Deployed Date | Rollback Target |
|---------|-------|---------------------|---------------|-----------------|
| v1.1 | Archived | 0.81 | 2024-01-10 | — |
| v1.2 | Production | 0.85 | 2024-02-15 | v1.1 |
| v1.3 | Staging | 0.87 | — | v1.2 |
| v1.4 | Development | 0.83 | — | — |

- Rollback time after bad deployment: 30 seconds (retag Production to v1.2)
- Audit trail: full lineage from experiment to serving
- Team confidence: high

---

## Common Confusion

1. **"A model registry is just a blob store like Amazon S3."** It is not. While S3 holds files, a registry adds semantic metadata, lifecycle stages, and approval workflows that govern how models move from experiment to production.

2. **"The registry trains models."** It does not. Training happens in experiment tracking or training pipelines. The registry only stores, versions, and stages finished models.

3. **"One registry entry per experiment."** Usually there are many. A single experiment may produce dozens of checkpoints, and only the best one is registered.

4. **"Staging and Production are the only stages."** They are not. Most registries support custom stages such as Development, Staging, Production, and Archived to match an organization's workflow.

5. **"A registry replaces experiment tracking."** It does not. Tracking logs the training process; the registry manages the artifact after training. They integrate but serve different lifecycle phases.

6. **"You cannot have multiple Production versions."** You can. Canary deployments and A/B tests may run two Production-tagged versions simultaneously on different traffic splits.

7. **"Registries are only for deep learning."** They are not. Any serialized model—scikit-learn, XGBoost, or a simple rule-based system—can be versioned and staged in a registry.

---

## Where It Is Used in Our Code

`src/phase91/phase91_experiment_tracking.py` — We implement a simplified artifact-management pattern that demonstrates versioning model weights. Each run saves weights as a named `.npy` artifact and records the path in the run log. This captures the same versioning concept that a full model registry automates across an organization.

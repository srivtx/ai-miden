## What Is MLflow?

---

## The Problem

As teams scale machine learning development, ad-hoc logging with spreadsheets or text files breaks down. There is no standard way to package experiments, compare runs, or transition models to production. Every team invents its own conventions, leading to fragmented tools and lost institutional knowledge. How do you standardize the entire ML lifecycle?

---

## Definition

**MLflow** is an open-source platform for managing the machine learning lifecycle. It provides modules for tracking experiments, packaging code into reproducible runs, and managing model deployment through a central registry.

**How it works:**
```
MLflow components:

  Tracking:
    - Log parameters, metrics, and artifacts per run
    - Query and compare runs via UI or API
    - Store results in local files or a remote tracking server

  Projects:
    - Package code with a conda/pip environment specification
    - Run the package on any platform with a single command
    - Reproduce results by re-running the exact same environment

  Models:
    - Save models in a standard format with flavor metadata
    - Deploy to diverse serving platforms without re-engineering

  Registry:
    - Version models and manage stage transitions
    - Control which versions are in Development, Staging, or Production
    - Maintain lineage back to the run that produced each version
```

**Why this matters:**
- Before MLflow, a team might store model weights in S3, metrics in a spreadsheet, and training code in an unversioned notebook. MLflow unifies these into one queryable system.
- A model promoted to Production in the Registry carries its full lineage: hyperparameters, metrics, and artifact URI.
- Open-source self-hosting means teams are not locked into a proprietary vendor.

---

## Real-Life Analogy

MLflow is like a factory assembly line for ML. Raw materials (data and code) enter at one end, each workstation (tracking, packaging, registry) adds structure, and a finished product (a versioned model) emerges at the other.

Imagine a craft brewery that started as a homebrew hobby. At first, the brewer scribbled recipes on sticky notes, stored bottles in the garage, and served friends from memory. As demand grew, chaos followed: a great batch could not be reproduced, and a bad batch reached customers because there was no quality gate. The brewery then installed a proper system: a recipe log (tracking), standardized ingredient kits (projects), labeled bottles with batch numbers (models), and a tasting panel that approves batches before release (registry). MLflow is that system for machine learning. It turns ad-hoc experimentation into a repeatable, auditable production pipeline.

**The trade-off:** MLflow requires infrastructure. A tracking server needs a database and storage backend. For a single researcher on a laptop, the setup may exceed the benefit. For a team of five or more, the standardization pays for itself within weeks.

---

## Tiny Numeric Example

**Before MLflow:**

| Asset | Location | Searchable | Versioned |
|-------|----------|------------|-----------|
| Model weights | S3 bucket / local disk | No | No |
| Metrics | Spreadsheet | Partially | No |
| Hyperparameters | Notebook cell | No | No |
| Training code | Git repo | Yes | Yes |
| Deployment status | Email thread | No | No |

- Time to find the best model from last month: 2 hours
- Risk of deploying wrong version: high
- Onboarding new team member: 1 week

**After MLflow:**

| Asset | Location | Searchable | Versioned |
|-------|----------|------------|-----------|
| Model weights | MLflow artifact store | Yes | Yes |
| Metrics | MLflow tracking server | Yes | Yes |
| Hyperparameters | MLflow tracking server | Yes | Yes |
| Training code | MLflow project / Git | Yes | Yes |
| Deployment status | MLflow Registry | Yes | Yes |

- Time to find the best model from last month: 30 seconds
- Risk of deploying wrong version: low (stage gates enforced)
- Onboarding new team member: 1 day

---

## Common Confusion

1. **"MLflow is the same as Weights & Biases."** They share core tracking concepts, but MLflow is open-source and self-hosted, whereas Weights & Biases is a proprietary cloud platform with additional collaboration dashboards.

2. **"MLflow replaces Git."** It does not. Git tracks code; MLflow tracks runs, metrics, and artifacts. They integrate but serve different purposes.

3. **"You need a server to use MLflow."** You do not. The tracking API can write to local files. A server is only needed for team sharing and centralized storage.

4. **"MLflow only works with Python."** While Python is the primary interface, MLflow models can be served via REST APIs and integrated with Java, R, and other languages.

5. **"The Model Registry is just a file store."** It is not. It adds semantic metadata, lifecycle stages, and approval workflows that govern how models move from experiment to production.

6. **"MLflow automatically improves model quality."** It does not. It improves reproducibility and governance. Model quality still depends on data, architecture, and hyperparameter choices.

7. **"MLflow is only for large enterprises."** It is not. A single researcher can benefit from MLflow Tracking on a laptop. The value scales with team size, but it does not require enterprise infrastructure.

---

## Where It Is Used in Our Code

`src/phase91/phase91_experiment_tracking.py` — We implement a lightweight JSON-based tracker that mirrors the same concepts of run logging and comparison. It captures hyperparameters, per-epoch metrics, and artifact paths, demonstrating the fundamental principles that MLflow automates at scale.

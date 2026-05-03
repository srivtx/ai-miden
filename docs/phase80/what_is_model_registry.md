# What is a Model Registry?

## 1. Why it exists (THE PROBLEM)

Your data scientist trains a new model with 5% better accuracy. She emails you the `.pkl` file. You put it on the production server. Two days later, a bug is found in her preprocessing code. You need to roll back to the old model, but you overwrote the file. Meanwhile, another team deployed a different "v2" model to staging, and nobody knows which is which. Production is chaos because there is no single source of truth for models.

## 2. Definition

A model registry is a centralized system that versions trained models, tracks their lifecycle stages (Staging, Production, Archived), and controls which model version is served to users.

## 3. Real-life analogy

Think of a model registry like a library catalog. Every book (model) has a unique ISBN (version). The catalog tracks whether a book is "in storage" (Archived), "on the new-shelf" (Staging), or "checked out to patrons" (Production). You never throw away old editions; you simply update the catalog to point readers to the correct one.

## 4. Tiny numeric example

Without a registry:
```
model.pkl          <- overwritten every deploy
model_backup.pkl   <- what even is this?
best_model.pkl     <- from which experiment?
```

With a registry (MLflow Model Registry):
```
Model: fraud-detector
  Version 1: accuracy=0.91 | Stage: Archived
  Version 2: accuracy=0.93 | Stage: Production
  Version 3: accuracy=0.95 | Stage: Staging  (awaiting QA)
```

## 5. Common confusion

- **"A model registry is just a folder of pickle files"** — No. A registry stores metadata, lineage (which experiment produced it), stage transitions, and approval workflows. A folder cannot enforce "only one Production model at a time."
- **"Versioning models is the same as git versioning"** — No. Git is for code (text files). Model binaries are large, and git is terrible at them. Registries are built for large artifacts with lifecycle metadata.
- **"Staging means the model is not ready"** — In registry terms, "Staging" is an environment stage, not a judgment of quality. A model in Staging might be undergoing A/B testing before promotion to Production.
- **"Once a model is in Production, it never changes"** — The model binary does not change, but its stage can transition back to Archived. Immutable versions plus mutable stages are the whole point.
- **"I need a registry only if I have dozens of models"** — Even one model benefits. The first time you need to roll back at 2 AM, you will understand why.
- **"Registries are only for MLflow"** — No. W&B has the Model Registry, AWS has SageMaker Model Registry, Azure has ML Model Registry, and open-source tools like DVC can approximate the workflow.
- **"A registry replaces model monitoring"** — No. A registry manages *deployment*. Monitoring watches *behavior*. They work together: monitoring detects drift, and the registry helps you deploy the replacement.

## 6. Where it is used in our code

- `src/phase80/phase80_mlops_colab.py`: After training, we register the new model to MLflow Model Registry as Version `N`. We set its stage to "Staging." After drift detection triggers retraining and the new model passes validation, we transition the old Production model to "Archived" and promote the new version to "Production" — all through API calls with audit trails.

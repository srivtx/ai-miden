# What is Experiment Tracking?

## 1. Why it exists (THE PROBLEM)

You run 47 experiments over a weekend: different learning rates, batch sizes, and architectures. By Monday, you have 47 model files named `model_final_v2_REALLY_final.pkl`. You forgot which hyperparameters produced the best validation score. You cannot reproduce your best result. Your team wastes days re-running experiments you already did. This chaos is why experiment tracking exists.

## 2. Definition

Experiment tracking is the systematic logging of every ingredient that goes into a model run: hyperparameters, code versions, metrics, artifacts (datasets, models, plots), and environment details, so that any result can be reproduced, compared, and audited.

## 3. Real-life analogy

Imagine a professional kitchen where every chef writes down the exact recipe, ingredients, oven temperature, and cooking time for every dish. If a customer loves a dish, the chef can reproduce it exactly. If a dish fails, the chef can compare notes with yesterday's attempt to find what changed.

## 4. Tiny numeric example

Without tracking:
```
Experiment 1: lr=0.01, acc=0.82   (lost)
Experiment 2: lr=0.001, acc=0.85  (lost)
Experiment 3: lr=0.005, acc=0.79  (kept, but why?)
```

With tracking (MLflow / W&B):
```
Run ID: abc123 | lr=0.01 | batch_size=32 | val_acc=0.82 | git_hash=a1b2c3
Run ID: def456 | lr=0.001 | batch_size=64 | val_acc=0.85 | git_hash=a1b2c3
```

## 5. Common confusion

- **"Experiment tracking is just saving model files"** — No. Saving the model without its hyperparameters, training data version, and metric history is useless for reproduction.
- **"I can track experiments in a spreadsheet"** — You can, until you have 1,000 runs across 5 team members and 3 machines. Spreadsheets do not scale and cannot capture artifacts automatically.
- **"Tracking slows down training"** — Modern tools like W&B and MLflow log asynchronously. The overhead is typically less than 1%.
- **"Tracking is only for hyperparameters"** — No. You should also log metrics over time (loss curves), hardware usage (GPU memory), dataset versions, and even random seeds.
- **"I only need to track my best run"** — No. Failed runs teach you what does not work. You cannot know what is "best" until you compare everything.
- **"Tracking replaces git"** — No. Tracking logs the *results* of code; git logs the *code itself*. You need both. Good practice is to log the git commit hash with every run.
- **"Open-source tracking tools are not secure enough for enterprise"** — MLflow has RBAC and artifact stores. W&B has private teams and SSO. They are used at Fortune 500 companies.

## 6. Where it is used in our code

- `src/phase80/phase80_mlops_colab.py`: We initialize an MLflow run at the start of training and log every hyperparameter (`n_estimators`, `max_depth`), the training dataset hash, validation metrics (accuracy, F1), and the trained model artifact. We also log the git commit hash so the experiment is fully reproducible.

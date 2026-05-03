## What Is Experiment Tracking?

---

## The Problem

Machine learning involves many moving parts: learning rates, batch sizes, model architectures, and random seeds. Without a systematic record, it is easy to lose track of which configuration produced which result. Teams often end up with dozens of unlabeled model files and no way to reproduce a promising run. How do you create a searchable, reproducible history of the modeling process?

---

## Definition

**Experiment tracking** is the practice of logging hyperparameters, metrics, code versions, and artifacts for every training run. It creates a searchable, reproducible history of the modeling process.

**How it works:**
```
Tracking workflow:
  1. Start a new run with a name and hyperparameters:
       run_name = "lr_sweep_0.01"
       hyperparams = {"lr": 0.01, "batch_size": 32, "epochs": 50}

  2. Each epoch, log metrics:
       log_metric(epoch=1, loss=0.45, accuracy=0.72)
       log_metric(epoch=2, loss=0.32, accuracy=0.81)

  3. Save artifacts:
       log_artifact("model_weights", final_weights)
       log_artifact("training_curves", plot_buffer)

  4. End the run and compute duration

  5. Compare runs:
       print table of run_name, hyperparams, final_accuracy
       plot loss curves for all runs on same axes
```

**Why this matters:**
- A team running fifty experiments can instantly identify which learning rate gave the best validation accuracy.
- Reproducing a six-month-old result requires only the run ID, not reverse-engineering from a forgotten notebook.
- Artifact logging preserves model weights, plots, and configuration files alongside metrics.

---

## Real-Life Analogy

Experiment tracking is like a scientist's lab notebook. Every chemical measurement, temperature setting, and observation is recorded so that the experiment can be repeated or audited later.

Imagine a pastry chef testing twenty variations of a croissant recipe. Each variation changes one ingredient: butter brand, fermentation time, oven temperature. Without notes, the chef bakes batch after batch and forgets which recipe produced the flaky layers. With a notebook, every batch is labeled with the exact recipe, the kitchen temperature, and a photo of the result. Six months later, the chef can reproduce the winning batch precisely. Experiment tracking is the digital version of that notebook: it records not just the recipe (hyperparameters) but also the rise height (metrics) and the crumb photo (artifacts) for every batch (run).

**The trade-off:** Tracking adds boilerplate to training code. Every run needs start, log, and end calls. The overhead is minimal compared to the cost of losing reproducibility, but small one-off scripts may not justify the setup.

---

## Tiny Numeric Example

**Three training runs without tracking:**

| File Name | Learning Rate | Final Accuracy | Notes |
|-----------|---------------|----------------|-------|
| model_v1.pth | ??? | ??? | Forgot which config |
| model_v2.pth | ??? | ??? | Maybe 0.01? |
| model_v3.pth | ??? | ??? | Best one, but why? |

- Time spent reverse-engineering: 2 hours
- Reproducibility: impossible
- Team confidence: low

**Three training runs with tracking:**

| Run Name | LR | Epochs | Final Accuracy | Duration |
|----------|----|--------|----------------|----------|
| run_lr0.1 | 0.10 | 20 | 0.8245 | 1.2 s |
| run_lr0.5 | 0.50 | 20 | 0.7823 | 1.1 s |
| run_lr0.01 | 0.01 | 20 | 0.7890 | 1.3 s |

- Time spent comparing: 10 seconds
- Reproducibility: full hyperparams and artifacts stored
- Team confidence: high
- Decision: deploy model from run_lr0.1

---

## Common Confusion

1. **"Experiment tracking is the same as version control."** It is not. Git tracks code changes; experiment tracking records the runtime configuration and results produced by that code. They are complementary, not interchangeable.

2. **"Tracking is only for large teams."** It is not. Even a solo researcher benefits from tracking after the third hyperparameter sweep, when memory alone is no longer reliable.

3. **"Logging metrics is enough."** It is not. Without hyperparameters and artifacts, metrics are meaningless. A 92% accuracy score tells you nothing if you do not know which learning rate produced it.

4. **"Experiment tracking slows down training."** The overhead is negligible. Writing a few scalars to disk or a remote server takes milliseconds per epoch, compared to seconds or minutes of compute.

5. **"Any spreadsheet is as good as a tracker."** It is not. Spreadsheets are manual, error-prone, and cannot version artifacts or reproduce plots. Automated tracking eliminates transcription errors.

6. **"You should track everything."** You should not. Tracking every intermediate tensor would consume terabytes. Track summary metrics, final model weights, and key plots. Log the full dataset only if storage permits.

7. **"Tracking guarantees reproducibility."** It helps enormously, but true reproducibility also requires pinning random seeds, versioning datasets, and documenting hardware and library versions.

---

## Where It Is Used in Our Code

`src/phase91/phase91_experiment_tracking.py` — We implement a `JSONExperimentTracker` class that logs run names, hyperparameters, per-epoch metrics, and artifact paths to a JSON file. We train three tiny linear classifiers with different learning rates, compare their final accuracy in a printed table, and plot all loss curves on the same axes. The comparison plot is saved to `phase91_runs.png`, and model weights are saved as `.npy` artifacts.

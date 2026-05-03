# What is Experiment Tracking?

## Problem it Solves
Machine learning involves many moving parts: learning rates, batch sizes, model architectures, and random seeds. Without a systematic record, it is easy to lose track of which configuration produced which result. Teams often end up with dozens of unlabeled model files and no way to reproduce a promising run.

## Definition
Experiment tracking is the practice of logging hyperparameters, metrics, code versions, and artifacts for every training run. It creates a searchable, reproducible history of the modeling process.

## Analogy
Think of experiment tracking as a scientist's lab notebook. Every chemical measurement, temperature setting, and observation is recorded so that the experiment can be repeated or audited later.

## Example
A researcher trains three ResNet variants with different learning rates. The tracker records:
- Hyperparameters: learning_rate=0.01, batch_size=32
- Metrics: epoch 1 loss=0.45, epoch 2 loss=0.32, validation accuracy=0.82
- Artifacts: final model weights, training curves plot

## Common Confusion
Experiment tracking is not the same as version control (Git). Git tracks code changes, while experiment tracking records the runtime configuration and results produced by that code.

## Code Location
See `src/phase91/phase91_experiment_tracking.py` for a JSON-based tracker that logs hyperparameters, per-epoch metrics, and model weights, and demonstrates comparing two runs.

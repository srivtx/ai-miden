# What is a Benchmark?

## Problem it Solves
Researchers need a common playing field to compare models. Without a shared evaluation protocol, every paper can claim superiority using a different dataset or metric, making progress impossible to measure.

## Definition
A benchmark is a standardized combination of dataset, task definition, evaluation metric, and protocol that allows fair comparison across models and research groups.

## Analogy
A benchmark is like a racing track. Every car (model) drives the same distance, under the same rules, so the stopwatch (metric) tells us which is genuinely faster.

## Example
ImageNet is a benchmark for image classification. It specifies 1.28 million training images, 1000 classes, and top-1/top-5 accuracy as the metric. Any model evaluated on ImageNet can be compared directly to others.

## Common Confusion
A benchmark is not just a dataset. A dataset is the raw material; a benchmark adds the task, metric, and rules that govern how the dataset is used.

## Code Location
See `src/phase92/phase92_benchmark_design.py` for a toy benchmark that demonstrates clean versus contaminated evaluation splits.

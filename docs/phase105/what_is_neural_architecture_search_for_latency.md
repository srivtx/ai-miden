# What is Neural Architecture Search for Latency?

## Problem

Standard NAS optimizes for accuracy on a validation set, but edge devices have strict latency, memory, and energy constraints. A model with 99% accuracy that takes 5 seconds per inference is useless for real-time mobile vision.

## Definition

Neural Architecture Search for Latency (Latency-Aware NAS) is a variant of NAS where the search objective is a multi-objective function combining accuracy and inference latency (or FLOPs, or memory). The search algorithm explores architectures on a Pareto frontier, trading off accuracy for speed.

## Analogy

A car designer is not just trying to maximize top speed. They must also meet fuel efficiency and safety regulations. Latency-aware NAS is like optimizing for both speed and mileage simultaneously, finding the best cars across the entire efficiency-performance curve.

## Example

MobileNetV3 was designed using hardware-aware NAS. The search space included operations with known latency profiles on target mobile CPUs. The reward function combined ImageNet accuracy with measured latency on a Pixel phone. The resulting model runs in real time on mobile cameras.

## Confusion

Latency-aware NAS does not simply mean "pick the smallest model." It means searching the architecture space for models that are unexpectedly efficient. Sometimes a slightly larger model with a better operation mix is faster than a smaller model with inefficient operations.

## Code Location

See `src/phase105/phase105_tiny_ml.py` for a NumPy simulation of knowledge distillation, a complementary technique often used alongside latency-aware NAS in Tiny ML pipelines.

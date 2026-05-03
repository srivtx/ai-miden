# What is Checkpointing?

## Why it exists (THE PROBLEM first)

Large neural network training jobs can run for days or weeks on expensive hardware. If a machine crashes, a network partition occurs, or a node is preempted, all progress made since the start is lost. Without periodic snapshots of training state, teams must restart from epoch zero, burning money and time.

## Definition (very simple)

Checkpointing is the act of saving the complete training state—including model weights, optimizer state, and random number generator state—to durable storage at regular intervals so that training can resume later from that exact point.

## Real-life analogy

Think of saving a video game. You do not want to replay the entire campaign from the beginning every time you die. A checkpoint lets you respawn at the last save point with all your inventory and progress intact.

## Tiny numeric example

A model trains for 100 epochs. A checkpoint is written every 10 epochs. If the server crashes at epoch 73, the job restarts from epoch 70 rather than epoch 0. The team loses 3 epochs of work instead of 73.

## Common confusion

- **Checkpointing is not the same as exporting a final model.** A checkpoint contains optimizer state and RNG seeds; a final model file usually contains only weights.
- **More frequent checkpoints do not always help.** Writing huge tensors to disk every step can stall the GPU and slow training.
- **Checkpointing does not prevent crashes.** It only reduces the cost of recovery.
- **A checkpoint is not a backup of the dataset.** It stores model state, not training data.
- **Resuming from a checkpoint is not automatic.** The training script must explicitly load the saved state and skip already-seen data.

## Where it is used in our code

In `src/phase87/phase87_checkpointing.py`, we build a dictionary with weights, optimizer momentum buffers, and the NumPy RNG state. We then reload that dictionary and verify that two runs starting from the same seed produce identical updates.

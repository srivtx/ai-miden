## What Is Checkpointing?

---

### The Problem

Large neural network training jobs can run for days or weeks on expensive hardware. If a machine crashes, a network partition occurs, or a cloud instance is preempted by a higher-priority job, all progress made since the start is lost. Without periodic snapshots of training state, teams must restart from epoch zero, burning thousands of dollars and days of calendar time. Checkpointing is the insurance policy that makes long-running training jobs survivable.

---

### Definition

**Checkpointing** is the act of saving the complete training state -- including model weights, optimizer state, and random number generator state -- to durable storage at regular intervals so that training can resume later from that exact point.

**How it works:**
```
Every N steps or epochs:
  1. Gather model weights
  2. Gather optimizer momentum/velocity buffers
  3. Gather random number generator state
  4. Gather current step/epoch count
  5. Serialize to disk (e.g., .pt, .pkl, or cloud storage)

On crash:
  1. Load checkpoint from disk
  2. Restore weights, optimizer, RNG, and step count
  3. Skip already-seen data
  4. Resume training
```

**Key contents of a checkpoint:**
- **Model weights:** the parameters being trained.
- **Optimizer state:** momentum buffers, adaptive learning rate states (e.g., Adam's m and v).
- **RNG state:** ensures that data shuffling and dropout resume exactly where they left off.
- **Training metadata:** current step, epoch, and best validation score.

**Why this matters:**
- A checkpoint every 10 epochs on a 100-epoch job limits maximum loss to 10 epochs.
- Checkpoints are also used for early stopping, ensemble creation, and hyperparameter search.

---

### Real-Life Analogy

Think of saving a video game. You do not want to replay the entire campaign from the beginning every time you die. A checkpoint lets you respawn at the last save point with all your inventory, experience points, and quest progress intact. Without it, a single mistake or power outage erases hours of effort.

The trade-off is how often to save. Saving after every step guarantees zero progress loss, but writing multi-gigabyte tensors to disk every step can stall the GPU and slow training by 50% or more. Saving too rarely means losing hours of work. The optimal frequency balances disk write speed against the cost of retraining. Many teams save every epoch and additionally save the best validation checkpoint separately, giving them both recovery and model selection.

---

### Tiny Numeric Example

A model trains for 100 epochs. Checkpoints are written every 10 epochs.

| Event | Without Checkpointing | With Checkpointing |
|---|---|---|
| Crash at epoch 73 | Restart from epoch 0 | Restart from epoch 70 |
| Work lost | 73 epochs | 3 epochs |
| Recovery time | 73 epochs of retraining | 3 epochs of retraining |

If each epoch takes 2 hours on an 8-GPU cluster costing $30/hour:

- Without checkpointing: 146 hours lost = $4,380 wasted.
- With checkpointing: 6 hours lost = $180 wasted.

The checkpoint itself might be 10 GB and take 30 seconds to write. Writing it 10 times during training costs 5 minutes -- negligible compared to the recovery savings.

---

### Common Confusion

1. **"Checkpointing is the same as exporting a final model."** No. A checkpoint contains optimizer state and RNG seeds so training can resume. A final model file usually contains only weights for inference.

2. **"More frequent checkpoints always help."** No. Writing huge tensors to disk every step can stall the GPU and slow training significantly.

3. **"Checkpointing does not prevent crashes."** Correct. It only reduces the cost of recovery. You still need fault-tolerant hardware and health monitoring.

4. **"A checkpoint is a backup of the dataset."** No. It stores model state, not training data. The dataset must be restored separately.

5. **"Resuming from a checkpoint is automatic."** No. The training script must explicitly load the saved state and skip already-seen data.

---

### Where It Is Used in Our Code

`src/phase87/phase87_checkpointing.py` -- We build a dictionary with weights, optimizer momentum buffers, and the NumPy RNG state. We then reload that dictionary and verify that two runs starting from the same seed produce identical updates, proving that the checkpoint captured every piece of state needed for deterministic recovery.

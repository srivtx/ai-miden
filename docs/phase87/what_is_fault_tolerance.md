# What is Fault Tolerance?

## Why it exists (THE PROBLEM first)

Data centers experience disk failures, power outages, network splits, and preemption by higher-priority jobs. A single failed GPU out of eight can kill an entire distributed training run. Without fault tolerance, every hiccup becomes a catastrophic loss of days of compute.

## Definition (very simple)

Fault tolerance is the ability of a system to continue operating—or to restart cleanly from a saved state—when one or more of its components fail.

## Real-life analogy

A commercial airliner has multiple engines. If one engine fails, the plane does not crash; it continues flying on the remaining engines and lands safely. Fault tolerance in computing is the same idea: redundancy and graceful degradation.

## Tiny numeric example

A training job uses 8 GPUs. At step 50,000, GPU 3 overheats and dies. A fault-tolerant system detects the failure, checkpoints the state, restarts the job on the remaining 7 GPUs (or a replacement node), and resumes from step 50,000.

## Common confusion

- **Fault tolerance is not the same as high availability.** High availability means the system never goes down; fault tolerance means it recovers gracefully when it does.
- **Fault tolerance does not mean zero downtime.** There is usually a pause while the system restarts or redistributes work.
- **Checkpoints are necessary but not sufficient.** You also need health monitoring and automatic restart logic.
- **It is not only about hardware.** A bug that crashes a process is also a fault; tolerance mechanisms should catch and log it.
- **More replicas do not always help.** If all replicas run identical code with identical bugs, they will all fail simultaneously.

## Where it is used in our code

In `src/phase87/phase87_checkpointing.py`, we simulate a crash by destroying the in-memory training state and then restoring it from a checkpoint dictionary. The script demonstrates that recovery is possible because the checkpoint contained every piece of state needed to resume.

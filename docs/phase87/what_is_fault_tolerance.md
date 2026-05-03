## What Is Fault Tolerance?

---

### The Problem

Data centers experience disk failures, power outages, network splits, and preemption by higher-priority jobs. A single failed GPU out of eight can kill an entire distributed training run that has been running for days. Without fault tolerance, every hardware hiccup becomes a catastrophic loss of compute time, money, and experimental momentum. For large-scale training, faults are not exceptional; they are statistically inevitable.

---

### Definition

**Fault tolerance** is the ability of a system to continue operating -- or to restart cleanly from a saved state -- when one or more of its components fail.

**How it works:**
```
Normal operation:
  Train step -> train step -> checkpoint -> train step -> ...

Failure at step 50,000:
  1. Health monitor detects GPU 3 is unresponsive
  2. Training job is terminated
  3. Orchestrator reads last checkpoint (step 48,000)
  4. Job restarts on remaining 7 GPUs (or replacement node)
  5. Training resumes from step 48,000

Result: lost work = 2,000 steps, not 50,000 steps
```

**Key components:**
- **Health monitoring:** detecting failed nodes, GPUs, or network links.
- **Checkpointing:** saving state frequently enough to limit retraining.
- **Automatic restart:** orchestrators like Kubernetes or Slurm relaunch jobs.
- **Redundancy:** spare nodes or replicated data to handle hardware loss.

**Why this matters:**
- In a 1,000-GPU cluster, the mean time between failures is measured in hours, not weeks.
- Fault tolerance turns fragile long-running jobs into robust pipelines.

---

### Real-Life Analogy

A commercial airliner has multiple engines. If one engine fails, the plane does not crash; it continues flying on the remaining engines and lands safely. Fault tolerance in computing is the same idea: redundancy and graceful degradation. The plane also has backup electrical systems, backup hydraulics, and emergency oxygen. No single point of failure destroys the mission.

The trade-off is weight and cost. Every redundant engine adds mass that reduces fuel efficiency. In computing, fault tolerance requires extra infrastructure: health monitors, checkpoint storage, spare nodes, and orchestration logic. These resources could otherwise be used for additional training. A perfectly fault-tolerant system is also perfectly expensive. In practice, teams accept a bounded recovery time -- say, retraining at most 2 hours of work -- rather than trying to eliminate all failure risk, because the cost of perfect tolerance exceeds the cost of occasional retraining.

---

### Tiny Numeric Example

A training job uses 8 GPUs for 100,000 steps. The mean time between GPU failures is 25,000 steps per GPU.

**Without fault tolerance:**
| Failure | Step | Result |
|---|---|---|
| GPU 3 dies | 50,000 | Entire job fails. 50,000 steps lost. |
| Restart from 0 | 0 | Must retrain 50,000 steps. |

**With fault tolerance (checkpoint every 2,000 steps):**
| Failure | Step | Recovery | Lost Work |
|---|---|---|---|
| GPU 3 dies | 50,000 | Restart from checkpoint 48,000 | 2,000 steps |
| GPU 7 dies | 75,000 | Restart from checkpoint 74,000 | 1,000 steps |

Total lost work: 3,000 steps instead of 50,000. At $30/hour for 8 GPUs and 10 minutes per 1,000 steps, the savings are roughly $2,250 in compute cost for the first failure alone.

---

### Common Confusion

1. **"Fault tolerance is the same as high availability."** No. High availability means the system never goes down. Fault tolerance means it recovers gracefully when it does.

2. **"Fault tolerance means zero downtime."** No. There is usually a pause while the system restarts or redistributes work across remaining nodes.

3. **"Checkpoints are necessary but not sufficient for fault tolerance."** Correct. You also need health monitoring to detect failures and automatic restart logic to resume the job.

4. **"Fault tolerance is only about hardware."** No. A bug that crashes a process is also a fault; tolerance mechanisms should catch, log, and recover from software failures too.

5. **"More replicas always improve fault tolerance."** No. If all replicas run identical code with identical bugs, they will all fail simultaneously. Diversity in implementation or data is required for true resilience.

---

### Where It Is Used in Our Code

`src/phase87/phase87_checkpointing.py` -- We simulate a crash by destroying the in-memory training state and then restoring it from a checkpoint dictionary. The script demonstrates that recovery is possible because the checkpoint contained every piece of state needed to resume, illustrating the core principle of fault tolerance.

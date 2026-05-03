# Phase 88: Docker, Kubernetes & ML Orchestration

## What We Learned

1. **Containerization solves environment reproducibility.** Packaging code with all dependencies into a container image guarantees identical behavior across laptops, servers, and cloud VMs, eliminating "works on my machine" failures.
2. **Kubernetes automates deployment and recovery at scale.** Its control plane schedules pods across clusters, reschedules workloads when nodes fail, and enables rolling updates without downtime.
3. **Orchestration coordinates complex pipelines.** It enforces dependency order, matches tasks to available resources, and retries failed steps automatically, turning fragile manual workflows into reliable systems.
4. **Resource-aware scheduling maximizes utilization.** Bin-packing jobs onto nodes based on CPU, GPU, and memory constraints can raise cluster utilization from below 40% to above 85%.
5. **These layers stack:** containers provide the unit of deployment, Kubernetes manages the cluster, and orchestrators manage the pipeline graph on top.
6. **Operational complexity is the trade-off.** Kubernetes and orchestrators shine for dynamic, large-scale workloads but may be overkill for a single researcher running one experiment on a laptop.

## Prerequisites

- Basic familiarity with Linux command line and shell scripting
- Understanding of Python virtual environments and `pip` dependency management
- Familiarity with client-server architecture and REST APIs
- Prior exposure to distributed computing concepts (nodes, clusters, scheduling)

## Recommended Reading Order

1. `what_is_containerization.md` — Understand the foundational packaging layer
2. `what_is_kubernetes.md` — Learn how containers are deployed and managed at scale
3. `what_is_orchestration.md` — See how multi-step pipelines are coordinated on top of Kubernetes

## Visual Outputs

- `src/phase88/scheduler_utilization.png` — Grouped bar chart comparing CPU, GPU, and memory utilization across three simulated cluster nodes after job assignment.

## Navigation

- [Previous Phase](../phase87/SUMMARY.md)
- [Next Phase](../phase89/SUMMARY.md)

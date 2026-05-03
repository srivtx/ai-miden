# What is Kubernetes?

## Why it exists (THE PROBLEM first)

Running one container is easy. Running one hundred containers across twenty machines, restarting failed ones, balancing load, and rolling out updates without downtime is impossibly complex to manage by hand. A control plane is needed.

## Definition (very simple)

Kubernetes (K8s) is an open-source platform that automates the deployment, scaling, and management of containerized applications across a cluster of machines.

## Real-life analogy

An airport control tower tracks every plane, assigns runways, schedules takeoffs and landings, and reroutes traffic when a runway closes. Kubernetes is the control tower for containers: it tracks every pod, assigns nodes, and reroutes work when a machine fails.

## Tiny numeric example

A cluster has 10 nodes. Kubernetes receives a request to run 50 training pods, each needing 1 GPU. It places 5 pods on each node. When node 7 goes offline, Kubernetes automatically reschedules those 5 pods onto the 9 remaining nodes that have free GPUs.

## Common confusion

- **Kubernetes does not run containers directly.** It uses a container runtime (like containerd) under the hood.
- **A pod is not a container.** A pod is the smallest deployable unit and can hold one or more tightly coupled containers.
- **Kubernetes is not a cloud provider.** It runs on top of cloud VMs or bare metal; it does not rent machines for you.
- **It does not auto-optimize your model.** It optimizes placement and scaling, not training hyperparameters.
- **Kubectl is not Kubernetes.** Kubectl is merely the command-line client that talks to the Kubernetes API server.

## Where it is used in our code

In `src/phase88/phase88_orchestration.py`, we simulate nodes and a scheduler that assigns jobs. Kubernetes performs this scheduling at scale, using concepts like resource requests, limits, and node affinity to decide where each containerized job should run.

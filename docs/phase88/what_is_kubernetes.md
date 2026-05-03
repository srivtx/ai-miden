## What Is Kubernetes?

---

## The Problem

Running one container is easy. Running one hundred containers across twenty machines, restarting failed ones, balancing load, and rolling out updates without downtime is impossibly complex to manage by hand. Without a control plane, a single machine failure strands dozens of workloads, and updates require manual SSH into every server. How do you automate deployment, scaling, and recovery at container scale?

---

## Definition

**Kubernetes** (K8s) is an open-source platform that automates the deployment, scaling, and management of containerized applications across a cluster of machines.

**How it works:**
```
Cluster components:
  - API server: receives deployment requests and desired state
  - etcd: distributed key-value store holding cluster state
  - Scheduler: watches for unscheduled pods and assigns them to nodes
  - Controller manager: detects failures and reschedules pods
  - Kubelet: agent on each node that talks to the container runtime
  - Container runtime (containerd/CRI-O): actually starts and stops containers

Deployment flow:
  1. Engineer sends YAML manifest to API server
  2. API server writes desired state to etcd
  3. Scheduler picks a node with enough CPU, memory, and GPU
  4. Kubelet on that node instructs container runtime to pull image and run pod
  5. Controller manager monitors health; if pod fails, it creates a replacement
```

**Why this matters:**
- A manual deployment to 20 nodes takes hours and is error-prone; Kubernetes does it in seconds declaratively.
- Rolling updates replace pods gradually, so serving traffic never drops to zero.
- Horizontal pod autoscaling adds replicas when CPU usage exceeds a threshold.

---

## Real-Life Analogy

An airport control tower tracks every plane, assigns runways, schedules takeoffs and landings, and reroutes traffic when a runway closes. Kubernetes is the control tower for containers: it tracks every pod, assigns nodes, and reroutes work when a machine fails.

Consider a busy international airport with fifty gates, multiple runways, and hundreds of daily flights. The control tower does not fly the planes, load luggage, or serve meals. It maintains a real-time map of every aircraft's position, fuel level, and scheduled route. When gate 12 breaks, the tower instantly reassigns the waiting flight to gate 14 and broadcasts the change to passengers and crew. When fog closes runway 2, inbound flights are redirected to runway 1 with adjusted approach paths. Kubernetes behaves identically: the API server is the radar screen, the scheduler is the gate-assigner, and the controller manager is the emergency rerouter.

**The trade-off:** Kubernetes adds significant operational complexity. A team running three static web servers may spend more time maintaining the cluster than maintaining the apps. The benefits outweigh the costs only when the workload is dynamic, distributed, and large enough that manual management is untenable.

---

## Tiny Numeric Example

**Manual container management across 10 nodes:**

| Request | Needs (GPU) | Assigned Node | Outcome |
|---------|-------------|---------------|---------|
| 50 training pods | 1 each | Nodes 0-9 (5 per node) | OK |
| Node 7 goes offline | — | — | 5 pods lost |
| Manual recovery | — | Engineer SSHs to nodes | 20 min downtime |

- Total GPU utilization before failure: 100%
- Downtime after failure: 20 minutes
- Human intervention required: yes

**Kubernetes-managed recovery:**

| Event | Action | Outcome |
|-------|--------|---------|
| 50 training pods requested | Scheduler places 5 per node | Running in 10 seconds |
| Node 7 goes offline | Controller detects missing pods | Automatic |
| Pods rescheduled | Scheduler finds 9 healthy nodes with free GPUs | 5 pods spread onto remaining nodes |
| Downtime | Zero | Traffic never dropped |

- Total GPU utilization after recovery: 100% (slightly more crowded on 9 nodes)
- Downtime: 0 seconds
- Human intervention: none

---

## Common Confusion

1. **"Kubernetes runs containers directly."** It does not. It uses a container runtime like containerd or CRI-O under the hood. Kubernetes is the control plane; the runtime is the executor.

2. **"A pod is a container."** A pod is the smallest deployable unit and can hold one or more tightly coupled containers that share network and storage. Most pods contain one container, but sidecar patterns use two or more.

3. **"Kubernetes is a cloud provider."** It is not. It runs on top of cloud VMs or bare metal. It does not rent machines; it orchestrates workloads on machines you already have.

4. **"It auto-optimizes your model."** Kubernetes optimizes placement and scaling, not training hyperparameters or architecture choices.

5. **"Kubectl is Kubernetes."** Kubectl is merely the command-line client that talks to the Kubernetes API server. The real system lives in the cluster control plane.

6. **"Kubernetes eliminates all downtime."** It reduces downtime through self-healing, but if an entire data center loses power, the cluster cannot magically recover without redundant infrastructure.

7. **"You must use Docker with Kubernetes."** Docker was the default runtime historically, but modern Kubernetes clusters often use containerd or Podman-compatible runtimes instead.

---

## Where It Is Used in Our Code

`src/phase88/phase88_orchestration.py` — We simulate nodes and a scheduler that assigns jobs based on CPU, GPU, and memory availability. Kubernetes performs this scheduling at production scale, using concepts like resource requests, limits, and node affinity to decide where each containerized job should run. The toy script captures the same bin-packing logic that K8s implements across thousands of nodes.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: Real schedulers assign ML jobs to machines based on resource needs.
# If a job needs 2 GPUs and a node has 1, it cannot run there.

np.random.seed(88)

# Simulate nodes with CPU, GPU, Memory
nodes = np.array([
    [8, 2, 32],   # node 0: 8 CPU, 2 GPU, 32 GB RAM
    [16, 4, 64],  # node 1
    [4, 1, 16],   # node 2
], dtype=float)

jobs = np.array([
    [2, 1, 8],    # job 0
    [4, 2, 16],   # job 1
    [1, 0, 4],    # job 2
    [8, 4, 32],   # job 3
    [2, 1, 8],    # job 4
], dtype=float)

# WHY: Bin packing tries to fit as many jobs as possible into each node.
assignments = [[] for _ in nodes]
remaining = nodes.copy()

for j_idx, job in enumerate(jobs):
    placed = False
    # WHY: Try each node to see if it fits (First Fit Decreasing concept simplified)
    for n_idx in range(len(nodes)):
        if np.all(remaining[n_idx] >= job):
            remaining[n_idx] -= job
            assignments[n_idx].append(j_idx)
            placed = True
            break
    if not placed:
        print(f"Job {j_idx} could not be placed (needs {job}, insufficient resources).")

print("Node assignments:", assignments)
print("Remaining resources per node:\n", remaining)

# WHY: Visualize utilization before and after.
fig, ax = plt.subplots()
utilization = 1 - (remaining / nodes)
x = np.arange(len(nodes))
width = 0.25
ax.bar(x - width, utilization[:, 0], width, label='CPU Util')
ax.bar(x, utilization[:, 1], width, label='GPU Util')
ax.bar(x + width, utilization[:, 2], width, label='Mem Util')
ax.set_ylabel('Utilization')
ax.set_title('Simulated Scheduler Resource Utilization')
ax.set_xticks(x)
ax.set_xticklabels([f'Node {i}' for i in range(len(nodes))])
ax.legend()
fig.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase88/scheduler_utilization.png')
print("Saved plot to scheduler_utilization.png")

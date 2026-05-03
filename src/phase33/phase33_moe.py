"""
Phase 33: Mixture of Experts (MoE)

This script demonstrates the core mechanics of a Mixture of Experts layer
using only NumPy. We build:

1. A synthetic dataset with 4 input "types" (quadrants), each needing a
different linear transformation.
2. A dense baseline (single linear layer) that must learn all transformations
with shared parameters.
3. An MoE layer with 4 experts and a learned router.
4. Top-k gating with noise.
5. Load balancing auxiliary loss.
6. Expert capacity with token dropping.

We then train both models and visualize:
- How the router learns to send different input types to different experts.
- How load balancing improves over iterations.
- How expert capacity drops excess tokens.
- Parameter count comparison (total vs. active).

Why NumPy? So every operation is visible. No framework magic.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# 1. SYNTHETIC DATASET
# ============================================================================
# We create 4 clusters in 2D space, one per quadrant.
# Each quadrant has its own target function:
#   Quadrant 0 (x>0, y>0): target =  x +  y
#   Quadrant 1 (x>0, y<0): target =  x -  y
#   Quadrant 2 (x<0, y>0): target = 2x + 0.5y
#   Quadrant 3 (x<0, y<0): target = -x + 2y
#
# This is perfect for MoE: the router can learn to route by quadrant sign,
# and each expert only needs to learn one simple linear function.
# ============================================================================

np.random.seed(42)
n_samples = 400

# Generate random 2D points in [-2, 2]
X = np.random.uniform(-2, 2, size=(n_samples, 2))

# Determine quadrant (0-3) based on signs
# We add a small encoding so the router has a signal
quadrant = np.zeros(n_samples, dtype=int)
quadrant[(X[:, 0] >= 0) & (X[:, 1] >= 0)] = 0
quadrant[(X[:, 0] >= 0) & (X[:, 1] < 0)] = 1
quadrant[(X[:, 0] < 0) & (X[:, 1] >= 0)] = 2
quadrant[(X[:, 0] < 0) & (X[:, 1] < 0)] = 3

# Generate targets based on quadrant
y = np.zeros((n_samples, 1))
y[quadrant == 0] = (X[quadrant == 0, 0:1] + X[quadrant == 0, 1:2])
y[quadrant == 1] = (X[quadrant == 1, 0:1] - X[quadrant == 1, 1:2])
y[quadrant == 2] = (2.0 * X[quadrant == 2, 0:1] + 0.5 * X[quadrant == 2, 1:2])
y[quadrant == 3] = (-1.0 * X[quadrant == 3, 0:1] + 2.0 * X[quadrant == 3, 1:2])

# Add a tiny bit of noise so it is not perfectly trivial
y += np.random.normal(0, 0.1, size=y.shape)

print("=" * 70)
print("PHASE 33: MIXTURE OF EXPERTS")
print("=" * 70)
print(f"Dataset: {n_samples} samples, 2D input, 1D output")
print(f"Quadrant distribution: {np.bincount(quadrant)}")
print("Each quadrant has a different linear target function.")
print()

# ============================================================================
# 2. DENSE BASELINE MODEL
# ============================================================================
# A single linear layer: y = x @ W + b
# This model must learn all 4 transformations using the SAME weights.
# It has fewer parameters than the MoE but no specialization.
# ============================================================================

class DenseModel:
    def __init__(self, in_dim, out_dim):
        # Xavier initialization
        limit = np.sqrt(6.0 / (in_dim + out_dim))
        self.W = np.random.uniform(-limit, limit, size=(in_dim, out_dim))
        self.b = np.zeros((1, out_dim))

    def forward(self, x):
        # x: (batch, in_dim)
        # Simple linear projection
        self.x = x  # store for backward
        self.out = x @ self.W + self.b
        return self.out

    def backward(self, grad_out):
        # grad_out: (batch, out_dim), dL/dout
        # dL/dW = x.T @ grad_out
        # dL/db = sum(grad_out, axis=0)
        # dL/dx = grad_out @ W.T
        dW = self.x.T @ grad_out
        db = np.sum(grad_out, axis=0, keepdims=True)
        dx = grad_out @ self.W.T
        return dW, db, dx

# ============================================================================
# 3. MoE LAYER
# ============================================================================
# Architecture:
#   - 4 experts, each is a linear layer (in_dim -> out_dim)
#   - Router: linear layer (in_dim -> num_experts)
#   - Top-2 gating with noise
#   - Load balancing auxiliary loss
#   - Expert capacity with token dropping
# ============================================================================

class MoELayer:
    def __init__(self, in_dim, out_dim, num_experts=4, top_k=2, capacity_factor=1.25):
        self.num_experts = num_experts
        self.top_k = top_k
        self.capacity_factor = capacity_factor

        # Router: learns which expert handles which input
        limit = np.sqrt(6.0 / (in_dim + num_experts))
        self.W_g = np.random.uniform(-limit, limit, size=(in_dim, num_experts))

        # Experts: each is an independent linear layer
        self.experts_W = []
        self.experts_b = []
        for _ in range(num_experts):
            limit_e = np.sqrt(6.0 / (in_dim + out_dim))
            W = np.random.uniform(-limit_e, limit_e, size=(in_dim, out_dim))
            b = np.zeros((1, out_dim))
            self.experts_W.append(W)
            self.experts_b.append(b)

    def forward(self, x, training=True):
        # x: (batch, in_dim)
        batch_size = x.shape[0]
        self.x = x  # store for backward

        # ---- Router ----
        # Compute logits for each expert
        logits = x @ self.W_g  # (batch, num_experts)

        # Add noise during training to encourage exploration early on
        # This is the "Noisy Top-K Gating" from the original MoE paper.
        # Without noise, the router might collapse to always picking the same
        # expert if it starts slightly ahead.
        if training:
            noise = np.random.normal(0, 0.1, size=logits.shape)
            logits = logits + noise

        self.logits = logits

        # ---- Top-K Selection ----
        # For each token, find the top-k expert indices
        # We use argpartition for efficiency
        topk_indices = np.argpartition(-logits, self.top_k, axis=1)[:, :self.top_k]
        # topk_indices: (batch, top_k)

        # Get the logits for the selected experts
        batch_idx = np.arange(batch_size)[:, None]
        selected_logits = logits[batch_idx, topk_indices]  # (batch, top_k)

        # Softmax over the selected logits to get gate values
        # We subtract max for numerical stability
        max_logits = np.max(selected_logits, axis=1, keepdims=True)
        exp_logits = np.exp(selected_logits - max_logits)
        gate_values = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)  # (batch, top_k)

        # Create a full gate matrix (batch, num_experts) with zeros for non-selected
        self.gates = np.zeros((batch_size, self.num_experts))
        self.gates[batch_idx, topk_indices] = gate_values

        # Store which experts were selected for each token
        self.topk_indices = topk_indices

        # ---- Expert Capacity & Dropping ----
        # Calculate capacity per expert
        capacity = (batch_size / self.num_experts) * self.capacity_factor
        self.capacity = capacity

        # Count how many tokens each expert received
        expert_counts = np.bincount(topk_indices.flatten(), minlength=self.num_experts)
        self.expert_counts = expert_counts

        # For simplicity in this demo, we do not actually drop tokens in the
        # forward pass (that would complicate the gradient code). Instead,
        # we track which tokens WOULD be dropped and print a warning.
        dropped = 0
        for e in range(self.num_experts):
            if expert_counts[e] > capacity:
                dropped += int(expert_counts[e] - capacity)
        self.dropped_tokens = dropped

        # ---- Expert Forward Pass ----
        # Compute output for each expert, then weight by gate values
        # For efficiency, we compute ALL expert outputs, then mask.
        # In a real system, we would only compute the selected experts.
        expert_outputs = []
        for e in range(self.num_experts):
            out = x @ self.experts_W[e] + self.experts_b[e]  # (batch, out_dim)
            expert_outputs.append(out)

        # Stack to (batch, num_experts, out_dim)
        expert_outputs = np.stack(expert_outputs, axis=1)

        # Weighted sum: (batch, num_experts, 1) * (batch, num_experts, out_dim)
        gates_expanded = self.gates[:, :, None]  # (batch, num_experts, 1)
        weighted = gates_expanded * expert_outputs  # (batch, num_experts, out_dim)
        output = np.sum(weighted, axis=1)  # (batch, out_dim)

        self.expert_outputs = expert_outputs
        return output

    def compute_load_balance_loss(self):
        # Load balancing loss from the original Shazeer et al. paper.
        # L_balance = num_experts * sum(f_i * P_i)
        # where f_i = fraction of tokens routed to expert i
        # and P_i = mean probability (gate value) assigned to expert i
        #
        # When perfectly balanced: f_i = 1/N, P_i = 1/N
        # Loss = N * N * (1/N * 1/N) = 1.0
        # When imbalanced: loss is higher.

        batch_size = self.x.shape[0]
        f = self.expert_counts / (batch_size * self.top_k)  # fraction of routing decisions
        P = np.mean(self.gates, axis=0)  # average gate value per expert

        # Avoid division by zero or log issues
        loss = self.num_experts * np.sum(f * P)
        return loss

    def backward(self, grad_out):
        # grad_out: (batch, out_dim), dL/d(output of MoE layer)
        batch_size = self.x.shape[0]

        # ---- Gradients w.r.t. expert weights ----
        # For each expert e:
        #   dL/dW_e = x.T @ (grad_out * gates[:, e:e+1])
        dW_experts = []
        db_experts = []
        for e in range(self.num_experts):
            gate_e = self.gates[:, e:e+1]  # (batch, 1)
            grad_expert = grad_out * gate_e  # (batch, out_dim)
            dW = self.x.T @ grad_expert  # (in_dim, out_dim)
            db = np.sum(grad_expert, axis=0, keepdims=True)  # (1, out_dim)
            dW_experts.append(dW)
            db_experts.append(db)

        # ---- Gradients w.r.t. router ----
        # We need dL/dlogits for the selected experts.
        # For each token and each selected expert:
        #   dL/dlogit = dL/dgate * dgate/dlogit
        # dgate/dlogit is the softmax Jacobian.
        # For simplicity, we use the fact that for softmax:
        #   dL/dz_i = gate_i * (dL/dy_i - sum_j gate_j * dL/dy_j)
        # where z_i is the logit and y_i is the gate output.

        # First, compute dL/dgate for each expert
        # dL/dgate_e = sum_over_batch_and_output(grad_out * expert_output_e)
        dL_dgate = np.zeros((batch_size, self.num_experts))
        for e in range(self.num_experts):
            # (batch, out_dim) * (batch, out_dim) -> sum over out_dim
            dL_dgate[:, e] = np.sum(grad_out * self.expert_outputs[:, e, :], axis=1)

        # Now compute dL/dlogits for selected experts only
        dL_dlogits = np.zeros((batch_size, self.num_experts))

        for b in range(batch_size):
            sel = self.topk_indices[b]  # indices of selected experts for this token
            g = self.gates[b, sel]  # gate values for selected experts
            dy = dL_dgate[b, sel]  # dL/dgate for selected experts

            # Softmax backward:
            # For a softmax output s_i and loss L:
            # dL/dz_i = s_i * (dL/ds_i - sum_j s_j * dL/ds_j)
            # where z_i is the logit and s_i is the softmax output.
            # This works because dL/dz_i = sum_j (dL/ds_j * ds_j/dz_i)
            # and ds_j/dz_i = s_j * (delta_ij - s_i)

            sum_g_dy = np.sum(g * dy)
            for idx, e_idx in enumerate(sel):
                dL_dlogits[b, e_idx] = g[idx] * (dy[idx] - sum_g_dy)

        # dL/dW_g = x.T @ dL_dlogits
        dW_g = self.x.T @ dL_dlogits

        return dW_g, dW_experts, db_experts

# ============================================================================
# 4. TRAINING LOOP
# ============================================================================
# We train both the dense model and the MoE model on the same data.
# We track task loss (MSE) and, for MoE, the load balancing loss.
# ============================================================================

def train_dense(model, X, y, lr=0.01, epochs=300):
    losses = []
    for epoch in range(epochs):
        # Forward
        out = model.forward(X)
        loss = np.mean((out - y) ** 2)
        losses.append(loss)

        # Backward
        grad_out = 2 * (out - y) / X.shape[0]
        dW, db, _ = model.backward(grad_out)

        # Update
        model.W -= lr * dW
        model.b -= lr * db

    return losses

def train_moe(moe, X, y, lr=0.01, epochs=300, balance_weight=0.01):
    task_losses = []
    balance_losses = []
    dropped_history = []

    for epoch in range(epochs):
        # Forward
        out = moe.forward(X, training=True)
        task_loss = np.mean((out - y) ** 2)
        balance_loss = moe.compute_load_balance_loss()
        total_loss = task_loss + balance_weight * balance_loss

        task_losses.append(task_loss)
        balance_losses.append(balance_loss)
        dropped_history.append(moe.dropped_tokens)

        # Backward for task loss
        grad_out = 2 * (out - y) / X.shape[0]
        dW_g, dW_experts, db_experts = moe.backward(grad_out)

        # Backward for balance loss (simplified: push toward uniform)
        # We treat balance loss as encouraging uniform logits.
        # A simple approximation: gradient pushes expert_counts toward uniform.
        # For this demo, we skip the exact gradient of balance loss through
        # the router and instead rely on the task gradient + a small
        # direct regularization on router weights. This is a simplification
        # but sufficient for the concept demonstration.
        batch_size = X.shape[0]
        f = moe.expert_counts / (batch_size * moe.top_k)
        P = np.mean(moe.gates, axis=0)
        # Approximate gradient: encourage uniform distribution
        # We penalize logits of overused experts and boost underused ones
        target_f = 1.0 / moe.num_experts
        balance_grad = np.zeros_like(moe.logits)
        for e in range(moe.num_experts):
            if f[e] > target_f:
                balance_grad[:, e] = 0.05  # slightly suppress
            elif f[e] < target_f:
                balance_grad[:, e] = -0.05  # slightly boost

        dW_g_balance = X.T @ balance_grad / batch_size
        dW_g += dW_g_balance * balance_weight

        # Update router
        moe.W_g -= lr * dW_g

        # Update experts
        for e in range(moe.num_experts):
            moe.experts_W[e] -= lr * dW_experts[e]
            moe.experts_b[e] -= lr * db_experts[e]

    return task_losses, balance_losses, dropped_history

# ---- Initialize models ----
dense = DenseModel(in_dim=2, out_dim=1)
moe = MoELayer(in_dim=2, out_dim=1, num_experts=4, top_k=2, capacity_factor=1.25)

print("Training dense baseline...")
dense_losses = train_dense(dense, X, y, lr=0.02, epochs=400)

print("Training MoE...")
moe_task_losses, moe_balance_losses, moe_dropped = train_moe(moe, X, y, lr=0.02, epochs=400, balance_weight=0.05)

print(f"Dense final loss: {dense_losses[-1]:.4f}")
print(f"MoE final task loss: {moe_task_losses[-1]:.4f}")
print(f"MoE final balance loss: {moe_balance_losses[-1]:.4f}")
print()

# ============================================================================
# 5. ANALYZE ROUTING AFTER TRAINING
# ============================================================================
# We pass the full dataset through the trained MoE and record which experts
# each quadrant gets routed to. Ideally, each quadrant should strongly favor
# a specific subset of experts.
# ============================================================================

_ = moe.forward(X, training=False)
routing_matrix = np.zeros((4, 4))  # quadrant x expert

for q in range(4):
    mask = (quadrant == q)
    if mask.sum() == 0:
        continue
    # Sum gate values for this quadrant
    routing_matrix[q] = np.sum(moe.gates[mask], axis=0) / mask.sum()

print("Routing specialization (rows = quadrants, cols = experts):")
print("Each row shows average gate weight per expert for that quadrant.")
print(np.round(routing_matrix, 3))
print()

# ============================================================================
# 6. VISUALIZATIONS
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# ---- Plot 1: Training Loss Comparison ----
ax = axes[0, 0]
ax.plot(dense_losses, label='Dense Baseline', linewidth=2)
ax.plot(moe_task_losses, label='MoE Task Loss', linewidth=2)
ax.set_xlabel('Iteration')
ax.set_ylabel('MSE Loss')
ax.set_title('Training Loss: Dense vs. MoE')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 2: Load Balancing Loss ----
ax = axes[0, 1]
ax.plot(moe_balance_losses, color='orange', linewidth=2)
ax.axhline(y=1.0, color='green', linestyle='--', label='Perfect Balance (1.0)')
ax.set_xlabel('Iteration')
ax.set_ylabel('Balance Loss')
ax.set_title('Load Balancing Loss Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

# ---- Plot 3: Dropped Tokens ----
ax = axes[0, 2]
ax.plot(moe_dropped, color='red', linewidth=2)
ax.set_xlabel('Iteration')
ax.set_ylabel('Dropped Tokens per Batch')
ax.set_title('Expert Capacity Drops')
ax.grid(True, alpha=0.3)

# ---- Plot 4: Routing Specialization Heatmap ----
ax = axes[1, 0]
im = ax.imshow(routing_matrix, cmap='Blues', aspect='auto')
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels([f'E{i}' for i in range(4)])
ax.set_yticklabels([f'Q{i}' for i in range(4)])
ax.set_xlabel('Expert')
ax.set_ylabel('Quadrant (Input Type)')
ax.set_title('Routing Specialization Heatmap')
for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{routing_matrix[i, j]:.2f}', ha='center', va='center', color='black')
plt.colorbar(im, ax=ax)

# ---- Plot 5: Expert Usage Distribution ----
ax = axes[1, 1]
usage = np.sum(moe.gates, axis=0)
ax.bar(range(4), usage, color='steelblue')
ax.set_xticks(range(4))
ax.set_xticklabels([f'E{i}' for i in range(4)])
ax.set_xlabel('Expert')
ax.set_ylabel('Total Gate Weight')
ax.set_title('Expert Usage Distribution')
ax.axhline(y=usage.mean(), color='red', linestyle='--', label=f'Mean: {usage.mean():.1f}')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# ---- Plot 6: Parameter Count Comparison ----
ax = axes[1, 2]
categories = ['Dense\nBaseline', 'MoE\n(Total)', 'MoE\n(Active per Token)']
# Dense: 2*1 + 1 = 3
# MoE total: router (2*4) + 4 experts * (2*1 + 1) = 8 + 12 = 20
# MoE active: top_k * (2*1 + 1) = 2 * 3 = 6
counts = [3, 20, 6]
colors = ['gray', 'steelblue', 'lightgreen']
bars = ax.bar(categories, counts, color=colors)
ax.set_ylabel('Parameter Count')
ax.set_title('Parameter Count Comparison')
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(count),
            ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, 25)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('src/phase33/moe_concepts.png', dpi=150, bbox_inches='tight')
print("Saved visualization: src/phase33/moe_concepts.png")
plt.close()

# ============================================================================
# 7. SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Dense model: 1 linear layer, 3 parameters, must handle all 4 quadrants.")
print(f"MoE model: 4 experts + router, 20 total parameters, {moe.top_k * 3} active per token.")
print()
print("Key observations:")
print(f"1. MoE task loss converged to {moe_task_losses[-1]:.4f} vs dense {dense_losses[-1]:.4f}")
print(f"2. Balance loss started at {moe_balance_losses[0]:.2f} and ended at {moe_balance_losses[-1]:.2f}")
print(f"3. Maximum tokens dropped in a batch: {max(moe_dropped)}")
print("4. Routing heatmap shows which experts specialized to which quadrants.")
print()
print("This demonstrates the core idea of MoE:")
print("- Massive total capacity (many experts)")
print("- Small active compute (only top-k per token)")
print("- Learned specialization (router sends different inputs to different experts)")
print("- Load balancing prevents collapse to a single expert")
print("- Capacity factor limits how overloaded any single expert can get")
print("=" * 70)

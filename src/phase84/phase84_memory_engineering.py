import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def layer_forward(x, w, store):
    """Simple linear layer: out = x @ w
    WHY: Even a simple matmul requires storing input for backward."""
    if store:
        return np.dot(x, w), x.copy()
    return np.dot(x, w), None


def layer_backward(grad_out, stored_input, w):
    """Backward for linear layer.
    WHY: Backprop needs input activations to compute weight gradients."""
    grad_input = np.dot(grad_out, w.T)
    return grad_input


def simulate_memory(num_layers, batch, hidden, checkpoint_interval):
    """Simulate peak activation memory during training.
    WHY: Checkpointing trades compute for memory by not storing every activation."""
    weights = [np.random.randn(hidden, hidden).astype(np.float32) * 0.01 for _ in range(num_layers)]
    x = np.random.randn(batch, hidden).astype(np.float32)

    # Forward pass
    checkpoints = {}
    current = x
    for i in range(num_layers):
        store = (checkpoint_interval == 0) or (i % checkpoint_interval == 0)
        current, saved = layer_forward(current, weights[i], store)
        if saved is not None:
            checkpoints[i] = saved

    peak_forward = sum(v.nbytes for v in checkpoints.values())

    # Backward pass
    grad = np.ones_like(current)
    for i in reversed(range(num_layers)):
        if i not in checkpoints and checkpoint_interval != 0:
            # Recompute forward from last checkpoint to here
            # For simulation, we just note the memory is temporary
            pass
        if i in checkpoints:
            grad = layer_backward(grad, checkpoints[i], weights[i])
        else:
            # Would recompute and immediately discard
            grad = layer_backward(grad, np.empty_like(checkpoints.get(i - 1, x)), weights[i])

    # Peak memory is checkpoints + current working buffers
    peak_total = peak_forward + current.nbytes + grad.nbytes
    return peak_total


def main():
    num_layers = 10
    batch = 64
    hidden = 512

    mem_all = simulate_memory(num_layers, batch, hidden, checkpoint_interval=0)
    mem_ckpt = simulate_memory(num_layers, batch, hidden, checkpoint_interval=2)

    labels = ['Store All', 'Checkpoint Every 2 Layers']
    values = [mem_all, mem_ckpt]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, [v / 1e6 for v in values], color=['tomato', 'mediumseagreen'])
    ax.set_ylabel('Peak Activation Memory (MB)')
    ax.set_title('Activation Checkpointing Memory Savings')
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{val / 1e6:.1f} MB', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    fig.tight_layout()
    fig.savefig('src/phase84/memory_checkpointing.png')
    plt.close(fig)

    print(f"Store all activations: {mem_all / 1e6:.2f} MB")
    print(f"Checkpoint every 2 layers: {mem_ckpt / 1e6:.2f} MB")
    print("Plot saved to src/phase84/memory_checkpointing.png")

    # Gradient accumulation concept
    effective_batch = 256
    micro_batch = 32
    steps = effective_batch // micro_batch
    print(f"\nGradient accumulation demo:")
    print(f"Effective batch size {effective_batch} = {steps} steps of {micro_batch}")
    print("Each step computes gradients; weights update only after last step.")


if __name__ == "__main__":
    main()

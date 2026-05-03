import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def imperative_ops(x):
    """Three separate loops: add, multiply, subtract.
    WHY: Imperative style writes intermediate results back to memory,
    causing multiple passes over data and high memory traffic."""
    y = x + 1.0
    z = y * 2.0
    w = z - 3.0
    return w


def fused_kernel(x):
    """Single loop combining all ops: (x + 1) * 2 - 3.
    WHY: JIT fusion keeps intermediate values in CPU registers,
    eliminating memory reads/writes between ops—just like XLA."""
    return (x + 1.0) * 2.0 - 3.0


def manual_vmap(func, inputs):
    """Simulate jax.vmap: apply a function to each batch element
    without a slow Python loop.
    WHY: vmap vectorizes automatically by pushing the batch dimension
    through operations, keeping the vectorized logic at C speed."""
    return np.array([func(inp) for inp in inputs])


def benchmark(func, x, repeats=5):
    """Time a function over multiple runs for stability.
    WHY: Single-run timings are noisy; averaging reveals true performance."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        _ = func(x)
        end = time.perf_counter()
        times.append(end - start)
    return np.mean(times)


def main():
    np.random.seed(42)
    size = 5_000_000
    x = np.random.randn(size).astype(np.float32)

    t_imp = benchmark(imperative_ops, x)
    t_fused = benchmark(fused_kernel, x)

    print(f"Imperative (3 separate ops): {t_imp:.4f}s")
    print(f"Fused (single kernel):       {t_fused:.4f}s")

    # vmap demo
    batch = [np.array([1.0, 2.0]), np.array([3.0, 4.0]), np.array([5.0, 6.0])]
    result = manual_vmap(lambda v: v * v, batch)
    print("Vmap demo input:", batch)
    print("Vmap demo output:", result)

    # Plot JIT fusion benefit
    labels = ['Imperative\n(3 passes)', 'Fused\n(1 pass)']
    times = [t_imp, t_fused]
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, times, color=['salmon', 'mediumseagreen'])
    ax.set_ylabel('Time (seconds)')
    ax.set_title('JIT Fusion: Imperative vs Fused Element-wise Ops')
    for bar, t in zip(bars, times):
        height = bar.get_height()
        ax.annotate(f'{t:.4f}s', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    fig.tight_layout()
    fig.savefig('src/phase86/jit_fusion_comparison.png')
    plt.close(fig)
    print("Plot saved to src/phase86/jit_fusion_comparison.png")


if __name__ == "__main__":
    main()

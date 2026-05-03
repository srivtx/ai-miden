import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def vector_add_kernel(a, b, c):
    """Conceptual CUDA kernel: each thread handles one element.
    WHY: SIMT means Single Instruction Multiple Thread; every thread
    runs the same instruction on different data, just like this loop."""
    for i in range(len(a)):
        c[i] = a[i] + b[i]


def coalesced_access(arr, block_size=256):
    """Simulate coalesced memory access: threads in a warp access
    consecutive memory locations.
    WHY: GPUs fetch memory in chunks (cache lines). When 32 threads
    read consecutive floats, one fetch serves all threads."""
    result = np.empty_like(arr)
    n = len(arr)
    for block_start in range(0, n, block_size):
        for i in range(block_start, min(block_start + block_size, n)):
            result[i] = arr[i]
    return result


def strided_access(arr, stride=32):
    """Simulate strided memory access: threads access memory far apart.
    WHY: If thread i reads index i*stride, each read needs a separate
    memory fetch, wasting bandwidth and saturating the memory controller."""
    result = np.empty_like(arr)
    n = len(arr)
    for i in range(n // stride):
        for j in range(stride):
            idx = i * stride + j
            if idx < n:
                result[idx] = arr[idx]
    return result


def benchmark_access(arr, access_fn, repeats=3):
    """Time an access pattern multiple times to reduce noise.
    WHY: Single runs are noisy; averaging gives stable comparison."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        _ = access_fn(arr)
        end = time.perf_counter()
        times.append(end - start)
    return np.mean(times)


def main():
    np.random.seed(42)
    sizes = [100_000, 500_000, 1_000_000, 2_000_000, 5_000_000]
    coalesced_times = []
    strided_times = []

    for size in sizes:
        arr = np.random.randn(size).astype(np.float32)
        t_coal = benchmark_access(arr, coalesced_access)
        t_strd = benchmark_access(arr, strided_access)
        coalesced_times.append(t_coal)
        strided_times.append(t_strd)

    # Plot comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, coalesced_times, marker='o', label='Coalesced (sequential)')
    ax.plot(sizes, strided_times, marker='s', label='Strided (simulated)')
    ax.set_xlabel('Array Size')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Coalesced vs Strided Memory Access (NumPy Simulation)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig('src/phase83/memory_access_patterns.png')
    plt.close(fig)

    # Demonstrate conceptual kernel
    a = np.random.randn(1_000_000).astype(np.float32)
    b = np.random.randn(1_000_000).astype(np.float32)
    c = np.empty_like(a)
    vector_add_kernel(a, b, c)
    np.testing.assert_allclose(c, a + b)
    print("Phase 83: Conceptual vector-add kernel passed.")
    print("Coalesced times:", [f"{t:.4f}s" for t in coalesced_times])
    print("Strided times:", [f"{t:.4f}s" for t in strided_times])
    print("Plot saved to src/phase83/memory_access_patterns.png")


if __name__ == "__main__":
    main()

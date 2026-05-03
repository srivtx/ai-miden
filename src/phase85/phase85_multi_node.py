import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def ring_allreduce(rank_tensors):
    """Conceptual ring-allreduce simulation.
    WHY: Ring-allreduce avoids a central bottleneck. Instead of all
    ranks sending to rank 0, ranks form a ring and pass chunks
    to their neighbor, fully utilizing bidirectional bandwidth."""
    num_ranks = len(rank_tensors)
    n = len(rank_tensors[0])
    chunk_size = n // num_ranks

    # Each rank breaks its tensor into chunks
    rank_chunks = []
    for r in range(num_ranks):
        chunks = [rank_tensors[r][i * chunk_size:(i + 1) * chunk_size].copy() for i in range(num_ranks)]
        rank_chunks.append(chunks)

    # Phase 1: Reduce-scatter
    # After N-1 steps, each rank holds one fully-reduced chunk
    # We simulate the mathematical result of the ring passes
    reduced_chunks = []
    for i in range(num_ranks):
        chunk_sum = np.zeros(chunk_size, dtype=np.float32)
        for r in range(num_ranks):
            chunk_sum += rank_chunks[r][i]
        reduced_chunks.append(chunk_sum)

    # Phase 2: Allgather
    # Every rank receives all reduced chunks
    full = np.concatenate(reduced_chunks)
    return full


def main():
    np.random.seed(0)
    num_ranks = 4
    n = 16
    # Each rank has different gradients (simulating data parallelism)
    rank_tensors = [np.random.randn(n).astype(np.float32) for _ in range(num_ranks)]

    result = ring_allreduce(rank_tensors)
    expected = np.sum(rank_tensors, axis=0)

    print("Rank 0 gradient:", rank_tensors[0])
    print("Allreduce result:", result)
    print("Expected sum:   ", expected)
    assert np.allclose(result, expected)
    print("Ring-allreduce simulation passed.")

    # Show chunking visually
    fig, axes = plt.subplots(1, num_ranks, figsize=(10, 3), sharey=True)
    chunk_size = n // num_ranks
    for i, ax in enumerate(axes):
        chunk = rank_tensors[0][i * chunk_size:(i + 1) * chunk_size]
        ax.bar(range(len(chunk)), chunk, color='steelblue')
        ax.set_title(f'Chunk {i}\n(Rank 0)')
        ax.set_xlabel('Index')
    axes[0].set_ylabel('Gradient Value')
    fig.suptitle('Gradient Tensor Split into Ring-Allreduce Chunks')
    fig.tight_layout()
    fig.savefig('src/phase85/ring_chunks.png')
    plt.close(fig)

    # Ring topology plot
    fig, ax = plt.subplots(figsize=(6, 6))
    for i in range(num_ranks):
        nxt = (i + 1) % num_ranks
        ax.annotate('', xy=(nxt, 0), xytext=(i, 0),
                    arrowprops=dict(arrowstyle='->', lw=2, color='steelblue'))
    ax.scatter(range(num_ranks), [0] * num_ranks, s=300, color='coral', zorder=5)
    for i in range(num_ranks):
        ax.text(i, 0, f'Rank {i}', ha='center', va='center')
    ax.set_xlim(-0.5, num_ranks - 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_title('Ring Communication Topology')
    ax.axis('off')
    fig.tight_layout()
    fig.savefig('src/phase85/ring_topology.png')
    plt.close(fig)
    print("Plots saved to src/phase85/")


if __name__ == "__main__":
    main()

"""
Phase 106: AI for Science (Protein, Molecules)
NumPy demo showing why rotation-invariant features are needed for 3D coordinates.
Implements a simple distance-based "equivariant" feature extractor.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)


def rotation_matrix_3d(axis, theta):
    """Return a 3D rotation matrix for given axis and angle."""
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([
        [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]
    ])


def naive_mlp_feature(points):
    """A naive feature: flatten and sum coordinates. Changes under rotation."""
    return np.sum(points.flatten())


def distance_based_feature(points):
    """
    A simple rotation-invariant feature extractor:
    compute pairwise distances and statistics.
    """
    n = points.shape[0]
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            dists.append(np.linalg.norm(points[i] - points[j]))
    dists = np.array(dists)
    return np.array([dists.mean(), dists.std(), dists.min(), dists.max()])


def main():
    # Create a simple 5-point "molecule" in 3D
    points = np.random.randn(5, 3)

    # Apply a random rotation
    R = rotation_matrix_3d([1, 1, 1], np.pi / 3)
    points_rot = points @ R.T

    naive_before = naive_mlp_feature(points)
    naive_after = naive_mlp_feature(points_rot)

    dist_before = distance_based_feature(points)
    dist_after = distance_based_feature(points_rot)

    print("Naive feature before rotation:", naive_before)
    print("Naive feature after rotation: ", naive_after)
    print("Naive feature changed?", not np.isclose(naive_before, naive_after))
    print()
    print("Distance feature before rotation:", dist_before)
    print("Distance feature after rotation: ", dist_after)
    print("Distance feature changed?", not np.allclose(dist_before, dist_after))
    print()

    # Plot: compare naive vs invariant under multiple rotations
    thetas = np.linspace(0, 2 * np.pi, 50)
    naive_vals = []
    dist_vals = []
    for theta in thetas:
        R = rotation_matrix_3d([0, 1, 0], theta)
        p_rot = points @ R.T
        naive_vals.append(naive_mlp_feature(p_rot))
        dist_vals.append(distance_based_feature(p_rot)[0])  # mean distance

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thetas, naive_vals, label='Naive feature (sum of coords)', color='red')
    ax.plot(thetas, dist_vals, label='Invariant feature (mean distance)', color='blue')
    ax.axhline(distance_based_feature(points)[0], color='blue', linestyle='--', alpha=0.5)
    ax.set_xlabel('Rotation angle (rad)')
    ax.set_ylabel('Feature value')
    ax.set_title('Why Rotation-Invariant Features Matter for 3D Molecules')
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig('src/phase106/rotation_invariant_demo.png')
    print("Saved plot to src/phase106/rotation_invariant_demo.png")


if __name__ == '__main__':
    main()

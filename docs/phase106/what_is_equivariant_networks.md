## What Are Equivariant Networks?

---

## The Problem

If you rotate a protein molecule in 3D space, its chemical properties do not change. A standard neural network, however, processes raw (x, y, z) coordinates through fully connected layers that have no notion of rotation. Feed the same molecule in two different orientations into an MLP, and you get two completely different predictions. The network treats rotation as meaningful variation rather than irrelevant nuisance. How do you build networks whose outputs transform predictably and consistently when the input transforms?

---

## Definition

An **equivariant function** f satisfies f(T(x)) = T(f(x)) for some transformation group T (e.g., rotations). An **invariant function** satisfies f(T(x)) = f(x). **E(n)-equivariant networks** are architectures where each layer respects the Euclidean symmetries (rotations, translations, reflections) of n-dimensional space. If you rotate the input point cloud, the output feature vectors rotate the same way.

**How it works:**
```
Input:          3D point cloud of a molecule
Transformation: rotate all points by matrix R

Standard MLP:   output changes arbitrarily → predictions differ by orientation
Equivariant net: output features rotate by R → predictions are consistent

Key operation:  message passing uses only relative vectors (x_j - x_i)
                and distances ||x_j - x_i||, which transform predictably
```

**Key architectures:**
- **EGNN (E(n) Equivariant Graph Neural Network):** updates node features using relative distances and directional vectors
- **Tensor field networks:** represent features as geometric tensors that transform under rotation
- **Steerable CNNs:** generalize convolutions to act on feature fields with defined transformation rules

**Why this matters:**
- Molecular property prediction requires orientation-independent energy estimates
- Force prediction requires equivariant vector outputs (rotating the molecule rotates the forces)
- Without equivariance, models must see every orientation in training, which is data-inefficient

---

## Real-Life Analogy

Think of a weather vane mounted on a roof. When the wind shifts direction, the vane rotates with it. The vane's orientation is always aligned to the wind, no matter which way the house faces. That is equivariance: the output (vane angle) changes in the same structured way as the input (wind direction). Now imagine a compass that reads "North" no matter which way you hold it. That is invariance: the output does not change at all. Both are useful, but they serve different purposes. You use a weather vane when you need to track direction; you use a compass when you need a fixed reference.

Equivariant networks are like the weather vane. When you rotate a molecule, the network's internal representations rotate the same way. If the network predicts forces on atoms, those force vectors rotate with the molecule. This is not a learned behavior; it is hardcoded into the architecture through the use of relative positions and distances. The network never sees absolute coordinates in isolation. It sees "atom B is 1.5 Angstroms to the left of atom A," and that relational fact is true regardless of how the entire molecule is oriented in space.

The trade-off is between expressiveness and constraint. An equivariant network cannot learn arbitrary functions of absolute coordinates; it is restricted to functions that respect the symmetry. This restriction is the point: it prevents overfitting to irrelevant orientations. But it also means that tasks requiring absolute positional information (e.g., docking into a fixed protein pocket) need careful framing, often by making the pocket itself the coordinate frame.

---

## Tiny Numeric Example

**A 5-point "molecule" in 3D, rotated by 60 degrees around the (1,1,1) axis:**

**Naive MLP feature (sum of all coordinates):**
```
Before rotation:   3.42
After rotation:   -0.87
Changed?          Yes — the feature is not invariant
```

**Distance-based invariant feature (mean of pairwise distances):**
```
Before rotation:   2.156
After rotation:    2.156
Changed?          No — distances are preserved under rotation
```

**Equivariant feature (relative vectors between points):**
```
Before rotation:   v_12 = [1.2, -0.5, 0.3]
After rotation:    v_12 = [0.8, -0.9, 0.7]  ← exactly R * v_12
Behavior:          transforms equivariantly (as required)
```

**Model predictions on energy (should be invariant):**
```
Standard MLP (trained on one orientation):
  Orientation A:  -12.5 kcal/mol
  Orientation B:   -8.3 kcal/mol   ← wrong! same molecule

Invariant network:
  Orientation A:  -12.5 kcal/mol
  Orientation B:  -12.5 kcal/mol   ← correct
```

**The shift:** Using distance-based invariant features eliminated orientation-dependent prediction errors entirely, while equivariant features ensured that vector outputs transformed correctly under rotation.

---

## Common Confusion

1. **"Equivariance and invariance are the same thing."** Invariance means the output does not change at all. Equivariance means the output changes in the same structured way as the input. Both are useful: invariant outputs for scalar predictions (energy), equivariant outputs for vector predictions (forces).

2. **"Equivariant networks are just data augmentation."** Data augmentation trains on many rotated versions. Equivariance encodes the symmetry into the architecture so the model generalizes to unseen orientations without seeing them in training.

3. **"Only molecular data needs equivariance."** Equivariance matters for any geometric data: point clouds (LiDAR), meshes (computer graphics), fluid simulations, and gravitational systems.

4. **"Equivariant networks are slower than standard networks."** Early implementations were slow, but modern frameworks (eNeRF, TorchMD-NET) achieve competitive speeds by exploiting sparse neighbor lists and efficient tensor contractions.

5. **"You can achieve equivariance by centering the coordinates."** Centering removes translation dependence but does not handle rotation. Rotation requires using relative vectors and distances, not just subtracting the centroid.

6. **"E(n)-equivariance handles all transformations."** E(n) covers rotations, translations, and reflections. It does not cover scaling (requires SE(3) or conformal methods) or permutations of atom indices (requires graph neural networks).

7. **"Equivariant networks cannot learn complex functions."** They can approximate any continuous equivariant function to arbitrary precision (universal approximation theorems exist for steerable CNNs and tensor field networks).

---

## Where It Is Used in Our Code

`src/phase106/phase106_ai_for_science.py` — We implement a simple distance-based feature extractor and compare it against a naive coordinate-sum feature under random 3D rotations. We plot how the naive feature oscillates wildly with rotation angle while the distance-based feature remains constant, demonstrating why equivariant/invariant representations are necessary for 3D scientific data.

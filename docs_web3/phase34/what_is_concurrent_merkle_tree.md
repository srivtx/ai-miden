# What Is a Concurrent Merkle Tree

## Why It Exists

Standard Merkle trees become bottlenecks in high-throughput environments because updating a leaf requires exclusive access to recompute the root hash. On Solana, where transactions execute in parallel, a single Merkle root would force sequential processing and destroy performance. A concurrent Merkle tree solves this by maintaining a changelog of recent root hashes and proof paths, allowing multiple transactions to propose updates simultaneously and settle correctly as long as they do not conflict on the same leaf.

## Definition

A concurrent Merkle tree is a Merkle tree augmented with a bounded circular buffer of recent root hashes and an indexed proof cache. It supports parallel leaf updates by accepting proofs that are valid for any root within the recent changelog window rather than requiring the absolute latest root.

## Real-Life Analogy

Picture a shared whiteboard in a busy office where everyone must update their project status. Instead of forcing employees to wait in line for the one pen, the office installs five identical whiteboards each showing the state from five minutes ago. Employees write on whichever board is free, and a coordinator periodically merges the changes. As long as no two employees edit the exact same project cell, all updates settle correctly without a queue.

## Tiny Numeric Example

A concurrent Merkle tree with a changelog size of three:

| Slot | Operation | Root Index | Valid Roots | Result |
|------|-----------|------------|-------------|--------|
| 100 | Mint leaf 5 | 0 | 0 | Success |
| 101 | Mint leaf 6 | 1 | 0, 1 | Success |
| 102 | Mint leaf 7 | 2 | 0, 1, 2 | Success |
| 103 | Mint leaf 8 | 0 (wrap) | 1, 2, 0 | Success |
| 104 | Update leaf 5 | 1 | 2, 0, 1 | Success if proof matches root 1 or 2 |

Transactions in slots 100-104 all proceed in parallel because each uses a proof valid within the three-root window.

## Common Confusion

- A concurrent tree is not lock-free magic; it still requires proof paths, but it relaxes the root recency requirement.
- The changelog size is not unlimited; if a proof refers to a root older than the buffer, the transaction fails.
- Concurrent trees do not allow editing the same leaf simultaneously; conflicting updates still require serialization.
- More changelog slots are not always better; each slot consumes account space and increases rent costs.
- Concurrent trees are not standard Merkle trees with extra metadata; they use indexed node caches to speed up proofs.
- Proof generation is not done on-chain; clients or indexers compute proofs off-chain and submit them for verification.
- The root hash still changes after every update; concurrency is achieved by tolerating slightly stale proofs.

## Key Properties
## Where It Appears in Our Code

Concurrent Merkle tree logic is demonstrated in `src_web3/phase34/compression/src/lib.rs`, where the program accepts proofs against recent changelog roots to authorize parallel compressed NFT mints.

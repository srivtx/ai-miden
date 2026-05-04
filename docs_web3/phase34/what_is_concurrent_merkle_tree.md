# What Is a Concurrent Merkle Tree

**The Problem:**

Standard Merkle trees become bottlenecks in high-throughput environments because updating a leaf requires exclusive access to recompute the root hash. On Solana, where transactions execute in parallel, a single Merkle root would force sequential processing and destroy performance. A concurrent Merkle tree solves this by maintaining a changelog of recent root hashes, allowing multiple transactions to propose updates simultaneously using proofs valid within the recent window.

**Definition:**

A concurrent Merkle tree is a Merkle tree augmented with a bounded circular buffer of recent root hashes and an indexed proof cache. It supports parallel leaf updates by accepting proofs that are valid for any root within the recent changelog window rather than requiring the absolute latest root.

**How It Works (Step-by-Step):**

1. **Proof generation:** A client reads the current Merkle root and computes a proof path for the leaf it intends to update.
2. **Transaction submission:** The client submits the update transaction with the leaf index, new value, and proof path.
3. **Changelog validation:** The on-chain program verifies that the recomputed root from the proof matches any root currently stored in the circular changelog buffer.
4. **Conflict detection:** If another transaction has already updated the same leaf or a conflicting path node, the proof will not match a valid changelog root and the transaction fails.
5. **Root update:** On success, the program updates the leaf, recomputes the new root, and overwrites the oldest entry in the changelog buffer with the new root.
6. **Parallel settlement:** Transactions updating non-conflicting leaves in different branches proceed in parallel because they touch disjoint sets of nodes.

**Real-life analogy:**

A university registrar maintains a master ledger of all student grades. Instead of forcing every advisor to wait in line to use today's exact ledger, the registrar publishes the last five versions of the ledger. Advisors can submit grade-change forms using any of those five versions. As long as two advisors do not try to change the same course grade, both updates settle correctly. If they do conflict, the second advisor must fetch a newer version and resubmit.

**Tiny numeric example:**

Consider a Merkle tree of depth 2 with four leaves. Define hash(a, b) = a + b for illustration.

Initial leaves: L0 = 1, L1 = 2, L2 = 3, L3 = 4.
Level 1 nodes: N0 = hash(1, 2) = 3, N1 = hash(3, 4) = 7.
Root R0 = hash(3, 7) = 10.

Step 1: Update L1 from 2 to 5.
N0' = hash(1, 5) = 6. Root R1 = hash(6, 7) = 13.
Changelog (size 3): [10, 13, -]

Step 2: Update L2 from 3 to 6.
N1' = hash(6, 4) = 10. Root R2 = hash(6, 10) = 16.
Changelog: [10, 13, 16]

Step 3: Client with stale proof updates L3 from 4 to 8.
Client computed proof for L3 valid at R1: sibling leaf L2 = 3, sibling node N0' = 6.
Verification: hash(3, 4) = 7, hash(6, 7) = 13. Root 13 is in the changelog. Valid.
Program updates L3 to 8: N1'' = hash(6, 8) = 14. Root R3 = hash(6, 14) = 20.
Changelog (wraps, overwriting oldest): [13, 16, 20]

Step 4: Conflict detection for L1.
Client A proof for L1 valid at R2: sibling L0 = 1, sibling N1' = 10. hash(1, 5) = 6, hash(6, 10) = 16. Valid.
Client B also targets L1 with proof valid at R3: sibling L0 = 1, sibling N1'' = 14. hash(1, 5) = 6, hash(6, 14) = 20. Valid.
If Client A succeeds first, L1 becomes 9 and root becomes R4. Client B's transaction targets the same leaf index. The on-chain tree detects that the leaf has been modified more recently than Client B's proof root and rejects the second update.

**Common confusion:**

- A concurrent tree is not lock-free magic. It still requires proof paths; it only relaxes the root recency requirement. No.
- The changelog size is not unlimited. If a proof refers to a root older than the buffer, the transaction fails. No.
- Concurrent trees do not allow editing the same leaf simultaneously. Conflicting updates still require serialization. No.
- More changelog slots are not always better. Each slot consumes account space and increases rent costs. No.
- Proof generation is not done on-chain. Clients or indexers compute proofs off-chain and submit them for verification. No.
- The root hash still changes after every update. Concurrency is achieved by tolerating slightly stale proofs, not by freezing the root. No.

**Key properties:**

- The changelog buffer size determines how stale a proof can be while remaining valid.
- Parallel updates are safe only when leaves reside in disjoint proof-path branches.
- The on-chain program stores and updates node values directly; no off-chain state is trusted.
- Proof verification cost is logarithmic in the number of leaves, same as standard Merkle trees.

**Where it appears in our code:**

Concurrent Merkle tree logic is demonstrated in `src_web3/phase34/compression/src/lib.rs`, where the program accepts proofs against recent changelog roots to authorize parallel compressed NFT mints.

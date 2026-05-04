# What Is a Compressed NFT

**The Problem:**

Traditional NFTs on Solana require one token account and one metadata account per mint, costing significant rent in SOL as collections grow to millions of items. Compressed NFTs store ownership and metadata inside Merkle tree leaves, reducing the on-chain footprint to a single tree account regardless of collection size. This makes mass minting economically viable for gaming assets, event tickets, and digital identity credentials.

**Definition:**

A compressed NFT is a non-fungible token whose ownership, metadata, and provenance are represented as a leaf in a Merkle tree rather than as individual token accounts. Transfers and updates are authorized by Merkle proofs submitted to an on-chain program that verifies inclusion against the tree root.

**How It Works (Step-by-Step):**

1. **Tree initialization:** A collection creator initializes a concurrent Merkle tree on-chain, specifying depth, max buffer size, and canopy depth.
2. **Mint:** The creator hashes the NFT metadata and owner public key into a leaf value. The on-chain program verifies the proof path, appends the leaf to the next empty index, and updates the tree root.
3. **Proof indexing:** An off-chain indexer observes the on-chain root update and reconstructs the full tree structure. It stores leaf values and generates Merkle proofs for each leaf.
4. **Transfer preparation:** The current owner initiates a transfer. The indexer provides a proof path showing the leaf is included in the current tree root.
5. **On-chain verification:** The owner submits the transfer transaction with the new owner, the leaf index, and the Merkle proof. The on-chain program verifies the proof against a root in the changelog.
6. **Leaf replacement:** On success, the program replaces the old leaf with a new leaf containing the new owner's public key, recomputes the root, and appends it to the changelog.

**Real-life analogy:**

Imagine a concert with one hundred thousand attendees. Instead of printing one hundred thousand physical tickets and renting a warehouse to store them, the venue issues a master ledger with one entry per attendee. Each attendee carries a QR code that proves their row exists in the ledger. Security scans the QR code, verifies it against the master hash, and admits the guest. The venue never touches paper tickets; it only maintains one digital commitment.

**Tiny numeric example:**

Consider a compressed NFT collection using a depth-2 Merkle tree. Define hash(a, b) = a + b.

Tree initialized with four empty leaves: 0, 0, 0, 0.
Root = hash(hash(0, 0), hash(0, 0)) = 0.

Mint NFT #0 for owner Alice:
Leaf 0 = hash("Alice", "metadata_uri_0") = 42,371.
Proof path (all siblings are 0): hash(0, 42,371) = 42,371, hash(0, 42,371) = 42,371.
Root becomes 42,371.

Mint NFT #1 for owner Bob:
Leaf 1 = hash("Bob", "metadata_uri_1") = 58,294.
Proof path: sibling leaf = 42,371, sibling node = 0.
Verification: hash(42,371, 58,294) = 100,665, hash(0, 100,665) = 100,665. Root = 100,665.
Root becomes 100,665.

Transfer NFT #0 from Alice to Carol:
Leaf 0' = hash("Carol", "metadata_uri_0") = 44,902.
Indexer provides proof for old leaf 0 valid at root 100,665:
Siblings: leaf 1 = 58,294, node N1 = hash(0, 0) = 0.
Verification of old leaf: hash(42,371, 58,294) = 100,665, hash(0, 100,665) = 100,665. Matches root. Valid.
Program replaces leaf 0 with 44,902.
New N0 = hash(44,902, 58,294) = 103,196.
New root = hash(0, 103,196) = 103,196.

Cost comparison for a one million item collection on Solana:

| Approach | On-Chain Accounts | Approximate Rent | Mint Cost per Item |
|----------|------------------|------------------|--------------------|
| Traditional NFT | 2,000,000 | ~2,400 SOL | ~0.0024 SOL |
| Compressed NFT | 1 Merkle tree | ~0.03 SOL | ~0.00000003 SOL |

The compressed approach reduces rent by over 99% by replacing millions of accounts with one tree root.

**Common confusion:**

- Compressed NFTs are not stored entirely off-chain. The Merkle root is on-chain, and proofs are verified on-chain. No.
- Ownership is not tracked in a token account. It is implied by the ability to produce a valid proof for a specific leaf. No.
- Decompressing is not automatic. Converting a compressed NFT back to a traditional format requires a specific on-chain instruction. No.
- Metadata is not retrieved from the chain directly. Indexers reconstruct it from off-chain data using the leaf hash. No.
- Compressed NFTs are not less secure. They inherit the same cryptographic guarantees as standard Merkle proofs. No.
- Burning a compressed NFT is a logical deletion. The leaf is updated to a null value rather than removing an account. No.

**Key properties:**

- The entire collection state collapses to a single on-chain account containing the tree root and changelog.
- Ownership transfer is authorized by a Merkle proof, not by a token account signature.
- Off-chain indexers are required to reconstruct metadata and generate proofs.
- The compression program enforces collection-level authority for mints and tree configuration.

**Where it appears in our code:**

Compressed NFT mint and transfer logic are implemented in `src_web3/phase34/compression/src/lib.rs`, with API support in `src_web3/phase34/compression_api.ts` for generating proofs and submitting tree updates.

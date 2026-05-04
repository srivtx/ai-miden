# What Is ZK Compression?

## Why it exists (THE PROBLEM)

Solana stores every token account, NFT metadata account, and program state account as a separate on-chain ledger entry.

At scale, millions of user token accounts each consume 128 bytes or more of rent-exempt lamports.

This makes airdrops, loyalty programs, and gaming economies prohibitively expensive because the protocol or users must pay state rent for every single account.

ZK compression solves this by storing many account states inside a single Merkle tree, replacing individual accounts with one shared root that costs the same regardless of how many leaves it contains.

## Definition

ZK compression is a scaling technique that batches many individual account states into a Merkle tree, keeps the tree root on-chain, and uses zero-knowledge proofs to verify reads and writes against that root without loading every leaf onto the ledger.

## How It Works

1. **Create Merkle tree.** A smart program initializes an on-chain Merkle tree account that will serve as the shared container for many compressed states.
2. **Add leaves.** Instead of creating individual token accounts, the protocol appends new account states as leaves to the tree off-chain or through a compressed instruction.
3. **Generate proof.** When a user wants to spend or read a compressed state, a prover generates a zero-knowledge proof that the leaf exists in the current tree without revealing the entire leaf set.
4. **Verify on-chain.** The Solana program receives the proof, verifies it against the stored Merkle root, and confirms the state transition is valid.
5. **Update root.** After a valid spend, the program removes the old leaf and appends new leaves, then updates the on-chain root to reflect the new tree state.
6. **Read compressed state.** Clients and indexers read the full tree off-chain and use the root to trustlessly verify that any leaf is current.

## Real-life analogy

Imagine a stadium that stores every ticket holder's name on a single master board instead of printing individual paper tickets.

When a fan enters, the gate attendant does not read every name on the board.

The fan presents a cryptographic proof that their name is on the board, the attendant verifies the proof against the master board's current hash, and lets them in.

The stadium only needs to maintain one board, no matter whether ten thousand or ten million fans attend.

ZK compression works the same way: one on-chain root replaces millions of separate accounts.

## Tiny numeric example

Consider a protocol that wants to create one million token accounts.

| Approach | Storage Per Account | Total Rent (approx) | Cost at 100 SOL |
|----------|---------------------|---------------------|-----------------|
| Standard SPL token account | 0.0029 SOL | 2,900 SOL | $290,000 |
| ZK compressed token leaf | 0.000017 SOL | 17 SOL | $1,700 |

A single standard token account costs roughly 0.0029 SOL in rent.

A compressed leaf inside a shared Merkle tree costs roughly 0.000017 SOL because only the tree root lives on-chain.

For one million users, the difference is thousands of SOL versus tens of SOL.

This cost reduction makes consumer-scale apps economically viable on Solana.

## Common confusion

- "ZK compression stores data off-chain, so it is no longer on Solana."
  No. The Merkle root remains on-chain and is updated by Solana programs; the data is simply compressed into a single root that is verifiably linked to Solana consensus.

- "ZK compression is only for tokens."
  No. Any account state can be compressed, including NFT metadata, user profiles, voting records, and game inventory.

- "ZK proofs make transactions slower."
  No. Proof generation happens off-chain or in a dedicated prover service; on-chain verification is a fast constant-time check that adds minimal latency.

- "Users lose custody because the state is off-chain."
  No. Users retain full custody. Only the hash of their state lives in the tree; their private key still authorizes spends, and the ZK proof ensures no one can forge a spend.

- "Reading compressed state requires a trusted indexer."
  No. While indexers make reading convenient, anyone can reconstruct the Merkle tree from on-chain instructions and verify inclusion trustlessly against the root.

- "ZK compression replaces Solana's base layer."
  No. It is a scaling layer built on top of Solana that uses the base layer for settlement, security, and proof verification.

## Key properties

1. **State rent minimization.** A single Merkle tree root costs the same rent regardless of leaf count, making million-user economies affordable.
2. **ZK-verified validity.** Every state transition is backed by a zero-knowledge proof, so validators do not need to read all leaves to confirm correctness.
3. **SPL compatibility.** Compressed tokens are still SPL tokens; they can be decompressed back into standard accounts when needed.
4. **Off-chain indexing.** Full tree reconstruction happens off-chain via indexers, but trust is minimized because the on-chain root is the source of truth.
5. **Composable with existing programs.** Decompression instructions allow compressed state to interact with standard Solana DeFi protocols that expect normal token accounts.

## Where it appears in our code

- `src_web3/phase64/compression_demo.ts`
  Demonstrates creating a compressed token mint, minting compressed tokens, transferring them with ZK proofs, and reading compressed balances via the Light Protocol SDK.

- `src_web3/phase64/compression_api.ts`
  Express API that exposes endpoints for minting compressed tokens, transferring them with ZK proofs, and querying compressed balances by address.

- `docs_web3/phase64/ARCHITECTURE.md`
  Step-by-step guide that walks through installing the Light Protocol SDK, creating a compressed mint, minting, transferring, verifying on-chain, and decompressing.

# What Is a Compressed Token?

## Why it exists (THE PROBLEM)

Standard SPL tokens require one on-chain account per user per mint.

A loyalty program with one million users needs one million token accounts, each paying 0.0029 SOL rent.

This makes large-scale token distributions, micro-transactions, and gaming rewards economically impossible.

Compressed tokens store balances as leaves in a Merkle tree so millions of users share one on-chain root, slashing rent by over 100x.

## Definition

A compressed token is a token balance that is stored as a leaf inside a Merkle tree managed by the Light Protocol program on Solana instead of residing in a standard SPL token account.

It behaves like a normal SPL token for minting and transferring, but its state is batched and verified with zero-knowledge proofs.

## How It Works

1. **Create Merkle tree.** The Light Protocol program initializes a tree that will contain all compressed token leaves for a given mint.
2. **Add leaves.** When tokens are minted, the SDK appends a leaf containing the owner public key and balance to the tree.
3. **Generate proof.** To transfer, the sender's wallet fetches a ZK proof from the Light RPC that proves ownership of a leaf with sufficient balance.
4. **Verify on-chain.** The Light verifier program checks the proof against the on-chain Merkle root, confirming the sender owns the tokens.
5. **Update root.** The program removes the spent leaf and appends new leaves for the recipient and any change owed to the sender.
6. **Read compressed state.** Wallets and apps query the Light RPC indexer to read balances, which reconstructs the tree from on-chain updates.

## Real-life analogy

Imagine a casino that replaces individual chip trays for every player with one communal ledger.

Instead of each player holding physical chips, the casino writes every player's balance in a single notebook.

When a player wants to pay another, the cashier verifies the payer's signature against the notebook and updates both balances in one atomic entry.

The notebook is the Merkle tree, the signature check is the ZK proof, and the atomic update is the on-chain root update.

Compressed tokens work the same way: one shared structure holds millions of balances securely.

## Tiny numeric example

Consider a protocol that wants to create one million token accounts.

| Approach | Storage Per Account | Total Rent (approx) | Cost at 100 SOL |
|----------|---------------------|---------------------|-----------------|
| Standard SPL token account | 0.0029 SOL | 2,900 SOL | $290,000 |
| Compressed token leaf | 0.000017 SOL | 17 SOL | $1,700 |

A single standard token account costs roughly 0.0029 SOL in rent.

A compressed token leaf costs roughly 0.000017 SOL because it lives inside a shared Merkle tree with a single on-chain root.

For one million users, the difference is thousands of SOL versus tens of SOL.

This cost reduction makes consumer-scale token economies viable on Solana.

## Common confusion

- "Compressed tokens are not real SPL tokens."
  No. They are compatible with the SPL token standard and can be decompressed into normal token accounts at any time.

- "Compressed token balances are invisible on-chain."
  No. Every mint, transfer, and root update is recorded in Solana transactions; the balances are simply compressed into a tree rather than stored in separate accounts.

- "You need a special wallet to hold compressed tokens."
  No. Any Solana wallet that can sign standard transactions can hold and transfer compressed tokens because the ownership model uses the same Ed25519 keypairs.

- "Compressed tokens cannot be used in DeFi."
  No. They can be decompressed into standard SPL accounts before being deposited into AMMs, lending protocols, or staking programs that expect normal accounts.

- "Minting compressed tokens is slower than standard SPL."
  No. Minting appends a leaf to the tree in a single transaction; the throughput is comparable and the rent cost is far lower.

- "Compressed tokens sacrifice security for cost."
  No. Security is maintained by the same Solana consensus and validator set; the ZK proof adds a cryptographic guarantee that no invalid spend can occur.

## Key properties

1. **Rent efficiency.** Millions of compressed token balances share one Merkle tree root, reducing per-user rent from 0.0029 SOL to roughly 0.000017 SOL.
2. **SPL compatibility.** Compressed tokens can be decompressed into standard SPL token accounts to interact with existing wallets and DeFi protocols.
3. **ZK-proven transfers.** Every transfer is backed by a zero-knowledge proof of Merkle inclusion, preventing double-spends without loading all balances on-chain.
4. **Atomic updates.** A single transaction can consume old leaves and create new ones, ensuring balance conservation is enforced by the on-chain verifier.
5. **Indexer-readable.** Balances are reconstructed off-chain by the Light Protocol indexer, enabling fast wallet UI lookups while keeping the on-chain footprint tiny.

## Where it appears in our code

- `src_web3/phase64/compression_demo.ts`
  Demonstrates creating a compressed token mint, minting compressed tokens to a recipient, and transferring them with ZK proofs.

- `src_web3/phase64/compression_api.ts`
  Express API with endpoints to mint compressed tokens, transfer them, and query compressed balances by owner address.

- `docs_web3/phase64/ARCHITECTURE.md`
  Step-by-step architecture guide covering compressed token mint creation, minting, transfer, verification, and decompression.

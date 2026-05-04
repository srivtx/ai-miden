# What Is a Compressed NFT

## Why It Exists

Traditional NFTs on Solana require one token account and one metadata account per mint, costing significant rent in SOL as collections grow to millions of items. Compressed NFTs store ownership and metadata inside Merkle tree leaves, reducing the on-chain footprint to a single tree account regardless of collection size. This makes mass minting economically viable for gaming assets, event tickets, and digital identity credentials.

## Definition

A compressed NFT is a non-fungible token whose ownership, metadata, and provenance are represented as a leaf in a Merkle tree rather than as individual token accounts. Transfers and updates are authorized by Merkle proofs submitted to an on-chain program that verifies inclusion against the tree root.

## Real-Life Analogy

Imagine a concert with one hundred thousand attendees. Instead of printing one hundred thousand physical tickets and renting a warehouse to store them, the venue issues a master ledger with one entry per attendee. Each attendee carries a QR code that proves their row exists in the ledger. Security scans the QR code, verifies it against the master hash, and admits the guest. The venue never touches paper tickets; it only maintains one digital commitment.

## Tiny Numeric Example

Cost comparison for a one million item collection on Solana:

| Approach | On-Chain Accounts | Approximate Rent | Mint Cost per Item |
|----------|------------------|------------------|--------------------|
| Traditional NFT | 2,000,000 | ~2,400 SOL | ~0.0024 SOL |
| Compressed NFT | 1 Merkle tree | ~0.03 SOL | ~0.00000003 SOL |

The compressed approach reduces rent by over 99% by replacing millions of accounts with one tree root.

## Common Confusion

- Compressed NFTs are not stored entirely off-chain; the Merkle root is on-chain, and proofs are verified on-chain.
- Ownership is not tracked in a token account; it is implied by the ability to produce a valid proof for a specific leaf.
- Decompressing is not automatic; converting a compressed NFT back to a traditional format requires a specific on-chain instruction.
- Metadata is not retrieved from the chain directly; indexers reconstruct it from off-chain data using the leaf hash.
- Compressed NFTs are not less secure; they inherit the same cryptographic guarantees as standard Merkle proofs.
- Not all wallets support compressed NFTs; clients need integration with the compression program to display and transfer them.
- Burning a compressed NFT is a logical deletion; the leaf is updated to a null value rather than removing an account.

## Key Properties
## Where It Appears in Our Code

Compressed NFT mint and transfer logic are implemented in `src_web3/phase34/compression/src/lib.rs`, with API support in `src_web3/phase34/compression_api.ts` for generating proofs and submitting tree updates.

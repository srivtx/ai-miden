# What Is Light Protocol?

## Why it exists (THE PROBLEM)

Existing ZK compression solutions require developers to write custom circuits, manage prover infrastructure, and maintain Merkle tree state manually.

This overhead is too high for application teams that want the cost benefits of ZK compression without becoming cryptography experts.

Light Protocol exists to provide a complete SDK, RPC, and prover service so developers can treat compressed state like normal SPL tokens.

## Definition

Light Protocol is a Solana infrastructure project that provides SDKs, an RPC service, and on-chain programs for creating, transferring, and reading ZK-compressed tokens and state.

It abstracts Merkle tree management, proof generation, and compressed account indexing behind familiar TypeScript and Rust APIs.

## How It Works

1. **Create Merkle tree.** The Light Protocol program initializes a Merkle tree account on Solana that will hold compressed state leaves.
2. **Add leaves.** Developers use the Light SDK to append compressed token accounts or generic state as leaves to the tree via standard instructions.
3. **Generate proof.** The Light RPC runs a prover that builds zero-knowledge proofs of Merkle inclusion for any leaf the user wants to spend.
4. **Verify on-chain.** Light Protocol's on-chain verifier program checks the proof against the stored root in a single fast instruction.
5. **Update root.** After verification, the program updates the Merkle root on-chain to reflect consumed and newly created leaves.
6. **Read compressed state.** The Light RPC indexer maintains an off-chain copy of the full tree and serves compressed balances and proofs to clients on demand.

## Real-life analogy

Imagine a postal service that decides to replace millions of individual PO boxes with one giant secure vault.

Instead of each customer renting an expensive box, the vault holds a single master list of all mail.

When a customer wants to retrieve mail, the postal clerk uses a secure scanner that proves the customer owns a specific slot without opening every other slot.

Light Protocol is the postal service, the vault, and the scanner combined.

Developers do not need to build the vault or the scanner; they simply hand mail to the service and let it handle the security.

## Tiny numeric example

Consider a protocol that wants to create one million token accounts.

| Approach | Storage Per Account | Total Rent (approx) | Cost at 100 SOL |
|----------|---------------------|---------------------|-----------------|
| Standard SPL token account | 0.0029 SOL | 2,900 SOL | $290,000 |
| ZK compressed token leaf via Light Protocol | 0.000017 SOL | 17 SOL | $1,700 |

A single standard token account costs roughly 0.0029 SOL in rent.

A compressed leaf managed by Light Protocol costs roughly 0.000017 SOL because the SDK batches leaves into one Merkle tree root.

For one million users, the difference is thousands of SOL versus tens of SOL.

This cost reduction makes consumer-scale apps economically viable on Solana.

## Common confusion

- "Light Protocol is a separate blockchain."
  No. Light Protocol is a suite of Solana programs and SDKs; all state settles on Solana and inherits Solana's security.

- "Light Protocol requires a new wallet."
  No. Any Solana wallet works because compressed tokens use the same keypairs and signatures as standard SPL tokens.

- "Light Protocol replaces the Solana validator set."
  No. Validators still execute and verify transactions; Light Protocol adds prover and indexer services off-chain that feed proofs to validators.

- "Developers must write ZK circuits to use Light Protocol."
  No. The SDK provides pre-built circuits for compressed tokens; developers call high-level functions like `mintTo` and `transfer` without touching circuit code.

- "Light Protocol is only for tokens."
  No. While the current SDK emphasizes compressed tokens, the underlying Merkle tree and proof system can compress any program state.

- "Using Light Protocol means trusting their RPC."
  No. The RPC provides convenience and proofs, but the on-chain root is the ultimate source of truth and anyone can verify proofs independently.

## Key properties

1. **Complete SDK abstraction.** `@lightprotocol/compressed-token` and `@lightprotocol/stateless.js` hide Merkle tree math behind familiar token APIs.
2. **Managed prover service.** The Light RPC generates validity proofs on demand so application servers do not need prover hardware.
3. **On-chain verification.** All proofs are verified by Solana programs, so compressed state transitions are as secure as standard transactions.
4. **Indexer-backed reads.** The RPC indexer reconstructs compressed balances off-chain and serves them via HTTP, enabling fast balance lookups.
5. **Composable decompression.** Light Protocol provides instructions to decompress tokens back into standard SPL accounts for compatibility with existing DeFi protocols.

## Where it appears in our code

- `src_web3/phase64/compression_demo.ts`
  Uses `@lightprotocol/compressed-token` and `@lightprotocol/stateless.js` to create a compressed mint, mint tokens, and transfer with ZK proofs.

- `src_web3/phase64/compression_api.ts`
  Express API that wraps the Light Protocol SDK in REST endpoints for minting, transferring, and balance queries.

- `docs_web3/phase64/ARCHITECTURE.md`
  Step-by-step guide for installing the Light Protocol SDK and using it to build compressed token applications.

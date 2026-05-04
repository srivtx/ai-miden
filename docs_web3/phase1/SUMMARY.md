# Phase 1 Summary: Blockchain Fundamentals

## Key Takeaways

- A blockchain is a cryptographically linked, append-only ledger maintained by many peers.
- Hash functions provide tamper-evident fingerprints; changing one bit produces a completely different hash.
- Immutability is enforced by hash chaining and economic consensus, making history retroactively unchangeable.
- Validation is local and deterministic: any node can verify the entire chain from genesis to tip.

## What Was Built

| File | Purpose |
|------|---------|
| `docs_web3/phase1/what_is_blockchain.md` | Core ledger concept with distributed maintenance analogy |
| `docs_web3/phase1/what_is_hash_function.md` | One-way fingerprinting with avalanche effect examples |
| `docs_web3/phase1/what_is_immutability.md` | Economic and cryptographic guarantees of unchangeable history |
| `src_web3/phase1/toy_blockchain.rs` | Working Rust blockchain with SHA-256 linkage and tamper detection |
| `src_web3/phase1/toy_blockchain.ts` | TypeScript equivalent using Node.js crypto for hash chaining |

## Connections to Other Phases

- Phase 0 explained why decentralization matters; this phase shows the data structure that makes it work.
- Phase 2 will add digital signatures so blocks can prove who authorized each transaction.
- Phase 3 replaces slow proof-of-work with Solana's Proof of History and Tower BFT.
- Phase 4 maps the chain's state into Solana's account model.

## Next Step

Proceed to Phase 2 to learn how private keys, public keys, and digital signatures secure ownership on the blockchain.

# Phase 2 Summary: Cryptography

## Key Takeaways

- A keypair gives users self-sovereign identity: the private key authorizes, the public key identifies.
- Digital signatures prove authenticity, integrity, and non-repudiation without revealing the secret key.
- Ed25519 is Solana's choice because it is fast, deterministic, compact, and resistant to implementation bugs.
- All key operations happen offline; the blockchain only sees public keys and signatures, never secrets.

## What Was Built

| File | Purpose |
|------|---------|
| `docs_web3/phase2/what_is_keypair.md` | Self-sovereign identity through public/private key pairs |
| `docs_web3/phase2/what_is_digital_signature.md` | Message binding, verification, and tamper detection |
| `docs_web3/phase2/what_is_ed25519.md` | Why Solana uses Ed25519 and how it outperforms older schemes |
| `src_web3/phase2/keypair_demo.rs` | Rust demo generating, signing, and verifying Ed25519 signatures |
| `src_web3/phase2/keypair_demo.ts` | TypeScript demo with TweetNaCl showing tamper and attacker rejection |

## Connections to Other Phases

- Phase 1's blockchain stores transactions; this phase provides the cryptographic tool to authorize them.
- Phase 3 uses these signatures in Solana's Proof of History and Tower BFT consensus.
- Phase 4 maps public keys to accounts that hold lamports and program state.
- Phase 5 sets up the tools to compile and deploy code that uses these keypairs.

## Next Step

Proceed to Phase 3 to discover how Solana's unique architecture achieves high speed without sacrificing security.

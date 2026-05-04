# What is Ed25519 Verification?

## The Problem
Faked signatures are exploits. If a bridge accepts a mint request without proving that authorized guardians actually approved it, an attacker can forge a signature, create infinite wrapped tokens, and drain the vault. Phase 56 used stubbed checks that always returned true. Phase 56v2 replaces those stubs with real Ed25519 signature verification on-chain.

## Definition
Ed25519 verification is the cryptographic process of checking that a digital signature was created by the holder of a specific private key, using the Twisted Edwards curve. On Solana, this is performed inside the smart contract using the `ed25519-dalek` library or the native Ed25519 program, ensuring that no off-chain actor can forge approval.

## How It Works
1. Message hashing: The bridge operation (amount, recipient, nonce) is hashed into a fixed 32-byte digest.
2. Sign with private key: Each guardian uses their offline Ed25519 private key to sign the digest.
3. Verify with public key: The on-chain program receives the signature and the guardian's public key and mathematically confirms the pairing.
4. Threshold check: The program counts how many distinct valid signatures are provided.
5. Execute: Only if the count meets or exceeds the configured threshold does the program mint or release tokens.
6. Record: The operation nonce is incremented to prevent the same proof from being replayed.

## Real-life Analogy
Imagine a bank vault that requires three senior managers to turn their keys simultaneously. The lock mechanism does not trust a photograph of a key; it physically tests the teeth. Ed25519 verification is the physical test. A threshold of three means two keys are insufficient no matter how authentic they look.

## Tiny Numeric Example with Actual Signature Bytes
Message hash (SHA-256): `a3f5...9b21` (32 bytes)
Guardian public key: `11aa...22bb` (32 bytes)
Guardian secret key: `secret...` (64 bytes, includes pubkey)
Signature produced (64 bytes):
`3a7f...e4d2` (first 32 bytes R)
`9c81...b105` (last 32 bytes s)
On-chain, the program loads these exact 64 bytes into `ed25519_dalek::Signature` and calls `verify`. If a single bit in the signature is flipped, the verification equation `8SB = 8R + 8H(R,A,m)A` fails and the instruction aborts.

## Common Confusion
- No, checking the length of a signature is not verifying it. A 64-byte string can still be random noise.
- No, verifying a Solana transaction signature is not the same as verifying a custom Ed25519 message. Transaction signatures prove fee payer consent, not bridge approval.
- No, skipping the message hash is not acceptable. The guardian must sign the exact digest the program verifies.
- No, one guardian signing three times does not count as three guardians. The program checks distinct public keys.
- No, you cannot reuse a signature from a previous mint. The nonce in the message makes each proof unique.
- No, leaving `assert!(true)` as a verification stub is safe only in local unit tests; in any deployed environment it is a critical exploit.

## Key Properties
1. Deterministic: The same message and key always produce the exact same valid signature.
2. Non-malleable: An attacker cannot tweak a valid signature to create a second valid signature for the same message.
3. Compact: Public keys are 32 bytes and signatures are 64 bytes, minimizing transaction size.
4. Fast: Ed25519 verification is optimized for batch and single-check performance on constrained environments like BPF.
5. Standardized: Widely audited and implemented across cryptography libraries, reducing custom implementation risk.

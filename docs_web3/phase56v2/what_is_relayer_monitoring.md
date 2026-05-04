# What is Relayer Monitoring?

## The Problem
Smart contracts cannot spontaneously act. A bridge program sitting on Solana does not know when a user locked tokens on Ethereum, and it cannot poll the internet. Someone must watch for off-chain events, package proofs, and submit transactions. Phase 56 had no relayer; students manually called mint. Phase 56v2 adds a standalone relayer that automates event detection and proof submission.

## Definition
Relayer monitoring is the off-chain process of polling or streaming blockchain events, constructing cryptographically signed proofs from guardians, and submitting those proofs as on-chain transactions. The relayer is an operational service, not a trusted authority, because the on-chain program verifies every proof independently.

## How It Works
1. Subscribe: The relayer opens an RPC connection and optionally subscribes to program logs or account changes.
2. Poll: At regular intervals, the relayer fetches the latest bridge nonce and compares it against its local cursor.
3. Detect: When a new `LockEvent` appears in transaction logs, the relayer reads the lock record to obtain user, amount, and nonce.
4. Sign: The relayer requests or locally produces Ed25519 signatures from guardian keys over the operation hash.
5. Submit: The relayer builds a `verify_and_mint_wrapped` transaction and sends it to the Solana cluster.
6. Confirm: The relayer waits for confirmation, advances its cursor, and emits a success metric or alert.

## Real-life Analogy
Imagine an international shipping company that has a team watching the departure port through binoculars. When a container is loaded, they radio the arrival port with the cargo manifest and captain's signature. The arrival port does not trust the radio operator; it only trusts the captain's cryptographic seal. The radio operator is the relayer, and if they fall asleep, another operator can take over without compromising security.

## Tiny Numeric Example with Actual Polling Intervals
The relayer starts with `lastProcessedNonce = -1`.
Poll 1 (T+0s): Bridge nonce is 0. No new locks.
Poll 2 (T+5s): Bridge nonce is 1. Lock record nonce=0 detected.
Relayer builds message = user_pubkey + amount(8 bytes LE) + nonce(8 bytes LE).
Relayer computes SHA-256(message) = `a3f5...9b21`.
Guardian key 1 signs hash -> 64 bytes.
Guardian key 2 signs hash -> 64 bytes.
Relayer submits mint transaction with both signatures and indices [0, 1].
Poll 3 (T+10s): Transaction confirmed. `lastProcessedNonce` advances to 0.

## Common Confusion
- No, the relayer is a trusted third party. The relayer only delivers messages; it cannot forge guardian signatures or bypass the threshold.
- No, one relayer is enough. A healthy bridge has multiple independent relayers running in different data centers to prevent single points of failure.
- No, the relayer must hold guardian private keys. In production, guardians run their own signer services and the relayer collects signatures via HTTP. This demo holds keys locally for simplicity.
- No, polling is the only option. Relayers can also use WebSocket subscriptions, webhooks, or block-streaming APIs for lower latency.
- No, a missed poll means the lock is lost. Locks remain on-chain forever; a relayer that restarts can catch up by scanning historical nonces.
- No, the relayer decides how many signatures are enough. The on-chain program enforces the threshold; a relayer submitting insufficient signatures pays a failed transaction fee and learns nothing.

## Key Properties
1. Stateless: The relayer can restart, crash, or migrate without losing bridge state because state lives entirely on-chain.
2. Replaceable: Any operator can run a relayer; there is no whitelist or permission required to submit proofs.
3. Observable: Relayer behavior is visible through RPC request patterns and on-chain transaction history.
4. Idempotent: Submitting the same proof twice is blocked by nonce and `is_released` flags, so duplicate submissions are harmless.
5. Resilient: The bridge does not depend on a specific relayer being online; users can also manually submit proofs if they collect guardian signatures themselves.

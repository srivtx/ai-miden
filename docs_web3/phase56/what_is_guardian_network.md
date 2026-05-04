# What Is a Guardian Network?

## The Problem

When tokens move from Chain A to Chain B, Chain B cannot natively see what happened on Chain A. Blockchains are isolated ledgers. Without a trusted observer, a malicious actor could claim "I locked 100 tokens on Chain A" when they did not, and mint fake tokens on Chain B. A single centralized oracle creates a single point of failure. We need a decentralized set of validators who independently witness events and agree before any tokens are minted.

## Definition

A Guardian Network is a decentralized set of validators (guardians) who independently monitor source chain events, cryptographically sign attestations that an event occurred, and collectively reach a threshold agreement before the target chain acts on that event. Each guardian stakes collateral that can be slashed if they sign false attestations.

## How It Works

1. **Event Emission**: A user locks tokens on the source chain. The bridge smart contract emits a `LockEvent` containing the amount, recipient address, and a unique nonce.
2. **Independent Observation**: Each guardian node runs a full validator for the source chain and sees the `LockEvent` in a finalized block.
3. **Individual Attestation**: Each guardian produces an ECDSA or Ed25519 signature over a structured message hash containing the event details.
4. **Signature Aggregation**: Off-chain relayers collect individual guardian signatures and bundle them into a multi-signature proof once the threshold is met.
5. **On-Chain Verification**: The target chain bridge contract verifies the aggregated proof by checking each signature against registered guardian public keys and ensuring the count meets or exceeds the threshold.
6. **Mint Authorization**: Only after successful verification does the target chain contract mint wrapped tokens to the user's specified address.

## Real-Life Analogy

Imagine you want to ship a valuable painting from New York to London. Instead of trusting one customs officer to verify the painting left New York, five independent inspectors each take a photo, sign a certificate, and seal it. The London gallery will only release the insured replica to the buyer when at least three of those signed certificates are presented. No single inspector can fake the shipment alone.

## Tiny Numeric Example with Signatures and Thresholds

Assume a guardian network of 5 nodes with a threshold of 3.

- Guardian public keys: G1, G2, G3, G4, G5
- User locks 50 USDC on Ethereum (source).
- The bridge contract emits: `LockEvent(user=0xABC, amount=50, nonce=42)`
- Each guardian computes the message hash: `keccak256("LOCK:0xABC:50:42")`
- G1 signs: `sig1 = Sign(G1_priv, hash)` -> valid
- G2 signs: `sig2 = Sign(G2_priv, hash)` -> valid
- G3 signs: `sig3 = Sign(G3_priv, hash)` -> valid
- G4 rejects (does not see the event)
- G5 signs a conflicting hash (malicious)

The relayer submits `sig1, sig2, sig3` to Solana (target).
The Solana guardian contract:
1. Recovers signer from sig1 -> G1 (valid, staked)
2. Recovers signer from sig2 -> G2 (valid, staked)
3. Recovers signer from sig3 -> G3 (valid, staked)
Count = 3, which meets threshold. Mint 50 wUSDC to the mapped Solana address.
G5's conflicting signature, if submitted alone, would not reach threshold and would result in a slash.

## Common Confusion

- **No.** A guardian network is not the same as a blockchain validator set. Guardians do not produce blocks; they attest to external events.
- **No.** A single guardian cannot authorize a mint. The threshold requirement prevents any individual from acting alone.
- **No.** Guardians do not hold user funds. They only hold stake as collateral and produce signatures.
- **No.** The guardian network does not replace the relayer. Guardians sign; relayers pay gas to submit those signatures on-chain.
- **No.** Signature verification happens on the target chain, not off-chain. The smart contract must validate every signature to trust the proof.
- **No.** Thresholds are fixed at deployment and cannot be changed by a single guardian. Rotation and parameter changes require their own multi-sig governance.

## Key Properties

1. **Byzantine Fault Tolerance**: As long as fewer than one-third of guardians are malicious or offline, the network reaches correct consensus.
2. **Cryptographic Accountability**: Every attestation is a signed message. Misbehavior is permanently recorded and attributable to a specific public key.
3. **Stake-Weighted Security**: The economic cost to attack the network equals the sum of staked collateral required to control the threshold.
4. **Asynchronous Operation**: Guardians observe and sign independently without a leader; no consensus protocol is required among them.
5. **Chain Agnostic**: The same guardian set can attest to events on Ethereum, Solana, or any chain that supports the signature scheme.

## Where It Appears

- Wormhole's Guardian Network (19 guardians, threshold 13)
- Axelar's validator set
- LayerZero's DVN (Decentralized Verifier Network)
- Chainlink's Cross-Chain Interoperability Protocol (CCIP) Risk Management Network
- Custom enterprise bridges requiring multi-party attestation

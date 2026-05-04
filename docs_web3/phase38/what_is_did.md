# What Is a DID

## The Problem

On the internet, identity is fragmented. Every website asks you to create a new account, stores your password in its own database, and controls your data. If the site shuts down or gets hacked, your digital identity suffers. A Decentralized Identifier (DID) gives individuals ownership of their identity by storing credentials on a blockchain or distributed ledger instead of a corporate server. You control the keys, you decide what to share, and no single company can revoke your identity.

## Definition

A DID is a globally unique identifier that does not require a centralized registration authority. It is created and controlled by the subject, cryptographically secured by a private key, and resolvable to a DID document that contains public keys, service endpoints, and verification methods.

## How It Works (Step-by-Step)

1. The user generates a cryptographic key pair, for example an Ed25519 key pair, producing a private key and a public key.
2. The user constructs a DID document that includes the public key, a list of verification methods, and optional service endpoints such as a personal website or messaging address.
3. The user derives the DID string from the public key according to a specific DID method, for example `did:ethr:0x71C7656EC7ab88b098defB751B7401B5f6d8976F`.
4. The user registers the DID document on a blockchain or distributed ledger by submitting a transaction that anchors the document and records the owner address.
5. A verifier who wants to authenticate the user resolves the DID by querying the ledger, retrieving the latest DID document, and extracting the public key.
6. The user proves ownership by signing a challenge with their private key; the verifier checks the signature against the public key in the resolved document without contacting any centralized authority.

## Real-life analogy

Imagine a passport that you print yourself. It contains a photo, your name, and a hologram that only you can produce because you invented the hologram technique. Every border agent knows how to verify the hologram, but no government issued the passport and no government can confiscate it. A DID is that self-issued passport for the digital world.

## Tiny numeric example

A user creates a DID on an Ethereum-compatible blockchain.

| Property | Value | Meaning |
|----------|-------|---------|
| DID string | did:ethr:0x71C7656EC7ab88b098defB751B7401B5f6d8976F | Unique identifier anchored on Ethereum |
| Controller | 0x71C7656EC7ab88b098defB751B7401B5f6d8976F | The Ethereum address that controls the DID |
| Public key | 0x04a1b2c3d4e5f6... | Used to verify signatures from the owner |
| Service endpoint | https://profile.example.com/jane | Where additional data can be fetched |
| Registration tx | 0xdef4567890abc... | Transaction hash that wrote the DID to the chain |
| Block number | 18,942,000 | Block in which the DID was registered |
| Created | 1715000000 | Unix timestamp of creation (2024-05-06) |

When Jane logs into a dApp, she presents a proof signed by her private key. The dApp resolves her DID, finds the public key at index 0 in the document, and verifies the signature against the challenge nonce `0x9a3e...` without needing a password database. The verification completes in 12 milliseconds.

## Common confusion

- No, a DID is not a blockchain account; it is an identifier that may be anchored on a blockchain but represents identity, not funds.
- No, DIDs are not anonymous by default; they are pseudonymous. Linking a DID to a real-world person requires additional verified credentials.
- No, resolving a DID does not reveal private keys; the DID document only contains public information.
- No, a DID is not tied to one device; the private key can be backed up or stored in a hardware wallet, and multiple keys can be listed in the DID document.
- No, DID methods (ethr, sol, web, etc.) are not interchangeable; each method defines how the DID is created, resolved, and updated on its target system.
- No, losing the private key does not automatically mean losing the DID; some methods support social recovery or multi-signature update mechanisms.

## Key properties

- Decentralized control: no central authority issues, manages, or revokes the identifier.
- Cryptographically verifiable: ownership is proved by signing with the associated private key.
- Resolvable: a DID maps to a DID document that contains public keys, service endpoints, and verification methods.
- Persistent: the identifier remains valid as long as the underlying ledger or storage exists.
- Interoperable: DIDs are standardized by the W3C and can be used across platforms and services.

## Where it appears in our code

The DID API in `src_web3/phase38/did_api.ts` simulates DID creation, resolution, and authentication, allowing users to register a DID, update its document, and verify ownership through challenge-response signatures.

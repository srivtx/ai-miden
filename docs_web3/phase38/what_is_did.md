# What Is a DID

## Why It Exists

On the internet, identity is fragmented. Every website asks you to create a new account, stores your password in its own database, and controls your data. If the site shuts down or gets hacked, your digital identity suffers. A Decentralized Identifier (DID) gives individuals ownership of their identity by storing credentials on a blockchain or distributed ledger instead of a corporate server. You control the keys, you decide what to share, and no single company can revoke your identity.

## Definition

A DID is a globally unique identifier that does not require a centralized registration authority. It is created and controlled by the subject, cryptographically secured by a private key, and resolvable to a DID document that contains public keys, service endpoints, and verification methods.

## Real-Life Analogy

Imagine a passport that you print yourself. It contains a photo, your name, and a hologram that only you can produce because you invented the hologram technique. Every border agent knows how to verify the hologram, but no government issued the passport and no government can confiscate it. A DID is that self-issued passport for the digital world.

## Tiny Numeric Example

A user creates a DID on a blockchain.

| Property | Value | Meaning |
|----------|-------|---------|
| DID string | did:ethr:0xabc123... | Unique identifier anchored on Ethereum |
| Controller | 0xabc123... | The Ethereum address that controls the DID |
| Public key | 0xpub456... | Used to verify signatures from the owner |
| Service endpoint | https://profile.example.com/jane | Where additional data can be fetched |
| Created | 1690000000 | Unix timestamp of creation |

When Jane logs into a dApp, she presents a proof signed by her private key. The dApp resolves her DID, finds the public key, and verifies the signature without needing a password database.

## Common Confusion

- A DID is not a blockchain account; it is an identifier that may be anchored on a blockchain but represents identity, not funds.
- DIDs are not anonymous by default; they are pseudonymous. Linking a DID to a real-world person requires additional verified credentials.
- Resolving a DID does not reveal private keys; the DID document only contains public information.
- A DID is not tied to one device; the private key can be backed up or stored in a hardware wallet, and multiple keys can be listed in the DID document.
- DID methods (ethr, sol, web, etc.) are not interchangeable; each method defines how the DID is created, resolved, and updated on its target system.
- Losing the private key does not automatically mean losing the DID; some methods support social recovery or multi-signature update mechanisms.
- A DID does not replace a government ID for legal purposes; it is a technical layer that can carry government-verified credentials.

## Key Properties

## Where It Appears in Our Code

The DID API in `src_web3/phase38/did_api.ts` simulates DID creation, resolution, and authentication, allowing users to register a DID, update its document, and verify ownership through challenge-response signatures.

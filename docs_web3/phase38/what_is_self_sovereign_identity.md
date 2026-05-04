# What Is Self-Sovereign Identity

## The Problem

For decades, identity has been something that companies give to you. Google assigns your email, Facebook assigns your profile, and governments assign your ID number. These centralized authorities can suspend accounts, sell behavioral data, or suffer breaches that expose millions of users. Self-Sovereign Identity (SSI) shifts control to the individual. You create your own identifiers, store your own credentials, and choose what to share with whom. No intermediary can revoke your existence or monetize your history without consent.

## Definition

Self-Sovereign Identity is a model of digital identity where the individual is the ultimate owner and controller of their identity data. It combines decentralized identifiers, verifiable credentials, and peer-to-peer communication to enable trust without centralized identity providers.

## How It Works (Step-by-Step)

1. The user generates a decentralized identifier and stores the private key in a secure wallet or hardware security module.
2. The user requests a verifiable credential from a trusted issuer, such as a government, university, or employer.
3. The issuer verifies the user's real-world identity through an out-of-band process and issues a cryptographically signed credential tied to the user's DID.
4. The user stores the credential in a personal vault that they control, not on a central server controlled by the issuer or a platform.
5. When a service asks for proof, the user selects the relevant credential and constructs a presentation, signing it with their private key to prove consent.
6. The service verifies the issuer's signature and the credential's revocation status independently, without contacting a centralized identity provider, and grants access based solely on the presented claims.

## Real-life analogy

Imagine carrying a physical wallet. Inside are your driver's license, gym membership card, and a handwritten letter of recommendation from a former boss. When you enter a bar, you show the bouncer your license. When you join a gym, you show the membership card. When you apply for a job, you show the letter. No single authority knows all three contexts. You decide what to show, when to show it, and to whom. Self-Sovereign Identity is that wallet, but digital and cryptographically secure.

## Tiny numeric example

A user named Alex builds an SSI profile.

| Property | Value | Meaning |
|----------|-------|---------|
| DID | did:ethr:0xalex789abcdef... | Self-created identifier |
| Created | 2024-01-15 09:00 UTC (timestamp 1705309200) | When the DID was registered |
| Credentials held | 3 | Proof of address, employment certificate, driver's license |
| Presentations made in 2024 | 7 | Number of times Alex shared a credential |
| Average verification time | 14 ms | How long a verifier takes to check a presentation |
| Revocation checks failed | 0 | All presented credentials were still valid |

When Alex opens a bank account, he presents only the proof of address. The bank verifies the municipal office's signature, checks that the credential was issued on block 18,200,000, and confirms the revocation status list shows bit 0 at index 847. The bank never sees Alex's employment certificate or social score. Alex retains full control.

## Common confusion

- No, SSI does not mean fake identities are allowed; issuers still verify real-world facts before signing credentials.
- No, self-sovereign does not mean isolated; users interact with services and share credentials selectively, they do not live in a digital vacuum.
- No, SSI is not just blockchain; while DIDs often use ledgers, credentials are stored off-chain and peer-to-peer protocols handle communication.
- No, losing your private key in SSI is not recoverable by customer support; it is catastrophic unless recovery mechanisms like social recovery are configured in advance.
- No, SSI does not eliminate trust; it shifts trust from centralized platforms to cryptographic proofs and trusted issuers.
- No, privacy is not absolute; verifiers see the claims you choose to present, and issuers may record that they issued a credential even if they do not know when it is presented.

## Key properties

- User-centric control: the individual owns their identifiers and credentials without intermediary gatekeepers.
- Portability: identity data can move across services and platforms without vendor lock-in or account migration.
- Minimal disclosure: users share only the specific claims required for a transaction, not their entire identity profile.
- Consent-driven: every presentation requires the user's explicit approval through cryptographic signing.
- Interoperable: built on open standards like W3C DIDs and Verifiable Credentials, enabling cross-platform use.

## Where it appears in our code

The SSI model is demonstrated in `src_web3/phase38/did_api.ts` through endpoints that let a user create a DID, receive credentials from issuers, store them in a personal vault, and present proofs to verifiers without revealing unnecessary data.

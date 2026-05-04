# What Is Self-Sovereign Identity

## Why It Exists

For decades, identity has been something that companies give to you. Google assigns your email, Facebook assigns your profile, and governments assign your ID number. These centralized authorities can suspend accounts, sell behavioral data, or suffer breaches that expose millions of users. Self-Sovereign Identity (SSI) shifts control to the individual. You create your own identifiers, store your own credentials, and choose what to share with whom. No intermediary can revoke your existence or monetize your history without consent.

## Definition

Self-Sovereign Identity is a model of digital identity where the individual is the ultimate owner and controller of their identity data. It combines decentralized identifiers, verifiable credentials, and peer-to-peer communication to enable trust without centralized identity providers.

## Real-Life Analogy

Imagine carrying a physical wallet. Inside are your driver's license, gym membership card, and a handwritten letter of recommendation from a former boss. When you enter a bar, you show the bouncer your license. When you join a gym, you show the membership card. When you apply for a job, you show the letter. No single authority knows all three contexts. You decide what to show, when to show it, and to whom. Self-Sovereign Identity is that wallet, but digital and cryptographically secure.

## Tiny Numeric Example

A user builds their SSI profile across three contexts.

| Context | Credential | Issuer | Stored By |
|---------|------------|--------|-----------|
| Banking | Proof of address | Municipal office | User's encrypted vault |
| Employment | Professional certificate | Industry board | User's encrypted vault |
| Social | Reputation score | Peer network | User's encrypted vault |

When opening a bank account, the user presents only the proof of address. The bank verifies the municipal office's signature and never sees the employment certificate or social score. The user retains full control.

## Common Confusion

- SSI does not mean fake identities are allowed; issuers still verify real-world facts before signing credentials.
- Self-sovereign does not mean isolated; users interact with services and share credentials selectively, they do not live in a digital vacuum.
- SSI is not just blockchain; while DIDs often use ledgers, credentials are stored off-chain and peer-to-peer protocols handle communication.
- Losing your private key in SSI is catastrophic unless recovery mechanisms are configured; there is no customer support to reset your password.
- SSI does not eliminate trust; it shifts trust from centralized platforms to cryptographic proofs and trusted issuers.
- Privacy is not absolute; verifiers see the claims you choose to present, and issuers may record that they issued a credential even if they do not know when it is presented.
- SSI is not yet universal; adoption depends on governments, businesses, and standards bodies accepting decentralized credentials.

## Key Properties

## Where It Appears in Our Code

The SSI model is demonstrated in `src_web3/phase38/did_api.ts` through endpoints that let a user create a DID, receive credentials from issuers, store them in a personal vault, and present proofs to verifiers without revealing unnecessary data.

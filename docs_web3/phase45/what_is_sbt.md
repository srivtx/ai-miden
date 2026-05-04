# What Is a Soulbound Token

## Why It Exists

Most tokens on blockchains are designed to be transferable. A dollar stablecoin, a governance token, or an NFT can be sent from one wallet to another without restriction. This property is essential for currency and tradable assets, but it becomes a liability when representing identity, credentials, or reputation. If a university issues a diploma as a transferable token, graduates can sell their academic credentials to strangers. If a protocol issues a participation badge as a transferable token, farmers can buy their way into governance without contributing. A soulbound token exists to solve this problem by creating digital records that are permanently tied to a specific wallet or identity. They cannot be sold, transferred, or stolen, making them suitable for representing things that are inherently personal.

## Definition

A soulbound token is a non-transferable digital token issued to a specific blockchain address and permanently bound to that address. It represents credentials, achievements, affiliations, reputation scores, or identity attributes that belong to the holder and cannot be separated from them. The concept extends the utility of tokens from tradeable value to irreplaceable personal history, enabling on-chain resumes, trust networks, and access control based on earned rather than purchased attributes.

## Real-Life Analogy

Imagine a tattoo that appears on your skin when you complete medical school. It displays your degree, your graduation year, and the name of your institution. You cannot give this tattoo to someone else. You cannot sell it. If someone steals your wallet, they do not get the tattoo because it is part of your body. Employers can look at the tattoo and immediately verify your credentials without calling the university registrar. The tattoo is permanent, non-transferable, and uniquely yours. A soulbound token is the digital equivalent of this tattoo. It is a credential that lives on your blockchain identity and cannot be moved.

## Tiny Numeric Example

A decentralized autonomous organization issues soulbound tokens for participation:

| Wallet Address | SBT Type | Issuer | Non-Transferable |
|----------------|----------|--------|------------------|
| 0xAlice | Governance Veteran | DAO Treasury | Yes |
| 0xAlice | Bug Bounty Hunter | Security Council | Yes |
| 0xBob | Early Contributor | DAO Treasury | Yes |
| 0xBob | Governance Veteran | DAO Treasury | Yes |

When a proposal requires voters to have at least two governance-related SBTs, the smart contract checks 0xAlice's wallet and finds one governance token. It checks 0xBob's wallet and finds two. 0xBob is eligible to vote on the sensitive proposal, while 0xAlice is not. Neither can buy the missing token on a marketplace because the tokens are soulbound. The eligibility is based on actual historical participation rather than wealth.

## Common Confusion

- A soulbound token is not a regular NFT.
  Standard NFTs are transferable and tradable, while soulbound tokens are permanently bound to one address.
- Soulbound tokens are not stored in a separate blockchain.
  They use the same token standards but enforce non-transferability at the smart contract level.
- Non-transferability does not mean the token is useless.
  It means the token's value is in its social and functional utility, not its market price.
- Soulbound tokens are not completely irrevocable.
  Issuers can burn or revoke them in cases of fraud or error, though this requires governance or issuer authority.
- A wallet full of SBTs is not an investment portfolio.
  It is a resume or reputation record that signals trustworthiness and history.
- Soulbound tokens do not solve all identity problems.
  They represent claims made by issuers, and those claims can still be false if the issuer is dishonest.
- You cannot recover a soulbound token if you lose your private key.
  Because it is non-transferable, there is no mechanism to move it to a new wallet.
- Soulbound tokens are not automatically private.
  All data on public blockchains is visible, so sensitive credentials should be hashed or encrypted.

## Key Properties

- Non-transferable by design, enforced in token contract logic
- Permanently bound to the receiving address at issuance
- Issuer-attested claims about the holder's history or attributes
- Composable reputation where multiple SBTs combine to grant access or rights
- Revocable by the issuer under predefined conditions

## Where It Appears in Our Code

Soulbound token logic is implemented in `src_web3/phase45/sbt_api.ts`.
The API exposes endpoints to issue soulbound tokens, query a wallet's credential record, and verify that a holder possesses specific tokens for access control.
It enforces non-transferability by rejecting any transfer request and tracks issuer authority for revocation.

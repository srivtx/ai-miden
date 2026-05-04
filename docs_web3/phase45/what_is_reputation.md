# What Is On-Chain Reputation

## Why It Exists

In traditional systems, reputation is fragmented and opaque. Your credit score is held by a bureau. Your professional history is on a resume that you write yourself. Your participation in a community is remembered only by the people who were there at the time. These systems are vulnerable to fraud, forgetting, and gatekeeping by centralized intermediaries. On-chain reputation exists to create a persistent, verifiable, and composable record of a wallet's history, credentials, and relationships. It transforms reputation from a subjective memory into an objective, queryable data layer that smart contracts can use to grant access, allocate rewards, and establish trust without knowing the user's real-world identity.

## Definition

On-chain reputation is the aggregate of tokens, transaction history, protocol interactions, and attestations associated with a blockchain address that signal trustworthiness, expertise, or participation. It is often represented by soulbound tokens, governance scores, or algorithmic ratings derived from on-chain behavior. Unlike off-chain reputation, it is transparent, immutable, and programmable, allowing decentralized applications to automate eligibility checks, reward distribution, and risk assessment based on historical evidence rather than self-reported claims.

## Real-Life Analogy

Imagine a small village where every good deed is carved into a public stone wall. If you help a neighbor rebuild a barn, the date and your name are carved. If you serve on the village council for two years, that is carved too. If you break a promise, that is also recorded. When a stranger arrives wanting to borrow a horse, the villagers do not ask for a bank statement. They read the wall. If the stranger has no carvings, they are unknown. If they have ten years of trustworthy carvings, they receive the horse without collateral. The wall is the blockchain. The carvings are the transaction history and soulbound tokens. The lending decision is the smart contract eligibility check.

## Tiny Numeric Example

A lending protocol uses on-chain reputation to determine collateral requirements:

| Reputation Metric | Source | 0xAlice Value | 0xBob Value |
|-------------------|--------|---------------|-------------|
| Governance Proposals Voted | DAO SBT | 12 | 2 |
| Loans Repaid On Time | Protocol History | 8 | 1 |
| Bug Bounties Completed | Security SBT | 3 | 0 |
| Reputation Score (Algorithmic) | Composite | 92 | 31 |

For a $10,000 loan, the protocol's smart contract queries these metrics. 0xAlice, with a high reputation score, is required to deposit only $5,000 in collateral. 0xBob, with a low score, must deposit $9,000. If 0xAlice defaults, her governance and security SBTs can be revoked by the protocol, publicly marking her as untrustworthy. This creates a strong disincentive to default because the loss extends beyond money into permanent reputational damage. 0xBob cannot buy 0xAlice's SBTs to improve his collateral terms because they are soulbound and non-transferable.

## Common Confusion

- On-chain reputation is not a universal credit score.
  Different protocols weight different behaviors according to their own risk models.
- A high reputation does not guarantee honesty.
  It only indicates a history of behavior that the protocol considers desirable.
- Reputation tokens are not financial investments.
  Their value is functional and social, not speculative or tradable.
- On-chain reputation is not anonymous privacy.
  It is pseudonymous; real-world identity is not required, but all behavior is publicly visible.
- Reputation cannot be erased by creating a new wallet.
  Because it is bound to a specific address, starting fresh means starting with zero reputation.
- Reputation algorithms are not objective truth.
  They encode the values and biases of the protocol designers.
- On-chain reputation does not replace legal enforcement.
  It complements it by adding a social and economic layer of accountability.
- Reputation is not static.
  It can decay over time if a wallet becomes inactive, or it can be damaged by negative actions.

## Key Properties

- Composability across protocols that read the same reputation tokens
- Transparency because all reputation data is publicly auditable on-chain
- Persistence because historical records remain visible indefinitely
- Automation because smart contracts can query and act on reputation without human intervention
- Non-transferability for credential-based reputation to prevent market manipulation

## Where It Appears in Our Code

On-chain reputation logic is implemented in `src_web3/phase45/sbt_api.ts`.
The API exposes endpoints to issue reputation-bearing soulbound tokens, query a wallet's composite reputation record, and simulate access control decisions based on token possession.
It demonstrates how non-transferable credentials create a trust layer that smart contracts can evaluate programmatically.

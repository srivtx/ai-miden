# What Is On-Chain Reputation

## The Problem:

In traditional systems, reputation is fragmented and opaque. Your credit score is held by a bureau. Your professional history is on a resume that you write yourself. Your participation in a community is remembered only by the people who were there at the time. These systems are vulnerable to fraud, forgetting, and gatekeeping by centralized intermediaries. On-chain reputation exists to create a persistent, verifiable, and composable record of a wallet's history, credentials, and relationships. It transforms reputation from a subjective memory into an objective, queryable data layer that smart contracts can use to grant access, allocate rewards, and establish trust without knowing the user's real-world identity.

## Definition:

On-chain reputation is the aggregate of tokens, transaction history, protocol interactions, and attestations associated with a blockchain address that signal trustworthiness, expertise, or participation. It is often represented by soulbound tokens, governance scores, or algorithmic ratings derived from on-chain behavior. Unlike off-chain reputation, it is transparent, immutable, and programmable, allowing decentralized applications to automate eligibility checks, reward distribution, and risk assessment based on historical evidence rather than self-reported claims.

## How It Works (Step-by-Step):

1. A protocol defines reputation dimensions that matter for its use case, such as payment history, trade completion, dispute resolution, and account longevity. Each dimension is assigned a weight, and the weights must sum to 100%.

2. Raw on-chain data is collected for each wallet. This includes transaction receipts, smart contract event logs, soulbound token balances, governance vote counts, and the timestamp of the wallet's first transaction.

3. Each raw metric is normalized to a 0-100 scale. For example, if the maximum observed on-time payments in the protocol is 20, a wallet with 19 on-time payments scores (19/20) * 100 = 95 on that dimension.

4. The composite reputation score is computed as a weighted sum: Score = sum(Dimension_i_Normalized * Weight_i). The result is a single number between 0 and 100.

5. The smart contract stores or queries the composite score when evaluating access control decisions. For example, a lending protocol may require a score above 70 for reduced collateral, or above 90 for zero-collateral loans.

6. Reputation scores are updated periodically as new on-chain behavior is recorded. Negative actions, such as late payments or disputed trades, can reduce dimension scores. Decay functions may reduce the weight of old behavior so that recent actions matter more than ancient history.

## Real-life analogy:

Imagine a small village where every good deed is carved into a public stone wall. If you help a neighbor rebuild a barn, the date and your name are carved. If you serve on the village council for two years, that is carved too. If you break a promise, that is also recorded. When a stranger arrives wanting to borrow a horse, the villagers do not ask for a bank statement. They read the wall. If the stranger has no carvings, they are unknown. If they have ten years of trustworthy carvings, they receive the horse without collateral. The wall is the blockchain. The carvings are the transaction history and soulbound tokens. The lending decision is the smart contract eligibility check.

## Tiny numeric example:

A lending protocol uses the following reputation scoring algorithm with four dimensions:

| Dimension | Weight | Normalization Basis | 0xAlice Raw | 0xAlice Normalized | 0xBob Raw | 0xBob Normalized |
|-----------|--------|---------------------|-------------|--------------------|-----------|------------------|
| On-Time Payments | 40% | Max = 20 payments | 19 | 95.0 | 10 | 50.0 |
| Successful Trades | 30% | Max = 30 trades | 28 | 93.33 | 6 | 20.0 |
| Dispute Resolutions | 20% | Max = 10 resolutions | 10 | 100.0 | 2 | 20.0 |
| Account Age (years) | 10% | Max = 5 years | 3 | 60.0 | 0.5 | 10.0 |

The composite score formula is:
Score = (Normalized_OnTime * 0.40) + (Normalized_Trades * 0.30) + (Normalized_Disputes * 0.20) + (Normalized_Age * 0.10)

**0xAlice calculation:**
Score = (95.0 * 0.40) + (93.33 * 0.30) + (100.0 * 0.20) + (60.0 * 0.10)
Score = 38.00 + 27.999 + 20.00 + 6.00
Score = 91.999, which rounds to **92**

**0xBob calculation:**
Score = (50.0 * 0.40) + (20.0 * 0.30) + (20.0 * 0.20) + (10.0 * 0.10)
Score = 20.00 + 6.00 + 4.00 + 1.00
Score = **31**

For a $10,000 loan, the protocol's smart contract queries these metrics. 0xAlice, with a composite score of 92, is required to deposit only $5,000 in collateral (50% ratio). 0xBob, with a composite score of 31, must deposit $9,000 (90% ratio). If 0xAlice defaults, her on-chain reputation record is updated to reflect the default, and future dimension scores are penalized. 0xBob cannot buy 0xAlice's soulbound tokens to improve his collateral terms because they are non-transferable.

## Common confusion:

- On-chain reputation is not a universal credit score. No. Different protocols weight different behaviors according to their own risk models.
- A high reputation does not guarantee honesty. No. It only indicates a history of behavior that the protocol considers desirable.
- Reputation tokens are not financial investments. No. Their value is functional and social, not speculative or tradable.
- On-chain reputation is not anonymous privacy. No. It is pseudonymous; real-world identity is not required, but all behavior is publicly visible.
- Reputation cannot be erased by creating a new wallet. No. Because it is bound to a specific address, starting fresh means starting with zero reputation.
- Reputation algorithms are not objective truth. No. They encode the values and biases of the protocol designers.

## Key properties:

- Composability across protocols that read the same reputation tokens
- Transparency because all reputation data is publicly auditable on-chain
- Persistence because historical records remain visible indefinitely
- Automation because smart contracts can query and act on reputation without human intervention
- Non-transferability for credential-based reputation to prevent market manipulation

## Where it appears in our code:

On-chain reputation logic is implemented in `src_web3/phase45/sbt_api.ts`.
The API exposes endpoints to issue reputation-bearing soulbound tokens, query a wallet's composite reputation record, and simulate access control decisions based on token possession.
It demonstrates how non-transferable credentials create a trust layer that smart contracts can evaluate programmatically.

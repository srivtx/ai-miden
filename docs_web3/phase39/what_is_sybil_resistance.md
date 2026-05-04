# What Is Sybil Resistance

## Why It Exists

Democratic systems depend on the principle of one person, one vote. On the internet, creating new accounts is free and instant, which means one person can pretend to be thousands. This is called a Sybil attack, and it destroys any voting, airdrop, or reputation system that assumes each participant is unique. Sybil resistance is the property of a system that makes it costly or impossible for a single actor to control multiple identities.

## Definition

Sybil resistance is a mechanism or set of mechanisms that prevents a single real-world entity from creating and operating multiple identities to gain disproportionate influence in a distributed system. It is achieved through proof of personhood, economic bonds, social graphs, or biometric verification.

## Real-Life Analogy

Imagine a local election where every voter must show a government-issued ID at the polling station. A single person cannot vote ten times because they only have one ID. If the election instead allowed anonymous online voting with no verification, a single activist could submit thousands of ballots. The ID check is Sybil resistance: it ties digital participation to a scarce real-world credential.

## Tiny Numeric Example

A DAO airdrops voice credits to unique users.

| Scenario | Identities Claimed | Real Humans | Credits per Identity | Total Credits Controlled by Attacker |
|----------|-------------------:|------------:|---------------------:|-------------------------------------:|
| No Sybil resistance | 1,000 | 1 | 25 | 25,000 |
| Weak resistance (phone) | 10 | 1 | 25 | 250 |
| Strong resistance (ID) | 1 | 1 | 25 | 25 |

Without Sybil resistance, one person controls the election. With phone verification they are limited to ten identities. With government ID verification they are limited to one.

## Common Confusion

- Sybil resistance is not the same as privacy; strong identity verification often reduces anonymity.
- It is not perfect; sophisticated attackers can still buy identities, forge documents, or collude with real humans.
- Proof of work is not Sybil resistance for voting; mining power is not tied to unique humans, only to hardware.
- CAPTCHAs are weak Sybil resistance; they stop bots but not humans running multiple accounts.
- Economic bonds (staking) are Sybil resistant in financial contexts because capital is scarce, but they exclude the poor.
- Social graph analysis assumes real humans cluster together; it can fail for isolated individuals or tightly coordinated groups.
- Sybil resistance is not needed for all applications; uncensored messaging benefits from anonymity, while governance requires uniqueness.

## Key Properties

## Where It Appears in Our Code

Sybil resistance is simulated in `src_web3/phase39/quadratic_voting_api.ts` through a voter registration endpoint that assigns a single budget per address and rejects duplicate registrations, illustrating the importance of identity verification before credit distribution.

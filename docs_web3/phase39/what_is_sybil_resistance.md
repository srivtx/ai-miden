# What Is Sybil Resistance

**The Problem:**

Democratic systems depend on the principle of one person, one vote. On the internet, creating new accounts is free and instant, which means one person can pretend to be thousands. This is called a Sybil attack, and it destroys any voting, airdrop, or reputation system that assumes each participant is unique. Sybil resistance is the property of a system that makes it costly or impossible for a single actor to control multiple identities.

**Definition:**

Sybil resistance is a mechanism or set of mechanisms that prevents a single real-world entity from creating and operating multiple identities to gain disproportionate influence in a distributed system. It is achieved through proof of personhood, economic bonds, social graphs, or biometric verification.

**How It Works (Step-by-Step):**

1. **Define identity requirement.** The system establishes a rule that each real-world human may only participate once, whether for voting, airdrops, or reputation.
2. **Verify identity.** During registration, the system requires proof of personhood. This may involve government ID, phone number, biometric scan, social graph analysis, or an economic stake.
3. **Bind identity to account.** The system creates a cryptographic link between the verified identity and a single account or wallet address. This binding is stored in a registry.
4. **Check for duplicates.** Before granting access or credits, the system queries the registry to ensure the same identity has not already been used to create another account.
5. **Reject or flag sybils.** If a duplicate is detected, the system rejects the new registration, slashes the economic stake, or flags the account for review.
6. **Monitor and adapt.** The system continuously analyzes behavior patterns for coordination or automation and updates verification requirements to stay ahead of attackers.

**Real-life analogy:**

Imagine a local election where every voter must show a government-issued ID at the polling station. A single person cannot vote ten times because they only have one ID. If the election instead allowed anonymous online voting with no verification, a single activist could submit thousands of ballots. The ID check is Sybil resistance: it ties digital participation to a scarce real-world credential.

**Tiny numeric example:**

A DAO airdrops voice credits to unique users.

| Scenario | Identities Claimed | Real Humans | Credits per Identity | Total Credits Controlled by Attacker |
|----------|-------------------:|------------:|---------------------:|-------------------------------------:|
| No Sybil resistance | 1,000 | 1 | 25 | 25,000 |
| Weak resistance (phone) | 10 | 1 | 25 | 250 |
| Strong resistance (ID) | 1 | 1 | 25 | 25 |

Without Sybil resistance, one person controls the election. With phone verification they are limited to ten identities. With government ID verification they are limited to one.

**Common confusion:**

- No, Sybil resistance is not the same as privacy; strong identity verification often reduces anonymity.
- No, it is not perfect; sophisticated attackers can still buy identities, forge documents, or collude with real humans.
- No, proof of work is not Sybil resistance for voting; mining power is not tied to unique humans, only to hardware.
- No, CAPTCHAs are not strong Sybil resistance; they stop bots but not humans running multiple accounts.
- No, economic bonds are not universally fair; staking is Sybil resistant because capital is scarce, but it excludes the poor.
- No, Sybil resistance is not needed for every application; uncensored messaging benefits from anonymity, while governance requires uniqueness.

**Key properties:**

- Requires a scarce, hard-to-fake signal tied to a real-world entity.
- Effectiveness scales with the cost and difficulty of obtaining multiple identities.
- Often introduces a trade-off between decentralization, privacy, and inclusivity.
- Must be continuously updated as attackers develop new methods to spoof identities.
- Single points of failure in identity verification can compromise the entire system.

**Where it appears in our code:**

Sybil resistance is simulated in `src_web3/phase39/quadratic_voting_api.ts` through a voter registration endpoint that assigns a single budget per address and rejects duplicate registrations, illustrating the importance of identity verification before credit distribution.

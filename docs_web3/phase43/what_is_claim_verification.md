# What Is Claim Verification

## Why It Exists

Insurance without verification is a giveaway. If anyone could claim a smart contract hack occurred and immediately receive a payout, attackers would simply buy coverage, trigger a fake event, and drain the pool. Claim verification exists to create a trustworthy, objective process that separates legitimate losses from fraudulent or mistaken requests. In decentralized protocols, this verification cannot rely on a single employee in a back office because there is no centralized company to employ them. Instead, verification must use cryptographic proofs, oracle data, governance votes, or automated on-chain triggers to establish that a covered event actually happened before any funds are released.

## Definition

Claim verification is the process by which an insurance protocol confirms that a covered event has occurred and that the claimant is entitled to a payout under the policy terms. Verification methods include parametric triggers from oracle feeds, multisig governance review, zero-knowledge proofs of loss, and challenge periods during which the community can dispute a claim. The goal is to minimize fraud, prevent griefing, and ensure that the premium pool is only depleted by valid claims.

## Real-Life Analogy

Imagine a shipping company that insures cargo against storms at sea. When a captain reports that waves destroyed the containers, the insurer does not immediately write a check. Instead, they check satellite weather data to confirm a storm occurred on the reported route. They inspect the ship's log for consistency. They interview the crew independently. Only when multiple sources corroborate the story does the insurer authorize payment. The verification layers exist because the insurer must protect the premiums of all other clients from a single dishonest captain.

The satellite data is the oracle feed. The ship's log is the on-chain transaction history. The crew interviews are the governance challenge process. The dishonest captain is the fraudulent claimant. The final payment authorization is the smart contract payout.

## Tiny Numeric Example

A protocol covers stablecoin depegs with the following verification rules:

| Rule | Threshold | Verification Source |
|------|-----------|---------------------|
| Price Feed | <$0.95 for >24 hours | Chainlink oracle |
| On-Chain Volume | >$10M abnormal swaps | DEX liquidity oracle |
| Governance Vote | >60% approval | Token holder vote |
| Challenge Window | 48 hours | Community dispute period |

A policyholder files a claim that USDC has depegged. The oracle reports $0.93 for 30 hours, satisfying the first rule. The DEX oracle confirms $12M in abnormal swap volume, satisfying the second rule. The claim enters a 48-hour challenge window. No successful disputes are raised. A governance vote reaches 65% approval. The smart contract releases the payout. Each layer reduces the probability of fraud. If only the price feed had been checked, a temporary exchange glitch could have triggered a wrongful payout. The multi-layer design prevents that.

## Common Confusion

- Claim verification is not the same as KYC identity checks.
  It verifies the event, not the personal identity of the claimant.
- Oracle-based verification is not perfectly trustless.
  Oracles can be manipulated or fail, so robust protocols use multiple independent sources.
- Governance voting is not instant.
  It requires a proposal period, a voting window, and sometimes a timelock before execution.
- A challenge period does not mean claims are always disputed.
  It is a safety window that honest claimants pass without issue.
- Parametric triggers are not subjective.
  They rely on numerical thresholds from objective data feeds, removing human judgment.
- Verification failure does not always mean fraud.
  It can mean the event did not meet the predefined policy terms, even if a real loss occurred.
- Decentralized verification is not faster than traditional insurance.
  It is often slower due to challenge windows and governance delays, but it is more transparent.
- Zero-knowledge proofs are not required for all claims.
  They are advanced tools used when privacy or complex off-chain computation is necessary.

## Key Properties

- Objective criteria defined in policy terms before any claim is filed
- Multi-source oracle aggregation to prevent single-point manipulation
- Governance or community oversight for edge cases and parameter changes
- Challenge windows that allow dispute before irreversible payout
- Automated finality once all conditions are met and timelocks expire

## Where It Appears in Our Code

Claim verification logic is implemented in `src_web3/phase43/insurance_api.ts`.
The API simulates a multi-stage verification flow where claims must pass oracle threshold checks, a challenge window, and a simplified governance vote before payout.
It demonstrates how delays and checks protect the premium pool from invalid disbursements.

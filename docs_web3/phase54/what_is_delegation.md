# What Is Delegation?

## The Problem

In a large DAO, most token holders do not have the time, expertise, or interest to vote on every proposal. If participation drops too low, a small group of active voters can control outcomes, or the DAO may fail to reach quorum. The system needs a way for passive holders to contribute their voting power without requiring constant attention.

## Definition

Delegation is the act of transferring your voting power to a representative, called a delegate, who votes on your behalf. You retain ownership of your tokens, and you can revoke or redirect delegation at any time. The delegate's vote weight equals the sum of all tokens delegated to them, plus any tokens they personally hold.

## How It Works (6 Steps)

1. **Choose a delegate.** A token holder reviews delegates based on their track record, alignment with the holder's values, or expertise in specific topics.

2. **Issue a delegation transaction.** The holder calls the governance program to assign their voting power to the delegate's address. This is a single on-chain action.

3. **Lock voting power for the delegate.** The program records that the holder's tokens are now counted toward the delegate's total. The holder cannot simultaneously vote those tokens themselves.

4. **The delegate votes.** When a proposal is active, the delegate submits a single vote that carries the combined weight of their own tokens and all delegated tokens.

5. **Results are tallied.** The governance program sums votes by delegate and by direct voters. Delegated votes are indistinguishable from direct votes in the final count.

6. **Revoke or redirect.** If the holder disagrees with the delegate's choices, they can undelegate at any time, instantly returning voting power to themselves or assigning it to a different delegate.

## Real-life Analogy

Imagine a shareholder in a large public company. Instead of attending every annual meeting and reading every proxy statement, the shareholder signs a proxy card giving their voting rights to a trusted advisor. The advisor votes on thousands of shares at once. The shareholder can change advisors or vote personally next year without selling their stock.

## Tiny Numeric Example with Proposal Thresholds

A DAO has 1,000 governance tokens outstanding.

- Alice holds 100 tokens and votes directly.
- Bob holds 80 tokens and delegates to Carol.
- Dave holds 70 tokens and delegates to Carol.
- Carol holds 50 tokens herself.

Carol's total voting power is 80 + 70 + 50 = 200 tokens. On a proposal requiring 150 votes to pass, Carol votes "yes" with her 200 tokens. The proposal passes even though only two addresses actually submitted votes (Alice and Carol). If Bob undelegates before the vote ends, Carol's power drops to 120, and the proposal fails unless Alice's 100 tokens also vote "yes."

## Common Confusion

- Does delegation transfer token ownership? No. The holder keeps full custody of their tokens. Only voting rights are assigned.

- Can a delegate spend delegated tokens? No. Delegation affects voting weight only. The delegate has no access to the holder's wallet.

- Is delegation permanent? No. It lasts until the holder actively undelegates or redirects to someone else.

- Does the delegate know who delegated to them? Yes, on-chain delegation is public. The delegate can see the addresses and amounts, which helps them understand their constituency.

- Can you delegate to multiple people? No. Each token holder can delegate to exactly one address at a time, including themselves.

- Do delegates earn fees automatically? No. Any compensation must be arranged off-chain or through a separate proposal. The protocol does not enforce payment.

## Key Properties (5)

1. **Liquid democracy.** Voting power flows to those with time and expertise while preserving the ability to reclaim it instantly.

2. **Quorum preservation.** Delegation helps the DAO reach minimum participation thresholds even when most holders are inactive.

3. **Accountability.** Delegates vote publicly, and holders can remove support immediately if performance drops.

4. **Non-custodial.** Tokens never leave the holder's wallet. There is no counterparty risk.

5. **Composable.** Delegation records are on-chain, so other programs can read delegate reputation or build delegation marketplaces.

## Where It Appears

Delegation is central to Compound's governance, where top delegates manage billions in protocol parameters. It is used in Uniswap, ENS, and Gitcoin to sustain high voter turnout. It also appears in representative democracy experiments like Optimism's Token House, where delegates are elected and publicly track their voting rationale.

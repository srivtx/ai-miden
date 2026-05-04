# What Is Timelock Execution?

## The Problem

Even after a proposal passes, immediate execution is dangerous. A malicious or buggy proposal could drain funds, change critical parameters, or lock the protocol before the community has time to react. There needs to be a mandatory waiting period between the end of voting and the moment the proposal's effects take hold.

## Definition

Timelock execution is a governance pattern that inserts a fixed delay between the conclusion of a successful vote and the on-chain execution of the proposal's instructions. During this delay, the proposal is queued but not yet active. Anyone can review the outcome, and in some systems, a guardian or multi-sig can cancel the proposal before it executes.

## How It Works (6 Steps)

1. **Voting ends.** The proposal's voting period closes. The governance program tallies the for and against votes.

2. **Check pass conditions.** The program verifies that the proposal met quorum and exceeded the required pass threshold.

3. **Queue the proposal.** If the vote passes, the proposal is moved to a queued state with a timestamp marking when it can execute. The timelock duration is a protocol parameter, often 2 to 7 days.

4. **Wait for the delay.** The proposal sits in the queue. During this window, the community reviews the result, security researchers scan for issues, and members decide whether to exit the protocol.

5. **Execute the proposal.** After the delay has elapsed, any user can call the execute function. The governance program verifies the delay has passed, then sends the proposal's instructions to the target programs.

6. **Cancel if needed.** During the delay, a guardian role or multi-sig can cancel the proposal if a critical flaw is discovered. After execution, cancellation is no longer possible.

## Real-life Analogy

Imagine a city council that passes a new zoning law. The law is published in the public record but does not take effect for 30 days. During that month, residents can read the details, file appeals, or move their businesses. If a major error is found, the council can rescind the law before the effective date. Once the 30 days pass, the law is binding.

## Tiny Numeric Example with Proposal Thresholds

A DAO has a timelock of 48 hours (172,800 slots on Solana).

- A proposal to upgrade the treasury program closes at slot 1,000,000.
- It received 65% yes votes, exceeding the 60% pass threshold.
- Quorum was 500 votes; 600 were cast.
- At slot 1,000,001, the proposal is queued with `execute_after = 1,172,800`.
- At slot 1,100,000, a member notices the upgrade contains a bug and calls `cancel`. The proposal is discarded.
- A second proposal passes and is queued. No one cancels it.
- At slot 1,172,801, a member calls `execute`. The program checks that the current slot is greater than `execute_after`, then applies the treasury upgrade.

## Common Confusion

- Is the timelock the same as the voting period? No. Voting is when members cast ballots. Timelock is the pause after voting ends and before execution begins.

- Can anyone execute a queued proposal? Yes. Execution is permissionless once the delay has passed. This prevents the DAO from being stuck if the original proposer disappears.

- Does the timelock prevent proposals from passing? No. It only delays execution. The vote result is final as soon as voting ends.

- Can a proposal be executed before the timelock expires? No. The program enforces the delay at the instruction level.

- Is there always a cancel option? Not always. Some DAOs use immutable timelocks without guardians. This trades flexibility for maximum trustlessness.

- Does timelock protect against all bugs? No. It only provides a window for human review. If no one reviews the proposal, the bug will still execute after the delay.

## Key Properties (5)

1. **Predictability.** Everyone knows exactly when a passed proposal will take effect.

2. **Reaction time.** The delay creates an opportunity to detect errors, coordinate responses, or exit positions.

3. **Permissionless execution.** No special role is needed to trigger execution after the delay, preventing centralized bottlenecks.

4. **Reversibility during delay.** Queued proposals can often be cancelled, providing a safety valve.

5. **Immutable enforcement.** Once the delay passes, execution is automatic and cannot be stopped by any single actor.

## Where It Appears

Timelock execution is used in Compound's Governor Bravo, Uniswap's governance contracts, Aave's protocol upgrades, and Solana DAOs like Mango Markets. It is a standard security control in any DAO that manages significant value or critical infrastructure.

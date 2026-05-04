# Architecture: Step-by-Step Build Guide

This document walks through building the DAO platform from an empty directory to a deployed system. Each step explains why the design choice was made, not just what code to write.

---

## Step 1: Design the Governance Token

**What to do:** Define the token that represents voting power. It can be an existing SPL token or a custom mint. Decide whether voting power is fixed at proposal creation or snapshotted at vote time.

**Why this step matters:** The governance token is the foundation of the entire DAO. Without a clear, auditable token, there is no legitimate way to measure who should have influence. A token that already exists in the ecosystem can bootstrap participation quickly. Snapshotting voting power at proposal creation prevents last-minute token purchases to manipulate a specific vote, which is a common attack vector.

**Implementation notes:** Create a `Mint` account for the token. Each member holds a `TokenAccount`. When a proposal is created, record the current block height or slot as the snapshot point. When a user votes, look up their balance at that snapshot.

---

## Step 2: Implement Proposal Creation

**What to do:** Build the instruction and account structure for creating a proposal. A proposal needs a title, description, target program, target instruction data, and voting parameters (start time, end time, quorum, pass threshold).

**Why this step matters:** The proposal is the atomic unit of governance. Every other feature depends on a well-defined proposal structure. Without clear voting parameters embedded in the proposal itself, the DAO could retroactively change the rules for a vote that is already in progress, destroying trust. Storing the target instruction data on-chain makes the proposal self-executing once it passes, removing the need for a trusted third party to craft the execution transaction.

**Implementation notes:** Define a `Proposal` account with fields for `proposer`, `title`, `description_url`, `target_program`, `target_data`, `start_slot`, `end_slot`, `for_votes`, `against_votes`, `status`, and `bump`. The `status` field tracks states: Draft, Active, Defeated, Succeeded, Queued, Executed, Cancelled.

---

## Step 3: Add Voting (Token-Weighted)

**What to do:** Implement the vote instruction. Users cast a vote "for" or "against" a proposal. The program records their voting power and updates the proposal totals. Prevent double voting.

**Why this step matters:** Voting is the mechanism by which the DAO makes collective decisions. Token-weighted voting ensures that those with the most economic stake in the protocol have the most influence. This aligns incentives: an attacker would need to acquire a majority of tokens to pass a malicious proposal, which is economically self-defeating if the attack destroys the token's value. Preventing double voting is critical for integrity.

**Implementation notes:** Create a `VoteRecord` account per user per proposal to track whether they voted and with what power. When a vote is cast, look up the voter's token balance at the proposal snapshot slot. Add that amount to `for_votes` or `against_votes`. Reject any subsequent vote from the same user on the same proposal.

---

## Step 4: Build the Delegation System

**What to do:** Allow token holders to assign their voting power to a delegate. The delegate votes on their behalf. The holder can undelegate at any time. Voting power must be recomputed correctly when delegation changes.

**Why this step matters:** Most token holders are passive. Without delegation, voter turnout is low, making it easy for a small active minority to control outcomes. Delegation creates a liquid democracy where influence naturally flows to engaged and knowledgeable participants. Because delegation is non-custodial, it avoids the security risks of pooling tokens in a centralized service.

**Implementation notes:** Add a `delegation` field to user state or a separate `DelegateRecord`. When computing voting power for a voter, check if they are a delegate and sum all delegated balances. When a user undelegates, update the records immediately so future proposals reflect the change.

---

## Step 5: Create the Timelock

**What to do:** After a proposal passes, place it in a queued state. Record the earliest slot at which it can be executed. Reject execution before that slot. Allow cancellation during the queued period.

**Why this step matters:** The timelock is the single most important security control in the DAO. It transforms governance from an instant attack vector into a manageable process. Even if an attacker passes a malicious proposal, the delay gives the community time to fork the protocol, exit liquidity, or coordinate a cancellation. Without a timelock, a flash loan attack could pass and execute a proposal in a single block.

**Implementation notes:** Add `queued_at` and `execute_after` fields to the `Proposal` account. In the `queue` instruction, set `execute_after = current_slot + timelock_duration`. In the `execute` instruction, assert `current_slot > execute_after`. In the `cancel` instruction, assert the proposal is in the Queued state.

---

## Step 6: Implement Treasury Execution

**What to do:** Build a separate treasury program that holds funds. The program should release funds only when it receives a valid execution signal from the governance program. Enforce multi-sig thresholds and spending limits.

**Why this step matters:** The treasury is what the DAO is actually governing. If funds can be moved without strict governance controls, the DAO is ceremonial. A separate program enforces the principle of least privilege: the treasury program does not need to know about proposals or votes; it only needs to trust the governance program's signature. Multi-sig adds a layer of operational security, and spending limits contain the damage from any single proposal.

**Implementation notes:** The treasury program owns a vault token account. It exposes an `execute_transfer` instruction that requires the governance program as a signer or that validates a proposal execution PDA. It checks that the amount is below the configured spending limit and that enough multi-sig signers have approved.

---

## Step 7: Add Emergency Pause

**What to do:** Implement a global pause flag in the governance program. When active, new proposals cannot be created, votes cannot be cast, and proposals cannot be executed. Only a guardian or multi-sig can toggle the pause.

**Why this step matters:** No code is perfect. If a critical vulnerability is discovered in the governance or treasury program, the DAO needs a way to halt all state-changing operations immediately while a fix is prepared. This is a circuit breaker. Without it, the DAO could be exploited repeatedly during the time it takes to pass an emergency proposal.

**Implementation notes:** Store a `paused: bool` field in the governance config account. Check this flag at the start of every mutable instruction. Use a separate `toggle_pause` instruction protected by a guardian signer.

---

## Step 8: Test Governance Flows

**What to do:** Write end-to-end tests covering the happy path and edge cases. Test proposal creation, voting with delegated power, queuing, timelock waiting, execution, treasury release, cancellation, and emergency pause.

**Why this step matters:** On-chain programs are immutable once deployed. Bugs cannot be patched with a hotfix. Testing is the only opportunity to find logic errors before real funds are at risk. Edge cases like delegation changes during an active vote, executing twice, or voting after the deadline are where most vulnerabilities hide.

**Implementation notes:** Use the Solana Program Test framework or Anchor's test suite. Create mock accounts for token holders, delegates, and the guardian. Simulate slot advancement to test timelock behavior. Verify account balances before and after treasury operations.

# Phase 58 Architecture: Building a Token Launchpad From Scratch

This document provides a step-by-step guide to building the Phase 58 token launchpad system from an empty directory to a fully functional decentralized fundraising platform. Each step explains not only what to build, but why the component exists and how it fits into the larger system.

---

## Step 1: Design Project Registration

### What to Build

Create a `ProjectAccount` struct that stores the core configuration of a token sale. This struct should include the token mint address, the project admin's public key, the sale start and end timestamps, the soft cap amount, the hard cap amount, the accepted payment token mint, and a boolean flag indicating whether the sale has been finalized.

Implement an `initialize_project` instruction that accepts these parameters and creates a new `ProjectAccount` on-chain. Validate that the start time is in the future, that the end time is after the start time, and that the soft cap is strictly less than the hard cap. Store the admin's public key so that only they can modify project-specific settings before the sale begins.

### Why This Step Matters

Project registration is the foundation of the entire launchpad. Without a structured configuration account, the contract has no reference point for what tokens are being sold, when the sale occurs, or what success looks like. By storing the soft cap and hard cap on-chain at initialization, you create immutable boundaries that prevent the project team from moving the goalposts after participants have already committed funds.

The admin authority is necessary because someone must whitelist participants, trigger finalization, and manage emergency scenarios. However, by storing this authority in a dedicated field rather than allowing unrestricted access, you create an auditable trail of privileged actions. This step transforms an abstract idea into a concrete on-chain record that every subsequent instruction will reference.

### Key Design Decision

Use a Program Derived Address (PDA) for the `ProjectAccount` seeded by the project admin's public key and a project nonce. This ensures that each admin can create multiple projects without account collision, and it allows other instructions to deterministically derive the project address without needing to store or pass it manually.

---

## Step 2: Implement Tiered Whitelist

### What to Build

Create a `WhitelistEntry` account that maps a participant's wallet address to a tier level. Define a `TierConfig` struct that holds the price per token, maximum allocation per wallet, and total tokens reserved for each tier. Store the `TierConfig` array inside the `ProjectAccount` so that all tier parameters are part of the project's immutable configuration.

Implement an `add_to_whitelist` instruction that only the project admin can invoke. This instruction creates a `WhitelistEntry` account for a specific wallet and assigns it a tier level. Implement a `verify_tier` helper function that checks whether a wallet has an active whitelist entry and returns its tier parameters. Reject any purchase attempt from a wallet that does not have a whitelist entry.

### Why This Step Matters

A tiered whitelist is the mechanism by which a project rewards its most valuable community members. Without this layer, the sale devolves into a free-for-all where bots and whales dominate. The whitelist creates a permissioned gate that ensures only approved addresses can participate, while the tier assignment determines the economic terms each participant receives.

Separating the whitelist into individual accounts rather than a single large mapping is a critical Solana design choice. Solana accounts have size limits, and a single project might whitelist thousands of users. By giving each participant their own small `WhitelistEntry` account, you avoid account bloat and enable parallel transactions during high-traffic sale periods.

The reason only the admin can add whitelist entries is to prevent Sybil attacks. If anyone could whitelist themselves, the tier system would be meaningless. The admin acts as a gatekeeper, but their power is bounded. They cannot change tier prices after initialization, and they cannot remove whitelist entries to steal spots. The trust model is minimal: participants trust the admin to form a fair whitelist, but they do not need to trust the admin with their money because the sale contract holds the funds.

---

## Step 3: Build Token Sale Contract

### What to Build

Implement a `contribute` instruction that accepts a payment amount from a participant. Inside this instruction, perform the following checks in order: verify that the current timestamp is between the sale start and end times, verify that the participant has a valid `WhitelistEntry`, verify that the participant's total contributions plus the new amount do not exceed their tier's maximum allocation, and verify that the project's total raised plus the new amount does not exceed the hard cap.

If all checks pass, transfer the payment tokens from the participant's token account to a project escrow token account. Update the participant's contribution total in a `Contribution` account. Calculate the number of tokens purchased using the participant's tier price and add this to their pending token balance.

### Why This Step Matters

The `contribute` instruction is the heart of the launchpad. It is where economic value flows from participants to the project, and it is the most attack-sensitive surface in the entire system. Every validation check exists to prevent a specific category of exploit.

The time check prevents early contributions that might exploit unannounced tier openings. The whitelist check ensures that only approved participants can buy. The allocation check enforces fairness by preventing any single wallet from monopolizing a tier. The hard cap check protects the project from over-raising, which can dilute token value and create treasury management problems.

The escrow pattern is essential here. If contributions were sent directly to the project team's wallet, there would be no way to enforce refunds if the soft cap is missed. By holding funds in a contract-controlled escrow account, you create the technical possibility of returning those funds. The `Contribution` account tracks each participant's individual deposit so that refunds can be processed accurately without needing to iterate through all transactions on-chain, which would be computationally expensive.

### Key Design Decision

Use an Associated Token Account (ATA) for the project escrow so that the escrow address is deterministically derived from the project PDA and the payment mint. This eliminates the need to store or pass the escrow address manually and reduces the risk of funds being sent to the wrong account.

---

## Step 4: Add Vesting Schedule Integration

### What to Build

Create a `VestingSchedule` account that defines how purchased tokens will be released over time. This account should store the total number of tokens to be vested, the vesting start timestamp, the vesting duration in seconds, the number of vesting intervals, and the amount released per interval. Implement a `create_vesting_schedule` instruction that the project admin invokes during project registration or before the sale begins.

Modify the `contribute` instruction so that instead of immediately transferring purchased tokens to the participant, it increments a vested balance in the participant's `Contribution` account and records the vesting schedule ID that applies to those tokens.

### Why This Step Matters

Vesting is the bridge between the fundraising phase and the long-term success phase. Without vesting, participants receive all their tokens immediately after the sale ends. This creates massive sell pressure the moment the token lists on an exchange, often crashing the price and destroying confidence in the project. Vesting aligns participant incentives with the project's timeline by ensuring that token holders have a financial interest in the project's continued success.

By storing the vesting schedule at the project level rather than per-user, you reduce storage costs. Every participant in the same sale follows the same vesting rules, which is the standard practice for launchpads. The `VestingSchedule` account acts as a template. When a participant claims tokens, the contract reads this template to determine how many tokens are currently unlocked.

The reason vesting is integrated during the contribution phase rather than after finalization is to ensure atomicity. If tokens were delivered immediately and then clawed back into a vesting contract later, you would need a complex and risky token migration. By never delivering the tokens in the first place and instead recording them as vested, you maintain a clean separation between liquid and locked balances from day one.

---

## Step 5: Implement Cliff and Unlock

### What to Build

Extend the `VestingSchedule` to include a `cliff_duration` field measured in seconds. The cliff represents a period after the vesting start time during which no tokens are releasable, even though the vesting clock has started. Implement a `claim_tokens` instruction that participants invoke to withdraw their unlocked tokens.

Inside `claim_tokens`, calculate the elapsed time since the vesting start. If the elapsed time is less than the cliff duration, return zero releasable tokens. If the elapsed time exceeds the cliff duration, calculate the number of full intervals that have passed since the cliff ended, multiply by the tokens per interval, subtract any tokens already claimed, and transfer the resulting amount to the participant's token account.

### Why This Step Matters

The cliff period is a psychological and market stability tool. It prevents participants from selling their initial allocation immediately upon token distribution, which is often the most volatile period for a new token. By enforcing a mandatory waiting period, the project demonstrates that the team and early investors are committed to at least a short-term holding period.

From a technical perspective, the cliff adds a boundary condition to the vesting math. Without it, the vesting calculation is linear: elapsed time divided by total duration multiplied by total tokens. With a cliff, the calculation has two regions. Before the cliff, output is zero. After the cliff, the calculation proceeds as normal but uses the cliff end time as the new starting point for interval counting.

The `claim_tokens` instruction uses a pull pattern, where the participant actively requests their tokens rather than the contract pushing tokens automatically. This is necessary because automatic distribution would require the contract to hold signing authority over all participant token accounts, which is a security nightmare. The pull pattern gives participants control over when they pay transaction fees and when they receive their tokens.

### Key Design Decision

Store the total claimed amount in the participant's `Contribution` account. This prevents double-claims without needing to maintain a separate claims history. The contract simply subtracts the cumulative claimed amount from the total earned amount to determine the current releasable balance.

---

## Step 6: Add Refund If Soft Cap Missed

### What to Build

Implement a `finalize_sale` instruction that can only be called after the sale end time has passed. This instruction sums all contributions recorded in `Contribution` accounts and compares the total against the project's soft cap. If the total is greater than or equal to the soft cap, set the project state to `Successful`, disable the `refund` instruction, and enable the `withdraw_funds` instruction for the admin. If the total is less than the soft cap, set the project state to `Failed` and enable the `refund` instruction.

Implement the `refund` instruction. It checks that the project state is `Failed`, verifies that the caller has a non-zero contribution balance, transfers the exact contributed amount from the escrow token account back to the caller's token account, and sets the caller's contribution balance to zero.

### Why This Step Matters

This is the safety mechanism that makes the entire launchpad credible. Without a refund option, participants are making irreversible donations to a project that might never ship a product. The soft cap creates a collective decision point. If the community does not collectively commit enough capital to reach the minimum threshold, the project is deemed non-viable and all funds are returned.

The `finalize_sale` instruction is a state transition function. It moves the project from an active fundraising state to a terminal state, either success or failure. This transition is irreversible. Once finalized, the project cannot accept new contributions or change its status. This immutability is what gives participants confidence. They know that the rules cannot be rigged after the fact.

The refund instruction is deliberately simple. It does not attempt to batch refunds or iterate through all participants. Each participant calls it individually. This design choice prioritizes reliability over convenience. A batch refund transaction might exceed Solana's compute unit limit or fail partway through, leaving some participants without their money. Individual refunds are atomic, predictable, and gas-efficient for the contract.

### Key Design Decision

Do not burn or destroy tokens during a failed sale. Since tokens were never minted or transferred to participants in a failed sale, there is no need for a burn mechanism. The project retains its originally locked token supply in its treasury, and participants retain their original payment currency. The state after a failed refund is identical to the state before the sale began.

---

## Step 7: Build Admin Controls

### What to Build

Implement a set of administrative instructions that only the project admin can invoke before the sale begins. These should include `update_tier_config` to adjust tier prices and allocations before any whitelisting occurs, `pause_sale` to temporarily block new contributions in case of an emergency, and `emergency_withdraw` to return all escrowed funds to participants if a critical bug is discovered before finalization.

Implement access control using a modifier or helper function that checks whether the transaction signer matches the admin field stored in the `ProjectAccount`. Reject any admin instruction if the sale has already been finalized.

### Why This Step Matters

Decentralization does not mean abandoning all control. It means distributing control according to transparent rules. Admin controls are necessary because real-world projects encounter edge cases that cannot be predicted at deployment. A project might need to pause the sale if a critical vulnerability is discovered in the payment token contract. They might need to adjust tier configurations if the initial parameters were miscalculated and no contributions have occurred yet.

However, admin power must be bounded. The access control helper enforces that only the original admin can perform these actions. The finalization check prevents the admin from changing rules after participants have already committed funds under the old terms. The `emergency_withdraw` function is a kill switch that prioritizes participant safety over project continuity.

The reason these controls exist on-chain rather than through a multisig or DAO is speed. In an emergency, waiting for a DAO vote might take days, during which funds remain at risk. A single admin can act immediately. For high-stakes launches, this admin key is often held by a multisig wallet or a hardware security module, combining the speed of single-key action with the security of shared custody.

### Key Design Decision

Log every admin action to the Solana event log using structured event emissions. This creates an immutable audit trail that participants and external monitors can review. If an admin abuses their power, the evidence is permanently recorded on-chain and can be used to hold them accountable through social or legal channels.

---

## Step 8: Test Full Sale Flow

### What to Build

Write comprehensive tests that cover the following scenarios: project initialization with valid and invalid parameters, tier whitelisting by the admin and rejection of unauthorized whitelist attempts, contributions within and exceeding allocation limits, contributions before and after the sale window, finalization above the soft cap with successful token distribution, finalization below the soft cap with full refunds, vesting claims during the cliff period returning zero tokens, vesting claims after the cliff returning the correct partial amount, admin pause and emergency withdraw functionality, and edge cases such as attempting to double-contribute, double-claim, or double-refund.

### Why This Step Matters

Testing is not an optional polishing step. In blockchain development, untested code is broken code. A single missing validation check can lead to the loss of millions of dollars. The scenarios listed above are not arbitrary. Each one corresponds to a known exploit vector or user error pattern that has caused real financial damage in production smart contracts.

The parameter validation tests ensure that the contract rejects nonsensical configurations before they can harm users. The allocation and timing tests ensure that the sale rules are enforced mechanically, not socially. The success and failure path tests ensure that the two terminal states of the sale function exactly as specified. The vesting tests ensure that the mathematical release schedule is accurate to the second. The admin tests ensure that privileged functions cannot be invoked by random participants.

Edge case testing is particularly important because smart contracts handle money. A double-refund bug, where a participant claims a refund twice and drains the escrow, would destroy the project's credibility and potentially bankrupt legitimate participants. A double-claim bug could over-allocate tokens and break the project's tokenomics. These tests are the final line of defense against catastrophic failure.

### Key Design Decision

Use Anchor's testing framework with a local validator to simulate time progression. Since vesting and sale windows depend on timestamps, you need the ability to warp the blockchain clock forward in tests. This allows you to verify cliff and unlock behavior without waiting for real time to pass, making the test suite fast enough to run on every code change.

---

## Integration Checklist

After completing all eight steps, verify that the system behaves as a cohesive whole:

1. A project admin can register a project with a token, caps, timeline, and vesting schedule.
2. The admin can whitelist wallets into tiers with distinct prices and limits.
3. Whitelisted wallets can contribute during the sale window without exceeding limits.
4. Contributions are held in escrow and recorded against each participant's address.
5. After the sale ends, the admin can finalize. If the soft cap is met, the sale succeeds. If not, refunds are enabled.
6. Successful participants can claim vested tokens according to the cliff and unlock schedule.
7. Failed sale participants can reclaim their exact contributions through the refund function.
8. Admin controls operate only before finalization and emit audit events.

This architecture produces a trustless, transparent, and fair token launchpad that serves both project creators and participant investors.

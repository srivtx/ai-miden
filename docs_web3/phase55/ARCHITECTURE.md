# Phase 55: Architecture — Step-by-Step Build from Scratch

This document guides you through building the complete yield farming protocol. Each step explains WHY the design choice was made.

---

## Step 1: Design Staking Pool Accounts

**What to do**: Define the on-chain data structures for pools and user positions.

**Pool account fields**:
- `authority`: The admin who can update emission rates. WHY: Centralized control is needed during bootstrap; can be transferred to governance later.
- `staking_token_mint`: The SPL token users deposit. WHY: Each pool supports exactly one staking asset for clarity.
- `reward_token_mint`: The token paid as rewards. WHY: Separating staking and reward tokens allows flexible incentives (e.g., stake SOL-USDC LP, earn PROTO token).
- `reward_per_share_stored`: A u128 accumulator tracking total rewards per staked token. WHY: This is the mathematical engine that makes O(1) reward calculation possible.
- `last_update_time`: Unix timestamp of the last reward accrual. WHY: Rewards accrue over time, so we must know the elapsed duration.
- `reward_rate`: Tokens emitted per second. WHY: Using per-second rate instead of per-block avoids chain-speed dependency.
- `total_staked`: Total tokens currently in the pool. WHY: Reward distribution divides by this to compute per-share amounts.

**User account fields**:
- `owner`: The wallet that owns this position. WHY: Prevents unauthorized access to rewards.
- `pool`: The pool this position belongs to. WHY: A user can stake in multiple pools; each needs isolated tracking.
- `staked_amount`: Principal tokens deposited. WHY: Needed to calculate the user's share of the pool.
- `reward_per_share_paid`: The global accumulator value at the user's last claim. WHY: The difference between global and personal accumulator equals pending rewards.

**WHY this design**: Using a global accumulator is the industry standard because it scales to any number of users without iterating. Each user only needs to store their personal snapshot.

---

## Step 2: Implement Single-Pool Staking

**What to do**: Write instructions to create a pool, stake tokens, and unstake tokens.

**Create pool**:
- Allocate a new account with the pool struct. WHY: Solana requires explicit account allocation.
- Initialize all fields to zero or the provided authority. WHY: Uninitialized memory is dangerous; zeroing prevents garbage data.
- Validate that staking and reward mints are valid SPL tokens. WHY: Invalid mints would break token transfers.

**Stake**:
- Transfer staking tokens from user to pool token account via CPI. WHY: The program must custody tokens to prove the user committed capital.
- Update `total_staked`. WHY: Future reward calculations depend on the new total.
- Update the global `reward_per_share_stored` before recording the stake. WHY: Rewards must accrue up to this moment so the new stake does not retroactively earn past rewards.
- Record the current global accumulator in the user's `reward_per_share_paid`. WHY: The user's reward clock starts now, not at pool creation.

**Unstake**:
- Calculate pending rewards. WHY: Users must not lose unclaimed rewards when withdrawing principal.
- Transfer staking tokens from pool back to user. WHY: Principal is returned in full.
- Reduce `total_staked`. WHY: Future reward calculations must reflect the reduced pool size.
- Zero out the user's `staked_amount`. WHY: Prevents double-withdrawal.

**WHY this design**: Staking is a simple escrow pattern. The program holds tokens and tracks who deposited what. The key complexity is in reward math, which we defer to the next step.

---

## Step 3: Add Multi-Pool Support

**What to do**: Ensure the program can handle many independent pools without collision.

**Pool address derivation**:
- Use a PDA seeded by `[b"pool", staking_token_mint.as_ref(), reward_token_mint.as_ref(), pool_index.to_le_bytes()]`. WHY: PDAs are deterministic and collision-resistant. Including both mints and an index allows multiple pools with the same pair.

**User position derivation**:
- Use a PDA seeded by `[b"user", pool.as_ref(), owner.as_ref()]`. WHY: Each user gets exactly one position per pool, preventing fragmentation.

**Program entry point**:
- Route instructions based on a discriminant byte. WHY: Solana programs have a single entry point; manual routing is required.
- Validate all accounts in each instruction handler. WHY: Solana's parallel execution model requires explicit account validation to prevent race conditions.

**WHY this design**: Multi-pool support turns a toy into a platform. Deriving addresses from seeds means clients can compute addresses off-chain without querying, which is critical for UX.

---

## Step 4: Implement Reward Accrual

**What to do**: Write the mathematical core that calculates how many rewards have been earned.

**Update reward-per-share**:
- Formula: `reward_per_share_stored += (elapsed_seconds * reward_rate * PRECISION) / total_staked`. WHY: This converts a time-based emission rate into a per-token debt accumulator. PRECISION (e.g., 1e12) prevents integer division truncation from destroying accuracy.
- Only update if `total_staked > 0`. WHY: If nobody is staking, rewards have nowhere to go. They should not accumulate in a vacuum; they are effectively burned or deferred.

**Calculate pending rewards for a user**:
- Formula: `pending = (staked_amount * (current_reward_per_share - user_reward_per_share_paid)) / PRECISION`. WHY: The difference in accumulators represents rewards per token earned since the user's last interaction. Multiplying by stake amount scales to the user's position.

**Claim rewards**:
- Call `update_reward_per_share()` first. WHY: Rewards must be accrued up to the current block time.
- Calculate pending rewards. WHY: Determines the exact payout.
- Transfer reward tokens from pool vault to user wallet. WHY: Rewards are liquid and immediately usable.
- Set `user_reward_per_share_paid = current_reward_per_share`. WHY: Resets the user's debt so they cannot claim the same rewards twice.

**WHY this design**: This is the Synthetix staking rewards algorithm. It is battle-tested, gas-efficient, and mathematically exact. Using u128 with a precision factor handles all realistic token decimal configurations without floating point.

---

## Step 5: Add Boost NFT Mechanics

**What to do**: Integrate the boost program so NFTs can multiply effective stake.

**Boost program responsibilities**:
- Mint NFTs with metadata encoding multiplier and expiration. WHY: On-chain metadata makes boosts self-describing and verifiable.
- Maintain a whitelist of valid boost mints. WHY: Prevents users from minting fake boosts and exploiting the farm.

**Farm program integration**:
- During `apply_boost`, verify the user holds at least one token from a whitelisted boost mint. WHY: Ownership proof is required.
- Read the multiplier from the NFT metadata account. WHY: The multiplier is stored off the main mint to save space.
- Store `boost_nft_mint` and `boost_multiplier` in the user position. WHY: Caching avoids re-reading metadata on every claim, saving compute units.

**Reward calculation with boost**:
- Effective stake = `staked_amount * boost_multiplier / BOOST_PRECISION`. WHY: Multipliers are stored as integers (e.g., 1500 for 1.5x) to avoid floats.
- When computing the user's share of total effective stake, use effective stake instead of raw stake. WHY: The boost only affects reward distribution, not the actual tokens held.

**Re-validation**:
- On every claim and unstake, re-check NFT ownership. WHY: NFTs are transferable; a user should not keep a boost after selling the NFT.
- If ownership is lost, set multiplier to 1.0x. WHY: Graceful degradation prevents transaction failures.

**WHY this design**: Boosts add a powerful gamification layer. By keeping the boost program separate, we maintain clean separation of concerns. Re-validating on every action prevents exploits at the cost of slightly higher compute, which is acceptable for security.

---

## Step 6: Build Auto-Compounder

**What to do**: Create a standalone service that harvests and reinvests rewards.

**Service structure**:
- A long-running Node.js process. WHY: It must monitor the blockchain continuously.
- A database or in-memory map of opted-in users and their pools. WHY: The service needs to know whom to compound for.

**Monitoring loop**:
- Every N seconds, fetch all user positions. WHY: Regular polling is simpler and more reliable than WebSocket subscriptions for this use case.
- For each user, call a simulated `claim` to determine pending rewards. WHY: Simulation is free and avoids wasting gas on small claims.

**Harvest trigger**:
- If `pending_rewards_value > gas_cost_threshold`, submit a real claim transaction. WHY: Compounding is only profitable when rewards exceed transaction costs.

**Reinvestment**:
- After claiming, swap reward tokens for staking tokens via a DEX aggregator or AMM. WHY: The pool only accepts staking tokens, so rewards must be converted.
- Stake the swapped tokens back into the pool. WHY: This increases principal and compounds future earnings.

**Fee handling**:
- Deduct a percentage from harvested rewards before reinvesting. WHY: The service needs sustainable revenue.
- Record fees in a dedicated account. WHY: Transparency and auditability.

**WHY this design**: Off-chain compounders are standard in DeFi because they are flexible and cheap. The user grants a limited permission (claim-only, not withdraw), maintaining self-custody. The service amortizes gas costs by batching transactions.

---

## Step 7: Test Reward Math

**What to do**: Write exhaustive tests for the reward calculation logic.

**Unit tests in Rust**:
- Test `update_reward_per_share` with zero total stake. WHY: Edge case; must not panic or divide by zero.
- Test single user staking, waiting, and claiming exact expected amount. WHY: Validates the core math.
- Test two users with different entry times. WHY: Ensures late entrants do not steal early rewards.
- Test unstake without claim. WHY: Ensures automatic claim-on-unstake works.
- Test precision boundaries with u128. WHY: Integer overflow or truncation must not occur.

**Integration tests with TypeScript**:
- Deploy to local validator. WHY: Tests the actual program binary, not just logic.
- Simulate a full user journey: create pool, stake, wait, claim, apply boost, compound. WHY: End-to-end validation catches instruction serialization and account validation bugs.
- Verify APR matches expected value over a known time period. WHY: Confirms the emission rate is implemented correctly.

**WHY this design**: DeFi protocols handle real money. A single math bug can drain the treasury. Exhaustive testing is non-negotiable. Local validator tests catch the subtle bugs that unit tests miss, like CPI account validation.

---

## Step 8: Deploy

**What to do**: Build both programs, deploy to devnet, and verify.

**Build**:
- Compile `farm` and `boost` with `cargo build-bpf`. WHY: Produces the `.so` binary that Solana validators execute.

**Deploy**:
- Use `solana program deploy` with a funded devnet wallet. WHY: Devnet is free and mimics mainnet behavior.
- Record program IDs. WHY: Clients need these to construct transactions.

**Verify**:
- Call `getProgramAccounts` to confirm program exists. WHY: Basic sanity check.
- Run the integration test suite against devnet. WHY: Devnet has network latency and slot timing that local validators do not; this catches timing assumptions.
- Initialize a real pool and stake a small amount. WHY: The ultimate test is a real transaction on a real network.

**WHY this design**: Deployment is the final step, not the first. By testing thoroughly before deploying, we minimize the risk of deploying a buggy program that is expensive to upgrade.

---

## Build Order Summary

1. Define data structures (Pool, UserPosition)
2. Implement stake and unstake (no rewards yet)
3. Add multi-pool PDA derivation
4. Implement reward-per-share math
5. Integrate boost NFT verification
6. Build the compounder service
7. Write Rust unit tests and TS integration tests
8. Build, deploy to devnet, verify

Follow this order strictly. Each step depends on the previous one being correct.

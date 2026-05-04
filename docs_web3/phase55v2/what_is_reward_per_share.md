# What is Reward Per Share?

## The Problem

Calculating proportional rewards for thousands of users in a staking pool is computationally impossible on-chain. If you have 10,000 stakers and you try to iterate through every user to update their reward balance on every deposit, the transaction would exceed Solana's compute unit limit and fail. Phase 55 used a naive approach that could not scale beyond a handful of users without running out of gas.

## Definition

Reward per share is a Synthetix-style mathematical accumulator that tracks the total rewards distributed per unit of staked token over time. Instead of updating every user's reward balance on every pool action, the pool stores a single global variable (reward_per_share) that increases as rewards are deposited. Each user stores their personal snapshot (reward_debt) of this accumulator at the time of their last interaction. Their pending rewards are calculated on-demand as: `(user_stake * current_reward_per_share) - reward_debt`.

## How It Works (6 Steps)

1. **Initialize Pool**: The pool starts with `reward_per_share = 0` and `total_staked = 0`. No rewards have been distributed yet.

2. **First Stake**: User A stakes 1,000 tokens. The pool records `total_staked = 1,000`. User A's `reward_debt = 1,000 * 0 = 0`. No rewards are pending because no time has passed.

3. **Rewards Accrue**: The protocol deposits 500 reward tokens into the pool over one day. The pool calculates `reward_per_share += 500 / 1,000 = 0.5`. Only the global variable changes. User A's account is not touched.

4. **Second Stake**: User B stakes 2,000 tokens. Before updating state, the pool first pays out User A's pending rewards implicitly by updating `reward_per_share`. Then User B's `reward_debt = 2,000 * 0.5 = 1,000`. This represents the rewards that accrued before User B joined, which User B is not entitled to.

5. **User A Claims**: User A calls claim. The contract calculates: `(1,000 * 0.5) - 0 = 500` reward tokens. A real CPI transfer sends 500 tokens to User A. User A's `reward_debt` is updated to `1,000 * 0.5 = 500` so they cannot claim the same rewards twice.

6. **More Rewards**: Another 300 reward tokens are deposited. `reward_per_share += 300 / 3,000 = 0.1`. Now `reward_per_share = 0.6`. User A's pending rewards: `(1,000 * 0.6) - 500 = 100`. User B's pending rewards: `(2,000 * 0.6) - 1,000 = 200`. The math always works regardless of how many users exist.

## Real-life Analogy

Imagine a company profit-sharing pool. Instead of the accountant writing a check to every employee every time a sale happens, they write the cumulative profit per share on a whiteboard in the break room. Each employee takes a photo of the whiteboard on their payday. Their bonus equals (their shares * current whiteboard number) minus (their shares * the whiteboard number when they last got paid). One whiteboard update serves thousands of employees without individual bookkeeping on every sale.

## Tiny Numeric Example with Actual Token-2022 Code

```rust
// Precision constant to avoid floating point on-chain
const PRECISION: u128 = 1_000_000_000_000_000_000; // WHY: 1e18 precision prevents rounding errors in integer division

// Pool state
pub struct Pool {
    pub reward_per_share: u128, // WHY: Global accumulator with u128 for precision
    pub total_staked: u64,      // WHY: Total staked tokens in the pool
    pub reward_rate: u64,       // WHY: Rewards emitted per second
    pub last_update_time: i64,  // WHY: Timestamp of last state update to calculate time delta
}

// User state
pub struct UserInfo {
    pub staked_amount: u64,     // WHY: User's current stake
    pub reward_debt: u128,      // WHY: Snapshot of reward_per_share at last interaction
}

// Calculate pending rewards on-chain
fn pending_reward(pool: &Pool, user: &UserInfo) -> u64 {
    // WHY: Must use u128 for intermediate math to prevent overflow
    let staked: u128 = user.staked_amount as u128; // WHY: Cast to u128 for precision math
    let rps: u128 = pool.reward_per_share;         // WHY: Current global accumulator
    let debt: u128 = user.reward_debt;             // WHY: User's personal snapshot
    
    // WHY: Multiply first, divide last to maintain precision
    let pending: u128 = staked.checked_mul(rps).unwrap() // WHY: staked * reward_per_share
        .checked_sub(debt).unwrap();                       // WHY: Subtract already-paid rewards
    
    // WHY: Convert back to u64 for token amounts after dividing by precision
    (pending / PRECISION) as u64 // WHY: Remove precision factor to get actual token count
}

// Update reward_per_share when rewards are deposited or time passes
fn update_pool(pool: &mut Pool, current_time: i64, reward_vault_balance: u64) {
    if pool.total_staked == 0 { // WHY: Cannot divide by zero if no one is staking
        pool.last_update_time = current_time; // WHY: Still update timestamp to track time passage
        return;
    }
    
    let time_delta: u64 = (current_time - pool.last_update_time) as u64; // WHY: Seconds since last update
    let reward: u64 = time_delta.checked_mul(pool.reward_rate).unwrap(); // WHY: Total rewards emitted in this period
    
    // WHY: reward_per_share increases by reward / total_staked, scaled by PRECISION
    let increase: u128 = (reward as u128)
        .checked_mul(PRECISION).unwrap()              // WHY: Scale up before division to keep decimals
        .checked_div(pool.total_staked as u128).unwrap(); // WHY: Divide by total stake for per-share amount
    
    pool.reward_per_share = pool.reward_per_share.checked_add(increase).unwrap(); // WHY: Accumulate into global state
    pool.last_update_time = current_time; // WHY: Reset timestamp for next calculation
}
```

## Common Confusion (6 Bullets with "No.")

- No, reward per share does not store each user's reward balance in a map. It stores one global number and each user stores one snapshot. The user's true balance is calculated on-demand, not stored explicitly.

- No, you cannot have precision loss if you use a large enough precision factor. With 1e18 precision and u128 arithmetic, the rounding error on a pool with millions of tokens is less than one-billionth of one token, which is negligible.

- No, the reward debt is not a debt that the user owes to the protocol. It is an accounting term representing rewards already credited to the user. A higher reward debt means the user has already claimed more rewards.

- No, you do not need to iterate all users when rewards are deposited. Only the global `reward_per_share` variable changes. Individual users are updated only when they interact with the pool (stake, unstake, or claim), making the system O(1) for reward deposits.

- No, this math only works with linear reward rates. If your protocol has vesting schedules, cliff periods, or decaying emissions, you must adjust the `update_pool` function to account for non-linear reward curves, but the core accumulator pattern still applies.

- No, front-running is not possible with reward per share because the accumulator only moves forward. A user who sees a reward deposit transaction in the mempool and tries to stake before it lands will still have their `reward_debt` set to the current (pre-deposit) `reward_per_share`, so they gain no advantage.

## Key Properties (5)

1. **O(1) Scalability**: Reward deposits and pool updates are constant-time operations regardless of the number of stakers. A pool with one user and a pool with one million users cost the same compute to update.

2. **Lazy Evaluation**: User rewards are not calculated until the user interacts with the pool. This means the protocol pays zero compute for inactive users. A user who stakes and forgets for a year costs the same on-chain resources as a user who claims daily.

3. **Exact Precision**: Using u128 with a 1e18 precision factor eliminates meaningful rounding errors. Even with billions of tokens and years of accrual, the mathematical error remains sub-atomic (less than one indivisible token unit).

4. **Composability**: The reward per share pattern is protocol-agnostic. The same accumulator math works for staking SOL, USDC, NFTs, or liquidity pool tokens. The underlying asset does not change the math.

5. **Auditability**: Every reward calculation is deterministic and verifiable from on-chain state. An auditor can reconstruct any user's reward entitlement using only the pool's `reward_per_share` and the user's `reward_debt`, with no hidden state or off-chain dependencies.

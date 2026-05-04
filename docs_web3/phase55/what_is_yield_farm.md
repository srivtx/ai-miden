# What Is a Yield Farm?

## The Problem

Liquidity providers need an incentive to lock their capital in decentralized exchanges. Without ongoing rewards, liquidity can exit at any moment, causing slippage and poor trading experience. Yield farming solves this by paying continuous rewards to stakers.

## Definition

A yield farm is a protocol that accepts staked LP tokens or single assets, tracks each user's proportional share over time, and distributes reward tokens based on accrued reward-per-share metrics. Multi-pool farming extends this to many independent pools, each with its own reward rate and token pair.

## How It Works

1. **Pool creation**: The protocol initializes a farming pool with a reward token mint, a staking token mint, and an initial reward emission rate. This establishes the economic parameters.

2. **User stakes**: A user deposits staking tokens into the pool. The protocol records the deposit amount and captures the current global reward-per-share value as the user's entry point.

3. **Reward accrual**: As time passes, the global reward-per-share increases based on the emission rate and total staked amount. This represents the rewards earned per unit of stake.

4. **User claims**: When a user claims, the protocol calculates pending rewards as stake amount multiplied by the difference between current reward-per-share and the user's recorded reward-per-share. It then resets the user's recorded value to the current global value.

5. **User unstakes**: The user withdraws their principal. Before returning tokens, the protocol automatically claims any pending rewards so nothing is lost.

6. **Emission adjustments**: The protocol owner can update reward rates or add new reward tokens. This allows flexible incentive programming across different market conditions.

## Real-life Analogy

Imagine a community garden where members contribute seeds and labor. Each day, the garden produces vegetables. The harvest is divided based on how many seeds you contributed and how long you left them in the ground. If you withdraw your seeds, you receive your share of vegetables earned up to that day. New garden plots can be added for different crops.

## Tiny Numeric Example

A pool emits 86,400 reward tokens per day. User A stakes 100 LP tokens. The total pool stake is 1,000 LP tokens. User A owns 10% of the pool.

APR calculation: If 100 LP tokens are worth $1,000 and daily rewards are worth $86.40, the APR is (86.40 * 365 / 1000) * 100 = 3153.6%. In practice, this is diluted as more users join.

Reward calculation after 1 day: User A receives 86,400 * 100 / 1,000 = 8,640 reward tokens.

Reward-per-share after day 1: 86,400 / 1,000 = 86.4 reward tokens per LP token.

If User B stakes 1,000 more LP tokens on day 2, total stake becomes 2,000. The new reward-per-share for day 2 is 86,400 / 2,000 = 43.2 additional per token. User A's total becomes 86.4 + 43.2 = 129.6. User B's recorded entry is 129.6.

## Common Confusion

- Is yield farming the same as staking? No. Staking usually secures a network. Yield farming specifically refers to earning rewards for providing liquidity or capital to a protocol.

- Are rewards guaranteed? No. Reward rates can change, and the value of reward tokens can drop. Impermanent loss also affects LP stakers.

- Does more TVL mean more rewards for me? No. More total value locked dilutes your share of the rewards. Your personal reward depends on your proportion of the total.

- Can I lose my principal? No, in a standard yield farm your principal is returned on unstake. However, the underlying LP token may suffer impermanent loss if the AMM pool is unbalanced.

- Are rewards compounded automatically? No. Most farms require manual claiming and restaking. Auto-compounders are a separate service layer.

- Is the APR fixed? No. APR is a backward-looking or estimated metric based on current reward rates and token prices. It changes constantly.

## Key Properties

1. **Proportional distribution**: Rewards are strictly proportional to stake amount and duration.

2. **Reward-per-share accounting**: Uses a global accumulator to avoid iterating over all users, making the protocol gas-efficient at scale.

3. **Multi-pool isolation**: Each pool operates independently with separate reward tokens and rates.

4. **Non-custodial principal**: Users retain ownership of their stake and can withdraw anytime unless a lockup is enforced.

5. **Composable with DeFi**: LP tokens from DEXes can be staked, creating yield stacking opportunities.

## Where It Appears

- SushiSwap Onsen pools
- PancakeSwap Syrup Pools
- Curve Finance gauge rewards
- Raydium Fusion Pools on Solana
- Most DEX incentive programs

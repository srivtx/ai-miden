# What Is a Compounding Strategy?

## The Problem

Yield farming generates rewards in a separate token from the staked principal. Left unclaimed, these rewards do not earn additional rewards. Users must manually claim and restake, paying gas fees each time and requiring constant attention. Auto-compounding solves this by programmatically harvesting and reinvesting rewards at regular intervals, maximizing returns through compound interest.

## Definition

An auto-compounding strategy is a programmed service that periodically claims pending rewards from a yield farm, optionally swaps them for the staking token, and restakes the proceeds. This transforms linear reward growth into exponential growth by increasing the principal that earns future rewards.

## How It Works

1. **User opts in**: The user delegates compounding authority to a compounding service, typically by signing a permission message or interacting with a vault contract. This grants the service the right to claim on their behalf.

2. **Monitoring loop**: The compounding service watches the blockchain for claimable rewards across all opted-in users. It runs continuously, checking every block or at fixed time intervals.

3. **Harvest trigger**: When pending rewards exceed a gas-cost-efficient threshold, the service submits a claim transaction. The threshold ensures the compound benefit exceeds the transaction cost.

4. **Reinvestment**: After claiming, the service swaps reward tokens for staking tokens through a DEX if they differ. It then stakes the resulting tokens back into the farm, increasing the user's principal.

5. **Fee deduction**: The service deducts a small performance fee from the harvested rewards. This aligns incentives; the service only earns when users earn.

6. **Reporting**: The service updates off-chain records with the new principal, total harvested amount, and fee charged. Users can view their effective APY versus the base APR.

## Real-life Analogy

Imagine a savings account where interest is paid monthly in cash to your desk. If you leave the cash on the desk, it does not earn interest. You must walk to the bank and deposit it. An auto-compounding service is like an assistant who collects the cash, walks to the bank, and deposits it for you every month, minus a small tip.

## Tiny Numeric Example

User stakes 1,000 tokens. Base APR is 365% (doubles in one year without compounding). Daily reward is 10 tokens.

Without compounding: After 365 days, user has 1,000 principal + 3,650 rewards = 4,650 total.

With daily compounding: Day 1: earn 10, restake. Principal = 1,010. Day 2: earn 10.1, restake. Principal = 1,020.1.

After 365 days of daily compounding: 1,000 * (1 + 0.01)^365 = 1,000 * 37.78 = 37,780 tokens.

Effective APY = 3,678%. The difference between APR and APY is enormous at high frequencies.

If the compounding service charges a 5% fee on rewards and compounds daily: Each day, 9.5 tokens are restaked instead of 10. Effective daily rate = 0.0095. After 365 days: 1,000 * (1.0095)^365 = 1,000 * 31.62 = 31,620 tokens.

## Common Confusion

- Is auto-compounding risk-free? No. Smart contract risk, slippage during swaps, and temporary liquidity issues can cause losses.

- Does compounding change the APR? No. APR is the base rate. Compounding increases the effective APY by reinvesting rewards.

- Can I compound myself? No. Well, you can, but gas costs and time make it inefficient for small positions. Services aggregate many users to amortize costs.

- Is my principal locked in a vault? No. In a non-custodial design, the compounding service only has claim permission, not withdrawal permission. However, many vault designs do custody tokens.

- Are fees charged on principal? No. Reputable services charge fees only on harvested rewards, never on principal.

- Does compounding work with boost NFTs? No. Wait, actually yes. Compounding operates on the reward output, while boosts operate on the reward calculation input. They stack multiplicatively.

## Key Properties

1. **Exponential growth**: Converts linear reward streams into geometric growth by reinvesting principal.

2. **Gas efficiency**: Aggregated compounding amortizes transaction costs across many users.

3. **Permissioned execution**: Requires explicit user authorization to claim on their behalf.

4. **Performance-fee model**: Aligns service provider incentives with user returns.

5. **Composable**: Can be layered on top of any yield farm, boost NFT, or leverage strategy.

## Where It Appears

- Yearn Finance vaults
- Beefy Finance auto-compounding vaults
- Tulip Protocol on Solana
- Harvest Finance
- Most vault-as-a-service platforms in DeFi

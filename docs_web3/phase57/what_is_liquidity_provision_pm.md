# What Is Liquidity Provision in Prediction Markets?

## The Problem

A prediction market with thin order books or wide spreads is unusable. If a trader wants to buy 100 YES shares but there are only 10 available at a reasonable price, the price will spike, discouraging participation. Without liquidity, prices become noisy and fail to reflect true probabilities. We need a mechanism that ensures shares are always available to trade at a fair, continuous price.

## Definition

**Liquidity provision** in prediction markets is the act of depositing collateral into an automated market maker (AMM) pool that facilitates trading of outcome shares. Liquidity providers (LPs) deposit both sides of the market (for example, equal values of YES and NO shares, or the underlying collateral) and earn a portion of trading fees in exchange for bearing the risk of adverse selection and impermanent loss.

## How It Works (6 Steps)

1. **Pool Initialization**: When a market is created, the first liquidity provider deposits collateral (for example, USDC) into the AMM pool. The AMM mints an equal value of YES and NO shares and holds them as reserves.
2. **LP Token Minting**: The AMM mints LP tokens representing the provider's fractional ownership of the pool. These tokens can be transferred or staked elsewhere.
3. **Trading Against the Pool**: Traders buy shares by sending collateral to the pool; the AMM calculates the price using a constant-product curve (x * y = k) or a logarithmic market scoring rule. The pool's reserves shift, changing the implied probability.
4. **Fee Accrual**: Every trade incurs a small fee (for example, 0.3 percent), which remains in the pool, increasing the total value of the LP tokens over time.
5. **Impermanent Loss Exposure**: If the market resolves and one outcome is worth 1 while the other is worth 0, the pool ends up holding mostly worthless shares and some collateral. The LP's final value may be lower than if they had simply held the initial collateral, depending on trading activity and fees.
6. **Liquidity Removal**: LPs burn their LP tokens to withdraw their proportional share of the pool's current reserves (collateral plus both types of shares) plus accumulated fees. They can then hold or redeem shares after market resolution.

## Real-life Analogy

Imagine a currency exchange booth at an airport. The booth always holds both dollars and euros so travelers can trade at any time. The booth owner earns a small spread on every transaction. If suddenly everyone wants euros and no one wants dollars, the booth ends up with too many dollars and too few euros. The owner took a risk by providing liquidity, but the accumulated spreads from thousands of small trades hopefully compensate for that risk.

## Tiny Numeric Example with Shares and Payouts

- The AMM pool starts with 1000 USDC, 1000 YES shares, and 1000 NO shares (constant-product k = 1,000,000).
- Alice provides 100 USDC and receives LP tokens representing 10 percent of the pool.
- Bob buys 100 YES shares. The AMM calculates the required USDC input using the constant-product formula.
- Bob pays 111.11 USDC (including a 1 USDC fee that stays in the pool). The pool now has 1111.11 USDC, 900 YES, 1000 NO.
- Carol buys 100 NO shares, paying 111.11 USDC. Pool: 1222.22 USDC, 900 YES, 900 NO.
- Fees earned: 2 USDC. Alice's 10 percent share is now worth 122.22 USDC in pool value.
- The market resolves to YES. The 900 NO shares become worthless.
- Alice removes liquidity, receiving 122.22 USDC worth of assets: mostly YES shares and USDC. She redeems YES shares for 1 USDC each.
- Alice's final return depends on the mix, but the fees partially offset the loss from holding worthless NO shares in the pool.

## Common Confusion

- No, liquidity providers are not betting on the outcome. They are neutral market makers who earn fees from trading volume, though they are exposed to the final outcome through impermanent loss.
- No, LP tokens are not shares in the prediction outcome. They represent ownership of the AMM pool reserves and the right to withdraw them.
- No, you cannot lose more than your deposit as an LP. The maximum loss is the full deposit, but you cannot be liquidated or go negative.
- No, providing liquidity guarantees profit. If trading fees are low and the outcome is heavily one-sided, impermanent loss can exceed fee revenue.
- No, the AMM price is the same as the true probability. The AMM price reflects supply and demand within the pool, which may diverge from external forecasts due to low liquidity or arbitrage gaps.
- No, removing liquidity before resolution is the same as after. Before resolution you receive a mix of shares and collateral; after resolution you may receive only collateral and winning shares, because losing shares are worthless.

## Key Properties

1. **Continuous Pricing**: The AMM provides a price for any trade size at any time, eliminating the need for counterparties.
2. **Fee Income**: LPs earn passive income proportional to trading volume, creating an incentive to bootstrap new markets.
3. **Impermanent Loss**: LPs bear the risk that the pool's composition shifts toward the losing outcome, potentially reducing returns.
4. **Permissionless Entry**: Anyone can add liquidity to an open pool without approval, democratizing market making.
5. **Composable LP Tokens**: LP tokens can be staked in reward contracts, used as collateral, or traded themselves, increasing capital efficiency.

## Where It Appears

- **Uniswap V3**: Concentrated liquidity AMMs used for trading prediction market shares on Ethereum.
- **Balancer**: Multi-token AMMs that allow custom weights for YES/NO/collateral pools.
- **Polymarket**: Uses a CLOB (central limit order book) with designated market makers, but early versions used AMM liquidity pools.
- **Gnosis Conditional Tokens**: Framework that integrates with AMMs like Balancer for prediction market liquidity.
- **Serum / OpenBook**: On-chain order books on Solana where liquidity providers operate as market makers with limit orders.

# What Is an AMM v2 (Concentrated Liquidity)?

## The Problem

Traditional AMMs (like the original Uniswap v2) spread liquidity evenly across the entire price range from zero to infinity. This is simple, but it is also extremely inefficient. Consider a stablecoin pair like USDC/USDT. The price should always hover near 1.0, yet in a classic AMM, a huge portion of the deposited liquidity is reserved for prices like 0.01 or 100.0, which will never be reached. As a result, traders experience high slippage on the prices that actually matter, and liquidity providers earn very low fees relative to the capital they lock up.

## Definition

A Concentrated Liquidity AMM (CLAMM) is an automated market maker that allows liquidity providers to deposit their assets within a specific, chosen price range rather than across the entire curve. This means capital is allocated precisely where trading actually happens, dramatically improving capital efficiency and reducing slippen for traders.

## How It Works (6 Steps)

1. **Select a Price Range**: A liquidity provider decides on a lower bound price and an upper bound price. They believe the market price will stay inside this range.
2. **Deposit Tokens**: The provider deposits tokens according to the ratio required at the edges of their chosen range. If the current price is inside the range, they deposit both tokens. If the current price is outside, they deposit only one token.
3. **Mint a Position NFT**: The AMM mints a non-fungible token representing that specific position, its range, and its share of the fees. This NFT is proof of ownership.
4. **Trade Within the Range**: When traders swap tokens, the pool uses only the liquidity from positions that cover the current price. As the price moves, it crosses into and out of different positions.
5. **Accumulate Fees**: Trading fees are earned proportionally by the active liquidity positions at the exact moment each trade occurs. Inactive positions earn nothing.
6. **Burn or Update**: The provider can remove liquidity at any time, burning the NFT and receiving back their original tokens plus any earned fees. They can also update the range by closing and reopening a position.

## Real-life Analogy

Imagine a traditional AMM as a farmer who scatters seeds evenly across an entire field, including the rocky hills and the flooded valley. Most seeds are wasted. A concentrated liquidity AMM is like a farmer who uses a map to plant seeds only in the fertile rows where crops actually grow. Every seed has a purpose, and the yield per seed is far higher.

## Tiny Numeric Example

Suppose a classic AMM pool has 100 Token A and 100 Token B. The constant product `k` is `100 * 100 = 10,000`.

A trader wants to buy 10 Token A. To keep `k` constant, the new amount of Token A must be 90.
So the new amount of Token B must be `10,000 / 90 = 111.11`.
The trader must pay `111.11 - 100 = 11.11` Token B.

Now imagine a concentrated liquidity pool where a provider has placed 20 Token A and 20 Token B specifically in the price range that covers the current trade. Because the capital is denser in that exact region, the same 10 Token A trade might only cost the trader 10.5 Token B. The provider earns fees on a much smaller deposit but achieves a better price for the trader.

## Common Confusion

- **No.** It does not mean you can lose more than you deposit. Impermanent loss is still bounded by your deposit value.
- **No.** It is not the same as a limit order. A limit order executes once at a specific price; concentrated liquidity earns fees continuously within a range.
- **No.** You do not have to monitor the price every second. You can set a wide range and treat it like a traditional AMM if you prefer.
- **No.** The NFT is not a speculative JPEG. It is a receipt that encodes your exact deposit parameters and accrued fees.
- **No.** You do not need to be a math expert. The interface calculates the required token ratios for you.
- **No.** It is not exclusive to Ethereum. Concentrated liquidity AMMs exist on Solana, Arbitrum, and many other chains.

## Key Properties

1. **Capital Efficiency**: Providers can achieve the same depth with far less capital, or greater depth with the same capital.
2. **Customizable Risk**: Narrow ranges yield higher fees but higher risk of the price moving out of range; wide ranges are safer but less efficient.
3. **Fee Granularity**: Different fee tiers can exist in the same pool, allowing providers to choose their risk-reward profile.
4. **Non-Fungible Positions**: Each range is unique, so liquidity positions are represented as NFTs rather than fungible LP tokens.
5. **Active Management**: The most successful providers often rebalance their ranges as market prices shift.

## Where It Appears

- Uniswap v3 (the pioneer of concentrated liquidity on Ethereum)
- Orca Whirlpools on Solana
- PancakeSwap v3 on BNB Chain
- Curve v2 (concentrated liquidity with dynamic curves)
- Virtually every modern DEX launching today

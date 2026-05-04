# What Is a Prediction Market?

## The Problem

How do we aggregate the beliefs of thousands of people into a single, reliable probability estimate? Polling is slow and biased. Expert panels are small and expensive. Social media is noisy and unaccountable. We need a mechanism where people put their money where their mouth is, so only those with genuine confidence participate, and the resulting price reflects the true consensus probability of an outcome.

## Definition

A **prediction market** is a financial marketplace where participants trade contracts whose payoff depends on the outcome of a future event. Each contract (or share) pays out a fixed amount (for example, 1 USDC) if a specific outcome occurs, and nothing otherwise. The market price of a share therefore represents the aggregated probability that the market assigns to that outcome. If a "YES" share trades at 0.70 USDC, the market collectively believes there is a 70 percent chance the event will happen.

## How It Works (6 Steps)

1. **Market Creation**: An operator defines an event with discrete outcomes (for example, "Will it rain tomorrow?" with outcomes YES and NO), sets an expiration date, and deposits collateral (for example, USDC) into a smart contract to back the shares.
2. **Share Minting**: The contract mints one pair of complementary shares (one YES and one NO) for every unit of collateral deposited. These shares are fungible tokens that can be traded freely.
3. **Trading**: Participants buy and sell outcome shares through an automated market maker (AMM). The AMM prices shares based on supply and demand; high demand for YES shares raises their price and lowers the price of NO shares.
4. **Oracle Resolution**: After the event concludes, a trusted oracle reports the true outcome to the smart contract. This triggers the resolution state.
5. **Settlement**: Once resolved, winning shares become redeemable for the full collateral value (1 USDC per share), while losing shares become worthless.
6. **Payout**: Traders burn their winning shares and receive the collateral payout from the contract. Liquidity providers reclaim their remaining collateral plus earned fees.

## Real-life Analogy

Imagine a racetrack where bettors buy tickets for Horse A or Horse B. The track sets initial odds, but as money flows in, the odds shift dynamically to balance the pool. When the race finishes, the track announces the winner (the oracle), and ticket holders for the winning horse collect their payout. The odds at any moment reflect the crowd's collective belief about which horse will win.

## Tiny Numeric Example with Shares and Payouts

- Alice creates a market with 100 USDC collateral.
- The contract mints 100 YES shares and 100 NO shares.
- Bob believes it will rain, so he buys 10 YES shares for 7 USDC (market price implies 70 percent probability).
- Carol believes it will not rain, so she buys 10 NO shares for 3 USDC.
- The AMM holds 100 USDC collateral at all times (the total is conserved).
- It rains. The oracle resolves the market to YES.
- Bob burns his 10 YES shares and receives 10 USDC (a profit of 3 USDC).
- Carol's 10 NO shares are worthless; she loses her 3 USDC.
- The 100 USDC collateral is fully distributed to YES shareholders.

## Common Confusion

- No, a prediction market is not the same as a sportsbook. Sportsbooks set odds and take the opposite side of every bet, whereas prediction markets are peer-to-peer and prices are determined by supply and demand.
- No, the market operator does not decide who wins. The oracle reports the objective outcome; the operator only creates the market and earns fees.
- No, buying a share does not mean you believe the outcome will happen. You might be hedging, arbitraging, or providing liquidity.
- No, the price is not guaranteed to equal the true probability. It is the best estimate given all publicly available information at that time, but it can be wrong.
- No, liquidity providers cannot lose money from traders being right. They lose money if the initial pricing is wrong relative to the final outcome, because they are effectively selling both sides of the market.
- No, shares do not expire worthless if the market is unresolved. They remain in circulation until the oracle resolves the market or the market reaches its expiration with a default resolution mechanism.

## Key Properties

1. **Price as Probability**: The trading price of a share directly maps to an implied probability, creating a real-time, crowd-sourced forecast.
2. **Incentive Alignment**: Because participants risk real money, only those with genuine insight or strong conviction tend to trade, filtering out noise.
3. **Permissionless Trading**: Once created, anyone can buy or sell shares without asking for approval, enabling global participation.
4. **Transparent Collateral**: All funds backing the shares are held on-chain in a smart contract, eliminating counterparty risk.
5. **Composable Shares**: Outcome shares are tokens that can be used in other DeFi protocols (for example, as collateral in lending markets) before resolution.

## Where It Appears

- **Polymarket**: Decentralized prediction markets on current events and politics.
- **Augur**: Peer-to-peer prediction markets with decentralized oracle resolution.
- **Gnosis (Omen)**: Conditional token framework for building prediction markets on Ethereum.
- **Kalshi**: Regulated prediction market in the United States for trading on economic and weather events.
- **Metaculus**: Forecasting platform that uses prediction market mechanisms to aggregate expert and crowd forecasts.

# What Is a Call and a Put

## Why It Exists

Market participants face two fundamentally different risks. A corn importer fears prices will rise before their next shipment. A gold miner fears prices will fall before they can sell their extracted ore. A single instrument cannot serve both fears because the directional exposure is opposite. Calls and puts exist to separate these two risk profiles into distinct, tradable contracts. A call profits when the market rises, protecting against upside risk or enabling bullish speculation. A put profits when the market falls, protecting against downside risk or enabling bearish speculation. By splitting the option universe into these two directions, markets achieve precise risk transfer between parties with opposite views.

## Definition

A call option gives the holder the right to buy an underlying asset at a fixed strike price before or on expiration. It increases in value as the underlying price rises above the strike. A put option gives the holder the right to sell an underlying asset at a fixed strike price before or on expiration. It increases in value as the underlying price falls below the strike. The seller of either instrument receives a premium and assumes the opposing obligation.

## Real-Life Analogy

Imagine a theater with two doors. The call door is labeled "Enter Here" and allows ticket holders to buy popcorn at a fixed price of $5 regardless of how high concession prices rise during the show. The put door is labeled "Exit Here" and allows ticket holders to sell their unwanted popcorn back to the theater for $5 regardless of how low street prices fall after the show. If popcorn becomes scarce and rises to $8, the call holder enters and buys cheaply. If popcorn becomes abundant and falls to $2, the put holder exits and sells dearly. The theater manager collects a small fee from everyone who takes a door ticket, knowing that most will not use it.

The call door is the call option. The put door is the put option. The $5 fixed price is the strike. The small fee is the premium. The theater manager is the option writer.

## Tiny Numeric Example

Consider a stock trading at $100. Two options exist:

| Option Type | Strike | Premium | Scenario at $110 | Scenario at $90 |
|-------------|--------|---------|------------------|-----------------|
| Call | $100 | $5 | Exercise, profit $5 net | Expire worthless, lose $5 |
| Put | $100 | $5 | Expire worthless, lose $5 | Exercise, profit $5 net |

At $110, the call holder buys at $100 and can sell at $110, making $10 gross minus $5 premium for $5 net profit. The put holder has no reason to sell at $100 when the market is $110, so the put expires worthless and the premium is lost. At $90, the reverse occurs. The put holder sells at $100 against a $90 market, making $10 gross minus $5 premium for $5 net. The call holder would not buy at $100 when the market is $90, so the call expires worthless.

## Common Confusion

- Buying a call is not the same as buying the asset.
  You control upside exposure with a fraction of the capital, but the contract can expire worthless.
- Buying a put is not short selling.
  Short selling requires borrowing the asset, while a put is a self-contained contract with capped risk.
- The strike price is not the breakeven price.
  For a call, breakeven is strike plus premium. For a put, breakeven is strike minus premium.
- Selling a call is not the mirror image of buying a call.
  The seller has limited gain and potentially unlimited loss, which is the opposite payoff profile.
- Selling a put does not mean you are bearish.
  Put sellers are actually bullish or neutral, because they profit if the price stays above the strike.
- Calls and puts are not used only for speculation.
  Puts are widely used as portfolio insurance, and calls can hedge against rising input costs.
- Being "long" always means owning something, but the risk differs.
  Long a call is bullish. Long a put is bearish. The word long only indicates ownership, not direction.
- Decentralized options do not settle automatically at the best price.
  Exercise is a manual or oracle-triggered action that must be initiated by the holder or protocol.

## Key Properties

- Call payoff increases linearly above the strike, floored at zero
- Put payoff increases linearly below the strike, floored at zero
- Writer exposure is opposite: call writers face unlimited upside risk, put writers face large downside risk
- Premiums for both are determined by moneyness, time remaining, and volatility expectations

## Where It Appears in Our Code

Call and put logic is implemented in `src_web3/phase42/options_api.ts`.
The API accepts a side parameter when creating an option contract and routes the payoff calculation to the appropriate formula.
It demonstrates how the same strike and premium produce opposite payoff profiles depending on whether the contract is a call or a put.

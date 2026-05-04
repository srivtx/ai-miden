# What Is Implied Volatility

## Why It Exists

Two option contracts on the same asset with the same strike and expiration can trade at wildly different premiums if the market expects turbulence. Historical volatility tells us what already happened, but traders need to price what might happen next. Implied volatility exists to extract the market's forward-looking expectation of price swings from the current option premium. It bridges the gap between a known option price and an unknown future, allowing traders to compare whether options are cheap or expensive relative to the expected movement. Without implied volatility, there would be no common language to discuss whether a $10 premium is a bargain or a rip-off.

## Definition

Implied volatility is the expected annualized standard deviation of an asset's returns that is implied by the current market price of an option. It is derived by inverting an option pricing model, such as Black-Scholes, to solve for the volatility input that makes the theoretical price equal to the observed market price. Higher implied volatility means the market expects larger price swings, which increases the probability that the option will finish in the money. Lower implied volatility means the market expects calm, reducing the option's time value.

## Real-Life Analogy

Imagine two identical beach houses for rent during summer. One is in a region where hurricanes are forecast. The other is in a region with clear skies. Even though both houses are the same size and price to buy, the hurricane-region rental costs twice as much because the owner demands extra compensation for the risk of sudden evacuation and damage. The rental price encodes the weather forecast. Implied volatility is the weather forecast encoded in the option price. You cannot see the future storm directly, but you can infer its likelihood from how much people are willing to pay for protection.

The beach house is the underlying asset. The rental price is the option premium. The hurricane forecast is the implied volatility. The extra cost is the risk premium.

## Tiny Numeric Example

Consider a stock at $100 with a call option at $100 strike expiring in 30 days:

| Observed Premium | Implied Volatility | Interpretation |
|------------------|-------------------|----------------|
| $2.00 | 20% | Low expected movement, calm market |
| $5.00 | 45% | High expected movement, uncertain market |
| $10.00 | 80% | Extreme fear, likely event pending |

Using the Black-Scholes formula in reverse, a $2 premium implies that the market expects daily moves of roughly 1.3%. A $10 premium implies expected daily moves of roughly 5%. Traders who believe actual volatility will exceed the implied level buy options, expecting to profit from larger swings. Traders who believe volatility is overstated sell options, expecting to keep the premium as the realized moves fall short of expectations.

## Common Confusion

- Implied volatility is not historical volatility.
  Historical volatility measures past price swings, while implied volatility predicts future swings.
- High implied volatility does not mean the price will go up.
  It means the price is expected to move a lot, but direction is still unknown.
- Implied volatility is not a physical measurement.
  It is a derived figure from a model, and changing the model changes the implied value.
- Low implied volatility does not mean the option is cheap in absolute terms.
  A deep out-of-the-money option can have low implied volatility and still be a poor purchase.
- Implied volatility skew is not random.
  It reflects real supply and demand imbalances across different strike prices.
- Implied volatility cannot be negative.
  It is a standard deviation, and standard deviations are always non-negative.
- Rising implied volatility helps option buyers even if the underlying price does not move.
  This is because the option's time value increases as uncertainty grows.
- Decentralized protocols may not compute implied volatility on-chain.
  It is often calculated off-chain and posted as an oracle input due to computational cost.

## Key Properties

- Forward-looking measure extracted from observed market prices
- Annualized percentage representing expected return dispersion
- Increases during uncertain events and decreases during stable periods
- Skew and term structure describe how implied volatility varies across strikes and expirations

## Where It Appears in Our Code

Implied volatility estimation logic is implemented in `src_web3/phase42/options_api.ts`.
The API includes a simplified inverse pricing function that estimates implied volatility from a given premium, strike, and time to expiration.
This allows users to see how premium changes map to volatility expectations without running complex numerical solvers.

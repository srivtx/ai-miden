# What Is Implied Volatility

## The Problem:

Two option contracts on the same asset with the same strike and expiration can trade at wildly different premiums if the market expects turbulence. Historical volatility tells us what already happened, but traders need to price what might happen next. Implied volatility exists to extract the market's forward-looking expectation of price swings from the current option premium. It bridges the gap between a known option price and an unknown future, allowing traders to compare whether options are cheap or expensive relative to the expected movement. Without implied volatility, there would be no common language to discuss whether a $10 premium is a bargain or a rip-off.

## Definition:

Implied volatility is the expected annualized standard deviation of an asset's returns that is implied by the current market price of an option. It is derived by inverting an option pricing model, such as Black-Scholes, to solve for the volatility input that makes the theoretical price equal to the observed market price. Higher implied volatility means the market expects larger price swings, which increases the probability that the option will finish in the money. Lower implied volatility means the market expects calm, reducing the option's time value.

## How It Works (Step-by-Step):

1. Observe the market price of a traded option, along with its strike price, time to expiration, the current spot price of the underlying asset, and the risk-free interest rate. These five inputs are required to invert the pricing model.

2. Write the Black-Scholes formula for a European call option: C = S0 * N(d1) - K * e^(-rT) * N(d2), where d1 = [ln(S0/K) + (r + sigma^2/2) * T] / (sigma * sqrt(T)) and d2 = d1 - sigma * sqrt(T). N() is the cumulative distribution function of the standard normal distribution. The only unknown is sigma (volatility).

3. Set the Black-Scholes theoretical price C equal to the observed market premium. Since sigma appears inside the non-linear N(d1) and N(d2) terms, there is no closed-form algebraic solution for sigma.

4. Apply a numerical root-finding method, such as the Newton-Raphson iteration or bisection method. Start with an initial guess for sigma (e.g., 30%). Compute the Black-Scholes price. If the computed price is higher than the observed premium, lower sigma; if lower, raise sigma.

5. Repeat the iteration until the difference between the computed price and the observed premium is smaller than a tolerance threshold (e.g., $0.001). The sigma that satisfies this convergence is the implied volatility.

6. The resulting sigma is naturally annualized because T is expressed in years. Express the final value as a percentage. This percentage represents the market's expectation of the underlying asset's annual price dispersion.

## Real-life analogy:

Imagine two identical beach houses for rent during summer. One is in a region where hurricanes are forecast. The other is in a region with clear skies. Even though both houses are the same size and price to buy, the hurricane-region rental costs twice as much because the owner demands extra compensation for the risk of sudden evacuation and damage. The rental price encodes the weather forecast. Implied volatility is the weather forecast encoded in the option price. You cannot see the future storm directly, but you can infer its likelihood from how much people are willing to pay for protection.

The beach house is the underlying asset. The rental price is the option premium. The hurricane forecast is the implied volatility. The extra cost is the risk premium.

## Tiny numeric example:

Consider a stock with the following observed parameters:

| Input | Symbol | Value |
|-------|--------|-------|
| Spot Price | S0 | $100.00 |
| Strike Price | K | $105.00 |
| Time to Expiration | T | 30 days = 30/365 = 0.08219 years |
| Risk-Free Rate | r | 5.0% (0.05) |
| Observed Call Premium | C_market | $2.34 |

We solve for sigma such that Black-Scholes(S0=100, K=105, T=0.08219, r=0.05, sigma) = $2.34.

**Iteration 1: Guess sigma = 20% (0.20)**
d1 = [ln(100/105) + (0.05 + 0.20^2/2) * 0.08219] / (0.20 * sqrt(0.08219))
d1 = [-0.04879 + (0.05 + 0.02) * 0.08219] / (0.20 * 0.28669)
d1 = [-0.04879 + 0.005748] / 0.057338 = -0.7507
d2 = -0.7507 - 0.057338 = -0.8080
N(d1) = 0.2264, N(d2) = 0.2095
C = 100 * 0.2264 - 105 * e^(-0.05*0.08219) * 0.2095
C = 22.64 - 105 * 0.9959 * 0.2095 = 22.64 - 21.88 = $0.76
$0.76 is far below $2.34, so sigma must be higher.

**Iteration 2: Guess sigma = 40% (0.40)**
d1 = [-0.04879 + (0.05 + 0.40^2/2) * 0.08219] / (0.40 * 0.28669)
d1 = [-0.04879 + (0.05 + 0.08) * 0.08219] / 0.11468
d1 = [-0.04879 + 0.010685] / 0.11468 = -0.3323
d2 = -0.3323 - 0.11468 = -0.4470
N(d1) = 0.3698, N(d2) = 0.3274
C = 100 * 0.3698 - 105 * 0.9959 * 0.3274
C = 36.98 - 34.23 = $2.75
$2.75 is above $2.34, so sigma is between 20% and 40%.

**Iteration 3: Guess sigma = 35% (0.35)**
d1 = [-0.04879 + (0.05 + 0.35^2/2) * 0.08219] / (0.35 * 0.28669)
d1 = [-0.04879 + (0.05 + 0.06125) * 0.08219] / 0.10034
d1 = [-0.04879 + 0.009146] / 0.10034 = -0.3951
d2 = -0.3951 - 0.10034 = -0.4954
N(d1) = 0.3464, N(d2) = 0.3102
C = 100 * 0.3464 - 105 * 0.9959 * 0.3102
C = 34.64 - 32.42 = $2.22
$2.22 is slightly below $2.34, so sigma is between 35% and 40%.

**Iteration 4: Guess sigma = 36% (0.36)**
d1 = [-0.04879 + (0.05 + 0.36^2/2) * 0.08219] / (0.36 * 0.28669)
d1 = [-0.04879 + (0.05 + 0.0648) * 0.08219] / 0.10321
d1 = [-0.04879 + 0.009439] / 0.10321 = -0.3813
d2 = -0.3813 - 0.10321 = -0.4845
N(d1) = 0.3515, N(d2) = 0.3141
C = 100 * 0.3515 - 105 * 0.9959 * 0.3141
C = 35.15 - 32.83 = $2.32
$2.32 is extremely close to $2.34. The difference is $0.02.

**Iteration 5: Guess sigma = 36.2% (0.362)**
d1 = [-0.04879 + (0.05 + 0.362^2/2) * 0.08219] / (0.362 * 0.28669)
d1 = [-0.04879 + (0.05 + 0.06552) * 0.08219] / 0.10378
d1 = [-0.04879 + 0.009488] / 0.10378 = -0.3787
d2 = -0.3787 - 0.10378 = -0.4825
N(d1) = 0.3526, N(d2) = 0.3147
C = 100 * 0.3526 - 105 * 0.9959 * 0.3147
C = 35.26 - 32.89 = $2.37
$2.37 is slightly above $2.34.

**Linear interpolation between 36.0% ($2.32) and 36.2% ($2.37):**
IV = 36.0% + [(2.34 - 2.32) / (2.37 - 2.32)] * 0.2%
IV = 36.0% + (0.02 / 0.05) * 0.2%
IV = 36.0% + 0.08% = 36.08%

The implied volatility is approximately **36.1%**. This means the market expects the stock to have an annualized standard deviation of roughly 36.1%. For a 30-day option, the expected move in standard deviation terms is 36.1% * sqrt(30/365) = 36.1% * 0.2867 = 10.35%. The market is pricing in an expected move of approximately +/- $10.35 around the $100 spot price over the next 30 days.

## Common confusion:

- Implied volatility is not historical volatility. No. Historical volatility measures past price swings, while implied volatility predicts future swings.
- High implied volatility does not mean the price will go up. No. It means the price is expected to move a lot, but direction is still unknown.
- Implied volatility is not a physical measurement. No. It is a derived figure from a model, and changing the model changes the implied value.
- Low implied volatility does not mean the option is cheap in absolute terms. No. A deep out-of-the-money option can have low implied volatility and still be a poor purchase.
- Implied volatility skew is not random. No. It reflects real supply and demand imbalances across different strike prices.
- Implied volatility cannot be negative. No. It is a standard deviation, and standard deviations are always non-negative.

## Key properties:

- Forward-looking measure extracted from observed market prices
- Annualized percentage representing expected return dispersion
- Increases during uncertain events and decreases during stable periods
- Skew and term structure describe how implied volatility varies across strikes and expirations

## Where it appears in our code:

Implied volatility estimation logic is implemented in `src_web3/phase42/options_api.ts`.
The API includes a simplified inverse pricing function that estimates implied volatility from a given premium, strike, and time to expiration.
This allows users to see how premium changes map to volatility expectations without running complex numerical solvers.

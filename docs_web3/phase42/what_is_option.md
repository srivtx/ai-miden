# What Is an Option

## Why It Exists

Financial markets are uncertain. A farmer planting corn in spring does not know what the price will be at harvest. A technology startup holding Ethereum treasury funds does not know if the price will crash before their next funding round. Buying or selling the asset outright locks in full exposure, which may be too risky or too capital intensive. An option exists to solve this asymmetry by giving the holder the right, but not the obligation, to buy or sell an asset at a predetermined price before a specific date. This transforms uncertainty into a quantifiable insurance premium, allowing participants to cap their downside or speculate with strictly limited risk.

## Definition

An option is a derivative contract that grants the buyer the right to buy or sell an underlying asset at a fixed strike price before or on an expiration date. The buyer pays a premium upfront for this right. A call option gives the right to buy. A put option gives the right to sell. The seller, or writer, of the option receives the premium and assumes the obligation to fulfill the contract if the buyer chooses to exercise.

## Real-Life Analogy

Imagine you are interested in buying a house currently listed at $500,000, but you are waiting for your mortgage approval which will take three months. You worry that another buyer will push the price to $550,000 before you are ready. You pay the current owner $5,000 for a signed agreement that says you may buy the house for $500,000 anytime in the next three months. If prices rise, you exercise the agreement and save $45,000 net of the premium. If prices fall to $450,000, you tear up the agreement and buy a cheaper house, losing only the $5,000 premium. The agreement is the option. The $5,000 is the premium. The $500,000 is the strike price. The three months is the expiration.

## Tiny Numeric Example

A trader buys a call option on ETH with the following terms:

| Field | Value |
|-------|-------|
| Underlying | ETH |
| Strike Price | $2,000 |
| Premium | $100 per ETH |
| Contract Size | 1 ETH |
| Expiration | 30 days |

At expiration, ETH trades at $2,200. The trader exercises the call, buying ETH for $2,000 and immediately selling at market for $2,200. Gross profit is $200. Net profit after the $100 premium is $100. If ETH finishes at $1,900, the trader lets the option expire worthless. The loss is capped at the $100 premium paid. The seller who wrote the call keeps the $100 premium in the down scenario but must deliver ETH at $2,000 in the up scenario, losing $200 gross and $100 net.

## Common Confusion

- An option is not the same as owning the asset.
  It is a contract about the asset that may expire worthless.
- Buying an option does not require buying the asset eventually.
  You can let it expire if the market moves against you.
- The premium is not a refundable deposit.
  It is the cost of the right, paid to the writer regardless of outcome.
- Options are not always profitable just because the asset moves in your direction.
  The move must exceed the strike plus the premium paid for a call to be net profitable.
- Selling an option is not free income.
  The seller accepts potentially unlimited risk for a fixed premium.
- European and American options are not geographic terms.
  European options can only be exercised at expiration, while American options can be exercised anytime before.
- Decentralized options protocols do not eliminate counterparty risk entirely.
  The smart contract itself becomes the counterparty, and bugs can cause settlement failures.
- Implied volatility is not historical volatility.
  It is the market's forward-looking expectation derived from current option prices.

## Key Properties

- Asymmetric payoff where the buyer's loss is capped at the premium
- Strike price that defines the transaction level if exercised
- Expiration date that bounds the window of exercisability
- Premium that reflects time value, intrinsic value, and implied volatility
- Obligation asymmetry: the writer must perform if assigned, while the buyer chooses

## Where It Appears in Our Code

Options logic is implemented in `src_web3/phase42/options_api.ts`.
The API exposes endpoints to create option contracts, calculate premiums based on strike and time to expiration, and simulate exercise at maturity.
It tracks the distinction between calls and puts and computes payoff diagrams for educational visualization.

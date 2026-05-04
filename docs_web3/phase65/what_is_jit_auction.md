# What Is a JIT Auction?

## The Problem

Traditional liquidations force the protocol to accept whatever price the on-chain oracle offers at the exact moment of liquidation. If a large position is dumped onto the market instantly, slippage is severe, the liquidated user receives almost nothing, and the protocol may absorb bad debt. There is no mechanism to let external liquidity providers compete to take over the position at a better price.

## Definition

A Just-in-Time (JIT) auction is a sub-second, on-chain competitive bidding process that activates when a liquidation is triggered. Instead of immediately seizing and dumping a position, the protocol invites third-party liquidators to bid on the right to take over the underwater account's positions. The winning bidder assumes the positions at the best price, reducing slippage and improving recoverable collateral for the liquidated user.

## How It Works

1. **Monitor positions.** A keeper detects an underwater account just like in a standard liquidation.
2. **Detect underwater.** The margin ratio falls below maintenance, triggering the liquidation eligibility flag.
3. **Calculate reward.** The protocol calculates the liquidation notional and defines an auction starting price, usually at a slight discount to the oracle price to incentivize bidding.
4. **Submit liquidation.** The keeper does not immediately seize the position. Instead, they initiate a `BeginLiquidation` instruction that opens a 5-10 slot JIT auction window.
5. **Collect fee.** Bidders submit competing `PlaceLiquidationBid` transactions with varying discounts. The highest bid (smallest discount) wins. The winner assumes the positions, the protocol clears the bad debt, and the original user retains more residual collateral than in an instant seizure.
6. **Repeat.** The cycle continues for every liquidation, with auctions ensuring continuous price discovery even in volatile markets.

## Real-life Analogy

Imagine a bank foreclosing on a house. Instead of immediately selling it to the first investor at a rock-bottom price, the bank holds a 30-second auction on the courthouse steps. Multiple investors shout bids. The highest bid wins, the bank recovers more money, and the homeowner keeps more equity. The auction happens just in time, only when foreclosure is actually triggered.

## Tiny Numeric Example

Bob has a $200,000 BTC-PERP short that has gone underwater. The oracle marks BTC at $60,000.

- Instant seizure discount: 5% below oracle = $57,000 per BTC
- Liquidation notional: $200,000
- Instant recovery: $200,000 * 0.95 = $190,000 (bad debt of $10,000)

JIT auction opens for 8 slots (~3.2 seconds):

- Bidder A offers 2.5% discount
- Bidder B offers 1.8% discount
- Bidder C offers 1.5% discount (wins)

Winning price: $60,000 * 0.985 = $59,100 per BTC

- Recovery: $200,000 * 0.985 = $197,000
- Bad debt reduced to $3,000
- Bob retains $7,000 more collateral than instant seizure
- Winning bidder gets a $200,000 position at a 1.5% discount

## Common Confusion

- Is a JIT auction the same as a Dutch auction?
  - No. A Dutch auction price descends over time. A JIT auction accepts competing bids within a fixed short window and awards to the best bid.

- Can anyone participate in a JIT auction?
  - No. Only addresses with sufficient collateral and open-margin accounts in the Drift protocol can submit bids. Random wallets without accounts cannot bid.

- Does the JIT auction delay liquidation and increase risk?
  - No. The auction window is 5-10 slots (~2-4 seconds). The account is frozen during the auction, so risk does not accumulate.

- Is the JIT auction off-chain?
  - No. The entire auction logic executes inside the Drift on-chain program. Bids are on-chain transactions.

- Does the original user participate in the auction?
  - No. The user is passive. Their position is automatically transferred to the winning bidder once the auction resolves.

- Are JIT auctions used for all liquidations on Drift?
  - No. JIT auctions typically apply to large liquidations above a threshold notional. Small positions may still use instant liquidation to save gas.

## Key Properties

1. **On-chain price discovery.** Competition among bidders replaces a fixed oracle discount with a market-clearing price.
2. **Short duration.** Auctions resolve in seconds, preventing prolonged exposure to volatile prices.
3. **Frozen state.** The liquidated account is locked during the auction; no new trades or withdrawals can occur.
4. **Bidder collateral requirement.** Bidders must post collateral to prove they can absorb the position if they win.
5. **Reduced bad debt.** By extracting the best possible bid, the protocol and the liquidated user both retain more value than in an instant seizure.

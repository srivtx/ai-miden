# What is MEV?

## Why It Exists

Blockchains process transactions in blocks, and someone decides the order of transactions within each block.
That ordering power creates opportunities to extract value by strategically placing transactions.
This includes front-running a large trade, back-running a price update, or sandwiching a user's swap between a buy and a sell.
This extracted value is called Maximum Extractable Value, or MEV.
It represents the profit available to those who control transaction ordering.
MEV is a fundamental property of any system where transaction sequence matters.
Understanding MEV dynamics is crucial for designing fair and robust blockchain systems.
Developers who ignore MEV expose their users to predictable exploitation.

## Definition

MEV is the profit that block producers or specialized searchers can extract by including, excluding, or reordering transactions within a block.
This often happens at the expense of regular users.
MEV is a fundamental property of blockchains where transaction ordering matters.
It is not a bug but an inherent feature of sequenced execution.
Where there is ordering power, there is value to be extracted.
Understanding MEV is essential for anyone building or using blockchain applications.

## Real-Life Analogy

Imagine an auction where the auctioneer can see every bid before opening them.
If the auctioneer sees a bid for $1,000, they can slip in their own bid for $999 just before it, winning the item by one dollar.
Then they can immediately resell it to the original bidder for $1,000.
The auctioneer extracted $1 of value simply by controlling the order in which bids were processed.

MEV is that auctioneer's power, but on a blockchain where searchers and validators compete to reorder transactions for profit.
The auctioneer profits from information advantage.
In blockchain, the auctioneer is replaced by validators and specialized bots.
The victim is the regular user who just wanted to make a simple trade.
The auction is the mempool, and the bids are pending transactions.

## Tiny Numeric Example

A user submits a swap to buy 10,000 USDC worth of SOL.

| Transaction | Action | SOL Price Impact |
|---|---|---|
| Searcher Buy | Buy SOL before user | +$0.05 |
| User Swap | Buy 10,000 USDC of SOL | +$0.15 |
| Searcher Sell | Sell SOL after user | -$0.10 |
| Searcher Profit | | $500+ |

The searcher's sandwich attack inflates the price before the user buys and crashes it after, pocketing the difference.
The user receives worse execution because of the searcher's interference.
The searcher profits from the user's slippage without taking any market risk.
This is why slippage protection is essential for traders.
Without protection, everyday users unknowingly subsidize searcher profits on every trade.
MEV awareness is becoming a core skill for both developers and traders.

## Common Confusion

- **"Is MEV the same as arbitrage?"** Arbitrage is one form of MEV, but MEV also includes front-running, back-running, liquidations, and sandwich attacks.
- **"Does MEV only happen on Ethereum?"** No. MEV exists on any chain where transaction ordering is valuable. Solana has MEV but less than Ethereum due to faster block times.
- **"Is MEV always harmful?"** Not always. Arbitrage MEV improves price efficiency. Liquidation MEV keeps protocols healthy. Sandwich attacks and front-running harm users.
- **"Can users protect themselves from MEV?"** Yes. Private mempools, slippage tolerance settings, and MEV-protecting RPC endpoints reduce exposure.
- **"Who captures MEV?"** On Ethereum, validators and searchers. On Solana, Jito-enabled validators and searchers using bundles.
- **"What are MEV bundles?"** A bundle is an ordered set of transactions submitted together. If any transaction fails, the entire bundle is rejected, enabling atomic MEV strategies.
- **"Is MEV extraction illegal?"** Generally no, though specific jurisdictions may regulate certain forms of market manipulation.
- **"What is a searcher?"** A specialized bot operator that scans the mempool for MEV opportunities and submits bundles to validators.
- **"Can MEV be eliminated?"** Completely eliminating MEV is difficult because ordering value is inherent to blockchains. It can be minimized and redistributed.

## Key Properties

- **Ordering Power:** Derives value from the ability to sequence, include, or exclude transactions within a block.
- **Search Competition:** Specialized bots compete to find and execute profitable MEV opportunities in real time.
- **User Impact:** Can harm regular users through sandwich attacks and front-running while improving market efficiency via arbitrage.
- **Bundle Atomicity:** Groups transactions together so they either all succeed or all fail as a single unit.
- **Protection Strategies:** Includes private mempools, slippage limits, and MEV-aware RPCs to reduce user exposure.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase30/arbitrage_bot.ts` includes a simulated MEV analysis endpoint that estimates sandwich attack risks and optimal bundle positioning.

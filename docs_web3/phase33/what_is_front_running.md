# What Is Front Running

## Why It Exists

In public blockchains, transaction ordering is visible before confirmation, allowing sophisticated actors to see pending trades and place their own transactions ahead for profit. Front running exploits this transparency by jumping the queue to buy an asset before a large order executes and selling immediately after the price moves. Without protective mechanisms, ordinary users systematically receive worse prices every time they trade.

## Definition

Front running is the act of placing a transaction ahead of a known pending transaction to exploit the resulting price movement. On-chain, this is typically done by bots monitoring the mempool and paying higher gas fees or using validator relationships to secure earlier block placement.

## Real-Life Analogy

Imagine standing in line at a ticket booth when someone overhears you ask for fifty front-row seats. They sprint to a second window, buy all available front-row seats, then immediately offer to sell them to you at double the price. They had no intention of attending the show; they simply used the public information of your large order to extract value from your transaction.

## Tiny Numeric Example

A user submits a swap to buy 10,000 TOKEN_A for USDC:

| Order | Buyer | Amount | Price Before | Price After | Profit Extracted |
|-------|-------|--------|--------------|-------------|------------------|
| Front runner | Bot | 0 TOKEN_A | $1.00 | $1.05 | Buys first |
| Victim | User | 10,000 TOKEN_A | $1.05 | $1.10 | Pays extra $500 |
| Back runner | Bot | 0 TOKEN_A | $1.10 | $1.05 | Sells first |

The front runner buys at $1.00, the victim buys at $1.05, and the back runner sells at $1.10, extracting value from both sides.

## Common Confusion

- Front running is not the same as normal arbitrage; arbitrage balances prices across venues, while front running exploits a specific known order.
- Higher gas fees are not the only method; private validator relationships and side channels also enable ordering manipulation.
- Front running is not illegal everywhere; in decentralized finance, it often falls outside traditional securities regulations.
- Not all fast transactions are front running; a legitimate arbitrageur may independently spot the same opportunity.
- Front running does not require reading the victim's mind; bots parse pending transactions algorithmically.
- Privacy alone does not stop front running; encryption of transactions must be paired with fair ordering mechanisms.
- Front running is not unique to Ethereum; any blockchain with visible pending transactions is vulnerable.

## Key Properties
## Where It Appears in Our Code

Front running mitigation logic is implemented in `src_web3/phase33/protected_swap/src/lib.rs`, where the program enforces maximum slippage and deadline constraints to limit the profit extractable by front runners.

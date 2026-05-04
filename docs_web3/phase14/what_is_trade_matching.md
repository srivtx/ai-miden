Why it exists
-------------
In a marketplace with many buyers and sellers, individual negotiation is too
slow and expensive. The problem is that without an automated matching engine,
trades happen manually, leading to delays, failed transactions, and poor price
discovery. Trade Matching is the algorithmic process of pairing compatible buy
and sell orders based on price, quantity, and eligibility rules. On-chain trade
matching ensures that the rules are transparent and enforced by code.

Definition
----------
Trade Matching is the process of comparing and pairing buy and sell orders
according to predefined rules such as price equality or better, sufficient
quantity, and valid expiration, resulting in an executed trade.

Real-life analogy
-----------------
Imagine a farmers market where buyers carry signs listing what they want and
sellers display their produce. A market manager walks around with a clipboard.
When a buyer willing to pay three dollars per pound meets a seller asking three
dollars per pound for tomatoes, the manager pairs them, records the deal, and
collects a small fee. The manager does not set prices; they only match existing
intentions. On-chain trade matching is that clipboard. The program reads orders
from an orderbook, finds compatible pairs, and executes the exchange.

Tiny numeric example
--------------------
An on-chain orderbook has four open orders:
- Buy: Alice wants 100 tokens at $5 each
- Buy: Bob wants 50 tokens at $4.50 each
- Sell: Carol offers 80 tokens at $5 each
- Sell: Dave offers 30 tokens at $5.50 each
The matching engine evaluates:
1. Alice ($5 buy) matches Carol ($5 sell). Quantity: min(100, 80) = 80.
   Result: Alice gets 80 tokens, Carol gets $400. Alice still wants 20.
2. Remaining Alice ($5 buy) does not match Dave ($5.50 sell) because $5 < $5.50.
3. Bob ($4.50 buy) does not match any sell because $4.50 is below all ask prices.
The engine executes one matched trade and leaves three orders on the book.

Common confusion
----------------
- Trade matching is not market making. Market makers actively provide liquidity
  by placing orders. Matching engines passively pair existing orders.
- On-chain matching does not guarantee the best price globally. It guarantees
  the best price available on that specific orderbook at that moment.
- A matching engine can process partial fills. An order does not need to match
  in its entirety. The remaining quantity stays open on the book.
- Matching can be first-in-first-out or pro-rata depending on the program design.
  There is no universal standard for on-chain matching priority.
- Trade matching does not hold funds in escrow by default. The matching engine
  may trigger an escrow or atomic swap as the settlement mechanism.
- Off-chain matching with on-chain settlement is common for speed. Orders are
  matched off-chain and batched for settlement to reduce transaction costs.
- Matching engines do not create tokens or money. They only move existing
  balances between accounts according to the matched terms.

Where it appears in our code
----------------------------
`src_web3/phase14/escrow/src/lib.rs` — implements a simple two-party order
matching system that pairs deposits and releases funds when both sides match.

Trade matching on Solana
------------------------
Solana's high throughput and low latency make it suitable for on-chain order
books, but most popular DEXs use automated market makers instead of traditional
matching engines. AMMs replace the matching engine with a pricing curve and
liquidity pools. However, order book DEXs still exist and rely on on-chain
or hybrid matching. Hybrid models match orders off-chain for speed and settle
only the final trades on-chain. When building a matching system, consider
whether you need the transparency of full on-chain matching or the efficiency
of hybrid settlement.

Practical Trade Matching checklist
----------------------------------
- Define matching priority rules explicitly (price, time, size).
- Handle partial fills carefully to avoid double spending.
- Validate order signatures to prevent spoofing.
- Consider batching settlements to reduce per-trade costs.
- Monitor for manipulative behavior such as wash trading.
- Ensure fair ordering to prevent front-running by validators or bots.

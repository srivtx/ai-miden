## What Is an Automated Market Maker?

**The Problem:**
Traditional finance relies on order books where buyers place bids and
sellers place asks. A trade only happens when two parties agree on the
exact same price. This creates three major failures in decentralized
systems.

First, illiquid assets can go hours without a single trade because no
counterparty exists at the same time. Second, professional market makers
must be paid enormous fees to sit between buyers and sellers, making
small markets unprofitable.

Third, new projects cannot afford the infrastructure to bootstrap
trading. In a world of thousands of tokens, waiting for human agreement
on every trade is impossibly slow and expensive. There must be a way to
trade continuously without finding a specific person who wants the
opposite trade at the exact same moment.

**Definition:**
An Automated Market Maker is a decentralized exchange protocol that
replaces the order book with a mathematical pricing curve.

Instead of matching a buyer with a seller, the AMM holds reserves of
two tokens inside a smart contract and automatically calculates the
exchange rate based on the current ratio between them. A trader always
trades against the pool itself, meaning there is always a price
available and no need for a human counterparty.

The pool is both buyer and seller simultaneously, and the price adjusts
after every single trade to reflect the new balance of assets. This
creates a permissionless market where any token can be traded as long
as someone is willing to fund the initial liquidity.

**Real-life analogy:**
Imagine a magical vending machine that sells both apples and oranges.
The machine does not have a cashier or a price tag. Instead, it
contains a fixed rule written into its hardware: the product of the
number of apples and oranges inside must always equal exactly one
thousand.

When you deposit apples, the machine instantly recalculates how many
oranges you receive to keep that product constant. If the machine is
full of apples but low on oranges, it will demand many apples for each
orange. If the machine is balanced, the exchange is fair.

The machine never closes, never needs a human operator, and never
truly runs out of stock because the pricing rule adjusts automatically
to protect the inventory. This is exactly how an AMM works: the pool
is the vending machine, the tokens are the fruit, and the constant
product formula is the immutable rule written into the smart contract
code.

Now imagine that everyone in the neighborhood can also add apples and
oranges to the machine. When they do, they receive special tickets
representing their share of the total inventory. These ticket holders
earn a tiny fee every time someone swaps fruit.

This mirrors liquidity providers in an AMM who deposit paired tokens
and receive LP tokens in return. The system is entirely
self-sustaining: traders get instant liquidity, providers earn fees,
and no central authority is required.

**Tiny numeric example:**
Consider a pool with 1,000 SOL and 10,000 USDC.
The constant product k equals 10,000,000.
This number never changes during a pure swap.

| Trade Size (SOL In) | SOL Reserve After | USDC Reserve After | USDC Received | Effective Price | Slippage |
|---------------------|-------------------|--------------------|---------------|-----------------|----------|
| 0                   | 1,000             | 10,000             | 0             | 10.00           | 0%       |
| 10                  | 1,010             | 9,900.99           | 99.01         | 9.90            | 1.0%     |
| 50                  | 1,050             | 9,523.81           | 476.19        | 9.52            | 4.8%     |
| 100                 | 1,100             | 9,090.91           | 909.09        | 9.09            | 9.1%     |
| 200                 | 1,200             | 8,333.33           | 1,666.67      | 8.33            | 16.7%    |

A trader who swaps 200 SOL receives only 1,666.67 USDC,
a slippage cost of 333.33 USDC. This non-linear penalty protects
the pool from being drained by a single massive trade.

**Common confusion:**
- **"The AMM chooses the price arbitrarily."**
  No. The price emerges from reserves and the mathematical formula.
  The AMM has no opinion about value. It simply enforces the curve.
  If traders believe the price is wrong, arbitrage aligns it.
  The AMM is a passive rule follower, not an active price setter.

- **"AMMs eliminate price volatility."**
  No. Prices in AMM pools can swing wildly, especially in low-liquidity
  pools. Deep liquidity helps, but the price follows the market rather
  than suppressing it. AMMs reflect volatility instantly.

- **"The protocol steals value during a trade."**
  No. Every token deposited stays inside the pool.
  Trading fees go to liquidity providers. The protocol does not pocket
  slippage. Slippage is a market impact cost, not a fee.

- **"All AMMs use the same formula."**
  No. While x times y equals k is the most common design, other
  formulas exist. Curve uses stableswap curves. Balancer supports
  multi-token weighted pools. Uniswap v3 uses concentrated liquidity.

- **"Liquidity providers always earn more than they lose."**
  No. When prices move significantly, providers suffer impermanent
  loss. This can exceed trading fees, especially during strong trends.
  Providers must select pools carefully and monitor positions.

- **"Slippage is an extra fee I pay to validators."**
  No. Slippage is the price impact caused by your own trade changing
  the pool ratio. It is not sent to anyone. Validators receive
  transaction fees, which are separate and usually much smaller.

- **"AMMs will make centralized exchanges obsolete."**
  No. Centralized exchanges still dominate high-frequency trading
  and fiat onramps. AMMs excel at permissionless long-tail assets,
  but both models will likely coexist.

**Where it appears in our code:**
`src_web3/phase16/amm/src/lib.rs` — Solana on-chain AMM program.
`src_web3/phase16/amm_api.ts` — Express API for pool creation and swaps.

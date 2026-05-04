## What Is an LP Token?

**The Problem:**
When many different people deposit funds into a single shared liquidity
pool, the smart contract needs a reliable way to track exactly how much
of the pool each person owns.

Without a bookkeeping mechanism, the contract would have no way to know
how much to return when someone wants to withdraw their share.
A simple list of deposits would fail because the value of the pool
changes constantly due to trading fees, price swings, and additional
deposits.

There must be a fungible, transferable receipt that represents a
proportional claim on the pool's current reserves.

**Definition:**
An LP token is a receipt token minted by a liquidity pool to represent
a provider's proportional ownership of the pool's total deposits.
When a user adds liquidity, they receive LP tokens.
When they want to exit, they burn their LP tokens and receive their
share of the current reserves.

LP tokens are fungible, meaning any single LP token is interchangeable
with another, and they can sometimes be used in other protocols as
collateral or for additional yield farming.

**Real-life analogy:**
Imagine you deposit a winter coat at a cloakroom during a concert.
The attendant does not give you back your exact coat immediately.
Instead, they hand you a numbered ticket.

That ticket has no intrinsic value to anyone else, but it serves as
proof that you deposited a coat and entitles you to retrieve one coat
of equivalent value later.

If the cloakroom suddenly becomes more valuable because the venue
starts charging a small fee to everyone who checks a coat, your ticket
entitles you to a share of that fee when you cash out.

LP tokens work the same way: they are not the underlying assets, but
they are the key that unlocks your proportional share of whatever is
in the pool when you decide to leave.

**Tiny numeric example:**
A pool starts with 1000 ETH and 2,000,000 USDC.
The initial LP token supply is 1,000.

| Event | ETH Reserve | USDC Reserve | LP Supply | ETH per LP | USDC per LP |
|-------|-------------|--------------|-----------|------------|-------------|
| Start | 1,000       | 2,000,000    | 1,000     | 1.00       | 2,000.00    |
| Alice adds 10% | 1,100 | 2,200,000 | 1,100 | 1.00 | 2,000.00 |
| Fees earned | 1,100 | 2,200,330 | 1,100 | 1.00 | 2,000.30 |
| Bob redeems 100 LP | 1,000 | 2,000,300 | 1,000 | 1.00 | 2,000.30 |

Alice deposits ten percent of the pool and receives one hundred LP
tokens. After fees accrue, each LP token is redeemable for slightly
more USDC than before. Bob redeems one hundred LP tokens and receives
his proportional share of the larger pool.

**Common confusion:**
- **"LP tokens are a separate cryptocurrency with independent value."**
  No. Their value is entirely derived from the underlying pool reserves.
  An LP token for an empty pool is worthless.
  It is a claim on assets, not an asset itself.

- **"Holding LP tokens guarantees profit."**
  No. If the pool suffers impermanent loss or is exploited, the
  underlying value of each LP token can drop below the value of the
  original deposit. LP tokens track the pool's health, not your
  principal.

- **"LP tokens are locked forever once minted."**
  No. Most LP tokens can be burned at any time to withdraw the
  proportional reserves. Some protocols impose lockups or penalties,
  but the token itself represents a redeemable claim.

- **"You receive the same number of tokens you deposited when you withdraw."**
  No. You receive your share of the current reserves.
  If the pool has rebalanced due to trades, you may withdraw a
  different ratio of tokens than you originally deposited.

- **"LP tokens are only used in decentralized exchanges."**
  No. LP tokens have become a primitive in DeFi.
  They can be staked in yield farms, used as collateral in lending
  protocols, or bundled into more complex financial products.

- **"The number of LP tokens you receive equals the dollar value you deposited."**
  No. The number of LP tokens depends on the pool's existing liquidity
  and the pricing formula. You might deposit one thousand dollars and
  receive ten LP tokens, or you might receive one million, depending
  on how the pool was initialized.

- **"LP tokens pay interest automatically to your wallet."**
  No. LP tokens do not automatically airdrop fees.
  The fees are retained inside the pool, increasing the value of each
  LP token. You realize the gains when you burn the LP tokens and
  withdraw the enlarged reserves.

**Where it appears in our code:**
`src_web3/phase17/liquidity_pool/src/lib.rs` — Solana program that mints
LP tokens on deposit and burns them on withdrawal to track ownership.

`src_web3/phase17/liquidity_api.ts` — Express API that calculates LP
token amounts, tracks provider balances, and handles redemption math.

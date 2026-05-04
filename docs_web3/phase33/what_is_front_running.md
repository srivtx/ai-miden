# What Is Front Running

**The Problem:**

On public blockchains, every pending transaction sits in a visible mempool before confirmation. Sophisticated bots monitor these pending transactions to identify large trades that will move prices. Without protection, a bot can place its own transaction ahead of the victim's trade, force the price to move unfavorably, and extract profit at the victim's expense. Ordinary users systematically receive worse prices than the market would otherwise provide.

**Definition:**

Front running is the act of submitting a transaction ahead of a known pending transaction to exploit the resulting price movement. On-chain, bots achieve this by paying higher priority fees or using direct validator relationships to secure earlier block placement.

**How It Works (Step-by-Step):**

1. **Surveillance:** A bot monitors the public mempool for a pending large swap that will materially move the price of an asset.
2. **Front-run placement:** The bot submits a buy transaction for the same asset with a higher priority fee, ensuring it is ordered before the victim's transaction.
3. **Price impact:** The bot's purchase pushes the asset price up inside the automated market maker.
4. **Victim execution:** The victim's swap executes at the new, inflated price, receiving fewer tokens than expected at the original market rate.
5. **Back-run placement:** The bot immediately sells the same tokens in a second transaction placed after the victim's swap.
6. **Profit realization:** The sale occurs at the elevated price created by the victim's own trade. The bot pockets the difference between the buy and sell prices.

**Real-life analogy:**

You are at a farmer's market and tell a vendor you will buy fifty baskets of strawberries at the listed price. A reseller standing nearby hears this, rushes to the same vendor, and buys fifty baskets first. The vendor's remaining supply is now low, so the price rises. You still complete your purchase, but at the higher price. The reseller then sells their fifty baskets to another buyer at that elevated price, profiting from the price movement your large order caused.

**Tiny numeric example:**

Consider a constant-product AMM pool with 10,000 TOKEN_A and 10,000 USDC. The constant k = 100,000,000. A victim submits a transaction to buy 1,000 TOKEN_A.

| Step | Actor | Action | TOKEN_A in Pool | USDC in Pool | Price (USDC per TOKEN_A) | USDC Paid |
|------|-------|--------|-----------------|--------------|--------------------------|-----------|
| 0 | Market | Initial state | 10,000 | 10,000 | 1.00 | - |
| 1 | Bot | Buy 500 TOKEN_A | 9,500 | 10,526.32 | 1.108 | 526.32 |
| 2 | Victim | Buy 1,000 TOKEN_A | 8,500 | 11,764.71 | 1.384 | 1,238.39 |
| 3 | Bot | Sell 500 TOKEN_A | 9,000 | 11,111.11 | 1.235 | Receives 653.60 |

Exact math:
- Step 1: Bot pays 100,000,000 / (10,000 - 500) - 10,000 = 526.32 USDC.
- Step 2: Victim pays 100,000,000 / (9,500 - 1,000) - 10,526.32 = 1,238.39 USDC.
- Step 3: Bot receives 11,764.71 - 100,000,000 / (8,500 + 500) = 653.60 USDC.

Bot profit: 653.60 - 526.32 = 127.28 USDC.
Victim extra cost: 1,238.39 - (100,000,000 / 9,000 - 10,000) = 1,238.39 - 1,111.11 = 127.28 USDC.

**Common confusion:**

- Front running is not the same as arbitrage. Arbitrage balances prices across venues; front running exploits a specific known order. No.
- Higher gas fees are not the only method. Private validator relationships and side channels also enable ordering manipulation. No.
- Front running is not illegal in all jurisdictions. In decentralized finance, it often falls outside traditional securities regulations. No.
- Not all fast transactions are front running. A legitimate arbitrageur may independently spot the same opportunity without seeing the victim's transaction. No.
- Front running does not require reading the victim's mind. Bots parse pending transactions algorithmically from the mempool. No.
- Privacy alone does not stop front running. Encryption must be paired with fair ordering or threshold decryption mechanisms. No.

**Key properties:**

- Profit is extracted directly from the victim's slippage tolerance.
- It requires only public mempool visibility, not privileged access.
- The attack completes within a single block, often in adjacent transaction slots.
- Protection mechanisms include slippage limits, deadline constraints, and private mempools.

**Where it appears in our code:**

Front running mitigation logic is implemented in `src_web3/phase33/protected_swap/src/lib.rs`, where the program enforces maximum slippage and deadline constraints to limit the profit extractable by front runners.

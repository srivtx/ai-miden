## Phase 17 Summary: Liquidity Pool

### Key Takeaways

1. **Liquidity pools are shared smart contract treasuries.** They hold paired tokens and act as the automatic counterparty for every trade.
2. **LP tokens are proportional receipts.** They track ownership, earn fees, and can be redeemed for the current reserve mix.
3. **Impermanent loss is the cost of rebalancing.** When prices diverge, the pool accumulates the losing asset, creating an opportunity cost versus holding.
4. **Fees must exceed IL for profitability.** A provider only profits if trading volume generates more fees than the impermanent loss.
5. **Permissionless deposits mean anyone can bootstrap a market.** No exchange approval is required to create or join a pool.

### What We Built

- A Solana program that accepts paired token deposits, mints LP tokens, and allows proportional withdrawals.
- A TypeScript Express API that simulates adding and removing liquidity with real-time ownership tracking.
- An impermanent loss calculator that shows the opportunity cost of providing liquidity versus holding.
- LP token accounting that updates shares fairly on every deposit and withdrawal.

### Files

| File | Purpose |
|---|---|
| `docs_web3/phase17/what_is_liquidity_pool.md` | Liquidity pool concepts and mechanics |
| `docs_web3/phase17/what_is_lp_token.md` | LP token ownership and redemption |
| `docs_web3/phase17/what_is_impermanent_loss.md` | Impermanent loss math and mitigation |
| `src_web3/phase17/liquidity_pool/src/lib.rs` | On-chain liquidity pool program |
| `src_web3/phase17/liquidity_api.ts` | Express API for liquidity operations |

### Dependencies

```toml
[dependencies]
solana-program = "1.16"
borsh = "0.10"
```

### Next Step

Phase 18: **Staking Program** — Learn how users lock tokens to earn rewards, how reward pools are funded, and how APY is calculated.

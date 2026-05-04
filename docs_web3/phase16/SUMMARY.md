## Phase 16 Summary: AMM

### Key Takeaways

1. **AMMs replace order books with math.** Instead of matching buyers and sellers, pools price assets automatically using the constant product formula.
2. **x times y equals k is the core rule.** The product of the two reserves stays fixed during swaps, creating a hyperbolic pricing curve.
3. **Slippage is the cost of your own trade size.** Large trades move the pool ratio against you, resulting in worse prices than the spot rate.
4. **Liquidity providers earn fees but face impermanent loss.** Fees reward depositors, but price divergence can cost more than fees earn.
5. **Permissionless trading means anyone can create a market.** No approval, no listing fee, and no centralized gatekeeper.

### What We Built

- A Solana program that initializes a two-token pool and enforces the constant product formula on-chain.
- A TypeScript Express API that simulates pool creation, liquidity addition, and token swaps.
- Price impact calculations that show slippage before execution.
- A health endpoint to monitor running pools.

### Files

| File | Purpose |
|---|---|
| `docs_web3/phase16/what_is_amm.md` | Automated Market Maker concepts |
| `docs_web3/phase16/what_is_constant_product.md` | x*y=k formula explained |
| `docs_web3/phase16/what_is_slippage.md` | Slippage mechanics and protection |
| `src_web3/phase16/amm/src/lib.rs` | On-chain AMM program |
| `src_web3/phase16/amm_api.ts` | Express API for pool operations |

### Dependencies

```toml
[dependencies]
solana-program = "1.16"
borsh = "0.10"
```

### Next Step

Phase 17: **Liquidity Pool** — Learn how LP tokens track ownership, how liquidity is added and removed, and why impermanent loss occurs.

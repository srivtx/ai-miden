## Phase 18 Summary: Staking Program

### Key Takeaways

1. **Staking locks tokens to earn rewards.** It aligns user incentives with protocol growth and network security.
2. **Reward pools are finite treasuries.** They must be funded by emissions, fees, or allocations, and they deplete over time.
3. **APY includes compounding.** It is always equal to or greater than APR for the same base rate.
4. **Early stakers often earn higher yields.** As more capital enters the pool, the same reward budget is shared among more participants.
5. **Staking is not risk-free.** Smart contract bugs, price drops, and changing emission schedules can all reduce real returns.

### What We Built

- A Solana program that initializes a staking pool, accepts token deposits, tracks stake duration, and calculates rewards algorithmically.
- A TypeScript Express API that simulates pool creation, staking, unstaking, reward claiming, and real-time APY estimation.
- Reward rate adjustment logic that reflects dilution as more users join the pool.

### Files

| File | Purpose |
|---|---|
| `docs_web3/phase18/what_is_staking.md` | Staking concepts and lockup mechanics |
| `docs_web3/phase18/what_is_reward_pool.md` | Reward pool funding and distribution |
| `docs_web3/phase18/what_is_apy.md` | APY versus APR and compounding math |
| `src_web3/phase18/staking/src/lib.rs` | On-chain staking program |
| `src_web3/phase18/staking_api.ts` | Express API for stake operations |

### Dependencies

```toml
[dependencies]
solana-program = "1.16"
borsh = "0.10"
```

### Next Step

Phase 19: **Lending Protocol** — Learn how collateralized loans work, how health factors prevent insolvency, and how liquidation protects lenders.

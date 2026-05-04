## Phase 19 Summary: Lending Protocol

### Key Takeaways

1. **Lending protocols connect depositors and borrowers without banks.** All terms are enforced by smart contracts.
2. **Loans are overcollateralized.** Borrowers must deposit more than they borrow because there are no credit checks.
3. **Collateral value is monitored in real time.** Price oracles constantly update asset values to detect unsafe positions.
4. **Health factor is the safety gauge.** Below one, liquidation is triggered automatically to protect lenders.
5. **Liquidation is permissionless.** Anyone can repay a bad debt and seize collateral at a discount.

### What We Built

- A Solana program that accepts collateral, tracks debt, calculates health factors, and executes liquidations.
- A TypeScript Express API that simulates lending markets with dynamic interest rates and collateral ratios.
- Health factor monitoring that warns borrowers before liquidation occurs.
- Liquidation simulation showing how liquidators profit while protecting protocol solvency.

### Files

| File | Purpose |
|---|---|
| `docs_web3/phase19/what_is_lending.md` | Lending protocol concepts and mechanics |
| `docs_web3/phase19/what_is_collateral.md` | Collateral deposits and loan security |
| `docs_web3/phase19/what_is_liquidation.md` | Liquidation process and incentives |
| `docs_web3/phase19/what_is_health_factor.md` | Health factor math and risk monitoring |
| `src_web3/phase19/lending/src/lib.rs` | On-chain lending program |
| `src_web3/phase19/lending_api.ts` | Express API for borrow/lend/liquidate |

### Dependencies

```toml
[dependencies]
solana-program = "1.16"
borsh = "0.10"
```

### Next Step

Phase 20: **Time-Locked Vault** — Learn how time locks protect large transfers, how the Clock sysvar provides trustless time, and how vesting schedules release tokens gradually.

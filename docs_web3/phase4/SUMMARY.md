# Phase 4 Summary: Accounts Model

## Key Takeaways

- Solana separates programs (immutable code) from data accounts (mutable state), enabling parallel execution and clear ownership.
- Program accounts contain executable bytecode and are owned by the BPF loader; they never hold user state.
- Data accounts store mutable state and are owned by a program; only that program can modify them.
- Rent economics ensure that storage has a real cost; rent-exempt accounts persist forever once funded above the threshold.
- The runtime enforces all these boundaries automatically, preventing unauthorized writes and data corruption.

## What Was Built

| File | Purpose |
|------|---------|
| `docs_web3/phase4/what_is_accounts_model.md` | Overview of program-state separation and parallel scheduling benefits |
| `docs_web3/phase4/what_is_program_account.md` | Executable accounts, deployment, and immutability guarantees |
| `docs_web3/phase4/what_is_data_account.md` | Mutable state containers, ownership, and initialization patterns |
| `docs_web3/phase4/what_is_rent.md` | Storage economics, rent-exempt thresholds, and account lifecycle |
| `src_web3/phase4/account_model_demo.rs` | Rust simulation of runtime with ownership enforcement and rent calculation |

## Connections to Other Phases

- Phase 3's parallel execution depends on the accounts model to identify non-overlapping state accesses.
- Phase 2's keypairs become the addresses that own accounts and authorize state mutations.
- Phase 1's blockchain stores the account state transitions in each block.
- Phase 5 will set up the tools to create real accounts on devnet and calculate actual rent.

## Next Step

Proceed to Phase 5 to install the Solana CLI, Rust toolchain, and verify your development environment.

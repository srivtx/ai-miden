# What Is the Accounts Model?

## Why It Exists

Traditional blockchains like Ethereum combine code and state into a single object called a contract, forcing every node to re-execute all code to verify state transitions and creating state bloat that is hard to prune.
The accounts model exists to separate programs from data, allowing the network to store state in discrete accounts that programs read and write, enabling parallel execution and cheaper state rent.
Without this separation, every validator must replicate massive state objects just to verify small changes.
The accounts model makes state explicitly addressable and manageable.

## Definition

The accounts model is a state architecture where every piece of data on the blockchain lives in an account identified by a public key, and programs are stateless executables that operate on accounts passed to them by transactions.
This separation makes state explicitly addressable and allows the runtime to schedule non-overlapping account accesses in parallel.
Programs do not contain state; they contain logic that transforms state in accounts.
This design is fundamental to Solana's performance advantages.

## Real-Life Analogy

Imagine a restaurant kitchen where the recipes are printed on paper and stored in a central binder, while the ingredients are kept in individually labeled refrigerators with clear ownership tags.
Any chef can grab a recipe and open the specific refrigerators needed for that dish.
If two chefs need different refrigerators, they cook simultaneously without interfering.
If they both need the same refrigerator, they take turns according to a schedule.
The recipes never contain ingredients, and the ingredients never contain recipes.
Solana's accounts model works the same way: programs are recipes, accounts are refrigerators, and the runtime is the head chef scheduling access.
This separation means you can update a recipe without touching the ingredients, and you can refill a refrigerator without rewriting the recipe book.
The kitchen operates more efficiently because the workflow is clearly separated.

## Tiny Numeric Example

State access parallelism with 100 transactions:

| Model | Accounts Touched | Parallel Groups | Effective TPS | State Overhead |
|-------|-----------------|-----------------|---------------|----------------|
| Monolithic contract | 1 shared | 1 | 500 | High |
| Accounts model | 80 unique, 20 shared | 4 batches | 2,000 | Low |

By isolating state into discrete accounts, Solana executes 4x more transactions in the same time window.
Additionally, unused accounts can be closed to reclaim rent, while monolithic contracts accumulate state forever, leading to node bloat.
The accounts model turns state management from a liability into an economic activity.
Validators benefit from smaller state because they can fit more in memory.
This keeps the ledger size manageable over years of operation.
State rent creates a market mechanism that prunes inactive accounts automatically.
Active users pay minimal costs while the network remains lean and efficient.
The accounts model is a foundational innovation that distinguishes Solana from earlier blockchains.
Understanding it is essential for anyone building on Solana.

## Common Confusion

- Accounts are not user profiles; they are generic data containers that can hold lamports, code, or arbitrary state depending on their type.
  A single user may control dozens of accounts for different purposes.
- Programs do not store state internally; all persistent data lives in separate data accounts owned by the program.
  This separation is what makes programs small and cacheable.
- Every account has exactly one owner program that can modify its data, enforced by the runtime on every transaction.
  The runtime checks ownership before allowing any write.
- Accounts are not free; rent in lamports is required to keep them alive on-chain, incentivizing cleanup.
  Unused accounts can be closed to recover their deposit.
- The accounts model is not the same as Ethereum's account model; Solana separates code and state explicitly into different objects.
  Ethereum contracts contain both code and state in a single address.
- A transaction must declare all accounts it will touch so the runtime can verify ownership and schedule parallel execution.
  This declaration is part of every Solana transaction format.
- Account addresses are public keys, but not all public keys own accounts with data; some are just identifiers.
  An address can exist without an account until it is funded.

## Key Properties
## Where It Appears in Our Code

- `src_web3/phase4/account_model_demo.rs` — Simulates program-owned data accounts, runtime access checks, and rent economics.
- `docs_web3/phase4/SUMMARY.md` — Recaps how the accounts model enables parallel execution and clear ownership boundaries.
- `src_web3/phase3/proof_of_history_demo.rs` — Prior phase where parallel execution batches are scheduled based on account access patterns.
- `src_web3/phase4/account_model_demo.rs` — Core simulation demonstrating program-data separation and runtime enforcement.
- `docs_web3/phase4/what_is_program_account.md` — Explains the executable accounts that operate on data in this model.
- `docs_web3/phase4/what_is_data_account.md` — Explains the mutable state containers owned by programs.
- `src_web3/phase5/dev_environment_check.sh` — Verifies the toolchain needed to compile account-aware Solana programs.
- `docs_web3/phase4/what_is_rent.md` — Explains the storage economics that keep the accounts model sustainable.
- `src_web3/phase2/keypair_demo.rs` — Prior phase demonstrating the cryptographic identities that own accounts.
- `src_web3/phase5/dev_environment_check.sh` — Verifies the Rust toolchain needed to build account-aware programs.
- `docs_web3/phase4/SUMMARY.md` — Phase recap connecting accounts to parallel execution and rent.
- `src_web3/phase3/proof_of_history_demo.rs` — Prior phase where account accesses are analyzed for parallel scheduling.
- `docs_web3/phase4/what_is_accounts_model.md` — This document explaining the program-data separation architecture.
- `src_web3/phase5/dev_environment_check.sh` — Verifies that the development environment supports account-aware program compilation.
- `docs_web3/phase4/what_is_accounts_model.md` — This document explaining the program-data separation architecture.

# What Is Rent?

## Why It Exists

Blockchains with free storage attract spam, state bloat, and permanent growth that makes nodes expensive to run, leading to centralization as only wealthy entities can afford full validation.
Rent exists to align incentives by requiring account holders to pay for the storage they consume, ensuring that abandoned or useless accounts do not burden the network indefinitely.
Without rent, anyone could create unlimited accounts for free, eventually crashing every validator.
Rent converts storage from an externality into an economic good.

## Definition

Rent is a time-based fee paid in lamports for storing data on Solana; accounts that maintain a balance above the rent-exempt threshold are exempt from periodic rent charges and persist forever, while accounts below the threshold have their balances slowly drained until they are purged from the ledger.
This mechanism converts storage into an economic good with measurable cost.
Rent-exempt status is the default recommendation for all persistent accounts.
The rent rate is set by governance and has historically decreased over time.

## Real-Life Analogy

Imagine a storage locker facility where you can either pay a small monthly fee or pay a larger one-time deposit that covers your rent forever.
If you stop paying monthly, the facility gradually sells your belongings to cover costs and eventually empties the locker for a new tenant.
If you paid the forever deposit, the locker remains yours in perpetuity even if you never visit.
Solana works the same way: rent-exempt accounts are forever lockers, and below-threshold accounts face gradual liquidation.
The facility owner uses the fees to maintain security, lighting, and climate control, ensuring the entire complex remains operational.
Without these fees, the facility would decay and become unusable.

## Tiny Numeric Example

Rent costs at typical network rates:

| Data Size | Monthly Rent | Rent-Exempt Balance (2 years) | Annual Cost if Not Exempt |
|-----------|-------------|-------------------------------|---------------------------|
| 0 bytes | 0 SOL | 0.001 SOL | Negligible |
| 100 bytes | 0.0001 SOL | 0.002 SOL | 0.0012 SOL |
| 1 MB | 0.001 SOL | 0.02 SOL | 0.012 SOL |
| 10 MB | 0.01 SOL | 0.2 SOL | 0.12 SOL |

A token account of 165 bytes requires approximately 0.002 SOL as a rent-exempt deposit, making it effectively free to maintain once funded.
For a developer creating 10,000 token accounts, the total rent-exempt deposit is only 20 SOL, a trivial cost compared to the operational expense of maintaining equivalent database records on traditional servers.
The low cost encourages developers to create granular accounts rather than monolithic state blobs.
Validators benefit because smaller accounts are easier to cache and index.
The rent system also discourages spam by making account creation cost something.
Even a tiny cost is enough to prevent automated abuse at scale.

## Common Confusion

- Rent is not a transaction fee; it is a storage cost separate from compute costs and priority fees.
  Transaction fees pay for execution; rent pays for persistence.
- Rent exemption is the default best practice; most dApps fund accounts above the threshold immediately upon creation.
  Creating a below-threshold account is almost always a mistake.
- Rent does not burn lamports immediately; below-threshold accounts decay gradually over epochs through rent collection.
  The decay rate is slow enough that users have time to top up their balance.
- The rent rate can change; it is set by governance and historically has been reduced over time to lower barriers.
  Future reductions could make existing rent-exempt accounts even more secure.
- Native programs are rent-exempt by protocol rule, not by balance, because they are essential infrastructure.
  This ensures core functionality is never deleted.
- Rent exemption is calculated per-account, not per-wallet; each data account needs its own deposit to survive.
  A wallet with 100 SOL does not automatically exempt its associated token accounts.
- Closing an account refunds the rent-exempt balance to a designated recipient address, recovering the deposit.
- Rent collection happens once per epoch, not continuously.
- The rent rate is deterministic and can be queried on-chain before creating an account.
Developers can use the CLI to calculate exact rent requirements for any data size.
This predictability helps with budgeting and user communication.
Rent economics ensure that Solana remains scalable as adoption grows.
Every account holder contributes to network sustainability through this mechanism.
  This refund mechanism encourages cleanup of unused accounts.

## Key Properties
## Where It Appears in Our Code

- `src_web3/phase4/account_model_demo.rs` — Calculates rent-exempt thresholds and simulates account lifecycle economics with rent collection.
- `docs_web3/phase4/SUMMARY.md` — Explains rent economics and why rent-exempt accounts are the default best practice.
- `src_web3/phase5/dev_environment_check.sh` — Verifies that the Solana CLI can calculate rent for account creation on devnet.
- `src_web3/phase4/account_model_demo.rs` — Core simulation calculating rent-exempt thresholds for various data sizes.
- `docs_web3/phase4/what_is_accounts_model.md` — Overview of the architecture where rent economics play a critical role.
- `docs_web3/phase4/what_is_data_account.md` — Explains the mutable accounts whose existence depends on rent payment.
- `src_web3/phase5/dev_environment_check.sh` — Verifies the Solana CLI can query rent rates on devnet.
- `docs_web3/phase4/SUMMARY.md` — Phase recap connecting rent to the broader accounts model.
- `src_web3/phase3/proof_of_history_demo.rs` — Prior phase where rent payments are ordered alongside other transactions.
- `docs_web3/phase4/what_is_rent.md` — This document explaining storage economics and rent exemption.
- `src_web3/phase5/dev_environment_check.sh` — Verifies CLI tools for rent calculation and account funding.
- `docs_web3/phase4/what_is_rent.md` — This document explaining storage economics and rent exemption.

Why it exists
-------------
Simply creating a token account is not enough for secure custody. The problem
is that regular token accounts are owned by user wallets, which are vulnerable
to phishing and key theft. A Vault is a higher-level construct that combines
a program-derived address, a state account, and programmable rules to protect
assets. It transforms raw token storage into a governed, conditional system.

Definition
----------
A Vault is a smart contract abstraction consisting of a PDA, a state account,
and one or more token accounts that together enforce rules about when and how
assets can be deposited, held, or withdrawn.

Real-life analogy
-----------------
Imagine a storage unit facility. A regular token account is like a locker at
the gym. You have a key, and if someone steals your key, they can open it.
A vault is like a high-security storage unit with a manager, cameras, and
access rules. The manager holds a master key, but they will only unlock your
unit if you show ID, provide a code, and visit during business hours. Even if
someone steals your gym locker key, they cannot access the storage unit because
the facility enforces additional layers of control. A Solana vault adds those
layers on-chain: time delays, multi-signature checks, or programmatic conditions.

Tiny numeric example
--------------------
A vault program manages three user vaults:
- Vault 1: Owner Alice, 5,000 USDC, unlocks after block height 2,000,000
- Vault 2: Owner Bob, 2 SOL wrapped as wSOL, requires 2-of-3 signatures
- Vault 3: Owner DAO, 50,000 governance tokens, releases upon proposal pass
Each vault has its own state account recording these rules. The program reads
the state before any withdrawal. If the rules are satisfied, the program
invokes a CPI to the SPL Token program to move the assets.

Common confusion
----------------
- A vault is not a single account. It is usually a system of accounts: a state
  account, one or more token accounts, and a PDA that acts as signer.
- Vaults do not earn interest automatically. Interest-bearing vaults are a
  separate layer that deposits vault funds into a lending protocol.
- The PDA owning a vault token account cannot hold tokens for arbitrary users
  in a single account without internal accounting. Each user typically needs
  a distinct token account or a state mapping.
- Vaults are not the same as token accounts. A token account stores a balance.
  A vault adds logic, rules, and controls around that balance.
- Creating a vault does not lock tokens automatically. A separate deposit
  instruction must move tokens into the vault's token account.
- Vault fees are program-specific. Some charge on deposit, some on withdrawal,
  and some are free. The fee logic is part of the program, not the SPL standard.
- Vault programs can be composable. One vault can hold receipts from another
  vault, creating nested or layered security structures.

Where it appears in our code
----------------------------
`src_web3/phase13/vault/src/lib.rs` — defines the vault state structure and
enforces deposit and withdrawal rules.

Vault state management
----------------------
A well-designed vault separates three concerns: the custody layer, the rule
layer, and the execution layer. The custody layer is the PDA-owned token
account that actually holds the tokens. The rule layer is the state account
that records who deposited what and under what conditions. The execution layer
is the program logic that reads the state, validates conditions, and issues
CPI transfers. Keeping these layers distinct makes the program easier to audit,
test, and upgrade. When the rule layer changes, the custody layer remains
stable, preventing accidental fund exposure.

Practical Vault checklist
-------------------------
- Separate custody, rule, and execution concerns in code.
- Use immutable state transitions: initialized, funded, released, closed.
- Log all state changes with clear messages for debugging.
- Validate every condition before executing any CPI transfer.
- Test edge cases such as zero deposits, double deposits, and early withdrawals.
- Perform integration tests with the SPL Token program on devnet.
- Document vault state schemas for client developers and auditors.
- Use versioned state structs to enable safe future upgrades.
- Benchmark compute usage under maximum vault load before mainnet launch.

## Phase 9 Summary: Program State with Accounts

### Key Takeaways

1. **Programs are stateless; accounts hold state.** Your program is bytecode. All persistent data lives in data accounts that your program owns.
2. **Serialization converts structs to bytes.** Account data is raw bytes. You must serialize before writing and deserialize after reading.
3. **Borsh is the standard format.** It is deterministic, compact, and cross-language. Use `#[derive(BorshSerialize, BorshDeserialize)]` in Rust.
4. **State changes are atomic.** If a transaction fails, no account data is modified. Only successful transactions commit state.
5. **Account size is fixed at creation.** You pay rent for the space you allocate. Plan your struct sizes carefully.

### What We Built

- Program state documentation explaining how state lives outside programs in owned accounts
- Serialization documentation showing the conversion between structs and raw bytes
- Borsh documentation covering the standard binary format for Solana
- A Counter Rust program that initializes and increments a u64 stored in account data
- A Cargo.toml with the correct dependencies for on-chain Borsh serialization
- Express API that initializes accounts, sends increment transactions, and reads back state

### Files

| File | Purpose |
|------|---------|
| `docs_web3/phase9/what_is_program_state.md` | How programs store data in owned accounts |
| `docs_web3/phase9/what_is_serialization.md` | Converting structs to bytes and back |
| `docs_web3/phase9/what_is_borsh.md` | Borsh as the deterministic serialization standard |
| `docs_web3/phase9/SUMMARY.md` | This file — phase recap and connections |
| `src_web3/phase9/counter/Cargo.toml` | Dependencies: solana-program, borsh |
| `src_web3/phase9/counter/src/lib.rs` | Counter program: Initialize and Increment instructions |
| `src_web3/phase9/state_api.ts` | Express API: read and write program state via REST |

### Connections to Other Phases

- **Phase 8** taught you the anatomy of a program. Phase 9 adds the missing piece: persistent state.
- **Phase 6** covered transactions and instructions. Now you see how instructions mutate account state through a program.
- **Phase 10** introduces PDAs, which let you derive deterministic state accounts for each user without managing keypairs.

### Next Step

Phase 10: **Program Derived Addresses (PDA)** — Learn how to create deterministic, program-controlled addresses that have no private key.

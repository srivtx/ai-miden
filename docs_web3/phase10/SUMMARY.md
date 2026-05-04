## Phase 10 Summary: Program Derived Addresses (PDA)

### Key Takeaways

1. **PDAs have no private key.** They are off-curve addresses that only the owning program can sign for using `invoke_signed`.
2. **PDAs are deterministic.** The same seeds and program_id always produce the same PDA. Anyone can calculate it, but only the program can create an account there.
3. **The bump ensures off-curve status.** The derivation algorithm tries bumps starting at 255 until the hash is off-curve. You must store and pass this bump.
4. **Seeds are public identifiers.** User pubkeys, string literals, and mint addresses make excellent seeds for generating unique addresses.
5. **PDAs are the foundation of user-specific state.** They allow you to give every user their own account without managing keypairs.

### What We Built

- PDA documentation explaining off-curve derivation and program control
- Bump documentation covering the brute-force search for a valid off-curve hash
- Seeds documentation showing how to compose unique identifiers for different use cases
- A PDA demo Rust program that derives a per-user PDA, creates it via CPI, and increments a counter stored inside
- Cargo.toml with dependencies for PDA programs using Borsh
- Express API that derives PDAs client-side and invokes the program to create and update them

### Files

| File | Purpose |
|------|---------|
| `docs_web3/phase10/what_is_pda.md` | Program Derived Addresses: no private key, program-controlled |
| `docs_web3/phase10/what_is_bump.md` | The byte that pushes the hash off the elliptic curve |
| `docs_web3/phase10/what_is_seeds.md` | Composing unique, deterministic identifiers |
| `docs_web3/phase10/SUMMARY.md` | This file — phase recap and connections |
| `src_web3/phase10/pda_demo/Cargo.toml` | Dependencies for PDA program with Borsh |
| `src_web3/phase10/pda_demo/src/lib.rs` | PDA program: derive, create, and increment per-user counters |
| `src_web3/phase10/pda_api.ts` | Express API: derive and create PDAs via REST |

### Connections to Other Phases

- **Phase 6** taught you transactions. PDAs are created and mutated through transactions that invoke your program.
- **Phase 8** introduced programs and entrypoints. PDAs are the addresses your program manages inside its processor.
- **Phase 9** covered state and serialization. PDAs are the accounts where that serialized state lives.

### Next Step

You now have a complete foundation: wallets, transactions, RPC, programs, state, and PDAs. Continue to advanced topics like token programs, CPI, and program security.

## Phase 8 Summary: Writing Your First Program

### Key Takeaways

1. **Programs are stateless bytecode.** They contain logic, not data. All state lives in separate accounts owned by the program.
2. **The entrypoint is the front door.** It is the single function the runtime calls when your program is invoked. Keep it thin.
3. **The processor is the brain.** It parses instructions, validates accounts, executes logic, and serializes state back to accounts.
4. **Programs are sandboxed.** They cannot access the internet, filesystem, or randomness. All inputs come through accounts and instruction data.
5. **Deployment is permanent.** Once deployed, a program lives at a fixed address. Only the upgrade authority can modify it.

### What We Built

- Program documentation explaining the anatomy of on-chain code
- Entrypoint documentation showing how the runtime connects to your logic
- Processor documentation covering business logic, validation, and state updates
- A "Hello World" Rust program that logs a message when invoked
- Express API that demonstrates building, deploying, and invoking programs

### Files

| File | Purpose |
|------|---------|
| `docs_web3/phase8/what_is_program.md` | Solana programs: stateless BPF bytecode |
| `docs_web3/phase8/what_is_entrypoint.md` | The single function the runtime calls |
| `docs_web3/phase8/what_is_processor.md` | Business logic, validation, and state mutation |
| `docs_web3/phase8/SUMMARY.md` | This file — phase recap and connections |
| `src_web3/phase8/hello_world/Cargo.toml` | Program dependencies and build config |
| `src_web3/phase8/hello_world/src/lib.rs` | Minimal program that logs "Hello, Solana!" |
| `src_web3/phase8/program_deploy_api.ts` | Express API: build, deploy, and invoke programs |

### Connections to Other Phases

- **Phase 6** taught you transactions and instructions. Now you understand what happens on the other end when a transaction invokes a program.
- **Phase 7** showed you how to read program accounts via RPC. You will use that to inspect deployed programs.
- **Phase 9** adds state to programs. The Hello World program has no state; the Counter program will store data in accounts.

### Next Step

Phase 9: **Program State with Accounts** — Learn how to store and mutate data in accounts owned by your program.

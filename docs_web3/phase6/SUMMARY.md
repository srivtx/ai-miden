## Phase 6 Summary: Your First Transaction

### Key Takeaways

1. **A transaction is an atomic container.** Every instruction inside either succeeds or fails together. No partial commits exist.
2. **An instruction is a single command.** It specifies the program, accounts, and data needed for one operation.
3. **The recent blockhash is a time limit.** It prevents replay attacks by making transactions valid only for a short window.
4. **Signatures prove authorization.** Any account that is mutated must sign the transaction.
5. **Devnet provides free SOL for testing.** Always develop on devnet, never on mainnet.

### What We Built

- Transaction anatomy documentation explaining how Solana moves value
- Instruction-level documentation showing how to construct operations
- Blockhash documentation explaining transaction expiration
- Rust client that creates a wallet, requests an airdrop, and sends SOL
- TypeScript client that mirrors the Rust logic using @solana/web3.js
- Express API that exposes transaction creation, signing, sending, and monitoring over HTTP

### Files

| File | Purpose |
|------|---------|
| `docs_web3/phase6/what_is_transaction.md` | Transaction anatomy, atomicity, and fees |
| `docs_web3/phase6/what_is_instruction.md` | Instruction structure: program ID, accounts, data |
| `docs_web3/phase6/what_is_recent_blockhash.md` | Blockhash as nonce, expiration, and replay protection |
| `docs_web3/phase6/SUMMARY.md` | This file — phase recap and connections |
| `src_web3/phase6/first_transaction.rs` | Rust client: airdrop, transfer, verify on devnet |
| `src_web3/phase6/first_transaction.ts` | TypeScript client: same logic with @solana/web3.js |
| `src_web3/phase6/transaction_api.ts` | Express API: create, sign, send, monitor transactions |

### Connections to Other Phases

- **Phase 5** provided the dev environment and wallet setup needed to run these transactions.
- **Phase 7** teaches you to read blockchain data, which you will use to verify transactions after sending them.
- **Phase 8** introduces writing your own program, which you will invoke using the instructions learned here.

### Next Step

Phase 7: **Reading Blockchain Data** — Learn how to query balances, account info, slots, and transactions using RPC nodes.

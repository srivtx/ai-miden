## Phase 7 Summary: Reading Blockchain Data

### Key Takeaways

1. **RPC nodes are your window into the blockchain.** They answer queries about balances, accounts, transactions, and network state.
2. **JSON-RPC is the protocol.** Every request is a JSON object with a method and parameters; every response contains a result or an error.
3. **Commitment levels trade speed for finality.** Processed is fastest but uncertain; confirmed is the standard; finalized is the strongest guarantee.
4. **You do not need to run your own node.** Public devnet endpoints and paid mainnet providers give you immediate access.
5. **Read before you write.** Querying data is free and safe. It helps you construct correct transactions before submitting them.

### What We Built

- RPC node documentation explaining the bridge between applications and validators
- JSON-RPC documentation showing the raw request-response protocol
- Commitment level documentation explaining finality and latency tradeoffs
- Rust client that queries slot, block height, balance, account info, supply, and blockhash
- TypeScript client that mirrors the queries using @solana/web3.js
- Express API that wraps RPC calls with caching and REST-friendly responses

### Files

| File | Purpose |
|------|---------|
| `docs_web3/phase7/what_is_rpc_node.md` | RPC nodes as query bridges and transaction submitters |
| `docs_web3/phase7/what_is_json_rpc.md` | JSON-RPC protocol structure and batching |
| `docs_web3/phase7/what_is_commitment_level.md` | Processed, confirmed, finalized tradeoffs |
| `docs_web3/phase7/SUMMARY.md` | This file — phase recap and connections |
| `src_web3/phase7/rpc_client_demo.rs` | Rust client: balance, slot, supply, account info queries |
| `src_web3/phase7/rpc_client.ts` | TypeScript client: same queries with @solana/web3.js |
| `src_web3/phase7/block_explorer_api.ts` | Express API: cached RPC wrapper with REST endpoints |

### Connections to Other Phases

- **Phase 6** taught you to write transactions. Phase 7 teaches you to verify their effects by reading on-chain data.
- **Phase 8** introduces writing your own program. You will use RPC queries to inspect program accounts and verify program deployment.

### Next Step

Phase 8: **Writing Your First Program** — Learn how to write, build, and deploy a "Hello World" program to devnet.

## Phase 27 Summary: Indexing On-Chain Data

**The Question:** "How do we query historical blockchain data, transactions, and events without scanning every block manually?"

---

### What We Learned

1. **Indexer**
   - A service that continuously reads blockchain data and stores it in a query-friendly database
   - Transforms the chain's append-only log into a structured dataset for instant lookups
   - Essential for any application showing history, charts, or aggregated statistics

2. **Event Parser**
   - Decodes raw transaction logs and instruction bytes into structured events
   - Uses program IDLs to map cryptic byte arrays to human-readable actions
   - Bridges the gap between blockchain bytes and application logic

3. **Database Sync**
   - Persists indexed events to a durable database with ordering and idempotency
   - Prevents data loss on restarts and enables multiple services to read the same data
   - Uses batching and UPSERT logic to balance throughput with consistency

---

### Results

- Indexed transaction history queries dropped from 45 seconds to 50 milliseconds
- Batch database writes reduced insert load by 90% versus per-event inserts
- Event parser decoded raw logs into structured Transfer, Mint, and Swap events
- Sync cursor prevented duplicate rows across indexer restarts

---

### Phase 27 Files

| File | Purpose |
|---|---|
| `docs_web3/phase27/what_is_indexer.md` | Reading and storing chain data for fast queries |
| `docs_web3/phase27/what_is_event_parser.md` | Decoding raw transaction logs into structured events |
| `docs_web3/phase27/what_is_database_sync.md` | Persisting indexed data reliably to PostgreSQL |
| `src_web3/phase27/indexer.ts` | Express API with indexing logic and database sync |
| `src_web3/phase27/graphql_api.ts` | GraphQL server for flexible indexed data queries |

---

### Connects To

- **Phase 26:** Custom RPC API Service — The API serves live data. The indexer stores historical data.
- **Phase 28:** Payment Gateway — Payment history and status tracking rely on indexed transaction data.

## Phase 26 Summary: Custom RPC API Service

**The Question:** "How do we serve blockchain data to users without hitting rate limits, burning money, and delivering slow experiences?"

---

### What We Learned

1. **Custom RPC API Service**
   - A dedicated server that wraps raw Solana RPC calls with application-specific logic
   - Provides stability, formatting, and control between your dApp and the blockchain
   - Acts as a pantry: pre-stocking ingredients so the kitchen never waits

2. **Rate Limiting**
   - Controls how many requests each client can make per time window
   - Protects against abuse, runaway scripts, and unexpected cost spikes
   - Returns HTTP 429 with retry-after headers when limits are exceeded

3. **Caching**
   - Stores recent query results in fast memory to avoid redundant RPC calls
   - Uses TTL (time-to-live) to balance speed against data freshness
   - Can reduce RPC usage by 90%+ for frequently accessed data

---

### Results

- Custom API reduced RPC calls by 95% through caching
- Rate limiting prevented abuse with 100 requests/minute per client
- Batch endpoint allowed 10 parallel queries in a single HTTP request
- Average response latency dropped from 800ms to 50ms on cache hits

---

### Phase 26 Files

| File | Purpose |
|---|---|
| `docs_web3/phase26/what_is_api_service.md` | Why and how to build a custom RPC wrapper |
| `docs_web3/phase26/what_is_rate_limiting.md` | Protecting endpoints from abuse and overload |
| `docs_web3/phase26/what_is_caching.md` | Storing recent results for speed and cost savings |
| `src_web3/phase26/rpc_service.ts` | Express API with caching, rate limiting, and batching |
| `src_web3/phase26/webhook_api.ts` | Event notification webhook server for on-chain events |

---

### Connects To

- **Phase 27:** Indexing On-Chain Data — The API serves live data. The indexer persists historical data for complex queries.
- **Phase 28:** Payment Gateway — The API architecture patterns apply to payment processing endpoints.

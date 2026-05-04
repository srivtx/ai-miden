# What is Caching?

## Why It Exists

Blockchain data does not change between blocks, yet applications repeatedly query the same balances, token supplies, and account states.
Each redundant RPC call wastes money, adds latency, and strains infrastructure.
Caching stores recent results so repeated questions get instant answers without burdening the network.
For high-traffic applications, caching is not optional; it is essential for survival.
Without caching, a popular dApp could burn through thousands of dollars in RPC fees every month.
Even a simple balance check repeated thousands of times becomes expensive without a cache.

## Definition

Caching is the practice of storing copies of frequently accessed data in fast, temporary storage.
Future requests for that data can be served quickly without re-fetching from the original slow source.
When the cached data expires or changes, the system fetches fresh data and updates the cache.
It is one of the most effective performance optimizations in distributed systems.
Understanding caching patterns is essential for any blockchain developer building production applications.
A well-designed cache can reduce response times by orders of magnitude.

## Real-Life Analogy

Imagine studying for an exam with a massive textbook.
Instead of walking to the library and flipping through 500 pages every time you forget a formula, you write the key formulas on a sticky note attached to your desk.
The sticky note is your cache.
The library is the blockchain.
For 90% of your study session, you glance at the sticky note.
You only return to the library when you need something new or when your notes get outdated.

A good student updates the sticky note every hour.
A bad student never updates it and memorizes outdated formulas.
The sticky note makes studying faster, but only if it is kept current.
If the formula changes, the student must go back to the textbook.
The best students keep multiple sticky notes for different subjects.

## Tiny Numeric Example

A DeFi dashboard displays a user's SOL balance, total supply, and latest blockhash.

| Data Type | Change Frequency | Cache TTL | RPC Calls Saved |
|---|---|---|---|
| SOL Balance | Per slot (400ms) | 5 sec | 92% |
| Total Supply | Per epoch (~2 days) | 60 sec | 99.9% |
| Latest Blockhash | Per slot | 2 sec | 80% |
| Account Info | Per slot | 10 sec | 96% |
| Token Metadata | Never | 300 sec | 99.99% |

Without caching: 5 RPC calls every page load.
With caching: 0-1 RPC calls per load after the first.
Over a day with 10,000 users, that difference is 50 million versus 10,000 RPC calls.
The cost savings alone justify implementing a cache layer on day one.
A global CDN cache can reduce latency from hundreds of milliseconds to under ten.
This transformation makes blockchain applications feel as responsive as traditional web services.

## Common Confusion

- **"Won't cached data be wrong?"** Only if the TTL is too long for the data type. Blockhash caches need 2 seconds; supply caches can survive 60 seconds.
- **"Is caching the same as an indexer?"** No. Caching is temporary and lives in memory. An indexer persists historical data to a database permanently.
- **"Does caching work for transactions?"** Never cache transaction submission results. Caching is for reads, not writes.
- **"What happens when the cache is full?"** In-memory caches use eviction policies like LRU (Least Recently Used) to drop old entries.
- **"Can't I just cache in the browser?"** Browser caching helps, but server-side caching protects your RPC provider quota and reduces backend load.
- **"Do I need Redis for this?"** Redis is great for production with multiple servers. A single Node.js server can start with a simple Map-based cache.
- **"Why not cache everything forever?"** Stale data causes bugs. A wallet showing an old balance after a transfer confuses users and breaks trust.
- **"What is cache invalidation?"** The hard part of caching: knowing when to delete or update cached data. Time-based TTL is the simplest approach.
- **"Does caching help with NFT metadata?"** Yes. NFT metadata rarely changes and benefits enormously from long cache times.

## Key Properties

- **Speed:** Delivers sub-millisecond responses for frequently requested data instead of waiting for blockchain confirmation.
- **Cost Reduction:** Minimizes expensive RPC calls by reusing recent results across multiple client requests.
- **Freshness Control:** Uses time-to-live settings to balance data accuracy against performance gains.
- **Eviction Policies:** Automatically removes old entries using strategies like LRU when memory limits are reached.
- **Layered Architecture:** Supports multiple cache layers from in-memory stores to distributed CDNs for global scale.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase26/rpc_service.ts` uses an in-memory Map cache with 5-second TTL for balances, blocks, and supply data, plus cache stats and clear endpoints.
The cache helpers `getCached` and `setCached` abstract the storage logic, making it easy to upgrade to Redis later.

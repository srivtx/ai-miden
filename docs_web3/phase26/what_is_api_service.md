# What is a Custom RPC API Service?

## Why It Exists

Every decentralized application needs blockchain data, but connecting thousands of users directly to public RPC nodes creates severe congestion.
Applications crash when free endpoints throttle or return inconsistent data during high traffic periods.
Developers waste money on redundant RPC calls and struggle to provide consistent latencies to their users.
The raw blockchain RPC is designed for validators and indexers, not for end-user applications that need formatted, cached, and protected access.
Without a middle layer, every user action becomes a potential point of failure.
A single viral tweet about your dApp can overwhelm public RPC endpoints and render your application unusable.

## Definition

A custom RPC API service is a dedicated server that wraps raw blockchain RPC calls with additional layers like caching, rate limiting, request batching, and formatted responses.
It improves reliability and performance for client applications by centralizing blockchain access patterns.
The service acts as a controlled gateway between your users and the decentralized network.
Think of it as a translator that converts blockchain complexity into simple HTTP responses.
It abstracts away the quirks of different RPC providers and presents a uniform interface.
This abstraction lets teams swap RPC backends without changing client code.

## Real-Life Analogy

Imagine a busy restaurant kitchen where every waiter runs directly to the farm for ingredients.
The kitchen would collapse from chaos, delay, and miscommunication.
Some waiters would fight over the same carrots, others would return with rotten produce, and the head chef would have no idea when food would arrive.
Instead, the restaurant builds a pantry: a central station that stocks fresh ingredients, tracks usage, controls access, and serves the kitchen instantly.

The custom RPC API is that pantry.
It pre-fetches popular data, controls how often waiters can request supplies, and delivers everything in a clean format so the kitchen never stops moving.
When a customer orders the special, the pantry already has the ingredients ready.
The farm still grows the food, but the pantry makes it usable for the kitchen staff.
Without the pantry, the restaurant would serve cold meals and angry customers.
The pantry manager also checks inventory, rejects unreasonable requests, and keeps records of what was used.

## Tiny Numeric Example

A mobile wallet app checks account balances for 10,000 users every minute.

| Approach | Requests/Min | Avg Latency | Monthly Cost |
|---|---|---|---|
| Direct RPC | 10,000 | 800ms | $500 |
| Custom API + Cache | 500 (cache hits) | 50ms | $50 |
| Batch Requests | 100 batches | 120ms | $45 |
| Savings | 95% | 93% faster | 90% cheaper |

With a 5-second cache TTL, 95% of balance requests hit the cache instead of the RPC node.
Batch endpoints further reduce overhead by letting clients request 10 operations in a single HTTP call.
Over a month, this saves millions of RPC requests and hundreds of dollars in infrastructure costs.
The savings scale linearly with user growth.
A startup with 100,000 users could save over $4,000 per month just by adding a cache layer.
Enterprise applications with millions of users see even more dramatic savings.
A properly architected API layer becomes a competitive advantage at scale.

## Common Confusion

- **"Isn't this just a proxy?"** No. A proxy forwards requests unchanged. A custom API adds caching, formatting, authentication, and business logic on top.
- **"Doesn't caching make data stale?"** Only if configured poorly. TTL settings balance freshness with speed. Balance caches use 5-30 seconds; blockhash caches use 1-2 seconds.
- **"Why not just use a paid RPC provider?"** Paid providers solve infrastructure, not application-specific needs. Your API adds custom formatting, user auth, and aggregated endpoints.
- **"Isn't this centralized?"** The API is centralized infrastructure, but it reads from decentralized blockchains. Users can always fall back to direct RPC.
- **"Do I need this for a small project?"** Small projects benefit too. Even a single cache layer prevents hitting public rate limits during development.
- **"Can't the frontend call the blockchain directly?"** It can, but every user then needs RPC URLs, handles errors, and parses raw responses. The API centralizes that complexity.
- **"Is this the same as an indexer?"** No. An indexer writes on-chain data to a database. An API service queries the chain live and may cache, but does not persist historical data.
- **"Does this replace my wallet connection?"** No. Wallets still sign transactions. The API only handles read queries and data formatting.
- **"How does this help during airdrops?"** Airdrops spike RPC usage by 100x. Rate limiting and caching keep your app alive while competitors crash.

## Key Properties

- **Performance:** Reduces latency by serving cached or pre-computed data instead of querying the blockchain directly.
- **Reliability:** Provides stable uptime even when upstream RPC nodes experience issues or rate limiting.
- **Cost Efficiency:** Dramatically lowers infrastructure costs by reducing redundant RPC calls and bandwidth usage.
- **Security:** Acts as a controlled gateway that can enforce authentication, rate limits, and input validation.
- **Scalability:** Handles traffic spikes gracefully through caching layers and load balancing strategies.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase26/rpc_service.ts` implements a complete Express server with balance queries, account info, block data, supply checks, batch requests, and cache management.
It also includes request timing middleware and health checks for operational monitoring.
The service uses in-memory caching with a 5-second TTL and enforces a 100-request-per-minute rate limit per IP address.

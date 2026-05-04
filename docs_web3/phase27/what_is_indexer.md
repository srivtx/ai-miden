# What is an Indexer?

## Why It Exists

Blockchain nodes are optimized for consensus and state validation, not for querying historical data.
Asking a node "show all token transfers for this wallet in the last month" requires scanning every block manually, which is unbearably slow and expensive.
Indexers solve this by pre-processing and storing chain data in query-friendly databases so applications can retrieve historical information instantly.
Without indexers, any feature involving history would be practically unusable.
Users would wait minutes for simple history queries.

## Definition

An indexer is a service that continuously reads blockchain data, extracts relevant events and state changes, and stores them in a structured database.
Applications can then query historical and aggregated information instantly.
The indexer transforms the blockchain from an append-only log into a queryable dataset.
It is the bridge between raw chain data and application-friendly databases.
An indexer is essentially a specialized ETL pipeline for blockchain data.
Building a robust indexer requires understanding both blockchain mechanics and database optimization.

## Real-Life Analogy

Imagine a library where books arrive in random boxes with no catalog.
Finding every mention of "whales" across 10,000 boxes would take years.
An indexer is the librarian who opens every box, reads every page, and builds a card catalog organized by topic, author, and date.
When you ask for whale books, the librarian points to the exact shelf in seconds instead of decades.

The librarian works continuously, adding new books to the catalog as they arrive, so the catalog is always current.
Without the librarian, the library is just a warehouse of unreadable boxes.
The librarian also cross-references related topics, making connections that would be impossible to find manually.
A good indexer is like a librarian who never sleeps.

## Tiny Numeric Example

A wallet app wants to display transaction history.

| Method | Latency | Cost per Query | Scalability |
|---|---|---|---|
| Direct RPC scan | 45 seconds | 10,000 RPC calls | Poor |
| Indexed database | 50 milliseconds | 1 SQL query | Excellent |
| Improvement | 900x faster | 99.99% cheaper | Infinite |

Scanning 100,000 blocks via RPC takes minutes and risks rate limits.
An indexed PostgreSQL table with an account index returns the same data in milliseconds.
The indexer pays the scanning cost once so every user query is instant.
This amortizes the expensive work across all future queries.
A well-indexed database can handle millions of historical queries per second.
This performance unlocks real-time analytics and rich user experiences impossible with direct RPC.
Modern indexers can process millions of events per second while maintaining sub-second query latency.
This performance makes blockchain data accessible to consumer applications for the first time.
Indexing transforms blockchain from a niche technology into a platform for mainstream apps.
Every major blockchain application relies on indexing to deliver responsive user experiences.

## Common Confusion

- **"Is an indexer just a cache?"** No. Caches store temporary copies of live data. Indexers persist historical data permanently and organize it for complex queries.
- **"Doesn't the blockchain already store this?"** Yes, but in a format optimized for consensus. Blockchains are write-optimized append-only logs, not read-optimized databases.
- **"Can't I use getSignaturesForAddress?"** That RPC method works for recent history but has limits and skips metadata. Indexers provide full history with parsed details.
- **"Is indexing centralized?"** The indexer is centralized infrastructure, but anyone can run their own. The underlying data remains on the decentralized chain.
- **"Do I need an indexer for a simple dApp?"** If you only need current balances, no. If you need history, charts, or aggregations, yes.
- **"What's the difference between an indexer and an API?"** An API serves requests from the chain or cache. An indexer writes chain data to a database so APIs and frontends can query it.
- **"Can I index everything?"** You can, but storage grows fast. Production indexers filter for specific programs or event types to stay efficient.
- **"How do indexers handle reorgs?"** They track blockhashes and confirmation levels, rolling back data if a fork is detected.
- **"What is the Graph?"** A popular decentralized indexing protocol that uses subgraphs to define what data to index.

## Key Properties

- **Historical Queries:** Enables fast lookups of past transactions, events, and state changes that would be impossible via RPC.
- **Structured Storage:** Converts raw blockchain bytes into organized database tables with indexes and relationships.
- **Real-Time Sync:** Continuously processes new blocks to keep the database current with the chain state.
- **Filtering:** Supports selective indexing so only relevant programs and events are stored, saving disk space.
- **Aggregations:** Powers dashboards and analytics by pre-computing sums, counts, and averages across large datasets.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase27/indexer.ts` implements an Express API that indexes account changes and program events into PostgreSQL tables for fast historical queries.
It includes a polling loop, event parser, and sync cursor to prevent duplicate processing.

# What is Database Sync?

## Why It Exists

An indexer reads blockchain data, but that data lives in memory temporarily.
If the indexer restarts, unwritten data is lost.
Database sync is the process of reliably persisting indexed events to a durable database so queries are consistent, historical data survives restarts, and multiple services can read the same dataset.
Without sync, an indexer is just a temporary viewer, not a permanent record.
Every production indexer must solve the sync problem before it can serve real users.
Developers should design sync architecture before writing a single line of parsing code.
Every query would return different results depending on when the indexer started.

## Definition

Database sync is the mechanism by which an indexer writes parsed blockchain events to a persistent database.
It maintains consistency between the chain's current state and the database's stored state through ordered inserts and idempotency checks.
Sync ensures that what the database contains matches what actually happened on-chain.
It is the persistence layer that makes indexing useful.
Sync transforms ephemeral memory into durable truth.
Without reliable sync, even the best indexer is just a temporary window into blockchain history.

## Real-Life Analogy

Imagine a journalist taking notes on a live press conference with a pencil and notepad.
If the journalist loses the notepad, the story is gone.
Database sync is the assistant who types every note into a shared document in real time.
Even if the journalist's pencil breaks or they step out, the document already contains every word up to that moment.
The newsroom can publish without waiting.

The assistant also checks for duplicates so the same quote never appears twice.
Without the assistant, the story dies with the notepad.
The assistant keeps track of which statements have already been recorded, preventing redundancy.
When the journalist returns, they pick up exactly where they left off.
The shared document is the database, and the assistant is the sync mechanism.

## Tiny Numeric Example

An indexer processes 10 blocks per second, each with 200 transactions.

| Strategy | Writes/Sec | Data Loss Risk | Recovery Time |
|---|---|---|---|
| One insert per event | 2,000 | Low | Instant |
| Batch insert every 5 blocks | 400 | Medium | 2 seconds |
| Batch insert every block + UPSERT | 200 | Low | 400ms |
| No sync | 0 | Total | Total loss |

Batching 5 blocks at a time reduces database load by 90% while keeping the data loss window under 2 seconds on Solana.
The UPSERT pattern prevents duplicate rows when re-processing blocks after a restart.
A sync cursor tracks the last committed block so recovery is automatic.
The cursor ensures no block is processed twice and no block is skipped.
This guarantees data integrity even across restarts and network interruptions.
Production indexers often run multiple sync processes for redundancy and fault tolerance.

## Common Confusion

- **"Isn't database sync just saving to a database?"** It is saving, but with ordering, idempotency, and conflict resolution. The same event might be re-indexed after a restart.
- **"Can't I just write as I parse?"** You can, but unbatched writes overwhelm the database during high-throughput periods and create lock contention.
- **"What happens if the indexer crashes mid-batch?"** Good sync logic tracks the last successfully committed block and resumes from there, skipping already-written events.
- **"Do I need a relational database?"** PostgreSQL works well for structured queries. NoSQL options like MongoDB work for flexible schemas. Column stores work for analytics.
- **"How do I handle chain reorganizations?"** Solana has minimal reorgs, but indexers should still handle forked slots by tracking blockhash confirmations.
- **"Is sync real-time or periodic?"** Both. Streaming sync is near real-time. Periodic sync processes blocks in batches on a schedule.
- **"What is idempotency and why does it matter?"** Idempotency means running the same operation twice produces the same result. It prevents duplicate rows when the indexer re-processes a block.
- **"Can I use a sync cursor?"** Yes. A sync cursor tracks the highest processed block so the indexer resumes correctly after restarts.
- **"What about data retention?"** Production indexers often archive old data to cold storage to keep query performance high.

## Key Properties

- **Durability:** Guarantees that indexed data survives restarts, crashes, and deployments without loss.
- **Idempotency:** Ensures re-processing the same block produces identical database state without duplicates.
- **Ordering:** Preserves chronological sequence of events so historical queries return correct timelines.
- **Batching:** Groups multiple writes into atomic transactions to improve throughput and reduce database load.
- **Cursor Tracking:** Maintains a pointer to the last synced block for reliable resume after interruptions.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase27/indexer.ts` implements batched event insertion with UPSERT logic and a sync cursor table to track the last processed slot and prevent duplicates.

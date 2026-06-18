# The Decisions

> *"Either both writes happen, or neither. There is no in-between."*

## Decision 1: Knex's transaction and not raw SQL

**Alternative**: Raw SQL with `BEGIN`, `COMMIT`, `ROLLBACK`.

**Why Knex: Same pattern as the rest of our code. The `trx` object is a query builder like `db`. No raw SQL.

**Trade-off**: Slightly less control. For complex transactions, you might want raw SQL.

## Decision 2: Default isolation level

**Alternative**: Set a custom isolation level (READ UNCOMMITTED, REPEATABLE READ, etc.).

**Why default: The default (SERIALIZABLE in SQLite, READ COMMITTED in Postgres) is the right choice for most apps. We don't need to change it.

**Trade-off**: For high-concurrency systems, you'd tune the isolation level. We don't.

## Decision 3: No savepoints

**Alternative**: Use savepoints for nested transactions.

**Why not: We don't have nested transactions. For our use case, a flat transaction is enough.

**Trade-off**: For complex workflows, you'd use savepoints. We don't.

## Decision 4: Validation in the transaction

We check the balance inside the transaction:

```js
const fromUser = await trx('users').where({ id: fromUserId }).first();
if (fromUser.balance < amount) {
  throw new ValidationError([...]);
}
```

**Why inside: The check and the update must be atomic. If we check outside, the balance could change between the check and the update.

**Trade-off**: The transaction holds locks for longer. For our use case, this is fine.

## Decision 5: Cache invalidation after the transaction

We invalidate the cache after the transaction:

```js
await db.transaction(async (trx) => { ... });
await cache.delete(`user:${fromUserId}`);
await cache.delete(`user:${toUserId}`);
```

**Why after: The transaction must commit first. Then we invalidate the cache.

**Trade-off**: A brief window where the cache has the old balance. We accept this. Could be solved with cache invalidation inside the transaction (with Redis) or with a stale-while-revalidate pattern.

## Decision 6: Authorization check outside the transaction

We check `req.user.userId !== fromUserId` outside the transaction:

```js
if (req.user.userId !== fromUserId) {
  throw new ForbiddenError('You can only transfer from your own account');
}
```

**Why outside: Auth checks don't need to be in the transaction. They're cheap and don't change.

**Trade-off**: A user could pass the auth check, then have their account deleted, then the transfer would fail. We accept this.

## Decision 7: Throw errors, don't return false

Inside the transaction, we throw errors:

```js
if (fromUser.balance < amount) {
  throw new ValidationError([...]);
}
```

**Why throw: Throwing triggers a rollback. Returning false would not.

**Trade-off**: We need to catch the throw. The `asyncHandler` wrapper catches it. The error wall maps it to a status code.

## Decision 8: No retry on transaction failure

**Alternative**: Retry the transaction on failure (e.g., deadlock).

**Why not: SQLite has no deadlocks (single writer). For Postgres, you'd retry on serialization failure.

**Trade-off**: A failed transaction is just an error. The user retries manually.

## Decision 9: No distributed transactions

**Alternative**: Use a saga pattern or 2PC for transactions across multiple services.

**Why not: We have one service. Single database. For multi-service, you'd use a saga (project 40).

**Trade-off**: For multi-service transactions, you need a different pattern. Out of scope.

## Decision 10: No optimistic locking

**Alternative**: Use a `version` column. On update, check that the version hasn't changed. If it has, retry.

**Why not: For our use case, the database's pessimistic locking is enough.

**Trade-off**: For high-concurrency updates, optimistic locking is more scalable. We don't.

---

## What We Did Not Decide

- **Savepoints** — out of scope
- **Custom isolation levels** — out of scope
- **Distributed transactions** — out of scope
- **Optimistic locking** — out of scope
- **Saga pattern** — out of scope
- **Retry on failure** — out of scope
- **Deadlock detection** — out of scope (SQLite has none)
- **Long-running transactions** — out of scope
- **Read-only transactions** — out of scope
- **Savepoint names** — out of scope

Each is a future decision.

---

## The Meta-Decision: Multi-Step Writes Are Atomic

For 26 projects, multi-step writes were independent. The first could succeed and the second could fail. The system was inconsistent.

Now multi-step writes are atomic. Either all succeed (commit) or all fail (rollback). The system is always consistent. Money is conserved. Users and workspaces are created together or not at all.

This is the foundation of *data integrity*. Transactions are non-negotiable for any non-trivial system. The patterns (`db.transaction`, `trx` object, error rollback) are universal.

**Phase 4 (Real-World Operations) is now complete!** Projects 19-27 added: search, file upload, email, caching, Redis, rate limiting, cron, queue, transactions. The API has all the real-world operations.

The next 13 projects will assume transactions exist. The path diverges:

- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

Multi-step writes are atomic. The path continues.

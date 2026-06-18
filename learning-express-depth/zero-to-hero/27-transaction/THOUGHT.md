# The Thought

> *"A transaction is a promise. Either the database keeps all the changes, or it keeps none."*

## How Transactions Work

A transaction is a sequence of operations that the database treats as a single unit. The lifecycle:

1. **BEGIN**: start the transaction
2. **Operations**: do the work (INSERT, UPDATE, DELETE)
3. **COMMIT**: save all the changes (if everything succeeded)
4. **ROLLBACK**: discard all the changes (if anything failed)

The database ensures atomicity: if any operation fails, all previous operations in the transaction are rolled back. The database state is as if the transaction never happened.

In SQL, the syntax is:

```sql
BEGIN;
UPDATE users SET balance = balance - 50 WHERE id = 1;
UPDATE users SET balance = balance + 50 WHERE id = 2;
COMMIT;
-- or ROLLBACK; if anything fails
```

In Knex (and Node), the syntax is:

```js
await db.transaction(async (trx) => {
  await trx('users').where({ id: 1 }).decrement('balance', 50);
  await trx('users').where({ id: 2 }).increment('balance', 50);
});
```

The `trx` is a transaction object. Operations on `trx` are part of the transaction. If the async function throws, the transaction is rolled back. If it succeeds, the transaction is committed.

## The Transfer Example

```js
app.post('/transfer', authMiddleware, asyncHandler(async (req, res) => {
  const { fromUserId, toUserId, amount } = req.body;

  await db.transaction(async (trx) => {
    // Check balance
    const fromUser = await trx('users').where({ id: fromUserId }).first();
    if (fromUser.balance < amount) {
      throw new ValidationError([{ path: 'amount', message: 'insufficient funds' }]);
    }

    // Debit from sender
    await trx('users').where({ id: fromUserId }).decrement('balance', amount);

    // Credit to receiver
    await trx('users').where({ id: toUserId }).increment('balance', amount);
  });

  res.json({ message: 'Transfer complete' });
}));
```

The transfer is atomic. Either:
- Both writes succeed: Alice is down $50, Bob is up $50.
- The check fails (insufficient funds): nothing is changed.
- The debit fails: nothing is changed.
- The credit fails: the debit is rolled back, nothing is changed.

There is no partial state.

## Why Use the `trx` Object

Inside `db.transaction(async (trx) => { ... })`, you must use `trx` instead of `db` for operations. If you use `db`, the operation is *outside* the transaction and is committed immediately. Only `trx` operations are part of the transaction.

```js
// Wrong
await db.transaction(async (trx) => {
  await trx('users').where({ id: 1 }).decrement('balance', 50);
  await db('users').where({ id: 2 }).increment('balance', 50); // OUTSIDE the transaction
});
// If the first write succeeds and the second fails, the second is committed, but the first is not rolled back.

await db.transaction(async (trx) => {
  // Right
  await trx('users').where({ id: 1 }).decrement('balance', 50);
  await trx('users').where({ id: 2 }).increment('balance', 50);
});
// Either both succeed or both fail.
```

## When to Use Transactions

Use transactions for any multi-step write that must be atomic:

- **Money transfer**: debit + credit
- **Order + inventory**: create order, decrement inventory
- **User + workspace**: create user, create default workspace
- **Post + notification**: create post, queue notification

Use single statements for one-step writes (no transaction needed).

## Common Confusions (read these)

**Confusion 1: "Why not just use `await` for each write?"**
You can, but each `await` is a separate statement. If the second fails, the first is already committed. The system is inconsistent.

**Confusion 2: "What if the server crashes mid-transaction?"**
The database rolls back the transaction. When the server restarts, the state is as if the transaction never happened.

**Confusion 3: "What about nested transactions?"**
SQLite (and most databases) don't support nested transactions. Knex simulates them with savepoints. For our use case, we don't need them.

**Confusion 4: "What about concurrent transactions?"**
The database handles concurrency. If two transactions try to update the same row, one waits for the other. We use the default isolation level (in SQLite, it's serializable).

**Confusion 5: "What if the transaction is slow?"**
Locks are held for the duration of the transaction. If the transaction takes 10 seconds, the row is locked for 10 seconds. For our use case, transactions are fast (milliseconds).

**Confusion 6: "What if I forget to use `trx`?"**
The operation is outside the transaction. It's committed immediately. If you intended it to be in the transaction, you have a bug.

**Confusion 7: "What about performance?"**
Transactions have overhead. For high-throughput systems, you'd minimize transaction scope. For our use case, the overhead is negligible.

**Confusion 8: "Why not just use a try/catch?"**
`try/catch` lets you handle errors. It doesn't make the writes atomic. If you `try { debit } catch { /* nothing */ }`, the debit is committed. The catch only prevents the throw from propagating.

## What We Are About to Build

A ~500-line Express app that:

1. Has a `balance` column on `users`
2. Has a `POST /transfer` endpoint
3. Wraps the transfer in a transaction
4. Returns 200 on success, 400 on insufficient funds, 500 on other errors

The handlers are slightly different. The new piece is the transfer endpoint with the transaction.

In [BUILD.md](./BUILD.md) we will go line by line.

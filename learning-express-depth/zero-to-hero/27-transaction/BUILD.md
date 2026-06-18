# The Build

> *"Either both writes happen, or neither. There is no in-between."*

We are going to add a transfer endpoint with a transaction. The change from project 26: add a `balance` column, add a `POST /transfer` endpoint, wrap the writes in a transaction.

## The Migration

```js
// Add to MIGRATIONS
{
  version: 6,
  up: `ALTER TABLE users ADD COLUMN balance INTEGER NOT NULL DEFAULT 0`,
},
```

The `balance` column defaults to 0. New users start with no balance. Existing users (if any) get 0.

## The Code

### The Transfer Endpoint

```js
const transferSchema = z.object({
  fromUserId: z.number().int().positive(),
  toUserId: z.number().int().positive(),
  amount: z.number().int().positive(),
});

app.post('/transfer', authMiddleware, validate(transferSchema), asyncHandler(async (req, res) => {
  const { fromUserId, toUserId, amount } = req.validated;

  // Only the authenticated user can transfer from their own account
  if (req.user.userId !== fromUserId) {
    throw new ForbiddenError('You can only transfer from your own account');
  }

  await db.transaction(async (trx) => {
    // Check balance
    const fromUser = await trx('users').where({ id: fromUserId }).first();
    if (!fromUser) {
      throw new NotFoundError('Sender not found');
    }
    if (fromUser.balance < amount) {
      throw new ValidationError([{ path: 'amount', message: 'insufficient funds' }]);
    }

    // Check receiver exists
    const toUser = await trx('users').where({ id: toUserId }).first();
    if (!toUser) {
      throw new NotFoundError('Receiver not found');
    }

    // Debit sender
    await trx('users').where({ id: fromUserId }).decrement('balance', amount);

    // Credit receiver
    await trx('users').where({ id: toUserId }).increment('balance', amount);
  });

  // Invalidate caches
  await cache.delete(`user:${fromUserId}`);
  await cache.delete(`user:${toUserId}`);

  res.json({ message: 'Transfer complete' });
}));
```

### The transaction

```js
await db.transaction(async (trx) => {
  // ... operations on trx ...
});
```

Inside the transaction:
- `trx('users').where(...).first()` — uses the transaction connection
- `trx('users').where(...).decrement(...)` — uses the transaction
- `trx('users').where(...).increment(...)` — uses the transaction

If any operation throws (e.g., insufficient funds, receiver not found), the transaction is rolled back. The balance is unchanged.

If all operations succeed, the transaction is committed. The balance is updated.

### Why use `trx` instead of `db`

`trx` is the transaction connection. Operations on `trx` are part of the transaction. If you use `db`, the operation is outside the transaction and is committed immediately. Mixing `db` and `trx` in the same transaction is a bug.

### Cache invalidation

After the transfer, we invalidate the cache for both users. Their balances have changed.

```js
await cache.delete(`user:${fromUserId}`);
await cache.delete(`user:${toUserId}`);
```

## Run It

```bash
# Set Alice's balance to 100
sqlite3 app.db "UPDATE users SET balance = 100 WHERE id = 1;"

# Set Bob's balance to 0
sqlite3 app.db "UPDATE users SET balance = 0 WHERE id = 2;"

# Login as Alice
TOKEN=$(curl -X POST http://localhost:3000/sessions \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# Transfer 50 from Alice to Bob
curl -X POST http://localhost:3000/transfer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fromUserId":1,"toUserId":2,"amount":50}'
# {"message":"Transfer complete"}

# Check balances
sqlite3 app.db "SELECT id, username, balance FROM users;"
# 1|alice|50
# 2|bob|50

# Try to transfer more than Alice has
curl -X POST http://localhost:3000/transfer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fromUserId":1,"toUserId":2,"amount":100}'
# {"error":"Validation failed","code":"VALIDATION","issues":[{"path":"amount","message":"insufficient funds"}]}

# Check balances (unchanged)
sqlite3 app.db "SELECT id, username, balance FROM users;"
# 1|alice|50
# 2|bob|50
```

The transfer succeeds when there's enough balance. The transfer fails when there isn't. The balances are consistent.

---

## Experiments

### Experiment 1: Transfer to non-existent user

```bash
curl -X POST http://localhost:3000/transfer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fromUserId":1,"toUserId":999,"amount":10}'
# {"error":"Receiver not found","code":"NOT_FOUND"}
```

The receiver doesn't exist. The transaction is rolled back. Alice's balance is unchanged.

### Experiment 2: Concurrent transfers

If two requests try to transfer from the same user at the same time, the database serializes them. The second waits for the first to complete. Both see consistent balances.

(In SQLite, only one writer at a time. In Postgres, the row is locked.)

### Experiment 3: Throw a non-Error in the transaction

```js
await db.transaction(async (trx) => {
  await trx('users').where({ id: 1 }).decrement('balance', 50);
  throw 'string error'; // not an Error
});
```

Knex detects the throw and rolls back. We pass an `Error` for clarity, but any throw works.

### Experiment 4: Try to do something outside the transaction

```js
await db.transaction(async (trx) => {
  await trx('users').where({ id: 1 }).decrement('balance', 50);
  await db('users').where({ id: 2 }).increment('balance', 50); // OUTSIDE!
});
```

The increment is outside the transaction. If the transaction fails, the increment is not rolled back. The system is inconsistent. Don't do this.

---

## Summary

You now have transactions. Multi-step writes are atomic. The system never ends up in an inconsistent state.

This is the foundation of *data integrity*. From here, every multi-step write is wrapped in a transaction. The patterns (`db.transaction`, `trx` object, error rollback) are universal.

**Phase 4 (Real-World Operations) is now complete!** Projects 19-27 added: search, file upload, email, caching, Redis, rate limiting, cron, queue, transactions. The API has all the real-world operations.

In project 28, we begin Phase 5: Real-Time. We add **WebSocket** — bidirectional communication between server and client. The server can push updates without the client asking.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

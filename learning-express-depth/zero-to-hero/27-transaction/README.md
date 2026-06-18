# Project 27: The Transaction

> *"Either both writes happen, or neither. There is no in-between."*

In projects 10-26, our database writes are independent. Each `INSERT`, `UPDATE`, `DELETE` is a single statement. The database handles each atomically.

But what if we need *multiple* writes to be atomic together? For example:

- **Transfer money**: debit account A, credit account B. Both must happen, or neither.
- **Create a post + send notification**: the post must be created, then a notification is sent. If the post fails, no notification.
- **Signup + create workspace**: the user is created, then a workspace is created for them. If the user fails, no workspace.

Without **transactions**, we have a problem:

1. Debit A succeeds. Server crashes. B is not credited. A lost money.
2. Create post succeeds. Send notification fails. The post exists but no one was notified.
3. Create user succeeds. Create workspace fails. User exists with no workspace.

The fix: **transactions**. A transaction is a group of operations that either all succeed (commit) or all fail (rollback). The database guarantees atomicity.

We use `db.transaction(async (trx) => { ... })` from Knex. The handler is async. If any operation throws, the transaction is rolled back.

By the end, multi-step writes are atomic. We don't end up in inconsistent states.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why do multi-step writes fail? What is a transaction?
2. [The Thought](./THOUGHT.md) — How do transactions work? What is ACID?
3. [The Build](./BUILD.md) — Line-by-line construction of the transaction
4. [The Decisions](./DECISIONS.md) — Why transactions? Why Knex? Why SQLite?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A transaction is a group of database operations that either all succeed (commit) or all fail (rollback). The database guarantees atomicity: you never see a partial result. Knex provides `db.transaction(async (trx) => { ... })` — operations inside use the `trx` object instead of `db`. If the async function throws, the transaction is rolled back. If it succeeds, the transaction is committed.

---

## The Code

```js
app.post('/transfer', authMiddleware, asyncHandler(async (req, res) => {
  const { fromUserId, toUserId, amount } = req.body;

  await db.transaction(async (trx) => {
    // Debit from user
    const fromUser = await trx('users').where({ id: fromUserId }).first();
    if (fromUser.balance < amount) {
      throw new ValidationError([{ path: 'amount', message: 'insufficient funds' }]);
    }
    await trx('users').where({ id: fromUserId }).decrement('balance', amount);

    // Credit to user
    await trx('users').where({ id: toUserId }).increment('balance', amount);
  });

  res.json({ message: 'Transfer complete' });
}));
```

The transfer is atomic. Either both writes happen, or neither. The user's balance is never inconsistent.

---

## What You Will Have Learned

- What a transaction is (atomic multi-write)
- The ACID properties (atomicity, consistency, isolation, durability)
- How Knex's `db.transaction` works
- How to use the `trx` object instead of `db`
- How errors trigger rollback
- When to use transactions (multi-step writes that must be atomic)

These are the foundations of *data integrity*. From here, every multi-step write is wrapped in a transaction.

# The Problem

> *"Either both writes happen, or neither. There is no in-between."*

## Why Multi-Step Writes Fail

In projects 10-26, our database writes are independent. Each `INSERT`, `UPDATE`, `DELETE` is a single statement. The database handles each atomically.

But what if we need *multiple* writes to be atomic together? The classic example is a money transfer:

1. Debit account A: $100
2. Credit account B: $100

If step 1 succeeds and step 2 fails, A is down $100 and B has nothing. The bank lost $100.

Or:

- Server crashes between step 1 and step 2 → A is down $100, B has nothing.
- Network drops between step 1 and step 2 → same.
- Database error in step 2 → same.

This is a *consistency* issue. The database is in a state that violates the rule "money is conserved."

## What Pain Is This Solving?

Imagine you have a `users` table with a `balance` column. Alice has $100. Bob has $0. Alice wants to send $50 to Bob.

```js
await db('users').where({ id: alice.id }).decrement('balance', 50);
await db('users').where({ id: bob.id }).increment('balance', 50);
```

Two writes. If both succeed, Alice has $50 and Bob has $50. The system is consistent.

But if the first write succeeds and the second fails (e.g., Bob's account was deleted between the two writes), Alice has $50 and Bob has $0. Alice lost $50. The system is inconsistent.

The fix: **transactions**. A transaction groups multiple writes. Either all succeed (commit) or all fail (rollback). The database guarantees atomicity.

## The Deeper Problem: ACID

Transactions provide **ACID** properties:

- **Atomicity**: all operations in the transaction succeed, or none do.
- **Consistency**: the database moves from one valid state to another. Constraints are not violated.
- **Isolation**: concurrent transactions don't interfere with each other.
- **Durability**: once committed, the changes are permanent (even if the server crashes).

These are the gold standard for database integrity. Every "real" database (Postgres, MySQL, even SQLite) provides ACID transactions.

## What This Project Will Solve

This project will:

1. Add a `balance` column to `users` (a new migration)
2. Add a `POST /transfer` endpoint
3. Wrap the transfer in a transaction
4. Show what happens if a step fails (rollback)

By the end, multi-step writes are atomic. The system never ends up in an inconsistent state.

## What This Project Will *Not* Solve

- **Deadlocks** — we don't cover the complexity of concurrent transactions. Out of scope.
- **Isolation levels** — we use the default. Out of scope.
- **Distributed transactions** — across multiple databases. Out of scope.
- **Optimistic locking** — using a version column to detect concurrent updates. Out of scope.
- **Saga pattern** — for distributed transactions across services. Out of scope (project 40).

## The Question This Project Answers

> *"How do I make multiple writes atomic?"*

If you can answer: "use `db.transaction(async (trx) => { ... })`, operations inside use `trx`, errors trigger rollback, success commits," you are ready for project 28.

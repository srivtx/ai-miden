# The Thought

> *"A migration is a number and a string. The number is its order. The string is the change. The database remembers which numbers have run."*

## What a Migration Is

A migration is a *versioned change to the schema*. Each migration has:

- A `version` (a number, increasing) — its order
- An `up` (a SQL string) — the change to apply
- Optionally, a `down` — how to revert (we skip this)

Example migrations:

```js
const MIGRATIONS = [
  { version: 1, up: `CREATE TABLE users ...; CREATE TABLE posts ...;` },
  { version: 2, up: `ALTER TABLE users ADD COLUMN email TEXT` },
  { version: 3, up: `CREATE TABLE comments ...` },
];
```

The versions are sequential. They are applied in order. Each migration is applied exactly once.

## The Migrations Table

We need a way to remember which migrations have been applied. The standard is a `migrations` table:

```sql
CREATE TABLE migrations (
  version INTEGER PRIMARY KEY,
  applied_at INTEGER NOT NULL
);
```

Each row is a migration that has been applied. The `version` is the migration's version. The `applied_at` is when it was applied (Unix timestamp).

On startup:

1. Create the `migrations` table if it doesn't exist
2. Read the list of applied versions
3. For each migration in `MIGRATIONS`, if its version is not in the applied set, apply it and insert a row

This is idempotent. If we restart the server, the applied migrations are skipped.

## Transactions

A migration should be *atomic*: either all the SQL in the migration is applied, or none of it is. We use a transaction:

```js
const tx = db.transaction(() => {
  db.exec(m.up);
  db.prepare('INSERT INTO migrations (version, applied_at) VALUES (?, ?)').run(m.version, Date.now());
});
tx();
```

`db.transaction(fn)` returns a function. When called, it runs `fn` inside a `BEGIN` ... `COMMIT`. If `fn` throws, the transaction is rolled back. If `fn` succeeds, the changes are committed.

We wrap both the schema change and the `migrations` insert in the same transaction. This way, if the schema change fails, the `migrations` row is not inserted (so we'll try again next time).

## ALTER TABLE in SQLite

```sql
ALTER TABLE users ADD COLUMN email TEXT UNIQUE
```

This adds a column to an existing table. The column is `email TEXT UNIQUE` — text, unique. Existing rows have `NULL` for the new column (because they didn't have it before).

SQLite supports `ALTER TABLE ADD COLUMN`. It does not support `ALTER TABLE DROP COLUMN` (in older versions) or many other alterations. For complex changes, you'd have to:

1. Create a new table with the new schema
2. Copy data from the old table
3. Drop the old table
4. Rename the new table

This is called a "table rebuild." It's complex. We don't need it yet.

## The Migration Code, Line by Line

```js
const MIGRATIONS = [
  { version: 1, up: `...` },
  { version: 2, up: `...` },
];

function runMigrations() {
  db.exec(`CREATE TABLE IF NOT EXISTS migrations (
    version INTEGER PRIMARY KEY,
    applied_at INTEGER NOT NULL
  )`);

  const applied = new Set(
    db.prepare('SELECT version FROM migrations').all().map((r) => r.version)
  );

  for (const m of MIGRATIONS) {
    if (applied.has(m.version)) continue;
    const tx = db.transaction(() => {
      db.exec(m.up);
      db.prepare('INSERT INTO migrations (version, applied_at) VALUES (?, ?)').run(m.version, Date.now());
    });
    tx();
    console.log(`Applied migration ${m.version}`);
  }
}

runMigrations();
```

### `db.exec('CREATE TABLE IF NOT EXISTS migrations ...')`

Create the migrations table if it doesn't exist. Idempotent.

### `const applied = new Set(...)`

Read all applied versions into a Set. `Set.has(version)` is O(1).

### `for (const m of MIGRATIONS)`

Iterate the migrations in order.

### `if (applied.has(m.version)) continue;`

Skip if already applied.

### `db.transaction(fn)`

Wrap the migration in a transaction. `fn` runs inside `BEGIN` ... `COMMIT`. If it throws, the changes are rolled back.

### `db.exec(m.up)`

Run the migration's SQL. This is the schema change.

### `db.prepare(...).run(m.version, Date.now())`

Insert a row into `migrations` to record that this migration has been applied.

## Common Confusions (read these)

**Confusion 1: "What if I add a migration with version 1.5?"**
Don't. Use integer versions. Migrations are ordered by version, and fractional versions complicate that.

**Confusion 2: "What if I want to change a migration that's already been applied?"**
You can't. The migration is in the past. To fix it, you add a new migration that does the change. The old migration stays as-is in the array (so the system knows it's been applied).

**Confusion 3: "What if I delete a migration from the array?"**
The system will see that the migration's version is in the `migrations` table but not in the array. It will ignore it (it's already applied). If you delete the migration AND the corresponding row in the `migrations` table, the system won't re-apply it (because the SQL is gone). So you can't really "undo" a migration by deleting the file.

**Confusion 4: "What if the SQL in the migration has a syntax error?"**
The transaction is rolled back. The migration is not recorded. Next startup, we'll try again. We should fix the SQL and restart.

**Confusion 5: "What if the migration succeeds but the INSERT fails?"**
The transaction is rolled back. Both the schema change and the insert are reverted. Next startup, we'll try again.

**Confusion 6: "Why integer timestamps?"**
Same reason as in the `users` table — Unix timestamps in milliseconds. Easy to format with `new Date(timestamp).toISOString()`.

**Confusion 7: "What if two servers start at the same time and both run migrations?"**
SQLite has file locking. The second server will fail with `SQLITE_BUSY`. We accept this. For multi-server setups, use Postgres with advisory locks.

**Confusion 8: "Why no down migrations?"**
Down migrations are useful but complex. We'd have to write the reverse SQL for every migration. If we get it wrong, we can lose data. We keep it simple. If we need to revert, we write a new migration that does the reverse.

## What We Are About to Build

A ~150-line Express app that:

1. Has the same auth and post flow as project 11
2. Has a `MIGRATIONS` array
3. Has a `runMigrations()` function
4. Migration 1: create the tables
5. Migration 2: add `email` to users
6. The auth flow is unchanged
7. The signup handler accepts an optional `email`

The new pieces are the migration system, the `ALTER TABLE`, and the optional `email` field in signup. The rest of the code is the same as project 11.

In [BUILD.md](./BUILD.md) we will go line by line.

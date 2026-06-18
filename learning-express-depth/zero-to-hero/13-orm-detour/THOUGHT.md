# The Thought

> *"A query builder is a function that takes JavaScript and returns SQL. The mapping is mechanical. The abstraction is useful."*

## What a Query Builder Is

A *query builder* is a library that lets you construct SQL queries using JavaScript method calls. Instead of:

```js
db.exec('SELECT * FROM users WHERE username = ?', [username]);
```

You write:

```js
db('users').where({ username }).first();
```

The library builds the SQL string, parameterizes it, runs it, and returns the result.

## Knex: A Query Builder

Knex is one of the most popular query builders for Node. It supports:

- Schema building (`createTable`, `alterTable`, `dropTable`)
- Querying (`select`, `where`, `join`, `orderBy`, `limit`, `offset`)
- Inserting (`insert`)
- Updating (`update`)
- Deleting (`delete` / `del`)
- Transactions (`transaction`)

It works with multiple database backends: SQLite, Postgres, MySQL, etc. We use SQLite.

## The Knex API

### Initialization

```js
const knex = require('knex');

const db = knex({
  client: 'better-sqlite3',
  connection: { filename: 'app.db' },
  useNullAsDefault: true,
});
```

`client` is the database driver. `connection` is the connection details. For SQLite, just the filename. `useNullAsDefault: true` is required for SQLite (otherwise it complains about default values).

### Schema: `createTable`

```js
await db.schema.createTable('users', (t) => {
  t.increments('id').primary();
  t.string('username').unique().notNullable();
  t.string('hash').notNullable();
  t.string('email').unique();
  t.bigInteger('created_at').notNullable();
});
```

`db.schema.createTable(name, callback)` creates a table. The callback receives a table builder. Methods on the builder:

- `t.increments('id')` — auto-incrementing integer primary key
- `t.string('username')` — VARCHAR
- `t.text('body')` — TEXT
- `t.integer('user_id')` — INTEGER
- `t.bigInteger('created_at')` — BIGINT
- `t.unique()` — UNIQUE constraint
- `t.notNullable()` — NOT NULL
- `t.references('id').inTable('users').onDelete('CASCADE')` — foreign key
- `t.primary()` — PRIMARY KEY

The result is the same `CREATE TABLE` SQL. Just written in JavaScript.

### Schema: `alterTable`

```js
await db.schema.alterTable('users', (t) => {
  t.string('email').unique();
});
```

Adds the `email` column. Same as `ALTER TABLE users ADD COLUMN email TEXT UNIQUE`. The builder handles the syntax.

### Schema: `hasColumn`

```js
const hasEmail = await db.schema.hasColumn('users', 'email');
if (!hasEmail) {
  await db.schema.alterTable('users', (t) => {
    t.string('email').unique();
  });
}
```

Check if a column exists. Use this for *idempotent* migrations.

### Querying: `select` and `where`

```js
const user = await db('users').where({ username: 'alice' }).first();
// user: { id, username, hash, email, created_at } or undefined
```

`db('users')` is a *query builder* for the `users` table. `.where({...})` adds a WHERE clause. `.first()` returns the first row (or undefined).

```js
const allUsers = await db('users');
// allUsers: array of user objects
```

Without `.first()`, it returns an array.

### Querying: `select` with specific columns

```js
const users = await db('users').select('id', 'username');
// users: [{ id, username }, ...]
```

By default, Knex selects all columns (`select *`). You can be explicit.

### Querying: `join`

```js
const posts = await db('posts')
  .join('users', 'posts.user_id', 'users.id')
  .select('posts.*', 'users.username as author')
  .orderBy('posts.created_at', 'desc');
```

`db('posts').join('users', 'posts.user_id', 'users.id')` is `FROM posts JOIN users ON posts.user_id = users.id`. The Knex syntax is more readable.

`.select('posts.*', 'users.username as author')` selects the columns we want.

`.orderBy('posts.created_at', 'desc')` orders by `posts.created_at` descending.

### Inserting: `insert`

```js
const [id] = await db('users').insert({
  username: 'alice',
  hash: '...',
  email: 'alice@example.com',
  created_at: Date.now(),
});
// id: 1 (the new row's primary key)
```

`db('users').insert({...})` inserts a row. Returns the new row's ID (or IDs, if inserting many).

Knex generates the `INSERT INTO users (username, hash, email, created_at) VALUES (?, ?, ?, ?)` SQL with the values as parameters. No SQL injection.

### Updating: `update`

```js
await db('users').where({ id: 1 }).update({ email: 'new@example.com' });
```

`update({...})` updates the matching rows. Returns the count of affected rows.

### Deleting: `delete` / `del`

```js
await db('users').where({ id: 1 }).delete();
```

Or `.del()` (alias). Deletes the matching rows.

### Transactions

```js
await db.transaction(async (trx) => {
  await trx('users').insert({...});
  await trx('posts').insert({...});
});
```

`db.transaction(callback)` runs the callback in a transaction. If the callback throws, the transaction is rolled back.

## Why Knex and Not Prisma

Knex is a *query builder*. It doesn't have a model layer. You write JavaScript expressions that compile to SQL.

Prisma is a *full ORM*. It has:
- A schema language (`schema.prisma`)
- Generated TypeScript types
- A migration system
- A client that's typed

For this project, Knex is enough. For larger apps, Prisma or Drizzle (TypeScript-first) might be better.

## Common Confusions (read these)

**Confusion 1: "Why is everything async now?"**
`better-sqlite3` was sync. Knex wraps it (or other drivers) and exposes a Promise-based API. So `db('users').insert(...)` returns a Promise. We `await` it.

**Confusion 2: "Where did my prepared statements go?"**
Knex creates prepared statements internally. You don't see them, but they're there. The query is compiled once and cached.

**Confusion 3: "Why `useNullAsDefault: true`?"**
SQLite complains about default values in some cases. This option tells Knex to use `NULL` as the default. Standard for SQLite.

**Confusion 4: "What if I forget `await`?"**
You get a Promise, not the result. Then `.first()` on a Promise doesn't work. Always `await`.

**Confusion 5: "Why `increments('id')` instead of `integer('id').primary()`?"**
`increments` is shorthand for `INTEGER PRIMARY KEY AUTOINCREMENT` in SQLite. It also sets up the auto-increment.

**Confusion 6: "What is the difference between `delete` and `del`?"**
None, in Knex. `del` is an alias for `delete` (because `delete` is a reserved word in some contexts).

**Confusion 7: "What about the `migrations` table from project 12?"**
Knex has its own migration system (`knex migrate:make`, `knex migrate:latest`). We could use it. We don't, because we're demonstrating the pattern, not adopting the library. In a real project, you'd use Knex's migration tools.

## What We Are About to Build

A ~150-line Express app that:

1. Uses Knex for all database operations
2. Has the same auth and post flow as project 12
3. Uses `db.schema.createTable` for migrations
4. Uses `db('users').insert(...)` for inserts
5. Uses `db('users').where({...}).first()` for queries
6. Uses `db('posts').join(...).select(...)` for joins

The handlers are slightly different (async, no prepared statements). The patterns are the same.

In [BUILD.md](./BUILD.md) we will go line by line.

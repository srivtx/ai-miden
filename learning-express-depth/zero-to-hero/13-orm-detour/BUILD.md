# The Build

> *"No more SQL strings. Just JavaScript that compiles to SQL."*

We are going to replace prepared statements with Knex. The change from project 12: replace `db.prepare(...)` with `db('table').method(...)`, and replace `db.exec('CREATE TABLE ...')` with `db.schema.createTable(...)`.

## Setup

```bash
npm install knex better-sqlite3
```

`knex` is the query builder. `better-sqlite3` is the SQLite driver that Knex uses.

## The File

Create `server.js`. Fill it in.

---

## Lines 1-12: The Imports and App

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());
```

Same as project 12, plus `knex`.

---

## Lines 14-19: The Database

```js
const db = knex({
  client: 'better-sqlite3',
  connection: { filename: 'app.db' },
  useNullAsDefault: true,
});
```

`knex(config)` creates a database client. The config:

- `client` — `'better-sqlite3'` (the driver)
- `connection.filename` — `'app.db'` (the database file)
- `useNullAsDefault: true` — required for SQLite

The `db` object is the Knex instance. We use it for all queries and schema operations.

Note: Knex is async. The `db` object has methods that return Promises.

---

## Lines 21-46: The Migrations

```js
async function migrate() {
  await db.schema.createTableIfNotExists('users', (t) => {
    t.increments('id').primary();
    t.string('username').unique().notNullable();
    t.string('hash').notNullable();
    t.string('email').unique();
    t.bigInteger('created_at').notNullable();
  });

  await db.schema.createTableIfNotExists('posts', (t) => {
    t.increments('id').primary();
    t.integer('user_id').notNullable().references('id').inTable('users').onDelete('CASCADE');
    t.string('title').notNullable();
    t.text('body').notNullable();
    t.bigInteger('created_at').notNullable();
  });

  const hasEmail = await db.schema.hasColumn('users', 'email');
  if (!hasEmail) {
    await db.schema.alterTable('users', (t) => {
      t.string('email').unique();
    });
  }
}

migrate().then(() => {
  app.listen(3000, () => console.log('Server listening on http://localhost:3000'));
});
```

### `db.schema.createTableIfNotExists(name, callback)`

Creates a table if it doesn't exist. The callback receives a table builder. We use the builder methods to define columns.

`t.increments('id').primary()` — auto-incrementing integer primary key. Knex's shorthand for `INTEGER PRIMARY KEY AUTOINCREMENT`.

`t.string('username').unique().notNullable()` — VARCHAR with UNIQUE and NOT NULL.

`t.integer('user_id').notNullable().references('id').inTable('users').onDelete('CASCADE')` — INTEGER with foreign key to `users.id`, cascading on delete.

### `db.schema.hasColumn(table, column)`

Returns a Promise that resolves to `true` if the column exists, `false` otherwise. We use it to make the `email` addition idempotent.

### `db.schema.alterTable(name, callback)`

Alters a table. The callback receives a table builder. We add the `email` column.

### Why `migrate().then(...)`?

Migrations are async. We wait for them to complete before starting the server. The `.then(() => app.listen(...))` ensures the server only listens after the schema is ready.

In a real app, you'd run migrations as a separate step (`npm run migrate`), not on server start. We do it on start for simplicity.

---

## Lines 48-110: The Auth and Post Handlers

The handlers are now async and use Knex instead of prepared statements. For example:

### Signup

```js
app.post('/signup', async (req, res) => {
  const { username, password, email } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const existing = await db('users').where({ username }).first();
  if (existing) {
    return res.status(409).json({ error: 'username already taken' });
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  res.status(201).json({ id, username, email: email || null });
});
```

### What changed

- `findUserByUsername.get(username)` → `await db('users').where({ username }).first()`
- `insertUser.run(username, hash, email, Date.now())` → `await db('users').insert({ username, hash, email, created_at: Date.now() })`
- The result is the new ID (Knex returns an array, we destructure the first element)

### Why `db('users').where({...}).first()`?

- `db('users')` — start a query on the `users` table
- `.where({...})` — add a WHERE clause. Knex generates `WHERE username = ?` and parameterizes the value.
- `.first()` — return the first row (or undefined if no match)

The result is a row object or `undefined`. Same as the old `findUserByUsername.get(...)`.

### Why `db('users').insert({...})`?

- `db('users')` — start a query on the `users` table
- `.insert({...})` — INSERT the row. Knex generates `INSERT INTO users (username, hash, ...) VALUES (?, ?, ...)` and parameterizes.

The result is an array of inserted IDs. We destructure the first.

### Login, /me, post routes

Same pattern. `db('users').where({...}).first()` for queries, `db('users').insert({...})` for inserts, `db('posts').join('users', ...).select(...)` for joins.

The full file shows the rewrites.

---

## The Full File

The full file is shown in the README. The new pieces are the Knex setup, the migration function, and the rewritten handlers. The auth flow is unchanged. The post flow is unchanged.

---

## Run It

```bash
npm install knex better-sqlite3
node server.js

# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2","email":"alice@example.com"}'
# {"id":1,"username":"alice","email":"alice@example.com"}

# Create post
TOKEN=$(curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","body":"World"}'
# {"id":1,"userId":1,"title":"Hello","body":"World"}
```

The handlers are slightly different. The behavior is the same.

---

## Experiments

### Experiment 1: Forget `await`

```js
const user = db('users').where({ username }).first();
// user is a Promise, not a row
```

`if (user)` is always true (a Promise is truthy). The check fails. Always `await`.

### Experiment 2: Use `select` to limit columns

```js
const users = await db('users').select('id', 'username');
// users: [{ id, username }, ...]
```

The hash and email are not returned. Useful for performance and security.

### Experiment 3: Use `count`

```js
const [{ count }] = await db('users').count('id as count');
// count: number of users
```

Knex supports aggregation: `count`, `sum`, `avg`, `min`, `max`.

### Experiment 4: Use `where` with operators

```js
const recent = await db('posts').where('created_at', '>', Date.now() - 86400000);
// posts created in the last 24 hours
```

Knex's `where` supports operators: `>`, `<`, `>=`, `<=`, `<>`, `like`, etc.

### Experiment 5: Use transactions

```js
await db.transaction(async (trx) => {
  const [id] = await trx('users').insert({...});
  await trx('posts').insert({ user_id: id, ... });
});
```

If the post insert fails, the user insert is rolled back. Atomic.

### Experiment 6: Use `pluck`

```js
const usernames = await db('users').pluck('username');
// usernames: ['alice', 'bob', ...]
```

`pluck` returns an array of a single column's values.

---

## Summary

You now have a query builder. SQL strings are gone. JavaScript expressions generate the SQL. Prepared statements are automatic. The handlers are slightly different but the patterns are stable.

This is the foundation of *database abstraction*. From here, every project uses Knex (or Prisma, or Drizzle). The patterns (`db('table').where({...}).first()`) are universal.

In project 14, we will add validation. We will reject bad input with proper status codes. The handlers will check the body before doing anything.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

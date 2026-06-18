# The Problem

> *"Every query is a string. Every string is a chance for a typo. Every typo is a runtime error. Or worse, a security hole."*

## Why Hand-Written SQL Is Painful

In projects 10-12, our database code looks like this:

```js
const insertUser = db.prepare(`
  INSERT INTO users (username, hash, email, created_at) VALUES (?, ?, ?, ?)
`);
const findUserByUsername = db.prepare(`
  SELECT id, username, hash, email, created_at FROM users WHERE username = ?
`);
const findUserById = db.prepare(`
  SELECT id, username, hash, email, created_at FROM users WHERE id = ?
`);
const findAllPosts = db.prepare(`
  SELECT posts.id, posts.user_id, posts.title, posts.body, posts.created_at,
         users.username AS author
  FROM posts JOIN users ON posts.user_id = users.id
  ORDER BY posts.created_at DESC
`);

// usage
const user = findUserByUsername.get(username);
const result = insertUser.run(username, hash, email, Date.now());
const posts = findAllPosts.all();
```

For 3 queries, this is manageable. For 30 queries, it's a lot of:

1. SQL string boilerplate
2. Manual `?` placeholder management
3. Manual column list maintenance (if you add a column, you have to update every `SELECT`)
4. Manual JOIN syntax
5. No compile-time checks (typos only show up at runtime)

## What Pain Is This Solving?

Imagine you have 50 prepared statements across 10 tables. Adding a column means updating every `SELECT` that mentions the table. Forgetting one is a silent bug — the API returns incomplete data, but no error.

Or imagine you have a typo in a SQL string: `SELECT * FORM users` (FORM instead of FROM). The query fails at runtime. There's no autocomplete. There's no type checking. You have to read the SQL string to find the bug.

An ORM/query builder solves this:

1. **No SQL strings** — you write JavaScript expressions that compile to SQL
2. **No placeholder management** — values are passed as objects
3. **No manual column lists** — `select('*')` or `select(['id', 'username'])` are explicit
4. **No JOIN syntax** — `.join('users', 'posts.user_id', 'users.id')` is more readable
5. **Type checking** — some ORMs (Prisma, Drizzle) generate TypeScript types from the schema

## The Deeper Problem: The Database Is a Foreign Language

SQL is a *declarative* language. You describe *what* you want, not *how* to get it. JavaScript is *imperative*. You describe *how* to do things. They're different paradigms.

Hand-written SQL mixes the two: you write JavaScript to call SQL strings. The boundary is awkward. You have to translate parameters, handle results, etc.

An ORM/query builder is a *translator*. It speaks both languages. You write JavaScript; it generates SQL. You get a JavaScript object back; it was a SQL row.

## What This Project Will Solve

This project will:

1. Replace prepared statements with a query builder (Knex)
2. Replace `db.exec('CREATE TABLE ...')` with `db.schema.createTable('users', t => {...})`
3. Replace `statement.run(...)` with `db('users').insert({...})`
4. Replace `statement.get(...)` with `db('users').where({...}).first()`
5. Replace `statement.all()` with `db('users')` (returns array of promises)

By the end, our database code is more readable, more maintainable, and less error-prone.

## What This Project Will *Not* Solve

- **Full ORM features** — Knex is a query builder, not a full ORM. No model classes, no relationships, no migrations built-in. For those, use Prisma, TypeORM, or Drizzle.
- **Type safety** — Knex doesn't generate TypeScript types. Prisma and Drizzle do.
- **Connection pooling** — Knex for SQLite doesn't need a pool. For Postgres, Knex provides one.
- **Multi-database** — we use Knex with `better-sqlite3`. The same Knex code works with `pg` (Postgres), `mysql2`, etc. Just change the client.

## The Question This Project Answers

> *"How do I write database code without writing SQL strings?"*

If you can answer: "use a query builder or ORM, write JavaScript expressions, the library generates SQL," you are ready for project 14.

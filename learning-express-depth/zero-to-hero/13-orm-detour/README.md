# Project 13: The ORM Detour

> *"SQL is a language. JavaScript is a language. An ORM is a translator that lets the second speak the first."*

Projects 10-12 have us writing raw SQL. Every query is a `db.prepare(...)` call. Every insert is a `statement.run(...)` call. The pattern is repetitive:

```js
const insertUser = db.prepare(`INSERT INTO users ...`);
const findUserById = db.prepare(`SELECT ... FROM users WHERE id = ?`);
const findUserByUsername = db.prepare(`SELECT ... FROM users WHERE username = ?`);
```

For 3 queries, that's manageable. For 30, it's a lot of boilerplate. We want a higher-level API.

This project introduces an **ORM** (Object-Relational Mapper). The most popular in the Node ecosystem is **Prisma** (or Drizzle, or Knex, or Sequelize). We use **Knex** — a SQL query builder that lets us write JavaScript instead of SQL strings, with prepared statements baked in.

By the end, our queries look like:

```js
await db('users').insert({ username, hash, email });
const user = await db('users').where({ username }).first();
```

The ORM generates the SQL. We don't write prepared statements by hand.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is hand-written SQL painful? What is an ORM?
2. [The Thought](./THOUGHT.md) — How does a query builder work? What is Knex?
3. [The Build](./BUILD.md) — Line-by-line construction of the Knex-based server
4. [The Decisions](./DECISIONS.md) — Why Knex? Why not Prisma? Why not raw SQL?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

An ORM is a library that maps *tables to classes* (or objects) and *rows to instances*. You write `db('users').where({id: 1}).first()` instead of `SELECT * FROM users WHERE id = 1`. The ORM generates the SQL, runs it, and returns the row. **Knex** is a *query builder*: it doesn't have a model layer (no classes), but it lets you write JavaScript expressions that compile to SQL. We use Knex for its simplicity, but Prisma, Drizzle, and TypeORM are also common.

---

## The Code

```js
// server.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());

const db = knex({
  client: 'better-sqlite3',
  connection: { filename: 'app.db' },
  useNullAsDefault: true,
});

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

// ... auth and post routes use db('users'), db('posts') instead of prepared statements ...
```

Setup:

```bash
npm install knex better-sqlite3
node server.js
```

Test it:

```bash
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
```

The pain of "I have to write prepared statements for every query" is solved. The query builder handles the SQL generation.

---

## What You Will Have Learned

- What an ORM is (a library that maps tables to objects and rows to instances)
- What a query builder is (a library that lets you write JavaScript to build SQL)
- How Knex's `db('table').where(...).first()` generates SQL
- How `db.schema.createTable` replaces `CREATE TABLE` strings
- How `db.schema.alterTable` replaces `ALTER TABLE` strings
- The trade-offs of an ORM (less control, more abstraction)

These are the foundations of *database abstraction*. From here, every project uses a query builder or ORM. The patterns (`db('table').where(...).first()`) become the default.

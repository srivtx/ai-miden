# Project 12: The Migration

> *"The schema is never done. It evolves. Let's evolve it safely."*

Projects 10-11 have a `users` table and a `posts` table. What if we want to add a column?

In project 11, we have one `db.exec(...)` that creates the tables. If we add a column, we'd update that string. But existing databases (from previous runs) already have the old schema. The new `CREATE TABLE` would be a no-op (`IF NOT EXISTS`), and the new column wouldn't be added.

We need a way to *evolve* the schema over time. That's **migrations**.

This project introduces a simple migration system. We keep a list of SQL statements, versioned. On startup, we apply any migrations that haven't been applied yet. Each migration is *idempotent* (safe to run multiple times) and *additive* (doesn't lose data).

By the end, we can add a column without dropping the table, and existing data is preserved.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why migrations? What happens if we change the schema?
2. [The Thought](./THOUGHT.md) — What is a migration? How does versioning work?
3. [The Build](./BUILD.md) — Line-by-line construction of the migration system
4. [The Decisions](./DECISIONS.md) — Why this simple approach? Why not a library?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A migration is a numbered SQL file that changes the schema. We keep a `migrations` table that records which migrations have been applied. On startup, we check: "what's the current version?" Then we apply any new migrations in order. Each migration is wrapped in a transaction (so it either fully applies or fully fails). This is the simplest possible migration system. It's not as feature-rich as Knex, Prisma Migrate, or Flyway, but it teaches the core idea.

---

## The Code

```js
// server.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());

const db = new Database('app.db');
db.pragma('foreign_keys = ON');

const MIGRATIONS = [
  {
    version: 1,
    up: `
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hash TEXT NOT NULL,
        created_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `,
  },
  {
    version: 2,
    up: `ALTER TABLE users ADD COLUMN email TEXT UNIQUE`,
  },
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

// ... rest of the server (same as project 11) ...
```

Setup:

```bash
npm install better-sqlite3
node server.js
```

Test it:

```bash
# First run: applies both migrations
node server.js
# Applied migration 1
# Applied migration 2

# Signup (now with optional email)
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2","email":"alice@example.com"}'

# Restart
node server.js
# (no migrations applied — they're already done)

# The email column is there
sqlite3 app.db "SELECT * FROM users"
```

The pain of "I can't evolve the schema without losing data" is solved. Adding a column is one line in the `MIGRATIONS` array. Existing data is preserved.

---

## What You Will Have Learned

- What a migration is (a versioned SQL change to the schema)
- Why we need a `migrations` table to track which have been applied
- How to apply migrations in order, skipping applied ones
- How to wrap a migration in a transaction
- Why `ALTER TABLE ADD COLUMN` is safe (doesn't lock the table in SQLite)
- The pattern for evolving a schema over time

These are the foundations of *schema evolution*. From here, every schema change is a new migration. Existing data is always preserved.

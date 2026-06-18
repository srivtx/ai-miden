# The Build

> *"If it's not tested, it's broken. You just don't know it yet."*

We are going to add automated tests. The change from project 35: add `vitest` and `supertest` as dev dependencies, write tests for the auth and post flows.

## Setup

```bash
npm install --save-dev vitest supertest
```

## The Code

### `vitest.config.js`

```js
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.js'],
  },
});
```

### `tests/setup.js` (test database)

```js
import knex from 'knex';

export function createTestDb() {
  return knex({
    client: 'better-sqlite3',
    connection: { filename: ':memory:' },
    useNullAsDefault: true,
  });
}

export async function migrate(db) {
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
}
```

### `tests/auth.test.js`

```js
import { describe, it, expect, beforeEach, afterAll } from 'vitest';
import request from 'supertest';
import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { createTestDb, migrate } from './setup.js';

// Create a minimal app for testing
function createApp(db) {
  const app = express();
  app.use(express.json());

  const SECRET = 'test-secret';
  const userCreateSchema = z.object({ username: z.string().min(3).max(30), password: z.string().min(8).max(100) });
  const sessionCreateSchema = z.object({ username: z.string().min(1), password: z.string().min(1) });

  app.post('/users', (req, res) => {
    const result = userCreateSchema.safeParse(req.body);
    if (!result.success) return res.status(400).json({ error: 'Validation failed' });
    const { username, password } = result.data;
    db('users').where({ username }).first().then((existing) => {
      if (existing) return res.status(409).json({ error: 'username already taken' });
      bcrypt.hash(password, 10).then((hash) => {
        db('users').insert({ username, hash, created_at: Date.now() }).then((result) => {
          res.status(201).json({ id: result[0], username });
        });
      });
    });
  });

  app.post('/sessions', (req, res) => {
    const result = sessionCreateSchema.safeParse(req.body);
    if (!result.success) return res.status(400).json({ error: 'Validation failed' });
    const { username, password } = result.data;
    db('users').where({ username }).first().then((user) => {
      if (!user) return res.status(401).json({ error: 'invalid credentials' });
      bcrypt.compare(password, user.hash).then((ok) => {
        if (!ok) return res.status(401).json({ error: 'invalid credentials' });
        const token = jwt.sign({ userId: user.id, username: user.username }, SECRET);
        res.status(201).json({ token, user: { id: user.id, username: user.username } });
      });
    });
  });

  return app;
}

describe('Auth', () => {
  let db, app;

  beforeEach(async () => {
    db = createTestDb();
    await migrate(db);
    app = createApp(db);
  });

  afterAll(async () => {
    await db.destroy();
  });

  it('signs up a new user', async () => {
    const res = await request(app)
      .post('/users')
      .send({ username: 'alice', password: 'hunter2long' });
    expect(res.status).toBe(201);
    expect(res.body.username).toBe('alice');
  });

  it('rejects short passwords', async () => {
    const res = await request(app)
      .post('/users')
      .send({ username: 'alice', password: 'short' });
    expect(res.status).toBe(400);
  });

  it('logs in with correct credentials', async () => {
    await request(app).post('/users').send({ username: 'alice', password: 'hunter2long' });
    const res = await request(app).post('/sessions').send({ username: 'alice', password: 'hunter2long' });
    expect(res.status).toBe(201);
    expect(res.body.token).toBeDefined();
  });

  it('rejects wrong password', async () => {
    await request(app).post('/users').send({ username: 'alice', password: 'hunter2long' });
    const res = await request(app).post('/sessions').send({ username: 'alice', password: 'wrong' });
    expect(res.status).toBe(401);
  });

  it('rejects duplicate usernames', async () => {
    await request(app).post('/users').send({ username: 'alice', password: 'hunter2long' });
    const res = await request(app).post('/users').send({ username: 'alice', password: 'otherlong' });
    expect(res.status).toBe(409);
  });
});
```

### `package.json` scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

## Run It

```bash
npm test
```

Output:
```
 ✓ tests/auth.test.js (5 tests) 250ms

 Test Files  1 passed (1)
      Tests  5 passed (5)
   Duration  250ms
```

The pain of "I have to click around to verify it works" is solved. We run `npm test`. The tests run. We see the results.

---

## Experiments

### Experiment 1: Add a post test

```js
describe('Posts', () => {
  it('requires auth', async () => {
    const res = await request(app).get('/posts');
    // ...
  });

  it('creates a post when authenticated', async () => {
    await request(app).post('/users').send({ username: 'alice', password: 'hunter2long' });
    const login = await request(app).post('/sessions').send({ username: 'alice', password: 'hunter2long' });
    const res = await request(app)
      .post('/posts')
      .set('Authorization', `Bearer ${login.body.token}`)
      .send({ title: 'Hello', body: 'World' });
    expect(res.status).toBe(201);
  });
});
```

### Experiment 2: Test the rate limiter

```js
it('rate limits after 100 requests', async () => {
  for (let i = 0; i < 100; i++) {
    await request(app).get('/');
  }
  const res = await request(app).get('/');
  expect(res.status).toBe(429);
});
```

### Experiment 3: Test with coverage

```bash
npx vitest --coverage
```

Shows which lines are covered. Aim for 80%+.

### Experiment 4: Test the WebSocket

```js
import WebSocket from 'ws';

it('broadcasts chat messages', async () => {
  const ws1 = new WebSocket('ws://localhost:3000/');
  const ws2 = new WebSocket('ws://localhost:3000/');

  await new Promise((resolve) => ws1.on('open', resolve));
  await new Promise((resolve) => ws2.on('open', resolve));

  ws1.send(JSON.stringify({ type: 'chat', user: 'alice', text: 'Hello' }));

  const message = await new Promise((resolve) => ws2.on('message', resolve));
  expect(JSON.parse(message).text).toBe('Hello');
});
```

---

## Summary

You now have an automated test suite. Every change runs through it. We catch bugs before they reach production.

This is the foundation of *test automation*. From here, every project that needs to verify correctness can use these tools. The patterns (Vitest, supertest, separate test DB) are universal.

In project 37, we will add **Docker** for reproducible deployments. The same image runs on any machine.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

# Project 36: The Test Suite

> *"If it's not tested, it's broken. You just don't know it yet."*

In projects 01-35, we've been running the server manually and clicking around. We verify it works by using it. That's not enough. We need **automated tests** that run automatically on every change.

We use **Vitest** (or Jest) — a JavaScript test framework. We write:

1. **Unit tests** for individual functions (e.g., `bcrypt.hash`, `jwt.verify`)
2. **Integration tests** for handlers (e.g., `POST /users` with a real database)
3. **End-to-end tests** for full flows (e.g., signup → login → create post)

The pattern:
- Test database: a separate SQLite file (or `:memory:`) for tests
- Test client: `supertest` makes HTTP requests to the Express app without a real server
- Test fixtures: helpers to create users, posts, etc.

By the end, every change runs through the test suite. If a test fails, the change is rejected. We catch bugs before they reach production.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is manual testing not enough? What is a test suite?
2. [The Thought](./THOUGHT.md) — How do you test an Express app? What is a test database?
3. [The Build](./BUILD.md) — Line-by-line construction of the test suite
4. [The Decisions](./DECISIONS.md) — Why Vitest? Why supertest? Why a separate test DB?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A test suite is a set of automated tests that verify the application works correctly. We use **Vitest** (fast, modern test framework) and **supertest** (HTTP testing). We use a separate test database (`:memory:` SQLite). Each test runs in isolation — the database is reset between tests. The test suite covers unit tests, integration tests, and end-to-end flows.

---

## The Code

```js
// tests/auth.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import request from 'supertest';
import { app, db } from '../server.js';

describe('Auth', () => {
  beforeEach(async () => {
    await db('users').del();
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
});
```

The pain of "I have to click around to verify it works" is solved. We run `npm test`. The tests run. We see the results.

---

## What You Will Have Learned

- What automated tests are (unit, integration, end-to-end)
- How to use Vitest (or Jest) to write tests
- How to use supertest to make HTTP requests
- How to set up a separate test database
- How to run tests in isolation (reset between tests)
- The pattern for testing Express handlers

These are the foundations of *test automation*. From here, every project that needs to verify correctness can use these tools.

# The Thought

> *"If it's not tested, it's broken. You just don't know it yet."*

## The Test Pyramid

There are three levels of tests:

1. **Unit tests**: test individual functions. Fast (microseconds). Many of these.
2. **Integration tests**: test handlers (or groups of handlers). Slower (milliseconds). Fewer of these.
3. **End-to-end tests**: test full user flows. Slowest (seconds). Fewest of these.

The pyramid: many unit tests, fewer integration tests, even fewer end-to-end tests.

For our project, we focus on **integration tests** with `supertest`. We make HTTP requests to the Express app and verify the responses. This covers the handlers, the middleware, the validation, the error wall, the database.

Unit tests are useful for pure functions (e.g., `bcrypt.hash`). End-to-end tests are useful for full flows. For this project, integration tests are the sweet spot.

## How to Test an Express App

`supertest` is a library that makes HTTP requests to an Express app without a real server. It binds to a random port, makes the request, returns the response.

```js
import request from 'supertest';
import { app } from '../server.js';

const res = await request(app).post('/users').send({ username: 'alice', password: 'hunter2long' });
expect(res.status).toBe(201);
```

The `app` is the Express app. We don't need a real server. `supertest` handles the HTTP layer.

## The Test Database

We use a separate database for tests. We have a few options:

- **`:memory:` SQLite**: in-memory, fast, no file. Each test file gets a fresh database.
- **Test file (`app.test.db`)**: on disk. Shared between tests. We reset between tests.
- **Transaction rollback**: run each test in a transaction, roll back at the end. Fast, but requires code changes.

We use `:memory:` for simplicity. Each test file creates a new database.

```js
// tests/setup.js
import knex from 'knex';

export function createTestDb() {
  return knex({
    client: 'better-sqlite3',
    connection: { filename: ':memory:' },
    useNullAsDefault: true,
  });
}
```

In each test file, we create a fresh database, run migrations, and run tests.

## Test Isolation

Each test should be independent. We use `beforeEach` to reset the database:

```js
import { beforeEach } from 'vitest';
import { db } from '../server.js';

beforeEach(async () => {
  // Reset the database
  await db('users').del();
  await db('posts').del();
});
```

Before each test, we delete all rows. The tests don't interfere with each other.

## Common Confusions (read these)

**Confusion 1: "Why a separate test database?"**
Isolation. Tests don't interfere. The dev database isn't polluted.

**Confusion 2: "Why `:memory:` SQLite?"**
Fast. No file. Each test file gets a fresh database.

**Confusion 3: "What about the queue / Redis / WebSocket?"**
Out of scope. We test the HTTP layer. For the queue, use a mock. For WebSocket, use `ws` directly. For Redis, mock it.

**Confusion 4: "What about authentication?"**
We make a real request, get a real token, use the token in subsequent requests. We test the full flow.

**Confusion 5: "What about file uploads?"**
`supertest` supports `multipart/form-data`. Use `.attach('file', path)`.

**Confusion 6: "What about time?"**
Mock time with `vi.useFakeTimers()` for time-sensitive tests (e.g., token expiration).

**Confusion 7: "What about coverage?"**
Use `vitest --coverage` to see which lines are covered. Aim for 80%+.

**Confusion 8: "What about parallelism?"**
Tests run in parallel by default. Each test file gets its own database. No conflicts.

## What We Are About to Build

A ~850-line Express app + ~200-line test suite that:

1. Has unit tests for individual functions
2. Has integration tests for handlers
3. Uses a separate `:memory:` test database
4. Resets the database between tests
5. Runs with `npm test`

The HTTP handlers are unchanged. The new piece is the test suite.

In [BUILD.md](./BUILD.md) we will go line by line.

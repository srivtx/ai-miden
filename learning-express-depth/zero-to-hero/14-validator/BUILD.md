# The Build

> *"Schemas at the door. Bad input stops here."*

We are going to add Zod validation. The change from project 13: define schemas, add a `validate` middleware, and use `req.validated` in the handlers.

## Setup

```bash
npm install knex better-sqlite3 zod
```

Zod is the new dependency.

## The File

Create `server.js`. Fill it in. Most of the code is the same as project 13. The new pieces are the schemas and the middleware.

---

## Lines 1-5: The Imports

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { z } = require('zod');
```

Zod is the new import. `z` is the namespace for all Zod methods.

---

## Lines 7-22: The App, Database, and Migration (Same as Project 13)

```js
const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());

const db = knex({...});

async function migrate() {...}

migrate().then(() => {
  app.listen(3000, () => console.log('Server listening on http://localhost:3000'));
});
```

Same as project 13.

---

## Lines 24-37: The Schemas (NEW)

```js
const signupSchema = z.object({
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(8).max(100),
  email: z.string().email().optional(),
});

const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

const postSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
});
```

### `signupSchema`

- `username`: string, 3-30 chars, alphanumeric + underscore
- `password`: string, 8-100 chars
- `email`: optional string, valid email format

### `loginSchema`

- `username`: required string
- `password`: required string

We use `min(1)` instead of `min(8)` for login because we want to reject empty inputs but accept any non-empty password (we don't re-validate the format on login — the user might be logging in with a password from a previous policy).

### `postSchema`

- `title`: required string, 1-200 chars
- `body`: required string, 1-10000 chars

---

## Lines 39-55: The validate Middleware (NEW)

```js
function validate(schema) {
  return (req, res, next) => {
    try {
      req.validated = schema.parse(req.body);
      next();
    } catch (err) {
      if (err.issues) {
        return res.status(400).json({
          error: 'Validation failed',
          issues: err.issues.map((i) => ({ path: i.path.join('.'), message: i.message })),
        });
      }
      next(err);
    }
  };
}
```

### What it does

A factory that returns Express middleware. The middleware:

1. Parses `req.body` against the schema
2. If valid, puts the parsed result on `req.validated` and calls `next()`
3. If invalid, returns 400 with a structured error

### Why a factory?

`validate(schema)` returns a middleware configured for that schema. We can reuse it for any schema:

```js
app.post('/signup', validate(signupSchema), handler);
app.post('/login', validate(loginSchema), handler);
app.post('/posts', authMiddleware, validate(postSchema), handler);
```

Each route has its own schema, but they all use the same `validate` function.

### Why `req.validated`?

The convention. We use `req.validated` in the handler, not `req.body`. This makes it clear the data has been validated and normalized.

### Why `err.issues`?

Zod's `ZodError` has an `issues` array. Each issue has `path` (e.g., `['username']`) and `message`. We map to a clean shape:

```json
{ "path": "username", "message": "String must contain at least 3 character(s)" }
```

The `path.join('.')` converts `['user', 'name']` to `'user.name'` for nested fields.

---

## Lines 57-110: The Auth and Post Handlers (Updated to use `req.validated`)

### Signup

```js
app.post('/signup', validate(signupSchema), async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    return res.status(409).json({ error: 'username already taken' });
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });
  res.status(201).json({ id, username, email: email || null });
});
```

The handler reads `req.validated` (not `req.body`). The data is guaranteed to be valid: `username` is 3-30 alphanumeric chars, `password` is 8-100 chars, `email` is a valid email or undefined.

### Login

```js
app.post('/login', validate(loginSchema), async (req, res) => {
  const { username, password } = req.validated;
  // ... same as project 13 ...
});
```

### Post creation

```js
app.post('/posts', authMiddleware, validate(postSchema), async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body });
});
```

The middleware chain is `authMiddleware` first (so we know who's logged in), then `validate(postSchema)` (so we know the body is valid), then the handler.

---

## The Full File

The full file is shown in the README. The new pieces are the Zod schemas, the `validate` middleware, and the use of `req.validated` in handlers.

---

## Run It

```bash
npm install knex better-sqlite3 zod
node server.js

# Bad input: short username
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"ab","password":"hunter2long"}'
# {"error":"Validation failed","issues":[{"path":"username","message":"String must contain at least 3 character(s)"}]}

# Bad input: invalid characters
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"ali ce","password":"hunter2long"}'
# {"error":"Validation failed","issues":[{"path":"username","message":"Invalid"}]}

# Bad input: invalid email
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long","email":"not-an-email"}'
# {"error":"Validation failed","issues":[{"path":"email","message":"Invalid email"}]}

# Good input
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long","email":"alice@example.com"}'
# {"id":1,"username":"alice","email":"alice@example.com"}

# Bad post: empty title
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"","body":"hello"}'
# {"error":"Validation failed","issues":[{"path":"title","message":"String must contain at least 1 character(s)"}]}

# Good post
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","body":"World"}'
# {"id":1,"userId":1,"title":"Hello","body":"World"}
```

---

## Experiments

### Experiment 1: Multiple validation errors at once

```bash
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"a","password":"short","email":"bad"}'
```

Zod reports *all* the failures in one response. The client sees the full list.

### Experiment 2: Trim and lowercase

```js
const signupSchema = z.object({
  username: z.string().min(3).max(30).trim().toLowerCase(),
  ...
});
```

`.trim()` removes leading/trailing whitespace. `.toLowerCase()` converts to lowercase. These are *transformations*: the parsed value is normalized. `req.validated.username` is the trimmed, lowercased version.

### Experiment 3: Default values

```js
const signupSchema = z.object({
  username: z.string().min(3),
  password: z.string().min(8),
  role: z.string().default('user'),
});
```

If the client doesn't send `role`, it's `'user'`. Defaults are applied during parse.

### Experiment 4: Coerce numbers

```js
const schema = z.object({
  age: z.coerce.number().int().min(0),
});
```

`z.coerce.number()` converts strings to numbers. `?age=25` becomes `25` (number). Useful for query string parsing (which is always strings).

### Experiment 5: Refine for custom logic

```js
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});
```

`.refine(fn, options)` adds custom validation. Here we check that the passwords match.

### Experiment 6: Reuse the error format

The `issues` array is a clean, stable contract. Frontend code can rely on it. `{ path, message }` is easy to display next to the corresponding form field.

---

## Summary

You now have validation. Bad input is rejected with a clear, structured error. Good input is normalized. The handlers are simpler.

This is the foundation of *input validation*. From here, every project that accepts input has a schema. The validation is centralized, reusable, and consistent.

In project 15, we will add error handling. We will catch errors from the database (constraint violations), the auth middleware (invalid tokens), and the handlers (unexpected exceptions). The error responses will be consistent.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

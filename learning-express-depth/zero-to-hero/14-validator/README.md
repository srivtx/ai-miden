# Project 14: The Validator

> *"Bad input should be rejected at the door. Don't let it reach the database."*

Projects 10-13 have us accepting any input. `POST /signup` accepts any `username`, `password`, `email`. Empty strings, 1MB strings, weird unicode — all accepted. The database does its best, but the result is unpredictable.

This project introduces **input validation**. We use **Zod** (or Joi, or Yup, or class-validator) — a schema validation library. We define a *schema* for each input (e.g., `username` must be 3-30 chars, `password` must be 8+ chars, `email` must be a valid email). We *parse* the input against the schema. If it fails, we return 400 with the validation errors. If it succeeds, we use the parsed value.

By the end, bad input is rejected with a clear error message. Good input is normalized (e.g., trimmed, lowercased).

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why validate? What happens if we don't?
2. [The Thought](./THOUGHT.md) — What is a schema? How does Zod work?
3. [The Build](./BUILD.md) — Line-by-line construction of the validation layer
4. [The Decisions](./DECISIONS.md) — Why Zod? Why not Joi? Why not hand-rolled?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A *schema* is a description of the shape of valid data. `z.string().min(3).max(30)` says "this must be a string, 3-30 characters." `z.object({ username: z.string().min(3) })` says "this must be an object with a `username` field that meets the string constraint." `schema.parse(input)` validates the input; if it fails, throws a `ZodError` with details. If it succeeds, returns the (possibly normalized) value. We use Zod because it's TypeScript-first, has a clean API, and is the most popular validation library in the Node ecosystem.

---

## The Code

```js
// server.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const knex = require('knex');
const { z } = require('zod');

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
  // ... same as project 13 ...
}

migrate().then(() => {
  app.listen(3000, () => console.log('Server listening on http://localhost:3000'));
});

// Schemas
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

app.post('/login', validate(loginSchema), async (req, res) => {
  const { username, password } = req.validated;
  // ... same as project 13 ...
});

app.post('/posts', authMiddleware, validate(postSchema), async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  res.status(201).json({ id, userId: req.user.userId, title, body });
});

// ... rest of the server ...
```

Setup:

```bash
npm install knex better-sqlite3 zod
node server.js
```

Test it:

```bash
# Bad input: short username
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"ab","password":"hunter2"}'
# {"error":"Validation failed","issues":[{"path":"username","message":"String must contain at least 3 character(s)"}]}

# Bad input: invalid email
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2","email":"not-an-email"}'
# {"error":"Validation failed","issues":[{"path":"email","message":"Invalid email"}]}

# Good input
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long","email":"alice@example.com"}'
# {"id":1,"username":"alice","email":"alice@example.com"}
```

The pain of "I accept any input" is solved. Bad input is rejected with a clear error. Good input is normalized.

---

## What You Will Have Learned

- What a schema is (a description of valid data)
- How Zod's `z.string()`, `z.number()`, `z.object()` work
- How to chain validations: `.min()`, `.max()`, `.email()`, `.regex()`, `.optional()`
- How `schema.parse(input)` validates and throws on failure
- How to write a `validate(schema)` middleware
- How to extract validation errors into a clean response
- Why validation is at the boundary, not in the database

These are the foundations of *input validation*. From here, every project that accepts input has a schema.

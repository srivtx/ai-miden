# The Problem

> *"Garbage in, garbage out. The garbage is the client's fault, but the response is yours."*

## Why Validate

In project 13, our handlers do basic checks:

```js
if (!username || !password) {
  return res.status(400).json({ error: 'username and password required' });
}
```

This catches *empty* inputs. It doesn't catch:

- `username = "a"` (too short)
- `username = "alice@bob"` (invalid characters)
- `password = "12345678"` (too short for some apps; we used 8+ in the schema above)
- `email = "not-an-email"` (no `@`)
- `email = "alice@example"` (no TLD)
- `body = { ... }` (a 1MB JSON object)
- `body = null` (missing body)
- `body = "string"` (a string instead of an object)
- `body = { "username": null }` (a null field)

Each of these is *valid* JSON, but invalid input. The database does its best, but the result is unpredictable:

- A 1-character username is stored.
- A "user" with no password can be created if we don't check.
- A "user" with a non-string username crashes the bcrypt compare.

We want to *reject* bad input *before* it reaches the database. With a clear error message. With a 400 status code. The client knows what they did wrong.

## What Pain Is This Solving?

Imagine the alternative. You deploy a signup endpoint. A user signs up with `username = ""` (empty). The database stores an empty string. Later, you try to display the username. It looks broken.

Or `username = "  alice  "` (with spaces). The database stores the spaces. Login fails because the user types `alice` (no spaces). Frustration.

Or `password = "a"` (one char). The user picks a weak password. Their account is hacked. Liability.

Or `email = "not-an-email"`. The user wants a password reset. The system sends the email to `not-an-email@nowhere`. It bounces. The user is confused.

Validation prevents all of this.

## The Deeper Problem: Trust

The client is *untrusted*. They could be a malicious attacker, a buggy frontend, or a well-meaning user with fat fingers. We must *never* trust the input.

Validation is the gate. It checks every input against a schema. If the input doesn't match, reject. If it matches, proceed.

The database is *also* untrusted. Even with validation, we should have constraints (NOT NULL, UNIQUE, foreign keys). Validation is the first line; database constraints are the second.

## What This Project Will Solve

This project will:

1. Add Zod as a dependency
2. Define schemas for each endpoint (`signupSchema`, `loginSchema`, `postSchema`)
3. Add a `validate(schema)` middleware
4. Apply the middleware to each protected route
5. Return 400 with detailed validation errors on failure

By the end, bad input is rejected with a clear, structured error. Good input is normalized (e.g., trimmed). The handlers are simpler (they trust `req.validated`).

## What This Project Will *Not* Solve

- **Database constraints** — we still have UNIQUE, NOT NULL, etc. Validation is the first line; the database is the second.
- **Authentication errors** — invalid tokens are handled by `authMiddleware`, not Zod.
- **Authorization errors** — RBAC (project 33) handles "you can't do this."
- **Custom validators** — we use built-in Zod methods. Custom logic is out of scope.
- **Internationalization of error messages** — we return English errors. Multi-language is out of scope.

## The Question This Project Answers

> *"How do I reject bad input with a clear error message?"*

If you can answer: "define a Zod schema, parse the input, return 400 with the issues on failure," you are ready for project 15.

# The Decisions

> *"Reject bad input at the door. Schema at the boundary. The rest of the code is simple."*

## Decision 1: Zod and not Joi / Yup / Ajv

**Alternatives**:
- **Joi** — older, mature, no TypeScript types
- **Yup** — similar to Zod, older
- **class-validator** — decorator-based, TypeScript-first
- **Ajv** — JSON Schema based, very fast, very verbose
- **Hand-rolled** — for 1-2 endpoints, fine

**Why Zod**: Modern, TypeScript-first, clean API, generates types, detailed errors. The de-facto standard in the Node ecosystem in 2024-2026.

**Trade-off**: Slightly newer than Joi. Some teams prefer Joi for its maturity. Both are fine.

## Decision 2: Validate `req.body` only

**Alternative**: Validate `req.query`, `req.params`, `req.headers` too.

**Why body only: We accept the most user input via body. Query and path are shorter and more constrained. We'll add validation for them in project 18 (Paginator) and 19 (Searcher) when we have more complex query strings.

**Trade-off**: We trust query and path parameters. For now, this is fine — they come from the URL, not from a free-form body. In production, you'd validate everything.

## Decision 3: `req.validated` and not `req.body`

**Alternative**: Overwrite `req.body` with the parsed value.

**Why `req.validated`: It's a clean signal: "this data has been validated and normalized." `req.body` is raw; `req.validated` is clean. Handlers should never read `req.body` after validation.

**Trade-off**: A new property. Easy to forget. We accept this for clarity.

## Decision 4: Structured error response

```json
{ "error": "Validation failed", "issues": [{ "path": "username", "message": "..." }] }
```

**Alternative**: Just a message string.

**Why structured: The frontend can map `issues` to form fields. The user sees exactly which field is wrong. The error is machine-readable.

**Trade-off**: A bit more code in the middleware. We accept this for usability.

## Decision 5: `.regex()` for username

```js
username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/)
```

**Why a regex: Usernames should be URL-safe (no spaces, no special chars). The regex restricts to alphanumeric + underscore. This prevents XSS (no `<script>` in usernames) and makes the username URL-safe.

**Trade-off**: Restrictive. Some users want spaces, dots, hyphens, etc. We can relax later.

## Decision 6: `min(8)` for password

**Alternative**: `min(12)`, no minimum, etc.

**Why 8: A common minimum. NIST recommends 8+ (with no other complexity requirements). We use 8 for now. We can require 12 in production.

**Trade-off**: 8 is not strong. For high-security apps, 12+ is better.

## Decision 7: `optional()` for email

**Alternative**: Required.

**Why optional: We added `email` in project 12's migration. Old users have `NULL`. We don't want to require them to update. We can require it for new signups in a future project.

**Trade-off**: Some users have no email. They can't reset their passwords (out of scope anyway).

## Decision 8: No sanitization (only validation)

We don't *modify* the input beyond what Zod's transformations do (e.g., `.trim()`, `.toLowerCase()`). We don't HTML-escape, we don't strip scripts.

**Why: The output is JSON. The frontend (or another client) is responsible for escaping when rendering. We store the data as-is. The database doesn't care.

**Trade-off**: A malicious user can store `<script>alert('xss')</script>` as their username. The frontend must escape it when rendering. We don't have a frontend in this project; in project 17 (REST Refactor) we'll discuss the rendering responsibility.

## Decision 9: No async validation

Zod schemas are synchronous. We don't have async validators (e.g., "check if email is unique in the database").

**Why: Most validation is synchronous (length, format, regex). For async validation (uniqueness), we check after Zod passes. The signup handler does the uniqueness check.

**Trade-off**: We do the uniqueness check in the handler, not in the schema. A bit more code. We accept this.

## Decision 10: Zod for both input and output

We use Zod for input validation. We could also use it for output (defining the response shape), but we don't.

**Why: Input validation is more important (reject bad data). Output is JSON, which is what the client expects. We don't enforce output shape — that's the client's problem.

**Trade-off**: A "contract" tool like tRPC or GraphQL enforces both. We use plain JSON, so we don't.

---

## What We Did Not Decide

- **Database constraints** — we still have UNIQUE, NOT NULL. Validation is the first line; the database is the second.
- **Authentication errors** — handled by `authMiddleware`, not Zod.
- **Authorization errors** — RBAC (project 33) handles "you can't do this."
- **Custom validators** — we use built-in Zod methods.
- **Internationalization** — we return English errors.
- **Async validation** (e.g., uniqueness in the database) — done in the handler.
- **Output validation** — we don't enforce response shape.
- **Sanitization** — we don't escape HTML, strip scripts, etc. (We do normalize with `.trim()`, `.toLowerCase()`.)

Each is a future decision.

---

## The Meta-Decision: Validation Is the Gate

For 13 projects, our handlers accepted any input. Empty strings, 1MB JSON, weird unicode — all accepted. The database did its best. The result was unpredictable.

Now the gate is *closed*. Every endpoint has a schema. Bad input is rejected with a clear, structured error. The database only sees valid data. The handlers are simpler — they trust `req.validated`.

This is the foundation of *robust APIs*. Every real API has validation. The patterns (Zod, schemas, middleware) are universal. The errors are consistent.

The next 26 projects will assume validation exists. The path diverges:

- **Error handling** (project 15): handle constraint violations, exceptions
- **Logging** (project 16): see what's happening
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance
- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse

The gate is closed. The path continues.

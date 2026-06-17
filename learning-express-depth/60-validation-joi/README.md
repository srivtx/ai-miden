# 60 — Validation with Joi

**New concept:** use a real validation library.

In project 5 we wrote a small validator. Joi is much more powerful. It handles dozens of types, formats, custom rules, error messages, defaults, transformations.

## Run it

```bash
npm install
node server.js
```

```bash
# Valid
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 25}'
# 201 { "name": "Alice", "email": "alice@example.com", "age": 25, "role": "user" }
# (role defaulted to "user" because we didn't send it)

# Invalid email
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "not-an-email"}'
# 422 { "error": "validation_failed", "errors": [{ "field": "email", "message": "..." }] }

# Multiple errors at once
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "A", "email": "bad", "age": 5}'
# 422 { "errors": [{ "field": "name", ... }, { "field": "email", ... }, { "field": "age", ... }] }

# Bad role
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "a@b.com", "role": "wizard"}'
# 422 { "field": "role", "message": "\"role\" must be one of [user, admin, moderator]" }
```

## How to think about it

Writing a validator by hand is fine for one project. When you have many projects, you want a library. Joi is the standard for Node. It has 50+ rules built in.

## How to build it (line by line)

```js
const userSchema = Joi.object({
  name: Joi.string().min(2).max(50).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(13).max(120),
  role: Joi.string().valid('user', 'admin', 'moderator').default('user'),
});
```

**Lines 9-14.** Define a schema. Each field has rules.

**`Joi.string().min(2).max(50).required()`** — string, between 2 and 50 chars, required.

**`Joi.string().email()`** — must be a valid email format.

**`Joi.string().valid('user', 'admin')`** — must be one of these values (enum).

**`default('user')`** — if the client doesn't send it, use 'user'.

```js
const { error, value } = schema.validate(req.body, { abortEarly: false });
```

**Line 23.** Validate the body.

**`abortEarly: false`** — collect ALL errors, don't stop at the first one.

```js
if (error) {
  const errors = error.details.map(d => ({
    field: d.path.join('.'),
    message: d.message,
  }));
  return res.status(422).json({ error: 'validation_failed', errors });
}
```

**Lines 24-30.** Format the errors and return 422.

## What we learned

1. Joi is a powerful validation library
2. Schemas are declarative: state the rules, Joi enforces them
3. `abortEarly: false` collects all errors
4. Defaults fill in missing fields
5. Joi handles: type, format, range, enum, pattern, custom rules, etc.
6. Alternatives: Zod, Yup, class-validator

## 🎉 End of 60 projects!

You've now built 60 small apps covering CRUD, real-time, file upload, search, rate limiting, scheduling, pub/sub, jobs, caching, analytics, auth, encryption, CSRF, CORS, security headers, i18n, and validation.

You have the structure. You can build anything.

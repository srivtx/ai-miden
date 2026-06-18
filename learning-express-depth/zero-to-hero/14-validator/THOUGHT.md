# The Thought

> *"A schema is a contract. The client promises to send data that matches. We promise to reject data that doesn't."*

## What a Schema Is

A *schema* is a description of the shape of valid data. It specifies:

- What fields are required
- What types they should be (string, number, boolean, etc.)
- What constraints they have (min length, max length, regex, etc.)
- What fields are optional

Example:

```js
const signupSchema = z.object({
  username: z.string().min(3).max(30),
  password: z.string().min(8),
  email: z.string().email().optional(),
});
```

This says: "the input must be an object with a `username` (string, 3-30 chars), a `password` (string, 8+ chars), and an optional `email` (string, valid email format)."

## Zod: A Schema Library

Zod is the most popular schema validation library in the Node ecosystem. It is:

- **TypeScript-first** — schemas generate types
- **Fluent API** — chainable methods
- **Composable** — schemas can be combined
- **Detailed errors** — `ZodError` has structured issue arrays

Other options:

- **Joi** — older, mature, no TypeScript types
- **Yup** — similar to Zod, older
- **class-validator** — decorator-based, requires TypeScript
- **Ajv** — JSON Schema based, very fast

We use Zod because it's modern, has a clean API, and generates TypeScript types (if you use TypeScript).

## The Zod API

### Primitive types

```js
z.string()      // must be a string
z.number()      // must be a number
z.boolean()     // must be a boolean
z.date()        // must be a Date
z.array(z.string())  // must be an array of strings
```

### String constraints

```js
z.string().min(3)        // at least 3 characters
z.string().max(30)       // at most 30 characters
z.string().length(10)    // exactly 10 characters
z.string().email()       // valid email format
z.string().url()         // valid URL
z.string().uuid()        // valid UUID
z.string().regex(/.../)  // matches a regex
z.string().trim()        // trim whitespace (also normalizes)
z.string().lowercase()   // convert to lowercase (also normalizes)
```

### Number constraints

```js
z.number().min(0)        // at least 0
z.number().max(100)      // at most 100
z.number().int()         // must be an integer
z.number().positive()    // must be positive
z.number().nonnegative() // must be non-negative
```

### Object schema

```js
const userSchema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  age: z.number().int().min(0).optional(),
});
```

The object has the specified fields. Optional fields can be missing.

### Validation

```js
const result = userSchema.parse({ username: 'alice', email: 'alice@example.com' });
// result: { username: 'alice', email: 'alice@example.com' }

try {
  userSchema.parse({ username: 'a' });
} catch (err) {
  // err.issues: [{ path: ['username'], message: 'String must contain at least 3 character(s)' }]
}
```

`schema.parse(input)` validates the input. If it fails, throws a `ZodError` with an `issues` array describing each failure.

`schema.safeParse(input)` returns `{ success, data, error }` instead of throwing.

## The `validate` Middleware

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

This is a *factory* that returns a middleware. The middleware:

1. Parses `req.body` against the schema
2. If valid, puts the result on `req.validated` and calls `next()`
3. If invalid, returns 400 with a structured error

We use `req.validated` (not `req.body`) in the handler. This is a clean way to distinguish validated data from raw input.

## Error Response Shape

```json
{
  "error": "Validation failed",
  "issues": [
    { "path": "username", "message": "String must contain at least 3 character(s)" },
    { "path": "email", "message": "Invalid email" }
  ]
}
```

This is a clean, structured error. The client knows exactly which field failed and why. The `issues` array is parallel — each issue is one failure.

## Common Confusions (read these)

**Confusion 1: "Why Zod and not Joi?"**
Joi is older and more mature. Zod is newer, TypeScript-first, and has a cleaner API. For a new project, Zod. For a legacy project, Joi.

**Confusion 2: "Why not just use `if` checks?"**
You could. For one endpoint, it's fine. For 10 endpoints with complex validation, Zod is cleaner. The schemas are reusable. The error messages are consistent.

**Confusion 3: "Should I validate at the database level too?"**
Yes. Validation is the first line; database constraints are the second. If validation is bypassed (e.g., a bug, a malicious client), the database catches it. Belt and suspenders.

**Confusion 4: "What if the body is not JSON?"**
`express.json()` parses JSON bodies. If the body is not JSON, `req.body` is `{}` (empty object). Zod's `z.object({...})` requires fields. So an empty body fails validation with "Required" errors. Good.

**Confusion 5: "What if the body is too large?"**
Express has a default body size limit of 100KB. Beyond that, it returns 413 (Payload Too Large). We can configure this with `express.json({ limit: '1mb' })`.

**Confusion 6: "What about query string and path parameter validation?"**
We validate `req.body` here. For query and path, we'd use the same Zod schemas, but parse `req.query` and `req.params`. Project 18 (Paginator) and 19 (Searcher) will do this.

**Confusion 7: "What about Zod's TypeScript types?"**
If you use TypeScript, `z.infer<typeof schema>` gives you the type. We don't use TypeScript in this path, but the same Zod schemas work.

**Confusion 8: "What is `req.validated` and not `req.body`?"**
We could put it back on `req.body`. The convention is to use a separate property to make it clear the data has been validated. `req.body` is raw; `req.validated` is clean.

## What We Are About to Build

A ~150-line Express app that:

1. Has the same auth and post flow as project 13
2. Has Zod schemas for signup, login, and post creation
3. Has a `validate(schema)` middleware
4. Returns 400 with structured errors on bad input
5. Uses `req.validated` in the handlers

The handlers are simpler: they trust `req.validated`. The validation is centralized in the middleware.

In [BUILD.md](./BUILD.md) we will go line by line.

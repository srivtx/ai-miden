# The Decisions

> *"Two lines of dispatch code. `URLSearchParams` does the hard work. We just wire it in."*

## Decision 1: `URLSearchParams` and not a hand-rolled parser

**Alternative**: Split on `&`, then on `=`, then URL-decode each part.

**Why we didn't**: `URLSearchParams` is a standard library class. It handles URL encoding (`%20` → space, etc.), edge cases (empty values, missing values), and is fast. It is available in Node and the browser, so the code is portable. There is no reason to write our own.

**Trade-off**: None. We use the standard library.

## Decision 2: `Object.fromEntries` for the plain object

**Alternative**: Manually iterate the `URLSearchParams` and build an object.

**Why we didn't**: `Object.fromEntries` is the standard way to convert an iterable of `[key, value]` pairs to an object. One line, clear intent. We use it.

**Trade-off**: Multi-value queries (`?tag=a&tag=b`) lose all but the last value. We don't need multi-value yet. If we do (project 18 or 19), we'll iterate manually.

## Decision 3: Mutate `req` to add `query`

**Alternative**: Pass the query as a separate argument to the handler.

**Why we didn't**: Mutation is the convention. Express, Fastify, Hono, Koa — all mutate `req` to add `req.query`, `req.body`, `req.params`, etc. Handlers receive a single `req` object that has everything. It's clean.

**Trade-off**: Mutation can be confusing if you don't expect it. But it is universal, so the surprise is small.

## Decision 4: Don't change `req.url`

**Alternative**: Strip the query from `req.url` so `req.url` is the path only.

**Why we didn't**: The original `req.url` is useful for logging, debugging, and proxies. We don't want to lose it. We *add* `req.query` and use a local `path` variable in the dispatch. The handler can still see `req.url` if it needs to.

Some frameworks (Express) add `req.path` (the URL without the query) and `req.originalUrl` (the original). We could do the same. We don't, to keep the example small.

## Decision 5: Split on the first `?` only

**Alternative**: `req.url.split('?')` splits on *every* `?`.

**Why this is fine**: URL syntax allows only one `?`. The path is everything before the first `?`, and the query is everything after. There can't be more than one. (The fragment uses `#`, not `?`.)

**Trade-off**: None. URL syntax is unambiguous.

## Decision 6: No multi-value support

**Alternative**: `?tag=a&tag=b` → `{ tag: ['a', 'b'] }`.

**Why we didn't**: We don't need it. When we do (project 18 or 19), we'll add it. YAGNI.

**Trade-off**: Right now, `?tag=a&tag=b` keeps only `'b'`. That's wrong for any real API that uses multi-value, but we don't have that API yet.

## Decision 7: No type coercion

**Alternative**: `?limit=10` becomes `{ limit: 10 }` (number).

**Why we didn't**: The query string is text. We don't know if `limit` is meant to be a number, a string, or a boolean. The handler can convert: `parseInt(req.query.limit, 10)`. We leave the type as string.

**Trade-off**: Handlers must remember to convert. For a real API, validation (project 14) will enforce types. For now, string is fine.

## Decision 8: No validation of query values

**Alternative**: Reject `?role=foo` with `400 Bad Request` because `foo` is not a valid role.

**Why we didn't**: We don't have a list of valid roles (yet). And validation is a project 14 concern. Right now, an unknown value just returns an empty list. The client knows.

**Trade-off**: A stricter API would reject unknown values. We don't, because we haven't been asked to.

## Decision 9: No query string length limit

**Alternative**: Reject query strings longer than 1KB.

**Why we didn't**: We don't have a problem with huge query strings. We will, when we add filtering. We can add a limit later. Node has a default `--max-http-header-size` of 16KB, which includes the URL.

**Trade-off**: For now, no protection. We'll add it in project 14 (Validator) or 24 (Rate Limiter).

## Decision 10: `URL` class is overkill

**Alternative**: `new URL(req.url, 'http://localhost')` and use `url.pathname` and `url.searchParams`.

**Why we didn't**: `URL` is great, but it requires a base URL for relative URLs (and `req.url` is relative). And `URL.pathname` returns the path with the query stripped, but it also percent-encodes characters, which can surprise. We use the simpler `split('?')` + `URLSearchParams` approach. It's also more explicit about what we're doing.

**Trade-off**: For relative URLs, `URL` is awkward. The `split` approach is direct.

---

## What We Did Not Decide

- **Multi-value query** — YAGNI
- **Nested query (`?user[name]=Alice`)** — out of scope, not a standard
- **Type coercion** — handler's job
- **Validation** — project 14
- **Sorting** — project 18
- **Field selection** — project 18
- **Pagination** — project 18
- **Rate limiting on expensive queries** — project 24

Each is a future decision. We will face them when their absence hurts.

---

## The Meta-Decision: The Dispatch is the Right Place for This Logic

The query string is a property of the *request*, not of any specific route. It applies to *every* request. So the right place to parse it is the *dispatch* — the function that handles every request — not in each handler.

This is the *separation of mechanism from policy* we keep coming back to:

- **Mechanism** (in the dispatch): parse the URL, parse the query, look up the route, dispatch to the handler.
- **Policy** (in the handler): decide what to do with the parsed query — filter, sort, paginate.

The mechanism changes only when the protocol changes (e.g., adding path parameters in a future project). The policy changes with every new endpoint.

Putting the parsing in the dispatch means: every handler gets `req.query` for free. The handler is small. The dispatch does the boring work.

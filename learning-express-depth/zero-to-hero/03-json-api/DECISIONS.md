# The Decisions

> *"JSON is a string. `JSON.stringify` makes it a string. `JSON.parse` makes it an object. The bridge is the only magic."*

## Decision 1: JSON over other formats (XML, YAML, MessagePack)

**Alternatives**:
- **XML** — older, more verbose, used in SOAP, banking, etc.
- **YAML** — human-friendly, used in config files (Kubernetes, GitHub Actions)
- **MessagePack** — binary, faster, smaller
- **Protocol Buffers / gRPC** — strongly typed, very fast, used for service-to-service

**Why JSON**: It is the lingua franca of HTTP APIs. Every language has a JSON parser. Every frontend knows it. It is human-readable. It is small enough for almost everything.

**Trade-off**: For high-performance service-to-service communication, gRPC or MessagePack is faster. We don't have that pain yet.

## Decision 2: `JSON.stringify` and `JSON.parse` (built-in) over a library

**Alternatives**: `lodash`, `serialize-javascript`, `flatted` (for circular refs).

**Why built-in**: It is fast, ubiquitous, and standard. No dependency. No version-skew risk.

**Trade-off**: No support for circular references, `Date` (becomes string), `undefined` (omitted), or other JS-only types. For an API, you usually want *clean* data anyway — circular structures are a sign of bad design at the API boundary. We will deal with this when it hurts (project 17, REST Refactor).

## Decision 3: Helper function, not method on `res`

**Alternative**: Mutate `res` to add a `res.json` method (like Express does).

**Why a free function**: It is *less code* and *less framework-like*. We are still in the "raw Node" phase. Mutating the response object is a project 07 (Framework Pivot) concern.

**Trade-off**: We have to pass `res` to the helper every time. Express's `res.json(body)` is cleaner. We accept the trade-off for now.

## Decision 4: Status as an argument to `json`

**Alternative**: `json(res, body)` with status set separately.

**Why pass status**: Most responses have a status code. Forcing it into the helper signature makes it explicit. You can't forget to set it.

**Trade-off**: For `204 No Content` (no body), we can't use the helper — we need `res.end()` with no body. So the helper is for "responses with a JSON body." For 204, we use the raw `res.end()`. This is fine.

## Decision 5: `201 Created` for `POST` that creates

**Alternative**: Always return `200 OK`.

**Why `201`**: It is the convention. REST APIs use it. It signals "a new resource was created." Clients can use it to trigger specific behavior (e.g., "show a success toast for created resources, but not for updates").

**Trade-off**: None. The status code is a small thing, but using it correctly is a sign of professionalism.

## Decision 6: JSON for errors, including 404

**Alternative**: Plain text for errors, JSON for success.

**Why JSON for errors**: Consistency. The client always parses JSON. No special case for errors. The error shape can be standardized: `{ error: '...' }`, or `{ error: { code: 'NOT_FOUND', message: '...' } }` (which we'll do in project 15).

**Trade-off**: A 404 page in a browser will display `{"error":"Not Found"}` instead of a nice HTML page. That's OK for an API (the client is a program, not a human). For an HTML-returning server, you'd serve an HTML 404 page. We are API-first; we return JSON.

## Decision 7: No pretty-printing in production

`JSON.stringify(body, null, 2)` adds whitespace, which is human-friendly but adds bytes. For production, we don't pretty-print. For development, we sometimes do. In this project, we use compact JSON. We'll add a dev/prod toggle in a later project (probably project 39, Observability).

## Decision 8: No streaming

For huge JSON responses (say, 10MB), `JSON.stringify(obj)` builds the whole string in memory. That's bad.

The right way is to *stream* the JSON: write `{`, then each item, then `}`, in chunks. This keeps memory low.

We don't have this pain yet. Our responses are small. We'll address it in project 18 (Paginator) and project 51 (Streams).

## Decision 9: No `null` for missing fields

If a user has no email, do we return `{ id: 1, name: 'Alice', email: null }` or `{ id: 1, name: 'Alice' }` (omit email)?

**Convention varies.** Some teams prefer explicit `null` (the field exists, the value is null). Some prefer omission (the field doesn't apply).

**We use omission** in this project for simplicity. The convention will be standardized in project 17 (REST Refactor).

## Decision 10: `application/json` is the only Content-Type we send

We don't send `text/html`, `text/plain`, `image/png`, etc. We're an API. JSON is the lingua franca. If we later need to send files or HTML, we'll add those content types in the appropriate projects (project 20 for files, project 39 for observability dashboards).

---

## What We Did Not Decide

- **Pagination shape** (page-based vs. cursor-based) — project 18
- **Filtering shape** (query string vs. request body) — project 04
- **Sorting shape** (`?sort=name` vs. `?sort=-name`) — project 18
- **Field selection** (`?fields=id,name`) — project 18
- **Error code standardization** (`{error: {code, message}}`) — project 15
- **API versioning** (`/v1/users` vs. `/users?v=1`) — project 17
- **HATEOAS** (links in responses) — out of scope for this path
- **GraphQL** — out of scope, mentioned only to acknowledge it exists

Each of these is a future decision. We will face them when their absence hurts.

---

## The Meta-Decision: This Project Changes the Wire Format, Nothing Else

The router is unchanged. The dispatch is unchanged. The handler signature is unchanged. We added one helper and changed the *bodies* of the handlers.

This is the pattern for the next several projects: small, focused changes that solve a specific pain. The shape of the system stays the same; the *details* get more sophisticated. By project 40, the details will be enormous (auth, validation, transactions, websockets, microservices). The shape will be the same. That is the power of a good architecture.

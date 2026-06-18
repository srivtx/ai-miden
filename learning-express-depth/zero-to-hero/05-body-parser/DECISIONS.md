# The Decisions

> *"The body is a stream. We listen for chunks. We wait for the end. Then we parse."*

## Decision 1: `Buffer.concat` and not streaming JSON parser

**Alternative**: Use a streaming JSON parser like `JSONStream` or `stream-json`.

**Why we didn't**: Our bodies are small. Loading the whole body into memory is fine. Streaming JSON is more code and only matters for multi-megabyte bodies. We'll address this in project 18 (Paginator) or 20 (Uploader).

**Trade-off**: A malicious client can send a 10 GB body. We accumulate it all. We'll add a size limit in project 14 (Validator).

## Decision 2: `try`/`catch` around `JSON.parse`

**Alternative**: Trust the client. Don't catch.

**Why we did**: `JSON.parse` throws on invalid JSON. If we don't catch, the response is never sent and the client hangs. Always catch.

**Trade-off**: We return `400 Bad Request` for any parse error. We don't tell the client *why* the JSON is invalid (e.g., "missing comma at position 42"). For a real API, you'd want better error messages. We don't, because we haven't been asked to.

## Decision 3: Empty body → `req.body = {}`

**Alternative**: Leave `req.body` as `undefined` when the body is empty.

**Why we set it to `{}`**: Handlers can safely do `req.body.name` (which would be `undefined` for missing fields). If we left it `undefined`, handlers would have to check `if (req.body) ...` everywhere. The empty object is a friendlier default.

**Trade-off**: A handler can't tell the difference between "no body sent" and "body is `{}`." We don't care, because we don't have that distinction in our API.

## Decision 4: Dispatch inside the `'end'` listener

**Alternative**: Use Promises and `await req.text()` in an async dispatch.

**Why we didn't**: Promises add complexity. The `'end'` event is the natural way to express "do this when the body is done." Node's API is event-based; we use it directly.

**Trade-off**: The code is callback-based, not Promise-based. Project 07 (Framework Pivot) will use Express, which is callback-based internally but exposes an async-friendly API to handlers.

## Decision 5: Read the body for every request, even `GET`

**Alternative**: Only read the body for `POST`/`PUT`/`PATCH`.

**Why we don't optimize**: The cost of listening for `'data'` events is near-zero (it returns immediately if there's no data). Optimizing is premature. The body is read; if it's empty, `req.body = {}` and the handler doesn't care.

**Trade-off**: We do a tiny bit of unnecessary work for `GET`. It's not a problem.

## Decision 6: Don't check `Content-Type`

**Alternative**: Only parse as JSON if `Content-Type: application/json`. Otherwise, leave the body as a string or an empty object.

**Why we don't**: We only have one content type we care about: `application/json`. Other content types are out of scope. If the client sends `text/plain`, we try to parse as JSON and fail with 400. That's the right behavior — we don't support `text/plain`.

**Trade-off**: A client sending `Content-Type: text/plain` with a valid plain-text body gets a 400. That's correct, because we only support JSON.

## Decision 7: No size limit

**Alternative**: Reject bodies larger than, say, 1 MB.

**Why we don't**: We don't have huge bodies. We don't have a problem yet. We'll add a limit when we have uploads (project 20) or untrusted input (project 14).

**Trade-off**: A malicious client can OOM the server. We accept this risk for now.

## Decision 8: Don't listen for `'error'`

**Alternative**: Listen for the `'error'` event on `req` and clean up.

**Why we don't**: We don't have a problem with client disconnects. We will, when we have real users. We'll add it in project 15 (Error Wall).

**Trade-off**: If the client disconnects mid-body, the response is never sent, the connection is closed, and we have a small leak (the chunks array is garbage-collected, but the connection lingers). We accept this.

## Decision 9: Buffers, not strings

**Alternative**: Concatenate chunks as strings: `chunks.push(chunk.toString())`.

**Why we use Buffers**: Chunks arrive as Buffers. Converting each to a string and concatenating strings works, but it's slightly slower and can fail on multi-byte UTF-8 characters that span chunk boundaries. Concatenating Buffers and decoding once is correct.

**Trade-off**: Slightly more code (`.toString('utf8')` at the end). Worth it for correctness.

## Decision 10: No timeout

**Alternative**: Reject requests that take more than 30 seconds to send the body.

**Why we don't**: Node has a default `server.timeout` of 0 (no timeout). We don't need to set one. We'll discuss timeouts in project 14 (Validator) or 24 (Rate Limiter).

**Trade-off**: A malicious client can open a connection, send headers, then never send the body. The connection lingers. We accept this for now.

---

## What We Did Not Decide

- **Streaming JSON** — YAGNI
- **Other content types** (`multipart/form-data`, `application/x-www-form-urlencoded`) — out of scope
- **Size limits** — out of scope
- **Validation** — project 14
- **Async handlers** — the handlers are still synchronous. We don't have async work yet.
- **Body parsing middleware** — we have body parsing *built into* the dispatch. In project 07, this will move into a middleware.

Each is a future decision.

---

## The Meta-Decision: The Dispatch is Becoming a Framework

Look at the dispatch now. It:

- Parses the URL (path + query)
- Reads the body (chunks → JSON)
- Looks up the route
- Dispatches to the handler
- Handles errors (400 for invalid JSON, 404 for no route)

This is a *lot* of behavior in one function. It's about 25 lines. It is the *kernel* of a web framework.

In project 07, we will adopt Express, which is essentially this dispatch plus middleware plus helpers. The patterns we built by hand will be Express's internals. You'll understand Express because you built its core.

The dispatch is the framework. The handler is the application. The boundary is `req` and `res`.

This is the moment to notice: the architecture is stable. The handler signature `(req, res) => { ... }` will not change in the next 35 projects. The dispatch will get more sophisticated (auth, validation, error handling, logging, real-time), but the handler interface is the same.

That's the power of a small, well-defined contract. Everything else is decoration.

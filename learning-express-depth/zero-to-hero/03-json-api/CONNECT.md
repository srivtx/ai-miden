# The Connect

> *"We can speak JSON. We cannot yet read it from the client."*

This API is now correct. It returns JSON for every response, including errors. It uses the right status codes. A frontend can `fetch('/users')` and get a real array of user objects.

But this API is *half* of a real API. We can *send* JSON, but we cannot *receive* it. The client can give us JSON, but we throw it away.

## What Works

- All responses are JSON.
- Status codes are correct (`200`, `201`, `404`).
- The `json()` helper enforces the `Content-Type` header.
- The router is unchanged. The handler structure is unchanged.
- A frontend can consume this API today.

## What Doesn't Work

### 1. We can't filter

```bash
curl 'http://localhost:3000/users?role=admin'
# {"error":"Not Found"}
```

We discussed this in project 02. The query string is part of `req.url`, and our route lookup uses the full URL. To support filtering, we need to:

1. Parse the query string (`?key=value&key2=value2`)
2. Strip it from `req.url` before the route lookup
3. Pass it to the handler so it can filter

This is project 04.

### 2. We can't accept JSON bodies

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve"}'
# (no body read)
```

The server receives the body in the request stream but never reads it. The body is silently discarded. The handler has no idea what the client sent.

**The pain**: Real APIs accept input. To accept JSON, we need to *parse* the request body. This is project 05.

### 3. We have no path parameters

```bash
curl http://localhost:3000/users/2
# {"error":"Not Found"}
```

We registered `GET /users/1` for Alice. We don't have `/users/2` for Bob. The router matches *exact* paths. To support `/users/<any id>`, we need path parameters.

**The pain**: When we have one user, we want to fetch it by id. We can't register `/users/1`, `/users/2`, etc. by hand. We need `/users/:id` to match any value.

This is project 11 (Foreign Key) or 17 (REST Refactor).

### 4. We have no persistence

`/users/1` always returns Alice. `/users` always returns the same 3 users. Restart the server, nothing changes. We have no way to *create* a real user.

**The pain**: A real API has data that survives restarts. We need a database. This is project 10 (SQLite Notebook).

### 5. We have no auth

Anyone can hit any endpoint. There is no concept of "logged in" or "not logged in."

**The pain**: Most APIs have private data (your messages, your account). We need authentication. This is project 08 (Bcrypt Vault).

### 6. We have no validation

The `POST /users` handler ignores the body. But if it *did* read it, it would accept any JSON — including malformed data (`{name: 123}`, `{}`, `{name: "<script>alert('xss')</script>"}`).

**The pain**: Bad input should be rejected. We need validation. This is project 14 (Validator).

### 7. We have no error handling

If our `json()` helper throws (e.g., a circular reference in the body), the response is never sent. The client hangs.

**The pain**: Real APIs fail. We need to catch errors. This is project 15 (Error Wall).

### 8. We have no logging

When a request comes in, we don't log it. We don't know who hit what, when. Debugging is impossible.

**The pain**: A production server must be observable. This is project 16 (Logger).

### 9. We have no CORS

A browser on `localhost:5173` (a Vite dev server) cannot call our server on `localhost:3000` — the browser blocks it. The browser will say "CORS error."

**The pain**: A frontend on a different origin can't talk to our API. We need CORS headers. This is project 57 (CORS).

### 10. We have no real-time

Every request is a one-shot. The server cannot push to the client. If a chat message arrives for a user, the server has no way to notify them.

**The pain**: Modern apps are real-time. This is project 28 (WebSocket).

---

## What This Project Forbids Us From Doing

This server cannot:

- Accept any input from the client (no body parsing)
- Filter results based on the request (no query string)
- Match dynamic paths (no path parameters)
- Persist data (no database)
- Authenticate users (no sessions or tokens)
- Validate input (no schema check)
- Handle errors gracefully (no try/catch around handlers)
- Be observed (no logging)
- Be called from a browser frontend on a different origin (no CORS)
- Push updates to the client (no WebSocket)

We will systematically address each of these.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 04 | The Query-String Reader | "I want `?role=admin` to filter results." |
| 05 | The Body Parser | "I want to read the JSON the client sent me." |
| 06 | The Cookie Jar | "I want to remember who the user is across requests." |
| 07 | The Framework Pivot + Session | "I want middleware: a way to run code before every handler." |
| 08 | The Bcrypt Vault | "I want to store passwords securely." |

Each is a small, focused change. Each answers a real pain. The path continues.

---

## What You Should Do Now

1. **Read the code.** Notice that the router is unchanged. Only the handlers and the helper changed.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Add a new endpoint** that returns JSON. Pick something that matters to *you* — maybe `/todos`, `/posts`, `/books`. Use the `json()` helper. Return an array of objects.
4. **Try to send a JSON body** to `POST /users`. Notice that it's discarded. Feel the pain.
5. **When you are ready**, move to [Project 04: The Query-String Reader](../04-query-reader/).
6. **If anything is unclear**, do not proceed. JSON is the wire format for everything in this path. It must be solid.

---

## A Note on the Bigger Picture

You now have a *real* API. It speaks JSON. It uses correct status codes. It can be consumed by any modern client. Most of the "hard" things in this path are *not* HTTP or JSON — they're auth, validation, real-time, scale. The HTTP layer is small.

This is the foundation. From here, the path diverges: input (body parsing, validation, auth), output (pagination, search, real-time), and operations (logging, observability, deployment).

Stay with the path. The next 37 projects will turn this 60-line server into a production-ready system. You will never be confused by HTTP or JSON again.

# The Connect

> *"We can filter. We can sort by reordering the array. We cannot yet accept input."*

This project added query string support. The pain of "I cannot filter" is solved. The router matches the path; the query is a clean object on `req.query`.

But this project also revealed a *new* pain: we can read the query, but we still can't read the *body*. The client can `GET /users?role=admin`, but they cannot `POST /users` with a JSON body. The body is silently discarded.

## What Works

- The router matches the path (not the full URL).
- The query is parsed once, in the dispatch.
- Handlers get `req.query` as a clean object.
- Filtering is a one-line addition to the handler.
- The convention is universal: query in URL, body in payload.

## What Doesn't Work

### 1. We can't accept request bodies

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve", "email": "eve@example.com"}'
# (no body read; the handler doesn't see what was sent)
```

The body is in the request *stream*. We never read it. To accept input, we need to *consume the stream* and parse it as JSON.

**The pain**: A real API accepts input. This is project 05.

### 2. We have no path parameters

```bash
curl http://localhost:3000/users/2
# {"error":"Not Found"}
```

The path is exact-match. `/users/1` and `/users/2` are different routes. We don't have `/users/:id` style matching.

**The pain**: When we have a database of users and want to fetch one by id, we can't register every id. We need path parameters.

This is project 11 (Foreign Key) or 17 (REST Refactor).

### 3. We have no persistence

The `USERS` array is in memory. Restart the server, and the data is gone. There is no way to *create* a user that survives a restart.

**The pain**: A real API has data. We need a database. This is project 10 (SQLite Notebook).

### 4. We have no auth

Anyone can hit any endpoint. There is no concept of "logged in."

**The pain**: A real API has private data. We need authentication. This is project 08 (Bcrypt Vault).

### 5. We have no validation

`?role=foo` returns an empty list. We don't reject obviously bad input.

**The pain**: Strict APIs reject bad input with `400`. We need validation. This is project 14 (Validator).

### 6. We have no error handling

If `URLSearchParams` fails (it won't, but if some part of the parsing throws), the response is never sent. The client hangs.

**The pain**: Real APIs fail. We need error handling. This is project 15 (Error Wall).

### 7. We have no logging

We don't log requests. We can't answer "what was the most popular query in the last hour?"

**The pain**: Production needs observability. This is project 16 (Logger).

### 8. We have no middleware

Logging, auth, error handling — all are *cross-cutting concerns*. They apply to every request. Putting them in the dispatch is one option, but a *middleware* chain is more flexible.

**The pain**: As the server grows, we'll want to compose behaviors. This is project 07 (Framework Pivot).

### 9. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: Frontends need CORS. This is project 57 (CORS).

### 10. We have no real-time

Every request is one-shot. The server cannot push.

**The pain**: Real-time is project 28 (WebSocket).

---

## What This Project Forbids Us From Doing

This server can:

- Read filters from the URL
- Return JSON
- Handle multiple routes

It cannot:

- Accept a JSON body
- Match dynamic paths
- Persist data
- Authenticate users
- Validate input
- Handle errors gracefully
- Be observed
- Be called from a browser on a different origin
- Push updates to clients

Each of these is a future project. The path continues.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 05 | The Body Parser | "I want to read the JSON the client sent me." |
| 06 | The Cookie Jar | "I want to remember who the user is across requests." |
| 07 | The Framework Pivot + Session | "I want middleware: code that runs before every handler." |
| 08 | The Bcrypt Vault | "I want to store passwords securely." |

Project 05 is the natural next step: the body is the *other half* of the input. Query is in the URL; body is in the payload. We will read the body, parse it as JSON, and put it on `req.body`. The pattern is the same as `req.query`.

---

## What You Should Do Now

1. **Read the code.** Notice that the dispatch got *one* new line (split + parse) and the handler got *one* new branch (filter on `req.query.role`). That's it.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Add another filter.** Try `?name=Alice` and see if you can match by name. (Hint: case-sensitive by default; use `.toLowerCase()` if you want case-insensitive.)
4. **Try to send a body** with `curl -X POST -d '{...}'`. Notice that it's discarded. Feel the pain.
5. **When you are ready**, move to [Project 05: The Body Parser](../05-body-parser/).
6. **If anything is unclear**, do not proceed. The query string is used in every API. It must be solid.

---

## A Note on the Bigger Picture

You now have a *filterable* API. The same handler can serve many clients with different filters. This is the foundation of *data APIs*. Every data API from here on will use `req.query` for filters, sort, paginate, and search.

The next project will add *body parsing* — the ability to *send* data, not just filter it. From there, the API becomes truly *interactive*: clients can create users, edit posts, send messages. The path continues.

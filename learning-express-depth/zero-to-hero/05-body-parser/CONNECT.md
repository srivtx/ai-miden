# The Connect

> *"We can read the body. We cannot remember who sent it."*

This project added body parsing. The pain of "I cannot accept input" is solved. The body is read, parsed as JSON, and put on `req.body`. Handlers can use it.

But this server is still *amnesiac*. Every request is a stranger. The server has no idea if the same client sent the previous request. There is no concept of "logged in" or "not logged in." There are no sessions.

## What Works

- The router matches the path.
- The query is parsed in the dispatch.
- **The body is read, parsed, and put on `req.body`.**
- The handler can use `req.body` to create resources.
- Invalid JSON returns 400.
- Empty body becomes `{}` (so handlers don't crash).

## What Doesn't Work

### 1. We can't recognize returning users

```bash
curl -X POST http://localhost:3000/users -d '{"name": "Eve"}'
# {"id":3,"name":"Eve","role":"user"}

curl -X POST http://localhost:3000/users -d '{"name": "Mallory"}'
# {"id":4,"name":"Mallory","role":"user"}
```

The server doesn't know these are two different clients (well, it does, by IP, but it doesn't *use* that). It doesn't know if the same client is sending multiple requests. There is no identity.

**The pain**: A real API has users. Users have sessions. We need cookies. This is project 06.

### 2. We can't authenticate

There is no `Authorization` header handling. Anyone can `POST /users` and create a user. There is no login, no signup, no "this endpoint requires auth."

**The pain**: A real API has private endpoints. We need authentication. This is project 08.

### 3. We can't match dynamic paths

```bash
curl http://localhost:3000/users/2
# {"error":"Not Found"}
```

We registered `GET /users/1` for Alice (in project 03). We don't have `/users/2` for Bob. The router matches exact paths.

**The pain**: We need path parameters (`/users/:id`). This is project 11 (Foreign Key) or 17 (REST Refactor).

### 4. We have no validation

`{"name": 123}` is accepted. `{"name": ""}` is accepted. `{}` is accepted. We don't reject bad input.

**The pain**: Strict APIs reject bad input with 400. We need validation. This is project 14 (Validator).

### 5. We have no error handling for handler errors

If the handler throws (e.g., `USERS.push` fails for some reason), the response is never sent. The client hangs. We only catch JSON parse errors; we don't catch handler errors.

**The pain**: Real APIs fail. We need to catch handler errors. This is project 15 (Error Wall).

### 6. We have no logging

We don't log requests. We can't answer "who hit what, when?"

**The pain**: Production needs observability. This is project 16 (Logger).

### 7. We have no persistence

The `USERS` array is in memory. Restart the server, the data is gone. We have no way to *save* the data.

**The pain**: A real API has data that survives restarts. We need a database. This is project 10 (SQLite Notebook).

### 8. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: Frontends need CORS. This is project 57 (CORS).

### 9. We have no real-time

Every request is one-shot. The server cannot push.

**The pain**: Real-time is project 28 (WebSocket).

### 10. We have no middleware

The dispatch is doing a *lot* of work: query parsing, body parsing, error handling, route lookup. As we add more (logging, auth, validation), the dispatch will get huge. The right pattern is *middleware* — small functions that compose.

**The pain**: Composition over monolith. This is project 07 (Framework Pivot).

---

## What This Project Forbids Us From Doing

This server can:

- Read the body
- Parse as JSON
- Use `req.body` in handlers
- Handle invalid JSON

It cannot:

- Remember who the user is across requests
- Authenticate users
- Match dynamic paths
- Validate input
- Handle handler errors gracefully
- Log requests
- Persist data
- Be called from a browser on a different origin
- Push updates

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 06 | The Cookie Jar | "I want to remember who the user is across requests." |
| 07 | The Framework Pivot + Session | "I want middleware: code that runs before every handler." |
| 08 | The Bcrypt Vault | "I want to store passwords securely." |
| 09 | The JWT | "I want stateless auth that scales across servers." |

Project 06 is the natural next step: cookies are the *bridge* between stateless HTTP and stateful applications. They let the server recognize a returning client.

---

## What You Should Do Now

1. **Read the code.** Notice the dispatch is now async. The handler is unchanged in shape — it just gets `req.body` for free.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try to send a malformed body.** See the 400. Then try a valid body. See the 201.
4. **Restart the server.** Notice the new users are gone. Feel the pain of "no persistence."
5. **Try to call the server twice in a row.** Notice the server doesn't recognize you. Feel the pain of "no identity."
6. **When you are ready**, move to [Project 06: The Cookie Jar](../06-cookie-jar/).
7. **If anything is unclear**, do not proceed. The body is the primary way clients send data. It must be solid.

---

## A Note on the Bigger Picture

You now have a *bidirectional* API. Clients can read (via the query) and write (via the body). The server can return JSON, parse JSON, and respond with appropriate status codes.

But the server is still *amnesiac*. It treats every request as a new event. There is no continuity. There is no identity. The next project — cookies — is the first step toward *state*. From here, the API becomes *personal*: it knows who you are, what you've done, what you can do.

Cookies are ancient (they predate JavaScript), but they are the foundation of every authenticated web app. We will build them from scratch in project 06, so you understand what `Set-Cookie` actually does.

# The Connect

> *"The HTTP substrate is complete. We can route, parse, identify. Now we need a framework, a database, and a future."*

This project added cookies and sessions. The pain of "I cannot recognize returning users" is solved. The server can now:

- Set a cookie via `Set-Cookie`
- Read cookies via `Cookie`
- Look up session data by the session ID in the cookie

The HTTP substrate — the layer that handles raw HTTP — is *done*. We have:

- A router (project 02)
- JSON I/O (project 03)
- Query strings (project 04)
- Body parsing (project 05)
- Cookies and sessions (project 06)

Every project from here will build *on top of* this substrate.

## What Works

- The router matches paths and dispatches to handlers.
- The query is parsed in the dispatch.
- The body is read and parsed as JSON.
- The cookies are parsed into `req.cookies`.
- The session is stored in an in-memory `SESSIONS` Map.
- The server can recognize returning users via `req.cookies.sessionId`.

## What Doesn't Work

### 1. The dispatch is too long

The dispatch is now ~30 lines. It does:
- URL parsing
- Cookie parsing
- Body parsing (with error handling)
- Route lookup
- 404 fallback

If we add more — validation, auth checks, logging, error handling, request IDs — it'll be 100 lines. We need a *framework* to handle the boilerplate.

**The pain**: Reinventing middleware by hand. This is project 07.

### 2. We don't store anything durable

`SESSIONS` is in memory. Restart the server, sessions are gone. `USERS` is gone too. We have no way to persist data across restarts.

**The pain**: A real app has data that survives restarts. We need a database. This is project 10 (SQLite Notebook).

### 3. We don't validate input

`POST /login` accepts any body, including `{}`. The username is just `req.body.username`, which could be `undefined`, a number, an object, etc.

**The pain**: Bad input should be rejected. We need validation. This is project 14 (Validator).

### 4. We don't hash passwords

`POST /login` just stores whatever the client sends as the username. There's no password. Anyone can log in as anyone.

**The pain**: We need real auth with passwords. This is project 08 (Bcrypt Vault).

### 5. We don't sign cookies

A user can edit their cookie. If they set `sessionId=2`, they become user 2. We don't sign cookies, so we can't tell if a cookie is authentic.

**The pain**: Tamper-proof tokens. We need JWT. This is project 09.

### 6. We have no error handling for handler errors

If `SESSIONS.set(...)` throws (it won't, but if some handler throws), the response is never sent.

**The pain**: Real APIs fail. We need error handling. This is project 15 (Error Wall).

### 7. We have no logging

We don't log requests. We can't answer "who hit what, when?"

**The pain**: Production needs observability. This is project 16 (Logger).

### 8. We have no real-time

Every request is one-shot. The server cannot push.

**The pain**: Real-time is project 28 (WebSocket).

### 9. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: Frontends need CORS. This is project 57.

### 10. We have no tests

We have no way to verify the server works. We're running it and clicking around. That's not sustainable.

**The pain**: Tests are project 36.

---

## What This Project Forbids Us From Doing

This server can:

- Recognize returning users
- Store sessions in memory

It cannot:

- Survive a restart (no DB)
- Validate input
- Hash passwords
- Sign cookies
- Handle errors gracefully
- Log requests
- Push updates
- Be called from a browser on a different origin
- Be tested automatically

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 07 | The Framework Pivot + Session | "I want middleware: code that runs before every handler." |
| 08 | The Bcrypt Vault | "I want to store passwords securely." |
| 09 | The JWT | "I want stateless auth that scales across servers." |
| 10 | The SQLite Notebook | "I want to persist data on disk." |

Project 07 is the natural next step. Our dispatch is doing too much. Express will take over the boilerplate. The handlers stay the same. The patterns (`req.query`, `req.body`, `req.cookies`) become middleware-provided.

**This is the moment to notice**: in 6 projects, we built a complete HTTP server. We can route, parse, identify. The next 34 projects will add *features*: auth, DB, validation, real-time, deployment. But the HTTP layer is done. We won't write raw HTTP code again.

---

## What You Should Do Now

1. **Read the code.** Notice the dispatch is now ~30 lines. It does a lot. We're ready to hand it off to a framework.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try logging in twice with the same cookie.** See how the same session is reused. Try logging in with a forged session ID. See how it's rejected.
4. **Restart the server.** Notice the sessions are gone. Feel the pain of "no persistence."
5. **When you are ready**, move to [Project 07: The Framework Pivot + Session](../07-framework-session/).
6. **If anything is unclear**, do not proceed. The HTTP substrate is the foundation. It must be solid.

---

## A Note on the Bigger Picture

You now have a *stateful* server. It can recognize users, store sessions, and respond to authenticated requests. This is the foundation of every web app.

But the server is still fragile. It runs on one process. It loses data on restart. It doesn't validate. It doesn't log. It doesn't scale. The next 34 projects will fix all of this.

The path continues. The HTTP substrate is solid. Now we build the rest of the system.

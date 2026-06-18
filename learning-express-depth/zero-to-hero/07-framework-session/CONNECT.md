# The Connect

> *"We adopted the framework. Now we need to fill it with real auth, real storage, real everything."*

This project adopted Express. The pain of "I am rewriting the dispatch for every feature" is solved. We now have:

- A standard, battle-tested framework
- Middleware for body parsing, cookies, sessions
- Helper methods (`res.json`, `res.status`, etc.)
- A handler interface that will not change for the next 33 projects

The HTTP substrate is *truly* done. We won't write raw HTTP code again.

## What Works

- Express middleware composes
- `express.json()` provides `req.body`
- `cookie-parser` provides `req.cookies`
- `express-session` provides `req.session`
- The handler interface is `(req, res) => { ... }`
- Path parameters work via `req.params`
- The server is ~40 lines (vs 90 in project 06)

## What Doesn't Work

### 1. We still don't have passwords

`POST /login` accepts any body with a `username`. No password. Anyone can log in as anyone.

**The pain**: We need real auth with passwords. This is project 08 (Bcrypt Vault).

### 2. We still don't have stateless tokens

Sessions are in memory. Restart the server, sessions are gone. We can't share sessions across multiple server processes.

**The pain**: A real app needs to scale. We need JWT. This is project 09.

### 3. We have no persistent storage

Sessions are in memory. Users are in memory (if we had users). Restart the server, all data is gone.

**The pain**: A real app has data. We need a database. This is project 10 (SQLite Notebook).

### 4. We don't validate input

`POST /login` accepts `{}` (we check `username` but no format). Bad input is accepted.

**The pain**: Strict APIs reject bad input. We need validation. This is project 14 (Validator).

### 5. We have no error handling for handler errors

If `req.session.username = ...` throws (it won't, but if some handler throws), Express's default error handler returns 500. We don't customize it.

**The pain**: We need a custom error handler. This is project 15 (Error Wall).

### 6. We have no logging

We don't log requests. We can't answer "who hit what, when?"

**The pain**: Production needs observability. This is project 16 (Logger).

### 7. We have no real-time

Every request is one-shot. The server cannot push.

**The pain**: Real-time is project 28 (WebSocket).

### 8. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: Frontends need CORS. This is project 57.

### 9. We have no security headers

We don't set `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, etc. The browser is not protected.

**The pain**: Helmet is project 58.

### 10. We have no tests

We have no way to verify the server works. We're running it and clicking around. That's not sustainable.

**The pain**: Tests are project 36.

---

## What This Project Forbids Us From Doing

This server can:

- Handle HTTP requests
- Parse bodies, cookies, sessions
- Recognize returning users
- Be extended with middleware

It cannot:

- Authenticate with passwords
- Issue stateless tokens
- Persist data
- Validate input strictly
- Handle errors gracefully
- Log requests
- Push updates
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 08 | The Bcrypt Vault | "I want real auth with passwords." |
| 09 | The JWT | "I want stateless auth that scales." |
| 10 | The SQLite Notebook | "I want to persist data on disk." |
| 11 | The Foreign Key | "I want to connect entities (users and posts)." |

Project 08 is the natural next step. We have sessions, but we have no *authentication* — anyone can be anyone. We need passwords, hashing, and a real `/signup` and `/login` flow.

---

## What You Should Do Now

1. **Read the code.** Notice the handlers are nearly identical to project 06. The dispatch is replaced by Express. The patterns (`req.body`, `req.session`) are provided by middleware.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try logging in twice with different usernames.** See the session change. Try logging out and back in. See the session persist (or not).
4. **Restart the server.** Notice the sessions are gone. Feel the pain of "no persistence."
5. **Try to log in as someone else.** Realize there's no password — anyone can be anyone. Feel the pain of "no auth."
6. **When you are ready**, move to [Project 08: The Bcrypt Vault](../08-bcrypt-vault/).
7. **If anything is unclear**, do not proceed. Express is the foundation for the rest of the path. It must be solid.

---

## A Note on the Bigger Picture

You now have a *standard* Node app. The patterns are familiar to every Node developer. The middleware is the standard middleware. The framework is the standard framework. From here, every project adds one concept on top of this foundation.

The inflection point is real. The HTTP substrate is done. Express is adopted. Sessions work. The rest is depth: auth, DB, validation, real-time, deployment.

The path continues.

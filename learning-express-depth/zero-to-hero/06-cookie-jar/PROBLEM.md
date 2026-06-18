# The Problem

> *"HTTP is a sequence of unrelated requests. Cookies are how we pretend otherwise."*

## Why HTTP Is Stateless

HTTP, the protocol, has no concept of "you." Each request is independent. The server receives a request, processes it, sends a response, and forgets everything. The next request — even from the same client, seconds later — is a brand new event.

This is a *design choice*, not a limitation. Statelessness is what makes HTTP simple: any server can handle any request. There's no need to maintain a long-running connection. A thousand different servers can all respond to the same client's requests, and it doesn't matter which one handled the previous request.

But for *applications*, statelessness is a problem. When a user logs in, the server needs to *remember* that they're logged in for subsequent requests. When a user adds an item to a cart, the server needs to remember the cart. When a user opens a chat, the server needs to remember they were in the chat.

We need *state* on top of a *stateless* protocol.

## What Pain Is This Solving?

Imagine you log in:

```bash
curl -X POST http://localhost:3000/login -d '{"username": "alice"}'
# {"userId": 1, "token": "abc123"}
```

The server says "you are user 1, your token is abc123." You now have a token. Good.

Now you want to fetch your profile:

```bash
curl http://localhost:3000/me
# {"error": "Not authenticated"}
```

The server has no idea who you are. The token you got from login — the server has *forgotten* about it. You have to send the token somehow. How?

**Option 1: Put the token in the URL.** `/me?token=abc123`. Works, but the token shows up in logs, browser history, etc. Bad for security.

**Option 2: Put the token in a header.** `Authorization: Bearer abc123`. Works, but JavaScript in a browser can't easily set headers (CORS preflight, etc.). Fine for mobile/native clients, awkward for browsers.

**Option 3: Put the token in a cookie.** The server says "here's a cookie," the browser stores it, and sends it back automatically on every subsequent request. This is the **HTTP standard** way to do it.

Cookies are how the web turned stateless HTTP into stateful applications.

## The Deeper Problem: Identity Requires Persistence

Even with cookies, we still need to *store* the session data somewhere. The cookie itself is just a token (like `sessionId=abc123`). The server needs to know "for sessionId=abc123, who is the user?"

In this project, we'll use an in-memory `Map` (`SESSIONS`) to store session data. In project 10 (SQLite Notebook), we'll move it to a database. In project 09 (JWT), we'll put the data *in* the cookie itself.

The principle: **the cookie is a token; the session storage is the data.**

## What This Project Will Solve

This project will:

1. Parse the `Cookie` header into `req.cookies` (an object)
2. Add a `setCookie(res, name, value)` helper
3. Implement a `POST /login` that creates a session and sets a cookie
4. Implement a `GET /me` that reads the cookie and looks up the session
5. Demonstrate cookies with `curl -c cookies.txt` (save) and `curl -b cookies.txt` (send)

By the end, the server *recognizes* returning users.

## What This Project Will *Not* Solve

- **Signed cookies** — anyone can edit cookies. We'll add signing in project 08 (Bcrypt) or 09 (JWT).
- **HttpOnly enforcement** — we'll set the attribute, but a deeper security discussion is project 33 (RBAC) and beyond.
- **Session expiration** — sessions live forever in this project. We'll add expiry in project 25 (Cron) or via session middleware in project 07.
- **Cross-domain cookies** — a cookie for `example.com` won't be sent to `api.example.com` (different subdomain) without `Domain=`. We don't need this yet.
- **Third-party cookies** — used for tracking. Out of scope, increasingly blocked by browsers.
- **SameSite** — the `SameSite` attribute controls cross-origin cookie sending. We'll add it later, in project 57 (CORS) or 33 (RBAC).
- **Secure flag** — required for HTTPS. We use plain HTTP for development.
- **Database storage of sessions** — the `SESSIONS` Map is in memory. Project 10 will move it to a DB.

## The Question This Project Answers

> *"How do I remember the user across multiple requests?"*

If you can answer: "set a cookie on login, read the cookie on subsequent requests, look up the session data," you are ready for project 07.

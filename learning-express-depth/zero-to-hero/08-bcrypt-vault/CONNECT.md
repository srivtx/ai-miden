# The Connect

> *"We have passwords. We have sessions. Now we need stateless tokens and a real database."*

This project added real authentication. The pain of "anyone can be anyone" is solved. Users sign up with a password (hashed with bcrypt). Users log in with a password (verified with bcrypt). The plaintext password is never stored.

But the auth flow has two remaining pain points:

1. **Sessions are stateful** — they live in the server's memory. Restart the server, all sessions are gone. We can't share sessions across multiple server processes.
2. **Sessions are server-side** — the server has to look up the session on every request. This is a database hit (in production) or a memory hit (in development). For high-traffic apps, this is expensive.

Project 09 (JWT) will solve this. JWT (JSON Web Token) is a *stateless* token. The session data is *in* the token, signed. The server doesn't need to store anything. Any server with the secret can verify the token.

The pain of "I need to scale to multiple servers" is solved.

## What Works

- Real authentication with passwords
- bcrypt hashing (slow, salted, one-way)
- Same error for unknown user and wrong password (prevents enumeration)
- Signup creates a user with a hashed password
- Login verifies the password and creates a session
- Sessions are in memory (express-session default)
- Plaintext passwords are never stored

## What Doesn't Work

### 1. Sessions don't survive restarts

Restart the server. All sessions are gone. All users are logged out. Annoying for development, fatal for production.

**The pain**: State persistence. We need a database. Project 10 (SQLite).

### 2. Sessions don't share across processes

If you run 2 server processes (e.g., behind a load balancer), each has its own session store. A user logged in to process 1 is not logged in to process 2. The session cookie points to the wrong process.

**The pain**: Stateless auth. We need JWT. Project 09.

### 3. Users are in memory

`USERS` is a Map. Restart, users are gone. We can't actually *create* users that survive a restart.

**The pain**: Persistence. We need a database. Project 10.

### 4. We don't have user IDs

We use `username` as the primary key. We can't change usernames. We can't have multiple users with the same display name. We need numeric IDs.

**The pain**: Proper user model. Project 11 (Foreign Key).

### 5. We don't validate input

`POST /signup` accepts any `username` and any `password`. Empty strings, 1MB strings, weird unicode — all accepted.

**The pain**: Validation. Project 14 (Validator).

### 6. We have no error handling

If `bcrypt.hash` throws (it won't, but if some handler throws), Express's default error handler returns 500. We don't customize it.

**The pain**: Error handling. Project 15 (Error Wall).

### 7. We have no logging

We don't log signups or logins. We can't answer "who signed up today?"

**The pain**: Observability. Project 16 (Logger).

### 8. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 9. We have no security headers

We don't set `helmet` headers.

**The pain**: Helmet is project 58.

### 10. We have no tests

We can't verify the auth flow works.

**The pain**: Tests are project 36.

---

## What This Project Forbids Us From Doing

This server can:

- Authenticate users with passwords
- Hash passwords securely
- Verify passwords
- Issue sessions

It cannot:

- Survive a restart (no DB)
- Scale to multiple processes (no stateless tokens)
- Have changing usernames (no ID model)
- Validate input strictly
- Handle errors gracefully
- Log requests
- Be called from a browser on a different origin
- Be tested automatically

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 09 | The JWT | "I want stateless auth that scales." |
| 10 | The SQLite Notebook | "I want to persist users and sessions on disk." |
| 11 | The Foreign Key | "I want users with proper IDs and connected entities." |
| 12 | The Migration | "I want to evolve the schema safely." |

Project 09 (JWT) is the natural next step. Sessions are stateful. We need stateless tokens to scale.

---

## What You Should Do Now

1. **Read the code.** Notice the handlers are async. bcrypt is async. The `await` is everywhere. The flow is clear: hash on signup, compare on login.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try signing up with the same username twice.** See the 409.
4. **Try logging in with the wrong password.** See the 401. Try logging in with an unknown user. See the *same* 401.
5. **Restart the server.** Notice the users are gone. Feel the pain of "no persistence."
6. **When you are ready**, move to [Project 09: The JWT](../09-jwt/).
7. **If anything is unclear**, do not proceed. Auth is the foundation of every secure app. It must be solid.

---

## A Note on the Bigger Picture

You now have real authentication. The flow is:

```
Signup: client → password → server → bcrypt.hash → store hash
Login:  client → password → server → bcrypt.compare → match? → session
```

The plaintext password is in memory for ~1 millisecond. Then it's hashed. The hash is what we keep.

This is the foundation of every secure app. From here, the path diverges:

- **Stateless tokens** (project 09): JWT instead of sessions
- **Persistent storage** (project 10): SQLite instead of in-memory Map
- **Proper user model** (project 11): numeric IDs, foreign keys
- **Validation** (project 14): reject bad input

Each adds a layer of *robustness* on top of the auth flow. The auth flow itself is solid.

The path continues.

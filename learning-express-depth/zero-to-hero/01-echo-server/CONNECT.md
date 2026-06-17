# The Connect

> *"Every project leaves a wound. The next project is the bandage."*

This server works. It is a real, honest, runnable HTTP server. It is also useless in any practical sense. That is not a flaw — it is the *point*. The pain this project leaves is the seed of project 02.

---

## What Works

- The server starts in 5ms.
- It responds to any URL with "Hello, world."
- It handles thousands of concurrent connections (the event loop scales).
- It uses zero npm dependencies.
- It is 11 lines of code.

If all you ever needed was "respond with a fixed string to any request," you could deploy this today. It is a complete, working program.

## What Doesn't Work

Let's list everything this server *cannot* do:

### 1. It has no routing

```bash
curl http://localhost:3000/users
# Hello, world.

curl http://localhost:3000/posts/42
# Hello, world.

curl http://localhost:3000/anything/at/all
# Hello, world.
```

The server ignores the URL entirely. There is no way to have a `/users` endpoint that returns users, and a `/posts` endpoint that returns posts. There is one response, applied to every request.

**The pain**: A real API has many endpoints. The next obvious step is "if the URL is `/users`, do X; if it is `/posts`, do Y." This is *routing*.

### 2. It has no method awareness

```bash
curl -X POST http://localhost:3000/users
# Hello, world.

curl -X DELETE http://localhost:3000/users/42
# Hello, world.
```

The server ignores the HTTP method entirely. `GET`, `POST`, `PUT`, `DELETE` all return the same string. There is no way to "create a user" with `POST` and "delete a user" with `DELETE` on the same URL.

**The pain**: REST APIs distinguish methods. A real API must look at `req.method` and dispatch accordingly.

### 3. It has no body parsing

The server cannot accept a JSON body. Even if a client sends:

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

The server receives the body in the request stream but never reads it. The body is silently discarded. The handler has no way to know what the client sent.

**The pain**: A real API accepts input. To accept JSON, we need to *parse* the request body.

### 4. It has no query string awareness

```bash
curl http://localhost:3000/users?role=admin
# Hello, world.
```

The server ignores the query string entirely. The `?role=admin` is in `req.url`, but the handler doesn't look at it. There is no way to say "give me users where role=admin."

**The pain**: Filtering, pagination, search — all need query strings. We need to parse `?key=value` pairs.

### 5. It has no state across requests

The server is *amnesiac*. It has no memory of past requests. If you ask it "who am I?" 100 times, it has no idea if you are the same person. There are no sessions, no cookies, no tokens. Every request is a stranger.

**The pain**: A real application has users. Users have identities. Identities must persist across requests.

### 6. It has no error handling

If our handler throws (e.g., `throw new Error('boom')`), the server catches the error and... what? The response is never sent. The client hangs. The connection times out. There is no recovery, no logging, no graceful failure.

**The pain**: Real servers fail. They fail because of bugs, because of bad input, because of network issues, because of third-party services being down. We need a strategy for failure.

### 7. It has no observability

If the server gets 1,000 requests, you have no idea. There is no log, no counter, no metric. You can't answer "how many users hit `/users` in the last hour?" You can't answer "what failed yesterday at 3am?"

**The pain**: A real production server must be observable.

### 8. It has no persistence

Restart the server. All state — sessions, in-memory caches, temporary uploads — is gone. Every restart is a clean slate.

**The pain**: Real applications have data. Data must survive restarts.

### 9. It has no security

There is no HTTPS, so traffic is plaintext. There is no authentication, so anyone can hit any endpoint. There is no rate limiting, so a malicious client can hammer the server. There is no input validation, so a malicious client can send a 10GB JSON body and crash the process.

**The pain**: Real servers are attacked. We need defense.

### 10. It has no real-time

Every request is a one-shot. The server cannot push to the client. If a chat message arrives for user X, the server has no way to tell user X's browser. The user would have to poll.

**The pain**: Modern applications are real-time. Chat, notifications, presence, live updates — all need server-push.

---

## What This Project Forbids Us From Doing

Because of all the above, this server cannot be the backend of any real application. It is a *toy*. And that is the right level of complexity for project 01.

In the next 39 projects, we will systematically address each of these 10 gaps, in an order where each project's success is built on the previous one.

---

## The Order of Subsequent Projects

Here is the next 5 projects, and what pain they answer:

| # | Project | Pain Answered |
|---|---------|---------------|
| 02 | The Router | "I have one URL. I want many." |
| 03 | The JSON API | "I want my body to be JSON, not text." |
| 04 | The Query-String Reader | "I want `?role=admin` to actually filter." |
| 05 | The Body Parser | "I want to read what the client sent me." |
| 06 | The Cookie Jar | "I want to remember who the user is." |

Each of these will introduce exactly one concept, and it will be obvious *why* we need it because we just lived without it.

---

## What You Should Do Now

1. **Read the code again** — every line should feel obvious.
2. **Run the experiments** in [BUILD.md](./BUILD.md) — break things on purpose.
3. **Predict before running** — for each experiment, predict what will happen *before* you run it. If your prediction is wrong, that's the lesson.
4. **When you are ready**, move to [Project 02: The Router](../02-router/) and address the routing pain.
5. **If anything is unclear**, do not proceed. Re-read THOUGHT.md. Look up `node:http` documentation. The foundation must be solid.

---

## A Note on Pacing

The first 6 projects in this path are the most important. They build the substrate. If you rush through them, every subsequent project will feel like magic. If you take your time, every subsequent project will feel like an obvious next step.

There is no deadline. There is no certificate. The only metric that matters is: *do you understand what your code is doing, and why?*

If yes, move on. If no, stay.

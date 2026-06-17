# The Connect

> *"We can route, but we cannot speak the language of the modern web."*

This router works. It correctly dispatches `GET /` to one handler, `POST /users` to another, and returns 404 for unknown URLs. The pain of "one URL is one function" is solved.

But this router is still a toy. Let's list the pain it leaves.

---

## What Works

- The router is fast (one `Map.get` per request).
- Adding a route is one line.
- Removing a route is one line.
- The dispatch is centralized.
- The handlers are independent.

If all you ever needed was "dispatch URLs to functions, return plain text," you could ship this.

## What Doesn't Work

### 1. We can't return structured data

```bash
curl http://localhost:3000/users
# Alice, Bob, Carol
```

That's a string with commas. It is not a list. A client that wants to *parse* this has to do `users.split(', ')`. That's brittle and ugly.

**The pain**: Modern APIs return *structured* data, not pre-formatted strings. The standard format is JSON.

```json
["Alice", "Bob", "Carol"]
```

A real client (browser, mobile app, server) can parse this directly into an array of strings. No string manipulation.

### 2. We can't return different shapes

A real `GET /users` returns *users*, not strings. Each user has fields: `id`, `name`, `email`, `createdAt`. We can't represent that in a plain text string.

**The pain**: We need JSON. With objects, nested structures, and arrays.

### 3. We can't accept structured input

```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Dave"}'
```

The server receives the request but ignores the body. We never read it. The handler has no idea what the client sent.

**The pain**: Real APIs accept JSON bodies. To accept them, we need to *parse* the body.

### 4. We have no query string support

```bash
curl 'http://localhost:3000/users?role=admin'
# Not Found
```

We discussed this. The query string is part of `req.url`, and our routes don't include it. To support filtering, we need to:

1. Parse the query string (`?key=value&key2=value2`)
2. Strip it from `req.url` before the route lookup
3. Pass it to the handler so it can filter

This is project 04.

### 5. We have no path parameters

```bash
curl http://localhost:3000/users/42
# Not Found
```

We don't have `GET /users/:id` style routes. We register exact paths only.

**The pain**: When we have one user and want to fetch it by id, we need `/users/42` to dispatch to the *same* handler that `/users/99` would. The current router can't do that. We will need path parameters in a few projects.

### 6. We have no state, no persistence

Every request is independent. The server has no memory of past requests. There are no users, no posts, no data. Restart the server, and the slate is clean.

**The pain**: A real API has data. Data must survive restarts. We need a database (project 10).

### 7. We have no auth

Anyone can hit any endpoint. There is no concept of "logged in" or "not logged in." There are no users.

**The pain**: Most APIs have private endpoints (your account, your messages, your data). To support that, we need authentication (project 08).

### 8. We have no error handling

```js
get('/boom', () => { throw new Error('kaboom'); });
```

A throwing handler hangs the connection. We don't catch errors. We don't return 500. The client times out.

**The pain**: Real APIs fail. We need a strategy for failure (project 15).

### 9. We have no logging

When a request comes in, we don't log it. We don't know what happened, when, or to whom. Debugging is impossible.

**The pain**: A production server must be observable (project 16).

### 10. We have no validation

A real `POST /users` should validate that the body has a `name` field, that `name` is a string, that `email` is a valid email. Right now, we don't even *read* the body, let alone validate it.

**The pain**: Bad input should be rejected with `400 Bad Request`, not accepted and processed (project 14).

---

## What This Project Forbids Us From Doing

Because of all the above, this server cannot be the backend of any real application. It is a *toy router*. The next 38 projects will systematically address these gaps.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 03 | The JSON API | "I want to return and accept JSON, not text." |
| 04 | The Query-String Reader | "I want `?role=admin` to actually filter." |
| 05 | The Body Parser | "I want to read what the client sent me." |
| 06 | The Cookie Jar | "I want to remember who the user is." |
| 07 | The Framework Pivot + Session | "I'm tired of writing all this by hand. Let me adopt Express." |

Each will introduce exactly one concept, and it will be obvious *why* we need it because we just lived without it.

---

## What You Should Do Now

1. **Read the code again.** Every line should feel obvious. The `Map` lookup is the central idea.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Add your own route.** Pick an endpoint, register a handler, hit it with `curl`. This is the loop.
4. **Try to break it.** What happens if a handler is `null`? What happens if `req.url` is `undefined`? What happens if a handler returns without calling `res.end()`?
5. **When you are ready**, move to [Project 03: The JSON API](../03-json-api/) and address the structured-data pain.
6. **If anything is unclear**, do not proceed. The router is a primitive every subsequent project builds on. It must be solid.

---

## A Note on the Bigger Picture

You now have a router. A `Map` of method+path to handler. Every other concept in this path — JSON, queries, body parsing, cookies, sessions, auth, validation, error handling, logging — is a *modification* to this router or a *handler that uses these features*.

When you reach project 40 and look back, you will see that the router didn't change. The *handlers* got more sophisticated. The *infrastructure around the router* (middleware, error handling, observability) grew. But the core idea — *dispatch a request to the right function* — is the same idea we have here.

This is the power of a small, well-understood primitive. Everything else is decoration.

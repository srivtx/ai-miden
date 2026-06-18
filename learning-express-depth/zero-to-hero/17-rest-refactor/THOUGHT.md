# The Thought

> *"URLs are nouns. Methods are verbs. Status codes are meanings. That is the REST pattern."*

## The REST Pattern

REST is not a standard. It's a set of conventions. The conventions are:

### 1. URLs Identify Resources (Nouns)

```
/users              (the collection of users)
/users/42           (one specific user)
/users/42/posts     (the collection of posts by user 42)
/users/42/posts/7   (one specific post by user 42)
```

The URL identifies *what*. It doesn't say *what to do with it*. The *do* is in the method.

### 2. HTTP Methods Are Verbs

| Method | Meaning | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Read a resource | Yes | Yes |
| POST | Create a resource | No | No |
| PUT | Replace a resource | Yes | No |
| PATCH | Update part of a resource | No | No |
| DELETE | Remove a resource | Yes | No |

- **Idempotent**: multiple identical requests have the same effect as one.
- **Safe**: doesn't modify the resource.

`GET /users/42` reads. `PUT /users/42` replaces. `DELETE /users/42` removes. The URL is the same; the method is different.

### 3. Status Codes Are Meanings

| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (created a new resource) |
| 204 | No Content | Successful DELETE (or any operation with no body) |
| 400 | Bad Request | Client sent malformed input |
| 401 | Unauthorized | Needs authentication |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | URL or resource doesn't exist |
| 409 | Conflict | State conflict (e.g., duplicate username) |
| 422 | Unprocessable Entity | Validation failed (alternative to 400) |
| 500 | Internal Server Error | Unexpected server error |

The status code is part of the protocol. Clients use it to decide what to do.

### 4. The CRUD Mapping

CRUD (Create, Read, Update, Delete) maps to HTTP:

- **Create** → `POST /collection` (creates a new resource in the collection)
- **Read** → `GET /collection/:id` (reads one) or `GET /collection` (lists)
- **Update** → `PUT /collection/:id` (replace) or `PATCH /collection/:id` (partial)
- **Delete** → `DELETE /collection/:id`

The `POST` is *not* on a specific resource — it's on the collection, because we're creating a new resource (we don't have its ID yet).

### 5. Nested Resources

For related resources, use a hierarchy:

```
GET    /users/42/posts          (list posts by user 42)
POST   /users/42/posts          (create post by user 42)
GET    /users/42/posts/7        (one post)
```

The hierarchy shows the relationship. `/users/42/posts/7` means "post 7, which belongs to user 42."

We could also flatten: `GET /posts?user_id=42`. Both are valid. Nested is more REST-y; flat is simpler. We use nested when the relationship is the primary access pattern.

### 6. Login as a Resource

Login is a special case. It's not really a resource — it's an action. But we can model it as a *session*:

- `POST /sessions` — create a session (login)
- `DELETE /sessions` — destroy the session (logout)
- `GET /sessions/me` — get the current session (who am I?)

The `POST /sessions` body has the credentials (username, password). The response has the token. `DELETE /sessions` (with the token) logs out. `GET /sessions/me` returns the user info.

This is a common pattern. Slack, GitHub, Twitter all use `/sessions` (or `/tokens`).

## The Refactor

### Before

```
POST /signup
POST /login
GET  /me
GET  /posts
GET  /posts/:id
POST /posts
GET  /users/:id/posts
```

### After

```
POST   /users        # was /signup
POST   /sessions     # was /login
GET    /sessions/me  # was /me
DELETE /sessions     # new (logout)

GET    /users        # new (list)
GET    /users/:id    # new (one)
PATCH  /users/:id    # new (update)
DELETE /users/:id    # new (delete)

GET    /posts        # unchanged
GET    /posts/:id    # unchanged
POST   /posts        # unchanged (no longer /users/:id/posts)
PATCH  /posts/:id    # new (update)
DELETE /posts/:id    # new (delete)

GET    /users/:id/posts  # nested resource
POST   /users/:id/posts  # nested resource
```

### Why a flatter `/posts` instead of always `/users/:id/posts`?

Both are valid. We keep both:

- `GET /posts` — list all posts (across all users)
- `GET /users/:id/posts` — list posts by a specific user (filtered)

The flat one is for "give me everything." The nested one is for "give me one user's posts." Same data, different access pattern.

### Why a `/sessions/me`?

It's a convention. The "me" endpoint is the current user. We could also use `/users/me` (with `/users/:id` interpreting `me` as the current user). We use `/sessions/me` because the session is the resource.

## Status Codes Recap

For each new endpoint:

| Endpoint | Success | Client error | Server error |
|----------|---------|--------------|--------------|
| POST /users | 201 | 400, 409 | 500 |
| GET /users | 200 | - | 500 |
| GET /users/:id | 200 | 404 | 500 |
| PATCH /users/:id | 200 | 400, 404 | 500 |
| DELETE /users/:id | 204 | 404 | 500 |
| POST /sessions | 201 | 401 | 500 |
| DELETE /sessions | 204 | 401 | 500 |
| GET /sessions/me | 200 | 401 | 500 |
| GET /posts | 200 | - | 500 |
| GET /posts/:id | 200 | 404 | 500 |
| POST /posts | 201 | 400, 401 | 500 |
| PATCH /posts/:id | 200 | 400, 404 | 500 |
| DELETE /posts/:id | 204 | 404 | 500 |

The pattern is consistent. The codes are meaningful. Clients can rely on them.

## Common Confusions (read these)

**Confusion 1: "Why not `POST /login` instead of `POST /sessions`?"**
You can. `POST /login` is action-shaped. `POST /sessions` is resource-shaped (you're creating a session resource). REST prefers resource-shaped.

**Confusion 2: "Why not `POST /logout` instead of `DELETE /sessions`?"**
You can. `POST /logout` is action-shaped. `DELETE /sessions` is REST-y (you're deleting the session resource). We use `DELETE`.

**Confusion 3: "Should I use `PUT` or `PATCH` for updates?"**
`PUT` replaces the entire resource. `PATCH` updates part. For most APIs, `PATCH` is more user-friendly (you don't have to send the whole resource to change one field).

**Confusion 4: "What if my API needs to do something that's not a CRUD operation?"**
Use an action endpoint: `POST /users/42/reset_password`. The action is a sub-resource. Or use RPC: `POST /rpc/resetPassword`. REST is for resources; for one-off actions, RPC is fine.

**Confusion 5: "What about HATEOAS?"**
HATEOAS (Hypermedia as the Engine of Application State) means responses include links to related resources. It's part of REST, but most APIs don't implement it. We don't.

**Confusion 6: "What about API versioning?"**
`/v1/users` vs. `/users`. We don't version. In a real app, you'd version. We'll discuss in a future project.

**Confusion 7: "What about content negotiation?"**
The client sends `Accept: application/json`. The server returns JSON. We don't implement negotiation; we always return JSON. The Accept header is ignored.

**Confusion 8: "What if a resource is hierarchical but doesn't fit `/users/:id/posts`?"**
Use whatever path makes sense. `/organizations/:id/teams/:id/members/:id/permissions` is fine. The convention is "hierarchy reflects ownership."

## What We Are About to Build

A ~250-line Express app that:

1. Has resource-shaped URLs (`/users`, `/posts`, `/sessions`)
2. Has the right methods (GET, POST, PATCH, DELETE)
3. Has the right status codes (200, 201, 204, 400, 401, 404, 409)
4. Includes list, get, create, update, delete for users and posts
5. Includes login (POST /sessions), logout (DELETE /sessions), me (GET /sessions/me)

The auth flow changes: instead of `POST /signup` and `POST /login`, we have `POST /users` and `POST /sessions`. The post flow changes: we add PATCH and DELETE.

In [BUILD.md](./BUILD.md) we will go line by line.

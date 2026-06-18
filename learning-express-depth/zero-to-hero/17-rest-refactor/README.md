# Project 17: The REST Refactor

> *"URLs are not paths. URLs are resources. Resources have representations. Representations have states."*

Projects 02-16 have us building URLs ad-hoc. `GET /posts` works, but `GET /users/:id/posts` is awkward. `POST /signup` is action-shaped, not resource-shaped. `POST /login` is too. `DELETE /posts/:id` doesn't exist (we never built it).

This project refactors our URLs to follow **REST** (Representational State Transfer). REST is a set of conventions for designing HTTP APIs. The key principles:

1. **Resources are nouns, not verbs.** URLs identify *things* (users, posts, comments), not *actions* (signup, login, getUser, createPost).
2. **HTTP methods are the verbs.** `GET` reads. `POST` creates. `PUT` updates. `PATCH` partially updates. `DELETE` removes.
3. **URLs are resource hierarchies.** `/users/42/posts` means "posts belonging to user 42."
4. **Status codes are meaningful.** `200` (OK), `201` (Created), `204` (No Content), `400` (Bad Request), `401` (Unauthorized), `403` (Forbidden), `404` (Not Found), `409` (Conflict), `500` (Server Error).
5. **Idempotency.** `GET`, `PUT`, `DELETE` are idempotent (multiple calls have the same effect as one). `POST` and `PATCH` are not.

By the end, our URLs are resource-shaped, our methods are consistent, and our status codes are correct.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why are ad-hoc URLs painful? What is REST?
2. [The Thought](./THOUGHT.md) — What are resources? How do HTTP methods map to CRUD?
3. [The Build](./BUILD.md) — Line-by-line refactor of the API
4. [The Decisions](./DECISIONS.md) — Why REST? Why not RPC? Why not GraphQL?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

REST is a set of conventions for HTTP API design. URLs identify *resources* (nouns), not *actions* (verbs). HTTP methods are the verbs. `POST /users` creates a user. `GET /users/42` reads a user. `PUT /users/42` updates a user. `DELETE /users/42` deletes a user. Status codes are meaningful: `200` for success, `201` for created, `204` for deleted (no body), `404` for not found, `409` for conflict. REST makes APIs predictable.

---

## The Code (URL Refactor)

### Before (ad-hoc)

```
POST /signup         (action)
POST /login          (action)
GET  /users/:id/posts
GET  /posts
GET  /posts/:id
POST /posts
```

### After (REST)

```
POST   /users       (create user)
POST   /sessions    (create session = login)
GET    /users       (list users)
GET    /users/:id   (get one user)
PATCH  /users/:id   (update user)
DELETE /users/:id   (delete user)

GET    /users/:id/posts    (list posts by user)
POST   /users/:id/posts    (create post by user)
GET    /posts              (list all posts)
GET    /posts/:id          (get one post)
PATCH  /posts/:id          (update post)
DELETE /posts/:id          (delete post)

DELETE /sessions    (delete session = logout)
```

We also add:
- `GET /users` (list users)
- `GET /users/:id` (get one user)
- `PATCH /users/:id` (update user — change username, email)
- `DELETE /users/:id` (delete user — cascades to posts)
- `PATCH /posts/:id` (update post)
- `DELETE /posts/:id` (delete post)

The shape of each endpoint:

| Method | URL | Purpose | Status |
|--------|-----|---------|--------|
| GET | /users | List users | 200 |
| GET | /users/:id | Get user | 200 / 404 |
| POST | /users | Create user | 201 / 409 |
| PATCH | /users/:id | Update user | 200 / 404 |
| DELETE | /users/:id | Delete user | 204 / 404 |
| POST | /sessions | Login | 201 / 401 |
| DELETE | /sessions | Logout | 204 |
| GET | /posts | List posts | 200 |
| GET | /posts/:id | Get post | 200 / 404 |
| POST | /posts | Create post | 201 |
| PATCH | /posts/:id | Update post | 200 / 404 |
| DELETE | /posts/:id | Delete post | 204 / 404 |
| GET | /users/:id/posts | List user's posts | 200 |

---

## What You Will Have Learned

- What REST is (resource-oriented HTTP API design)
- The mapping of CRUD to HTTP methods
- Why URLs should be nouns, not verbs
- Why status codes are meaningful
- The convention of `/sessions` for login/logout
- The convention of nested resources (`/users/:id/posts`)

These are the foundations of *every* modern API. From here, every project follows REST conventions.

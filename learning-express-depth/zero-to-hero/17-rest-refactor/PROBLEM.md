# The Problem

> *"Ad-hoc URLs are chaos. Each developer picks a different style. The API becomes a museum of personal taste."*

## Why Ad-Hoc URLs Are Painful

In projects 02-16, our URLs evolved organically. We added them as we needed them:

- `POST /signup` — when we needed signup
- `POST /login` — when we needed login
- `GET /posts` — when we needed to list posts
- `GET /users/:id/posts` — when we needed posts by user

Each is fine in isolation. Together, they have problems:

1. **Inconsistent naming** — `signup` and `login` are actions, not resources. `/users` (when we add it) is a resource.
2. **No PUT/PATCH/DELETE** — we never built update or delete for users or posts.
3. **No GET for users** — we don't have `GET /users` or `GET /users/:id`.
4. **Mixed concerns** — `/users/:id/posts` is a nested resource, but it's listed at the same level as `/posts`. The hierarchy is implicit.
5. **No logout** — we have `POST /signup` and `POST /login`, but no `DELETE /sessions` (or `POST /logout`).

A new developer joining the team has to guess the conventions. They might add `POST /create_user` instead of `POST /users`. The API becomes a mess.

## What Pain Is This Solving?

We want a *consistent*, *predictable* API. The same patterns apply to every resource. New resources follow the same shape. New developers can guess the endpoints.

REST gives us that consistency. It's a set of conventions:

- URLs are *resources* (nouns)
- HTTP methods are *verbs*
- Status codes are *meaningful*
- The shape is the same for every resource

Once we adopt REST, the API is predictable. `POST /comments` is a new comment. `GET /comments/42` is one comment. `DELETE /comments/42` is delete. Same shape as users, posts, anything.

## The Deeper Problem: HTTP Semantics

HTTP is a *protocol*, not just a transport. It has semantics: methods, status codes, headers. Many APIs use HTTP as a *transport* — they ignore the semantics. They use `POST` for everything. They use `200 OK` for every response, including errors. They use URLs as RPC calls (`/doSomething?action=foo&value=bar`).

This wastes HTTP's expressiveness. It makes the API harder to use. It makes caching, proxies, and tools less effective.

REST uses HTTP's semantics:

- `GET` is safe and idempotent (multiple calls have the same effect)
- `POST` creates a new resource
- `PUT` replaces a resource (idempotent)
- `PATCH` partially updates a resource
- `DELETE` removes a resource (idempotent)
- `200 OK` for success
- `201 Created` for new resources
- `204 No Content` for successful deletes
- `400 Bad Request` for client errors
- `404 Not Found` for missing resources
- `500 Internal Server Error` for server errors

Caches, proxies, and tools can use these semantics. A `GET` can be cached. A `PUT` is retryable. A `DELETE` can be assumed idempotent. An `OPTIONS` request can be handled automatically.

## What This Project Will Solve

This project will:

1. Refactor URLs to be resource-shaped (`/users`, `/posts`, `/sessions`)
2. Add missing methods (PATCH, DELETE)
3. Add missing endpoints (GET /users, GET /users/:id, etc.)
4. Use correct status codes
5. Add a `DELETE /sessions` for logout

By the end, the API follows REST conventions. The URLs are predictable. The methods are consistent.

## What This Project Will *Not* Solve

- **HATEOAS** — links in responses. Out of scope.
- **API versioning** — `/v1/users` vs. `/users`. Out of scope.
- **Content negotiation** — Accept header for JSON vs. XML. Out of scope (we only do JSON).
- **Caching headers** — ETag, Last-Modified. Out of scope.
- **Pagination** — separate project (18).
- **Filtering / sorting** — separate project (19).
- **Bulk operations** — `POST /users/bulk`. Out of scope.

## The Question This Project Answers

> *"How do I design a predictable, consistent HTTP API?"*

If you can answer: "URLs are resources (nouns), HTTP methods are verbs (GET/POST/PUT/PATCH/DELETE), status codes are meaningful (200/201/204/400/404/409)," you are ready for project 18.

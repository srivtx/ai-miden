# The Decisions

> *"URLs are resources. Methods are verbs. Status codes are meanings. That is REST."*

## Decision 1: REST and not RPC

**Alternative**: RPC-style URLs. `POST /api` with `?action=createUser` in the body. Or `POST /createUser`.

**Why REST**: Predictable. Standard. The same patterns apply to every resource. New developers can guess the endpoints. Tools (caches, proxies) understand the methods.

**Trade-off**: Some operations don't fit REST (e.g., "send password reset email"). For those, we use action endpoints (`POST /users/:id/reset_password`) or RPC.

## Decision 2: `POST /users` for signup, not `POST /signup`

**Why: `/users` is the resource. `POST` creates. The URL identifies *what*, the method identifies *what to do with it*.

**Trade-off**: `POST /signup` is more obvious to a beginner. We accept the trade-off for REST.

## Decision 3: `POST /sessions` for login, not `POST /login`

**Why: Login creates a session. `POST /sessions` says "create a session." The body has the credentials.

**Trade-off**: `POST /login` is more obvious. We accept the trade-off for REST.

## Decision 4: `DELETE /sessions` for logout

**Why: Logout destroys the session. `DELETE` removes a resource. `DELETE /sessions` is the REST way.

**Trade-off**: `POST /logout` is more obvious. We accept the trade-off for REST.

## Decision 5: PATCH for updates, not PUT

**Why: `PUT` replaces the entire resource. `PATCH` updates part. For most APIs, `PATCH` is more user-friendly (you don't have to send the whole resource to change one field).

**Trade-off**: `PUT` is more idempotent. We use PATCH for partial updates and accept the trade-off.

## Decision 6: 204 for deletes

**Why: `DELETE` returns 204 No Content. The body is empty. The client knows it succeeded by the status code.

**Trade-off**: Some APIs return the deleted resource. We don't — the client can fetch it if needed (but it's deleted, so it can't).

## Decision 7: Nested resources for some endpoints

**Why: `GET /users/:id/posts` makes the relationship explicit. It's clear that we're listing posts *by user 42*.

**Trade-off**: We also have `GET /posts` (all posts) and `POST /posts` (create a post for the current user). The nested route is for filtering. Both are valid.

## Decision 8: Authorization checks (you can only update your own posts)

**Why: A user should not be able to update or delete another user's posts. We check ownership in the handler.

**Trade-off**: This is *authorization* (you're allowed to do this), not just *authentication* (you're logged in). We check both. We could extract this to middleware, but for now, we keep it in the handler.

## Decision 9: `ForbiddenError` (new in this project)

**Why: We need a 403 for authorization failures. We add `ForbiddenError` to our error class hierarchy.

**Trade-off**: We could use `UnauthorizedError` for both. The convention is `401` for "you're not logged in" and `403` for "you're logged in but not allowed." We use both.

## Decision 10: No HATEOAS

HATEOAS (Hypermedia as the Engine of Application State) means responses include links to related resources. It's part of REST, but most APIs don't implement it.

**Why not: It's complex. Most clients don't use it. We omit it.

**Trade-off**: Less "REST-y." We accept this for simplicity.

---

## What We Did Not Decide

- **API versioning** — out of scope (future project)
- **HATEOAS** — out of scope
- **Content negotiation** — out of scope
- **Caching headers** — out of scope
- **Bulk operations** — out of scope
- **GraphQL** — out of scope (mentioned only to acknowledge it exists)
- **gRPC** — out of scope
- **WebSockets** — out of scope (project 28)

Each is a future decision.

---

## The Meta-Decision: The API Is REST

For 16 projects, our URLs were ad-hoc. Each new endpoint was added without a clear convention. The API was a museum of personal taste.

Now the API is *REST*. URLs are resources. Methods are verbs. Status codes are meaningful. The shape is consistent. New developers can guess the endpoints.

This is the foundation of *every* modern HTTP API. REST is the standard. The patterns (`POST /collection`, `GET /collection/:id`, `PATCH /collection/:id`, `DELETE /collection/:id`) are universal.

The next 23 projects will follow REST conventions. The path diverges:

- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance
- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API is REST. The path continues.

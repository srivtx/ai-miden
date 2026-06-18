# The Connect

> *"The API is REST. Now we need pagination, search, and the rest of the operations."*

This project refactored the URLs to follow REST conventions. The pain of "ad-hoc URLs are chaos" is solved. The API is now resource-shaped. Methods are consistent. Status codes are meaningful.

But the API is still incomplete:

1. **No pagination** — `GET /users` and `GET /posts` return everything. For 1M users, this is a problem.
2. **No search** — `GET /posts?search=hello` is a slow `LIKE` query.
3. **No sorting** — we hardcode `ORDER BY created_at DESC`.

Projects 18-19 (rest of Phase 3) will fix these. After Phase 3, the API is *robust* and *complete*: validated input, validated output, structured logging, REST-shaped URLs, paginated, searchable.

## What Works

- Resource-shaped URLs (`/users`, `/posts`, `/sessions`)
- All CRUD methods (GET, POST, PATCH, DELETE)
- Meaningful status codes (200, 201, 204, 400, 401, 403, 404, 409)
- New endpoints: list, get, update, delete for users and posts
- Login as `POST /sessions`, logout as `DELETE /sessions`, me as `GET /sessions/me`
- Authorization checks (you can only update your own posts)
- The auth and post flows work

## What Doesn't Work

### 1. No pagination

`GET /users` and `GET /posts` return everything. For 1M users, this is a 100MB response.

**The pain**: Pagination. Project 18 (Paginator).

### 2. No search

`GET /posts?search=hello` would be a slow `LIKE` query. No relevance.

**The pain**: Search. Project 19 (Searcher).

### 3. No sorting

We hardcode `ORDER BY created_at DESC`. Can't sort by title, author, etc.

**The pain**: Sorting. Future project (or part of 18).

### 4. No filtering

`GET /posts?author=42` would be a simple addition. We don't have it.

**The pain**: Filtering. Future project (or part of 18).

### 5. No API versioning

`/v1/users` vs. `/users`. We don't have versioning.

**The pain**: Versioning. Future project.

### 6. No HATEOAS

Responses don't include links to related resources.

**The pain**: HATEOAS. Out of scope.

### 7. No bulk operations

Can't create 100 users at once.

**The pain**: Bulk. Out of scope.

### 8. No file upload

Can't attach images to posts.

**The pain**: File upload. Project 20.

### 9. No email

Can't notify users.

**The pain**: Email. Project 21.

### 10. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

---

## What This Project Forbids Us From Doing

This server can:

- Handle REST-shaped URLs
- Use the right HTTP methods
- Return the right status codes
- Authenticate and authorize users
- List, get, create, update, delete resources

It cannot:

- Paginate large lists
- Search with relevance
- Sort by arbitrary columns
- Filter by arbitrary fields
- Version the API
- Include HATEOAS links
- Bulk-create resources
- Accept file uploads
- Send email
- Be called from a browser on a different origin

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 18 | The Paginator | "I want to handle large lists." |
| 19 | The Searcher | "I want to find with relevance." |

Project 18 is the natural next step. We have list endpoints, but they return everything. We need pagination.

---

## What You Should Do Now

1. **Read the code.** Notice the new URL patterns, the new methods, the new status codes, the new endpoints.
2. **Try the new endpoints**:
   - `GET /users` (list)
   - `GET /users/:id` (one)
   - `PATCH /users/:id` (update)
   - `DELETE /users/:id` (delete)
   - `POST /sessions` (login)
   - `DELETE /sessions` (logout)
   - `GET /sessions/me` (me)
   - `PATCH /posts/:id` (update post)
   - `DELETE /posts/:id` (delete post)
3. **Notice the status codes** — 201 for create, 204 for delete, 404 for not found, 409 for conflict.
4. **Try to update another user's post.** See the 403 Forbidden.
5. **When you are ready**, move to [Project 18: The Paginator](../18-paginator/).
6. **If anything is unclear**, do not proceed. REST is the foundation of every modern API. It must be solid.

---

## A Note on the Bigger Picture

You now have a *REST* API. URLs are resources. Methods are verbs. Status codes are meaningful. The patterns are universal.

From here, the path diverges:

- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The API is REST. The path continues.

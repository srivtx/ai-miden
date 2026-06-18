# The Problem

> *"A URL is two things: the resource (path) and the question (query). Treat them differently."*

## Why Query Strings Exist

An API is a contract. `GET /users` means "give me the users." But a real client often wants more: "give me the users where role is admin." How do you express that in a URL?

The convention: put the question in the *query string*, after a `?`. So:

```
GET /users
GET /users?role=admin
GET /users?role=admin&limit=10
```

The path `/users` is the resource. The query `?role=admin&limit=10` is the filter. The client asks for users, and adds conditions.

The server's job: read the resource from the path, read the question from the query, and answer.

## What Pain Is This Solving?

In projects 02 and 03, our router used `req.url` directly. So:

- `GET /users` → key is `'GET /users'` → matches → handler runs
- `GET /users?role=admin` → key is `'GET /users?role=admin'` → no match → 404

Every filter caused a 404. The client had to put filters in the *path* (e.g., `/users/admin`), which:

- Pollutes the path with non-resource information
- Doesn't scale (imagine `/users/admin/active/sorted-by-name/limit-10`)
- Makes the path harder to read

The query string is the right place for filters. We need to *strip* it from `req.url` before the route lookup, and *parse* it for the handler.

## The Deeper Problem: Separating Identity from Operations

A URL is doing two things:

1. **Identifying a resource**: `/users` (the list of users), `/users/42` (user 42), `/posts` (the list of posts).
2. **Specifying an operation on that resource**: filter, sort, paginate, search.

The first is the *path*. The second is the *query string*. HTTP was designed this way: the path is the noun, the query is the verb (sort of).

Mixing them is a common mistake. `GET /users/admin` is wrong because `admin` is not part of the resource identity — it's a filter. The right URL is `GET /users?role=admin`.

This project enforces the convention. The router matches the *path only*. The query is a separate concern, accessible via `req.query`.

## What This Project Will Solve

This project will:

1. Split `req.url` into `path` and `queryString` on the first `?`
2. Use the `path` for the route lookup
3. Parse the `queryString` with `URLSearchParams` and put it on `req.query`
4. Pass `req` (now with `req.query`) to the handler

By the end, the same handler can serve:

- `GET /users` — return all users
- `GET /users?role=admin` — return only admins
- `GET /users?role=user&limit=5` — return only users, with a limit

The handler looks at `req.query` and decides what to do.

## What This Project Will *Not* Solve

- **Body parsing** — for `POST` we want to read the body, not the query. Project 05.
- **Validation of query values** — `?role=foo` is just an unknown value. We filter; if no user has `role=foo`, we return `[]`. We don't return 400. Project 14 (Validator) introduces validation.
- **Pagination** — `?limit=10&offset=20` is a real query, but we don't handle it here. Project 18 (Paginator).
- **Sorting** — `?sort=name` or `?sort=-name` is a real query. Project 18.
- **Field selection** — `?fields=id,name` is real. Project 18.
- **Path parameters** — `?id=42` is a query, not a path. `/users/42` is a path. They're different. Path parameters are a future project (probably 11 or 17).
- **Multi-value query** — `?tag=a&tag=b` is a real pattern. We will not handle it here. Project 18.

## The Question This Project Answers

> *"How do I read filters and parameters from the URL?"*

If you can answer: "split on `?`, look up the path, parse the query with `URLSearchParams`, put it on `req.query`," you are ready for project 05.

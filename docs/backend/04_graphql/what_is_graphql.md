## Why it exists (THE PROBLEM)

REST returns fixed data shapes. `GET /users/42` returns ALL user fields. `GET /users/42/posts` requires a separate request. For mobile apps (slow networks), 5 REST calls to build a screen = 5 round trips = 1500ms. For a dashboard with 10 widgets, 10 REST calls = 3000ms.

**GraphQL** lets the client specify EXACTLY what data it wants in ONE request. No over-fetching (getting fields you don't need). No under-fetching (needing multiple requests). One query, one response, exactly the right data.

## Definition (very simple)

GraphQL = a query language for APIs. The client writes:
```graphql
query {
  user(id: 42) {
    name
    email
    posts(limit: 5) {
      title
      commentCount
    }
  }
}
```

One request returns: `{ user: { name: "Zen", email: "...", posts: [{ title: "Hello", commentCount: 3 }] } }`. No extra fields. No follow-up requests. The server defines a SCHEMA (types and relationships). The client queries against it. The server resolves each field.

**Key difference from REST:**
- REST: server decides response shape. Client gets what server gives.
- GraphQL: client decides response shape. Server gives what client asks for.

## The components

1. **Schema (SDL):** defines types and their fields
2. **Resolvers:** functions that return data for each field
3. **Query:** read data
4. **Mutation:** write data
5. **Subscription:** real-time updates (WebSocket-based)

## Key properties

| | REST | GraphQL |
|---|---|---|
| Requests per screen | N (one per resource) | 1 |
| Over-fetching | Yes (all fields returned) | No (only requested fields) |
| Under-fetching | Yes (need follow-up calls) | No (nested queries) |
| Caching | HTTP cache (CDN) | Client-side (Apollo, Relay) |
| Error handling | HTTP status codes | Always 200, errors in body |
| Versioning | URL-based (/v1, /v2) | Schema evolution (deprecate fields) |

## Connection to our projects

Any of our REST APIs can be converted to GraphQL. The data model stays the same. Add: type definitions + resolvers. Apollo Server wraps Express. The client (mobile/web) gets exactly what it needs in one call.

## Why it exists (THE PROBLEM)

You built `/users/42`. Customers use it. Now you need to add a new field. Some clients send it, some don't. If you just modify the response shape, the old clients break. If you add a new field, you have to support both shapes forever. 

Three months later, the new shape is the only one. You want to remove the old one. But you can't — the old clients are still on the old version. They paid for "API v1" and "API v2" or they didn't. Without versioning, removing the old shape breaks them. With versioning, you can say "v1 is deprecated, will be removed in 6 months, migrate to v2."

The second problem: "I want to test a breaking change." Without versioning, you test in production. With versioning, you ship v2 in parallel, route 1% of traffic to it, see if it works, then route 100%.

The third problem: "What did v1 look like?" Without versioning, you git-blame and hope. With versioning, v1 is its own code, its own docs, its own status page.

## Definition (very simple)

**Versioning = a contract.** When you say "v1", you mean: "this set of endpoints, with these request/response shapes, will not change in breaking ways for N months." Clients build against that contract. They can rely on it.

**Breaking change** = any change that requires clients to update code. Removing a field. Renaming a field. Changing a field's type. Adding a required field. Changing an error code. Changing pagination shape. These all break clients.

**Non-breaking change** = a change that doesn't require clients to update. Adding a new optional field. Adding a new endpoint. Adding a new optional query parameter. These are safe.

**Deprecation** = "this version still works, but will be removed on date X." Clients get a warning header. They migrate. You remove on the announced date.

## Real-life analogy

**Software versions = car model years.** A 2018 Honda Civic has certain features. A 2024 Honda Civic has different features. They're both "Honda Civic" but different versions. The 2018 still works (you can drive it). The 2024 has improvements. If Honda changed the 2018 in 2019, all 2018 owners would be confused. They don't. They make a new model year.

**API versions = the same.** A v1 endpoint is "the 2018 Civic." A v2 endpoint is "the 2024 Civic." Clients pick which year they want to drive. You can deprecate v1 ("we'll stop making parts in 2026"), but until then, it works.

## Tiny numeric example

Three versioning strategies:

**1. URI path** (most common)
```
GET /api/v1/users
GET /api/v2/users
```
Pros: clear, easy to route, easy to test. Cons: every endpoint needs a version in the URL.

**2. Query parameter**
```
GET /api/users?version=2
```
Pros: clean URLs. Cons: not obvious, easy to forget, cache keys are weird.

**3. Header**
```
GET /api/users
Accept: application/vnd.myapi.v2+json
```
Pros: very clean, RESTful. Cons: harder to test in browser, tools don't always make it easy.

Most companies use URI path. It's simple, explicit, and works with curl/browser.

## Common confusion (5+ bullet points)

1. **"I'll just add a new endpoint."** That's not versioning, that's a new feature. Versioning is for breaking changes. If you add `/users/:id/posts` and it doesn't break `/users/:id`, you don't need a version. If you change `/users/:id` to return `{ user: {...} }` instead of `{ id, name, ... }`, you need a version.

2. **"I'll always support all versions."** Forever? Even 10-year-old versions? Pick a deprecation policy. "We support the current version and one back. Older versions are removed 6 months after the new version ships." Tell customers. They'll migrate.

3. **"v1 and v2 are different codebases."** They can be, but it's painful to maintain. Often: one codebase, two routers, branching at the entry point. `v1Routes` and `v2Routes` files, both pointing to similar handlers with slight differences.

4. **"Once v2 is out, I can stop maintaining v1."** NO. You maintain v1 until the deprecation date. Bug fixes, security patches. If you stop, the v1 customers are exposed. They paid for v1. Honor the contract.

5. **"Versioning prevents breaking changes."** It doesn't. It CONTAINS them. v2 can still break clients who migrate to v2. The contract is: "v1 won't break." v2 is a new contract. New clients opt in.

6. **"I'll version everything."** Don't. Version the API surface, not internal code. `/api/v1/users` is versioned. Your internal helper function `formatUser()` is not. Version where the contract starts (the API boundary), not where the work happens (internal code).

## Key properties

| Property | URI path | Query param | Header |
|---|---|---|---|
| Visibility | High | Low | Low |
| Browser testable | Yes | Yes | No |
| Tooling | Easy | OK | Hard |
| Cache | Per-URL | Per-URL+query | Per-URL+header |
| Common | Yes (most) | No | RESTful purists |

## When to introduce a new version

Only when you need to make a breaking change. Some teams version at launch ("v1" from day 1) so the contract is explicit. Others version only when needed. Both work. The key is: tell customers in advance. Document the contract. Set a deprecation date.

## Sunset header

When you deprecate a version, return a `Sunset` header:
```
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
Deprecation: true
Link: <https://api.example.com/v2/migrate>; rel="successor-version"
```

Clients can read these and warn the developers. "This version will stop working on Jan 1, 2027. Migrate to v2."

## Connection to our projects

For our 73 apps, you can add `/v1` to all routes in 2 minutes. Add `/v2` for breaking changes. Use `app.use('/v1', v1Router)` and `app.use('/v2', v2Router)`. The `api-versioning-demo/` project in apps/level1 shows the pattern.

For CortexCode and logogen: same. The API server can have `/v1/complete` and `/v2/complete`. Old clients use v1, new clients use v2. When v1 is sunset, you can remove it without breaking v2 users.

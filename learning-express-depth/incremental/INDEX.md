# Incremental — Build the Todo App in 12 Stages

Each stage adds ONE new thing. You can run each stage and see how the app grows.

**The point:** see how a real backend is built up one piece at a time. Every stage is a working app.

## The 12 stages

| # | Stage | What it adds |
|---|---|---|
| 01 | todo-memory | In-memory CRUD (the start) |
| 02 | todo-sqlite | Add a database (data survives restart) |
| 03 | todo-relations | Tags (many-to-many) and categories |
| 04 | todo-auth | Users, login, JWT |
| 05 | todo-multi-tenant | Tenants (teams), data isolation |
| 06 | todo-soft-delete | Mark as deleted, restore, trash |
| 07 | todo-audit | Log every change (who, what, when) |
| 08 | todo-versioning | Optimistic locking, conflict detection |
| 09 | todo-caching | Cache-aside, invalidate on write |
| 10 | todo-rate-limit | Per-user token bucket |
| 11 | todo-search | Full-text search with FTS5 |
| 12 | todo-webhooks | Subscribe to events, signed delivery |

## How to use this folder

### For each stage:

1. **Read the README** — it explains what's new
2. **Read the code** — it's small, builds on the previous stage
3. **Run it** — `npm install && node server.js`
4. **Try the curl examples**
5. **Move to the next stage**

### The progression

Each stage adds 1 thing. The shape grows:
- Stage 01: 30 lines. Just CRUD.
- Stage 12: 150 lines. A real backend.

The shape stays familiar — same routes, same patterns — but each stage adds one new tool to the toolbox.

## The 11 patterns you'll learn

1. **CRUD with a database** — every app needs this
2. **Relations** — one-to-many, many-to-many
3. **Auth** — passwords, JWT, middleware
4. **Multi-tenancy** — data isolation by tenant
5. **Soft delete** — never actually delete
6. **Audit log** — every change recorded
7. **Versioning** — conflict detection
8. **Caching** — speed up reads
9. **Rate limiting** — prevent abuse
10. **Search** — full-text with ranking
11. **Webhooks** — notify other systems

These 11 patterns appear in **every** production backend. Stripe, GitHub, Slack, Notion — all of them use these.

## After the 12 stages

Pick any of the apps in `learning-express-depth/` (the 60 small projects). Apply these 11 patterns to it. The data is different. The shape is the same.

Or build something new from scratch. You have the toolbox.

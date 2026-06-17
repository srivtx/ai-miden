# 12 — Todo (webhooks) — final stage

Subscribe to events. When a todo changes, we POST to your URL with a signed payload.

**What's new:**
- `webhooks` table: URL, secret, list of events to subscribe to
- `deliveries` table: log of every attempt
- `fire()` posts to all subscribed URLs after every change
- HMAC signature in `X-Signature` header — you can verify it's from us
- The final piece: when X happens, Y is notified

**Why webhooks?** Instead of polling ("did anything change?"), we tell you when something changes. Like a notification.

**The full flow:**
1. You POST `/webhooks` with your URL and which events you want
2. We give you back a secret
3. When something happens, we POST to your URL with the event data
4. The body is signed with your secret — you verify with HMAC
5. You can replay any failed delivery from the deliveries log

## Run
```bash
npm install && node server.js
```

```bash
# Subscribe
curl -X POST http://localhost:3000/webhooks -H "Content-Type: application/json" \
  -d '{"url": "https://yourapp.com/hook", "events": ["todo.created", "todo.updated"]'
# 201 { id, url, events, secret: "abc..." }

# Now create a todo — webhook fires
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Test"}'
# Server logs: [webhook] Would POST to https://yourapp.com/hook ...
#              X-Signature: sha256=...
#              Body: {"event": "todo.created", ...}

# See delivery history
curl http://localhost:3000/webhooks/wh_xxx/deliveries
```

## What this stage teaches
- Webhook subscriptions
- HMAC signatures for verification
- Delivery log
- Event types

## 🎉 12 stages complete!

The full todo app now has:
- Database ✓
- Relations (tags, categories) ✓
- Auth (JWT) ✓
- Multi-tenant ✓
- Soft delete + restore ✓
- Audit log ✓
- Optimistic locking ✓
- Caching with invalidation ✓
- Rate limiting ✓
- Full-text search ✓
- Webhooks ✓

This is a production-quality backend. Every pattern in this app appears in real systems: Stripe, GitHub, Slack, Notion. You can apply these 12 patterns to anything.

## What you've learned (12 patterns)
1. **CRUD with a database** — the foundation
2. **Relations** — one-to-many, many-to-many
3. **Auth** — password hashing, JWT, middleware
4. **Multi-tenant** — data isolation
5. **Soft delete** — never actually delete
6. **Audit log** — every change recorded
7. **Versioning** — conflict detection
8. **Caching** — speed up reads, invalidate on writes
9. **Rate limiting** — prevent abuse
10. **Search** — full-text with ranking
11. **Webhooks** — notify other systems

These 11 patterns are the building blocks of every backend.

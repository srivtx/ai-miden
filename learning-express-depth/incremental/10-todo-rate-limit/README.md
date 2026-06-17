# 10 — Todo (rate limit)

Per-user rate limits. Different limits for read vs write operations.

**What's new:**
- Token bucket per user
- Reads: 60 per minute
- Writes: 10 per minute (writes are more expensive)
- 429 with `Retry-After` when exceeded
- `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers

**Why different limits?** A user might read 1000 times an hour. But if they're creating 100 todos per minute, something is wrong (bot, abuse). Different limits reflect different costs.

## Run
```bash
npm install && node server.js
```

```bash
# 11 writes in a row — the 11th gets 429
for i in {1..11}; do
  curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" \
    -H "X-User-Id: alice" -d "{\"title\": \"T$i\"}" -o /dev/null -w "$i: %{http_code}\n"
done
# 1-10: 201
# 11: 429

# Reads work fine (different limit)
curl -H "X-User-Id: alice" http://localhost:3000/todos
# 200
```

## What this stage teaches
- Token bucket algorithm
- Per-user limits
- Different limits for different operations
- 429 status with Retry-After

## Where we are: 10 stages in
The todo app now has:
- Database ✓
- Relations ✓
- Auth ✓
- Multi-tenant ✓
- Soft delete ✓
- Audit ✓
- Versioning ✓
- Caching ✓
- Rate limit ✓

The remaining stages:
- **11-todo-search** — full-text search
- **12-todo-webhooks** — notify on changes

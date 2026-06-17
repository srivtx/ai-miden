# 32 — Bug Tracker

Bugs have a status (open / in_progress / closed) and a priority. New thing: **filter by multiple fields** with query parameters.

## Run it

```bash
npm install
node server.js
```

```bash
# Add bugs
curl -X POST http://localhost:3000/bugs -H "Content-Type: application/json" -d '{"title": "Login broken", "priority": "high"}'
curl -X POST http://localhost:3000/bugs -H "Content-Type: application/json" -d '{"title": "Slow page", "priority": "low"}'

# Filter by status
curl 'http://localhost:3000/bugs?status=open'

# Filter by priority
curl 'http://localhost:3000/bugs?priority=high'

# Filter by both
curl 'http://localhost:3000/bugs?status=open&priority=high'

# Update status
curl -X PATCH http://localhost:3000/bugs/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

## How to think about it

The list endpoint supports multiple filters at once. Each one is a query parameter. We apply them in order: first by status, then by priority.

## How to build it (line by line)

```js
if (status) result = result.filter(b => b.status === status);
if (priority) result = result.filter(b => b.priority === priority);
```

**Lines 11-12.** Each filter narrows the result. Both can be applied together.

**Why two `if` statements?** Each filter is independent. Either can be present or not. We don't want to filter by priority if the user didn't ask for it.

## What we learned

1. Multiple filters: apply them one after the other
2. `if (param) filter(...)` — only filter if the user asked
3. We've now seen multi-filter endpoints

## What's next

In **33-feedback-app** we build a feedback form. Submissions have a rating and a comment. We get the average rating.

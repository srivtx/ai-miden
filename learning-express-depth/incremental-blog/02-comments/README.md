# 02 — Comments

Threaded comments. Top-level and nested replies. Moderation queue.

**What's new:**
- `comments` table with `parent_id` for replies
- Tree structure: comments can have replies, which can have replies
- Status: `pending` (awaiting moderation), `approved` (public), `hidden` (admin removed)
- Moderation endpoint requires `X-Role: admin` header

**Why moderation?** Without it, your blog becomes a spam magnet. Bots post links. Trolls post garbage. Moderation queue gives you control.

**Why tree structure?** Same as chat — a comment can have replies. We build the tree from flat rows by following `parent_id`.

## Run
```bash
npm install && node server.js
```

```bash
# Add a top-level comment
curl -X POST http://localhost:3000/posts/hello/comments -H "Content-Type: application/json" \
  -d '{"author": "alice", "body": "Great post!"}'
# 201 (status: pending)

# Reply to it
curl -X POST http://localhost:3000/posts/hello/comments -H "Content-Type: application/json" \
  -d '{"author": "bob", "body": "I agree", "parent_id": 1}'

# Moderate
curl -X PATCH http://localhost:3000/comments/1 -H "X-Role: admin" -H "Content-Type: application/json" -d '{"status": "approved"}'
curl -X PATCH http://localhost:3000/comments/2 -H "X-Role: admin" -H "Content-Type: application/json" -d '{"status": "approved"}'

# See the thread
curl http://localhost:3000/posts/hello/comments
# { comments: [{ author: "alice", body: "Great post!", replies: [{ author: "bob", body: "I agree" }] }] }
```

## What this stage teaches
- Self-referencing (parent_id)
- Building a tree from flat rows
- Moderation queue
- Role-based access (X-Role header)

## Next
**03-users** — proper user accounts. Email, password, profile.

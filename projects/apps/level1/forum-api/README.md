# Forum API — Step 7 in the learning path

Builds on Chat. Adds: persistent threads, nested replies, voting, categories, moderation flags.

## Endpoints
```
GET    /categories                              # categories with thread counts
GET    /threads?category=&sort=                 # sort=recent|top|new
GET    /threads/:id                             # thread + all replies
POST   /threads                                 # create (X-User-Id header)
POST   /threads/:id/replies                     # reply (nested via parent_id)
POST   /vote                                    # { target_id, target_type: thread|reply, value: 1|-1|0 }
```

## Try
```bash
# Create thread
curl -X POST http://localhost:3000/threads \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"category_id": "<id>", "title": "How do I learn backend?", "body": "I want to learn"}'

# Reply
curl -X POST http://localhost:3000/threads/<id>/replies \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"body": "Start with Node.js", "parent_id": null}'

# Nested reply
curl -X POST http://localhost:3000/threads/<id>/replies \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_bob" \
  -d '{"body": "Agreed, Express is great", "parent_id": "<reply-id>"}'

# Upvote
curl -X POST http://localhost:3000/vote \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_bob" \
  -d '{"target_id": "<thread-id>", "target_type": "thread", "value": 1}'

# Sort by top
curl 'http://localhost:3000/threads?sort=top'
```

## What this teaches
1. **Nested replies**: `parent_id` self-reference
2. **Voting system**: separate `votes` table, recalculate score
3. **Polymorphic association**: `target_type` (thread OR reply)
4. **Sort options**: recent, top (by score), new
5. **Pinning/locking**: moderation flags
6. **Category organization**: separate category table

## Next project
→ **calendar-api** — adds: events, time slots, recurring events, attendees

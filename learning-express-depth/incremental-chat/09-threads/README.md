# 09 — Threads (Chat)

Reply to a message in a thread. The thread is a separate timeline.

**What's new:**
- `parent_id` on messages (a reply has a parent)
- `thread_count` and `latest_reply_at` on parent
- Reply endpoint: `POST /messages/:id/replies`
- Get thread: `GET /messages/:id/thread`
- Top-level messages in a room have `parent_id = NULL`
- Default list shows only top-level (replies are in the thread)

**Why threads?** Without them, a busy channel becomes 90% "yes" / "no" / "thanks" replies to one message. Threads let you have a side conversation without polluting the main channel.

**Why parent_id IS NULL filter?** The default list shows only top-level messages. Replies are inside their thread. The client can click "3 replies" to expand.

## Run
```bash
npm install && node server.js
```

```bash
# Top-level message
curl -X POST http://localhost:3000/rooms/general/messages -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "text": "Anyone seen the new docs?"}'

# Reply in thread
curl -X POST http://localhost:3000/messages/1/replies -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob", "text": "Yes! Just pushed them."}'

# Get the thread
curl http://localhost:3000/messages/1/thread
# { parent: { ..., thread_count: 1 }, replies: [...] }

# Top-level messages in the room (no replies shown)
curl http://localhost:3000/rooms/general/messages
# [ { id: 1, text: "Anyone seen the new docs?", thread_count: 1 } ]
```

## What this stage teaches
- Threading pattern (parent_id self-reference)
- Filtering top-level only
- Aggregating reply counts
- UX of threads (kept out of main view)

## Next
**10-notifications** — the final stage. Notify users when something happens.

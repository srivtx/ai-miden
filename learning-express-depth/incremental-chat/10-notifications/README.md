# 10 — Notifications (Chat, final stage)

Notify users when something happens. Mentions, replies. Read state.

**What's new:**
- `notifications` table: user_id, type, message, source, read_at
- @mention detection in messages (regex: `@\w+`)
- Reply notification (parent != replier)
- Per-user notification feed
- Mark as read (specific ids or all)
- Unread count

**Why notifications?** Without them, users miss things. "Did Alice reply to me?" You'd have to check the channel. Notifications bring it to you.

**Why @mentions specifically?** You can't notify on every message (overload). @mention is opt-in: "I want to know about this."

**The regex `/@(\w+)/g`** matches `@username` in text. `g` flag finds all. The `slice(1)` removes the `@`. `toLowerCase()` for case-insensitive.

## Run
```bash
npm install && node server.js
```

```bash
# Send a message that mentions bob
curl -X POST http://localhost:3000/rooms/general/messages -H "Content-Type: application/json" \
  -H "X-Username: alice" \
  -d '{"user_id": "u_alice", "text": "Hey @bob check this out!"}'

# Get bob's notifications
curl 'http://localhost:3000/notifications?user_id=u_bob'
# { unread_count: 1, notifications: [{ type: "mention", message: "alice mentioned you" }] }

# Reply to alice's message
curl -X POST http://localhost:3000/messages/1/replies -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob", "text": "Got it!"}'
# Alice gets a "reply" notification

# Mark all as read
curl -X POST http://localhost:3000/notifications/read -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob"}'
```

## What this stage teaches
- @mention detection
- Notification patterns (mention, reply, reaction)
- Read state
- Unread counts

## 🎉 10 stages complete!

The full chat app has:
- Messages ✓
- Rooms ✓
- Users ✓
- Presence ✓
- Typing indicators ✓
- Read receipts ✓
- File sharing ✓
- Reactions ✓
- Threads ✓
- Notifications ✓

This is how Slack, Discord, Telegram, WhatsApp all work. Same 10 patterns, different code.

## The 10 patterns from this app
1. **Messages** — cursor pagination, ordering
2. **Rooms** — nested resources, auto-create
3. **Users** — auth + profile, JOINs
4. **Presence** — heartbeats, last-seen
5. **Typing** — ephemeral state, auto-expiry
6. **Receipts** — read state, ranges
7. **Files** — uploads, path safety
8. **Reactions** — whitelisted emoji, aggregation
9. **Threads** — parent_id, kept out of main view
10. **Notifications** — @mentions, unread count

These 10 patterns are the building blocks of every real-time chat backend.

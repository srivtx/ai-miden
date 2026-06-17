# 04 — In-App (Notifications)

In-app notifications. Inbox, unread count, mark as read.

**What's new:**
- `notifications` table with `read_at`
- Send: `POST /notifications`
- Inbox: `GET /notifications?user_id=X`
- Unread count: `GET /notifications/unread-count`
- Mark read: `POST /notifications/:id/read`
- Mark all read: `POST /notifications/read-all`

**Why in-app notifications?** Email and push get missed. The user closes the app, the notification is gone. In-app notifications live in the app: a bell icon, an inbox page. They never get lost.

**Why unread count?** Critical for UX. Shows on the bell icon. The user knows there's something to look at.

## Run
```bash
npm install && node server.js
```

```bash
# Send
curl -X POST http://localhost:3000/notifications -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "title": "New comment", "body": "Bob commented on your post", "link": "/posts/1"}'

# Inbox
curl 'http://localhost:3000/notifications?user_id=u_alice'

# Unread only
curl 'http://localhost:3000/notifications?user_id=u_alice&unread=true'

# Unread count
curl 'http://localhost:3000/notifications/unread-count?user_id=u_alice'

# Mark as read
curl -X POST http://localhost:3000/notifications/n_xxx/read

# Mark all read
curl -X POST http://localhost:3000/notifications/read-all -H "Content-Type: application/json" -d '{"user_id": "u_alice"}'
```

## What we learned
- Inbox pattern
- Unread count (separate query for the badge)
- Mark as read (single and bulk)
- The "bell icon" UX

## Next
**05-templates** — reusable notification templates. Subject + body with placeholders.

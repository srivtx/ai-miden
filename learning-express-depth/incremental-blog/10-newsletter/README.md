# 10 — Newsletter (final stage)

Subscribe by email. When a post is published, send to all subscribers.

**What's new:**
- `subscribers` table with confirmation flow (pending → active)
- `newsletters` table: one row per send
- `newsletter_sends` table: one row per recipient
- Subscribe, confirm, unsubscribe
- Auto-send when a post is published

**Why confirmation (double opt-in)?** Without it, anyone can subscribe anyone else to your list. That's spam. Confirmation proves the email is real and the person wants to receive.

**The flow:**
1. User submits email
2. We send a confirmation email with a unique token
3. User clicks the link
4. Their status changes to `active`
5. When a post is published, we send to all `active` subscribers

## Run
```bash
npm install && node server.js
```

```bash
# Subscribe
RESP=$(curl -X POST http://localhost:3000/newsletter/subscribe -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}')
TOKEN=$(echo $RESP | grep -o '"confirm_url":"[^"]*' | cut -d'"' -f4 | cut -d= -f2)

# Confirm
curl "http://localhost:3000/newsletter/confirm?token=$TOKEN"
# { confirmed: true }

# Publish a post (sends to all subscribers)
curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "New post!", "body": "...", "status": "published"}'
# Server logs: [email] To alice@example.com: New post: New post!

# Unsubscribe
curl -X POST http://localhost:3000/newsletter/unsubscribe -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}'

# See send history
curl http://localhost:3000/admin/newsletters
```

## What this stage teaches
- Double opt-in (confirmation)
- Token-based verification
- Mass send pattern
- Per-recipient tracking

## 🎉 10 stages complete!

The full blog/CMS app has:
- Posts with slugs ✓
- Comments (threaded, moderated) ✓
- Users with profiles ✓
- Roles (reader, author, admin) ✓
- Media uploads ✓
- Drafts with auto-save and scheduling ✓
- Revisions (history, restore, diff) ✓
- Full-text search ✓
- RSS / Atom / JSON feeds ✓
- Email newsletter ✓

This is how WordPress, Ghost, Substack, Medium work. Same 10 patterns, different code.

## The 10 patterns from this app
1. **Posts** — slugs, draft/published, excerpts
2. **Comments** — threaded, moderation queue
3. **Users** — auth + profile separation
4. **Roles** — reader/author/admin permissions
5. **Media** — uploads, MIME validation, alt text
6. **Drafts** — auto-save, schedule
7. **Revisions** — full history, restore, diff
8. **Search** — FTS5, ranking, autocomplete
9. **Feeds** — RSS, Atom, JSON
10. **Newsletter** — double opt-in, mass send

These 10 patterns are the building blocks of every publishing platform.

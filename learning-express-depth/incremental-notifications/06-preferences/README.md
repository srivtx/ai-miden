# 06 — Preferences (Notifications)

Per-user notification preferences. Each event_type can be sent via different channels.

**What's new:**
- `preferences` table: user_id, event_type, channel, enabled
- `GET /users/:id/preferences` — get all preferences
- `PUT /users/:id/preferences/:event_type/:channel` — set a preference
- `GET /should-send` — check if a notification should be sent

**Why preferences?** Without them, every user gets every notification. Some want email for comments but not for follows. Some want push but not email. Preferences let them choose.

**Default true:** New users get all notifications. They can opt out. Otherwise new users would be silent, which feels broken.

**The `should-send` check:** Before sending a notification, ask "would this user want this?" The system checks preferences and only sends if yes.

## Run
```bash
npm install && node server.js
```

```bash
# Get defaults (no preferences set)
curl http://localhost:3000/users/u_alice/preferences
# { defaults: { email: true, push: true, in_app: true, sms: false } }

# Disable email for new_follower
curl -X PUT http://localhost:3000/users/u_alice/preferences/new_follower/email \
  -H "Content-Type: application/json" -d '{"enabled": false}'

# Check before sending
curl 'http://localhost:3000/should-send?user_id=u_alice&event_type=new_follower&channel=email'
# { should_send: false }

curl 'http://localhost:3000/should-send?user_id=u_alice&event_type=new_follower&channel=push'
# { should_send: true }
```

## What we learned
- Per-user, per-event, per-channel preferences
- Default to true (opt-out, not opt-in)
- The `should-send` pattern
- Check before sending

## Next
**07-digest** — instead of 10 emails, send 1 daily digest.

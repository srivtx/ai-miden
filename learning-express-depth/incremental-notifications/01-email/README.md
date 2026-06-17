# 01 — Email (Notifications)

Send emails. Queue, status tracking, retry on failure.

**What's here:**
- `emails` table with status (queued, sent, failed)
- `POST /emails` queues an email and returns 202 immediately
- Background processing: send the email, update status
- Retry endpoint for failed emails
- Track attempts and last error

**Why a queue?** Sending an email takes 100ms. If the user is waiting for a response, that's 100ms of latency. We queue the email and return 202 immediately. The email sends in the background.

**Why retry?** Emails fail. SMTP servers go down. Recipients' inboxes are full. We retry so transient failures don't lose emails.

## Run
```bash
npm install && node server.js
```

```bash
# Queue an email
curl -X POST http://localhost:3000/emails -H "Content-Type: application/json" \
  -d '{"to": "alice@example.com", "subject": "Welcome!", "body": "Thanks for signing up"}'
# 202 { id, status: "queued" }

# Check status
curl http://localhost:3000/emails/em_xxx
# After a moment: { status: "sent", sent_at: "..." }

# Failed email (to anything but @example.com)
curl -X POST http://localhost:3000/emails -H "Content-Type: application/json" \
  -d '{"to": "bad@other.com", "subject": "Test"}'

# Retry
curl -X POST http://localhost:3000/emails/em_xxx/retry
```

## What we learned
- Queue + background worker
- 202 Accepted pattern
- Retry on failure
- Status tracking

## Next
**02-sms** — same idea, but for SMS. Different provider, similar pattern.

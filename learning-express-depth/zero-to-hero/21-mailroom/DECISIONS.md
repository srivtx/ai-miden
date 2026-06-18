# The Decisions

> *"Email is the original API. The user is the recipient. SMTP is the protocol. Nodemailer is the library."*

## Decision 1: Nodemailer and not direct SMTP

**Alternative**: Use Node's `net` module to send SMTP directly.

**Why Nodemailer: SMTP is complex. Nodemailer handles authentication, TLS, attachments, etc. We don't write the protocol.

**Trade-off**: We depend on Nodemailer. It's well-maintained.

## Decision 2: Ethereal in dev, real provider in production

**Alternative**: Use a real provider in dev too. Or use a local SMTP server (MailHog, MailCatcher).

**Why Ethereal in dev: It's free. No setup. No real emails sent. The preview URL is logged so we can see what was sent.

**Trade-off**: The dev experience is different from production. In production, we use SendGrid (or similar).

## Decision 3: Tokens are hashed

**Alternative**: Store tokens in plaintext.

**Why hashed: If the database is leaked, the attacker has the tokens. They could use them to reset passwords. With hashed tokens, they can't reverse them.

**Trade-off**: We have to hash on every reset. Negligible cost.

## Decision 4: Tokens are single-use

**Alternative**: Allow reuse until expiration.

**Why single-use: An attacker who intercepts a token can only use it once. After the user resets, the token is invalid.

**Trade-off**: The user can't accidentally click the link twice. We delete the token after use.

## Decision 5: Tokens expire in 1 hour

**Alternative**: 24 hours, 7 days, never.

**Why 1 hour: A balance between UX and security. Long enough for the user to find the email. Short enough that an intercepted token is only useful for 1 hour.

**Trade-off**: A user who takes longer to click has to request a new reset. We accept this.

## Decision 6: No email enumeration

**Alternative**: Return "user not found" if the email doesn't exist.

**Why no enumeration: An attacker can use the error message to determine which emails are registered. We always return the same message, even if the user doesn't exist.

**Trade-off**: The user has to check their inbox to know if the reset was sent. We accept this for security.

## Decision 7: Welcome email but not verification

**Alternative**: Require email verification before allowing login.

**Why not require: Verification adds complexity (the user has to click the link, etc.). For this project, we send the welcome email but don't require verification. We could add it in a future project.

**Trade-off**: Unverified users can use the API. They have an `email_verified = false` flag, but it's not enforced.

## Decision 8: Plain text + HTML

**Alternative**: HTML only, or plain text only.

**Why both: Plain text is for older email clients and screen readers. HTML is for modern clients with formatting. We send both.

**Trade-off**: Slightly more code. We accept it for compatibility.

## Decision 9: No email queue

**Alternative**: Use BullMQ (project 26) to queue emails.

**Why not queue: For low volume, sending inline is fine. For high volume, you'd queue. We accept this for simplicity.

**Trade-off**: Sending an email blocks the request. If the SMTP server is slow, the request is slow. We accept this for now.

## Decision 10: No rate limiting on email

**Alternative**: Limit "forgot password" requests to prevent abuse.

**Why not: Out of scope. A malicious user could spam the email system. We'll add rate limiting in project 24.

**Trade-off**: A spammer could send thousands of emails. We accept this for now.

---

## What We Did Not Decide

- **Email verification requirement** — out of scope
- **Email queue** — out of scope (project 26)
- **Email rate limiting** — out of scope (project 24)
- **Email templates** (MJML, Handlebars) — out of scope
- **Bounce handling** — out of scope
- **Spam prevention (SPF, DKIM, DMARC)** — out of scope (provider handles)
- **Multi-language emails** — out of scope
- **Email analytics** — out of scope

Each is a future decision.

---

## The Meta-Decision: The API Talks to Users

For 20 projects, our API was silent. The user signed up and had no idea. They forgot their password and couldn't recover. They were alone.

Now the API talks. The user gets a welcome email. The user can request a password reset. The user receives notifications. The user is informed.

This is the foundation of *every* real user-facing product. Email is non-negotiable. The patterns (SMTP, transactional provider, tokens) are universal.

The next 19 projects will assume email exists. The path diverges:

- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The API talks to users. The path continues.

# The Thought

> *"SMTP is the protocol. Nodemailer is the library. Ethereal is the dev server. SendGrid is the prod server. The user is the recipient."*

## What SMTP Is

SMTP (Simple Mail Transfer Protocol) is the standard protocol for sending email. It's been around since 1982. It's text-based. It's used by every email server on the planet.

A typical SMTP conversation:

```
S: 220 mail.example.com ESMTP
C: HELO client.example.com
S: 250 mail.example.com
C: MAIL FROM:<alice@example.com>
S: 250 OK
C: RCPT TO:<bob@example.com>
S: 250 OK
C: DATA
S: 354 Send message content
C: From: alice@example.com
C: To: bob@example.com
C: Subject: Hello
C:
C: This is the message body.
C: .
S: 250 OK
C: QUIT
S: 221 Bye
```

This is way too low-level to do by hand. We use Nodemailer.

## What Nodemailer Does

Nodemailer is a Node library that sends emails. It:

1. Connects to an SMTP server
2. Authenticates (if required)
3. Builds the message (from, to, subject, body, attachments)
4. Sends it
5. Returns the result (message ID, accepted recipients, etc.)

The basic API:

```js
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: 'smtp.example.com',
  port: 587,
  auth: { user: '...', pass: '...' },
});

const info = await transporter.sendMail({
  from: '"Alice" <alice@example.com>',
  to: 'bob@example.com',
  subject: 'Hello',
  text: 'This is the message body.',
  html: '<p>This is the message body.</p>',
});
```

`createTransport` creates a reusable transporter. `sendMail` sends one email.

The transporter is reusable. You can send many emails with the same transporter.

## What Ethereal Is

Ethereal is a fake SMTP service. It doesn't actually deliver email. It captures the email and gives you a preview URL.

```js
const testAccount = await nodemailer.createTestAccount();
const transporter = nodemailer.createTransport({
  host: 'smtp.ethereal.email',
  port: 587,
  auth: { user: testAccount.user, pass: testAccount.pass },
});

const info = await transporter.sendMail({...});
const url = nodemailer.getTestMessageUrl(info);
// url: 'https://ethereal.email/message/abc...'
```

The URL is a web page that shows the email. You can see what the user would receive.

In production, you replace Ethereal with a real provider:

```js
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST, // e.g., 'smtp.sendgrid.net'
  port: 587,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
});
```

The same Nodemailer API. Just different SMTP server.

## What a Transactional Email Provider Does

A transactional email provider (SendGrid, Postmark, Resend, AWS SES) is a service that:

- Sends email on your behalf
- Manages IP reputation (so your emails don't go to spam)
- Provides analytics (open rates, click rates)
- Handles bounces and complaints
- Provides templates and tools

You send via their SMTP server (or API). They deliver to the recipient. They track everything.

In production, you *always* use a provider. You never send directly from your server. (Sending directly from your server is how spammers operate; your IP gets blacklisted.)

## The Password Reset Flow

The standard flow for password reset:

1. User requests reset: `POST /sessions/forgot { email }`
2. Server generates a random token, stores it in the database with an expiration
3. Server sends an email with a reset link: `https://app.com/reset?token=abc`
4. User clicks the link, sees a form for the new password
5. User submits: `POST /sessions/reset { token, newPassword }`
6. Server looks up the token, validates the expiration, hashes the new password, updates the user, deletes the token

The token is:

- Random (e.g., 32 bytes from `crypto.randomBytes`)
- Single-use (deleted after use)
- Time-limited (e.g., expires in 1 hour)
- Stored hashed (so even if the database is leaked, the tokens can't be reused)

## The Welcome Email Flow

1. User signs up: `POST /users { username, password, email }`
2. Server creates the user with `email_verified = false`
3. Server generates a verification token
4. Server sends a welcome email with a verification link
5. User clicks the link
6. User submits: `POST /users/verify { token }`
7. Server validates the token, sets `email_verified = true`, deletes the token

For this project, we implement the welcome email but not the verification flow (out of scope to keep the project focused).

## Common Confusions (read these)

**Confusion 1: "Why not just use `sendmail`?"**
`sendmail` is a Unix tool. It connects to localhost's SMTP server. It's complex to set up. It doesn't handle authentication, encryption, or providers. We use Nodemailer.

**Confusion 2: "Why not send directly from our server?"**
Your IP gets blacklisted. Email is a *reputation* game. Providers like SendGrid have established IPs. Use them.

**Confusion 3: "Why is the token single-use?"**
If a token is reused, an attacker who intercepts it can reset the password multiple times. Single-use limits the window.

**Confusion 4: "Why hash the token?"**
If the database is leaked, the attacker has the tokens. They could try to use them. If hashed, they can't reverse them to the actual token.

**Confusion 5: "What about email verification?"**
We send a welcome email but don't require verification. For high-security apps, you'd require verification before allowing login. We do that in a future project (RBAC).

**Confusion 6: "What if the email fails to send?"**
We log the error but don't fail the request. The user is created; the email failed. The user can request a password reset later.

**Confusion 7: "What about spam filters?"**
The provider handles SPF, DKIM, DMARC. We don't have to worry about it. Just send the email.

**Confusion 8: "Why port 587?"**
587 is the standard SMTP submission port. 25 is the original SMTP port (now often blocked). 465 is the legacy SMTPS port. 587 is the modern standard.

## What We Are About to Build

A ~400-line Express app that:

1. Uses Nodemailer with Ethereal in dev
2. Sends a welcome email on signup
3. Has a `POST /sessions/forgot` endpoint
4. Has a `POST /sessions/reset` endpoint
5. Stores reset tokens hashed, with expiration
6. Sends reset emails with the token link

The handlers are slightly different. The auth flow has new endpoints. The user creation triggers an email.

In [BUILD.md](./BUILD.md) we will go line by line.

# Project 21: The Mailroom

> *"A user signed up. They don't know if it worked. Send them an email."*

In projects 07-20, we have user signup, login, sessions, JWT, password reset (out of scope). But we never *notify* the user. They sign up, and... silence. They might wonder if the signup worked. They might forget their password and have no way to reset it.

This project adds **email**. We use **Nodemailer** — the de-facto Node email library — with **Ethereal** (a fake SMTP server for development) or a transactional provider like SendGrid, Postmark, or Resend for production.

We add:

1. An `email_verified` column to `users` (default false)
2. A welcome email on signup
3. A password reset flow (`POST /sessions/forgot` + `POST /sessions/reset`)
4. The reset email contains a one-time token

The flow: user signs up → welcome email sent. User forgets password → request reset → email with token → submit new password with token.

By the end, the API can communicate with users via email.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is email needed? What is a transactional email?
2. [The Thought](./THOUGHT.md) — How does SMTP work? What is Nodemailer? What is Ethereal?
3. [The Build](./BUILD.md) — Line-by-line construction of the mailroom
4. [The Decisions](./DECISIONS.md) — Why Nodemailer? Why Ethereal? Why not SES?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Email is sent via SMTP (Simple Mail Transfer Protocol). Nodemailer is a Node library that sends emails via SMTP. For development, we use Ethereal (a fake SMTP server that captures emails). For production, we'd use a real provider (SendGrid, Postmark). The flow: build a message (from, to, subject, body), pass it to Nodemailer, it sends via SMTP. The user receives the email.

---

## The Code

```bash
npm install nodemailer
```

```js
const nodemailer = require('nodemailer');

// In dev, use Ethereal (a fake SMTP server)
let transporter;

async function setupMailer() {
  if (process.env.NODE_ENV === 'production') {
    // Use a real provider in production
    transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: process.env.SMTP_PORT,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    });
  } else {
    // Use Ethereal in development
    const testAccount = await nodemailer.createTestAccount();
    transporter = nodemailer.createTransport({
      host: 'smtp.ethereal.email',
      port: 587,
      auth: { user: testAccount.user, pass: testAccount.pass },
    });
    logger.info('Ethereal account: ' + testAccount.user);
  }
}

setupMailer();

async function sendEmail({ to, subject, text, html }) {
  const info = await transporter.sendMail({
    from: '"My App" <noreply@example.com>',
    to,
    subject,
    text,
    html,
  });
  const url = nodemailer.getTestMessageUrl(info);
  if (url) logger.info('Preview URL: ' + url);
  return info;
}
```

Test it:

```bash
# Sign up
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long","email":"alice@example.com"}'
# (Server logs: "Ethereal account: ...")
# (Server logs: "Preview URL: https://ethereal.email/message/...")

# Open the Preview URL in a browser to see the email
```

The pain of "the user doesn't know what happened" is solved. The user gets an email. They can verify, reset, etc.

---

## What You Will Have Learned

- What SMTP is (a protocol for sending email)
- How Nodemailer sends emails
- The difference between a real SMTP server and Ethereal
- How to use a transactional email provider in production
- Why we never use SMTP directly (port 25) for transactional email

These are the foundations of *email*. From here, every project that needs to communicate with users via email uses Nodemailer (or similar).

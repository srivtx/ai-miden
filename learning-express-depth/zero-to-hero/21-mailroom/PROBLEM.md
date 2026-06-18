# The Problem

> *"A user signed up. The database has their record. The user has no idea."*

## Why Email Is Needed

In projects 07-20, the auth flow works: signup, login, sessions, JWT. But the user is in the dark. They:

- Sign up: "Did it work? Did I get an account?"
- Forget password: "How do I get back in?"
- Want to verify their email: "Is this email really mine?"
- Get a security alert: "Someone logged in from a new device. Was that me?"

Without email, the user can't know. Without email, the user can't recover. Without email, the user can't trust.

A real auth flow *requires* email:

- **Welcome email** after signup: "Welcome! Click here to verify your email."
- **Email verification**: confirms the user owns the email
- **Password reset**: "Click here to reset your password" (with a one-time token)
- **Security alerts**: "Someone logged in from a new device"

## What Pain Is This Solving?

Imagine you sign up for a service. You give your email. You click "Sign up." Nothing happens. No email. No welcome. No "click here to verify." You're confused. Is the signup broken? Did they lose your data? Should you try again?

A welcome email solves this. "Welcome to MyApp! Click here to verify your email." The user knows the signup worked. They feel welcomed. They verify their email.

## The Deeper Problem: SMTP Is Hard

SMTP (Simple Mail Transfer Protocol) is the standard protocol for sending email. But it's a 1980s protocol. It's text-based. It has weird quirks. Implementing SMTP from scratch is a bad idea.

You use a library (Nodemailer) and a *transactional email provider* (SendGrid, Postmark, Resend, AWS SES). The provider handles the SMTP server, the IP reputation, the spam filters. You just send the email.

For development, you don't want to send real emails. You want to *capture* them. **Ethereal** is a fake SMTP server that captures emails and gives you a preview URL. You can see the email in your browser without actually sending it.

## What This Project Will Solve

This project will:

1. Add `nodemailer` as a dependency
2. Set up a transporter (Ethereal in dev, real provider in production)
3. Add an `email_verified` column to `users` (default false)
4. Add a `password_reset_token` column to `users`
5. Add a `password_reset_expires_at` column
6. Send a welcome email on signup (with a verification link)
7. Add `POST /sessions/forgot` (request password reset)
8. Add `POST /sessions/reset` (reset password with token)
9. Send a password reset email

By the end, the API can send emails. The user can verify, reset, and recover.

## What This Project Will *Not* Solve

- **Email templates** — we use plain text or simple HTML. For styled emails, you'd use MJML, Handlebars, etc.
- **Email tracking** — open rates, click rates. Out of scope.
- **Bounce handling** — bounced emails. Out of scope.
- **Spam prevention** — SPF, DKIM, DMARC. Out of scope (the provider handles it).
- **Multi-language emails** — we use English. Out of scope.
- **Email queue** — sending is synchronous. For async, use project 26 (Queue).
- **Email rate limiting** — sending too many emails. Out of scope.

## The Question This Project Answers

> *"How do I send a notification to the user?"*

If you can answer: "use Nodemailer, send via SMTP (Ethereal in dev, real provider in prod), the user receives the email," you are ready for project 22.

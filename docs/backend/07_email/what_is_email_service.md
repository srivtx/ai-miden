## Why it exists (THE PROBLEM)

Your server generates an email: user signs up → welcome email. User forgets password → reset link. Payment succeeds → receipt. You can't call `sendEmail()` directly in the request handler — if the email service is slow (2s) or down, the user waits. For 100 signups/minute, you'd need 100 concurrent email connections.

The solution: **queue the email, don't send it in the request.** The handler enqueues a job: `{ type: 'welcome', to: 'user@test.com', data: {...} }`. A background worker picks it up, renders the HTML template, sends via SMTP. If SMTP fails, retry 3 times with backoff. The user's signup is instant. The email arrives 2 seconds later.

**Email service** = templating engine (Handlebars/MJML) + transport (Nodemailer for SMTP, SendGrid/Mailgun for API) + queue (Bull/Redis for async processing). Never `await transport.sendMail()` inside a request handler.

## The pattern

```javascript
// DO: enqueue, respond immediately
app.post('/signup', async (req, res) => {
  const user = await createUser(req.body);
  await emailQueue.add('welcome', { to: user.email, name: user.name });
  res.status(201).json(user); // instant response
});

// DON'T: await email inside handler
app.post('/signup', async (req, res) => {
  const user = await createUser(req.body);
  await transporter.sendMail({ to: user.email, ... }); // BLOCKS response
  res.status(201).json(user); // slow if SMTP is slow
});
```

## Common confusion

1. **"Just use `await sendMail()` — it's one line."** It works for 10 users. It breaks at 100 signups/minute when SMTP throttles. Queue from day one. Cost: 5 extra lines of code.

2. **"I don't need email templates — just plain text."** HTML emails have 2-3× higher engagement (click rates). Plain text looks like spam. Use MJML (responsive email framework) — handles Outlook/Gmail/iOS rendering quirks.

3. **"Gmail SMTP is free."** Gmail SMTP limits to 500 emails/day. For production: SendGrid (100/day free), Mailgun (100/day free), AWS SES ($0.10/1000). Use a transactional email service, not personal Gmail.

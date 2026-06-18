# The Build

> *"Send the email. The user receives it. The user clicks. The user resets."*

We are going to add email with Nodemailer. The change from project 20: add `email_verified` and `password_reset_token` columns, set up the mailer, send a welcome email, add password reset endpoints.

## Setup

```bash
npm install knex better-sqlite3 zod pino pino-http pino-pretty multer nodemailer
```

## The Migration

```js
// Add to MIGRATIONS
{
  version: 5,
  up: `
    ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE users ADD COLUMN password_reset_token TEXT;
    ALTER TABLE users ADD COLUMN password_reset_expires_at INTEGER;
  `,
},
```

Three new columns on `users`:
- `email_verified` (boolean as integer)
- `password_reset_token` (the hashed token)
- `password_reset_expires_at` (Unix timestamp)

## The Mailer Setup

```js
const nodemailer = require('nodemailer');

let transporter;

async function setupMailer() {
  if (process.env.SMTP_HOST) {
    // Use a real provider in production
    transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT) || 587,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    });
    logger.info('Using SMTP provider: ' + process.env.SMTP_HOST);
  } else {
    // Use Ethereal in development
    const testAccount = await nodemailer.createTestAccount();
    transporter = nodemailer.createTransport({
      host: 'smtp.ethereal.email',
      port: 587,
      auth: { user: testAccount.user, pass: testAccount.pass },
    });
    logger.info({ user: testAccount.user, pass: testAccount.pass }, 'Ethereal account created');
  }
}

setupMailer();

async function sendEmail({ to, subject, text, html }) {
  const info = await transporter.sendMail({
    from: '"MyApp" <noreply@myapp.com>',
    to,
    subject,
    text,
    html,
  });
  const url = nodemailer.getTestMessageUrl(info);
  if (url) {
    logger.info({ url }, 'Preview email at:');
  }
  return info;
}
```

### How it works

- If `SMTP_HOST` is set, use a real provider (production)
- Otherwise, create a test Ethereal account (development)
- `sendEmail` is a wrapper around `transporter.sendMail`
- The Ethereal preview URL is logged

## The Schemas

```js
const forgotPasswordSchema = z.object({
  email: z.string().email(),
});

const resetPasswordSchema = z.object({
  token: z.string().min(1),
  password: z.string().min(8).max(100),
});
```

## The Signup Handler (Updated)

```js
app.post('/users', validate(userCreateSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  const existing = await db('users').where({ username }).first();
  if (existing) {
    throw new ConflictError('username already taken');
  }
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });

  // Send welcome email (if email was provided)
  if (email) {
    const verifyToken = crypto.randomBytes(32).toString('hex');
    const hashedToken = crypto.createHash('sha256').update(verifyToken).digest('hex');
    await db('users').where({ id }).update({ email_verified: 0 }); // not yet verified

    await sendEmail({
      to: email,
      subject: 'Welcome to MyApp!',
      text: `Welcome, ${username}! Click here to verify your email: http://localhost:3000/users/verify?token=${verifyToken}`,
      html: `<p>Welcome, ${username}!</p><p>Click <a href="http://localhost:3000/users/verify?token=${verifyToken}">here</a> to verify your email.</p>`,
    });
  }

  res.status(201).json({ id, username, email: email || null });
}));
```

We send a welcome email if an email was provided. The email contains a verification link with a random token.

## The Password Reset Flow

### `POST /sessions/forgot` (request reset)

```js
app.post('/sessions/forgot', validate(forgotPasswordSchema), asyncHandler(async (req, res) => {
  const { email } = req.validated;
  const user = await db('users').where({ email }).first();

  // Always return 200 to prevent email enumeration
  if (!user) {
    return res.json({ message: 'If the email exists, a reset link has been sent' });
  }

  // Generate a random token
  const resetToken = crypto.randomBytes(32).toString('hex');
  const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');

  // Store the hashed token with expiration (1 hour)
  await db('users').where({ id: user.id }).update({
    password_reset_token: hashedToken,
    password_reset_expires_at: Date.now() + 60 * 60 * 1000,
  });

  // Send the reset email
  await sendEmail({
    to: email,
    subject: 'Reset your password',
    text: `Click here to reset your password: http://localhost:3000/sessions/reset?token=${resetToken}`,
    html: `<p>Click <a href="http://localhost:3000/sessions/reset?token=${resetToken}">here</a> to reset your password. This link expires in 1 hour.</p>`,
  });

  res.json({ message: 'If the email exists, a reset link has been sent' });
}));
```

**Important**: We always return the same response, even if the user doesn't exist. This prevents email enumeration — an attacker can't tell which emails are registered.

### `POST /sessions/reset` (reset with token)

```js
app.post('/sessions/reset', validate(resetPasswordSchema), asyncHandler(async (req, res) => {
  const { token, password } = req.validated;
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
  const user = await db('users').where({ password_reset_token: hashedToken }).first();

  if (!user || user.password_reset_expires_at < Date.now()) {
    throw new BadRequestError('Invalid or expired token');
  }

  const hash = await bcrypt.hash(password, 10);
  await db('users').where({ id: user.id }).update({
    hash,
    password_reset_token: null,
    password_reset_expires_at: null,
  });

  res.json({ message: 'Password reset successful' });
}));
```

We hash the incoming token and look it up. If found and not expired, we update the password and clear the token.

## Run It

```bash
# Sign up (sends a welcome email)
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long","email":"alice@example.com"}'
# (Server logs: "Preview email at: https://ethereal.email/message/...")

# Open the preview URL in a browser to see the welcome email

# Request a password reset
curl -X POST http://localhost:3000/sessions/forgot \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com"}'
# {"message":"If the email exists, a reset link has been sent"}
# (Server logs: "Preview email at: ...")

# Open the preview URL to see the reset email

# Reset the password (with the token from the email)
curl -X POST http://localhost:3000/sessions/reset \
  -H "Content-Type: application/json" \
  -d '{"token":"<token from email>","password":"newpass123"}'
# {"message":"Password reset successful"}
```

The user can sign up, get a welcome email, request a reset, get a reset email, and reset their password.

---

## Experiments

### Experiment 1: Check the email preview

After signing up, check the server logs. There's a preview URL. Open it in a browser. You see the email as the user would.

### Experiment 2: Test email enumeration prevention

```bash
curl -X POST http://localhost:3000/sessions/forgot \
  -H "Content-Type: application/json" \
  -d '{"email":"nonexistent@example.com"}'
# {"message":"If the email exists, a reset link has been sent"}
```

Same response, even though the email doesn't exist. The attacker can't tell.

### Experiment 3: Test expired tokens

Request a reset. Wait 1 hour. Try to use the token. Get "Invalid or expired token."

In dev, you can change the expiration to 10 seconds:
```js
password_reset_expires_at: Date.now() + 10 * 1000
```

### Experiment 4: Test single-use tokens

Use a token. Then try to use it again. Get "Invalid or expired token." The token is deleted after use.

### Experiment 5: Use a real provider

Set environment variables:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=<your-sendgrid-api-key>
```

The app uses SendGrid. Real emails are sent.

---

## Summary

You now have email. The server can send transactional emails. The user can verify, reset passwords, and receive notifications. The flow is the standard one used by every real app.

This is the foundation of *user communication*. From here, every project that needs to communicate with users via email uses Nodemailer (or similar). The patterns (SMTP, transactional provider, tokens) are universal.

In project 22, we will add caching. We will reduce database load by caching popular queries in memory.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

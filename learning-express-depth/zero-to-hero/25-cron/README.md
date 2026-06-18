# Project 25: The Cron

> *"Some things should happen on a schedule. Don't make the user trigger them."*

In projects 01-24, every action is triggered by a user request. But some things need to happen *automatically*:

- **Session cleanup**: delete expired sessions every hour
- **Daily digest**: email users a summary of activity at 9am
- **Scheduled posts**: publish a post at a future time
- **Database vacuum**: run SQLite VACUUM nightly to reclaim space
- **Token cleanup**: delete expired password reset tokens

These are **cron jobs** — scheduled tasks that run at fixed intervals or times. In Unix, `cron` is a daemon that runs commands at scheduled times. In Node, we have libraries like `node-cron` that let us schedule tasks in our app.

We use `node-cron` — a simple cron-like scheduler. We add a few cron jobs:

1. Session cleanup: every hour, delete expired sessions
2. Database vacuum: every day at 3am, run SQLite VACUUM
3. Daily digest: every day at 9am, email users a digest

By the end, the server runs scheduled tasks automatically. The user doesn't have to trigger them.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why do we need scheduled tasks? What is cron?
2. [The Thought](./THOUGHT.md) — How does node-cron work? What is the cron syntax?
3. [The Build](./BUILD.md) — Line-by-line construction of the cron jobs
4. [The Decisions](./DECISIONS.md) — Why node-cron? Why in-process? Why not BullMQ?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A cron job is a scheduled task that runs at fixed intervals or times. `node-cron` lets us schedule tasks in our Node app using cron syntax (`* * * * *` for "every minute"). We add a few jobs: session cleanup every hour, database vacuum every day at 3am, daily digest at 9am. The jobs run in the same process as the server. No external service needed.

---

## The Code

```bash
npm install node-cron
```

```js
const cron = require('node-cron');

// Session cleanup: every hour
cron.schedule('0 * * * *', async () => {
  // No sessions in our app (we use JWT), but if we had a sessions table, we'd delete expired ones
  logger.info('Running session cleanup');
});

// Database vacuum: every day at 3am
cron.schedule('0 3 * * *', async () => {
  await db.raw('VACUUM');
  logger.info('Database vacuumed');
});

// Daily digest: every day at 9am
cron.schedule('0 9 * * *', async () => {
  const users = await db('users').select('id', 'email', 'username').whereNotNull('email');
  for (const user of users) {
    await sendEmail({
      to: user.email,
      subject: 'Your daily digest',
      text: `Hi ${user.username}, here's your daily digest...`,
    });
  }
  logger.info({ count: users.length }, 'Daily digest sent');
});
```

The pain of "I need to run things on a schedule" is solved. The server runs tasks automatically.

---

## What You Will Have Learned

- What cron is (a daemon for scheduled tasks)
- The cron syntax (`* * * * *`)
- How to use `node-cron` in a Node app
- How to schedule recurring tasks
- How to log cron job execution
- The trade-offs of in-process scheduling vs. external

These are the foundations of *scheduled tasks*. From here, every project that needs periodic work can use cron.

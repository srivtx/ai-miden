# The Thought

> *"A clock ticks. When the minute changes, the job runs. The user is asleep."*

## What Cron Is

`cron` is a Unix daemon that runs commands at scheduled times. The schedule is a 5-field expression:

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── day of week (0-6, Sun=0)
│ │ │ └───── month (1-12)
│ │ └─────── day of month (1-31)
│ └───────── hour (0-23)
└─────────── minute (0-59)
```

Examples:

- `* * * * *` — every minute
- `0 * * * *` — every hour, on the hour
- `0 9 * * *` — every day at 9:00am
- `0 3 * * *` — every day at 3:00am
- `*/5 * * * *` — every 5 minutes

## How node-cron Works

`node-cron` is a Node library that parses cron expressions and schedules tasks. The basic usage:

```js
const cron = require('node-cron');

cron.schedule('* * * * *', () => {
  console.log('Running every minute');
});
```

The second argument is a function that runs at the scheduled time. The schedule is in cron syntax.

`node-cron` uses the same cron syntax as Unix cron. It runs in the same process as your app. The schedule is evaluated by the library; it doesn't depend on the OS.

## The Jobs

For this project, we add three jobs:

### Job 1: Session cleanup (every hour)

We don't have a `sessions` table in this project (we use JWT), but the pattern is the same. If we had a sessions table:

```js
cron.schedule('0 * * * *', async () => {
  await db('sessions').where('expires_at', '<', Date.now()).delete();
  logger.info('Session cleanup done');
});
```

For our app, we don't have sessions. The job is a no-op (just a log). The pattern is here for reference.

### Job 2: Database vacuum (every day at 3am)

SQLite has a `VACUUM` command that reclaims space from deleted rows. Over time, the database file can grow even after deletes. VACUUM shrinks it.

```js
cron.schedule('0 3 * * *', async () => {
  await db.raw('VACUUM');
  logger.info('Database vacuumed');
});
```

We run it at 3am, when traffic is low. The VACUUM locks the database briefly, so we don't want to do it during peak hours.

### Job 3: Daily digest (every day at 9am)

Email users a daily digest. For our app, we don't have much activity to summarize, so the digest is just a "hello" email. The pattern is here for reference.

```js
cron.schedule('0 9 * * *', async () => {
  const users = await db('users').select('id', 'email', 'username').whereNotNull('email');
  for (const user of users) {
    await sendEmail({
      to: user.email,
      subject: 'Your daily digest',
      text: `Hi ${user.username}, here's your daily digest.`,
    });
  }
  logger.info({ count: users.length }, 'Daily digest sent');
});
```

We loop over all users with an email and send each one a digest. For 1M users, this could take a while. We could use a queue (project 26) to send in parallel.

## Common Confusions (read these)

**Confusion 1: "Why not use the OS cron?"**
You can. The OS cron runs commands at scheduled times. But you'd have to write a script, set up the schedule, and manage it. `node-cron` is in the same process, easier to manage.

**Confusion 2: "What if the server restarts?"**
The schedule is lost. We don't persist cron jobs. When the server restarts, the jobs are re-scheduled on the next `node server.js`. We accept this for simplicity.

**Confusion 3: "What if a job takes longer than the interval?"**
The next run starts while the previous is still going. They overlap. For our jobs, this isn't a problem. For long-running jobs, you'd add overlap protection (a lock).

**Confusion 4: "What about retries?"**
We don't retry. We log the error. The next run is on schedule. For critical jobs, you'd add retries with exponential backoff.

**Confusion 5: "What about multi-server?"**
If you have 10 server processes, each runs the cron jobs. The jobs run 10 times. Bad. For multi-server, you'd use a separate worker process, or a leader-election system (only one process runs the jobs).

**Confusion 6: "What timezone?"**
`node-cron` uses the server's local timezone. For production, you'd use UTC and convert.

**Confusion 7: "What if a job throws?"**
We catch and log. The next job runs on schedule.

**Confusion 8: "Why `0 9 * * *` for 9am?"**
The 5 fields are minute, hour, day of month, month, day of week. `0 9 * * *` = at minute 0 of hour 9, every day. So 9:00am every day.

## What We Are About to Build

A ~450-line Express app that:

1. Has 3 cron jobs (session cleanup, vacuum, digest)
2. Logs every job execution
3. The handlers are unchanged

The new piece is the cron job registration. We register 3 jobs on server start. They run on their schedule.

In [BUILD.md](./BUILD.md) we will go line by line.

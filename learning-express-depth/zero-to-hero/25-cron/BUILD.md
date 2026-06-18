# The Build

> *"A clock ticks. When the minute changes, the job runs. The user is asleep."*

We are going to add scheduled tasks with `node-cron`. The change from project 24: add 3 cron jobs that run on a schedule.

## Setup

```bash
npm install node-cron
```

## The Code

### Imports

```js
const cron = require('node-cron');
```

### Job 1: Session Cleanup (every hour)

```js
cron.schedule('0 * * * *', async () => {
  try {
    // No sessions in our app, but the pattern is here
    logger.info('Session cleanup job started');
    logger.info('Session cleanup job done');
  } catch (err) {
    logger.error({ err: err.message }, 'Session cleanup job failed');
  }
});
```

We log the start and end. The try/catch logs errors. The job runs every hour on the hour.

### Job 2: Database Vacuum (every day at 3am)

```js
cron.schedule('0 3 * * *', async () => {
  try {
    logger.info('Database vacuum job started');
    await db.raw('VACUUM');
    logger.info('Database vacuum job done');
  } catch (err) {
    logger.error({ err: err.message }, 'Database vacuum job failed');
  }
});
```

`db.raw('VACUUM')` runs the SQLite VACUUM command. The job runs every day at 3am.

### Job 3: Daily Digest (every day at 9am)

```js
cron.schedule('0 9 * * *', async () => {
  try {
    logger.info('Daily digest job started');
    const users = await db('users').select('id', 'email', 'username').whereNotNull('email');
    for (const user of users) {
      try {
        await sendEmail({
          to: user.email,
          subject: 'Your daily digest',
          text: `Hi ${user.username}, here's your daily digest from MyApp.`,
        });
      } catch (err) {
        logger.error({ err: err.message, userId: user.id }, 'Failed to send digest to user');
      }
    }
    logger.info({ count: users.length }, 'Daily digest job done');
  } catch (err) {
    logger.error({ err: err.message }, 'Daily digest job failed');
  }
});
```

We loop over all users with an email and send each one a digest. Each user has their own try/catch so one failure doesn't stop the rest. The outer try/catch catches errors in the loop itself.

## When to Register

Register the jobs on server start, after the migration is done:

```js
migrate().then(() => {
  app.listen(3000, () => logger.info('Server listening on http://localhost:3000'));
  // Register cron jobs
  cron.schedule('0 * * * *', async () => { /* ... */ });
  cron.schedule('0 3 * * *', async () => { /* ... */ });
  cron.schedule('0 9 * * *', async () => { /* ... */ });
});
```

This ensures the database is ready before the jobs run.

## Run It

```bash
node server.js
# (cron jobs are scheduled; nothing runs immediately)

# Check the log to see the jobs are registered
# (you can add a startup log that lists the registered jobs)

# Wait for the scheduled time, see the jobs run
# (or, for testing, change the cron expression to '* * * * *' to run every minute)
```

For testing, change the cron expression to `* * * * *` (every minute). You'll see the jobs run every minute in the logs.

---

## Experiments

### Experiment 1: Run every minute (for testing)

```js
cron.schedule('* * * * *', async () => { /* ... */ });
```

Now the job runs every minute. Easy to see in the logs.

### Experiment 2: Add a startup log

```js
const jobs = [
  { name: 'session-cleanup', schedule: '0 * * * *', handler: sessionCleanupJob },
  { name: 'db-vacuum', schedule: '0 3 * * *', handler: dbVacuumJob },
  { name: 'daily-digest', schedule: '0 9 * * *', handler: dailyDigestJob },
];

for (const job of jobs) {
  cron.schedule(job.schedule, job.handler);
  logger.info({ name: job.name, schedule: job.schedule }, 'Cron job registered');
}
```

Now the startup logs show which jobs are registered.

### Experiment 3: Manually trigger a job

```js
const job = cron.schedule('0 9 * * *', dailyDigestJob);
job.start(); // start now
job.stop(); // stop
```

Useful for testing.

### Experiment 4: Use BullMQ instead

For multi-server or retries, use BullMQ (project 26). `node-cron` is in-process; BullMQ is on Redis.

### Experiment 5: Add a job to clean up expired tokens

```js
cron.schedule('0 * * * *', async () => {
  await db('users').where('password_reset_expires_at', '<', Date.now()).update({
    password_reset_token: null,
    password_reset_expires_at: null,
  });
  logger.info('Expired tokens cleaned up');
});
```

Cleanup for the password reset flow.

---

## Summary

You now have scheduled tasks. The server runs them automatically. The user doesn't have to trigger them.

This is the foundation of *automation*. From here, every project that needs periodic work can use cron. The patterns (cron syntax, in-process scheduling, logging) are universal.

In project 26, we will add a queue. We will move slow work (email send, image processing) off the request and into a background queue.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

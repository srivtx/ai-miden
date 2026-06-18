# The Build

> *"Add the job. Return. The worker picks it up. The user doesn't wait."*

We are going to move the welcome email from the request to a queue. The change from project 25: add BullMQ, add a job on signup, set up a worker.

## Setup

```bash
npm install bullmq
```

## The Code

### Imports

```js
const { Queue, Worker } = require('bullmq');
```

### The Queue

```js
const emailQueue = new Queue('email', { connection: redis });
```

Create the queue. The connection is our existing Redis. The queue is named 'email'. Jobs are added to this queue.

### The Worker

```js
const emailWorker = new Worker('email', async (job) => {
  if (job.name === 'welcome') {
    const { email, username } = job.data;
    await sendEmail({
      to: email,
      subject: 'Welcome to MyApp!',
      text: `Welcome, ${username}!`,
      html: `<p>Welcome, ${username}!</p>`,
    });
    logger.info({ userId: job.data.userId }, 'Welcome email sent');
  }
}, { connection: redis });

emailWorker.on('failed', (job, err) => {
  logger.error({ err: err.message, jobId: job.id }, 'Email job failed');
});
```

The worker:
- Listens for jobs in the 'email' queue
- If the job name is 'welcome', it sends the welcome email
- Logs the result
- Logs failures

The `on('failed', ...)` handler logs when a job fails. BullMQ retries up to the `attempts` option.

### Updated Signup Handler

```js
app.post('/users', validate(userCreateSchema), asyncHandler(async (req, res) => {
  const { username, password, email } = req.validated;
  if (await db('users').where({ username }).first()) throw new ConflictError('username already taken');
  const hash = await bcrypt.hash(password, 10);
  const [id] = await db('users').insert({ username, hash, email: email || null, created_at: Date.now() });

  // Add welcome email to the queue (instead of sending inline)
  if (email) {
    await emailQueue.add('welcome', { userId: id, email, username }, {
      attempts: 3,
      backoff: { type: 'exponential', delay: 1000 },
    });
  }

  res.status(201).json({ id, username, email: email || null });
}));
```

The handler:
- Creates the user (synchronous-ish)
- Adds a `welcome` job to the queue
- Returns 201

The user gets a fast response. The email is sent in the background.

### Queue Options

```js
await emailQueue.add('welcome', data, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
});
```

- `attempts: 3` — retry up to 3 times on failure
- `backoff: { type: 'exponential', delay: 1000 }` — wait 1s, 2s, 4s between retries

If the email send fails, BullMQ retries with backoff. After 3 failures, the job is in the failed set (for manual review).

## Run It

```bash
# Start Redis
redis-server

# Start the server
node server.js
# (worker is started; queue is registered)

# Sign up (returns immediately)
time curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long","email":"alice@example.com"}'
# (fast, ~50ms)
# {"id":1,"username":"alice","email":"alice@example.com"}

# Check the server log
# (within seconds, the worker picks up the job and sends the email)
# "Welcome email sent"
# "Preview email at: https://ethereal.email/..."
```

The signup is fast. The email is sent in the background.

---

## Experiments

### Experiment 1: Inspect the queue with redis-cli

```bash
redis-cli keys 'bull:*'
# bull:email:* (jobs, events, etc.)
```

The queue is stored in Redis. You can see the jobs.

### Experiment 2: Add a delay

```js
// In the worker
await new Promise(resolve => setTimeout(resolve, 5000));
```

The worker takes 5 seconds. The queue grows. Try adding 10 jobs quickly; they all sit in the queue.

### Experiment 3: Use a separate worker process

In a real app, the worker is in a separate process. Create `worker.js`:

```js
const { Worker } = require('bullmq');
const Redis = require('ioredis');
const nodemailer = require('nodemailer');

const redis = new Redis({ host: 'localhost', port: 6379 });

const transporter = nodemailer.createTransport({
  host: 'smtp.ethereal.email',
  port: 587,
  auth: { user: '...', pass: '...' },
});

async function sendEmail({ to, subject, text, html }) {
  await transporter.sendMail({ from: '"MyApp" <noreply@myapp.com>', to, subject, text, html });
}

const worker = new Worker('email', async (job) => {
  if (job.name === 'welcome') {
    const { email, username } = job.data;
    await sendEmail({ to: email, subject: 'Welcome!', text: `Welcome, ${username}!` });
  }
}, { connection: redis });

console.log('Worker started');
```

Run it: `node worker.js`. Now the worker is in a separate process. The server can be scaled independently.

### Experiment 4: Use the BullMQ UI

```bash
npm install @bull-board/express
```

```js
const { createBullBoard } = require('@bull-board/api');
const { BullMQAdapter } = require('@bull-board/api/bullMQAdapter');
const { ExpressAdapter } = require('@bull-board/express');

const serverAdapter = new ExpressAdapter();
serverAdapter.setBasePath('/admin/queues');

createBullBoard({
  queues: [new BullMQAdapter(emailQueue)],
  serverAdapter,
});

app.use('/admin/queues', serverAdapter.getRouter());
```

Visit `http://localhost:3000/admin/queues` to see the queue in a web UI.

### Experiment 5: Multiple queues

```js
const emailQueue = new Queue('email', { connection: redis });
const imageQueue = new Queue('image', { connection: redis });

// Different workers for different queues
const emailWorker = new Worker('email', handleEmail);
const imageWorker = new Worker('image', handleImage);
```

Multiple queues, one per concern. Each worker handles its own queue.

---

## Summary

You now have a queue. Slow work is moved off the request. The user gets a fast response. The work is done reliably in the background.

This is the foundation of *background work*. From here, every project that needs to do slow work asynchronously can use a queue. The patterns (BullMQ, Redis-backed, retries, backoff) are universal.

In project 27, we will add transactions. We will make multi-step writes atomic, so we don't end up in an inconsistent state.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

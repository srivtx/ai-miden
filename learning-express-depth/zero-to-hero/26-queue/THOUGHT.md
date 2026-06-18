# The Thought

> *"Add the job. Return. The worker picks it up. The user doesn't wait."*

## What a Queue Is

A queue is a buffer between producers and consumers. The producer adds jobs to the queue. The consumer (worker) pulls jobs from the queue and processes them.

```
Producer → Queue → Worker
   (request)        (background)
```

The producer and worker can be in the same process or different processes. They communicate via the queue (in our case, Redis).

The benefits:

- **Fast response**: the producer doesn't wait for the work to finish
- **Reliability**: jobs persist in the queue (Redis); if the worker crashes, the job is retried
- **Scale**: you can have multiple workers pulling from the same queue
- **Backpressure**: if the producer is faster than the worker, the queue grows; the worker catches up when it can

## BullMQ

BullMQ is the standard Node queue. It's:

- **Redis-backed**: jobs persist in Redis; jobs survive a restart
- **Reliable**: jobs are retried on failure
- **Observable**: you can see the queue, the jobs, the workers in the BullMQ UI
- **Performant**: thousands of jobs per second

The basic API:

```js
const { Queue, Worker } = require('bullmq');

// Producer
const queue = new Queue('email', { connection: redis });
await queue.add('welcome', { userId, email, username });

// Worker
const worker = new Worker('email', async (job) => {
  if (job.name === 'welcome') {
    // send the email
  }
}, { connection: redis });
```

The `Queue` and `Worker` share a connection to Redis. They can be in the same process or different processes.

## Adding a Job

`queue.add(name, data, options)`:

```js
await queue.add('welcome', { userId: 1, email: 'alice@example.com', username: 'alice' }, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
});
```

- `name`: the job name (we use 'welcome' for the welcome email)
- `data`: the data the worker needs
- `options.attempts`: retry up to 3 times
- `options.backoff`: wait 1s, 2s, 4s between retries (exponential)

If the job fails, BullMQ retries with the backoff. After 3 failures, the job goes to the failed set.

## Processing a Job

The worker's handler:

```js
const worker = new Worker('email', async (job) => {
  if (job.name === 'welcome') {
    const { email, username } = job.data;
    await sendEmail({ to: email, subject: 'Welcome!', text: `Welcome, ${username}!` });
  }
}, { connection: redis });
```

- `job.name` is the name we added with
- `job.data` is the data we passed
- The handler is async; BullMQ waits for the promise to resolve
- If the promise rejects, the job is marked as failed and retried

## The Flow

1. User signs up
2. We create the user in the database
3. We add a `welcome` job to the queue (with the user's email and username)
4. We return 201
5. The user gets a fast response
6. The worker picks up the job
7. The worker sends the email
8. The user receives the email

Steps 6-8 happen in the background. The user is not waiting for them.

## Common Confusions (read these)

**Confusion 1: "Why not just use `setImmediate` or `setTimeout`?"**
You can, for fire-and-forget tasks. But you lose reliability: if the process crashes, the work is lost. A queue persists the work in Redis.

**Confusion 2: "Why not use Node's `worker_threads`?"**
`worker_threads` is for CPU-intensive work. A queue is for I/O-bound work (like sending emails) that benefits from being on a different process or machine.

**Confusion 3: "Why BullMQ and not Bee-Queue, Kue, or agenda?"**
BullMQ is the modern standard. It's actively maintained. It has good documentation. It supports the features we need (retries, backoff, etc.).

**Confusion 4: "What if the worker is down?"**
The queue grows. When the worker comes back, it processes the backlog. The jobs are persisted in Redis.

**Confusion 5: "What if the same job is added twice?"**
BullMQ has a "jobId" option. If you set the same jobId, the second add is a no-op. We don't use this here, but it's a useful feature.

**Confusion 6: "What about idempotency?"**
If a job runs twice (e.g., the worker crashes after sending the email but before acking), the email is sent twice. For idempotency, you'd add a check (e.g., "did we already send this email?"). We don't do this here.

**Confusion 7: "Why Redis and not RabbitMQ, SQS, etc.?"**
Redis is simple. We already have it (project 23). For higher scale, use RabbitMQ or SQS.

**Confusion 8: "What about the BullMQ UI?"**
BullMQ has a UI for monitoring the queue. We don't add it here. You can run it as a separate process.

## What We Are About to Build

A ~450-line Express app that:

1. Has an `email` queue
2. The signup handler adds a `welcome` job instead of sending the email inline
3. A worker in the same process processes the queue
4. The worker sends the email
5. The user gets a fast response

The handlers are slightly different (we add to the queue instead of sending the email). The worker is a new piece.

In [BUILD.md](./BUILD.md) we will go line by line.

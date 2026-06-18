# Project 26: The Queue

> *"Don't make the user wait for slow work. Move it to the background."*

In project 21, we send a welcome email on signup. The email send blocks the request. If the SMTP server is slow, the user waits. If the SMTP server times out, the signup fails. The user retries. The duplicate email sends.

This project adds a **queue**. We use **BullMQ** — a Redis-backed queue for Node. Instead of sending the email inline, we add a job to the queue. A separate **worker** process picks up the job and sends the email. The user gets a fast response.

The flow:
1. User signs up
2. We add a `sendWelcomeEmail` job to the queue
3. We return 201 immediately
4. A worker picks up the job and sends the email
5. The user gets the email seconds later

We can have multiple workers. The queue distributes jobs. If one worker is busy, the next job goes to another. The queue persists in Redis, so jobs survive a server restart.

By the end, slow work is off the request. The user gets a fast response. The work is done reliably in the background.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is slow work bad in the request? What is a queue?
2. [The Thought](./THOUGHT.md) — How does BullMQ work? What is a worker?
3. [The Build](./BUILD.md) — Line-by-line construction of the queue
4. [The Decisions](./DECISIONS.md) — Why BullMQ? Why Redis? Why a separate worker?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A queue is a *buffer* between the request and the work. We add jobs to the queue. A worker (a separate process or thread) pulls jobs from the queue and does the work. The user gets a fast response. The work is done reliably in the background. BullMQ is the standard Node queue, backed by Redis. We use it to move slow work (email send) off the request.

---

## The Code

```bash
npm install bullmq
```

```js
const { Queue, Worker } = require('bullmq');

// Create the queue
const emailQueue = new Queue('email', { connection: redis });

// Producer: add a job
await emailQueue.add('welcome', { userId, email, username });

// Worker: process a job
const emailWorker = new Worker('email', async (job) => {
  if (job.name === 'welcome') {
    const { email, username } = job.data;
    await sendEmail({ to: email, subject: 'Welcome!', text: `Welcome, ${username}!` });
  }
}, { connection: redis });
```

Test it:

```bash
# Sign up (returns immediately)
curl -X POST http://localhost:3000/users -d '{"username":"alice","password":"hunter2long","email":"alice@example.com"}'
# 201 Created (fast)

# Wait a moment, the worker sends the email
# (Server logs: "Email sent for userId: 1")
# (Ethereal preview URL is logged)
```

The pain of "the user waits for the email" is solved. The user gets a fast response. The email is sent in the background.

---

## What You Will Have Learned

- What a queue is (a buffer between request and work)
- How BullMQ works (Redis-backed, persistent, with retries)
- How to add jobs (producer) and process them (worker)
- How to move slow work off the request
- The trade-offs of queues (latency, complexity, retries)

These are the foundations of *background work*. From here, every project that needs to do slow work asynchronously can use a queue.

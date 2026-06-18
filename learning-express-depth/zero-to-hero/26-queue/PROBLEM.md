# The Problem

> *"If the user is waiting for the email, they're not using the app."*

## Why Slow Work Is Bad in the Request

In project 21, our `POST /users` handler:

1. Hashes the password (fast, ~100ms)
2. Inserts the user (fast, ~10ms)
3. Sends the welcome email (slow, ~1-2 seconds)

The total request time is 1-2 seconds. The user waits. They see a spinner. They wonder if the signup worked.

The email send is the bottleneck. We don't need to send the email *before* returning the response. The user doesn't care if the email arrives in 100ms or 2 seconds — they just want to know the signup worked.

The fix: **move the email send off the request**. Return 201 immediately. Send the email in the background.

## What Pain Is This Solving?

Imagine the SMTP server is slow. 5 seconds per email. The user signs up. They wait 5 seconds. They refresh. They wait another 5 seconds. The signup didn't actually fail — it's just slow. The user thinks it's broken. They try a different email. Now we have two signups for the same person.

Or imagine the SMTP server is down. The email send fails. The signup fails. The user can't sign up. The site is broken because of an external service.

The fix: the signup should not depend on the SMTP server. The user is created in the database. The email is sent in the background. If the email fails, the user is still created. The admin can re-send the email later.

## The Deeper Problem: Reliability

When we move the email to the background, we need to make sure it actually gets sent. The user is created. The email should be sent. What if the worker crashes? What if Redis is down? What if the network drops?

The queue must be **reliable**:
- Jobs persist in Redis (durable)
- If a worker crashes, the job is retried by another worker
- If a job fails, it's retried with exponential backoff
- If a job keeps failing, it goes to a "dead letter" queue for manual review

BullMQ handles all of this. It's a production-ready queue.

## What This Project Will Solve

This project will:

1. Add `bullmq` as a dependency
2. Create an `email` queue
3. Move the welcome email from the request to the queue
4. Set up a worker to process the queue
5. Handle failures (retry, log)

By the end, the user gets a fast signup. The email is sent reliably in the background.

## What This Project Will *Not* Solve

- **Multiple worker processes** — we run one worker in the same process. For scale, run separate worker processes.
- **Delayed jobs** — we process jobs immediately. BullMQ supports delayed jobs (e.g., send in 1 hour). Out of scope.
- **Job priority** — we process jobs FIFO. BullMQ supports priorities. Out of scope.
- **Recurring jobs** — we use cron (project 25) for those. BullMQ also supports them. Different use case.
- **Job dependencies** — "do B after A finishes." Out of scope. We do simple jobs.
- **Job progress tracking** — "this job is 50% done." Out of scope.
- **Dead letter queue** — BullMQ has one, but we don't customize it.

## The Question This Project Answers

> *"How do I do slow work without making the user wait?"*

If you can answer: "add a job to a queue, a worker processes the job in the background, return a fast response," you are ready for project 27.

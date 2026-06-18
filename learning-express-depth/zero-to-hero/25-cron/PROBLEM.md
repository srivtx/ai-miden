# The Problem

> *"If the user has to trigger a scheduled task, it's not a scheduled task. It's a button."*

## Why Scheduled Tasks Are Essential

Some work doesn't happen in response to a user request:

- **Cleanup**: expired sessions, expired tokens, old logs
- **Reports**: daily digests, weekly summaries
- **Maintenance**: database vacuum, cache warmup
- **Scheduled actions**: publish a post at a future time, send a reminder

If we required the user to trigger these, they wouldn't happen. The user wouldn't click "Run cleanup" every day. The user wouldn't click "Send my digest" at 9am. The work would never get done.

The fix: **scheduled tasks**. The server runs them automatically, on a schedule. The user doesn't have to know.

## What Pain Is This Solving?

Imagine you have expired password reset tokens in your database. They should be deleted after 1 hour. But no user is going to click a "clean up expired tokens" button. The tokens accumulate. After a year, you have 1 million expired tokens. Queries are slow. Storage is bloated.

The fix: a cron job that runs every hour, deletes expired tokens. Automatic. The user doesn't have to know.

## The Deeper Problem: When Things Run

A scheduled task has a few questions:

1. **When?** — what time / interval?
2. **What process?** — same as the server? Or a separate worker?
3. **What if it fails?** — do we retry? Do we alert?
4. **What if it overlaps?** — what if the previous run is still going?

For this project, we keep it simple: in-process, on a schedule, no retry, no overlap protection. We log failures. For production, you'd add a separate worker process, retries, and a monitoring system.

## What This Project Will Solve

This project will:

1. Add `node-cron` as a dependency
2. Schedule a session cleanup job (every hour)
3. Schedule a database vacuum job (every day at 3am)
4. Schedule a daily digest job (every day at 9am)
5. Log every job execution

By the end, the server runs scheduled tasks automatically.

## What This Project Will *Not* Solve

- **External scheduler** — we use in-process. For multi-process / multi-server, you'd use a separate worker (BullMQ on Redis, or a separate Node process).
- **Retries** — we don't retry failed jobs. We just log the error.
- **Overlap protection** — if a job takes longer than the interval, the next run starts while the previous is still going. We don't protect against this.
- **Monitoring** — we log. We don't have a dashboard showing job status.
- **Cron expressions in the UI** — users can schedule jobs themselves. Out of scope.

## The Question This Project Answers

> *"How do I run tasks on a schedule without the user triggering them?"*

If you can answer: "use node-cron, schedule in the same process, log execution, the task runs automatically," you are ready for project 26.

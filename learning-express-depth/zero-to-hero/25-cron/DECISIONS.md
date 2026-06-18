# The Decisions

> *"Some things should happen on a schedule. The user doesn't have to know."*

## Decision 1: node-cron and not the OS cron

**Alternative**: Use the OS cron (set up a crontab entry).

**Why node-cron: In the same process. Easy to manage. No OS-level setup. The schedule is in the code.

**Trade-off**: Lost on server restart (we don't persist the schedule). For most apps, this is fine. For critical jobs, you'd use a persistent scheduler.

## Decision 2: In-process and not a separate worker

**Alternative**: Run the cron jobs in a separate Node process.

**Why in-process: Simpler. One deployment. No extra process to manage. For our scale, in-process is fine.

**Trade-off**: If the server is busy, the cron jobs are delayed. For production, you'd run jobs in a separate worker.

## Decision 3: No retries

**Alternative**: Retry on failure with exponential backoff.

**Why no: Simpler. We log the error. The next run is on schedule. For most jobs, a missed run is acceptable.

**Trade-off**: A failed job is lost. For critical jobs (e.g., billing), you'd add retries with a queue (project 26).

## Decision 4: No overlap protection

**Alternative**: Use a lock (Redis SETNX) to prevent overlap.

**Why no: Our jobs are fast. Overlap is unlikely. We accept the risk.

**Trade-off**: A long-running job could overlap with the next run. For long jobs, add a lock.

## Decision 5: Log every job

We log every job start, end, and error.

**Why: For debugging. We can see which jobs ran, when, and if they failed.

**Trade-off**: Log volume. We accept it.

## Decision 6: Use the server's local timezone

**Alternative**: Use UTC and convert.

**Why local: Simpler. For development, this is fine. We can convert to UTC later.

**Trade-off**: If the server is in a different timezone than the users, the schedules might be off. For production, use UTC.

## Decision 7: No monitoring / alerting

**Alternative**: Send a Slack message when a job fails.

**Why no: Out of scope. We log the error. The error shows up in the log aggregator. Someone will see it.

**Trade-off**: A failed job might go unnoticed. For critical jobs, add alerting.

## Decision 8: No leader election

**Alternative**: Only one process runs the jobs (others are idle).

**Why no: We run in a single process. For multi-process, we'd need a leader-election system.

**Trade-off**: If we scale to multiple processes, the jobs run multiple times. We'd need a separate worker or leader election.

## Decision 9: Three jobs for the demo

We added 3 jobs: session cleanup, vacuum, digest. The pattern is the same. We can add more.

**Why 3: A good demo. Different intervals (hourly, daily, daily). Different purposes (cleanup, maintenance, communication).

**Trade-off**: The actual content of the jobs is minimal (we don't have much to do). The pattern is the focus.

## Decision 10: No persistent schedule

**Alternative**: Store the schedule in the database. The server reads the schedule on startup.

**Why no: Simpler. The schedule is in the code. We accept that it can't be changed at runtime.

**Trade-off**: Changing the schedule requires a code change and deploy. For runtime changes, use a persistent scheduler.

---

## What We Did Not Decide

- **External scheduler** — out of scope (use BullMQ or similar)
- **Retries** — out of scope
- **Overlap protection** — out of scope
- **Monitoring** — out of scope (project 39)
- **Leader election** — out of scope
- **Persistent schedule** — out of scope
- **Alerting** — out of scope
- **Timezone handling** — out of scope
- **Dynamic schedules** — out of scope
- **Multi-region** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Has Automation

For 24 projects, every action was triggered by a user request. Nothing happened unless the user asked.

Now the server runs scheduled tasks. Session cleanup. Database vacuum. Daily digest. The work happens automatically. The user doesn't have to know.

This is the foundation of *every* production app. Scheduled tasks are non-negotiable for any non-trivial work. The patterns (cron syntax, in-process scheduling, logging) are universal.

The next 15 projects will assume automation exists. The path diverges:

- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server has automation. The path continues.

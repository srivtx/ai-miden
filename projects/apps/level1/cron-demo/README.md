# Cron Demo — Scheduled tasks with a real cron parser

Run tasks on a schedule. Same pattern as `node-cron`, but from scratch. Tasks are persisted in SQLite and run by a scheduler loop.

## Endpoints
```
GET  /tasks                  # list all tasks
POST /tasks        { name, schedule }   # create a task
POST /tasks/:id/run          # trigger manually
GET  /runs                   # recent run history
```

## Schedule format
Standard 5-field cron: `minute hour day month weekday`
- `* * * * *` — every minute
- `0 3 * * *` — every day at 3am
- `0 9 * * 1` — every Monday at 9am
- `*/5 * * * *` — every 5 minutes
- `0 0 1 1 *` — every January 1st at midnight

## Built-in tasks
- `health_check` — runs every minute
- `cleanup_logs` — runs at 3am
- `send_digest` — runs Monday 9am

## Try
```bash
# List tasks
curl http://localhost:3000/tasks

# Create a new task
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "refresh_cache", "schedule": "*/5 * * * *"}'

# Trigger manually
curl -X POST http://localhost:3000/tasks/t1/run

# See run history
curl http://localhost:3000/runs
```

## What this teaches
1. **Cron parsing**: 5-field format, wildcards, ranges, steps, lists
2. **Scheduler loop**: check every minute if any task should run
3. **Idempotency**: same task won't run twice in the same minute
4. **Run history**: track success/failure, output, duration
5. **Manual triggers**: test a task without waiting for the schedule
6. **Real cron** (Linux) uses the same format

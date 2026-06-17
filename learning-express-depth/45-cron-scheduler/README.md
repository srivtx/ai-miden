# 45 — Cron Scheduler

**New concept:** scheduled tasks. Run a function every minute, every hour, every Monday at 9am, etc.

Cron is a syntax for describing schedules. It's used everywhere:
- `* * * * *` = every minute
- `0 9 * * *` = every day at 9am
- `0 9 * * 1` = every Monday at 9am
- `*/5 * * * *` = every 5 minutes

The five fields are: minute, hour, day of month, month, day of week.

## Run it

```bash
npm install
node server.js
```

```bash
# See all schedules
curl http://localhost:3000/schedules

# Add a new schedule
curl -X POST http://localhost:3000/schedules/my-task \
  -H "Content-Type: application/json" \
  -d '{"schedule": "*/5 * * * *"}'
# Runs every 5 minutes

# Watch the server logs — tasks fire on schedule
```

## How to think about it

In Linux, cron is a system service that runs commands on a schedule. We can build the same thing in Node. The pattern: keep a list of tasks with schedules. Every minute (or every second), check if any should run.

## How to build it (line by line)

```js
function parseField(field, min, max) {
  if (field === '*') return Array.from({ length: max - min + 1 }, (_, i) => i + min);
  // ...
}
```

**Lines 9-16.** Parse one field of a cron expression. Return the list of values it matches.

**`field === '*'`** — wildcard, matches all values.

**`field.includes(',')`** — list: `1,3,5` matches 1, 3, 5.

**`field.includes('/')`** — step: `*/5` matches every 5th value.

**`field.includes('-')`** — range: `1-5` matches 1, 2, 3, 4, 5.

```js
function shouldRun(schedule) {
  const [m, h, d, mo, w] = schedule.split(' ');
  const now = new Date();
  return (
    parseField(m, 0, 59).includes(now.getMinutes()) &&
    parseField(h, 0, 23).includes(now.getHours()) &&
    // ...
  );
}
```

**Lines 19-30.** Check if a cron schedule matches the current minute.

**For each field, parse it, get the list of valid values, and check if the current value is in the list.**

```js
setInterval(() => {
  for (const [name, schedule] of Object.entries(schedules)) {
    if (shouldRun(schedule)) tasks[name]();
  }
}, 10000);
```

**Lines 47-52.** Every 10 seconds, check all schedules. If one should run, run it.

## What we learned

1. Cron syntax: 5 fields, each one is a number, range, list, or step
2. We can parse and check cron schedules in code
3. `setInterval` is the simple way to run something on a schedule
4. Real cron libraries (like `node-cron`) do this with more features

## What's next

In **46-pub-sub** we build a publish/subscribe system. One part of the app publishes events, others subscribe.

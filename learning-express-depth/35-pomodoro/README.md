# 35 — Pomodoro Timer

Track Pomodoro sessions. Each session has a task, duration, and when it was completed. New thing: **default values** that aren't `0`.

## Run it

```bash
npm install
node server.js
```

```bash
# Log a session (default 25 min)
curl -X POST http://localhost:3000/sessions \
  -H "Content-Type: application/json" \
  -d '{"task": "Write report"}'

# Log a 50-min deep work session
curl -X POST http://localhost:3000/sessions \
  -H "Content-Type: application/json" \
  -d '{"task": "Deep work", "duration": 50}'

# Stats
curl http://localhost:3000/stats
# { "sessions": 2, "totalMinutes": 75, "totalHours": "1.25" }
```

## How to think about it

A short one. Sometimes the smallest app is enough to teach a thing. The new thing: `duration: duration || 25` — if the client didn't send a duration, use 25 (a Pomodoro is 25 minutes by default).

## How to build it (line by line)

```js
duration: duration || 25,
```

**Line 12.** If `duration` is missing, use 25. If it's 0, also use 25 (because 0 is falsy in JavaScript). For Pomodoro, that's fine.

**For numbers, prefer `??`:** `duration ?? 25` only falls back to 25 if duration is `null` or `undefined`. `duration: 0` stays 0.

## What we learned

1. `||` falls back on any falsy value (0, '', null, undefined)
2. `??` falls back only on null/undefined
3. We've now built 35 small apps

## What's next

In **36-flashcards** we build flashcards. Each card has a question and answer. Mark as "known" or "review."

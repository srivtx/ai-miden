# 25 — Sleep Tracker

Track sleep. Each entry has bedtime and wake time. New thing: **computing a duration** from two timestamps.

## Run it

```bash
npm install
node server.js
```

```bash
# Log a sleep
curl -X POST http://localhost:3000/entries \
  -H "Content-Type: application/json" \
  -d '{"bedtime": "2024-12-14T23:00:00Z", "wakeTime": "2024-12-15T07:00:00Z"}'
# { "id": 1, "bedtime": "...", "wakeTime": "...", "durationHours": "8.00" }

# Average
curl http://localhost:3000/average
# { "averageHours": "8.00", "count": 1 }
```

## How to think about it

When you have two timestamps, you can subtract them. The result is in milliseconds. We convert to hours.

## How to build it (line by line)

```js
const bed = new Date(bedtime);
const wake = new Date(wakeTime);
const durationHours = (wake - bed) / (1000 * 60 * 60);
```

**Lines 11-13.** Convert strings to Date objects. Subtract them. Divide to get hours.

**`wake - bed`** gives the difference in milliseconds. `1000 * 60 * 60` is the number of milliseconds in an hour.

## What we learned

1. Date subtraction gives milliseconds
2. We can convert to any unit (seconds, minutes, hours, days)
3. We've now seen two date apps (calendar, sleep) — same pattern

## What's next

In **26-reading-list** we build a reading list. Books to read, books we've read, ratings.

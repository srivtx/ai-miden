# 19 — Habit Tracker

A habit has a name and a list of dates when it was done. New thing: **streak calculation** — how many days in a row has this habit been done?

## Run it

```bash
npm install
node server.js
```

```bash
# Create a habit
curl -X POST http://localhost:3000/habits \
  -H "Content-Type: application/json" \
  -d '{"name": "Read for 30 minutes"}'
# { "id": 1, "name": "Read for 30 minutes", "completions": [] }

# Mark it done today
curl -X POST http://localhost:3000/habits/1/complete
# { "id": 1, "name": "Read for 30 minutes", "completions": ["2024-..."] }

# Get the streak
curl http://localhost:3000/habits/1/streak
# { "habit": "Read for 30 minutes", "streak": 1, "completions": ["2024-..."] }
```

## How to think about it

This is similar to the calendar app. We store a list of dates and we do date math. The streak calculation is a small algorithm: walk backward from today, count consecutive days.

## How to build it (line by line)

```js
const today = new Date().toISOString().slice(0, 10);
```

**Line 19.** Get today's date as a string like `"2024-12-15"`. `toISOString()` gives the full timestamp. `slice(0, 10)` takes the first 10 characters, which is the date part.

```js
if (!habit.completions.includes(today)) {
  habit.completions.push(today);
}
```

**Lines 20-22.** Only add today if it's not already there. This prevents double-counting if someone marks the habit done twice in one day.

```js
let streak = 0;
let day = new Date();
while (dates.has(day.toISOString().slice(0, 10))) {
  streak++;
  day.setDate(day.getDate() - 1);
}
```

**Lines 33-37.** Walk backward from today, counting consecutive days.

- Start with today (`new Date()`)
- Check if today's date is in our completions set
- If yes, increment streak, move to yesterday
- If no, stop

**`day.setDate(day.getDate() - 1)`** — set the date to one day earlier. JavaScript Date handles this even across month boundaries.

## What we learned

1. Storing dates as strings (`"2024-12-15"`) is simple and works
2. We can do date math with `setDate` and `getDate`
3. The streak is a small algorithm
4. We've now built 14 apps

## What's next

In **20-url-shortener** we build a URL shortener. You give it a long URL, it gives you a short code. When someone visits the short code, they get redirected to the long URL.

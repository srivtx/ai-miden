# 22 — Mood Journal

A mood journal. Each entry has a mood (1-5), a note, and a date. New thing: **validation of numeric ranges** + a summary endpoint.

## Run it

```bash
npm install
node server.js
```

```bash
# Add an entry
curl -X POST http://localhost:3000/entries \
  -H "Content-Type: application/json" \
  -d '{"mood": 4, "note": "Good day, finished a project"}'

# Try a bad mood (rejected)
curl -X POST http://localhost:3000/entries \
  -H "Content-Type: application/json" \
  -d '{"mood": 7}'
# 422 { "error": "mood must be between 1 and 5" }

# Get the average mood
curl http://localhost:3000/summary
# { "average": "4.00", "count": 1 }
```

## How to think about it

Same CRUD + a summary endpoint. The new thing: validating a number is in a range. We use a simple `if` check. In a bigger app, you'd use a library like Zod or Joi.

## How to build it (line by line)

```js
if (mood < 1 || mood > 5) return res.status(422).json({ error: 'mood must be between 1 and 5' });
```

**Line 14.** Range check. If the mood is less than 1 OR more than 5, reject.

**`||`** is OR. If either side is true, the whole condition is true.

**`res.status(422)`** — 422 Unprocessable Entity. The body is well-formed but the content is wrong.

## What we learned

1. Numeric range checks are common validation
2. `||` is OR, `&&` is AND
3. 422 is the right code for validation failures
4. We've now seen validation in 3 different apps

## What's next

In **23-fitness-log** we build a fitness log. Each entry has an exercise, reps, and weight.

# 30 — Meal Planner

Plan meals for each day. Each day has breakfast, lunch, dinner. New thing: **lookup by date** (the date is the id).

## Run it

```bash
npm install
node server.js
```

```bash
# Plan a day
curl -X POST http://localhost:3000/days \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-12-15", "breakfast": "Eggs", "lunch": "Salad", "dinner": "Pasta"}'

# Get that day
curl http://localhost:3000/days/2024-12-15
# { "date": "2024-12-15", "breakfast": "Eggs", "lunch": "Salad", "dinner": "Pasta" }

# Update one meal
curl -X PATCH http://localhost:3000/days/2024-12-15 \
  -H "Content-Type: application/json" \
  -d '{"dinner": "Pizza"}'
```

## How to think about it

The "id" doesn't have to be a number. Here it's a date string. The URL captures it as a parameter: `/days/:date`. We look up by date instead of by number.

## How to build it (line by line)

```js
const day = days.find(d => d.date === req.params.date);
```

**Line 21.** Find the day where the date matches the URL parameter. Same as `find` with id, just using a string field.

## What we learned

1. Ids can be strings, not just numbers
2. The URL parameter is whatever you make it
3. Same shape, different field type

## What's next

In **31-grocery-list** we build a grocery list. Same CRUD, but the new thing is a "check off" pattern.

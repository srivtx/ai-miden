# 31 — Grocery List

A grocery list. Items with a "purchased" flag. Check them off as you shop. Same shape as todos, with a different name.

## Run it

```bash
npm install
node server.js
```

```bash
# Add items
curl -X POST http://localhost:3000/items -H "Content-Type: application/json" -d '{"name": "Milk", "quantity": 2}'
curl -X POST http://localhost:3000/items -H "Content-Type: application/json" -d '{"name": "Eggs"}'

# Check off "Milk"
curl -X PATCH http://localhost:3000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"purchased": true}'

# List
curl http://localhost:3000/items
# { "count": 2, "items": [{ "id": 1, "name": "Milk", "purchased": true }, { "id": 2, "name": "Eggs", "purchased": false }] }
```

## How to think about it

Same as the todo app. Just a different domain. The shape is the same because the problem is the same: a list of things with a status.

## How to build it (line by line)

```js
if (req.body.purchased !== undefined) item.purchased = req.body.purchased;
```

**Line 18.** Update `purchased` if the client sent it. We use `!== undefined` (not just truthy) so we can also set it to false.

## What we learned

1. The shape carries across domains
2. `!== undefined` is the right check for "did the client send this?"
3. We've now built 30+ apps with the same shape

## What's next

In **32-bug-tracker** we build a bug tracker. Bugs have a status (open/in_progress/closed) and a priority.

# 16 — Poll App

A poll has a question and options. Users vote. New thing: a **vote endpoint** that mutates state in a specific way.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a poll
curl -X POST http://localhost:3000/polls \
  -H "Content-Type: application/json" \
  -d '{"question": "Favorite color?", "options": ["Red", "Blue", "Green"]}'
# { "id": 1, "question": "Favorite color?", "options": [{ "text": "Red", "votes": 0 }, ...] }

# Vote for option 0
curl -X POST http://localhost:3000/polls/1/vote \
  -H "Content-Type: application/json" \
  -d '{"optionIndex": 0}'
# { "id": 1, "options": [{ "text": "Red", "votes": 1 }, ...] }

# Vote for option 1
curl -X POST http://localhost:3000/polls/1/vote \
  -H "Content-Type: application/json" \
  -d '{"optionIndex": 1}'

# See the poll
curl http://localhost:3000/polls/1
# options: [{ Red: 1 }, { Blue: 1 }, { Green: 0 }]
```

## How to think about it

This is a new kind of endpoint: a **mutation that doesn't create a new resource**. The poll exists. We're not creating a new thing — we're changing it. We call this an "action" endpoint.

## How to build it (line by line)

```js
options: options.map(text => ({ text, votes: 0 })),
```

**Line 14.** Convert a list of strings into a list of objects with `votes: 0`. We need the count field, so each option is an object, not a string.

**`map`** is like `forEach` but returns a new array. For each `text` in the input, we make `{ text, votes: 0 }`.

```js
poll.options[optionIndex].votes += 1;
```

**Line 30.** Increment the votes. The option's `votes` field goes up by 1.

**`optionIndex`** is the position in the array. 0 = first option, 1 = second, etc.

## What we learned

1. Some endpoints mutate existing things, not create new ones
2. We can validate input and return 422 for invalid options
3. `array.map` transforms an array into a new shape
4. We've now built 11 apps

## What's next

In **17-quiz-app** we build a quiz. Similar to a poll, but the question has a "correct" answer. After answering, the user gets a score.

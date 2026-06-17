# 17 — Quiz App

A quiz has questions, each with options and a correct answer. Submit answers, get a score.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a quiz (with correct answers in the body)
curl -X POST http://localhost:3000/quizzes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "JS Basics",
    "questions": [
      { "text": "What is 2+2?", "options": ["3", "4", "5"], "correctIndex": 1 },
      { "text": "What is a closure?", "options": ["A loop", "A function with access to outer variables", "An array method"], "correctIndex": 1 }
    ]
  }'

# Get the quiz (no answers shown)
curl http://localhost:3000/quizzes
# { "questions": [{ "text": "What is 2+2?", "options": [...] }, ...] }
# (no correctIndex!)

# Submit answers
curl -X POST http://localhost:3000/quizzes/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": [1, 1]}'
# { "score": 2, "total": 2, "percent": 100 }
```

## How to think about it

When we GET the quizzes, we **hide the correct answers**. The client should never see them — that would be cheating. We strip the field when returning the list.

When the client submits, we compare their answers to the correct ones and return a score.

## How to build it (line by line)

```js
quizzes.map(q => ({
  id: q.id,
  title: q.title,
  questions: q.questions.map(question => ({
    text: question.text,
    options: question.options,
  })),
})),
```

**Lines 11-18.** Map over quizzes, map over questions, and return only the fields the client should see. `correctIndex` is omitted — we don't send it.

**`map` inside `map`.** For each quiz, we map over its questions. We build a new shape for each question that excludes the answer.

## What we learned

1. Be careful about what you return — don't leak secrets
2. We can transform data before sending it
3. Score calculation is a simple loop with a counter
4. We've now built 12 apps

## What's next

In **18-recipe-app** we build a recipe book. Recipes have ingredients and steps. New thing: nested data — ingredients are a list inside each recipe.

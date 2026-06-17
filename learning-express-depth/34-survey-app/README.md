# 34 — Survey App

A survey has questions, each with options. People submit responses. We can compute the results.

## Run it

```bash
npm install
node server.js
```

```bash
# Create a survey
curl -X POST http://localhost:3000/surveys \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer satisfaction",
    "questions": [
      { "text": "How satisfied are you?", "options": ["Very", "Somewhat", "Not really"] }
    ]
  }'

# Submit responses
curl -X POST http://localhost:3000/surveys/1/responses \
  -H "Content-Type: application/json" \
  -d '{"answers": [0], "respondent": "Alice"}'

curl -X POST http://localhost:3000/surveys/1/responses \
  -H "Content-Type: application/json" \
  -d '{"answers": [1], "respondent": "Bob"}'

# Get the results
curl http://localhost:3000/surveys/1/results
# { "survey": "Customer satisfaction", "responseCount": 2, "results": [{ "question": "How satisfied are you?", "options": ["Very", "Somewhat", "Not really"], "counts": [1, 1, 0] }] }
```

## How to think about it

Two collections: surveys and responses. A response has answers (one per question). The results endpoint joins them — for each question, count how many people chose each option.

## How to build it (line by line)

```js
const results = survey.questions.map((q, qi) => {
  const counts = q.options.map(() => 0);
  for (const r of surveyResponses) {
    if (r.answers[qi] !== undefined) counts[r.answers[qi]]++;
  }
  return { question: q.text, options: q.options, counts };
});
```

**Lines 39-45.** For each question, count the answers.

**`q.options.map(() => 0)`** — start with a 0 for each option.

**`counts[r.answers[qi]]++`** — for each response, find the chosen option and increment its count.

## What we learned

1. Two collections: surveys and responses
2. The results endpoint joins them in code
3. We can build complex aggregations with loops
4. We've now seen multiple aggregation patterns

## What's next

In **35-pomodoro** we build a Pomodoro timer. Sessions have a start time and duration. We track completed sessions.

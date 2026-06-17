# 39 — Resume Builder

A resume with sections. New thing: **PUT** (full replacement) vs **PATCH** (partial update).

## Run it

```bash
npm install
node server.js
```

```bash
# PUT — replace the whole resume
curl -X PUT http://localhost:3000/resume \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "experience": [{ "company": "Acme", "title": "Engineer" }],
    "education": [{ "school": "MIT", "degree": "BS CS" }],
    "skills": ["JS", "Python"]
  }'

# PATCH — update just one section
curl -X PATCH http://localhost:3000/resume/skills \
  -H "Content-Type: application/json" \
  -d '["JS", "Python", "Rust", "Go"]'
```

## How to think about it

We've seen POST (create) and PATCH (partial update). Now we see PUT.

- **POST** = create a new thing
- **PATCH** = update some fields of an existing thing
- **PUT** = replace the whole thing

For a resume, PUT is useful: "I'm submitting my whole resume." PATCH is useful: "I just added a new skill."

## How to build it (line by line)

```js
app.put('/resume', (req, res) => {
  const { name, email, experience, education, skills } = req.body;
  resume = {
    name: name || '',
    email: email || '',
    experience: experience || [],
    education: education || [],
    skills: skills || [],
  };
  res.json(resume);
});
```

**Lines 15-26.** Replace the whole resume. Every field is overwritten.

**`|| []`** — defaults to empty array if the client didn't send it. So after PUT, the resume always has all five fields, even if some are empty.

## What we learned

1. PUT = full replacement
2. PATCH = partial update
3. Both are valid. The choice depends on your use case.
4. Defaults ensure consistent shape

## What's next

In **40-event-rsvp** (the last one) we build an event RSVP. Events have a list of attendees. People can RSVP yes or no.

# Learning Express — 40 Small Projects

This folder has 40 small apps. Each one is 30-60 lines. Each one teaches a slightly different shape.

**The point is not to memorize each one. The point is to see the patterns.**

## The 40 apps

### Part 1: The basics (01-05)
| # | Project | What it teaches |
|---|---|---|
| 01 | hello-server | Node's built-in `http` |
| 02 | hello-express | Express basics |
| 03 | todo-list | Empty list endpoint |
| 04 | todo-add | POST with JSON body |
| 05 | todo-delete | DELETE with URL parameter |

### Part 2: Variations (06-20)
| # | Project | What it teaches |
|---|---|---|
| 06 | notes-app | Title + body, GET one |
| 07 | blog-app | Adding a field (author) |
| 08 | products-app | Filter with `?category=` |
| 09 | chat-app | Nested resources (rooms/messages) |
| 10 | bookmarks-app | Uniqueness check |
| 11 | weather-app | Read-only, hardcoded data |
| 12 | calendar-app | Range queries (from/to) |
| 13 | contacts-app | Lookup by email |
| 14 | password-vault | Hashing (don't store plain text) |
| 15 | expense-tracker | Aggregations (summary) |
| 16 | poll-app | Voting (action endpoint) |
| 17 | quiz-app | Hiding fields (don't leak answers) |
| 18 | recipe-app | Nested data (lists inside a thing) |
| 19 | habit-tracker | Date math, streak |
| 20 | url-shortener | Random codes, redirect |

### Part 3: More variations (21-40)
| # | Project | What it teaches |
|---|---|---|
| 21 | emoji-app | Substring search |
| 22 | mood-journal | Range validation |
| 23 | fitness-log | Volume calculation |
| 24 | water-tracker | Filter by date (today) |
| 25 | sleep-tracker | Date subtraction → duration |
| 26 | reading-list | PATCH (partial update) |
| 27 | movie-watchlist | Updating a boolean |
| 28 | music-playlist | Two-level nesting |
| 29 | photo-album | Two-level nesting (different data) |
| 30 | meal-planner | Lookup by date string |
| 31 | grocery-list | Check-off pattern |
| 32 | bug-tracker | Multi-field filter |
| 33 | feedback-app | Distribution stats |
| 34 | survey-app | Per-question results |
| 35 | pomodoro | Default values |
| 36 | flashcards | Status field with default |
| 37 | kanban-board | Enum validation, action endpoint |
| 38 | inventory | Delta operations, low-stock query |
| 39 | resume-builder | PUT (full replacement) |
| 40 | event-rsvp | Update-or-create |

## How to use this folder

### For each project:

1. **Read the README.** It explains the new thing.
2. **Read the code.** It's short. Read every line.
3. **Run it.** `npm install && node server.js`
4. **Try the curl examples.** See what each one does.
5. **Modify it.** Add a field, change a value, break it, fix it.

### The order to do them:

- **01-05** — the todo app, building it up step by step
- **06-20** — fifteen more apps with the same CRUD shape, each with a new angle
- **21-40** — twenty more apps, each teaching another pattern

### Don't rush.

Each project is small. Spend 10-15 minutes on it. Read the README, run the code, try a curl, modify it. Move on.

After 40 projects, you'll have the structure in your head. Then you can build anything.

## The shape you'll see over and over

```js
const app = express();
app.use(express.json());

const things = [];  // the data, in memory

app.get('/things', (req, res) => {
  res.json({ count: things.length, things });
});

app.post('/things', (req, res) => {
  const thing = { id: things.length + 1, ...req.body };
  things.push(thing);
  res.status(201).json(thing);
});

app.get('/things/:id', (req, res) => {
  const thing = things.find(t => t.id === parseInt(req.params.id));
  if (!thing) return res.status(404).json({ error: 'Not found' });
  res.json(thing);
});

app.patch('/things/:id', (req, res) => {
  const thing = things.find(t => t.id === parseInt(req.params.id));
  if (!thing) return res.status(404).json({ error: 'Not found' });
  Object.assign(thing, req.body);
  res.json(thing);
});

app.delete('/things/:id', (req, res) => {
  const index = things.findIndex(t => t.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Not found' });
  things.splice(index, 1);
  res.status(204).end();
});

app.listen(3000);
```

This is 90% of every small app. The data is different. The shape is the same.

## After the 40

You'll be ready to:
- Add a database (so data survives restarts)
- Add user accounts (auth, login, sessions)
- Add tests (so you can change code without breaking)
- Add error handling (graceful failures)
- Build anything

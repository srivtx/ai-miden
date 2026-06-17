# Learning Express — 20 Small Projects

This folder has 20 small apps. Each one is 30-60 lines. Each one teaches a slightly different shape.

**The point is not to memorize each one. The point is to see the patterns.**

## The 20 apps

| # | Project | What it teaches |
|---|---|---|
| 01 | hello-server | Node's built-in `http` |
| 02 | hello-express | Express basics |
| 03 | todo-list | Empty list endpoint |
| 04 | todo-add | POST with JSON body |
| 05 | todo-delete | DELETE with URL parameter |
| 06 | notes-app | New app, similar shape (title + body) |
| 07 | blog-app | Adding a field (author) |
| 08 | products-app | Filter with query parameters |
| 09 | chat-app | Nested resources (rooms/messages) |
| 10 | bookmarks-app | Uniqueness check (no duplicate URLs) |
| 11 | weather-app | Read-only, hardcoded data |
| 12 | calendar-app | Range queries (from/to) |
| 13 | contacts-app | Lookup by non-id field |
| 14 | password-vault | Hashing (don't store plain text) |
| 15 | expense-tracker | Aggregations (summary endpoint) |
| 16 | poll-app | Voting (mutation) |
| 17 | quiz-app | Hiding fields (don't leak answers) |
| 18 | recipe-app | Nested data (lists inside a thing) |
| 19 | habit-tracker | Date math, streak calculation |
| 20 | url-shortener | Random codes, redirect |

## How to use this folder

### For each project:

1. **Read the README.** It explains the new thing.
2. **Read the code.** It's short. Read every line.
3. **Run it.** `npm install && node server.js`
4. **Try the curl examples.** See what each one does.
5. **Modify it.** Add a field, change a value, break it, fix it.

### The order to do them:

- **01-05** — the todo app, building it up step by step
- **06-09** — three more apps with the same CRUD shape
- **10-15** — more variations: uniqueness, lookups, hashing, aggregation
- **16-20** — final patterns: voting, hiding fields, nested data, redirects

### Don't rush.

Each project is small. Spend 10-15 minutes on it. Read the README, run the code, try a curl, modify it. Move on.

After 20 projects, you'll have the structure in your head. Then you can build anything.

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

app.delete('/things/:id', (req, res) => {
  const index = things.findIndex(t => t.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Not found' });
  things.splice(index, 1);
  res.status(204).end();
});

app.listen(3000);
```

This is 90% of every small app. The data is different. The shape is the same.

## After the 20

You'll be ready to:
- Add a database (so data survives restarts)
- Add user accounts (auth, login, sessions)
- Add tests (so you can change code without breaking)
- Add error handling (graceful failures)
- Build anything

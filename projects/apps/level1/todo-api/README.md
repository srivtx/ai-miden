# Todo API — Step 1 in the learning path

The classic first project. CRUD on a list of todos. Add filter, sort, mark done.

## Endpoints
```
GET    /todos                  # list (filter: ?done=true&priority=high&q=buy)
POST   /todos                  # create { title, priority? }
GET    /todos/:id              # read
PATCH  /todos/:id              # update { title?, done?, priority? }
DELETE /todos/:id              # delete
GET    /stats                  # total, done, pending, by priority
```

## Try
```bash
# Create
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Buy milk", "priority": "high"}'

# List
curl http://localhost:3000/todos
# { count: 1, items: [{ id: 1, title: "Buy milk", done: 0, priority: "high" }] }

# Mark done
curl -X PATCH http://localhost:3000/todos/1 -H "Content-Type: application/json" -d '{"done": true}'

# Filter
curl 'http://localhost:3000/todos?done=false&priority=high'

# Search
curl 'http://localhost:3000/todos?q=milk'

# Stats
curl http://localhost:3000/stats
# { total: 5, done: 2, pending: 3, byPriority: [...] }
```

## What this teaches
1. **REST basics**: GET/POST/PATCH/DELETE
2. **SQLite CRUD**: INSERT, SELECT, UPDATE, DELETE
3. **Filtering**: query params, LIKE for search
4. **Validation**: priority must be one of three values
5. **Aggregation**: COUNT, GROUP BY for stats

## Next project
→ **notes-api** — adds tags, full-text search, categories

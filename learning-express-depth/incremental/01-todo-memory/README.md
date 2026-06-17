# 01 — Todo (in-memory)

The starting point. In-memory CRUD. No database, no auth.

**What's here:**
- Create, read, update, delete todos
- Data lives in an array, lost on restart

**What's NOT here yet:**
- Database (data survives restart)
- Auth (anyone can do anything)
- Tags, categories
- Soft delete, audit
- Multi-tenancy

## Run
```bash
npm install && node server.js
```

```bash
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Buy milk"}'
curl http://localhost:3000/todos
curl -X PATCH http://localhost:3000/todos/1 -H "Content-Type: application/json" -d '{"done": true}'
curl -X DELETE http://localhost:3000/todos/1
```

## What this stage teaches
The basic CRUD shape. Every other stage adds ONE thing to this.

## Next
**02-todo-sqlite** — add a database. Data survives restart.

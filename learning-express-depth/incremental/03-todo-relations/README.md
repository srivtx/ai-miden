# 03 — Todo (relations)

Add tags (many-to-many) and categories (one-to-many).

**What's new:**
- Three new tables: `categories`, `tags`, `todo_tags`
- One-to-many: a todo has one category, a category has many todos
- Many-to-many: a todo has many tags, a tag has many todos
- Filter by category, by tag, or by search term
- Auto-create categories and tags if they don't exist

**Schema:**
```
categories:  id, name
todos:       id, title, done, category_id
tags:        id, name
todo_tags:   todo_id, tag_id  (junction table)
```

**Why a junction table?** Many-to-many needs a third table that says "this tag is on this todo." Each row is a connection.

## Run
```bash
npm install && node server.js
```

```bash
# Create a category
curl -X POST http://localhost:3000/categories -H "Content-Type: application/json" -d '{"name": "work"}'

# Create a todo with category and tags
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" \
  -d '{"title": "Finish report", "category": "work", "tags": ["urgent", "this-week"]}'

# Filter
curl 'http://localhost:3000/todos?category=work'
curl 'http://localhost:3000/todos?tag=urgent'
curl 'http://localhost:3000/todos?q=report'
```

## What this stage teaches
- One-to-many relations
- Many-to-many with junction tables
- JOIN queries
- Filter by related field

## Next
**04-todo-auth** — add users, login, JWT. Each user has their own todos.

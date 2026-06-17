# Notes API — Step 2 in the learning path

Builds on Todo. Adds: tags (many-to-many), full-text search, categories, archive.

## Endpoints
```
GET    /notes              # list, filter: ?q=keyword&category=work&tag=urgent&archived=false
POST   /notes              # create { title, body?, category?, tags?: ["urgent", "work"] }
GET    /notes/:id          # read (with tags)
PATCH  /notes/:id          # update any field including tags
DELETE /notes/:id          # delete (and its tag links)
GET    /tags               # list all tags with counts
```

## Try
```bash
# Create with tags
curl -X POST http://localhost:3000/notes -H "Content-Type: application/json" \
  -d '{"title": "API design", "body": "REST is good", "tags": ["work", "important"]}'

# Search across title and body
curl 'http://localhost:3000/notes?q=REST'

# Filter by tag
curl 'http://localhost:3000/notes?tag=important'

# See all tags with counts
curl http://localhost:3000/tags
# [{ name: "work", count: 5 }, { name: "important", count: 2 }]
```

## What this teaches
1. **Many-to-many**: notes ↔ tags via junction table
2. **JOIN queries**: pulling related data
3. **Full-text search**: simple LIKE-based search across multiple columns
4. **Tag management**: dedupe, count by usage
5. **Soft state**: archived flag instead of delete

## Next project
→ **blog-api** — adds: users, comments, slugs, published/draft, public + private routes

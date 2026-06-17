# Note API — Full REST app with user ownership and search

A complete note-taking API. Users register, login, create notes, search them.
Teaches: auth, CRUD, user ownership (can't see others' notes), search, pagination.

## Run
```
npm install && npm start
```

## Test
```
npm test
```

## Endpoints
```
POST   /auth/register    { name, email, password }
POST   /auth/login       { email, password }
GET    /notes?search=...&page=1&limit=10
POST   /notes            { title, content, tags:[] }
GET    /notes/:id
PATCH  /notes/:id        { title, content, tags }
DELETE /notes/:id
```

## What this teaches
- Multi-user data isolation (userId on every note)
- Full-text search across title + content
- Tag-based filtering
- PATCH for partial updates
- JWT auth guard middleware

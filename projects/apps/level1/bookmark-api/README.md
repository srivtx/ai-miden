# Bookmark API — Save, organize, and search bookmarks with tags

A complete bookmark management API. Users save URLs, tag them, search across title/URL/tags.

**Teaches:** CRUD, user ownership, multi-tag filtering, full-text search, duplicate detection, pagination.

## Run
```
npm install express jsonwebtoken bcryptjs && node server.js
```

## Endpoints
```
POST   /auth/register       { name, email, password }
POST   /auth/login          { email, password }
GET    /bookmarks?tag=dev&search=express&page=1&limit=20
POST   /bookmarks           { url, title, tags:[], description }
GET    /bookmarks/:id
PATCH  /bookmarks/:id
DELETE /bookmarks/:id
GET    /bookmarks/tags      List all user's tags with counts
```

## Key patterns learned
1. URL validation (must start with http)
2. Duplicate detection (same URL for same user = reject)
3. Tag-based filtering with multi-tag intersection
4. Full-text search across title + URL + description
5. Tag cloud endpoint (GET /bookmarks/tags)
6. Sorting by date or title

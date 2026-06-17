# Blog API — Step 3 in the learning path

Builds on Notes. Adds: users (authors), comments, slugs (URL-friendly IDs), published/draft, public + private routes.

## Endpoints
```
# Public
GET    /posts                              # list published posts
GET    /posts/:slug                        # read post (with comments)
GET    /users/:username                    # author profile + their posts

# User (X-User-Id header)
POST   /users                              # create user
POST   /posts                              # create post (draft by default)
PATCH  /posts/:id                          # edit (only your own)
DELETE /posts/:id                          # delete (only your own)
POST   /posts/:id/comments                 # comment on a post
```

## Try
```bash
# Create a user
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@x.com", "bio": "writer"}'

# Create a post (draft)
curl -X POST http://localhost:3000/posts \
  -H "Content-Type: application/json" \
  -H "X-User-Id: <user-id>" \
  -d '{"title": "My First Post", "body": "Hello world"}'
# 201, published: 0 (draft)

# Publish it
curl -X PATCH http://localhost:3000/posts/<post-id> \
  -H "Content-Type: application/json" \
  -H "X-User-Id: <user-id>" \
  -d '{"published": true}'

# Public list (only published)
curl http://localhost:3000/posts

# Read by slug
curl http://localhost:3000/posts/my-first-post

# Comment
curl -X POST http://localhost:3000/posts/<post-id>/comments \
  -H "Content-Type: application/json" \
  -H "X-User-Id: <other-user-id>" \
  -d '{"body": "Nice post!"}'
```

## What this teaches
1. **Multi-table relationships**: users → posts → comments
2. **Slugs**: URL-friendly identifiers (`my-first-post` not `p_abc123`)
3. **Public vs private**: published posts visible to all, drafts only to author
4. **Authorization**: only the author can edit/delete their post
5. **JOINs**: pulling related data efficiently
6. **Simple auth**: header-based user ID (real apps use JWT/session)

## Next project
→ **products-api** — adds: categories, prices, inventory, search, sort

# 01 — Posts (Blog)

Blog posts with slugs, public/private, basic CRUD.

**What's here:**
- Posts with title, body, excerpt, slug
- Status: `draft` or `published` (only published is publicly visible)
- Tags as a comma-separated string
- Slug auto-generated from title if not provided
- Excerpt included in lists, body only on detail

**Why slugs?** URLs are user-facing. `/posts/123` is ugly. `/posts/how-to-learn-backend` is readable. We use the slug as the URL.

**Why status?** Writers work in private. Readers see only published. Drafts are for the author, not the public.

## Run
```bash
npm install && node server.js
```

```bash
# Create a draft
curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "My First Post", "body": "Hello world", "author": "alice"}'
# 201 (status: "draft", not visible to public)

# Publish it
curl -X PATCH http://localhost:3000/posts/1 -H "Content-Type: application/json" \
  -d '{"status": "published"}'

# Now it's visible
curl http://localhost:3000/posts
curl http://localhost:3000/posts/my-first-post
```

## What this stage teaches
- Slugs (URL-friendly identifiers)
- Draft vs published (state)
- Excerpt for lists, body for detail

## Next
**02-comments** — readers can comment on posts. Nested replies.

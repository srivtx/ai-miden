# 05 — Media

Upload images. Posts can have featured images.

**What's new:**
- `media` table: filename, mime type, size, alt text, uploader
- Image-only upload (jpg, png, gif, webp)
- 10MB size limit
- Random filenames (prevents overwrites and path traversal)
- Alt text for accessibility
- `featured_media_id` on posts (the post's hero image)

**Why random filenames?** If a user uploads `evil.exe`, we don't save it as `evil.exe`. They could overwrite another file. Random names are safe.

**Why alt text?** Screen readers use it. Search engines use it. It's required for accessibility.

## Run
```bash
npm install
node server.js
```

```bash
# Upload an image
curl -X POST http://localhost:3000/media -F "file=@/path/to/image.png" -H "X-User-Id: alice"
# 201 { id: "m_...", url: "/media/abc123.png", size: 12345 }

# Add alt text
curl -X PATCH http://localhost:3000/media/m_xxx -H "Content-Type: application/json" \
  -d '{"alt_text": "A diagram showing the architecture"}'

# Create a post with this image
curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "Architecture Overview", "body": "...", "featured_media_id": "m_xxx", "author_id": "u_alice"}'
```

## What this stage teaches
- File upload with multer
- MIME type validation (only images)
- Size limits
- Random filenames
- Alt text for accessibility

## Next
**06-drafts** — improve the draft workflow. Save as you go, schedule for later.

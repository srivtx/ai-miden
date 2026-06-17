# 08 — Thumbnails (File Storage)

Generate image thumbnails. Don't make users download 4MB to see a preview.

**What's new:**
- `width`, `height` on files
- `thumbnail_url` for previews
- Custom thumbnail sizes

**Why thumbnails?** A 4MB photo is overkill for a preview. Generate a 200x200 thumbnail once, serve it for the list/preview. The user clicks to download the full version.

**In real life**, use `sharp` (Node) or `PIL` (Python) to actually resize. This demo just returns a URL.

## Run
```bash
npm install && node server.js
```

```bash
# Add an image file (with dimensions)
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "photo.jpg", "mime_type": "image/jpeg", "size_bytes": 4000000, "width": 4000, "height": 3000}'

# Get the thumbnail URL
curl http://localhost:3000/files/f_xxx/thumbnail

# Custom size
curl http://localhost:3000/files/f_xxx/thumbnail/100x100
```

## What we learned
- Thumbnail pattern
- Image dimensions metadata
- Custom sizes on demand

## Next
**09-compression** — compress files on upload to save space.

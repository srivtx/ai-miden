# 09 — Compression (File Storage)

Compress text files on upload. Save 70-90% on text. Track savings.

**What's new:**
- `original_size` and `stored_size` on files
- `compression_ratio` (how much we saved)
- gzip compression via Node's built-in `zlib`
- Stats endpoint: total savings

**Why compress text?** Text compresses incredibly well. A 1MB JSON file becomes ~100KB. Saves disk, saves bandwidth, saves money.

**Why not compress everything?** Images are already compressed (JPEG, PNG). Videos are too. Compressing them again wastes CPU and saves nothing. We only compress text.

**Trade-off:** CPU on upload vs disk/bandwidth savings. For text, compression always wins. For binaries, it doesn't.

## Run
```bash
npm install && node server.js
```

```bash
# Upload text (gets compressed)
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "doc.txt", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. ...(lots of text)..."}'
# 201 { ratio: 5.2 }  (compressed to 1/5th the size)

# Stats
curl http://localhost:3000/stats
# { total_original: 1000000, total_stored: 200000, ratio: 5 }
```

## What we learned
- gzip compression (built-in)
- Compression ratio tracking
- When to compress (text) vs not (binary)
- Space savings

## Next
**10-quotas** — the final stage. Per-user storage limits.

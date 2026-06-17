# 02 — Download (File Storage)

Serve files for download or preview. Stream large files.

**What's new:**
- `/files/:id/download` — download with `Content-Disposition: attachment`
- `/files/:id/preview` — inline view (browser shows it)
- Streamed (no buffering for large files)
- `Content-Type` and `Content-Length` set correctly

**Why two endpoints?** Download vs preview are different. A user clicks "download" — save to disk. A user clicks "preview" — show in browser. Same file, different UX.

**Why stream?** For a 1GB file, you don't want to load it all into memory. `fs.createReadStream` reads chunks as needed.

## Run
```bash
npm install && node server.js
```

```bash
# Upload
curl -X POST http://localhost:3000/files -F "file=@/path/to/image.png" -F "user_id=u_alice"

# Download
curl http://localhost:3000/files/f_xxx/download -o file.png

# Preview
curl http://localhost:3000/files/f_xxx/preview -o preview.png
```

## What this stage teaches
- Download vs preview
- Content-Disposition header
- Streamed file serving
- Content-Type / Content-Length

## Next
**03-folders** — organize files in folders (hierarchical).

# 42 — File Upload

**New concept:** receiving files from clients.

When you upload a file in a browser, the browser sends it as `multipart/form-data` — a different format than JSON. You need a library to parse it. The most popular is `multer`.

## Setup

```bash
npm install
node server.js
```

Make sure to put a file at `/path/to/some-image.png` for testing.

## Try it

```bash
# Upload a single file
curl -X POST http://localhost:3000/upload \
  -F "file=@/path/to/some-image.png"
# { "id": "abc123.png", "originalName": "image.png", "size": 12345, "mimetype": "image/png" }

# Upload multiple files
curl -X POST http://localhost:3000/upload-many \
  -F "files=@/path/to/file1.txt" \
  -F "files=@/path/to/file2.txt"
# { "count": 2, "files": [...] }

# Download a file
curl http://localhost:3000/files/abc123.png -o downloaded.png
```

## How to think about it

JSON is one type of body. Files are another. The browser sends files with a different format. The server needs a library to handle them.

## How to build it (line by line)

```js
const upload = multer({ storage, limits: { fileSize: 5 * 1024 * 1024 } });
```

**Line 21.** Configure multer. The storage tells it where to put files. The limits set the max size (5MB here).

```js
app.post('/upload', upload.single('file'), (req, res) => {
  res.json({ id: req.file.filename, ... });
});
```

**Line 24.** `upload.single('file')` is middleware. It expects one file in a field called `file`. After it runs, `req.file` has info about the uploaded file.

**`upload.array('files', 10)`** — for multiple files (up to 10).

## What we learned

1. Files use multipart/form-data, not JSON
2. Multer is the standard library for file uploads
3. Always set a size limit (don't let users upload 10GB files)
4. Generate random filenames (don't let users control the path)
5. Use `path.basename` to prevent path traversal attacks

## What's next

In **43-search-with-ranking** we build a search engine that ranks results by relevance.

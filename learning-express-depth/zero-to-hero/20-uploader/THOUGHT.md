# The Thought

> *"Multipart is a series of parts separated by a boundary. Each part is a header + body. The body is text or file."*

## The Multipart Format

A `multipart/form-data` body looks like this (simplified):

```
--boundary
Content-Disposition: form-data; name="title"

Hello
--boundary
Content-Disposition: form-data; name="image"; filename="photo.jpg"
Content-Type: image/jpeg

<binary data>
--boundary--
```

Each part starts with `--boundary`. The body of the part is the bytes until the next boundary. The last boundary ends with `--`.

The Content-Disposition header describes the part:
- `name="..."` — the field name (used in the form)
- `filename="..."` — the original filename (only for files)

The Content-Type header is the MIME type of the body (e.g., `text/plain`, `image/jpeg`).

## How Multer Parses

Multer is Express middleware. You register it on a route:

```js
app.post('/posts', upload.single('image'), handler);
```

`upload.single('image')` tells Multer: "expect a single file in the field named `image`."

When a request comes in, Multer:

1. Checks the Content-Type is `multipart/form-data`
2. Reads the body as a stream
3. Splits at the boundary
4. For each part:
   - If it's a text field, adds it to `req.body`
   - If it's a file, adds it to `req.file` (or `req.files` for multiple)
5. Calls `next()` when done

After Multer, `req.body` has the text fields and `req.file` has the file.

## Disk Storage

Multer's `diskStorage` saves files to disk. We configure:

```js
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    const id = crypto.randomUUID();
    cb(null, `${id}${ext}`);
  },
});
```

- `destination` — where to save the file. `UPLOADS_DIR` is `./uploads/`.
- `filename` — what to name the file. We use a UUID + the original extension. The UUID ensures uniqueness; the extension preserves the file type.

`cb` is a Node-style callback: `cb(error, value)`. We call `cb(null, value)` on success, `cb(error)` on failure.

## File Size Limit

```js
limits: { fileSize: 10 * 1024 * 1024 } // 10 MB
```

Multer rejects files larger than 10 MB. Without a limit, a malicious client could send a 10 GB file and OOM the server.

## MIME Type Filter

```js
fileFilter: (req, file, cb) => {
  if (!file.mimetype.startsWith('image/')) {
    return cb(new Error('Only images are allowed'));
  }
  cb(null, true);
},
```

We only accept images. Other types are rejected. The `mimetype` is from the Content-Type header of the part. `image/jpeg`, `image/png`, `image/gif` all start with `image/`.

## Serving Files

```js
app.use('/uploads', express.static(UPLOADS_DIR));
```

`express.static` serves files from a directory. The first argument is the URL prefix; the second is the directory.

When a request comes in for `/uploads/abc.jpg`, Express looks for `./uploads/abc.jpg` and serves it.

## The `image_url` Column

We add a column to `posts`:

```sql
ALTER TABLE posts ADD COLUMN image_url TEXT
```

The migration (added to the `MIGRATIONS` array) adds the column. Existing posts have `NULL` for `image_url`.

The handler sets `image_url` to the file URL if a file was uploaded, or `NULL` if not.

## Common Confusions (read these)

**Confusion 1: "Why not just use base64 in JSON?"**
You can. `{"image": "data:image/jpeg;base64,..."}`. But base64 inflates the size by 33%. Multipart is more efficient for binary data.

**Confusion 2: "Why not use S3 directly?"**
You can. We save to disk for simplicity. In production, you'd use S3. The pattern is the same: receive the file, save it somewhere, store the URL.

**Confusion 3: "Why a UUID for the filename?"**
To prevent collisions. If two users upload "photo.jpg," they'd overwrite each other. The UUID ensures uniqueness.

**Confusion 4: "Why serve files from our server?"**
For development, it's fine. For production, you'd use a CDN (CloudFront, Cloudflare) and S3. The server shouldn't serve static files in production.

**Confusion 5: "What about image processing?"**
We don't resize or compress. The user uploads a 5 MB image, we store a 5 MB image. For a profile picture, you'd resize to 200x200. Use Sharp.

**Confusion 6: "What about authentication on file access?"**
`/uploads/abc.jpg` is public. Anyone with the URL can see it. For private files, you'd check auth before serving.

**Confusion 7: "What about virus scanning?"**
We don't scan. A malicious user could upload a virus. Use ClamAV or a similar service.

**Confusion 8: "Why Multer and not busboy?"**
Multer is built on busboy. Multer adds the Express integration. We use Multer.

## What We Are About to Build

A ~350-line Express app that:

1. Uses Multer for `multipart/form-data` parsing
2. Saves files to `uploads/` with UUID names
3. Has a 10 MB file size limit
4. Accepts only image files
5. Serves uploaded files via `express.static`
6. Has an `image_url` column on `posts`
7. Updates `POST /posts` to accept an `image` field

The handler is slightly different. It uses `upload.single('image')` middleware. `req.file` has the uploaded file. We save the URL to the database.

In [BUILD.md](./BUILD.md) we will go line by line.

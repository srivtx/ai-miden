# The Build

> *"Multipart is a series of parts. Each part is a header + body. The body is text or file."*

We are going to add file upload with Multer. The change from project 19: add `image_url` column, configure Multer, update `POST /posts` to accept an image.

## Setup

```bash
npm install knex better-sqlite3 zod pino pino-http pino-pretty multer
```

## The Migration

```js
// Add to MIGRATIONS
{
  version: 4,
  up: `ALTER TABLE posts ADD COLUMN image_url TEXT`,
},
```

Existing posts have `NULL` for `image_url`. New posts can have a URL or NULL.

## The File Structure

```
project/
  server.js
  uploads/        <-- created automatically
    abc123.jpg
    def456.png
```

## The Code

### Imports

```js
const multer = require('multer');
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
```

### The Uploads Directory

```js
const UPLOADS_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR);
```

We create the `uploads/` directory if it doesn't exist. `__dirname` is the directory of the current file.

### The Multer Configuration

```js
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    const id = crypto.randomUUID();
    cb(null, `${id}${ext}`);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.startsWith('image/')) {
      return cb(new ValidationError([{ path: 'image', message: 'Only images are allowed' }]));
    }
    cb(null, true);
  },
});
```

#### `diskStorage`

Tells Multer to save files to disk:
- `destination` — `./uploads/`
- `filename` — `{uuid}{ext}` (e.g., `abc123.jpg`)

#### `limits.fileSize`

10 MB max. Larger files are rejected.

#### `fileFilter`

Only images. Other MIME types are rejected with a `ValidationError`.

### Serve Static Files

```js
app.use('/uploads', express.static(UPLOADS_DIR));
```

`express.static(UPLOADS_DIR)` serves files from `./uploads/` at the URL prefix `/uploads`.

When the client requests `/uploads/abc123.jpg`, Express serves `./uploads/abc123.jpg`.

### Updated `POST /posts`

```js
app.post('/posts', authMiddleware, upload.single('image'), validate(postCreateSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const imageUrl = req.file ? `/uploads/${req.file.filename}` : null;
  const [id] = await db('posts').insert({
    user_id: req.user.userId,
    title,
    body,
    image_url: imageUrl,
    created_at: Date.now(),
  });
  req.log.info({ postId: id, hasImage: !!req.file }, 'post created');
  res.status(201).json({ id, userId: req.user.userId, title, body, imageUrl });
}));
```

#### The middleware chain

1. `authMiddleware` — verify the JWT
2. `upload.single('image')` — parse the multipart body. `req.file` has the file (if any). `req.body` has the text fields.
3. `validate(postCreateSchema)` — validate the text fields (title, body)
4. The handler

`upload.single('image')` is *before* `validate`. Why? Because Multer populates `req.body` from the multipart parts. The validator reads `req.body`. So Multer must run first.

#### The handler

- `req.validated.title` and `req.validated.body` come from the validator
- `req.file` is the uploaded file (set by Multer)
- `imageUrl` is the URL of the uploaded file, or `null` if no file

We insert the post with the `image_url` column.

### Error Handling

If Multer throws (file too large, wrong type, etc.), it's a regular error. Our error wall catches it. We should map Multer errors to specific status codes:

```js
// In errorHandler
if (err instanceof multer.MulterError) {
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(413).json({ error: 'File too large', code: 'FILE_TOO_LARGE' });
  }
  // ... other Multer errors
}
```

Out of scope for this project. We'll add in a future project.

## Run It

```bash
# Create a test image
curl -o /tmp/test.jpg https://via.placeholder.com/300.jpg

# Login
TOKEN=$(curl -X POST http://localhost:3000/sessions \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2long"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# Create a post with an image
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Hello" \
  -F "body=World" \
  -F "image=@/tmp/test.jpg"
# {"id":1,"title":"Hello","body":"World","imageUrl":"/uploads/abc123.jpg"}

# Fetch the post
curl http://localhost:3000/posts/1
# {"id":1,"title":"Hello","body":"World","imageUrl":"/uploads/abc123.jpg",...}

# Fetch the image
curl http://localhost:3000/uploads/abc123.jpg -o downloaded.jpg
```

The image is uploaded, stored, and served. The URL is in the response.

---

## Experiments

### Experiment 1: Create a post without an image

```bash
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=No image" \
  -F "body=Just text"
# {"id":2,"title":"No image","body":"Just text","imageUrl":null}
```

`imageUrl` is `null`. The handler gracefully handles no file.

### Experiment 2: Try a non-image file

```bash
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Test" \
  -F "body=Test" \
  -F "image=@/etc/passwd"
# {"error":"Validation failed","code":"VALIDATION","issues":[{"path":"image","message":"Only images are allowed"}]}
```

The file filter rejects non-images.

### Experiment 3: Try a file too large

```bash
# Create a 20 MB file
dd if=/dev/zero of=/tmp/big.jpg bs=1M count=20

curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Test" \
  -F "body=Test" \
  -F "image=@/tmp/big.jpg"
# (rejected with an error)
```

The 10 MB limit kicks in. The error is a Multer error (mapped to 413 in a future project).

### Experiment 4: Multiple files

```js
app.post('/posts', authMiddleware, upload.array('images', 5), ...);
```

`upload.array('images', 5)` accepts up to 5 files in the `images` field. `req.files` is an array.

### Experiment 5: Multiple fields

```js
upload.fields([{ name: 'image', maxCount: 1 }, { name: 'attachment', maxCount: 3 }]);
```

Multiple fields, each with a max count.

### Experiment 6: Memory storage

```js
const storage = multer.memoryStorage();
```

Stores files in memory as a `Buffer`. Useful for small files or when you want to process them before saving. For large files, disk is better.

---

## Summary

You now have file upload. The client can attach an image to a post. The server stores it. The URL is in the response. The file is served via `express.static`.

This is the foundation of *every* API that accepts files. From here, every project that needs file upload uses Multer (or similar). The patterns (multipart, disk storage, static serving) are universal.

In project 21, we will add email. We will send notifications (signup confirmation, password reset) using a transactional email provider.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.

# Project 20: The Uploader

> *"The body is in the URL. The body is in the body. The body is also in the file."*

In projects 05 and 14, we parse the request body as JSON. But not all data is JSON. Users want to upload images, videos, PDFs, and other files. These come as `multipart/form-data` — a different format with multiple parts (text fields + binary files).

This project teaches file upload. We:

1. Accept `multipart/form-data` requests
2. Parse the parts: text fields + files
3. Save the files to disk
4. Return the file URL in the response
5. Add an `image_url` column to `posts` (for post images)

We use **Multer** — the de-facto Node middleware for `multipart/form-data`. It parses the parts and gives us the files. We then save them to disk (or S3, in a future project).

By the end, the client can attach an image to a post.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is multipart/form-data different? What is file upload?
2. [The Thought](./THOUGHT.md) — How does multipart work? What is Multer? Where do we save files?
3. [The Build](./BUILD.md) — Line-by-line construction of the uploader
4. [The Decisions](./DECISIONS.md) — Why Multer? Why disk? Why not S3 directly?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

`multipart/form-data` is a request format that bundles multiple parts (text fields, files) into one request. Each part has its own headers (Content-Type, filename). Multer parses these parts and gives us `req.body` (text fields) and `req.file` (or `req.files` for multiple). We save the file to a directory and store the URL in the database. The client gets a URL to display the image.

---

## The Code

```bash
npm install multer
```

```js
const multer = require('multer');
const path = require('node:path');
const fs = require('node:fs');

const UPLOADS_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR);

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
      return cb(new Error('Only images are allowed'));
    }
    cb(null, true);
  },
});

// Serve uploaded files
app.use('/uploads', express.static(UPLOADS_DIR));

// Create post with image
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
  res.status(201).json({ id, userId: req.user.userId, title, body, imageUrl });
}));
```

Test it:

```bash
# Create a post with an image
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Hello" \
  -F "body=World" \
  -F "image=@/path/to/photo.jpg"
# {"id":1,"title":"Hello","body":"World","imageUrl":"/uploads/abc123.jpg"}

# Fetch the post
curl http://localhost:3000/posts/1
# {"id":1,"title":"Hello","body":"World","imageUrl":"/uploads/abc123.jpg",...}

# Fetch the image
curl http://localhost:3000/uploads/abc123.jpg -o photo.jpg
```

The pain of "I can't attach an image" is solved. The client can upload an image. The server stores it. The URL is in the response.

---

## What You Will Have Learned

- What `multipart/form-data` is (a request format for files + fields)
- How Multer parses multipart requests
- The difference between `req.body` (text) and `req.file` (file)
- How to save files to disk with a unique name
- How to serve static files with `express.static`
- File size limits and MIME type filters

These are the foundations of *file upload*. From here, every project that accepts files uses Multer (or similar). The patterns (multipart, disk storage, static serving) are universal.

# The Connect

> *"The API accepts files. Now we need email, caching, and the rest of the operations."*

This project added file upload with Multer. The pain of "I can't attach an image" is solved. The client can upload an image. The server stores it. The URL is in the response. The file is served via `express.static`.

But the API is still limited:

1. **No email** — can't send signup confirmations, password resets, notifications.
2. **No caching** — every request hits the database.
3. **No Redis** — sessions and cache are in memory.
4. **No rate limiting** — a malicious client can hammer endpoints.
5. **No cron** — things that should fire on a schedule don't.
6. **No queue** — slow work blocks the request.
7. **No transactions** — multi-step writes can fail mid-way.

Projects 21-27 (rest of Phase 4) will fix these. After Phase 4, the API has *all* the real-world operations: file upload, email, caching, rate limiting, cron, queue, transactions.

## What Works

- File upload with Multer
- 10 MB file size limit
- Image MIME type filter
- UUID filenames
- Static file serving via `express.static`
- `image_url` column on `posts`
- `POST /posts` accepts an `image` field

## What Doesn't Work

### 1. No email

Can't send signup confirmations, password resets, notifications.

**The pain**: Email. Project 21 (Mailroom).

### 2. No caching

Every request hits the database. For "popular posts" or "user profile," we re-query the same data.

**The pain**: Caching. Project 22 (Cache).

### 3. No Redis

Sessions and cache are in memory. Multi-process / multi-region is hard.

**The pain**: Redis. Project 23.

### 4. No rate limiting

A malicious client can hammer endpoints.

**The pain**: Rate limiting. Project 24.

### 5. No cron

Things that should fire on a schedule (session cleanup, daily digest) don't.

**The pain**: Cron. Project 25.

### 6. No queue

Slow work (email send, image processing) blocks the request.

**The pain**: Queue. Project 26.

### 7. No transactions

Multi-step writes can fail mid-way, leaving the database in a bad state.

**The pain**: Transactions. Project 27.

### 8. No CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 9. No security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 10. No tests

We can't verify the upload works.

**The pain**: Tests. Project 36.

---

## What This Project Forbids Us From Doing

This server can:

- Accept file uploads
- Save files to disk
- Serve files via static URL
- Filter by MIME type
- Limit by file size

It cannot:

- Send email
- Cache responses
- Share state across processes
- Rate-limit clients
- Run scheduled jobs
- Move slow work off the request
- Make atomic multi-step writes
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 21 | The Mailroom | "I want to send notifications." |
| 22 | The Cache | "I want to reduce DB load." |
| 23 | The Redis | "I want shared state across processes." |

Project 21 is the natural next step. We accept file uploads, but we can't notify users. We need email.

---

## What You Should Do Now

1. **Read the code.** Notice the Multer config, the `upload.single('image')` middleware, the `image_url` column. The handler is slightly updated.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Upload an image** to a post. See the URL.
4. **Fetch the image** via the URL. See the file.
5. **Try a non-image file.** See the rejection.
6. **Try a file too large.** See the rejection.
7. **When you are ready**, move to [Project 21: The Mailroom](../21-mailroom/).
8. **If anything is unclear**, do not proceed. File upload is the foundation of every modern API. It must be solid.

---

## A Note on the Bigger Picture

You now have an API that *accepts files*. The user can attach an image. The server stores it. The URL is in the response.

From here, the path diverges:

- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API accepts files. The path continues.

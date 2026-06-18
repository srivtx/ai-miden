# The Decisions

> *"Multipart is the envelope. The file is the letter. The server reads the letter and saves it."*

## Decision 1: Multer and not busboy / formidable

**Alternatives**:
- **busboy** — lower-level, more flexible
- **formidable** — older, more popular in some communities
- **Built-in fetch `FormData`** — client-side, not server-side

**Why Multer: It's the de-facto Express middleware for `multipart/form-data`. It has a clean API. It supports disk storage, memory storage, and S3.

**Trade-off**: We depend on Multer. If it becomes unmaintained, we'd have to migrate. It's still active as of 2024-2026.

## Decision 2: Disk storage and not memory or S3

**Alternatives**:
- **Memory storage** — `multer.memoryStorage()`. Files in memory.
- **S3** — `multer-s3`. Files in S3.

**Why disk: Simple. Works for development. The files are on the same machine as the server. For our scale, this is fine.

**Trade-off**: For production with multiple servers, you'd use S3 (with a shared filesystem or a CDN). For a single server, disk is fine.

## Decision 3: UUID filenames

**Alternative**: Use the original filename (`photo.jpg`).

**Why UUID: Prevents collisions. If two users upload `photo.jpg`, they'd overwrite each other. With UUID, each file has a unique name.

**Trade-off**: The user can't tell what the file is from the URL (`/uploads/abc123.jpg`). They have to look at the post to see the image.

## Decision 4: 10 MB file size limit

**Alternative**: No limit, or 100 MB, or 1 MB.

**Why 10 MB: A balance between flexibility and safety. Most images are under 5 MB. 10 MB allows for high-res images. Larger files are rare and probably malicious.

**Trade-off**: A user with a 50 MB image is rejected. They have to compress. We accept this.

## Decision 5: Only images

**Alternative**: All file types.

**Why images only: We only have an `image_url` column on `posts`. We don't have a generic attachment system. We restrict to images for now.

**Trade-off**: A user can't attach a PDF. We accept this for the demo.

## Decision 6: Serve files from our server

**Alternative**: Serve from S3 / CDN.

**Why our server: Simple. Works for development. The server returns the file directly.

**Trade-off**: The server has to handle file I/O. For high-traffic apps, you'd use a CDN to offload. We accept this.

## Decision 7: No image processing

**Alternative**: Use Sharp to resize / compress.

**Why no processing: Out of scope. The user uploads a 5 MB image, we store a 5 MB image. For a profile picture, you'd resize to 200x200.

**Trade-off**: Storage costs are higher. Bandwidth is higher. We accept this for simplicity.

## Decision 8: Public files

**Alternative**: Authenticated file access.

**Why public: `/uploads/abc.jpg` is served to anyone with the URL. Simple. Matches the "posts are public" pattern.

**Trade-off**: Anyone with the URL can see the image. For private files (e.g., a user's medical record), you'd need auth.

## Decision 9: No virus scanning

**Alternative**: Use ClamAV or a similar service.

**Why no scanning: Out of scope. We trust the user.

**Trade-off**: A malicious user could upload a virus. We accept this for the demo.

## Decision 10: No progress tracking

**Alternative**: Use streaming with progress events.

**Why no progress: The user uploads and waits. We don't show a progress bar.

**Trade-off**: For large files, the user has no feedback. We could add `req.on('data', ...)` to track progress, but it's complex.

---

## What We Did Not Decide

- **S3 storage** — out of scope (future project)
- **CDN** — out of scope
- **Image processing** (Sharp) — out of scope
- **Multiple files per post** — out of scope (use `upload.array()`)
- **Auth on file access** — out of scope
- **Virus scanning** — out of scope
- **Streaming uploads** — out of scope
- **Progress tracking** — out of scope
- **Thumbnail generation** — out of scope
- **WebP conversion** — out of scope

Each is a future decision.

---

## The Meta-Decision: The API Accepts Files

For 19 projects, our API accepted only JSON. The user could create text data but couldn't attach files. Real apps need file upload.

Now the API accepts files. The user can attach an image to a post. The server stores it. The URL is in the response. The file is served.

This is the foundation of *every* API that handles user-generated content. File upload is non-negotiable for any modern app. The patterns (multipart, disk storage, static serving) are universal.

The next 20 projects will assume file upload exists. The path diverges:

- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The API accepts files. The path continues.

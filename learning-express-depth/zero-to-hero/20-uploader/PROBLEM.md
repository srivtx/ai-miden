# The Problem

> *"JSON is for data. Files are for bytes. They travel in different envelopes."*

## Why Multipart Exists

In project 05, we parse the request body as JSON. JSON is great for structured data: `{"title": "Hello", "body": "World"}`. But what if the user wants to attach an image? An image is binary data — not text. JSON can't represent binary.

The solution is a different content type: `multipart/form-data`. The body is a series of *parts*. Each part has its own headers and body. Text fields are parts with `Content-Type: text/plain`. File fields are parts with `Content-Type: image/jpeg` and a `filename`.

```
POST /posts HTTP/1.1
Content-Type: multipart/form-data; boundary=----abc

------abc
Content-Disposition: form-data; name="title"

Hello
------abc
Content-Disposition: form-data; name="image"; filename="photo.jpg"
Content-Type: image/jpeg

<binary data here>
------abc--
```

The `boundary` is a unique string that separates the parts. The server uses it to parse the body.

## What Pain Is This Solving?

Imagine the alternative. The user wants to attach a profile picture. They:

1. Upload the image to a separate service (S3, Imgur)
2. Get a URL
3. Send the URL in a JSON body

This works, but it's clunky. The user has to know about the upload service. The frontend has to coordinate two requests. The URL might expire.

A better experience: the user attaches the image in the same form as the rest of the data. The server handles both. The user gets one URL back.

`multipart/form-data` is the standard way to do this. HTML forms use it. Most APIs support it. The client can attach files in one request.

## The Deeper Problem: Streams

A file is a stream of bytes. The body is a stream of bytes. We need to read the stream, identify the parts, and save each part to a file.

Parsing `multipart/form-data` is non-trivial. You need to:

1. Read the body as a stream
2. Find the boundary
3. Split the body at the boundary
4. For each part, parse the headers and body
5. Save the file body to disk

Libraries like Multer do this for us. We don't write the parser.

## What This Project Will Solve

This project will:

1. Add `multer` as a dependency
2. Configure multer to save files to `uploads/` with a unique name
3. Add a file size limit (10 MB)
4. Add a MIME type filter (only images)
5. Serve uploaded files via `express.static`
6. Add an `image_url` column to `posts` (in a new migration)
7. Update `POST /posts` to accept an `image` field

By the end, the client can upload an image. The server stores it. The URL is in the response.

## What This Project Will *Not* Solve

- **S3 / cloud storage** — we save to disk. For production, you'd use S3. Project 39 (Observability) or a separate project.
- **Image processing** — we don't resize, compress, or convert. We'd use Sharp or similar.
- **CDN** — we serve files from our server. For scale, you'd use a CDN.
- **Multiple files per post** — we accept one file. For multiple, use `upload.array()`.
- **Progress tracking** — we don't show upload progress. We could use streaming.
- **Virus scanning** — we don't scan uploads. You'd use ClamAV or similar.
- **Auth on file access** — `/uploads/abc.jpg` is public. For private files, you'd check auth before serving.

## The Question This Project Answers

> *"How do I accept a file from the client?"*

If you can answer: "use `multipart/form-data`, parse with Multer, save to disk, serve via `express.static`," you are ready for project 21.

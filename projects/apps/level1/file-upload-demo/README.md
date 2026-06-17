# File Upload Demo — Multipart parsing without multer

A 50-line multipart parser that handles file uploads. No external libraries. Shows: how `multipart/form-data` works, validation, storage, download.

## Endpoints
```
POST /upload         # multipart/form-data with a file field
GET  /files/:id      # download a file
GET  /admin/files    # list all uploaded files
```

## Try
```bash
# Upload
curl -X POST http://localhost:3000/upload \
  -F "file=@/path/to/your/image.png"
# 201 { id: "abc123...", filename: "image.png", type: "image/png", size: 12345, url: "/files/abc123.png" }

# Download
curl http://localhost:3000/files/abc123.png -o downloaded.png

# List
curl http://localhost:3000/admin/files
```

## What this teaches
1. **multipart/form-data format**: how browsers send files
2. **Boundary parsing**: each part separated by `--<boundary>`
3. **Validation**: file type whitelist, size limit (5MB)
4. **Safe storage**: random ID, original filename kept in metadata only
5. **Content-Type header**: based on actual file type
6. **413 Payload Too Large**: when file exceeds limit
7. **415 Unsupported Media Type**: when file type not allowed

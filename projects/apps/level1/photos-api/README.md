# Photos API — Step 13 in the learning path

Builds on Music. Adds: real image upload (multipart), albums with ordered photos, public/private, EXIF-like metadata, tags.

## Endpoints
```
POST   /photos                       # multipart upload (X-User-Id)
GET    /photos?user=&tag=&is_public=
GET    /photos/:id                   # with tags
GET    /files/:filename              # download

POST   /albums
POST   /albums/:id/photos/:photoId   # add to album
GET    /albums/:id                   # with all photos in order
```

## Try
```bash
# Upload a photo
curl -X POST http://localhost:3000/photos \
  -H "X-User-Id: u_alice" \
  -F "file=@/path/to/image.jpg" \
  -F "taken_at=2024-12-15" \
  -F "camera=iPhone 15" \
  -F "location=Paris" \
  -F "tags=travel,summer" \
  -F "is_public=true"
# 201 { id: "p_abc...", url: "/files/p_abc.jpg", size: 12345, type: "image/jpeg" }

# Create an album, add photos
ALBUM=$(curl -X POST http://localhost:3000/albums -H "Content-Type: application/json" -H "X-User-Id: u_alice" -d '{"name": "Vacation"}' | jq -r .id)
curl -X POST http://localhost:3000/albums/$ALBUM/photos/<photo-id> -H "X-User-Id: u_alice"

# Get the album with all photos
curl http://localhost:3000/albums/$ALBUM
```

## What this teaches
1. **Multipart upload**: file + form fields together
2. **Binary storage**: write to filesystem, store metadata in DB
3. **Privacy**: public vs private photos
4. **EXIF-like metadata**: camera, location, taken_at
5. **Albums with order**: position field
6. **Path safety**: `path.basename()` to prevent traversal

## Next project
→ **library-api** — combines books + movies + music into a unified catalog

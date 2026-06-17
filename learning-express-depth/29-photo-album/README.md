# 29 — Photo Album

Albums have photos. Same nested pattern as the music playlist. Just different data.

## Run it

```bash
npm install
node server.js
```

```bash
# Create an album
curl -X POST http://localhost:3000/albums \
  -H "Content-Type: application/json" \
  -d '{"title": "Vacation 2024"}'

# Add a photo
curl -X POST http://localhost:3000/albums/1/photos \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/photo1.jpg", "caption": "Beach"}'

# See the album
curl http://localhost:3000/albums/1
```

## How to think about it

Same as the playlist. Different data. The shape is identical: create album, add photos to it, list, get, delete.

## What we learned

1. Same shape, different data — second time
2. The data is whatever the app is about (photos, songs, todos)
3. The structure is the same

## What's next

In **30-meal-planner** we build a meal planner. Each day has breakfast, lunch, dinner.

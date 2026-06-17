# Music API — Step 12 in the learning path

Builds on Movies. Adds: artists → albums → tracks hierarchy, playlists, play counts, top charts.

## Endpoints
```
GET    /artists                       # all artists
POST   /artists
GET    /artists/:id                   # with albums
GET    /albums
POST   /albums
GET    /albums/:id                    # with tracks
POST   /tracks
POST   /play/:trackId                 # log a play (X-User-Id)
GET    /charts/top                    # top tracks by play count
POST   /playlists
POST   /playlists/:id/tracks          # add a track
GET    /playlists/:id                 # with all tracks in order
```

## Try
```bash
# Create artist, album, tracks
ARTIST=$(curl -X POST http://localhost:3000/artists -H "Content-Type: application/json" -d '{"name": "Pink Floyd"}' | jq -r .id)
ALBUM=$(curl -X POST http://localhost:3000/albums -H "Content-Type: application/json" -d "{\"artist_id\": \"$ARTIST\", \"title\": \"Dark Side of the Moon\", \"release_year\": 1973}" | jq -r .id)
TRACK=$(curl -X POST http://localhost:3000/tracks -H "Content-Type: application/json" -d "{\"album_id\": \"$ALBUM\", \"title\": \"Time\", \"duration_sec\": 413, \"track_number\": 4}" | jq -r .id)

# Log plays
for i in {1..100}; do curl -X POST http://localhost:3000/play/$TRACK -H "X-User-Id: user_$i"; done

# See top charts
curl 'http://localhost:3000/charts/top?limit=5'
```

## What this teaches
1. **Hierarchical data**: artist → albums → tracks
2. **Aggregations**: `COUNT`, `GROUP BY` for play counts
3. **Rankings**: `ORDER BY play_count DESC`
4. **Ordered lists**: position field in playlist_tracks
5. **Anonymous data logging**: play counts work even if user is anon

## Next project
→ **photos-api** — adds: image upload, albums, EXIF data, sharing

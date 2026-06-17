# 28 — Music Playlist

A playlist has songs. Songs are nested inside playlists. New thing: **two-level nesting** (playlist has many songs).

## Run it

```bash
npm install
node server.js
```

```bash
# Create a playlist
curl -X POST http://localhost:3000/playlists \
  -H "Content-Type: application/json" \
  -d '{"name": "Workout Mix"}'
# { "id": 1, "name": "Workout Mix", "songs": [] }

# Add a song
curl -X POST http://localhost:3000/playlists/1/songs \
  -H "Content-Type: application/json" \
  -d '{"title": "Eye of the Tiger", "artist": "Survivor"}'

# Add another
curl -X POST http://localhost:3000/playlists/1/songs \
  -H "Content-Type: application/json" \
  -d '{"title": "Lose Yourself", "artist": "Eminem"}'

# See the playlist
curl http://localhost:3000/playlists/1
# { "id": 1, "name": "Workout Mix", "songs": [{ "id": 1, "title": "..." }, ...] }

# Remove a song
curl -X DELETE http://localhost:3000/playlists/1/songs/1
```

## How to think about it

The chat app had messages inside rooms. This is the same idea, but two levels: a playlist has songs, songs belong to a playlist. The URL says it: `/playlists/:id/songs`.

## How to build it (line by line)

```js
app.post('/playlists/:id/songs', (req, res) => {
  const playlist = playlists.find(p => p.id === parseInt(req.params.id));
  if (!playlist) return res.status(404).json({ error: 'Playlist not found' });
  const { title, artist } = req.body;
  const song = { id: playlist.songs.length + 1, title, artist };
  playlist.songs.push(song);
  res.status(201).json(playlist);
});
```

**Lines 27-34.** Add a song. Find the playlist. Add the song to its `songs` array.

**`playlist.songs.length + 1`** — song ids are scoped to the playlist. Two different playlists can both have a song with id 1. That's fine.

## What we learned

1. Two-level nesting: playlist has songs
2. Ids can be scoped to the parent
3. The URL structure mirrors the data structure
4. We've now seen nesting in 2 apps

## What's next

In **29-photo-album** we build a photo album. Albums have photos. The data is similar.

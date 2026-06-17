# 27 — Movie Watchlist

A list of movies to watch. Each movie has a title, year, watched flag, and rating. New thing: **updating a boolean** with PATCH.

## Run it

```bash
npm install
node server.js
```

```bash
# Add a movie
curl -X POST http://localhost:3000/movies \
  -H "Content-Type: application/json" \
  -d '{"title": "Inception", "year": 2010}'

# Mark as watched
curl -X PATCH http://localhost:3000/movies/1 \
  -H "Content-Type: application/json" \
  -d '{"watched": true, "rating": 5}'

# List all
curl http://localhost:3000/movies
```

## How to think about it

We've seen the same shape three times now. This is what "intuition for building" looks like: you know the shape, you adapt the data.

## How to build it (line by line)

```js
if (req.body.watched !== undefined) movie.watched = req.body.watched;
```

**Line 20.** Update `watched` if the client sent it.

**`!== undefined`** — check whether the client sent this field. The client might send `watched: false`, and we want to update it to false. If we used `if (req.body.watched)`, we'd skip the false case.

**Why?** `if (false)` is false. `if (undefined)` is false. We need to distinguish: "didn't send it" vs "sent false." `!== undefined` does that.

## What we learned

1. `!== undefined` checks "did the client send this field?"
2. We can update booleans with PATCH
3. Same shape, different data — third time seeing it

## What's next

In **28-music-playlist** we build a music playlist. Songs belong to playlists.

# Library API — Step 14 in the learning path

Builds on Books + Movies + Music. Combines all three into one unified catalog with a single search.

## Endpoints
```
GET    /items?type=&q=&genre=&year=&sort=         # search across all media
GET    /items/:type/:id                          # type=book|movie|album
POST   /items                                    # add a book/movie/album
POST   /items/:type/:id/reviews                  # review (X-User-Id)
GET    /genres                                   # all genres grouped by type

POST   /collection/:type/:id                     # add to your collection
GET    /collection                               # your collection with status
```

## Try
```bash
# Add a book
curl -X POST http://localhost:3000/items -H "Content-Type: application/json" \
  -d '{"type": "book", "title": "Dune", "creator": "Frank Herbert", "year": 1965, "genre": "Sci-Fi"}'

# Add a movie
curl -X POST http://localhost:3000/items -H "Content-Type: application/json" \
  -d '{"type": "movie", "title": "Dune", "creator": "Villeneuve", "year": 2021, "genre": "Sci-Fi"}'

# Search all media for "Dune"
curl 'http://localhost:3000/items?q=Dune'
# Returns both the book and the movie

# Filter by type
curl 'http://localhost:3000/items?type=book'

# Add to your collection with status
curl -X POST http://localhost:3000/collection/book/<id> \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"status": "in_progress"}'

# See your collection
curl http://localhost:3000/collection -H "X-User-Id: u_alice"
```

## What this teaches
1. **Unified search across types**: one endpoint, many kinds
2. **Polymorphic references**: `item_type` to disambiguate which table
3. **Polymorphic associations**: reviews can be for books OR movies OR albums
4. **Status tracking**: planned / in_progress / completed / dropped
5. **CHECK constraints**: type must be one of three values

## Next project
→ **twitter-api** — adds: follow graph, timeline, likes, retweets

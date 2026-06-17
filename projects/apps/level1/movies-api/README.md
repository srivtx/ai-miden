# Movies API — Step 11 in the learning path

Builds on Books. Adds: genres (many-to-many), cast (with roles), similar movies, personal watchlist.

## Endpoints
```
GET    /movies?q=&genre=&year=&sort=            # sort=recent|year|title
GET    /movies/:id                              # with genres + cast
POST   /movies                                  # create with genres and cast
GET    /movies/:id/similar                      # movies with overlapping genres
POST   /watchlist/:movieId                      # add to watchlist
GET    /watchlist                               # your watchlist
```

## Try
```bash
# Create
curl -X POST http://localhost:3000/movies -H "Content-Type: application/json" \
  -d '{"title": "Inception", "year": 2010, "director": "Nolan", "duration_min": 148, "genres": ["Sci-Fi", "Action"], "cast": [{"person_name": "DiCaprio", "role": "lead"}]}'

# Filter by genre
curl 'http://localhost:3000/movies?genre=Sci-Fi'

# Find similar
curl http://localhost:3000/movies/<id>/similar

# Add to watchlist
curl -X POST http://localhost:3000/watchlist/<movie-id> -H "X-User-Id: u_alice"

# Your watchlist
curl http://localhost:3000/watchlist -H "X-User-Id: u_alice"
```

## What this teaches
1. **Many-to-many**: movies ↔ genres
2. **Composite entities**: cast with role attribute
3. **Recommendation by overlap**: SQL with `IN (subquery)` and `DISTINCT`
4. **Personal collections**: per-user lists (watchlist)

## Next project
→ **music-api** — adds: artists, albums, tracks, playlists, play counts

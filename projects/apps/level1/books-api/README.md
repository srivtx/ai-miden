# Books API — Step 10 in the learning path

Builds on Calendar. Adds: ISBN lookup, many-to-many authors, ratings, reviews, aggregations.

## Endpoints
```
GET    /books?q=&author=&year=&sort=             # sort=recent|rating|title
GET    /books/:id                                # by id OR isbn; includes authors + reviews
POST   /books                                    # create with authors
POST   /books/:id/reviews                        # { rating: 1-5, body }
GET    /authors                                  # with book counts
```

## Try
```bash
# Create
curl -X POST http://localhost:3000/books -H "Content-Type: application/json" \
  -d '{"isbn": "978-0-13-110362-7", "title": "The C Programming Language", "published_year": 1978, "authors": ["Kernighan", "Ritchie"]}'

# Lookup by ISBN
curl http://localhost:3000/books/978-0-13-110362-7

# Add a review
curl -X POST http://localhost:3000/books/<id>/reviews \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"rating": 5, "body": "Classic"}'

# Search by author
curl 'http://localhost:3000/books?author=Kernighan'

# Sort by rating
curl 'http://localhost:3000/books?sort=rating'
```

## What this teaches
1. **Many-to-many**: books ↔ authors via junction
2. **ISBN as alternate key**: lookup by id OR isbn
3. **Aggregations**: `AVG(rating)`, `COUNT(reviews)`
4. **CHECK constraints**: rating BETWEEN 1 AND 5
5. **Composite sort**: by rating, then by recency

## Next project
→ **movies-api** — adds: genres, cast, similar movies, watchlist

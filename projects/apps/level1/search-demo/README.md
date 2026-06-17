# Search Demo — In-memory full-text search with inverted index

A toy search engine built from scratch. Tokenize, build an inverted index, score by term frequency, rank, return snippets.

## Endpoints
```
GET /search?q=...&category=...&limit=10
GET /admin/index-stats   # term count, top terms
```

## Try
```bash
curl 'http://localhost:3000/search?q=cache'
# Returns: 2 results (caching, cache-aside)

curl 'http://localhost:3000/search?q=security&category=security'
# Returns: SQL injection, JWT authentication (filtered by category)

curl 'http://localhost:3000/search?q=node+js'
# Multi-word search, score is sum of all term matches
```

## What this teaches
1. **Inverted index**: `term -> [{docId, count}]` for O(1) term lookup
2. **Tokenization**: lowercase, split on non-alphanumeric
3. **Title boost**: matches in title weighted higher (3x) than body (1x)
4. **TF ranking**: more occurrences = higher score
5. **Filtering**: combine full-text with structured filters (category)
6. **Snippets**: show the matching text in context
7. **Real search engines** (Elasticsearch, Meilisearch) do the same but at scale

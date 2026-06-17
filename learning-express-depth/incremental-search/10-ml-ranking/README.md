# 10 — ML Ranking (Search, final stage)

Use ML to learn the best ranking. Features + weights from training data.

**What's new:**
- `WEIGHTS` object: feature → weight
- `computeFeatures()`: extracts features for a query/doc pair
- `scoreDoc()`: weighted sum of features
- `/train` endpoint: update weights from training data

**Why ML ranking?** Hand-tuned rules (title boost, popularity, freshness) work, but you have to guess the weights. ML learns them from data: "users who clicked result X for query Y, what features did X have?"

**The features:**
- `text_relevance` — does the body contain the query terms?
- `title_match` — does the title contain the query terms?
- `popularity` — log of click count (saturating scale)
- `freshness` — 1 / days since published (newer = higher)
- `body_length_match` — prefer medium-length documents

**The score:** weighted sum. `Σ (feature × weight)`. Weights are learned.

**In real life:**
- Use a learning-to-rank library (LightGBM, XGBoost)
- Features include dozens of signals: page rank, CTR, dwell time, query-document similarity
- Train on click logs: query + clicked doc = positive, query + shown-but-not-clicked = negative

## Run
```bash
npm install && node server.js
```

```bash
# Search
curl 'http://localhost:3000/search?q=javascript'
# Returns docs scored with the current weights

# See weights
curl http://localhost:3000/weights
# { text_relevance: 1.0, title_match: 2.0, ... }

# Update weights (e.g., from offline training)
curl -X POST http://localhost:3000/train -H "Content-Type: application/json" \
  -d '{"weights": {"text_relevance": 1.5, "title_match": 3.0}}'
```

## What we learned
- Feature-based ranking
- Weighted sum
- ML-learned weights
- The path from rules to ML
- What features matter (text, title, popularity, freshness)

## 🎉 10 stages complete!

The full search system has:
- Basic search ✓
- Relevance ranking ✓
- Filters ✓
- Facets ✓
- Autocomplete ✓
- Spell check ✓
- Synonyms ✓
- CTR-based ranking ✓
- Search analytics ✓
- ML ranking ✓

This is how Elasticsearch, Algolia, Vespa, Solr all work. Same 10 patterns, different code.

## The 10 patterns
1. **Basic** — substring match
2. **Relevance** — title boost, frequency
3. **Filters** — combine with search
4. **Facets** — counts per field
5. **Autocomplete** — FTS5 prefix matching
6. **Spell check** — Levenshtein
7. **Synonyms** — query expansion
8. **Ranking** — CTR-based feedback
9. **Analytics** — top queries, no-results, CTR
10. **ML ranking** — feature-based with learned weights

These 10 patterns are the building blocks of every search engine.

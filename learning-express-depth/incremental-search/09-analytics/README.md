# 09 — Search Analytics

Track what users search for, what they click, and what returns nothing.

**What's new:**
- `search_logs` table: query, results_count, clicked_position
- Log search and click events
- Top queries (most popular)
- No-result queries (improvement opportunities)
- CTR (click-through rate)

**Why track search analytics?** "What are people searching for?" reveals intent. "What are they not finding?" reveals content gaps. "What do they click?" reveals ranking quality.

**Why no-result queries?** If 100 people search "vacuum cleaner" and get 0 results, you have a content gap. Add products in that category. Or improve the search.

**Why CTR?** If users search and click the first result 80% of the time, your ranking is good. If they click the 5th result, your top results are bad.

## Run
```bash
npm install && node server.js
```

```bash
# Log some searches
curl -X POST http://localhost:3000/log/search -H "Content-Type: application/json" -d '{"query": "javascript", "results_count": 42}'
curl -X POST http://localhost:3000/log/search -H "Content-Type: application/json" -d '{"query": "python", "results_count": 18}'

# Log a click
curl -X POST http://localhost:3000/log/click -H "Content-Type: application/json" -d '{"query": "javascript", "position": 1}'

# Top queries
curl http://localhost:3000/analytics/top-queries

# No-result queries
curl http://localhost:3000/analytics/no-results

# CTR
curl http://localhost:3000/analytics/ctr
# { total_searches: 2, with_clicks: 1, ctr: "50.0" }
```

## What we learned
- Search log table
- Top queries, no-result queries, CTR
- "What are people searching for" reveals intent
- "What's not being found" reveals gaps
- "What gets clicked" reveals quality

## Next
**10-ml-ranking** — the final stage. Use ML to learn the best ranking.

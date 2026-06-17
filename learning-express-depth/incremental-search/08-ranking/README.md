# 08 — Ranking (Search)

Learn from clicks. Pages that get clicked more rank higher. CTR-based ranking.

**What's new:**
- `doc_stats` table: impressions (shown) and clicks
- CTR = clicks / impressions
- Search results boosted by CTR
- Track impressions and clicks

**Why CTR-based ranking?** The user's behavior is the best signal. If many people search for "javascript" and click the first result, that result must be good. Boost it.

**Why impressions vs clicks?** An impression = "we showed this in the results". A click = "the user picked this". Click is the strong signal. We track both so we can compute CTR.

**The boost formula:** `base_score + ctr * 2`. If CTR is 0.5, boost is 1.0. A document with high CTR rises to the top over time.

**Why feedback loop?** Without it, search quality is fixed. With it, search quality improves as more users use it.

## Run
```bash
npm install && node server.js
```

```bash
# Initial: FTS ranking
curl 'http://localhost:3000/search?q=javascript'
# Returns: standard order

# Track that the first result was shown
curl -X POST http://localhost:3000/track/impression -H "Content-Type: application/json" -d '{"doc_ids": [1, 2, 3]}'

# Track that the user clicked the first one
curl -X POST http://localhost:3000/track/click -H "Content-Type: application/json" -d '{"doc_id": 1}'

# Now the boosted order favors doc 1
curl 'http://localhost:3000/search?q=javascript'
# Doc 1 first now (higher CTR)

# See all stats
curl http://localhost:3000/admin/stats
```

## What we learned
- CTR-based ranking
- Tracking impressions and clicks
- The feedback loop
- Learning from user behavior

## Next
**09-analytics** — track what users search for, click on, find nothing.

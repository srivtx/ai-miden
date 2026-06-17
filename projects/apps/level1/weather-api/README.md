# Weather API — Step 5 in the learning path

Builds on Products. Adds: external API calls, in-memory caching, time-series data, fallback handling.

## Endpoints
```
GET /weather/:city                       # current weather (cached 10 min)
GET /weather/:city/forecast?days=5       # multi-day forecast
GET /weather/:city/history               # query history
GET /admin/cache                         # inspect cache
DELETE /admin/cache/:city                # invalidate cache
```

## Try
```bash
# First call: fetches from "provider"
curl http://localhost:3000/weather/london
# { city: "london", tempC: 22, ..., cached: false }

# Second call within 10 min: cache hit
curl http://localhost:3000/weather/london
# { ..., cached: true }

# Forecast
curl 'http://localhost:3000/weather/tokyo/forecast?days=7'

# See cache state
curl http://localhost:3000/admin/cache

# Manually invalidate
curl -X DELETE http://localhost:3000/admin/cache/london
```

## What this teaches
1. **External API integration**: the app calls another service
2. **Cache-aside pattern**: check cache, on miss call provider, store result
3. **TTL**: cache expires after N minutes
4. **Cache invalidation**: manually clear when needed
5. **Time-series data**: query history grows over time
6. **Error handling**: provider errors → 502

## Next project
→ **chat-api** — adds: WebSockets, rooms, real-time messaging

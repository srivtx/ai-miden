# 11 — Weather App

Not every app needs a database. This one has hardcoded data. The "API" just looks up the city and returns it.

## Run it

```bash
npm install
node server.js
```

```bash
# Get weather for London
curl http://localhost:3000/weather/london
# { "city": "London", "temp": 15, "condition": "cloudy" }

# Try a city we don't have
curl http://localhost:3000/weather/mars
# 404 { "error": "No weather data for mars" }
```

## How to think about it

A "real" weather app would call an external API (like OpenWeather). We're faking it. But the structure is the same: the URL says what the user wants, the server looks it up, and returns it.

This is a **read-only** app. There's no POST or DELETE. Just GET. Many APIs are read-only.

## How to build it (line by line)

```js
const weather = {
  'london': { city: 'London', temp: 15, condition: 'cloudy' },
  // ...
};
```

**Lines 7-11.** A plain JavaScript object. Each key is a city name, each value is the weather data. This is our "database" — for now, it's just an object.

**Why an object?** Fast lookups. `weather['london']` is O(1) — instant. With an array, we'd have to loop.

```js
app.get('/weather/:city', (req, res) => {
  const city = req.params.city.toLowerCase();
  const data = weather[city];
  if (!data) return res.status(404).json({ error: `No weather data for ${req.params.city}` });
  res.json(data);
});
```

**Lines 14-18.** Three steps:
1. Get the city from the URL, lowercase it (so "London" and "london" both work)
2. Look it up in our object
3. If not found, 404. Otherwise, return the data.

**`req.params.city.toLowerCase()`** — the URL has the city as the client typed it. We lowercase it so the lookup is case-insensitive.

## What we learned

1. Not every app needs a database
2. Objects are great for fast lookups
3. URL parameters can be normalized (lowercase, trim, etc.)
4. Read-only APIs are common
5. We've now seen 5 apps with the same shape

## What's next

In **12-calendar-app** we build a calendar. Events have a start time, end time, and a title. We add a new concept: **range queries** — "show me events between date X and date Y."

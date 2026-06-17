// 11 — Weather App
// No database. The "data" is hardcoded. We just look it up and return.
const express = require('express');
const app = express();

// Our fake weather data. In a real app, this would come from an API.
const weather = {
  'london': { city: 'London', temp: 15, condition: 'cloudy' },
  'tokyo': { city: 'Tokyo', temp: 22, condition: 'sunny' },
  'new york': { city: 'New York', temp: 18, condition: 'rainy' },
  'paris': { city: 'Paris', temp: 12, condition: 'cloudy' },
};

app.get('/weather/:city', (req, res) => {
  // The city comes from the URL. We lowercase it to match our keys.
  const city = req.params.city.toLowerCase();
  const data = weather[city];
  if (!data) return res.status(404).json({ error: `No weather data for ${req.params.city}` });
  res.json(data);
});

app.listen(3000, () => console.log('Weather server on http://localhost:3000'));

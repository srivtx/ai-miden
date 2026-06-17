// 02 — Hello Express
// Same as 01, but with Express. We get cleaner code.
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello');
});

app.listen(3000, () => console.log('Server on http://localhost:3000'));

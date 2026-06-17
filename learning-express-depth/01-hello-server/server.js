// 01 — Hello Server
// Just Node's built-in http. No Express, no libraries.
// When you visit localhost:3000, the browser sends a request.
// Our server says "Hello" back.
const http = require('http');

http.createServer((req, res) => {
  res.end('Hello');
}).listen(3000, () => console.log('Server on http://localhost:3000'));

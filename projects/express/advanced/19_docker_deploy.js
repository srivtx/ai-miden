// 19_docker_deploy.js — Dockerfile + docker-compose ready project.
// This file documents the deployment; the actual deploy uses the Docker files below.

const express = require('express');
const app = express();
app.get('/health', (req, res) => res.json({ status: 'ok', uptime: process.uptime() }));
app.get('/', (req, res) => res.json({ msg: 'Hello from Docker!' }));
app.listen(3000, () => console.log('Server :3000'));

/*
---- Dockerfile (same directory) ----
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]

Build:  docker build -t myapp .
Run:    docker run -p 3000:3000 -e NODE_ENV=production myapp

---- docker-compose.yml (same directory) ----
version: '3.8'
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    volumes: [redisdata:/data]

volumes:
  pgdata:
  redisdata:

Run: docker-compose up -d
*/

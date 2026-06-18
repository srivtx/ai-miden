# Stage 1: build
FROM node:20-alpine AS build
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci --production=false && npm prune --production

# Stage 2: run
FROM node:20-alpine
RUN addgroup -S app && adduser -S -G app nodeapp && mkdir /data && chown nodeapp:app /data
WORKDIR /app
COPY --from=build /build/node_modules ./node_modules
COPY server.js .
EXPOSE 3000
USER nodeapp
CMD ["node", "server.js"]

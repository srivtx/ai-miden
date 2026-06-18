# Multi-stage Docker build
FROM node:20-alpine AS build
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci --production=false && npm prune --production

FROM node:20-alpine
RUN addgroup -S app && adduser -S -G app nodeapp && mkdir /data && chown nodeapp:app /data
WORKDIR /app
COPY --from=build /build/node_modules ./node_modules
COPY . .
USER nodeapp
EXPOSE 3000
CMD ["node", "server.js"]

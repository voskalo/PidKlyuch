# Stage 1: Build static React / Vite SPA
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Leave empty when served behind Caddy on the same HTTPS origin (frontend already prefixes /api/...)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Optional Google OAuth 2.0 Web Client ID for "Sign in with Google"
ARG VITE_GOOGLE_CLIENT_ID=""
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

RUN npm run build

# Stage 2: Serve built assets on port 80 with SPA history fallback
FROM caddy:2-alpine

COPY --from=build /app/dist /usr/share/caddy

RUN printf ':80 {\n\troot * /usr/share/caddy\n\tencode zstd gzip\n\ttry_files {path} /index.html\n\tfile_server\n}\n' > /etc/caddy/Caddyfile

EXPOSE 80

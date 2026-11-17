# PidKlyuch Infrastructure & Deployment (`infra/`)

This directory contains the Docker, database, and Caddy v2 reverse-proxy setup used to run and deploy **PidKlyuch («Під ключ»)** over **HTTPS**.

## Architecture

PidKlyuch runs behind **Caddy v2 (`caddy:2-alpine`)** on a single HTTPS origin (`DOMAIN`), eliminating cross-origin (CORS) friction between the frontend and backend while providing automatic Let's Encrypt TLS certificates and HTTP → HTTPS redirects.

```text
Internet / Client (HTTPS :443, HTTP :80, HTTP/3 :443/udp)
        │
        ▼
  [ caddy:2-alpine ]
        ├── /healthz          ──▶ 200 OK
        ├── /api/*, /docs*    ──▶ [ backend:8000 ]  (FastAPI + Uvicorn) ──▶ [ db:5432 ] (PostgreSQL 16 or AWS RDS)
        └── /*                ──▶ [ frontend:80 ]   (React/Vite SPA)
                                  └─ fallback (`--profile fallback`): [ hello:80 ] (infra/hello-world/index.html)
```

## Files in `infra/`

| File | Purpose |
|---|---|
| `docker-compose.yml` | Full-stack orchestration (`db`, `backend`, `frontend`, `caddy`) plus optional `fallback` profile (`hello`) |
| `Caddyfile` | Caddy v2 reverse-proxy config with automatic HTTPS (`{$DOMAIN:localhost}`) and upstream routing |
| `backend.Dockerfile` | Production Python 3.12 FastAPI container with `/api/health` Docker `HEALTHCHECK` |
| `frontend.Dockerfile` | Multi-stage Node 20 Vite build + lightweight Caddy static SPA server (`try_files {path} /index.html`) |
| `.env.example` | Template for Compose, PostgreSQL, Caddy, and backend secrets/variables |
| `Dockerfile` & `hello-world/` | Standalone static verification container used by the `fallback` profile |

## Prerequisites

- Docker Engine 24+ and Docker Compose v2 (`docker compose version`)
- For production HTTPS on AWS EC2:
  - Inbound Security Group ports open: `80/tcp` (ACME HTTP-01 + redirect), `443/tcp` (HTTPS), `443/udp` (HTTP/3)
  - Either a custom domain DNS `A` record or `<EC2-PUBLIC-IP-WITH-DASHES>.sslip.io` (e.g. `3-75-120-45.sslip.io`)

## Running Full-Stack Locally

```bash
cp infra/.env.example infra/.env
docker compose --env-file infra/.env -f infra/docker-compose.yml up --build
```

Verify:
- App UI: `https://localhost`
- API health: `https://localhost/api/health`
- Swagger docs: `https://localhost/docs`
- Proxy health: `https://localhost/healthz` → `OK`

## Fallback Mode (Before `backend/` or `frontend/` Are Merged)

If you want to smoke-test HTTPS on EC2 using only `infra/` without building `backend/` or `frontend/`:

```bash
DOMAIN=3-75-120-45.sslip.io ACME_EMAIL=you@example.com \
  docker compose --profile fallback -f infra/docker-compose.yml up -d --build caddy hello
```

## Production Deployment (AWS EC2 Ubuntu)

1. Copy and edit `infra/.env`:
   ```bash
   cp infra/.env.example infra/.env
   # Set DOMAIN=<EC2-IP-WITH-DASHES>.sslip.io, ACME_EMAIL, POSTGRES_PASSWORD, JWT_SECRET, CORS_ORIGINS
   ```
2. Launch all services in detached mode:
   ```bash
   docker compose --env-file infra/.env -f infra/docker-compose.yml up -d --build
   ```
3. Inspect logs and TLS certificate issuance:
   ```bash
   docker compose --env-file infra/.env -f infra/docker-compose.yml logs -f caddy backend
   ```

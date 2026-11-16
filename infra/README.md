# PidKlyuch Infrastructure & Deployment (`infra/`)

This directory contains the Docker and reverse-proxy configuration used to run and deploy **PidKlyuch («Під ключ»)** over **HTTPS**.

## Architecture

PidKlyuch uses **Docker Compose** behind a **Caddy v2** reverse proxy:

- **Caddy v2 (`caddy:2-alpine`)** listens on ports `80` (HTTP), `443` (HTTPS TCP), and `443/udp` (HTTP/3).
- Caddy automatically provisions and renews TLS certificates via Let's Encrypt / ZeroSSL when `DOMAIN` points to the server's public IP, and automatically redirects all HTTP traffic to HTTPS.
- For local development (`DOMAIN=localhost`), Caddy uses its internal local CA or self-signed certificates so HTTPS can be tested locally.

### Day 1 ("Hello World" HTTPS Verification)

```text
Internet / Client (HTTPS :443, HTTP :80)
        │
        ▼
  [ caddy:2-alpine ]  ── /healthz ──▶ 200 OK
        │
        ▼ (all other routes)
  [ hello:80 ]        ── static status page (infra/hello-world/index.html)
```

### Day 2+ (Full Application Routing — planned)

Once `backend/` and `frontend/` services are added:

- `/api/*` → routed to `backend:8000`
- `/*` → routed to `frontend:3000`

## Prerequisites

- Docker Engine 24+ and Docker Compose v2 (`docker compose version`)
- For production HTTPS:
  - A domain name with an `A` (and/or `AAAA`) DNS record pointing to the host VM
  - Inbound firewall ports `80/tcp`, `443/tcp`, and `443/udp` open

## Environment Variables

| Variable | Description | Default | Required in Prod |
|---|---|---|---|
| `DOMAIN` | Public domain name (e.g. `pidklyuch.example.com`) or `localhost` for local testing | `localhost` | Yes |
| `ACME_EMAIL` | Email address for Let's Encrypt / ACME certificate notifications | `admin@example.com` | Recommended |

## Running Locally

From the repository root:

```bash
DOMAIN=localhost docker compose -f infra/docker-compose.yml up --build
```

Then verify:
- Static page: `https://localhost` (accept local dev cert warning if using local CA)
- Health endpoint: `https://localhost/healthz` → `OK`

To stop:

```bash
docker compose -f infra/docker-compose.yml down
```

## Production Deployment

1. Provision a Linux VPS (e.g. Ubuntu 24.04) with Docker and Docker Compose installed, and point your domain's DNS `A` record to the server IP.
2. Clone the repository on the server and export production variables (or place them in a `.env` file next to `docker-compose.yml` — never commit `.env`):
   ```bash
   export DOMAIN=your-domain.example.com
   export ACME_EMAIL=your-email@example.com
   ```
3. Start the stack in detached mode:
   ```bash
   docker compose -f infra/docker-compose.yml up -d --build
   ```
4. Check Caddy logs to confirm TLS certificate issuance:
   ```bash
   docker compose -f infra/docker-compose.yml logs -f caddy
   ```

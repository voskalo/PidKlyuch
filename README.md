# PidKlyuch («Під ключ»)

**Know the full price of anything you buy abroad, from a parcel to a car.**

PidKlyuch is a web calculator for people in Ukraine who buy goods abroad. You pick what you are importing
(a parcel of electronics or clothing, or a car), enter the price and shipping cost, and in under a minute you get
the **final landed price**: customs duty, VAT, and excise, each shown with the formula used to calculate it.
Foreign currencies are converted using the official daily rates of the National Bank of Ukraine (NBU).

Customs rules in Ukraine differ by category, so the final cost is hard to predict. A €200 parcel adds about €16 in
duties, a €10,000 car adds €2,048–€4,640 in taxes, and from July 2027 VAT applies to every imported parcel.
PidKlyuch makes that cost visible before you buy.

> OOAD course project by Liubomyr Voskalo, Anna Kravchenko, and Anton Vertyporoh.

- **Live demo:** _TBD (HTTPS URL)_
- **Report:** _TBD (`docs/report.pdf`)_

---

## Team & division of work

Deadline: **Thursday 19 November 2026**, live demo. Every member submits individually: the repo link, the demo URL,
and the report PDF.

### 👤 Liubomyr Voskalo: Backend & Auth  (`backend/`)
- Set up the backend project, database, and data models (User, Calculation).
- **Auth:** sign-up, sign-in, sign-out, password hashing, sessions or JWT, protected routes.
- **Calculation engine:** implement the parcel and car customs formulas from Anton's spec (`docs/customs-rules.md`)
  in one backend module, with unit tests built from Anton's test cases.
- **Exchange rates:** fetch NBU daily rates, cache them, and keep a fallback when the NBU API is down.
- **History:** save calculations for signed-in users and return them in a list endpoint.
- **API contract:** write the list of endpoints in `AGENTS.md` §8 on **day 1**, so Anna can build the UI against it.
- Basic counters for the report: number of sign-ups and calculations, and returning users.

### 👤 Anna Kravchenko: Frontend & UX  (`frontend/`)
- Set up the frontend project and layout (mobile-friendly, since most users come from Telegram or TikTok on phones).
- Sign-up and sign-in pages, plus "logged in / logged out" UI states.
- **Smart input flow:** choose the delivery type (parcel / car), then the category, then short dynamic questions.
- **Result page:** itemized breakdown (duty, VAT, excise, total), the formula for each line, and the
  **"today vs. July 2027"** comparison for parcels.
- **History page** for signed-in users.
- **Donation button** (e.g. to a volunteer fund) for the bonus criterion.
- UI text in Ukrainian.
- Apply the UX fixes from user feedback on Wednesday.

### 👤 Anton Vertyporoh: Infra, Customs Rules, User Testing & Report  (`infra/`, `docs/`)
- **Infra:** Dockerfiles / compose, hosting, domain, and **HTTPS**. Deploy a "hello world" on **day 1**, then
  redeploy as features land. Optional CI that runs the backend tests.
- **Customs rules research:** write `docs/customs-rules.md` with the exact current rules for parcels and cars, the
  July 2027 parcel rules, and official sources. Include **10+ worked test cases** (input → expected output) that
  Liubomyr turns into unit tests.
- **User testing coordination:** feedback form (Google Form), testing script, and a shared table of testers and
  their feedback.
- **Report (PDF):** who tried it, how many people, what they said, what we changed, and donation evidence (screenshots).
- README sections **"How to run"** and **"How to deploy"**.

### 🤝 Everyone
- Each member brings **at least 5 real users** who are not close friends: post in Telegram/Facebook groups about
  shopping abroad or importing cars, and ask people who recently bought something abroad. Target: **15+ testers.**
- Write down each tester's feedback in the shared table: who they are, what they tried, what they said, and quotes.
- Ask testers for a small donation to a volunteer cause and collect screenshots as evidence (bonus).
- If you use an AI agent, it must read and update [`AGENTS.md`](AGENTS.md) (see the rules inside).

### 📅 Timeline

| Day | Liubomyr (backend) | Anna (frontend) | Anton (infra/docs) |
|---|---|---|---|
| **Mon 16** | Agree on stack together · scaffold backend · write API contract | Agree on stack · scaffold frontend · page layout | Agree on stack · hello-world deploy over HTTPS · start customs rules research |
| **Tue 17** | Auth + parcel/car calculation + NBU rates · deployed | Auth pages + calculator flow + result page, connected to the API | Finish `customs-rules.md` + test cases · feedback form · recruit testers |
| **Wed 18** | Morning: history + fixes · afternoon: fixes from feedback | Morning: history + donation · afternoon: fixes from feedback | **User testing sessions (all members)** · collect feedback · start the report |
| **Thu 19** | Final bug fixes, freeze in the morning | Final polish | Finish report PDF, README run/deploy · **demo** · everyone submits |

**Must have for the demo:** HTTPS deploy, sign-up and sign-in, parcel and car calculation with an itemized
breakdown, NBU rates, history, donation link.
**Only if time remains:** comparing 3 carriers, rule-change alerts, price tracking.

---

## Repository structure

```
backend/    API server, auth, customs calculation engine, database   (Liubomyr)
frontend/   Web UI                                                  (Anna)
infra/      Docker, deployment configs, CI                          (Anton)
docs/       Customs rules spec, user-testing notes, report          (Anton)
AGENTS.md   Shared context and work log for AI agents: read first, update after every task
```

## How to run

### Option A: Full-Stack via Docker Compose (Recommended)

**Prerequisites:** Docker Engine 24+ and Docker Compose v2 (`docker compose version`).

```bash
cp infra/.env.example infra/.env
docker compose --env-file infra/.env -f infra/docker-compose.yml up --build
```

- **App UI (HTTPS via Caddy):** `https://localhost`
- **API health check:** `https://localhost/api/health`
- **Interactive API docs (Swagger):** `https://localhost/docs`
- **Reverse-proxy health check:** `https://localhost/healthz`

*(If running only the Day 1 HTTPS infrastructure before `backend/` or `frontend/` are present on your branch, use the fallback profile:)*

```bash
DOMAIN=localhost docker compose --profile fallback -f infra/docker-compose.yml up --build caddy hello
```

### Option B: Run Services Individually (Local Development)

#### Backend (Python 3.12+ / FastAPI)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env            # uses local SQLite (pidklyuch.db) by default
.venv/bin/uvicorn app.main:app --reload
```

- API health: `http://localhost:8000/api/health`
- Interactive Swagger docs: `http://localhost:8000/docs`
- Unit tests (`66` tests): `cd backend && .venv/bin/pytest`
- Law watcher check: `cd backend && .venv/bin/python scripts/check_law_updates.py`

#### Frontend (Node.js 20+ / React + Vite)

```bash
cd frontend
npm install
npm run dev
```

- Local UI: `http://localhost:5173` (CORS is pre-configured on the backend for `http://localhost:5173` and `http://localhost:3000`).

---

## How to deploy

PidKlyuch deploys as a single HTTPS origin on **AWS EC2 (Ubuntu 24.04 LTS)** using **Docker Compose** and **Caddy v2** (automatic Let's Encrypt TLS certificates, HTTP → HTTPS redirect, and `/api/*` → FastAPI + `/*` → SPA routing).

### Step 1: Launch AWS EC2 Instance & Open Firewall Ports
1. Launch an **Ubuntu Server 24.04 LTS** EC2 instance (`t3.small` recommended, or `t3.micro` with 1–2 GB swap).
2. In the EC2 **Security Group** inbound rules, allow:
   - `22/tcp` (SSH from your IP)
   - `80/tcp` (HTTP — required for Let's Encrypt ACME challenge and HTTP → HTTPS redirect)
   - `443/tcp` (HTTPS)
   - `443/udp` (HTTP/3)

### Step 2: Install Docker & Docker Compose on EC2
SSH into the instance and run:

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
docker compose version
```

### Step 3: Clone Repo & Configure Production Environment
Use `<EC2-PUBLIC-IP-WITH-DASHES>.sslip.io` (e.g. `3-75-120-45.sslip.io`) so Caddy v2 automatically issues a valid Let's Encrypt HTTPS certificate without purchasing a custom domain:

```bash
git clone https://github.com/voskalo/PidKlyuch.git
cd PidKlyuch
cp infra/.env.example infra/.env
```

Generate a strong `JWT_SECRET`:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Edit `infra/.env` (never commit `.env` to git):

```dotenv
DOMAIN=3-75-120-45.sslip.io
ACME_EMAIL=your-email@example.com
POSTGRES_USER=pidklyuch
POSTGRES_PASSWORD=<strong-db-password>
POSTGRES_DB=pidklyuch
DATABASE_URL=postgresql+psycopg://pidklyuch:<strong-db-password>@db:5432/pidklyuch
# Or point DATABASE_URL to AWS RDS for PostgreSQL:
# DATABASE_URL=postgresql+psycopg://user:pass@<rds-endpoint>:5432/pidklyuch?sslmode=require
JWT_SECRET=<generated-48-byte-secret>
JWT_EXPIRE_MINUTES=10080
CORS_ORIGINS=https://3-75-120-45.sslip.io
NBU_API_URL=https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json
VITE_API_URL=/api
```

### Step 4: Start the Production Stack & Verify HTTPS

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml up -d --build
docker compose --env-file infra/.env -f infra/docker-compose.yml logs -f caddy backend
```

Verify from your browser or `curl`:
- `https://<DOMAIN>/healthz` → `OK`
- `https://<DOMAIN>/api/health` → `{"status":"ok"}`
- `https://<DOMAIN>/` → PidKlyuch web UI over valid HTTPS

### Step 5: Optional Weekly Law-Watcher Check (`cron`)
Monitor `zakon.rada.gov.ua` source clauses weekly so any legislative change triggers a non-zero exit alert:

```bash
0 9 * * 1 cd /home/ubuntu/PidKlyuch && docker compose --env-file infra/.env -f infra/docker-compose.yml exec -T backend python scripts/check_law_updates.py
```

# AGENTS.md — Shared AI Context & Work Log for PidKlyuch

> **Every AI agent (Claude Code, Codex, Cursor, Copilot, Gemini, etc.) working in this repo MUST read this file first.**
> It is the single source of truth about the project. Read this file *instead of* scanning the whole repo,
> and open individual source files only when you need to change them.
>
> **Every AI agent MUST also update this file at the end of every task** (see §1). If you changed the repo and did
> not update this file, the task is not finished.

---

## 0. Quick facts (keep this section current)

| Item | Value |
|---|---|
| Product | PidKlyuch («Під ключ») — a web calculator for the full landed price of goods imported into Ukraine (parcel → car): duty, VAT, excise |
| Course | OOAD (OOP), 2nd year, university team project |
| Team | Liubomyr Voskalo, Anna Kravchenko, Anton Vertyporoh |
| **Deadline** | **Thursday 19 November 2026 (Module 11)**: live demo + submission |
| Current phase | Day 2 (Tue 17 Nov 2026): **Full-stack app live over HTTPS on AWS EC2** (`i-00ab50698f9435a50`, project `334177992228`, `eu-north-1`) with React 19 UI + FastAPI + PostgreSQL 16 + Caddy Let's Encrypt TLS; PR #3 (`anton/infra-and-docs`) ready to merge into `main`; user testing Wed 18 Nov |
| Tech stack | Backend: Python 3.12+ / FastAPI + SQLAlchemy 2.0 (SQLite local, PostgreSQL 16 prod). Frontend: React 19 + TypeScript + Vite + Tailwind CSS v4. Hosting: AWS EC2 + Docker Compose + Caddy v2 (see §5) |
| Live demo URL | https://16.170.212.120.sslip.io _(full-stack React SPA + FastAPI + PostgreSQL 16 over Let's Encrypt HTTPS on AWS EC2 `i-00ab50698f9435a50`; Swagger UI at `/api/docs`)_ |
| Repo URL | https://github.com/voskalo/PidKlyuch (`main` has `backend/`, `frontend/`, `infra/`, `docs/` since PRs #1–#3; edge-case fixes via PR #4) |

---

## 1. MANDATORY rules for AI agents

### 1.1 Before you start a task
1. Read this whole file.
2. Check §0 (current phase), §6 (repo structure), §8 (API contract), and the last ~10 entries of §12 (Change log).
3. Check §11 (Open issues / TODO) for anything related to your task.
4. Find out which team member you are working for. Their area of ownership is in §3. Do **not** rewrite another
   member's area without saying so explicitly in the log, because teammates use different agents and will not know.
5. Check §14 (Runbooks). If a runbook there is assigned to the member you work for and is not marked DONE, tell them
   about it at the start of the session and offer to run it.

### 1.2 While working
- Follow the conventions in §9.
- Never commit secrets (API keys, DB passwords, JWT secrets). Put them in `.env` (git-ignored) and document the
  variable **name** in `.env.example` and in §7.
- Keep the required top-level layout: `backend/`, `frontend/`, `infra/`, `README.md` (graded).

### 1.3 After every task (REQUIRED)
Update this file, in this order:
1. **§12 Change log**: append a new entry using the template in §12. Newest entries go at the **bottom**.
2. **§0 Quick facts**: update the phase, stack, URLs if they changed.
3. **§6 Repo structure**: if you added or moved files or folders, update the tree and describe what each part does.
4. **§5 Tech stack / §7 Env vars / §8 API contract**: update if you touched them.
5. **§10 Decisions**: if you made a non-obvious choice (library, schema, formula, hosting), add it with the reason.
6. **§11 Open issues / TODO**: add what is left, and remove what you finished.

Write log entries so that **another AI with no other context** can continue the work. Be concrete: file paths,
function names, endpoints, commands, and what is not working yet. Do not write "updated stuff" or "minor fixes".

If you are not sure whether something is worth logging, log it.

---

## 2. Product summary (from the one-page pitch)

**Tagline:** Know the full price of anything you buy abroad, from a parcel to a car.

**Problem:** Ukrainian import customs rules differ heavily by category, so the final cost is unpredictable.
- A €200 parcel adds ~€16 in unexpected duties.
- A €10,000 car adds €2,048–€4,640 in import taxes.
- From **July 2027**, mandatory VAT applies to **every** imported parcel (no duty-free threshold for VAT).

**Product:** A web calculator. The user selects an import category (electronics, clothing, vehicles, …) and a
delivery type (parcel, luggage, car), enters item price and shipping, and gets the exact final landed price with an
itemized breakdown of duty, VAT, and excise in under one minute.

**Target users**
- Primary B2C: Ukrainians aged 18–35 ordering from Amazon, eBay, or AliExpress near the €150 duty limit (75.6M parcels in 2025).
- Secondary B2C: people self-importing used cars from the EU or North America (278,628 cars in 2025).
- B2B (future): parcel forwarders and car-import brokers who want to embed the calculator (API or white-label).

**V1 feature scope from the pitch** (see §4 for what is actually in the demo)
1. Smart input flow: category + delivery type → short dynamic question flow.
2. Itemized tax breakdown: duty, VAT, and excise, each with a transparent formula.
3. Scenario and exchange-rate comparison: 3 carrier offers side by side, today's rules vs. July 2027 rules, live NBU daily rates.
4. User account and alerts: saved calculation history, price tracking, alerts when customs rules change.

**Validation plan from the pitch:** friends' opinions don't count; users must pay with time or donations.
Interviews (6 of 10 didn't know their final cost) → MVP with sign-up (100+ sign-ups, 30% return in 14 days) →
voluntary donation button (10+ donations).

---

## 3. Team & ownership

Full division of work is in `README.md` → "Team & division of work". Summary:

| Member | Owns | Folders |
|---|---|---|
| **Liubomyr Voskalo** | Backend: API, database, auth (sign-up/sign-in), **customs rules research + rates file**, calculation engine, law watcher, NBU rates, history | `backend/` |
| **Anna Kravchenko** | Frontend: all UI, calculator flow, breakdown view, auth pages, history page, donation button | `frontend/` |
| **Anton Vertyporoh** | Infra and deploy on **AWS** (HTTPS), scheduled law-watcher run, customs spec & test cases (`docs/`), user testing coordination, final report | `infra/`, `docs/` |

The main interface between members is the **API contract (§8)**, owned by Liubomyr and consumed by Anna.
Customs rules live in `backend/app/customs/tax_rates.json` (source of truth for backend runtime) and are documented with worked test cases in `docs/customs-rules.md`, summarized in §13.

---

## 4. Assignment requirements (graded)

Build a working prototype of the product, put it in front of real users, and report what happened.
Demo: **Thursday 19 November 2026**. **Every team member submits individually.**

Submit:
- Online text: link to the repository + URL of the running demo.
- File: the report (PDF).

| Criterion | Points | Status |
|---|---|---|
| Repo organised with top-level `backend/`, `frontend/`, `infra/` and a `README.md` that tells a stranger what the product is and how to run and deploy it | 3 | ✅ `backend/`, `frontend/`, `infra/`, `docs/`, and `README.md` complete |
| Working prototype with sign-in: deployed, reachable over **HTTPS**, users can **sign up and sign in** | 3 | ✅ Live at `https://16.170.212.120.sslip.io` (AWS EC2 `i-00ab50698f9435a50`, Let's Encrypt HTTPS + React + FastAPI + Postgres 16) |
| Report with user feedback: who you showed it to, how many tried it, what they said, **what you changed because of it** | 4 | 🟡 User testing script, Google Form & recruiting templates ready; sessions Wed 18 Nov |
| **Bonus:** users ready to pay real money (donation to a volunteer cause, or a working payment in the product), with **evidence in the report** | bonus | ⬜ Donation modal ready in UI; collect screenshots during Wed testing |

**Demo MVP scope (must have by Wed evening):**
- Sign up, sign in, sign out.
- Calculator for **parcels** (category, price, shipping, currency) → itemized duty / VAT / total, with formulas shown.
- Calculator for **cars** (price, engine type/volume, year) → duty / excise / VAT / total.
- "Today's rules vs. July 2027 rules" toggle or side-by-side for parcels.
- Currency conversion using NBU rates (live, with a cached fallback).
- Saved calculation history for signed-in users.
- Donation button/link (for a volunteer cause, for the bonus).
- Simple usage tracking (sign-ups, calculations) to put numbers in the report.

**Nice to have (only if time remains):** compare 3 carrier offers, rule-change alerts, price tracking, luggage mode.

Update the Status column above when a criterion is met.

---

## 5. Tech stack

**Confirmed 2026-11-17** (Backend chosen by Liubomyr, Frontend by Anna, AWS hosting & reverse proxy by Anton).

| Layer | Choice | Notes |
|---|---|---|
| Backend language/framework | **Python 3.12+ / FastAPI** | `backend/`, entry point `app.main:app` (uvicorn on `$PORT`, default `8000`, `--proxy-headers`) |
| ORM / Database | **SQLAlchemy 2.0**: SQLite locally, **PostgreSQL 16** in prod | Set via `DATABASE_URL` (`postgres:16-alpine` in Compose or AWS RDS Postgres); tables auto-created on startup via `init_db()` |
| Auth method | **JWT bearer tokens** (PyJWT, HS256) + optional **Google Sign-In** (GIS ID tokens) | Passwords hashed with stdlib PBKDF2-SHA256 (`390,000` iterations); Google ID tokens verified via `google-auth` (`POST /api/auth/google`) |
| Tests | **pytest** + FastAPI `TestClient` | `cd backend && .venv/bin/pytest` (126 tests passing on `main`) |
| Frontend framework | **React 19 / TypeScript / Vite 8 / Tailwind CSS v4** | `frontend/`, Lucide Icons, dev proxy `/api` → `127.0.0.1:8000`; built with Node 22 and served on `:80` behind Caddy in prod |
| Hosting (backend & frontend) | **AWS EC2 (Ubuntu 24.04)** + **Docker Compose + Caddy v2** (automatic HTTPS) | Single HTTPS origin via `<EC2-IP>.sslip.io` (Let's Encrypt TLS); `/api/*` → `backend:8000`, `/*` → `frontend:80` |
| Database (prod) | **PostgreSQL 16** (Docker Compose `db` or **AWS RDS for PostgreSQL**) | Set via `DATABASE_URL` (`?sslmode=require` if using RDS; never SQLite in prod) |
| Secrets | `.env` locally / AWS Secrets Manager or SSM on EC2 | `JWT_SECRET`, `POSTGRES_PASSWORD` never committed to git |
| Logs | Docker Compose stdout / **CloudWatch Logs** | Uvicorn + Python `logging` + Caddy access logs |
| Infra as code | `infra/` (Docker Compose, multi-stage Dockerfiles, Caddyfile) | Includes `--profile fallback` (`hello:80`) and full-stack setup |
| CI / CD | **GitHub Actions** `.github/workflows/ci-cd.yml` | every push/PR: `pytest` + `npm run build`; push to `deploy` → SSH deploy to EC2 + HTTPS health check (see §9) |
| Automation | `backend/scripts/check_law_updates.py` | Weekly law-watcher cron verifying `zakon.rada.gov.ua` fingerprints against `tax_rates.json` |

**AWS implications for the backend (already handled or to keep in mind):**
- **Do not use SQLite in prod.** Container filesystems are ephemeral; `DATABASE_URL` points to PostgreSQL (`db` or RDS).
- The container listens on `$PORT` (default `8000`), and uvicorn runs with `--proxy-headers --forwarded-allow-ips='*'`, working behind Caddy or ALB.
- Outbound internet access is required for NBU API (`bank.gov.ua`); if unreachable, the backend cleanly falls back to `FALLBACK_UAH_PER_UNIT` (`rate_source: "fallback"`).
- Routing `/api/*` and `/*` through the same Caddy HTTPS origin eliminates CORS overhead in production (while `CORS_ORIGINS` also includes the `https://<DOMAIN>` origin).
- Tables are auto-created on startup (`init_db()`), so first boot against an empty Postgres DB needs no manual SQL.

---

## 6. Repository structure

Current state (update on every structural change):

```
PidKlyuch/
├── AGENTS.md                  # this file: shared AI context + work log (read first, update last)
├── CLAUDE.md                  # pointer so Claude Code auto-loads AGENTS.md
├── README.md                  # public description, team division of work, run & deploy instructions
├── backend/                   # FastAPI service (owner: Liubomyr)
│   ├── requirements.txt       # runtime deps (pinned)
│   ├── requirements-dev.txt   # + pytest
│   ├── .env.example           # documented env vars (copy to .env)
│   ├── Dockerfile             # python:3.12-slim, runs uvicorn on $PORT (default 8000)
│   ├── scripts/check_law_updates.py  # law watcher: compares zakon.rada.gov.ua fingerprints with tax_rates.json
│   ├── app/
│   │   ├── main.py            # create_app(): CORS, routers, DB init on startup
│   │   ├── core/              # config.py (Settings), database.py (init_db, normalize_db_url), security.py (PBKDF2 + JWT)
│   │   ├── api/               # health.py, auth.py, calculate.py, history.py, deps.py, schemas_{auth,calc}.py
│   │   ├── models/            # SQLAlchemy ORM models: user.py (User), calculation.py (Calculation)
│   │   ├── services/          # auth_service.py, rates_service.py, calculation_service.py, history_service.py
│   │   └── customs/           # pure Python engine: tax_rates.json, rules.py, models.py, calculators.py
│   └── tests/                 # pytest (126 tests). Run: cd backend && .venv/bin/pytest
│                              #   test_edge_cases.py = hostile/boundary input (bad tokens, NaN, decimals, thresholds
│                              #   after conversion, car year/engine bounds, signup race, CORS) + 17.11 regressions
├── frontend/                  # React 19 + TypeScript + Vite SPA (owner: Anna)
│   ├── package.json           # React 19, TypeScript, Vite 8, Tailwind CSS v4, Lucide Icons
│   ├── vite.config.ts         # dev server on port 5173 with proxy /api → http://127.0.0.1:8000
│   ├── index.html             # meta tags, Ukrainian title & description, responsive viewport
│   ├── public/favicon.svg     # key brand icon
│   ├── README.md              # frontend documentation & run guide
│   └── src/
│       ├── main.tsx           # React DOM root entry point
│       ├── index.css          # Tailwind CSS v4 root stylesheet
│       ├── App.tsx            # Main UI layout, hero, calculator tabs (parcels/cars), state & modals
│       ├── types/api.ts       # TypeScript models matching backend §8 contract
│       ├── services/api.ts    # Fetch API wrapper with JWT Bearer auth & VITE_API_BASE_URL
│       ├── context/AuthContext.tsx # React AuthProvider (user state, login/signup/logout, token storage)
│       └── components/        # Navbar, RatesBar, ParcelForm, CarForm, BreakdownView, CompareRulesModal, HistoryView, AuthModal, DonationModal, StatsModal, Footer
├── .github/workflows/ci-cd.yml # CI on every push/PR (backend pytest + frontend build); push to `deploy` → auto-deploy to EC2
├── infra/                     # Docker, deployment configs, Caddy HTTPS proxy (owner: Anton)
│   ├── deploy_key.pub         # PUBLIC half of the GitHub Actions deploy key (goes into the server's authorized_keys)
│   ├── hello-world/index.html # Fallback static status/landing page for HTTPS smoke test
│   ├── .env.example           # Full-stack Compose, DB, Caddy, backend & frontend env var template
│   ├── .gitignore             # Ignores infra/.env and *.env.local
│   ├── Caddyfile              # Caddy v2 reverse proxy (/healthz, /api/docs*, /api/* -> backend, /* -> frontend)
│   ├── Dockerfile             # Lightweight caddy:2-alpine static server image for fallback hello-world
│   ├── backend.Dockerfile     # Production Python 3.12 FastAPI container with /api/health HEALTHCHECK
│   ├── frontend.Dockerfile    # Multi-stage Node 22 Vite build + Caddy static SPA server
│   ├── docker-compose.yml     # Full-stack Compose (db, backend, frontend, caddy + fallback hello profile)
│   └── README.md              # Deployment architecture, full-stack & fallback modes, AWS EC2 HTTPS guide
└── docs/                      # Customs spec, user-testing docs, report (owner: Anton)
    ├── customs-rules.md       # Locked Ukrainian customs spec (parcels, cars, NBU rates, 10 test cases)
    ├── recruiting-messages.md # Ukrainian outreach templates for Telegram/FB/DMs (15+ testers)
    └── user-testing-plan.md   # Moderator script (2 tasks), Google Form questions, 15-tester tracker table
```

**Frontend architecture:**
`App.tsx` (state orchestrator, tab switching, modals) → `context/AuthContext.tsx` (token & user session) → `services/api.ts` (HTTP layer with Bearer token & `VITE_API_BASE_URL`) → `components/` (presentational & dynamic forms/modals).

**Backend architecture:**
`api/` (HTTP: routing, pydantic validation, auth dependencies) → `services/` (use cases: `AuthService`, `CalculationService`, `RatesService`, `HistoryService`) → `customs/` (pure domain logic, no I/O) and `models/` (ORM).

---

## 7. Environment variables

Format: `NAME`: where it is used, example value (never a real secret), required or optional.

### Infra & Reverse Proxy (`infra/.env.example`, `infra/docker-compose.yml`)
- `DOMAIN`: `infra/docker-compose.yml` & `infra/Caddyfile` (site block host for automatic HTTPS), example `13.60.162.78.sslip.io` or `localhost`, optional (defaults to `localhost`).
- `ACME_EMAIL`: `infra/docker-compose.yml` & `infra/Caddyfile` (Let's Encrypt / ACME notification email), example `admin@example.com`, optional (defaults to `admin@example.com`).
- `POSTGRES_USER`: Postgres container (`db` service in `infra/docker-compose.yml`), example `pidklyuch`, optional locally.
- `POSTGRES_PASSWORD`: Postgres container (`db` service in `infra/docker-compose.yml`), example `change-me-strong-db-password`, **required in prod** when using local Compose Postgres.
- `POSTGRES_DB`: Postgres container (`db` service in `infra/docker-compose.yml`), example `pidklyuch`, optional.

### Backend (`backend/.env.example`, `backend/app/core/config.py`)
- `DATABASE_URL`: backend, SQLAlchemy URL (`sqlite:///./pidklyuch.db` locally; `postgresql+psycopg://user:pass@host:5432/pidklyuch` or RDS URL with `?sslmode=require` in prod). Optional locally, **required in prod**.
- `JWT_SECRET`: backend, signs HS256 auth tokens. **Required in prod** (default `dev-insecure-secret-change-me` is insecure).
- `JWT_EXPIRE_MINUTES`: backend, token lifetime in minutes, default `10080` (7 days). Optional.
- `CORS_ORIGINS`: backend, comma-separated allowed origins, default `http://localhost:5173,http://localhost:3000`, e.g. `https://13.60.162.78.sslip.io`. **Required in prod.**
- `NBU_API_URL`: backend, NBU exchange-rate endpoint, default `https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json`. Optional.
- `PASSWORD_HASH_ITERATIONS`: backend, PBKDF2 iterations, default `390000` (lowered only in tests). Optional.
- `TAX_RATES_PATH`: backend, optional override path for `tax_rates.json` (default `app/customs/tax_rates.json`). Optional.
- `GOOGLE_CLIENT_ID`: backend, Google OAuth 2.0 Web Client ID used as expected `audience` when verifying ID tokens in `POST /api/auth/google`. Optional (defaults to `""`).

### GitHub Actions secrets (repo Settings → Secrets → Actions; used by `.github/workflows/ci-cd.yml`)
- `EC2_HOST` (`16.170.212.120`), `EC2_USER` (`ubuntu`): the SSH target. **Set 18.11.** Update `EC2_HOST` if the server IP changes.
- `EC2_SSH_KEY`: private half of a dedicated ed25519 deploy key (the public half is `infra/deploy_key.pub`). **Set 18.11.**
  The private key exists ONLY in GitHub secrets; to rotate, generate a new pair, `gh secret set EC2_SSH_KEY < key`, and
  replace the line in the server's `~/.ssh/authorized_keys`.
- `EC2_KNOWN_HOSTS`: pinned SSH host keys of the server (`ssh-keyscan 16.170.212.120`). **Set 18.11.** Re-set if the server is replaced.
- Optional: `EC2_APP_DIR` (default `/home/ubuntu/PidKlyuch`), `DEPLOY_URL` (default `https://<EC2_HOST>.sslip.io`).

### Frontend (`frontend/src/services/api.ts`, `frontend/src/components/AuthModal.tsx`, `infra/frontend.Dockerfile`)
- `VITE_API_BASE_URL`: frontend build-time env var, backend base URL (`https://api.pidklyuch.example.com` if hosted on a separate origin; leave empty `""` when behind Caddy on the same HTTPS origin because `api.ts` already prefixes `/api/...`). Optional locally (defaults to `""` with Vite `/api` proxy).
- `VITE_GOOGLE_CLIENT_ID`: frontend build-time env var, Google OAuth 2.0 Web Client ID for Google Identity Services (`https://accounts.google.com/gsi/client`). When empty, the Google Sign-In button is hidden cleanly. Optional.

---

## 8. API contract (backend ↔ frontend)

Owner: Liubomyr. Base path: `/api`. JSON everywhere. Interactive docs: `GET /docs` (and `GET /api/docs` via Caddy) on the running backend.
Auth: send `Authorization: Bearer <access_token>` (the token comes from sign-up/sign-in). Errors use the FastAPI
format: `{"detail": "..."}` (422 validation errors put a list in `detail`).
Money in responses is a **string with 2 decimals** (e.g. `"16.00"`), so no float rounding happens in JS.

| Status | Method | Path | Auth | Purpose |
|---|---|---|---|---|
| ✅ | GET | `/api/health` | – | liveness check for deploy & Docker healthcheck |
| ✅ | POST | `/api/auth/signup` | – | create account → token |
| ✅ | POST | `/api/auth/signin` | – | sign in → token |
| ✅ | POST | `/api/auth/google` | – | verify Google ID token & sign in / auto-register → token |
| ✅ | GET | `/api/auth/me` | required | current user |
| ✅ | POST | `/api/calculate` | optional | calculate landed price; saved to history if signed in |
| ✅ | POST | `/api/calculate/compare-rules` | – | parcel: current rules vs July 2027 rules |
| ✅ | GET | `/api/rates` | – | NBU rates used for conversion |
| ✅ | GET | `/api/history` | required | user's saved calculations, newest first |
| ✅ | DELETE | `/api/history/{id}` | required | delete one saved calculation |
| ✅ | GET | `/api/stats` | – | aggregate counters for the report |

**Sign-out** is client-side: delete the stored token (JWT is stateless).

**Token rules (since 17.11):** no `Authorization` header → anonymous (allowed on `/api/calculate`). A header with an
invalid or expired token → **401 on every endpoint, including `/api/calculate`**, so the client signs the user out
instead of silently not saving to history. Retrying without the header works anonymously.

**Notes for the frontend:**
- Store the `access_token` in `localStorage` (`pidklyuch_access_token`) and send it on every request. `/api/calculate` works without it too, but then `calculation_id` is `null`.
- On any `401`, clear the token and show sign-in.
- CORS allows `http://localhost:5173` (Vite) and `http://localhost:3000` by default.

**POST /api/auth/signup**: body `{"email": "a@b.com", "password": "8–128 chars", "name": "Anna"}` (`name` optional,
max 100 chars, trimmed; blank → `null`; the email is trimmed and lowercased)
→ `201 {"access_token": "...", "token_type": "bearer", "user": {"id": 1, "email": "a@b.com", "name": "Anna", "created_at": "ISO"}}`.
`409` if the email is already registered.

**POST /api/auth/signin**: body `{"email", "password"}` → `200`, same shape as signup. `401` on wrong credentials.

**POST /api/auth/google**: body `{"credential": "<google_id_token>"}` → `200`, same `TokenOut` shape as signin/signup; links existing user by email (`google_sub`) or auto-registers an OAuth user (`auth_provider="google"`). `401` on invalid/unverified token.

**GET /api/auth/me** → `{"id", "email", "name", "created_at"}`. `401` if missing/invalid/expired token.

**POST /api/calculate**: body is either a parcel or a car (discriminated by `delivery_type`):
```json
{"delivery_type": "parcel", "category": "electronics", "item_price": 200, "shipping_price": 15,
 "currency": "EUR", "rules": "current", "sender": "marketplace"}
```
- `category`: `electronics | clothing | cosmetics | toys | other`
- `currency`: `EUR | USD | UAH | GBP | PLN`
- `rules`: `current | july_2027` (default `current`)
- `sender`: `marketplace | private` (default `marketplace`; only affects `july_2027`, where `private` $\le €45$ is tax-free)
```json
{"delivery_type": "car", "car_price": 10000, "shipping_price": 1200, "currency": "EUR",
 "engine_type": "petrol", "engine_volume_cc": 2000, "battery_kwh": null,
 "manufacture_year": 2014, "origin": "eu"}
```
- `engine_type`: `petrol | diesel | hybrid | electric` (`engine_volume_cc` required for petrol/diesel/hybrid; `battery_kwh` required for electric)
- `origin`: `eu | other` (`eu` = EUR.1 / origin declaration proved, 0% duty; EVs always have 0% duty)

Response `200`:
```json
{"delivery_type": "parcel", "rules": "current", "input_currency": "EUR",
 "rate_date": "2026-11-16", "rate_source": "nbu", "eur_uah": "50.2220",
 "goods_value_eur": "200.00", "shipping_eur": "15.00",
 "lines": [
   {"code": "duty", "label": "Мито", "amount_eur": "5.00", "amount_uah": "240.62",
    "formula": "10% × (200.00 − 150.00) = 5.00 EUR"},
   {"code": "vat", "label": "ПДВ", "amount_eur": "11.00", "amount_uah": "529.36",
    "formula": "20% × (50.00 + 5.00) = 11.00 EUR"}
 ],
 "taxes_total_eur": "16.00", "taxes_total_uah": "769.97",
 "landed_total_eur": "231.00", "landed_total_uah": "11116.51",
 "notes": ["..."], "rates_version": "2026-11-16", "rates_verified_at": "2026-11-16",
 "calculation_id": 42}
```
`line.code` ∈ `duty | excise | vat`. A parcel under the threshold has `lines: []`. `calculation_id` is `null`
when the caller is not signed in. `rate_source` is `"fallback"` if NBU was unreachable, in which case `notes` says so
and the UI should show a small warning. `formula` and `notes` are Ukrainian text, ready to display. The 422 body for
a car missing `engine_volume_cc` / `battery_kwh` contains the reason in `detail[0].msg`. Since 17.11, 422 errors
only describe the model chosen by `delivery_type` (before, a bad car also produced "Input should be 'parcel'"). An
unknown `delivery_type` gives `detail[0].type == "union_tag_invalid"`. Prices accept at most 2 decimal places
(`"150.005"` → 422), so the UI should round or limit input to cents.
`rates_verified_at` = the date the tax rates were last checked against the law. Show it in the UI (e.g. "Ставки
станом на 16.11.2026"). Parcels over €10,000 get a note that the result is only approximate.

**POST /api/calculate/compare-rules**: same parcel body (`rules` ignored) → `{"current": <result>, "july_2027": <result>}`.

**GET /api/rates** → `{"date": "2026-11-16", "source": "nbu" | "fallback", "uah_per_unit": {"UAH": "1", "EUR": "50.222", "USD": "45.4274", "GBP": "60.106", "PLN": "11.3916"}}`.

**GET /api/history** → `[{"id", "created_at", "delivery_type", "input": {...}, "result": {...}}]` (max 100, newest first).

**DELETE /api/history/{id}** → `204` (`404` if missing or not owner).

**GET /api/stats** → `{"users": 12, "calculations": 80, "calculations_by_signed_in": 40, "returning_users": 5}`.

---

## 9. Conventions

- **Git:** short-lived branches `name/feature` (e.g. `anna/calculator-ui`), merge to `main` via PR or after a quick
  review in chat. Do not force-push `main`.
- **Deploying = updating the `deploy` branch.** Every push to `deploy` runs `.github/workflows/ci-cd.yml`: backend tests +
  frontend build, then (only if green) SSH to EC2 → `git merge --ff-only origin/deploy` → `docker compose up -d --build`
  → checks `/api/health` and `/` over HTTPS. To release what is on `main`:
  `git push origin main:deploy` (fast-forward; never force-push `deploy`). Watch it in the repo's **Actions** tab.
  Do not edit tracked files directly on the server: the fast-forward then refuses and the deploy stops (by design).
- **Commits:** imperative, short (`Add parcel duty calculation`). If an AI wrote the commit, it may add its own
  co-author line.
- **Secrets:** never in git. Use `.env` + `.env.example`.
- **Money:** do not use binary floats for money if avoidable (use decimal types or integer cents). Round only for
  display. Always keep the currency next to the amount.
- **Customs logic** lives in one place in the backend (a single module or service), not duplicated in the frontend.
- **Language:** code and docs in English. UI text in Ukrainian (target users), with English optional.

---

## 10. Decisions log

Format: `YYYY-MM-DD: decision: reason (who)`

- 2026-11-16: `AGENTS.md` is the single shared AI context file. `CLAUDE.md` only imports it. Reason: the team uses
  different AI agents. Most of them (Codex, Cursor, Copilot, Gemini CLI via config) read `AGENTS.md`, and Claude Code
  reads `CLAUDE.md`. (Liubomyr + Claude Code)
- 2026-11-16: Backend = Python/FastAPI + SQLAlchemy. Reason: fastest path to a working, tested API in 3 days.
  Auto-generated `/docs` lets Anna explore the API, and SQLAlchemy lets the same code run on SQLite locally and
  Postgres in prod. (Liubomyr + Claude Code)
- 2026-11-16: Money in API responses is a string with 2 decimals, and internally it is `decimal.Decimal`. Reason: avoid
  float rounding errors in tax math. (Liubomyr + Claude Code)
- 2026-11-16: Customs engine = Strategy pattern (`CustomsCalculator` → `ParcelCalculator`, `CarCalculator`) with
  rules injected as immutable `ParcelRules`/`CarRules` objects. Reason: "today vs July 2027" is just a different
  rules object, new delivery types (luggage) are a new class, and rates change in one file. (Liubomyr + Claude Code)
- 2026-11-16: All calculations are persisted, including anonymous ones, to get real usage numbers for the report
  (`/api/stats`). "Returning user" = a user with calculations on 2 or more different UTC days. (Liubomyr + Claude Code)
- 2026-11-16: **All hosting on AWS**, using Docker Compose + Caddy v2 for deployment and automatic Let's Encrypt HTTPS. (Liubomyr + Anton)
- 2026-11-16: **All tax numbers live in `backend/app/customs/tax_rates.json`** monitored by `scripts/check_law_updates.py` rather than auto-updated from the internet. (Liubomyr + Claude Code)
- 2026-11-16: Customs rules verification moved from Anton to Liubomyr (`tax_rates.json` + law watcher); Anton documented the locked spec and 10 test fixtures in `docs/customs-rules.md`. (Liubomyr + Anton)
- 2026-11-17: Frontend stack = React 19 + TypeScript + Vite 8 + Tailwind CSS v4 + Lucide Icons, with dev proxy `/api` → `http://127.0.0.1:8000` and dedicated volunteer donation modal («Повернись живим», Фонд Сергія Притули, Monobank). (Anna + Gemini)
- 2026-11-17: Host full-stack deployment on AWS EC2 (Ubuntu 24.04) using Docker Compose (`db` Postgres 16, `backend`, `frontend` built on Node 22 with empty `VITE_API_BASE_URL` for same-origin proxy, `caddy` v2) and `<EC2-IP>.sslip.io` for zero-DNS-purchase automatic Let's Encrypt HTTPS, eliminating CORS friction. (Anton + Antigravity CLI)
- 2026-11-18: Form input UX polish: replaced default OS `<select>` dropdown styling with `appearance-none`, custom `ChevronDown`, `shrink-0 min-w-[76px]` and added `min-w-0` to flex inputs across `ParcelForm.tsx` and `CarForm.tsx` so currencies (EUR, USD, PLN, GBP, UAH) and units (см³, кВт⋅год, рік) fit cleanly without text truncation. (Anna + Gemini)
- 2026-11-18: Added quick currency switcher pills (`[EUR] [USD] [UAH] [PLN] [GBP]`) and currency symbols (`€ EUR`, `$ USD`, etc.) in price inputs, and replaced static tooltip on "Хто відправник" with an interactive expandable explanation card for July 2027 rules (Law 5025-IX / 5026-IX). (Anna + Gemini)

- 2026-11-18: **Auto-deploy via GitHub Actions on push to the `deploy` branch** (SSH to EC2 + docker compose), not on push
  to `main`. Reason: the team merges to `main` many times a day; a separate `deploy` branch makes releases deliberate,
  and every deploy is gated by the same tests as CI. Plain `ssh` (no third-party SSH action), a dedicated revocable
  deploy key, a pinned host key, and fast-forward-only updates on the server (never `reset --hard`, never touches
  `infra/.env`). Alternative considered: GitHub OIDC → IAM role → SSM Run Command (no SSH key) — better long-term,
  but needs IAM setup in Anton's AWS account; not worth it the day before the demo. (Liubomyr + Claude Code)
---

## 11. Open issues / TODO

- [x] Choose the tech stack and fill in §5 (all — Backend FastAPI/SQLAlchemy, React 19 + TS + Vite + Tailwind v4, AWS EC2 + Docker Compose + Caddy v2 HTTPS).
- [x] Create `backend/`, `frontend/`, `infra/`, `docs/` (`backend/` merged in PR #1; `frontend/` merged in PR #2; `infra/` & `docs/` merged into `anton/infra-and-docs`).
- [x] Write the API contract in §8 and implement all backend endpoints (Liubomyr).
- [x] Verify customs rates in `tax_rates.json` and finalize `docs/customs-rules.md` with 10 test cases (Liubomyr + Anton).
- [x] Deploy full-stack app (`db` + `backend` + `frontend` + `caddy`) on active AWS project `334177992228` (`eu-north-1`, EC2 `i-00ab50698f9435a50`, `https://16.170.212.120.sslip.io` verified `200 OK` across `/healthz`, `/api/health`, `/api/rates`, `/api/docs`, `/api/calculate`, `/api/stats`, and `/`).
- [x] Fill in "How to run" and "How to deploy" in `README.md` (Anton + Liubomyr + Anna).
- [x] Create user-testing script, Google Form questions, master tracker (`docs/user-testing-plan.md`), and Ukrainian recruiting templates (`docs/recruiting-messages.md`) (Anton).
- [x] Merge `anton/infra-and-docs` (PR #3) into `main` (merged 17.11).
- [x] **ONE-TIME, to enable auto-deploy (Anton, ~1 min):** appended `infra/deploy_key.pub` to `ubuntu@16.170.212.120:~/.ssh/authorized_keys` and fast-forwarded `origin/deploy` from `main` (18.11).
- [ ] Schedule `cd backend && python scripts/check_law_updates.py` weekly and alert team on non-zero exit (Anton).
- [ ] Run Wednesday user-testing sessions (15+ external testers, collect quotes, UX fixes, and donation screenshots) and write `docs/report.pdf` (all, Wed 18 – Thu 19 Nov).
- [ ] Re-check by hand when the Cabinet sets the start date of the July 2027 parcel VAT (source `law_5025_ix`) (Liubomyr).
- [ ] Optional: a "luggage" delivery type. The rules are already verified (Customs Code 374 p.1 and p.4) (Liubomyr).
- [ ] Frontend: show a Ukrainian message after a 401 on calculate, and limit price inputs to 2 decimals (Anna).

---

## 12. Change log

**Template (copy for each entry, newest at the bottom):**

```
### YYYY-MM-DD HH:MM: <short title>
- **Who:** <team member> via <agent + model, e.g. Claude Code (Opus 5.5) / Codex / Cursor>
- **Area:** backend | frontend | infra | docs | repo
- **What was done:** <concrete description>
- **Files touched:** <paths, created/modified/deleted>
- **Decisions & why:** <or "none">
- **How to verify / run:** <commands, URLs, or "n/a">
- **Not done / known problems / next steps:** <or "none">
```

### 2026-11-16: Created shared AI context file and work division
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** repo / docs
- **What was done:** Created `AGENTS.md`, `CLAUDE.md`, and initial `README.md`.
- **Files touched:** `AGENTS.md` (created), `CLAUDE.md` (created), `README.md` (modified)
- **Decisions & why:** see §10, first entry.
- **How to verify / run:** n/a (docs only)
- **Not done / known problems / next steps:** see §11.

### 2026-11-16: Backend scaffold, Auth, Customs Engine, NBU Rates, History, Law Watcher
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend / docs
- **What was done:** Implemented complete FastAPI + SQLAlchemy backend MVP (`backend/`): JWT auth (`/api/auth/*`), Strategy-pattern parcel/car calculation engine with `tax_rates.json` (verified against МКУ/ПКУ and Laws № 5025-IX / № 5026-IX), live NBU exchange rates (`RatesService`) with fallback, calculation history & usage `/api/stats`, `scripts/check_law_updates.py` clause-fingerprint watcher, `backend/Dockerfile`, and 66 passing pytest tests. Recorded AWS hosting plan and API contract (§8).
- **Files touched:** `backend/` (created), `README.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** see §10 (FastAPI, Decimal money, `tax_rates.json`, AWS).
- **How to verify / run:** `cd backend && .venv/bin/pytest` (66 passed); `.venv/bin/python scripts/check_law_updates.py` (all `[ok]`).
- **Not done / known problems / next steps:** Merged into `main` via PR #1 (`cbb4ece`).

### 2026-11-16 13:33–13:42: Infra day-1 HTTPS config & `docs/customs-rules.md`
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra / docs
- **What was done:** Created `infra/` day-1 skeleton (`README.md`, `Dockerfile`, `hello-world/index.html`, `Caddyfile`, `docker-compose.yml` using `caddy:2-alpine`) and `docs/customs-rules.md` (precision rules, official sources, parcel current/July 2027 formulas, NBU rate specs, car import formulas, and 10 worked test cases `TC-P1`..`TC-P5`, `TC-C1`..`TC-C5` with JSON fixture).
- **Files touched:** `infra/*` (created), `docs/customs-rules.md` (created), `AGENTS.md` (modified)
- **Decisions & why:** Docker Compose + Caddy v2 for automatic HTTPS; deterministic offline test fixtures in `docs/customs-rules.md`.
- **How to verify / run:** `DOMAIN=localhost docker compose -f infra/docker-compose.yml up --build`.
- **Not done / known problems / next steps:** Full-stack Compose wiring and live EC2 deployment.

### 2026-11-17: Backend PR #1 & Frontend SPA PR #2 merged into `main`
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5) & Anna Kravchenko via Antigravity (Gemini 3.8 Flash)
- **Area:** repo / frontend
- **What was done:** Merged `liubomyr/backend` into `main` (PR #1, `cbb4ece`). Built and merged the full responsive React 19 + TypeScript + Vite 8 + Tailwind CSS v4 frontend in `frontend/` (PR #2, `0895245`): AuthModal + AuthContext, ParcelForm & CarForm with live $K_{age}$ preview, BreakdownView with transparent formulas, CompareRulesModal ("Today vs July 2027"), HistoryView, RatesBar, DonationModal («Повернись живим», Сергій Притула, Monobank), and StatsModal (`/api/stats`). Verified `npm run build` compiles with 0 errors.
- **Files touched:** `frontend/` (created), `README.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** see §10 (React 19 + TypeScript + Vite + Tailwind v4, proxy `/api`, `VITE_API_BASE_URL`).
- **How to verify / run:** `cd frontend && npm install && npm run build` (outputs `dist/`); `npm run dev` on `http://localhost:5173`.
- **Not done / known problems / next steps:** Full-stack AWS HTTPS deployment by Anton.

### 2026-11-17 11:12–11:28: Lock customs spec, full-stack Compose/Caddy infra, README guides & user testing prep
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra / docs / repo
- **What was done:** Resolved legal TODOs in `docs/customs-rules.md` to match Laws № 5025-IX / № 5026-IX and `tax_rates.json`. Upgraded `infra/` with `backend.Dockerfile`, `frontend.Dockerfile`, `.env.example`, `.gitignore`, `db` (`postgres:16-alpine`), and Caddy routing (`/healthz`, `/api/*`, `/*` with `--profile fallback`). Added full-stack "How to run" and AWS EC2 "How to deploy" guides to `README.md`. Created `docs/user-testing-plan.md` (moderator script, 8 Google Form questions, 15-tester tracker table) and `docs/recruiting-messages.md` (4 Ukrainian outreach templates).
- **Files touched:** `docs/{customs-rules.md,user-testing-plan.md,recruiting-messages.md}`, `infra/*`, `README.md`, `AGENTS.md`
- **Decisions & why:** Single HTTPS origin via Caddy v2 + `sslip.io` eliminates CORS friction and automates Let's Encrypt TLS.
- **How to verify / run:** Review `README.md`, `infra/README.md`, and `docs/`.
- **Not done / known problems / next steps:** Live EC2 deploy.

### 2026-11-17 12:18: Deploy fallback HTTPS stack on legacy AWS EC2
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra / docs
- **What was done:** Provisioned Ubuntu 24.04 `t3.micro` (`i-0f47475721f5e04a5`, `13.60.162.78`, `eu-north-1`) on legacy account `591554481308`, fixed Caddy v2 `handle /healthz` directive precedence in `infra/Caddyfile` and `frontend` alias in `infra/docker-compose.yml`, and verified `https://13.60.162.78.sslip.io/healthz` (`HTTP/2 200` `OK`).
- **Files touched:** `infra/Caddyfile`, `infra/docker-compose.yml`, `AGENTS.md`
- **Decisions & why:** Wrapped `/healthz` in `handle /healthz` because Caddy evaluates `reverse_proxy` before bare `respond` directives.
- **How to verify / run:** `curl -i https://13.60.162.78.sslip.io/healthz`
- **Not done / known problems / next steps:** Account `591554481308` was suspended; merge `origin/main` and deploy full stack on active AWS account `334177992228` (`main-aws`).

### 2026-11-17 17:12: Merge `origin/main` into `anton/infra-and-docs` and align `VITE_API_BASE_URL`
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** repo / infra / docs
- **What was done:** Merged `origin/main` (`0895245`, containing complete `backend/` and `frontend/` MVPs) into `anton/infra-and-docs` and resolved all conflicts in `README.md` and `AGENTS.md` cleanly. Updated `infra/frontend.Dockerfile` to Node 22 (`vite@8.3.8` engine requirement) with `ARG VITE_API_BASE_URL=""`, updated `infra/docker-compose.yml` and `infra/.env.example` to pass `VITE_API_BASE_URL`, and added `handle /api/docs* { uri strip_prefix /api; reverse_proxy backend:8000 }` to `infra/Caddyfile` so both `/api/docs` and `/docs` serve Swagger UI.
- **Files touched:** `README.md`, `AGENTS.md`, `infra/frontend.Dockerfile`, `infra/docker-compose.yml`, `infra/.env.example`, `infra/Caddyfile`, `infra/README.md`
- **Decisions & why:** `frontend/src/services/api.ts` reads `VITE_API_BASE_URL` and already prefixes `/api/...`, so leaving `VITE_API_BASE_URL=""` routes browser API calls to the same Caddy HTTPS origin cleanly; Node 22 satisfies Vite 8's engine constraint.
- **How to verify / run:** `! git grep -E '^(<<<<<<<|=======|>>>>>>>)'` and `cd backend && .venv/bin/pytest`.
- **Not done / known problems / next steps:** Push `anton/infra-and-docs`, provision EC2 on active AWS account `334177992228` (`eu-north-1`), deploy full-stack Compose app, and verify HTTPS endpoints.

### 2026-11-17 17:17: Deploy full-stack PidKlyuch on active AWS project `334177992228` over HTTPS
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra / docs
- **What was done:** Provisioned Ubuntu 24.04 `t3.micro` EC2 instance (`i-00ab50698f9435a50`, public IP `16.170.212.120`) on active AWS project `334177992228` (`main-aws`, `eu-north-1`) with Security Group `sg-0921755abdeb9049f` (TCP `22`, `80`, `443` + UDP `443`), imported SSH key `pidklyuch-ec2` (`key-0bb3845d47275c9b2` from `~/.ssh/pidklyuch-ec2.pem`), configured 2 GB `/swapfile` for Node 22/Vite builds, generated `infra/.env` with random `JWT_SECRET`/`POSTGRES_PASSWORD` and `DOMAIN=16.170.212.120.sslip.io`, and launched full-stack Docker Compose (`db` Postgres 16, `backend` FastAPI, `frontend` React 19 SPA, `caddy` v2). Verified all endpoints over Let's Encrypt HTTPS. Updated `AGENTS.md` (§0, §4, §11, §12) and `README.md` (Live demo URL).
- **Files touched:** `AGENTS.md` (modified), `README.md` (modified)
- **Decisions & why:** Added 2 GB swapfile in user-data so Node/Vite production builds stay well within memory on `t3.micro`; full-stack serves frontend and `/api/*` under a single Caddy HTTPS origin (`https://16.170.212.120.sslip.io`).
- **How to verify / run:** `curl -i https://16.170.212.120.sslip.io/healthz` (`200 OK`), `curl -i https://16.170.212.120.sslip.io/api/health` (`200 OK`), `curl -s https://16.170.212.120.sslip.io/api/rates` (`200 OK`, live NBU), `curl -s -o /dev/null -w "%{http_code}" https://16.170.212.120.sslip.io/api/docs` (`200`), `curl -s -o /dev/null -w "%{http_code}" https://16.170.212.120.sslip.io/` (`200`), and `POST /api/calculate` (`200`, `taxes_total_eur: "16.00"`).
- **Not done / known problems / next steps:** PR #3 ready to merge `anton/infra-and-docs` into `main`; run Wednesday user testing sessions with `https://16.170.212.120.sslip.io` and compile `docs/report.pdf`.

### 2026-11-18 11:00: Fix currency and unit selector truncation in input fields
- **Who:** Anna Kravchenko via Antigravity (Gemini 3.8 Flash)
- **Area:** frontend
- **What was done:** Resolved UI clipping issue where currency selectors and badges were cut off to "EU" on certain screen widths and browsers. Added `min-w-0` to all number inputs to prevent flex items from crushing sibling containers; upgraded currency `<select>` with `appearance-none`, custom `ChevronDown` icon, `shrink-0 min-w-[76px]`, and `pl-3 pr-7`; centered and fixed unit badges (`см³`, `кВт⋅год`, `рік`, and shipping currency) with `shrink-0 min-w-[76px] justify-center` across `ParcelForm.tsx` and `CarForm.tsx`.
- **Files touched:** `frontend/src/components/ParcelForm.tsx`, `frontend/src/components/CarForm.tsx`, `AGENTS.md`
- **Decisions & why:** `appearance-none` removes unpredictable OS-native dropdown arrows that steal horizontal padding, while `shrink-0 min-w-[76px]` ensures 3-letter currency codes (EUR, USD, UAH, PLN, GBP) have dedicated comfortable spacing.
- **How to verify / run:** `cd frontend && npm run build` (0 errors); run `npm run dev` and inspect parcel/car forms: currencies and units fit with ample breathing room.
- **Not done / known problems / next steps:** None; ready for user testing sessions.

### 2026-11-18 11:10: High-visibility currency picker & interactive sender explanation popup
- **Who:** Anna Kravchenko via Antigravity (Gemini 3.8 Flash)
- **Area:** frontend
- **What was done:**
  1. **Enhanced Currency Visibility:** Added prominent one-click currency toggle chips (`EUR`, `USD`, `UAH`, `PLN`, `GBP`) directly in the field header above the price input in `ParcelForm.tsx` and `CarForm.tsx`. Upgraded dropdown options and badge displays to explicitly show currency symbols with bold text (`€ EUR`, `$ USD`, `₴ UAH`, `zł PLN`, `£ GBP`) on high-contrast backgrounds, ensuring the currency is immediately clear when entering prices.
  2. **Interactive Sender Explanation:** Replaced static HTML `title` tooltip on "Хто відправник" with an interactive button (`HelpCircle` icon + "Що це означає?" toggle) that opens an animated, accessible explainer card directly on mobile & desktop explaining why the sender type matters under Law № 5025-IX / 5026-IX (non-commercial gift up to €45 exempt from July 2027 vs marketplace parcels paying 20% VAT).
- **Files touched:** `frontend/src/components/ParcelForm.tsx`, `frontend/src/components/CarForm.tsx`, `AGENTS.md`
- **Decisions & why:** One-click currency pills provide the fastest UX for switching currencies without even opening a dropdown, and interactive in-place explainer eliminates mobile tooltip failure.
- **How to verify / run:** `cd frontend && npm run build` (builds in ~680ms with 0 errors); open `http://localhost:5173`, click the quick currency pills and click the `?` icon next to "Хто відправник" to see the explanation card.
- **Not done / known problems / next steps:** None; ready for user testing.


### 2026-11-18: GitHub Actions CI/CD with auto-deploy from the `deploy` branch
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** infra / repo
- **What was done:** Added `.github/workflows/ci-cd.yml` (there was no CI before):
  jobs `backend-tests` (Python 3.12, `pytest`), `frontend-build` (Node 22, `npm ci && npm run build`) on every
  push/PR, and `deploy` (only on push to `deploy`, after both pass): SSH to `ubuntu@16.170.212.120` →
  `cd /home/ubuntu/PidKlyuch` → fetch + `git checkout deploy` + `git merge --ff-only origin/deploy` →
  `docker compose --env-file infra/.env -f infra/docker-compose.yml up -d --build` → `docker image prune -f` →
  polls `https://<EC2_HOST>.sslip.io/api/health` and `/` until 200 (5 min max). Uses `sudo -n` automatically if the repo is
  root-owned (EC2 user-data clone). Refuses to deploy if `infra/.env` is missing. Generated a dedicated ed25519 deploy
  key: the private half was stored ONLY as GitHub secret `EC2_SSH_KEY` and deleted locally; the public half is
  `infra/deploy_key.pub`. Set the secrets `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `EC2_KNOWN_HOSTS` (pinned via `ssh-keyscan`).
  Created the `deploy` branch from `main`.
- **Files touched:** created `.github/workflows/ci-cd.yml`, `infra/deploy_key.pub`; modified `AGENTS.md` (§5, §6, §7,
  §9, §10, §11, §12), `README.md` (How to deploy → automatic deploys).
- **Decisions & why:** see §10 (deploy branch, plain ssh, fast-forward only).
- **How to verify / run:** repo → Actions tab → "CI/CD". After Anton adds the key: `git push origin main:deploy`, then
  watch the `deploy` job turn green and `curl https://16.170.212.120.sslip.io/api/health`.
- **Not done / known problems / next steps:** the deploy job cannot log in until the public key is added to the server
  (§11, Anton). Not tested end-to-end against the server yet for that reason. If the EC2 IP changes, update
  `EC2_HOST` and `EC2_KNOWN_HOSTS`.

### 2026-11-18 11:24: Add Google OAuth ID-token sign-in endpoint (`POST /api/auth/google`)
- **Who:** Anton Vertyporoh via Antigravity CLI (cross-area request in `backend/` with Liubomyr's auth pattern)
- **Area:** backend
- **What was done:** Added `google-auth==2.37.0` and `requests==2.32.3` to `backend/requirements.txt`; added `GOOGLE_CLIENT_ID` (`google_client_id`) to `Settings` and `backend/.env.example`; made `User.password_hash` nullable and added `google_sub` + `auth_provider` columns with safe idempotent `_migrate_users_table()` `ALTER TABLE` logic in `init_db()` (Postgres + SQLite); guarded `verify_password()` against empty/OAuth password hashes; added `GoogleAuthIn`, `InvalidGoogleToken`, `AuthService.authenticate_google()`, and `POST /api/auth/google` returning `TokenOut`; added 4 unit tests in `backend/tests/test_auth.py` mocking `id_token.verify_oauth2_token` (auto-registration, email account linking, invalid token 401, unverified email & audience forwarding).
- **Files touched:** `backend/requirements.txt`, `backend/.env.example`, `backend/app/core/{config.py,database.py,security.py}`, `backend/app/models/user.py`, `backend/app/api/{auth.py,schemas_auth.py}`, `backend/app/services/auth_service.py`, `backend/tests/test_auth.py`, `AGENTS.md`
- **Decisions & why:** OAuth-only users get `password_hash="!oauth"` and `auth_provider="google"`, keeping existing password auth rejected (`401`) while remaining compatible even with pre-existing SQLite tables; additive `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `init_db()` preserves production Postgres data without destructive migrations.
- **How to verify / run:** `cd backend && .venv/bin/pytest -v` (`126 passed in 0.67s`).
- **Not done / known problems / next steps:** Step 2 (frontend Google Sign-In UI) and Step 3–4 (infra, docs, live EC2 deploy).

### 2026-11-18 11:26: Add Google Sign-In UI flow in frontend (`AuthModal`, `AuthContext`, `api.ts`)
- **Who:** Anton Vertyporoh via Antigravity CLI (cross-area request in `frontend/` following Anna's React/TS patterns)
- **Area:** frontend
- **What was done:** Added `api.googleAuth(credential)` in `frontend/src/services/api.ts` posting `{ credential }` to `/api/auth/google` and persisting the returned JWT token; added `googleLogin(credential)` to `AuthContext`; updated `frontend/src/components/AuthModal.tsx` to load Google Identity Services (`https://accounts.google.com/gsi/client`) dynamically when `VITE_GOOGLE_CLIENT_ID` is set, render the localized (`uk`) Google button on both Sign In and Sign Up tabs, and hide the Google block cleanly without errors when `VITE_GOOGLE_CLIENT_ID` is empty.
- **Files touched:** `frontend/src/services/api.ts`, `frontend/src/context/AuthContext.tsx`, `frontend/src/components/AuthModal.tsx`, `AGENTS.md`
- **Decisions & why:** Dynamic script loader caches a singleton promise and measures modal container width dynamically (`Math.min(360, Math.max(220, offsetWidth))`) so the Google iframe never overflows narrow mobile viewports.
- **How to verify / run:** `cd frontend && npm run lint && npm run build && VITE_GOOGLE_CLIENT_ID=test npm run build` (0 errors).
- **Not done / known problems / next steps:** Step 3 (infra + docs + push) and Step 4 (live EC2 deploy).

### 2026-11-18 11:27: Wire `GOOGLE_CLIENT_ID` & `VITE_GOOGLE_CLIENT_ID` in Docker Compose and update docs
- **Who:** Anton Vertyporoh via Antigravity CLI
- **Area:** infra / docs
- **What was done:** Passed `VITE_GOOGLE_CLIENT_ID` build arg in `infra/frontend.Dockerfile` and `infra/docker-compose.yml`, passed `GOOGLE_CLIENT_ID` env var to `backend` in `infra/docker-compose.yml`, documented both variables in `infra/.env.example`, `README.md`, and `AGENTS.md` (§5, §6, §7, §8, §12).
- **Files touched:** `infra/frontend.Dockerfile`, `infra/docker-compose.yml`, `infra/.env.example`, `README.md`, `AGENTS.md`
- **Decisions & why:** none (consistent with existing `VITE_API_BASE_URL` build-arg pattern).
- **How to verify / run:** `docker compose --env-file infra/.env.example -f infra/docker-compose.yml config`
- **Not done / known problems / next steps:** Step 4 (live AWS EC2 deploy and HTTPS verification).

### 2026-11-18 11:29: Deploy Google Sign-In update to AWS EC2 (`https://16.170.212.120.sslip.io`)
- **Who:** Anton Vertyporoh via Antigravity CLI
- **Area:** infra / docs
- **What was done:** Connected via SSH to `ubuntu@16.170.212.120`, switched `/home/ubuntu/PidKlyuch` to `main` and fast-forwarded to `origin/main` (`221012c`), appended `infra/deploy_key.pub` to `~/.ssh/authorized_keys`, added `GOOGLE_CLIENT_ID` and `VITE_GOOGLE_CLIENT_ID` (`173388861976-tejqvtfmt2emurajvrim2i6huq75rnd5.apps.googleusercontent.com`) to `/home/ubuntu/PidKlyuch/infra/.env`, and rebuilt/restarted Compose containers (`docker compose --env-file .env up -d --build`). Verified all containers up/healthy and all HTTPS endpoints live.
- **Files touched:** `AGENTS.md` (§11, §12)
- **Decisions & why:** none
- **How to verify / run:** `curl -fsSL https://16.170.212.120.sslip.io/openapi.json | grep -o '"/api/auth/google"'` (`"/api/auth/google"`), `curl -s -o /dev/null -w "%{http_code}" https://16.170.212.120.sslip.io/api/docs` (`200`), `curl -s -o /dev/null -w "%{http_code}" https://16.170.212.120.sslip.io/` (`200`), `POST /api/auth/google` with invalid token (`401 {"detail":"Invalid Google token"}`), and live JS bundle contains `VITE_GOOGLE_CLIENT_ID`.
- **Not done / known problems / next steps:** None for Google Sign-In deploy; test interactively with a real Google account in browser (ensure `https://16.170.212.120.sslip.io` is in Authorized JavaScript origins in Google Cloud Console).

### 2026-11-18: Runbook §14.1 for finishing auto-deploy (for Anton's agent)
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** docs / infra
- **What was done:** Checked the state: PR #5 merged, `deploy` branch = `main` (`4c40c62`), the 4 secrets are set, and
  the first `CI/CD` run on `deploy` (run 44275118001) passed tests + build but failed at SSH with `Permission denied
  (publickey)`. The host-key pinning worked; only the deploy key is missing on the server. Added §14 "Runbooks" with
  14.1: an agent-executable checklist (C1–C8 with check commands, fixes, ASK/HUMAN stop points, troubleshooting,
  IP-change procedure, safety rules), plus §1.1 step 5 (agents surface open runbooks), and pointed the §11 item at it.
- **Files touched:** `AGENTS.md` (§1.1, §11, §12, new §14)
- **Decisions & why:** the instructions live in AGENTS.md (not a PDF or chat message) so Anton's agent finds and
  executes them itself, checking what is already done first.
- **How to verify / run:** ask any agent: "run runbook §14.1".
- **Not done / known problems / next steps:** none. Anton installed the deploy key in parallel (11:29), and the first
  automatic deploy (run 44276538099, commit `5b6c631`) succeeded. Verified live with runbook check C8: `/api/health`
  is OK, a bad car input gets a 422 about `engine_volume_cc` (new backend), an invalid token on `/api/calculate` gets
  401, `/api/auth/google` exists, and `/` returns 200. Runbook §14.1 marked DONE; it stays as the reference for an
  IP change or a broken deploy.

---

## 13. Domain notes: Ukrainian customs (VERIFIED & LOCKED 2026-11-17)

All numbers live in `backend/app/customs/tax_rates.json` (verified against `zakon.rada.gov.ua` Customs Code rev. 23.10.2026, Tax Code rev. 01.11.2026, and Laws № 5025-IX / № 5026-IX of 15.10.2026) and are documented with 10 worked test fixtures in [`docs/customs-rules.md`](docs/customs-rules.md).

**Parcels (Customs Code art. 374 p.7–8):**
- **Current rules:** Invoice value ≤ **€150.00** (goods only, shipping excluded) is tax-free. For `€150 < value ≤ €10,000`: **10%** duty + **20%** VAT on the **excess above €150** (`VAT = 20% × (excess + duty)`; €200 parcel → €5 duty + €11 VAT = **€16.00** ✔). Above €10,000 adds an approximate-calculation note.
- **July 2027 rules (Laws № 5025-IX & № 5026-IX, ≥ 01.07.2027):** Marketplace parcels ≤ €150 pay **20% VAT** on goods value (no duty); non-commercial private-to-private parcels ≤ **€45.00** stay tax-free (`sender = "private"`); parcels > €150 remain unchanged.

**Cars (Tax Code 215.3.5-1, DCFTA):**
- **Duty:** **10%** of `(car_price + shipping_to_border)` for `origin = "other"`; **0%** for `origin = "eu"` with EUR.1 / origin proof; **0%** for `electric`.
- **Excise:** `base × (cc / 1000) × K_age`, where `base` is `€50/€100` (`petrol` ≤3000 / >3000 cc) or `€75/€150` (`diesel` ≤3500 / >3500 cc), `hybrid` uses `petrol` rate, and `K_age = clamp(current_year − manufacture_year − 1, 1, 15)`. Electric (`8703 80`) = `€1/kWh`.
- **VAT:** **20%** on `(customs_value + duty + excise)` (EV VAT exemption expired 01.01.2026). Pension Fund levy, certification, and broker fees excluded.
- **Pitch check (€10,000 car):** EU new 0.8L petrol or 40 kWh EV → **€2,048.00**; 2013 non-EU 2.0L petrol ($K_{age}=12$) or 2.0L diesel ($K_{age}=8$) → **€4,640.00** ✔.

**Exchange rates (`backend/app/services/rates_service.py`):** NBU official daily JSON (`EUR`, `USD`, `UAH`, `GBP`, `PLN`), 1h in-memory cache with last-good / static fallback (`rate_source: "fallback"`).

---

## 14. Runbooks (step-by-step procedures for agents)

A runbook is written so that **any agent can execute it**: it checks the real state first, does the safe steps
itself, and stops to ask its human only where marked **ASK** (a decision) or **HUMAN** (something only a person can
do: a password, a console click, admin rights). Every step is idempotent: re-running a finished step changes nothing.

### 14.1 Finish GitHub Actions auto-deploy to EC2 — owner: Anton — status: DONE (18.11, deploy run 44276538099, `5b6c631`)

**Goal:** a push to the `deploy` branch automatically deploys to https://16.170.212.120.sslip.io (see §9 and
`.github/workflows/ci-cd.yml`). **Done when** the latest `CI/CD` run on `deploy` is green and the live API runs the
current `deploy` commit (check C8).

**How the agent must run it:** go through C1–C8 **in order**. For each check, run the command and report
`✅ done` / `❌ not done` to Anton. If not done, apply the fix (agent does it unless marked ASK/HUMAN), re-run the
check, and only then continue. Stop at the first step you cannot complete and tell Anton exactly what he must do.
Finish with a status table of C1–C8, then do "When finished" at the bottom.

**Facts** (verify, don't assume; update this table if something changed):

| Item | Value |
|---|---|
| Repo | `voskalo/PidKlyuch` (public), workflow `.github/workflows/ci-cd.yml` (name `CI/CD`) |
| Server | EC2 `i-00ab50698f9435a50`, `eu-north-1`, AWS account `334177992228`, public IP `16.170.212.120` |
| SSH (Anton's personal key) | `ssh -i ~/.ssh/pidklyuch-ec2.pem ubuntu@16.170.212.120` |
| App dir on server | `/home/ubuntu/PidKlyuch` (production secrets in `infra/.env`, git-ignored) |
| Deploy key (public half) | `infra/deploy_key.pub`, fingerprint **`SHA256:XA4izkTWYZ8tViCdnaUaE+zJfhWh8boH3YhEpeK9w3A`** |
| GitHub secrets (set 18.11) | `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `EC2_KNOWN_HOSTS` (+ optional `EC2_APP_DIR`, `DEPLOY_URL`) |

Shorthand used below: `SSH="ssh -i ~/.ssh/pidklyuch-ec2.pem -o ConnectTimeout=10 ubuntu@16.170.212.120"`.

**C1. Workflow is on `main`, `deploy` branch exists** — status 18.11: ✅
```bash
gh api repos/voskalo/PidKlyuch/contents/.github/workflows/ci-cd.yml?ref=main --jq .path
git ls-remote --heads https://github.com/voskalo/PidKlyuch.git deploy     # must print one line
```
Fix: the workflow missing → **HUMAN:** ask Liubomyr to merge PR #5. `deploy` missing → **ASK** Anton, then
`git push origin origin/main:refs/heads/deploy` (this starts a deploy run).

**C2. Secrets exist** — status 18.11: ✅ (set by Liubomyr)
```bash
gh secret list -R voskalo/PidKlyuch      # must list EC2_HOST, EC2_USER, EC2_SSH_KEY, EC2_KNOWN_HOSTS
```
A `403`/permission error only means Anton is not a repo admin, which is fine: skip and trust the C7 run log instead.
If a secret is really missing → **HUMAN:** Liubomyr re-creates it (see §7; the private deploy key exists only in
GitHub — if `EC2_SSH_KEY` is lost, generate a new pair with `ssh-keygen -t ed25519 -N "" -f /tmp/k`, `gh secret set
EC2_SSH_KEY < /tmp/k`, replace `infra/deploy_key.pub` with `/tmp/k.pub` in a PR, delete `/tmp/k*`, redo C5).

**C3. Server is reachable with Anton's key**
```bash
$SSH 'echo ok; hostname'
```
Fix: `Permission denied` → **HUMAN:** Anton must find `~/.ssh/pidklyuch-ec2.pem` (path may differ on his laptop).
Timeout → the instance is stopped or the IP changed:
`aws ec2 describe-instances --region eu-north-1 --instance-ids i-00ab50698f9435a50 --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' --output text`
(use Anton's AWS profile for account `334177992228`). If `stopped` → **ASK** Anton, then
`aws ec2 start-instances --region eu-north-1 --instance-ids i-00ab50698f9435a50`. If the IP is new → do the
"IP changed" procedure at the bottom, then continue.

**C4. Server repo is in a deployable state**
```bash
$SSH 'cd /home/ubuntu/PidKlyuch && ls -ld . .git && git status --short && git remote get-url origin \
  && test -f infra/.env && echo ENV_OK; (docker ps >/dev/null 2>&1 && echo DOCKER_OK) || (sudo -n true && echo SUDO_OK)'
```
Must show: no lines from `git status --short`, `ENV_OK`, and `DOCKER_OK` or `SUDO_OK`; the origin must be
`https://github.com/voskalo/PidKlyuch.git`. If `ls -ld` shows the repo is owned by `root`, git as `ubuntu` prints
"detected dubious ownership". That is fine (the workflow then uses `sudo`); run the git commands as `sudo git ...`.
Fixes:
- `cd: No such file` → find it: `$SSH "sudo find / -path '*/infra/docker-compose.yml' 2>/dev/null"`; **HUMAN:**
  Liubomyr runs `gh secret set EC2_APP_DIR --body <dir> -R voskalo/PidKlyuch`; use that dir below.
- `git status` shows modified files → show Anton `$SSH 'cd /home/ubuntu/PidKlyuch && git diff'`. If the same change
  is already on `main`, **ASK** Anton, then `git checkout -- <file>` on the server. Otherwise **ASK** Anton whether
  to commit the change to the repo via a PR (preferred) or `git stash` it. **Never** run `git reset --hard` or
  `git clean` on the server.
- No `ENV_OK` → **STOP, HUMAN:** production secrets are missing; Anton restores `infra/.env` (template:
  `infra/.env.example`, values from his notes). Never invent or print secret values.
- Neither `DOCKER_OK` nor `SUDO_OK` → **ASK** Anton, then `$SSH 'sudo usermod -aG docker ubuntu'` (requires sudo with
  a password: **HUMAN**).

**C5. Deploy key is installed on the server** — status 18.11: ✅ (installed by Anton 11:29)
```bash
$SSH 'grep -c "github-actions-deploy@PidKlyuch" ~/.ssh/authorized_keys'      # must print 1
```
Fix (agent may do it; it only appends one public key):
```bash
curl -fsS https://raw.githubusercontent.com/voskalo/PidKlyuch/main/infra/deploy_key.pub -o /tmp/deploy_key.pub
ssh-keygen -lf /tmp/deploy_key.pub      # MUST show SHA256:XA4izkTWYZ8tViCdnaUaE+zJfhWh8boH3YhEpeK9w3A — else STOP
$SSH 'cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' < /tmp/deploy_key.pub
$SSH 'grep -c "github-actions-deploy@PidKlyuch" ~/.ssh/authorized_keys'      # now 1 (if 2+, remove duplicates)
```
Always append (`>>` / `cat >>`); never overwrite `authorized_keys`, or Anton loses access to the server.

**C6. (Optional) Deploy key logs in and can run the deploy commands** — needs the private key, which agents do not
have; skip. C7 tests it for real.

**C7. Latest deploy run is green**
```bash
gh run list -R voskalo/PidKlyuch --workflow ci-cd.yml --branch deploy --limit 1 \
  --json databaseId,status,conclusion,headSha,url --jq '.[0]'
```
If the conclusion is not `success`: re-run it (agent may): `gh run rerun <databaseId> -R voskalo/PidKlyuch`, then wait:
`gh run watch <databaseId> -R voskalo/PidKlyuch --exit-status` (the first deploy builds images on a t3.micro: 5–10 min).
If it fails again: `gh run view <databaseId> -R voskalo/PidKlyuch --log-failed | tail -40` and use this table:

| Error in log | Cause → fix |
|---|---|
| `Missing repository secrets:` | → C2 |
| `Permission denied (publickey)` | key not on server / wrong user → C5 |
| `Host key verification failed` | server replaced or IP changed → "IP changed" procedure |
| `No git repo at ...` | → C4 (EC2_APP_DIR) |
| `infra/.env missing on server` | → C4 (STOP, HUMAN) |
| `would be overwritten` / `Not possible to fast-forward` | server has local edits → C4 |
| `sudo: a password is required` | → C4 (docker group) |
| `no space left on device` | **ASK**, then `$SSH 'sudo docker system prune -af'` (20 GB disk), re-run |
| `Site did not become healthy` | `$SSH 'cd /home/ubuntu/PidKlyuch && sudo docker compose --env-file infra/.env -f infra/docker-compose.yml logs --tail 100 backend caddy'`, report the errors to Anton |

**C8. Live site runs the new code**
```bash
curl -s https://16.170.212.120.sslip.io/api/health                     # {"status":"ok"}
curl -s -X POST https://16.170.212.120.sslip.io/api/calculate -H 'content-type: application/json' \
  -d '{"delivery_type":"car","car_price":10000,"engine_type":"petrol","engine_volume_cc":0,"manufacture_year":2014}'
$SSH 'cd /home/ubuntu/PidKlyuch && git rev-parse --short HEAD'; git ls-remote https://github.com/voskalo/PidKlyuch.git deploy
```
Done when the 422 error mentions `engine_volume_cc` (not `Input should be 'parcel'`, which is the old backend)
and the server commit equals the `deploy` branch head.

**"IP changed" procedure** (after an instance stop/start; recommended permanent fix: Elastic IP — **ASK** Anton:
`aws ec2 allocate-address --region eu-north-1` then `aws ec2 associate-address --region eu-north-1 --instance-id
i-00ab50698f9435a50 --allocation-id <eipalloc-id>`; release it after the course to stop charges):
1. **HUMAN (repo admin = Liubomyr):** `gh secret set EC2_HOST --body <new-ip> -R voskalo/PidKlyuch` and
   `ssh-keyscan <new-ip> | grep -v '^#' | gh secret set EC2_KNOWN_HOSTS -R voskalo/PidKlyuch`.
2. Agent (**ASK** first): on the server edit `infra/.env` → `DOMAIN=<new-ip>.sslip.io`,
   `CORS_ORIGINS=https://<new-ip>.sslip.io` (change only these two keys).
3. Agent: update the live URL in `README.md`, `AGENTS.md` §0, and this runbook's Facts table via a PR.
4. Re-run C3–C8.

**Rules for this runbook:** never print or paste secret values (`infra/.env`, private keys); never `git reset --hard`,
`git clean`, or force-push `deploy`; never overwrite `~/.ssh/authorized_keys`; never terminate or modify the EC2
instance beyond what a step says.

**When finished:** set this runbook's status to `DONE (date, commit)`, tick the §11 item, add a §12 change-log entry
(who, which checks were already done, what was fixed, final deploy commit and run URL), and tell Anton that from now
on releasing is `git push origin main:deploy`.

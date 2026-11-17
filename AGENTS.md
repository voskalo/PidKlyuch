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
| Repo URL | https://github.com/voskalo/PidKlyuch (`main` has `backend/` + `frontend/`; `anton/infra-and-docs` merges `main` + `infra/` + `docs/`) |

---

## 1. MANDATORY rules for AI agents

### 1.1 Before you start a task
1. Read this whole file.
2. Check §0 (current phase), §6 (repo structure), §8 (API contract), and the last ~10 entries of §12 (Change log).
3. Check §11 (Open issues / TODO) for anything related to your task.
4. Find out which team member you are working for. Their area of ownership is in §3. Do **not** rewrite another
   member's area without saying so explicitly in the log, because teammates use different agents and will not know.

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
| Auth method | **JWT bearer tokens** (PyJWT, HS256) | Passwords hashed with stdlib PBKDF2-SHA256 (`390,000` iterations) |
| Tests | **pytest** + FastAPI `TestClient` | `cd backend && .venv/bin/pytest` (66 tests passing on `main`) |
| Frontend framework | **React 19 / TypeScript / Vite 8 / Tailwind CSS v4** | `frontend/`, Lucide Icons, dev proxy `/api` → `127.0.0.1:8000`; built with Node 22 and served on `:80` behind Caddy in prod |
| Hosting (backend & frontend) | **AWS EC2 (Ubuntu 24.04)** + **Docker Compose + Caddy v2** (automatic HTTPS) | Single HTTPS origin via `<EC2-IP>.sslip.io` (Let's Encrypt TLS); `/api/*` → `backend:8000`, `/*` → `frontend:80` |
| Database (prod) | **PostgreSQL 16** (Docker Compose `db` or **AWS RDS for PostgreSQL**) | Set via `DATABASE_URL` (`?sslmode=require` if using RDS; never SQLite in prod) |
| Secrets | `.env` locally / AWS Secrets Manager or SSM on EC2 | `JWT_SECRET`, `POSTGRES_PASSWORD` never committed to git |
| Logs | Docker Compose stdout / **CloudWatch Logs** | Uvicorn + Python `logging` + Caddy access logs |
| Infra as code | `infra/` (Docker Compose, multi-stage Dockerfiles, Caddyfile) | Includes `--profile fallback` (`hello:80`) and full-stack setup |
| CI / Automation | `backend/scripts/check_law_updates.py` + `pytest` | Weekly law-watcher cron verifying `zakon.rada.gov.ua` fingerprints against `tax_rates.json` |

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
│   └── tests/                 # pytest (66 tests). Run: cd backend && .venv/bin/pytest
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
├── infra/                     # Docker, deployment configs, Caddy HTTPS proxy (owner: Anton)
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

### Frontend (`frontend/src/services/api.ts`, `infra/frontend.Dockerfile`)
- `VITE_API_BASE_URL`: frontend build-time env var, backend base URL (`https://api.pidklyuch.example.com` if hosted on a separate origin; leave empty `""` when behind Caddy on the same HTTPS origin because `api.ts` already prefixes `/api/...`). Optional locally (defaults to `""` with Vite `/api` proxy).

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
| ✅ | GET | `/api/auth/me` | required | current user |
| ✅ | POST | `/api/calculate` | optional | calculate landed price; saved to history if signed in |
| ✅ | POST | `/api/calculate/compare-rules` | – | parcel: current rules vs July 2027 rules |
| ✅ | GET | `/api/rates` | – | NBU rates used for conversion |
| ✅ | GET | `/api/history` | required | user's saved calculations, newest first |
| ✅ | DELETE | `/api/history/{id}` | required | delete one saved calculation |
| ✅ | GET | `/api/stats` | – | aggregate counters for the report |

**Sign-out** is client-side: delete the stored token (JWT is stateless).

**Notes for the frontend:**
- Store the `access_token` in `localStorage` (`pidklyuch_access_token`) and send it on every request. `/api/calculate` works without it too, but then `calculation_id` is `null`.
- On any `401`, clear the token and show sign-in.
- CORS allows `http://localhost:5173` (Vite) and `http://localhost:3000` by default.

**POST /api/auth/signup**: body `{"email": "a@b.com", "password": "min 8 chars", "name": "Anna"}` (`name` optional)
→ `201 {"access_token": "...", "token_type": "bearer", "user": {"id": 1, "email": "a@b.com", "name": "Anna", "created_at": "ISO"}}`. `409` if duplicate email.

**POST /api/auth/signin**: body `{"email", "password"}` → `200`, same shape as signup. `401` on wrong credentials.

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

**POST /api/calculate/compare-rules**: same parcel body (`rules` ignored) → `{"current": <result>, "july_2027": <result>}`.

**GET /api/rates** → `{"date": "2026-11-16", "source": "nbu" | "fallback", "uah_per_unit": {"UAH": "1", "EUR": "50.222", "USD": "45.4274", "GBP": "60.106", "PLN": "11.3916"}}`.

**GET /api/history** → `[{"id", "created_at", "delivery_type", "input": {...}, "result": {...}}]` (max 100, newest first).

**DELETE /api/history/{id}** → `204` (`404` if missing or not owner).

**GET /api/stats** → `{"users": 12, "calculations": 80, "calculations_by_signed_in": 40, "returning_users": 5}`.

---

## 9. Conventions

- **Git:** short-lived branches `name/feature` (e.g. `anna/calculator-ui`), merge to `main` via PR or after a quick
  review in chat. Do not force-push `main`.
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

---

## 11. Open issues / TODO

- [x] Choose the tech stack and fill in §5 (all — Backend FastAPI/SQLAlchemy, React 19 + TS + Vite + Tailwind v4, AWS EC2 + Docker Compose + Caddy v2 HTTPS).
- [x] Create `backend/`, `frontend/`, `infra/`, `docs/` (`backend/` merged in PR #1; `frontend/` merged in PR #2; `infra/` & `docs/` merged into `anton/infra-and-docs`).
- [x] Write the API contract in §8 and implement all backend endpoints (Liubomyr).
- [x] Verify customs rates in `tax_rates.json` and finalize `docs/customs-rules.md` with 10 test cases (Liubomyr + Anton).
- [x] Deploy fallback HTTPS stack on AWS EC2 (`i-0f47475721f5e04a5`, `13.60.162.78`, `https://13.60.162.78.sslip.io/healthz` verified `200 OK`); [ ] deploy full-stack (`backend` + `frontend` + `db` + `caddy`) on active AWS project `334177992228` (`eu-north-1`) over HTTPS.
- [x] Fill in "How to run" and "How to deploy" in `README.md` (Anton + Liubomyr + Anna).
- [x] Create user-testing script, Google Form questions, master tracker (`docs/user-testing-plan.md`), and Ukrainian recruiting templates (`docs/recruiting-messages.md`) (Anton).
- [ ] Merge `anton/infra-and-docs` (PR #3) into `main` once full-stack HTTPS deploy is verified.
- [ ] Schedule `cd backend && python scripts/check_law_updates.py` weekly and alert team on non-zero exit (Anton).
- [ ] Run Wednesday user-testing sessions (15+ external testers, collect quotes, UX fixes, and donation screenshots) and write `docs/report.pdf` (all, Wed 18 – Thu 19 Nov).

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

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
| Current phase | Day 2 (Tue 17 Nov 2026): Backend MVP implemented on `origin/liubomyr/backend` (66 pytest tests); AWS EC2 (`i-0f47475721f5e04a5`, `eu-north-1`) live over Let's Encrypt HTTPS (`fallback` profile); full-stack Compose infra, locked customs spec, and user testing prep on `anton/infra-and-docs`; `frontend/` pending from Anna |
| Tech stack | Python 3.12+ / FastAPI + SQLAlchemy (SQLite local, PostgreSQL prod) · React / Vite SPA · AWS EC2 + Docker Compose + Caddy v2 (see §5) |
| Live demo URL | https://13.60.162.78.sslip.io (verified `200 OK` on `/healthz` and `/`; currently serving fallback HTTPS test page on AWS EC2 `eu-north-1`) |
| Repo URL | https://github.com/voskalo/PidKlyuch (`origin/main` at docs baseline; `origin/liubomyr/backend` has backend PR #1; `anton/infra-and-docs` has infra & docs) |

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
| **Liubomyr Voskalo** | Backend: API, database, auth (sign-up/sign-in), calculation engine implementation, NBU rates, history | `backend/` |
| **Anna Kravchenko** | Frontend: all UI, calculator flow, breakdown view, auth pages, history page, donation button | `frontend/` |
| **Anton Vertyporoh** | Infra and deploy (HTTPS), customs-rules research and test cases, user testing coordination, final report | `infra/`, `docs/` |

The interfaces between members are the **API contract (§8)**, owned by Liubomyr and consumed by Anna, and the
**customs rules spec + test cases (§13 and `docs/customs-rules.md`)**, owned by Anton and implemented by Liubomyr.

---

## 4. Assignment requirements (graded)

Build a working prototype of the product, put it in front of real users, and report what happened.
Demo: **Thursday 19 November 2026**. **Every team member submits individually.**

Submit:
- Online text: link to the repository + URL of the running demo.
- File: the report (PDF).

| Criterion | Points | Status |
|---|---|---|
| Repo organised with top-level `backend/`, `frontend/`, `infra/` and a `README.md` that tells a stranger what the product is and how to run and deploy it | 3 | ⬜ |
| Working prototype with sign-in: deployed, reachable over **HTTPS**, users can **sign up and sign in** | 3 | 🟡 HTTPS live on AWS EC2 `https://13.60.162.78.sslip.io` (fallback page); awaiting `backend/` & `frontend/` merge |
| Report with user feedback: who you showed it to, how many tried it, what they said, **what you changed because of it** | 4 | ⬜ |
| **Bonus:** users ready to pay real money (donation to a volunteer cause, or a working payment in the product), with **evidence in the report** | bonus | ⬜ |

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

**Confirmed 2026-11-17** (synced from `origin/liubomyr/backend` + team hosting plan; frontend branch pending Anna's push).

| Layer | Choice | Notes |
|---|---|---|
| Backend language/framework | **Python 3.12+ / FastAPI** | `backend/`, entry point `app.main:app` (Uvicorn on `$PORT`, default `8000`, `--proxy-headers`) |
| ORM / Database | **SQLAlchemy 2.0**: SQLite locally, **PostgreSQL 16** in prod | Set via `DATABASE_URL` (Compose `postgres:16-alpine` or AWS RDS Postgres); tables auto-created on startup via `init_db()` |
| Auth method | **JWT Bearer tokens** (PyJWT, HS256) | Passwords hashed with stdlib PBKDF2-SHA256 (`390,000` iterations) |
| Tests | **pytest** + FastAPI `TestClient` | `cd backend && .venv/bin/pytest` (66 tests on `origin/liubomyr/backend`) |
| Frontend framework | **React / Vite SPA** (port `5173` dev; static build on port `80` behind Caddy in prod) | Consumes `/api/*` from §8; `CORS_ORIGINS` defaults include `http://localhost:5173,http://localhost:3000` |
| Hosting (backend & frontend) | **AWS EC2 (Ubuntu 24.04)** + **Docker Compose + Caddy v2** (automatic HTTPS) | Single HTTPS origin via `<EC2-IP>.sslip.io` or custom domain; optional AWS RDS for PostgreSQL |
| Secrets | `.env` locally / AWS Secrets Manager or SSM on EC2 | `JWT_SECRET`, DB credentials never in git |
| CI / Automation | `backend/scripts/check_law_updates.py` + `pytest` | Weekly law-watcher script checking `zakon.rada.gov.ua` fingerprints against `tax_rates.json` |

---

## 6. Repository structure

Current state (update on every structural change):

```
PidKlyuch/
├── docs/
│   ├── customs-rules.md       # Locked Ukrainian customs spec (parcels, cars, NBU rates, 10 test cases)
│   ├── recruiting-messages.md # Ukrainian outreach templates for Telegram/FB/DMs (15+ testers)
│   └── user-testing-plan.md   # Moderator script (2 tasks), Google Form questions, 15-tester tracker table
├── infra/
│   ├── hello-world/
│   │   └── index.html      # Fallback static status/landing page for HTTPS smoke test
│   ├── .env.example        # Full-stack Compose, DB, Caddy, and backend env var template
│   ├── .gitignore          # Ignores infra/.env and *.env.local
│   ├── Caddyfile           # Caddy v2 reverse proxy (/api/* -> backend, /* -> frontend/hello, /healthz)
│   ├── Dockerfile          # Lightweight caddy:2-alpine static server image for fallback hello-world
│   ├── backend.Dockerfile  # Production Python 3.12 FastAPI container with /api/health HEALTHCHECK
│   ├── frontend.Dockerfile # Multi-stage Node 20 Vite build + Caddy static SPA server
│   ├── docker-compose.yml  # Full-stack Compose (db, backend, frontend, caddy + fallback hello profile)
│   └── README.md           # Deployment architecture, full-stack & fallback modes, AWS EC2 HTTPS guide
├── AGENTS.md               # this file: shared AI context + work log (read first, update last)
├── CLAUDE.md               # pointer so Claude Code auto-loads AGENTS.md
└── README.md               # public description, team division of work, run & deploy instructions
```

Planned (required by grading):

```
PidKlyuch/
├── backend/       # API server, auth, calculation engine, DB access   (owner: Liubomyr)
├── frontend/      # web UI                                           (owner: Anna)
├── infra/         # Docker / compose / deploy configs, CI            (owner: Anton)
├── docs/          # customs-rules.md, user-testing notes, report     (owner: Anton)
├── AGENTS.md
└── README.md
```

---

## 7. Environment variables

Format: `NAME`: where it is used, example value (never a real secret), required or optional.

### Infra & Reverse Proxy (`infra/.env.example`, `infra/docker-compose.yml`)
- `DOMAIN`: `infra/docker-compose.yml` & `infra/Caddyfile` (site block host for automatic HTTPS), example `3-75-120-45.sslip.io` or `localhost`, optional (defaults to `localhost`).
- `ACME_EMAIL`: `infra/docker-compose.yml` & `infra/Caddyfile` (Let's Encrypt / ACME notification email), example `admin@example.com`, optional (defaults to `admin@example.com`).
- `POSTGRES_USER`: Postgres container (`db` service in `infra/docker-compose.yml`), example `pidklyuch`, optional locally.
- `POSTGRES_PASSWORD`: Postgres container (`db` service in `infra/docker-compose.yml`), example `change-me-strong-db-password`, **required in prod** when using local Compose Postgres.
- `POSTGRES_DB`: Postgres container (`db` service in `infra/docker-compose.yml`), example `pidklyuch`, optional.
- `VITE_API_URL`: frontend build arg in `infra/docker-compose.yml` & `infra/frontend.Dockerfile`, defaults to `/api` when served behind Caddy.

### Backend (`backend/.env.example`, `backend/app/core/config.py`)
- `DATABASE_URL`: backend, SQLAlchemy URL (`sqlite:///./pidklyuch.db` locally; `postgresql+psycopg://user:pass@host:5432/pidklyuch` or RDS URL with `?sslmode=require` in prod). Optional locally, **required in prod**.
- `JWT_SECRET`: backend, signs HS256 auth tokens. **Required in prod** (default `dev-insecure-secret-change-me` is insecure).
- `JWT_EXPIRE_MINUTES`: backend, token lifetime in minutes, default `10080` (7 days). Optional.
- `CORS_ORIGINS`: backend, comma-separated allowed origins, default `http://localhost:5173,http://localhost:3000`, e.g. `https://pidklyuch.example.com`. **Required in prod** if frontend is on a separate origin.
- `NBU_API_URL`: backend, NBU exchange-rate endpoint, default `https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json`. Optional.
- `PASSWORD_HASH_ITERATIONS`: backend, PBKDF2 iterations, default `390000` (lowered only in tests). Optional.
- `TAX_RATES_PATH`: backend, optional override path for `tax_rates.json` (default `app/customs/tax_rates.json`). Optional.

---

## 8. API contract (backend ↔ frontend)

Owner: Liubomyr (`origin/liubomyr/backend`). Base path: `/api`. JSON everywhere; interactive OpenAPI docs at `GET /docs` (Swagger). Auth uses `Authorization: Bearer <access_token>`. Monetary fields are serialized as 2-decimal strings (e.g. `"16.00"`). Full request/response schemas live on `origin/liubomyr/backend` (`backend/app/api/schemas_*.py` & `AGENTS.md` §8).

| Status | Method | Path | Auth | Purpose |
|---|---|---|---|---|
| ✅ | GET | `/api/health` | – | Liveness check for deploy & Docker healthcheck |
| ✅ | POST | `/api/auth/signup` | – | Create account (`email`, `password`, optional `name`) → `201` JWT + user |
| ✅ | POST | `/api/auth/signin` | – | Sign in → `200` JWT + user (`401` on invalid credentials) |
| ✅ | GET | `/api/auth/me` | required | Current authenticated user profile |
| ✅ | POST | `/api/calculate` | optional | Calculate parcel (`sender`: `marketplace`/`private`, `rules`: `current`/`july_2027`) or car (`origin`: `eu`/`other`, `engine_type`: `petrol`/`diesel`/`hybrid`/`electric`); saves to DB (`calculation_id` non-null when signed in) |
| ✅ | POST | `/api/calculate/compare-rules` | – | Parcel comparison: returns `{"current": <result>, "july_2027": <result>}` |
| ✅ | GET | `/api/rates` | – | Live/cached/fallback NBU UAH rates (`EUR`, `USD`, `GBP`, `PLN`, `UAH`) |
| ✅ | GET | `/api/history` | required | Signed-in user's saved calculations (max 100, newest first) |
| ✅ | DELETE | `/api/history/{id}` | required | Delete one saved calculation (`204`, `404` if not found/owner) |
| ✅ | GET | `/api/stats` | – | Aggregate usage counters (`users`, `calculations`, `calculations_by_signed_in`, `returning_users`) |

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
- 2026-11-16: Use Docker Compose + Caddy v2 for deployment and automatic HTTPS: Caddy provisions and renews Let's Encrypt TLS certificates automatically with minimal config, meeting the mandatory HTTPS grading requirement. (Anton + Antigravity CLI)
- 2026-11-17: Backend MVP implemented by Liubomyr on `origin/liubomyr/backend` using Python 3.12 / FastAPI + SQLAlchemy 2.0 + JWT (PBKDF2-SHA256) with all tax parameters centralized in `backend/app/customs/tax_rates.json` and monitored via `scripts/check_law_updates.py`. (Liubomyr via Claude Code; recorded on `anton/infra-and-docs` by Anton + Antigravity CLI)
- 2026-11-17: Host full-stack deployment on AWS EC2 (Ubuntu 24.04) using Docker Compose + Caddy v2 with `<EC2-IP>.sslip.io` for zero-DNS-purchase automatic Let's Encrypt HTTPS, routing `/api/*` to FastAPI (`backend:8000`) and `/*` to the React/Vite static frontend (`frontend:80`) on a single origin so CORS issues are minimized. (Anton + Antigravity CLI)

---

## 11. Open issues / TODO

- [x] Choose the tech stack and fill in §5 (all — Backend FastAPI/SQLAlchemy on `origin/liubomyr/backend`, React/Vite SPA, AWS EC2 + Docker/Caddy HTTPS).
- [ ] Create `backend/`, `frontend/`, `infra/` skeletons (`infra/` full-stack ready by Anton; `backend/` done on `origin/liubomyr/backend`; `frontend/` pending Anna).
- [x] Deploy fallback HTTPS stack on AWS EC2 (`i-0f47475721f5e04a5`, `13.60.162.78` in `eu-north-1`, Let's Encrypt verified on `https://13.60.162.78.sslip.io/healthz`); [ ] redeploy full stack once `backend/` & `frontend/` merge to `main`.
- [x] Write the API contract in §8 (Liubomyr on `origin/liubomyr/backend`; synced into `AGENTS.md` §8).
- [x] Write `docs/customs-rules.md` with verified rules, sources, and test cases (Anton — 2026-11-16; see `docs/customs-rules.md`).
- [x] Fill in "How to run" and "How to deploy" in `README.md` (Anton — 2026-11-17; local Docker/dev + AWS EC2 Ubuntu `sslip.io` HTTPS guide).
- [x] Create user-testing script, Google Form questions, and master tester tracker (`docs/user-testing-plan.md`, Anton — 2026-11-17).
- [x] Create Ukrainian tester recruiting templates (`docs/recruiting-messages.md`, Anton — 2026-11-17).
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
- **What was done:** Created `AGENTS.md` (this file) as the single shared context + log for all AI agents. Created
  `CLAUDE.md`, which only imports `AGENTS.md`. Rewrote `README.md` with the product description, assignment
  requirements, the division of work for the 3 members, a timeline up to the 19 Nov demo, and placeholder
  run/deploy sections.
- **Files touched:** `AGENTS.md` (created), `CLAUDE.md` (created), `README.md` (modified)
- **Decisions & why:** see §10, first entry.
- **How to verify / run:** n/a (docs only)
- **Not done / known problems / next steps:** tech stack not chosen; no code yet; see §11.

### 2026-11-16 13:33: Add infra directory skeleton and README
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra
- **What was done:** Verified current git branch `anton/infra-and-docs`. Created `infra/README.md` documenting the Docker Compose + Caddy v2 reverse-proxy architecture for automatic HTTPS, Day 1 hello-world layout vs. Day 2+ `/api/*` and `/*` routing, prerequisites, `DOMAIN`/`ACME_EMAIL` env vars, local run commands, and production deploy instructions. Updated `AGENTS.md` §0, §5, §6, and §10.
- **Files touched:** `infra/README.md` (created), `AGENTS.md` (modified)
- **Decisions & why:** Chosen Docker Compose + Caddy v2 for automatic HTTPS provisioning (see §10).
- **How to verify / run:** Read `infra/README.md`; compose stack will be added in Steps 2–3.
- **Not done / known problems / next steps:** Still need `infra/hello-world/index.html`, `infra/Dockerfile`, `infra/Caddyfile`, `infra/docker-compose.yml`, and `docs/customs-rules.md`.

### 2026-11-16 13:34: Add Dockerfile and hello-world page for HTTPS test
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra
- **What was done:** Created `infra/hello-world/index.html` (bilingual UA/EN PidKlyuch Day 1 HTTPS verification landing page) and `infra/Dockerfile` (`caddy:2-alpine` running `caddy file-server --listen :80 --root /usr/share/caddy`). Updated `AGENTS.md` §6.
- **Files touched:** `infra/hello-world/index.html` (created), `infra/Dockerfile` (created), `AGENTS.md` (modified)
- **Decisions & why:** Used `caddy:2-alpine` with explicit `caddy file-server` on port 80 so the container stays lightweight and shares the same base image family as the reverse proxy.
- **How to verify / run:** `docker build -t pidklyuch-hello ./infra` (full compose verification after Step 3).
- **Not done / known problems / next steps:** Still need `infra/Caddyfile`, `infra/docker-compose.yml`, and `docs/customs-rules.md`.

### 2026-11-16 13:37: Add Caddyfile and docker-compose for HTTPS deploy
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra
- **What was done:** Verified Caddy v2 Caddyfile & Docker Compose syntax via `context7` (`/websites/caddyserver_caddyfile`, `/caddyserver/caddy-docker`). Created `infra/Caddyfile` (global `email`, `{$DOMAIN:localhost}` site block, `encode zstd gzip`, `/healthz` responder, `reverse_proxy hello:80`, and Day 2+ commented placeholders for `/api/*` and `/*`) and `infra/docker-compose.yml` (`caddy:2-alpine` mapping ports 80/443/443udp with `caddy_data` & `caddy_config` volumes + `hello` service). Updated `AGENTS.md` §6, §7, and §11.
- **Files touched:** `infra/Caddyfile` (created), `infra/docker-compose.yml` (created), `AGENTS.md` (modified)
- **Decisions & why:** Used `{$DOMAIN:localhost}` and `{$ACME_EMAIL:admin@example.com}` Caddyfile env-var placeholders so the same compose stack works for local HTTPS smoke-testing and live VPS deployment without editing config files.
- **How to verify / run:** `DOMAIN=localhost docker compose -f infra/docker-compose.yml up --build` then visit `https://localhost` and `https://localhost/healthz`.
- **Not done / known problems / next steps:** Live VPS deployment still pending host selection; next step is writing `docs/customs-rules.md`.

### 2026-11-16 13:39: Initialize customs-rules.md with current parcel rules
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Created `docs/customs-rules.md` with precision/rounding rules (`Decimal`, `ROUND_HALF_UP` to 2 decimals), official Ukrainian legal/API sources (МКУ, ПКУ, customs.gov.ua, tax.gov.ua, NBU JSON API), and Section 1 covering current parcel import rules (€150 duty-free threshold, 10% duty + 20% VAT on excess, landed price formula, and €200 parcel check). Updated `AGENTS.md` §6.
- **Files touched:** `docs/customs-rules.md` (created), `AGENTS.md` (modified)
- **Decisions & why:** Standardized on `ROUND_HALF_UP` at each tax line item (`duty`, `excise`, `vat`) and EUR as threshold base with NBU UAH conversion so backend unit tests and frontend breakdowns match exactly.
- **How to verify / run:** Review `docs/customs-rules.md` §1; €200 parcel yields €5.00 duty + €11.00 VAT = €16.00 total tax.
- **Not done / known problems / next steps:** Add July 2027 parcel rules, NBU rate conversion/fallback specs, car tax formulas, and 10 worked test cases to `docs/customs-rules.md`.

### 2026-11-16 13:40: Add July 2027 parcel rules and NBU rate specs
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Appended Section 2 (upcoming July 2027 parcel rules removing the €150 VAT threshold, formulas for `<= €150` and `> €150`, and `TODO` legal-verification markers for shipping-in-VAT-base and duty/C2C edge cases) and Section 3 (NBU daily exchange rate API spec, `CC -> UAH -> EUR` conversion formulas, and 3-tier caching/fallback strategy with `rate_source` flags) to `docs/customs-rules.md`. Updated `AGENTS.md` §12.
- **Files touched:** `docs/customs-rules.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Defined a 3-tier NBU rate fallback (`nbu_live`/`nbu_cached` -> `nbu_stale_cache` -> static `fallback` constants) and defaulted July 2027 VAT base to `V_EUR + Duty_2027` (with explicit legal-verification TODO) so "Today vs. July 2027" comparisons stay deterministic and transparent.
- **How to verify / run:** Review `docs/customs-rules.md` §2–§3; verify €200 parcel gives €16.00 today vs. €46.00 under July 2027 rules.
- **Not done / known problems / next steps:** Add Section 4 (car import tax formulas) and Section 5 (10 worked test cases) to `docs/customs-rules.md`.

### 2026-11-16 13:41: Add car import tax formulas to customs-rules.md
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Appended Section 4 (Passenger Car Import Tax Formulas under ПКУ Art. 215.3.5-1 & МКУ) to `docs/customs-rules.md`, specifying customs duty (10% ICE, 0% EV), excise formulas (`R_base * (cm3/1000) * K_age` with `[1, 15]` age clamping and `€1/kWh` for EVs), 20% VAT (noting 2026 expiry of EV VAT exemption), and pitch benchmark checks (`€2,048` EV to `€4,640` diesel on a `€10,000` vehicle). Updated `AGENTS.md` §12.
- **Files touched:** `docs/customs-rules.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Specified `K_age = min(15, max(1, current_year - production_year - 1))` (with optional explicit `age_years` override) and baseline 10% ICE duty + 2026 20% EV VAT so backend calculations align with both current Ukrainian law and the pitch's `€2,048–€4,640` range.
- **How to verify / run:** Review `docs/customs-rules.md` §4 and check §4.6 calculations against €2,048 and €4,640 bounds.
- **Not done / known problems / next steps:** Add Section 5 (10 worked test cases) to `docs/customs-rules.md` and update `AGENTS.md` §11 & §13.

### 2026-11-16 13:42: Add 10 worked customs calculation test cases
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Appended Section 5 to `docs/customs-rules.md` with 10 deterministic worked test cases (`TC-P1`–`TC-P5` covering parcels under both current & July 2027 rules including USD→EUR conversion, and `TC-C1`–`TC-C5` covering electric, petrol, and diesel cars across displacement thresholds and the 15-year age cap) formatted as both summary tables and a JSON fixture block for backend unit tests. Updated `AGENTS.md` §11 (marked `docs/customs-rules.md` task done) and §13 (verified domain summary).
- **Files touched:** `docs/customs-rules.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Provided fixed test NBU rates (`EUR=45.00 UAH`, `USD=41.40 UAH`) and explicit `current_year=2026` in the JSON test fixture so Liubomyr's backend unit tests are 100% deterministic offline.
- **How to verify / run:** Check all 10 cases in `docs/customs-rules.md` §5 against formulas in §1–§4 (note `TC-C1` = `€2,048` and `TC-C3` = `€4,640` match pitch bounds exactly).
- **Not done / known problems / next steps:** Wait for team tech stack decision (§5) and Liubomyr's API contract (§8), then deploy live VPS over HTTPS and update `README.md` run/deploy sections.

### 2026-11-17 11:12: Sync with main and document team tech stack
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** repo / docs
- **What was done:** Ran `git fetch origin && git merge origin/main` (already up to date with `982757b`). Inspected `origin/liubomyr/backend` (`0b4851d`) read-only without merging `backend/` into `anton/infra-and-docs` (`backend/Dockerfile`, `backend/.env.example`, `backend/app/core/config.py`, `backend/app/customs/{tax_rates.json,rules.py,calculators.py}`, `backend/tests/test_customs.py`, `AGENTS.md`). Verified no `frontend/` branch exists on `origin` yet. Populated `AGENTS.md` §0, §5, §7, §8, §10, and §11 with the confirmed Python 3.12 / FastAPI + SQLAlchemy + JWT backend stack, React/Vite frontend expectation, AWS EC2 + Docker Compose + Caddy v2 (`sslip.io`) HTTPS hosting plan, environment variables, and §8 API endpoint summary.
- **Files touched:** `AGENTS.md` (modified)
- **Decisions & why:** Documented AWS EC2 + Docker Compose + Caddy v2 (`sslip.io` automatic HTTPS) in §10 and aligned §5/§7/§8 with `origin/liubomyr/backend` without touching `backend/` or `frontend/`.
- **How to verify / run:** `git fetch origin && git merge origin/main` and inspect `AGENTS.md` §5, §7, §8.
- **Not done / known problems / next steps:** Next step (Step 2) is resolving the remaining legal TODOs in `docs/customs-rules.md` against verified Laws № 5025-IX / № 5026-IX and `backend/app/customs/tax_rates.json`.

### 2026-11-17 11:15: Finalize customs-rules.md and resolve legal TODOs
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Resolved all `TODO (Legal Verification)` placeholders in `docs/customs-rules.md` against enacted Laws № 5025-IX / № 5026-IX (15.10.2026), Law № 2697-IX (DCFTA), Law № 4695-IX, and `backend/app/customs/tax_rates.json`. Locked July 2027 parcel rules (20% VAT on `V_EUR` excluding shipping for `<= €150`, €45 P2P private gift exemption, `> €150` unchanged), car rules (DCFTA 0% EU origin duty with EUR.1, hybrid excise at petrol ICE rate, EV 20% VAT since 01.01.2026, Pension Fund/broker exclusions), and updated all 10 worked test cases (`TC-P1`..`TC-P5`, `TC-C1`..`TC-C5`) + §13 domain summary in `AGENTS.md`.
- **Files touched:** `docs/customs-rules.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Aligned `docs/customs-rules.md` 1:1 with `backend/app/customs/calculators.py` & `tax_rates.json` so Liubomyr's backend tests and Anton's documentation cannot diverge.
- **How to verify / run:** Inspect `docs/customs-rules.md` §2, §4, §5 and cross-check with `backend/app/customs/tax_rates.json` on `origin/liubomyr/backend`.
- **Not done / known problems / next steps:** Next step (Step 3) is upgrading `infra/` to full-stack Docker Compose + Caddy reverse proxy.

### 2026-11-17 11:18: Configure full-stack Docker Compose and Caddy reverse proxy
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra
- **What was done:** Upgraded `infra/` for full-stack production deployment while preserving `hello-world` under `--profile fallback`. Created `infra/backend.Dockerfile` (Python 3.12-slim + `/api/health` Docker `HEALTHCHECK`), `infra/frontend.Dockerfile` (Node 20 Vite multi-stage build + Caddy SPA server with `try_files {path} /index.html`), `infra/.env.example`, and `infra/.gitignore`. Updated `infra/Caddyfile` (`/healthz` → 200 OK, `/api/*` & `/docs*` & `/openapi.json` → `backend:8000`, `/*` → `frontend:80` with `hello:80` failover via `lb_policy first`), `infra/docker-compose.yml` (added `db` `postgres:16-alpine` with `pg_isready`, `backend`, `frontend`, `caddy`, and `hello` under `profiles: ["fallback"]`), and `infra/README.md`. Updated `AGENTS.md` §6, §7, §11, and §12.
- **Files touched:** `infra/backend.Dockerfile` (created), `infra/frontend.Dockerfile` (created), `infra/.env.example` (created), `infra/.gitignore` (created), `infra/Caddyfile` (modified), `infra/docker-compose.yml` (modified), `infra/README.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Kept `hello` under `profiles: ["fallback"]` and avoided hard `depends_on` from `caddy` to `backend`/`frontend` so `caddy + hello` can run independently before `backend/` & `frontend/` merge, while full-stack mode runs `db`, `backend`, `frontend`, and `caddy` cleanly on one HTTPS origin.
- **How to verify / run:** `cp infra/.env.example infra/.env && docker compose --env-file infra/.env -f infra/docker-compose.yml config` (or `--profile fallback` for `caddy hello`).
- **Not done / known problems / next steps:** Next step (Step 4) is writing "How to run" and "How to deploy" in root `README.md`.

### 2026-11-17 11:21: Add How to run and How to deploy guides to README.md
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs / repo
- **What was done:** Replaced the placeholder "How to run locally" and "How to deploy" sections in root `README.md` with copy-pasteable guides: (1) Full-stack Docker Compose + `--profile fallback` command, (2) individual local dev commands for `backend/` (Python 3.12+ venv, `uvicorn`, `pytest`, `check_law_updates.py`) and `frontend/` (`npm install && npm run dev`), and (3) a 5-step AWS EC2 Ubuntu 24.04 deployment guide covering Security Group ports (`22`, `80`, `443/tcp`, `443/udp`), Docker installation, `infra/.env` configuration with `<EC2-IP>.sslip.io` automatic HTTPS (plus optional AWS RDS `?sslmode=require`), verification endpoints, and weekly law-watcher cron setup. Updated `AGENTS.md` §11 and §12.
- **Files touched:** `README.md` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Recommended `<EC2-IP>.sslip.io` + Caddy v2 in `README.md` so the team gets zero-cost valid Let's Encrypt HTTPS certificates immediately on any EC2 public IP without buying a domain.
- **How to verify / run:** Review `README.md` "How to run" and "How to deploy" sections.
- **Not done / known problems / next steps:** Next step (Step 5) is creating `docs/user-testing-plan.md`.

### 2026-11-17 11:25: Add user testing script, feedback form, and tracker template
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Created `docs/user-testing-plan.md` with: (1) a 10-minute Ukrainian moderator testing script covering 2 realistic tasks (Task 1: `$220 + $18` Amazon parcel with sign-up, EUR/UAH breakdown, formula check, and July 2027 comparison; Task 2: `€10,000` 2018 2.0L diesel / `€12,000` 60 kWh EV import + calculation history + volunteer donation flow), (2) 8 copy-pasteable Google Form feedback questions in Ukrainian, and (3) a 15-row master tester tracking table (`T-01`..`T-15`, 5 per team member) with columns for channel, profile, key quote, bug/UX issue, fix taken, and donation screenshot proof. Updated `AGENTS.md` §6, §11, and §12.
- **Files touched:** `docs/user-testing-plan.md` (created), `AGENTS.md` (modified)
- **Decisions & why:** Structured the script and Google Form around concrete grading evidence (task completion, verbatim quotes, Wednesday UX changes, and donation screenshots) to feed directly into `docs/report.pdf`.
- **How to verify / run:** Review `docs/user-testing-plan.md` and copy questions from §3 into the team's Google Form.
- **Not done / known problems / next steps:** Next step (Step 6) is creating `docs/recruiting-messages.md`.

### 2026-11-17 11:28: Add Ukrainian tester recruiting message templates
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** docs
- **What was done:** Created `docs/recruiting-messages.md` with 4 ready-to-send Ukrainian recruiting templates (international online shopping TG/FB groups, car-import TG/FB communities, student/IT chats, and direct personal DMs + follow-up with donation screenshot prompt) plus a 3-member outreach quota checklist targeting 15+ external testers for Wednesday 18 Nov. Updated `AGENTS.md` §6, §11, and §12 (and confirmed §13 verified customs summary is locked).
- **Files touched:** `docs/recruiting-messages.md` (created), `AGENTS.md` (modified)
- **Decisions & why:** Tailored hooks separately for parcel shoppers (€150 threshold + July 2027 VAT shift) and car buyers (age coefficient, 2026 EV VAT, EUR.1) to maximize external non-friend conversion before Wednesday testing.
- **How to verify / run:** Review `docs/recruiting-messages.md`, fill in `<HTTPS_DEMO_URL>` and `<GOOGLE_FORM_URL>` once deployed, and send across target communities.
- **Not done / known problems / next steps:** Awaiting `backend/` (`origin/liubomyr/backend`) and `frontend/` merge to `main`, live AWS EC2 HTTPS deployment via `infra/docker-compose.yml`, Wednesday testing execution, and `docs/report.pdf`.

### 2026-11-17 12:18: Deploy fallback HTTPS stack on AWS EC2 and record live URL
- **Who:** Anton Vertyporokh via Antigravity CLI
- **Area:** infra / docs
- **What was done:** Provisioned a Free Tier Ubuntu 24.04 `t3.micro` EC2 instance (`i-0f47475721f5e04a5`, public IP `13.60.162.78`) in AWS project `591554481308` (`eu-north-1`, profile `pidklyuch`) with Security Group `sg-00ef1a31821b16763` (TCP `22`, `80`, `443` + UDP `443` from `0.0.0.0/0`), SSH key pair `~/.ssh/pidklyuch-ec2.pem` (`chmod 400`), IMDSv2 enforced (`HttpPutResponseHopLimit=2`), encrypted 20 GB `gp3` EBS volume, and user-data bootstrap (Docker + `git clone` + `docker compose --profile fallback`). Fixed a Caddy v2 directive-order bug discovered during live smoke testing: moved `respond /healthz "OK" 200` inside `handle /healthz { ... }` in `infra/Caddyfile` so `/healthz` executes before `reverse_proxy`, and added `frontend` network alias to `hello` in `infra/docker-compose.yml` for `--profile fallback`. Synced both files to EC2 and verified `https://13.60.162.78.sslip.io/healthz` (`HTTP/2 200` `OK`) and `https://13.60.162.78.sslip.io/` (`HTTP/2 200`). Updated `AGENTS.md` §0, §4, §11, and §12.
- **Files touched:** `infra/Caddyfile` (modified), `infra/docker-compose.yml` (modified), `AGENTS.md` (modified)
- **Decisions & why:** Wrapped `/healthz` in `handle /healthz` in `infra/Caddyfile` because Caddy v2 executes `reverse_proxy` before bare `respond` directives by default; added `frontend` network alias to `hello` in `--profile fallback` so Caddy proxies immediately without waiting on `frontend` fail-over timeout.
- **How to verify / run:** `curl -i https://13.60.162.78.sslip.io/healthz` (returns `HTTP/2 200` `OK`) and `curl -I https://13.60.162.78.sslip.io/` (returns `HTTP/2 200`).
- **Not done / known problems / next steps:** Full-stack redeploy on `13.60.162.78` once `backend/` and `frontend/` merge to `main` (and attach an Elastic IP if needed to preserve the public IP across instance stops, or clean up resources after demo).

---

## 13. Domain notes: Ukrainian customs (Verified & Locked 2026-11-17)

> Verified against МКУ (Art. 234, 374 p.7–8), ПКУ (Art. 14.1.49-1, 196.1.17, 215.3.5-1), Laws № 5025-IX / № 5026-IX (15.10.2026), Law № 2697-IX (DCFTA), Law № 4695-IX, and `backend/app/customs/tax_rates.json`. Full specification, resolved edge cases, and 10 worked test cases live in [`docs/customs-rules.md`](docs/customs-rules.md).

**Parcels (current rules — МКУ Art. 374 p.7–8):**
- Duty-free threshold: **€150.00** per parcel (invoice value of goods $V_{\text{EUR}}$; itemized shipping excluded from threshold base, included in total landed cost). Above €10,000 requires full commercial declaration (calculator notes approximate estimate).
- Above €150 on the **excess**: **10%** duty, then **20%** VAT on $(\text{Excess} + \text{Duty})$ (`€200` parcel → `€5.00` duty + `€11.00` VAT = **€16.00** tax).
- **July 2027 change (Laws № 5025-IX / № 5026-IX, ≥ 01.07.2027):** Marketplace/commercial parcels $\le €150$ pay **20% VAT** on $V_{\text{EUR}}$ (excluding shipping) and **0% duty**; private P2P parcels $\le €45$ remain tax-free (`sender = "private"`); parcels $> €150$ remain unchanged (`€200` → **€16.00** tax). All legal TODOs resolved.

**Cars (ПКУ Art. 215.3.5-1, DCFTA):**
- **Duty:** 10% of $(V_{\text{car}} + S_{\text{border}})$ for `origin="other"`; 0% for documented EU origin (`origin="eu"` with EUR.1); 0% for `electric` regardless of origin.
- **Excise:** ICE & `hybrid` (at petrol rate) = $R_{\text{base}} \times (E_{\text{cm3}} / 1000) \times K_{\text{age}}$, where $R_{\text{base}}$ is `€50`/`€100` (`petrol` $\le 3000$ / $>3000\text{ cm}^3$) or `€75`/`€150` (`diesel` $\le 3500$ / $>3500\text{ cm}^3$), and $K_{\text{age}} = \min(15, \max(1, Y_{\text{curr}} - Y_{\text{prod}} - 1))$. EV = `€1.00 × battery_kWh`.
- **VAT:** 20% on $(V_{\text{EUR}} + \text{Duty} + \text{Excise})$ (EV 0% VAT exemption expired 01.01.2026). Pension Fund first-registration levy, certification, and broker fees excluded.
- **Pitch check (€10,000 car):** 40 kWh EV (or EU 0.8L new petrol) → **€2,048.00** tax; 2.0L diesel ($K_{\text{age}}=8$) / 2013 2.0L petrol ($K_{\text{age}}=12$) → **€4,640.00** tax ✔

**Exchange rates:** NBU official daily JSON API (`https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json`). In-memory cache (1h TTL) + last-good cache + static `fallback` constants (`rate_source: "fallback"`).

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
| Current phase | Day 2: **backend MVP merged into `main`** (PR #1, 17.11; all §8 endpoints ✅, customs rates verified 16.11, 66 tests, not deployed yet); frontend and infra not started |
| Tech stack | Backend: Python/FastAPI + SQLAlchemy. **Hosting: AWS (all parts).** Frontend: TBD (see §5) |
| Live demo URL | TBD (must be HTTPS) |
| Repo URL | https://github.com/voskalo/PidKlyuch (`main` contains the backend since PR #1) |

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
| **Anton Vertyporoh** | Infra and deploy on **AWS** (HTTPS), scheduled law-watcher run, user testing coordination, final report | `infra/`, `docs/` |

The main interface between members is the **API contract (§8)**, owned by Liubomyr and consumed by Anna.
Customs rules research was moved from Anton to Liubomyr on 16.11.2026. The rules now live in
`backend/app/customs/tax_rates.json`, summarized with sources in §13.

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
| Working prototype with sign-in: deployed, reachable over **HTTPS**, users can **sign up and sign in** | 3 | 🟡 backend auth done, not deployed yet; no UI |
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

Backend chosen 2026-11-16 (Liubomyr). **Everything is hosted on AWS using AWS services** (team decision, 16.11). The specific AWS services are still to be chosen by Anton. Frontend framework is still open.

| Layer | Choice | Notes |
|---|---|---|
| Backend language/framework | **Python 3.12+ / FastAPI** | `backend/`, entry point `app.main:app` (uvicorn) |
| ORM / Database | **SQLAlchemy 2.0**: SQLite locally, **Postgres** in prod | set via `DATABASE_URL`; tables are auto-created on startup (no migrations yet) |
| Auth method | **JWT bearer tokens** (PyJWT, HS256) | passwords hashed with PBKDF2-SHA256 (stdlib) |
| Tests | **pytest** + FastAPI `TestClient` | `cd backend && .venv/bin/pytest` |
| Frontend framework | TBD (Anna) | consumes §8 |
| Hosting (backend) | **AWS**: service TBD (Anton). Options: App Runner, ECS Fargate + ALB, Elastic Beanstalk (Docker) | runs `backend/Dockerfile`; health check `GET /api/health`; HTTPS required (ACM certificate or the service's built-in HTTPS) |
| Database (prod) | **AWS RDS for PostgreSQL** | `DATABASE_URL=postgresql://user:pass@<rds-endpoint>:5432/pidklyuch?sslmode=require` |
| Hosting (frontend) | **AWS**: service TBD (Anton/Anna). Options: S3 + CloudFront, or Amplify Hosting | HTTPS via CloudFront/ACM |
| Secrets | **AWS Secrets Manager or SSM Parameter Store** → env vars | `JWT_SECRET`, DB password: never in git |
| Logs | **CloudWatch Logs** | the backend logs to stdout (uvicorn + `logging`) |
| Infra as code | TBD in `infra/` (CloudFormation / CDK / Terraform, or documented console steps) | graded: `infra/` must exist |
| CI | TBD (e.g. GitHub Actions → ECR) | |

**AWS implications for the backend (already handled or to keep in mind):**
- **Do not use SQLite on AWS.** Container filesystems are ephemeral, so the data would be lost on every redeploy.
  `DATABASE_URL` must point to RDS.
- The container listens on `$PORT` (default 8000), and uvicorn runs with `--proxy-headers`, so it works behind
  ALB/App Runner/CloudFront.
- RDS: allow inbound 5432 only from the backend's security group/VPC connector. Add `?sslmode=require` to the URL.
- Outbound internet access is required (NBU API `bank.gov.ua`). If the backend runs in private subnets, it needs a
  NAT gateway / VPC egress. Without it, the app still works but uses the fallback rates (`rate_source: "fallback"`).
- `CORS_ORIGINS` = the frontend's HTTPS URL (CloudFront/Amplify domain). Alternative: route `/api/*` through the same
  CloudFront distribution to the backend, so the frontend and API share one origin and CORS is not needed.
- The NBU rate cache is in memory per instance. That's fine with several instances (each one fetches on its own).
- Tables are auto-created on startup (`init_db()`), so the first deploy against an empty RDS database needs no
  manual SQL.

---

## 6. Repository structure

Current state (update on every structural change):

```
PidKlyuch/
├── AGENTS.md      # this file: shared AI context + work log (read first, update last)
├── CLAUDE.md      # pointer so Claude Code auto-loads AGENTS.md
├── README.md      # public description, team division of work, run & deploy instructions
└── backend/                     # FastAPI service (owner: Liubomyr)
    ├── requirements.txt         # runtime deps (pinned)
    ├── requirements-dev.txt     # + pytest
    ├── .env.example             # documented env vars (copy to .env)
    ├── Dockerfile               # python:3.12-slim, runs uvicorn on $PORT (default 8000); build context = backend/
    ├── scripts/check_law_updates.py  # law watcher: fetches source articles from zakon.rada.gov.ua, compares clause
    │                                 #   fingerprints with tax_rates.json; exit 0 ok / 1 changed / 2 can't check
    ├── app/
    │   ├── main.py              # create_app(): CORS, routers, DB init on startup
    │   ├── core/config.py       # Settings (pydantic-settings, reads env/.env)
    │   ├── core/database.py     # engine, SessionLocal, Base, get_db(), init_db(), normalize_db_url()
    │   ├── api/health.py        # GET /api/health
    │   ├── api/auth.py          # /api/auth/signup|signin|me
    │   ├── api/schemas_auth.py  # pydantic request/response models for auth
    │   ├── api/deps.py          # get_current_user / get_optional_user (Bearer JWT)
    │   ├── core/security.py     # PBKDF2 password hashing, JWT encode/decode
    │   ├── api/calculate.py     # POST /api/calculate, POST /api/calculate/compare-rules, GET /api/rates
    │   ├── api/schemas_calc.py  # ParcelIn/CarIn (discriminated by delivery_type), CalculationOut, RatesOut
    │   ├── api/history.py       # GET /api/history, DELETE /api/history/{id}, GET /api/stats
    │   ├── models/              # SQLAlchemy ORM models: user.py (User), calculation.py (Calculation: input/result JSON)
    │   ├── services/            # business services (use cases)
    │   │   ├── auth_service.py        # AuthService: register/authenticate
    │   │   ├── rates_service.py       # RatesService: NBU fetch, 1h cache, fallback; RateTable.to_eur()
    │   │   ├── calculation_service.py # CalculationService: request → EUR → calculator → response with UAH
    │   │   └── history_service.py     # HistoryService: record / list_for / delete_for / stats
    │   └── customs/             # customs calculation engine (pure Python, no DB/HTTP), all amounts in EUR
    │       ├── tax_rates.json   # ★ ALL tax numbers (thresholds, rates, excise table) + legal sources + fingerprints
    │       │                    #   → THE ONLY place to change taxes. No numbers in code.
    │       ├── rules.py         # loads + validates tax_rates.json (or $TAX_RATES_PATH) into ParcelRules/CarRules;
    │       │                    #   exports TAX_RATES, PARCEL_RULES, PARCEL_CURRENT, PARCEL_JULY_2027, CAR_CURRENT
    │       ├── models.py        # ParcelInput, CarInput, TaxLine, Breakdown (totals), money() rounding, enums
    │       └── calculators.py   # CustomsCalculator (ABC) → ParcelCalculator, CarCalculator (Strategy pattern)
    └── tests/                   # pytest (66 tests). Run: cd backend && .venv/bin/pytest
        ├── conftest.py          # sets test env (SQLite test.db, fast hashing), `client` fixture with fresh tables,
        │                        #   overrides get_rates_service with FAKE_NBU (1 EUR = 50 UAH, 1 USD = 40 UAH)
        ├── test_health.py       # /api/health
        ├── test_auth.py         # hashing, signup/signin/me, duplicates, validation, bad tokens
        ├── test_customs.py      # pure engine: hand-calculated cases from the verified law (parcels, 2027, cars, EV)
        ├── test_tax_rates_file.py # rates file loads, cites sources, TAX_RATES_PATH override, broken file fails
        ├── test_law_watcher.py  # watcher offline: normalize/extract/fingerprint, changed → 1, missing/offline → 2
        ├── test_rates.py        # NBU parsing, conversion, fallback, cache-on-failure, /api/rates
        ├── test_calculate_api.py# /api/calculate (parcel, car, USD conversion, 422s), compare-rules
        └── test_history.py      # history save/list/delete/privacy, /api/stats, normalize_db_url
```

**Backend architecture (layers; each one only calls the layer below it):**
`api/` (HTTP: routing, pydantic validation, auth dependencies) → `services/` (use cases: AuthService,
CalculationService, RatesService, HistoryService) → `customs/` (pure domain logic, no I/O) and `models/` (ORM).
Adding a new delivery type = a new `*Rules` dataclass in `rules.py`, a new `CustomsCalculator` subclass, a new `*In`
schema added to the `CalculationIn` union, and a branch in `CalculationService._breakdown()`.

Planned (required by grading):

```
PidKlyuch/
├── backend/       # API server, auth, calculation engine, DB access   (owner: Liubomyr)
├── frontend/      # web UI                                           (owner: Anna)
├── infra/         # Docker / compose / deploy configs, CI            (owner: Anton)
├── docs/          # user-testing notes, report                       (owner: Anton)
├── AGENTS.md
└── README.md
```

---

## 7. Environment variables

Format: `NAME`: where it is used, example value (never a real secret), required or optional.
Backend vars are documented in `backend/.env.example`, read by `backend/app/core/config.py`.

- `DATABASE_URL`: backend. `sqlite:///./pidklyuch.db` (default) or `postgresql+psycopg://user:pass@host:5432/db`. Optional locally, **required in prod**.
- `JWT_SECRET`: backend, signs auth tokens. **Required in prod** (the default is insecure).
- `JWT_EXPIRE_MINUTES`: backend, token lifetime, default `10080` (7 days). Optional.
- `CORS_ORIGINS`: backend, comma-separated frontend origins, e.g. `https://pidklyuch.example.com`. **Required in prod.**
- `NBU_API_URL`: backend, NBU exchange-rate endpoint. Optional (has a default).
- `PASSWORD_HASH_ITERATIONS`: backend, PBKDF2 iterations, default `390000`. Only lowered in tests.
- `TAX_RATES_PATH`: backend, alternative rates file (default `app/customs/tax_rates.json`), e.g. one synced from S3. Optional.

---

## 8. API contract (backend ↔ frontend)

Owner: Liubomyr. Base path: `/api`. JSON everywhere. Interactive docs: `GET /docs` (Swagger) on the running backend.
Auth: send `Authorization: Bearer <access_token>` (the token comes from sign-up/sign-in). Errors use the FastAPI
format: `{"detail": "..."}` (422 validation errors put a list in `detail`).
Money in responses is a **string with 2 decimals** (e.g. `"16.00"`), so no float rounding happens in JS.

| Status | Method | Path | Auth | Purpose |
|---|---|---|---|---|
| ✅ | GET | `/api/health` | – | liveness check for deploy |
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

**Notes for the frontend (Anna):**
- Store the `access_token` (e.g. in `localStorage`) and send it on every request. `/api/calculate` works without
  it too, but then nothing is saved to history.
- On any `401`, clear the token and show sign-in.
- CORS allows `http://localhost:5173` (Vite) and `http://localhost:3000` by default. For another origin, add it to
  `CORS_ORIGINS` in `backend/.env`.
- Start the backend locally (README → "How to run locally") and use http://localhost:8000/docs to try requests.

**POST /api/auth/signup**: body `{"email": "a@b.com", "password": "min 8 chars", "name": "Anna"}` (`name` optional)
→ `201 {"access_token": "...", "token_type": "bearer", "user": {"id": 1, "email": "a@b.com", "name": "Anna", "created_at": "ISO"}}`.
`409` if the email is already registered.

**POST /api/auth/signin**: body `{"email", "password"}` → `200`, same shape as signup. `401` on wrong credentials.

**GET /api/auth/me** → `{"id", "email", "name", "created_at"}`. `401` if the token is missing, invalid, or expired.

**POST /api/calculate**: body is either a parcel or a car (discriminated by `delivery_type`):
```json
{"delivery_type": "parcel", "category": "electronics", "item_price": 200, "shipping_price": 15,
 "currency": "EUR", "rules": "current"}
```
- `category`: `electronics | clothing | cosmetics | toys | other`
- `currency`: `EUR | USD | UAH | GBP | PLN`
- `rules`: `current | july_2027` (default `current`)
- `sender`: `marketplace | private` (default `marketplace`). It only matters for `july_2027`, where a non-commercial
  parcel from a private person up to €45 is tax-free. The UI can ask "Is this a gift from a private person?".
```json
{"delivery_type": "car", "car_price": 10000, "shipping_price": 1200, "currency": "EUR",
 "engine_type": "petrol", "engine_volume_cc": 2000, "battery_kwh": null,
 "manufacture_year": 2014, "origin": "eu"}
```
- `engine_type`: `petrol | diesel | hybrid | electric` (`engine_volume_cc` is required for petrol, diesel, and
  hybrid; `battery_kwh` is required for electric)
- `origin`: `eu | other`. `eu` means **EU origin proven by EUR.1 / an origin declaration** (0% duty), not "bought in
  the EU". Electric cars always have 0% duty.
- `hybrid` pays excise by its combustion engine volume at the petrol rate (diesel hybrids: choose `diesel`).

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
a car missing `engine_volume_cc` / `battery_kwh` contains the reason in `detail[0].msg`.
`rates_verified_at` = the date the tax rates were last checked against the law. Show it in the UI (e.g. "Ставки
станом на 16.11.2026"). Parcels over €10,000 get a note that the result is only approximate.

**POST /api/calculate/compare-rules**: same parcel body (`rules` is ignored) → `{"current": <result>, "july_2027": <result>}`.

**GET /api/rates** → `{"date": "2026-11-16", "source": "nbu" | "fallback", "uah_per_unit": {"UAH": "1", "EUR": "50.222", "USD": "45.4274", "GBP": "60.106", "PLN": "11.3916"}}`

**GET /api/history** → `[{"id", "created_at", "delivery_type", "input": {...request body...}, "result": {...response...}}]`
(at most 100, newest first; numbers inside `input` come back as strings, e.g. `"item_price": "200"`)

Note: **every** `/api/calculate` call is stored in the DB (anonymous ones with `user_id = NULL`) so `/api/stats`
can count usage. Only signed-in users see their own calculations in `/api/history`. `compare-rules` is not stored.

**DELETE /api/history/{id}** → `204`. `404` if the item doesn't exist or isn't yours.

**GET /api/stats** → `{"users": 12, "calculations": 80, "calculations_by_signed_in": 40, "returning_users": 5}`
(`returning_users` = users who made calculations on 2 or more different days; used for the report)

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
  rules object, new delivery types (luggage) are a new class, and rates change in one file. The engine works only
  in EUR; currency conversion happens in the service layer. Lines are rounded to cents with ROUND_HALF_UP.
  (Liubomyr + Claude Code)
- 2026-11-16: All calculations are persisted, including anonymous ones, to get real usage numbers for the report
  (`/api/stats`). "Returning user" = a user with calculations on 2 or more different UTC days. (Liubomyr + Claude Code)
- 2026-11-16: **All hosting on AWS, using AWS services** (backend, database, frontend, secrets). Reason: team
  decision. The concrete services (App Runner vs ECS vs Beanstalk, S3+CloudFront vs Amplify) are Anton's choice;
  record them here and in §5 once chosen. (Liubomyr)
- 2026-11-16: **All tax numbers live in one data file, `backend/app/customs/tax_rates.json`, which is loaded at
  startup; it is not auto-updated from the internet.** Reason: there is no official machine-readable API for
  Ukrainian customs/excise rates (only legal text). Auto-applying scraped numbers could silently show users wrong
  taxes, and the law changes rarely and with advance notice. Instead, `scripts/check_law_updates.py` **detects**
  changes (fingerprints of the exact clauses) and a human updates the JSON in a reviewed commit, so git history is
  the audit trail. Exchange rates, which change daily, ARE loaded automatically (NBU API). `TAX_RATES_PATH` allows
  an external file (e.g. from S3) if rates ever need to change without a redeploy. (Liubomyr + Claude Code)
- 2026-11-16: Customs rules research moved from Anton to Liubomyr (Liubomyr's decision). (Liubomyr)
- 2026-11-16: Work happens on branch `liubomyr/backend`; it gets merged into `main` when the backend MVP is ready. (Liubomyr)

---

## 11. Open issues / TODO

- [x] Backend stack chosen (§5). [ ] Frontend stack and hosting still open (Anna, Anton).
- [x] `backend/` skeleton. [ ] `frontend/`, `infra/` skeletons (Anna, Anton).
- [ ] Deploy a "hello world" on AWS over HTTPS on day 1 to find hosting problems early (Anton). The backend already has `GET /api/health`.
- [x] Write the API contract in §8 (Liubomyr).
- [x] Implement the backend endpoints in §8 (Liubomyr).
- [x] Merge `liubomyr/backend` into `main` (Liubomyr, PR #1, 17.11).
- [ ] Choose the AWS services (backend compute, frontend hosting, IaC tool) and fill in §5 (Anton).
- [ ] Deploy the backend on AWS over HTTPS with RDS Postgres. `backend/Dockerfile` is ready (push the image to ECR); set `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS` from Secrets Manager/SSM (Anton + Liubomyr).
- [ ] Put the AWS setup into `infra/` (IaC templates or step-by-step console instructions), since `infra/` is graded (Anton).
- [ ] The Docker image build was not verified (no Docker daemon on Liubomyr's machine on 16.11). Run `docker build backend` once.
- [x] Verify the customs rates against the law, move them into `tax_rates.json`, and test with hand-calculated cases (Liubomyr, 16.11).
- [ ] Optional: rate limiting on auth endpoints, password reset (not needed for the demo).
- [ ] Schedule `cd backend && python scripts/check_law_updates.py` weekly (GitHub Actions cron or AWS EventBridge) and alert the team when it exits ≠ 0 (Anton).
- [ ] Re-check by hand when the Cabinet sets the start date of the July 2027 parcel VAT (source `law_5025_ix`) (Liubomyr).
- [ ] Optional: a "luggage" delivery type. The rules are already verified (Customs Code 374 p.1 and p.4): €1000 tax-free by air, €500/50 kg by land, then 10% duty + VAT on the excess (Liubomyr).
- [x] README "How to run locally" → Backend, plus backend production env vars under "How to deploy" (Liubomyr).
- [ ] README: the Frontend run section (Anna) and the actual deploy steps / hosting / HTTPS (Anton).

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

### 2026-11-16: Backend scaffold + API contract
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend
- **What was done:** Created the FastAPI project in `backend/` on branch `liubomyr/backend`: settings from env,
  SQLAlchemy engine/session/Base, `init_db()` on startup, CORS, `GET /api/health`, and a pytest setup with a
  `client` fixture (fresh SQLite tables per test). Wrote the full API contract in §8 (all endpoints planned for the
  backend MVP) so the frontend can start now.
- **Files touched:** created `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/.env.example`,
  `backend/.gitignore`, `backend/app/{main.py,core/config.py,core/database.py,api/health.py}`, empty package
  `__init__.py` files, `backend/tests/{conftest.py,test_health.py}`. Modified `AGENTS.md` (§5–§8, §10–§12).
- **Decisions & why:** see §10 (FastAPI/SQLAlchemy, Decimal-as-string money, branch).
- **How to verify / run:** `cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && .venv/bin/pytest`;
  run with `.venv/bin/uvicorn app.main:app --reload`, then open http://localhost:8000/docs
- **Not done / known problems / next steps:** auth, calculation engine, NBU rates, history, stats (§8 ⬜).


### 2026-11-16: Auth: sign-up, sign-in, current user
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend
- **What was done:** Added the `User` model (email is unique and stored lowercase; lookups are case-insensitive),
  PBKDF2-SHA256 password hashing, JWT access tokens, `AuthService` (register/authenticate), the
  `get_current_user` / `get_optional_user` dependencies, and the endpoints `POST /api/auth/signup` (201, 409 on a
  duplicate), `POST /api/auth/signin` (401 on bad credentials), and `GET /api/auth/me`.
- **Files touched:** created `backend/app/models/user.py`, `backend/app/core/security.py`,
  `backend/app/services/auth_service.py`, `backend/app/api/{auth.py,deps.py,schemas_auth.py}`,
  `backend/tests/test_auth.py`; modified `backend/app/models/__init__.py`, `backend/app/main.py`, `AGENTS.md`.
- **Decisions & why:** stdlib PBKDF2 instead of bcrypt, so there are no native build deps on hosting. Sign-out is
  client-side (stateless JWT).
- **How to verify / run:** `cd backend && .venv/bin/pytest tests/test_auth.py`
- **Not done / known problems / next steps:** no password reset or email verification (out of scope for the demo).


### 2026-11-16: Customs calculation engine (parcels + cars)
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend
- **What was done:** Added the pure-Python customs engine in `backend/app/customs/`: rule sets (current parcel,
  July 2027 parcel, current car), value objects, and `ParcelCalculator` / `CarCalculator`. These return a `Breakdown`
  with itemized `TaxLine`s (duty/excise/vat), each with a human-readable formula in Ukrainian, plus notes and totals.
  Formulas are documented in §13.
- **Files touched:** created `backend/app/customs/{rules.py,models.py,calculators.py}`,
  `backend/tests/test_customs.py` (21 tests); modified `AGENTS.md` (§6, §10, §12, §13).
- **Decisions & why:** see §10 (Strategy pattern, EUR-only engine).
- **How to verify / run:** `cd backend && .venv/bin/pytest tests/test_customs.py`. The tests reproduce the pitch
  numbers: €16 for a €200 parcel, and €2,048 / €4,640 for a €10,000 car.
- **Not done / known problems / next steps:** not exposed over HTTP yet (next: NBU rates + `/api/calculate`). The
  rates still need Anton's verification (see the open questions in §13).


### 2026-11-16: NBU exchange rates + calculate API
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend
- **What was done:** Added `RatesService` (live NBU fetch via httpx, 1h in-memory cache, last-good / static fallback)
  and `CalculationService`, which converts the input currency to EUR, runs the customs engine, and adds UAH amounts
  and notes. Added the endpoints `POST /api/calculate` (parcel or car, discriminated by `delivery_type`, 422 on
  invalid engine data), `POST /api/calculate/compare-rules` (current vs July 2027 for parcels), and `GET /api/rates`.
  Tests override `get_rates_service` with a fake NBU payload (1 EUR = 50 UAH, 1 USD = 40 UAH) in `tests/conftest.py`.
  Checked against the live NBU API on 16.11.2026: 1 EUR = 50.222 UAH.
- **Files touched:** created `backend/app/services/{rates_service.py,calculation_service.py}`,
  `backend/app/api/{calculate.py,schemas_calc.py}`, `backend/tests/{test_rates.py,test_calculate_api.py}`;
  modified `backend/app/main.py`, `backend/tests/conftest.py`, `AGENTS.md` (§6, §8, §12, §13).
- **Decisions & why:** the response adds a `rate_source` field (not in the original contract) so the UI can warn
  when fallback rates are used. Formulas are shown in EUR, because the customs rules are defined in EUR.
- **How to verify / run:** `cd backend && .venv/bin/pytest` (39 tests). Manual check: run uvicorn, open `/docs`, and
  try `POST /api/calculate` with the parcel example from §8.
- **Not done / known problems / next steps:** calculations are not saved to history yet (`calculation_id` is always
  null); history and stats endpoints are next.


### 2026-11-16: Calculation history, usage stats, deploy readiness
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend
- **What was done:** Added the `Calculation` model (input/result stored as JSON, nullable `user_id`) and
  `HistoryService`. `POST /api/calculate` now stores every calculation and returns `calculation_id` for signed-in
  users. Added `GET /api/history`, `DELETE /api/history/{id}` (owner only, 404 otherwise), and `GET /api/stats`
  (users, calculations, calculations_by_signed_in, returning_users) for the report. Added `normalize_db_url()`
  (accepts the `postgres://` URLs that hosting providers give), a backend `Dockerfile` + `.dockerignore`, and the
  backend run instructions in `README.md`. Smoke-tested with a real uvicorn and the live NBU API: sign-up →
  calculate in USD → history → stats all work.
- **Files touched:** created `backend/app/models/calculation.py`, `backend/app/services/history_service.py`,
  `backend/app/api/history.py`, `backend/tests/test_history.py`, `backend/Dockerfile`, `backend/.dockerignore`;
  modified `backend/app/api/calculate.py`, `backend/app/models/__init__.py`, `backend/app/core/database.py`,
  `backend/app/main.py`, `README.md`, `AGENTS.md`.
- **Decisions & why:** see §10 (store all calculations; definition of a returning user).
- **How to verify / run:** `cd backend && .venv/bin/pytest` (43 passed); `.venv/bin/uvicorn app.main:app --reload` → http://localhost:8000/docs
- **Not done / known problems / next steps:** not deployed; Docker build not verified locally; no DB migrations
  (tables are auto-created, so a schema change on prod requires a manual ALTER or a fresh DB); customs rates
  are unverified. See §11.


### 2026-11-16: AGENTS.md completeness pass
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** docs
- **What was done:** Checked this file against the actual repo and filled the gaps: repo URL + push status (§0),
  the test files and what each covers, and the backend layer architecture + "how to add a delivery type" (§6),
  real `/api/rates` example values and notes for the frontend: token handling, 401, CORS dev origins (§8),
  and the stale README TODO (§11).
- **Files touched:** modified `AGENTS.md`
- **Decisions & why:** none
- **How to verify / run:** n/a (docs only)
- **Not done / known problems / next steps:** none new; see §11.


### 2026-11-16: Hosting target set to AWS
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** docs / infra planning
- **What was done:** Recorded the team decision that everything is hosted on AWS using AWS services. Updated §5 with
  the AWS service options (backend compute, RDS Postgres, frontend hosting, Secrets Manager/SSM, CloudWatch) and the
  AWS-specific backend notes: no SQLite in prod, RDS SSL, outbound access for the NBU API, CORS vs. single
  CloudFront origin. Also updated §0, §3, §10, and §11, and in `README.md`, Anton's role and the deploy section.
  No code changes were needed: the Dockerfile already uses `$PORT` and proxy headers, and `postgres://` URLs are
  accepted.
- **Files touched:** modified `AGENTS.md`, `README.md`
- **Decisions & why:** see §10 (AWS).
- **How to verify / run:** n/a (docs only)
- **Not done / known problems / next steps:** the concrete AWS services and `infra/` are still to be done (Anton).


### 2026-11-16: Customs rules verified against the law; all rates moved to tax_rates.json; law watcher
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** backend / docs
- **What was done:** The customs research task was moved from Anton to Liubomyr. Checked every rate against the
  official consolidated texts (Customs Code art. 374, Tax Code 215.3.5-1 and 14.1.49-1, Laws 5025-IX/5026-IX of
  15.10.2026). **Fixed 4 wrong rules:**
  (1) car age coefficient is `current − year − 1` (was `current − year`);
  (2) hybrids pay excise by engine volume at the petrol rate (was a flat €100, which belongs to other codes);
  (3) electric cars always have 0% duty (was by origin);
  (4) July 2027 parcels: VAT only on parcels ≤ €150, no duty on them, P2P ≤ €45 exempt, >€150 unchanged (was VAT on
  the full value of every parcel).
  Added a warning note for parcels > €10,000. Moved all numbers into `backend/app/customs/tax_rates.json` (loaded and
  validated by `rules.py`, overridable via `TAX_RATES_PATH`). Added `scripts/check_law_updates.py` (clause
  fingerprints, verified working against the live site). The API now accepts `sender` (parcel) and returns
  `rates_version` and `rates_verified_at`. Rewrote the customs tests with hand-calculated cases. 66 tests pass.
- **Files touched:** created `backend/app/customs/tax_rates.json`, `backend/scripts/check_law_updates.py`,
  `backend/tests/test_tax_rates_file.py`, `backend/tests/test_law_watcher.py`; modified
  `backend/app/customs/{rules.py,calculators.py,models.py}`, `backend/app/api/schemas_calc.py`,
  `backend/app/services/calculation_service.py`, `backend/tests/{test_customs.py,test_calculate_api.py}`,
  `backend/.env.example`, `README.md` (task moved to Liubomyr, timeline), `AGENTS.md` (§3, §6–§8, §10, §11, §13).
- **Decisions & why:** see §10 (rates in a data file + change detection instead of auto-update).
- **How to verify / run:** `cd backend && .venv/bin/pytest` (66 passed); `.venv/bin/python scripts/check_law_updates.py` (all `[ok]`).
- **Not done / known problems / next steps:** schedule the watcher weekly (Anton); 3 sources are manual (news,
  tariff annex); the July 2027 start date depends on a Cabinet decision. **Pitch note:** the €4,640 figure matches a
  2013 car, not a 2014 one; it is still a valid example.


### 2026-11-17: Backend merged into main
- **Who:** Liubomyr Voskalo via Claude Code (Opus 5.5)
- **Area:** repo
- **What was done:** Opened PR #1 (https://github.com/voskalo/PidKlyuch/pull/1) from `liubomyr/backend` and merged
  it into `main` with a merge commit (`cbb4ece`), so all 10 backend commits keep their history. Verified on `main`: 66 tests pass.
- **Files touched:** `AGENTS.md` (§0, §11, §12)
- **Decisions & why:** a merge commit, not squash, to keep the step-by-step history of the backend work.
- **How to verify / run:** `git pull origin main && cd backend && .venv/bin/pytest`
- **Not done / known problems / next steps:** teammates should branch from the updated `main` (e.g. `anna/frontend`,
  `anton/infra`). The branch `liubomyr/backend` still exists on GitHub and can be deleted.

---

## 13. Domain notes: Ukrainian customs (VERIFIED 16.11.2026)

All numbers are in `backend/app/customs/tax_rates.json`, which includes source ids, URLs, and fingerprints. Verified
by Liubomyr (via Claude Code) against the consolidated texts on zakon.rada.gov.ua (Customs Code revision of
23.10.2026, Tax Code revision of 01.11.2026) plus news coverage of the laws adopted 15.10.2026.

**Parcels: current rules (Customs Code art. 374 p.7, verbatim check):**
- Goods (except excisable ones) in international postal or express shipments with a **total invoice value ≤ €150** are
  **not taxed**. The threshold is based on the invoice value of the goods, so **shipping is not counted**.
- **€150 < value ≤ €10,000:** duty **10%** and VAT **20%**, and the tax base is **only the part above €150**.
  VAT = 20% × (excess + duty).
- **> €10,000 (p.8):** full commercial declaration at full tariff rates. The calculator adds an "approximate" note.
- Check: €200 parcel → duty €5 + VAT €11 = **€16** ✔ (the pitch number).

**Parcels: July 2027 rules (Laws № 5025-IX (Tax Code) and № 5026-IX (Customs Code), adopted 15.10.2026):**
- VAT 20% on parcels **≤ €150**, collected by the marketplace at checkout ("distance sale", Tax Code 14.1.49-1).
  **No duty** on them. Starts **no earlier than 1 July 2027**, after a Cabinet decision.
- Non-commercial **private person → private person parcels up to €45** remain tax-free.
- Parcels **> €150**: the same as now (duty + VAT on the excess).
- Implementation assumptions (flagged): the VAT base is the goods value without shipping. Private parcels between
  €45 and €150 pay VAT (only ≤ €45 is exempt).

**Cars (Tax Code 215.3.5-1, verbatim check):**
- Excise = base × K_engine × K_age.
  - Base, € per unit: petrol ≤3000 cm³ **50**, >3000 **100**; diesel ≤3500 cm³ **75**, >3500 **150**.
  - K_engine = cm³ / 1000.
  - **K_age = full calendar years from the year AFTER manufacture to the current year**, i.e. `current − year − 1`,
    min 1, max 15. A 2014 car in 2026 has K=11, not 12. Many online calculators get this wrong.
- **Hybrids:** there is no separate rate; they pay by the combustion engine (spark-ignition = petrol rate). The flat
  €100 rate in the code applies to other codes (8703 80 x0 90, 8703 90), not hybrids.
- **Electric (8703 80 10 10 / 80 90 10):** €1 per kWh of battery; duty 0%; **VAT 20% since 01.01.2026** (the
  exemption was not extended; secondary sources).
- Duty: **10%** of the customs value (car price + delivery to the border); **0% for EU origin** under the DCFTA,
  only with proof of origin (secondary sources). VAT 20% × (customs value + duty + excise).
- Not included: the Pension Fund levy at first registration, certification, and broker fees.
- Checks against the pitch: €10,000 non-EU petrol 2.0 l → €4,520 for a 2014 car, **€4,640 for a 2013 car** (the
  pitch's upper number). EU-origin new petrol 0.8 l → **€2,048** ✔.

**Keeping rates current:** run `cd backend && .venv/bin/python scripts/check_law_updates.py` (planned to run weekly).
- `[CHANGED]`/`[MISSING]` → read the new law text, edit `tax_rates.json` (and tests), run `pytest`, then
  `scripts/check_law_updates.py --update` to store the new fingerprints, then commit with the law number in the message.
- `[manual]` sources (news, tariff annex) must be re-checked by hand.

**Exchange rates (implemented in `backend/app/services/rates_service.py`):** NBU official daily rates from
`https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json` (a list of `{cc, rate, exchangedate}`, where rate is
UAH per 1 unit). They are cached in memory for 1 hour. If a fetch fails, the last good table is used, and if there is
none, the static `FALLBACK_UAH_PER_UNIT` (`source: "fallback"`). Supported: EUR, USD, UAH, GBP, PLN. Input amounts are
converted to EUR (amount × UAH-per-currency ÷ UAH-per-EUR), the calculation runs in EUR, and the results are shown in
EUR and UAH.

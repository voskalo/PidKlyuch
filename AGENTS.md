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
| Current phase | Day 1: backend in progress on branch `liubomyr/backend`; frontend and infra not started |
| Tech stack | Backend: Python/FastAPI + SQLAlchemy (see §5). Frontend and hosting: TBD |
| Live demo URL | TBD (must be HTTPS) |
| Repo URL | TBD |

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
| Working prototype with sign-in: deployed, reachable over **HTTPS**, users can **sign up and sign in** | 3 | ⬜ |
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

Backend chosen 2026-11-16 (Liubomyr). Frontend and hosting are still open.

| Layer | Choice | Notes |
|---|---|---|
| Backend language/framework | **Python 3.12+ / FastAPI** | `backend/`, entry point `app.main:app` (uvicorn) |
| ORM / Database | **SQLAlchemy 2.0**: SQLite locally, **Postgres** in prod | set via `DATABASE_URL`; tables are auto-created on startup (no migrations yet) |
| Auth method | **JWT bearer tokens** (PyJWT, HS256) | passwords hashed with PBKDF2-SHA256 (stdlib) |
| Tests | **pytest** + FastAPI `TestClient` | `cd backend && .venv/bin/pytest` |
| Frontend framework | TBD (Anna) | consumes §8 |
| Hosting (backend) | TBD | must be HTTPS |
| Hosting (frontend) | TBD | must be HTTPS |
| CI | TBD | |

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
    ├── app/
    │   ├── main.py              # create_app(): CORS, routers, DB init on startup
    │   ├── core/config.py       # Settings (pydantic-settings, reads env/.env)
    │   ├── core/database.py     # engine, SessionLocal, Base, get_db(), init_db()
    │   ├── api/health.py        # GET /api/health
    │   ├── api/auth.py          # /api/auth/signup|signin|me
    │   ├── api/schemas_auth.py  # pydantic request/response models for auth
    │   ├── api/deps.py          # get_current_user / get_optional_user (Bearer JWT)
    │   ├── core/security.py     # PBKDF2 password hashing, JWT encode/decode
    │   ├── models/              # SQLAlchemy ORM models: user.py (User)
    │   ├── services/            # business services: auth_service.py (AuthService: register/authenticate)
    │   └── customs/             # customs calculation engine (pure Python, no DB/HTTP)
    └── tests/                   # pytest; conftest.py sets a test SQLite DB + fresh tables per test
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
Backend vars are documented in `backend/.env.example`, read by `backend/app/core/config.py`.

- `DATABASE_URL`: backend. `sqlite:///./pidklyuch.db` (default) or `postgresql+psycopg://user:pass@host:5432/db`. Optional locally, **required in prod**.
- `JWT_SECRET`: backend, signs auth tokens. **Required in prod** (the default is insecure).
- `JWT_EXPIRE_MINUTES`: backend, token lifetime, default `10080` (7 days). Optional.
- `CORS_ORIGINS`: backend, comma-separated frontend origins, e.g. `https://pidklyuch.example.com`. **Required in prod.**
- `NBU_API_URL`: backend, NBU exchange-rate endpoint. Optional (has a default).
- `PASSWORD_HASH_ITERATIONS`: backend, PBKDF2 iterations, default `390000`. Only lowered in tests.

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
| ⬜ | POST | `/api/calculate` | optional | calculate landed price; saved to history if signed in |
| ⬜ | POST | `/api/calculate/compare-rules` | – | parcel: current rules vs July 2027 rules |
| ⬜ | GET | `/api/rates` | – | NBU rates used for conversion |
| ⬜ | GET | `/api/history` | required | user's saved calculations, newest first |
| ⬜ | DELETE | `/api/history/{id}` | required | delete one saved calculation |
| ⬜ | GET | `/api/stats` | – | aggregate counters for the report |

**Sign-out** is client-side: delete the stored token (JWT is stateless).

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
```json
{"delivery_type": "car", "car_price": 10000, "shipping_price": 1200, "currency": "EUR",
 "engine_type": "petrol", "engine_volume_cc": 2000, "battery_kwh": null,
 "manufacture_year": 2014, "origin": "eu"}
```
- `engine_type`: `petrol | diesel | hybrid | electric` (`engine_volume_cc` is required for petrol, diesel, and
  hybrid; `battery_kwh` is required for electric)
- `origin`: `eu | other` (EU-origin cars have a different duty rate)

Response `200`:
```json
{"delivery_type": "parcel", "rules": "current", "input_currency": "EUR",
 "rate_date": "2026-11-16", "eur_uah": "48.1234",
 "goods_value_eur": "200.00", "shipping_eur": "15.00",
 "lines": [
   {"code": "duty", "label": "Мито", "amount_eur": "5.00", "amount_uah": "240.62",
    "formula": "10% × (200.00 − 150.00) = 5.00 EUR"},
   {"code": "vat", "label": "ПДВ", "amount_eur": "11.00", "amount_uah": "529.36",
    "formula": "20% × (50.00 + 5.00) = 11.00 EUR"}
 ],
 "taxes_total_eur": "16.00", "taxes_total_uah": "769.97",
 "landed_total_eur": "231.00", "landed_total_uah": "11116.51",
 "notes": ["..."], "calculation_id": 42}
```
`line.code` ∈ `duty | excise | vat`. `calculation_id` is `null` when the caller is not signed in.

**POST /api/calculate/compare-rules**: same parcel body (`rules` is ignored) → `{"current": <result>, "july_2027": <result>}`.

**GET /api/rates** → `{"date": "2026-11-16", "source": "nbu" | "fallback", "uah_per_unit": {"EUR": "48.12", "USD": "41.50", ...}}`

**GET /api/history** → `[{"id", "created_at", "delivery_type", "input": {...request body...}, "result": {...response...}}]`

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
- 2026-11-16: Work happens on branch `liubomyr/backend`; it gets merged into `main` when the backend MVP is ready. (Liubomyr)

---

## 11. Open issues / TODO

- [x] Backend stack chosen (§5). [ ] Frontend stack and hosting still open (Anna, Anton).
- [x] `backend/` skeleton. [ ] `frontend/`, `infra/` skeletons (Anna, Anton).
- [ ] Deploy a "hello world" over HTTPS on day 1 to find hosting problems early (Anton). The backend already has `GET /api/health`.
- [x] Write the API contract in §8 (Liubomyr).
- [ ] Implement the backend endpoints marked ⬜ in §8 (Liubomyr).
- [ ] Write `docs/customs-rules.md` with verified rules, sources, and test cases (Anton).
- [ ] Fill in "How to run" and "How to deploy" in `README.md` (Anton, with input from both other owners).

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

---

## 13. Domain notes: Ukrainian customs (to be verified)

> ⚠️ Anton must verify these against official sources (Customs Code of Ukraine, Tax Code of Ukraine,
> customs.gov.ua, tax.gov.ua) and record the sources and exact rules in `docs/customs-rules.md`.
> Update this section with a short summary and the date of verification.

**Parcels (current rules, as assumed in the pitch):**
- Duty-free threshold: **€150** per parcel (value of goods, excluding shipping, as assumed).
- Above the threshold, on the **excess over €150**: duty **10%**, then VAT **20%** on (excess + duty).
- Pitch consistency check: €200 parcel → excess €50 → duty €5 → VAT 20% × €55 = €11 → **total ≈ €16** ✔
- **July 2027 change (from the pitch):** VAT applies to every imported parcel (no threshold for VAT). Exact
  rules (e.g. whether duty is still threshold-based) must be confirmed.

**Cars:** taxes are customs duty + excise + VAT. Excise depends on engine type, engine volume, and car age, and
VAT is charged on (customs value + duty + excise). The duty rate may depend on country of origin (EU vs. non-EU).
Exact formulas and rates are **not filled in yet**. The pitch's reference point is a €10,000 car → €2,048–€4,640
in taxes, which can serve as a sanity check for test cases.

**Exchange rates:** National Bank of Ukraine (NBU) official daily rates. The public NBU API returns JSON. Cache the
rates daily and keep a fallback if the API is down.

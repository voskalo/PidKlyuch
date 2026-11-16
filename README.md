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
- **Infra (AWS):** pick the AWS services for the backend (container from `backend/Dockerfile`), RDS Postgres, frontend hosting, and **HTTPS**. Put the setup in `infra/`. Deploy a "hello world" on **day 1**, then redeploy as features land. Optional CI (e.g. GitHub Actions → ECR) that runs the backend tests.
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

## How to run locally

### Backend (Python 3.12+)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env            # defaults work locally (SQLite file pidklyuch.db)
.venv/bin/uvicorn app.main:app --reload
```

- API: http://localhost:8000/api/health
- Interactive API docs (try every endpoint): http://localhost:8000/docs
- Tests: `.venv/bin/pytest`
- With Docker instead: `docker build -t pidklyuch-backend backend && docker run -p 8000:8000 pidklyuch-backend`

The API endpoints and the request/response formats are described in [`AGENTS.md`](AGENTS.md) §8.

### Frontend

_TBD (Anna)._

## How to deploy

Everything is hosted on **AWS**: the backend container, **RDS PostgreSQL**, and the frontend with HTTPS. _TBD (Anton): the exact services, how HTTPS is set up, and deploy commands (see `infra/`)._

The backend is a single Docker image (`backend/Dockerfile`, listens on `$PORT`) and needs these environment
variables in production:

| Variable | Example |
|---|---|
| `DATABASE_URL` | `postgresql://user:pass@<rds-endpoint>:5432/pidklyuch?sslmode=require` (RDS Postgres; never SQLite on AWS) |
| `JWT_SECRET` | store in Secrets Manager / SSM; a long random string: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CORS_ORIGINS` | the HTTPS URL of the frontend, e.g. `https://pidklyuch.example.com` |

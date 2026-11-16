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
| Current phase | Day 1: setup & scaffolding. Infra and customs rules spec in progress on `anton/infra-and-docs` |
| Tech stack | **TBD.** Record it in §5 as soon as it is chosen |
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

**Status: TBD.** Whoever decides fills this in and logs the decision in §10.

| Layer | Choice | Notes |
|---|---|---|
| Backend language/framework | TBD | |
| Database | TBD | |
| Auth method | TBD | e.g. sessions vs JWT; passwords must be hashed |
| Frontend framework | TBD | |
| Hosting (backend) | TBD | Docker Compose + Caddy v2 (automatic HTTPS) |
| Hosting (frontend) | TBD | Docker Compose + Caddy v2 (automatic HTTPS) |
| CI | TBD | |

---

## 6. Repository structure

Current state (update on every structural change):

```
PidKlyuch/
├── docs/
│   └── customs-rules.md    # Ukrainian customs rules spec (parcels, cars, NBU rates, test cases)
├── infra/
│   ├── hello-world/
│   │   └── index.html      # Day 1 static status/landing page for HTTPS smoke test
│   ├── Caddyfile           # Caddy v2 reverse proxy config with automatic HTTPS and /healthz
│   ├── Dockerfile          # lightweight caddy:2-alpine static server image for hello-world
│   ├── docker-compose.yml  # Docker Compose stack (caddy + hello) with ports 80/443 & volumes
│   └── README.md           # deployment architecture, prerequisites, run & HTTPS deploy instructions
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

- `DOMAIN`: `infra/docker-compose.yml` & `infra/Caddyfile` (site block host for automatic HTTPS), example `pidklyuch.example.com` or `localhost`, optional (defaults to `localhost`).
- `ACME_EMAIL`: `infra/docker-compose.yml` & `infra/Caddyfile` (Let's Encrypt / ACME notification email), example `admin@example.com`, optional (defaults to `admin@example.com`).

---

## 8. API contract (backend ↔ frontend)

Not defined yet. Liubomyr's first task is to write the endpoint list here so Anna can build against mocks.
For each endpoint: method, path, auth required?, request body, response body, error codes.

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

---

## 11. Open issues / TODO

- [ ] Choose the tech stack and fill in §5 (all, Mon 16 Nov).
- [ ] Create `backend/`, `frontend/`, `infra/` skeletons (`infra/` done by Anton; `backend/`, `frontend/` pending).
- [ ] Deploy a "hello world" over HTTPS on day 1 to find hosting problems early (compose + Caddy config ready in `infra/`; live VPS deploy pending hosting choice).
- [ ] Write the API contract in §8 (Liubomyr).
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

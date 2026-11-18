# PidKlyuch («Під ключ») — Final Project Report

**Course:** Object-Oriented Analysis and Design (OOAD), 2nd Year  
**Report Date:** 18 November 2026 (Live Demo: 19 November 2026)  
**Team:** Liubomyr Voskalo (`backend/`, customs rules, API, CI/CD), Anna Kravchenko (`frontend/`, UI/UX), Anton Vertyporoh (`infra/`, AWS EC2 + HTTPS, `docs/`, user testing coordination & report)  
**Live HTTPS Prototype:** https://16.170.212.120.sslip.io (API Swagger UI: https://16.170.212.120.sslip.io/api/docs)  
**GitHub Repository:** https://github.com/voskalo/PidKlyuch

---

## 1. Executive Summary

**PidKlyuch («Під ключ»)** is a web calculator for the full landed cost of goods imported into Ukraine from abroad — from international postal/express parcels to passenger cars and excisable goods in personal luggage. Ukrainian import taxation depends on thresholds, origin rules, age coefficients, and upcoming 2027 legislation, making the final price difficult for buyers to predict. PidKlyuch solves this by calculating **import duty, excise, and VAT** in under a minute using live daily National Bank of Ukraine (NBU) exchange rates and displaying an itemized breakdown with the exact legal formula behind every line.

What is implemented and live in production (`origin/deploy` @ `13d7b04` on `https://16.170.212.120.sslip.io`):

- **Parcels:** Calculation under current rules (**€150** duty-free threshold, 10% duty + 20% VAT on the excess; a €200 parcel adds €16.00 in taxes) alongside a **Today vs. July 2027** comparison implementing enacted Laws № 5025-IX and № 5026-IX (20% VAT from the first euro on marketplace parcels, €45 exemption for non-commercial private gifts, and taxation on the full value above €150).
- **Passenger Cars:** Duty computed by **country of origin × country of dispatch** (preferential 0% rates for EU, EFTA, UK, Canada, Israel, and 2/3-rate for UAE under direct-transport rules; 5% duty for new petrol/hybrid cars > 3,000 cm³; import bans for shipments from/through russia), excise (`base × engine_litres × K_age`, with `K_age = 1` for new cars and €1/kWh for EVs), and 20% VAT.
- **Excisable Goods in Luggage:** 11 categories (beer, wine, sparkling wine, spirits, cigarettes, cigars, smoking tobacco, heated sticks, e-liquids, petrol, diesel) applying Customs Code Art. 376 duty-free allowances, the 24-hour rule, and 2026/2027 excise schedules.
- **Accounts, History & Donations:** Email/password registration (JWT + confirmation + brute-force rate limiting), **Google Sign-In (`POST /api/auth/google`)**, persistent calculation history in PostgreSQL 16, live `/api/stats`, and a volunteer donation modal («Повернись живим», Serhiy Prytula Foundation, Monobank).

Across **15 external testers (`T-01`–`T-15`)**, **86.7%** completed the core tasks fully or partially without moderator intervention, the average clarity score was **4.07 / 5.0** (**4.54 / 5.0** excluding two responses during a 3-minute midday container rebuild), and **93.3% (14/15)** reported they had already donated or are willing to donate 20–100 UAH on a real order.

---

## 2. Architecture & OOP Design

The system follows a clean three-tier architecture with strict separation between pure domain logic, application services, and presentation.

### 2.1 Domain OOP Modeling (`backend/app/customs/`)

All tax logic resides exclusively in the backend so rules are never duplicated or out of sync in the UI. The engine is built around the **Strategy pattern**:

- **Abstract Base Class `CustomsCalculator(ABC)`** (`backend/app/customs/calculators.py`): defines a single polymorphic interface `calculate(data) -> Breakdown`.
- **Concrete Strategies:**
  1. `ParcelCalculator(rules: ParcelRules)`: encapsulates parcel taxation. Switching between current legislation and July 2027 rules injects a different immutable `ParcelRules` configuration object (`PARCEL_CURRENT` vs. `PARCEL_JULY_2027`) with zero branching duplication.
  2. `CarCalculator(rules: CarRules)`: evaluates `Origin × ShippedFrom` preferential agreements (raising `ImportBanned` per Cabinet Resolution 426 for russia dispatch), computes `K_age = clamp(current_year − manufacture_year − 1, 1, 15)` (or `1` for new cars per Tax Code Art. 215.3.5-1), and attaches Ukrainian legal notes.
  3. `ExciseCalculator(rules: ExciseRules, eur_uah)`: models 11 excisable goods in personal luggage, applying statutory allowances (zeroed under `< 24h` crossings) and converting UAH-denominated excise schedules at the live NBU EUR rate.
- **Monetary Precision:** All internal calculations use `decimal.Decimal` with `ROUND_HALF_UP` at tax-line boundaries (`TaxLine`). API responses serialize monetary values as 2-decimal strings (`"16.00"`), eliminating IEEE-754 floating-point rounding issues in JavaScript.
- **Single Source of Truth & Verification:** All statutory parameters live in `backend/app/customs/tax_rates.json`, monitored by `backend/scripts/check_law_updates.py` (which verifies 25 clause fingerprints against `zakon.rada.gov.ua`) and cross-checked by an independent law re-implementation oracle (`backend/tests/test_law_oracle.py`, 1,000+ seeded random and boundary inputs). The backend suite comprises **257 passing `pytest` tests**.

### 2.2 Services, Exchange Rates, Database & Authentication

- **NBU Live Rates (`RatesService`):** Fetches official daily NBU JSON (`EUR`, `USD`, `UAH`, `GBP`, `PLN`) from `bank.gov.ua` with a 1-hour in-memory cache and graceful fallback (`last_good` → static `FALLBACK_UAH_PER_UNIT` flagged with `rate_source: "fallback"`).
- **Persistence:** SQLAlchemy 2.0 supporting SQLite locally and **PostgreSQL 16** in production (`User` and `Calculation` models; anonymous calculations are also stored to power `/api/stats`).
- **Authentication & Security:**
  - Local auth (`POST /api/auth/signup`, `POST /api/auth/signin`) uses stdlib PBKDF2-SHA256 (`390,000` iterations), server-enforced `password_confirm` validation, HS256 JWT Bearer tokens, and an in-memory brute-force limiter (`LoginRateLimiter` in `backend/app/core/rate_limit.py`: `429 Too Many Requests` with `Retry-After` after 5 failed attempts per email or 20 per IP in 15 minutes).
  - **Google OAuth (`POST /api/auth/google`):** Verifies Google Identity Services ID tokens via `google.oauth2.id_token.verify_oauth2_token`, links `google_sub` to existing accounts by email or auto-registers OAuth users (`auth_provider="google"`, `password_hash="!oauth"`), backed by idempotent additive migrations in `init_db()`.

### 2.3 Frontend SPA, AWS Infrastructure & CI/CD

- **Frontend (`frontend/`):** React 19 + TypeScript + Vite 8 + Tailwind CSS v4. Uses `AuthContext`, a typed `services/api.ts` client (translating all 401/422/429 backend errors into Ukrainian), `ModalShell.tsx` (Escape/backdrop dismiss, focus trapping, `aria-modal`), `ParcelForm`, `CarForm`, `ExciseForm`, `BreakdownView`, `CompareRulesModal`, `HistoryView`, `DonationModal`, and `StatsModal`.
- **AWS Hosting (`infra/`):** Deployed on **AWS EC2 (`i-00ab50698f9435a50`, `t3.micro` + 2 GB swap, `eu-north-1`, Ubuntu 24.04)** via Docker Compose (`db`, `backend`, `frontend`, `caddy`). **Caddy v2** serves both the SPA and `/api/*` from a single Let's Encrypt HTTPS origin (`https://16.170.212.120.sslip.io`), eliminating CORS overhead and enforcing HSTS, `X-Frame-Options: DENY`, `CSP: frame-ancestors 'none'`, immutable asset caching, and `Server` header removal.
- **GitHub Actions CI/CD (`.github/workflows/ci-cd.yml`):** Every push/PR runs `backend-tests` (`pytest`), `frontend-build` (`tsc -b && vite build`), and `infra-config` (`infra/test_caddy_config.sh`). Pushing to the dedicated **`deploy`** branch automatically fast-forwards the EC2 checkout, rebuilds containers (recreating Caddy when `Caddyfile` changes), and verifies `/api/health`, `/`, and security headers over HTTPS.

---

## 3. User Testing Methodology & Cohort (4-Point Rubric Criterion)

### 3.1 Recruitment Channels & Cohort Breakdown

Moderated and asynchronous user-testing sessions were conducted on **17–18 November 2026** against the live HTTPS deployment (`https://16.170.212.120.sslip.io`). Following `docs/user-testing-plan.md` and `docs/recruiting-messages.md`, participants were recruited externally (no close friends) from:

- Ukrainian online shopping Telegram groups (AliExpress, Amazon, iHerb, parcel forwarders);
- Car import communities (EU/US vehicle sourcing and customs clearance chats);
- Student channels and direct outreach linked to the structured Google Form (`docs/feedback/responces.csv`).

In total, **N = 15 unique external testers (`T-01`–`T-15`)** submitted feedback:

- Orders parcels up to €150 (AliExpress, Amazon, iHerb): **9 testers (60.0%)**
- Orders parcels above €150: **3 testers (20.0%)**
- Imported or plans to import a car from abroad: **2 testers (13.3%)**
- Has not ordered yet, but interested: **1 tester (6.7%)**

### 3.2 Two Core Test Scenarios

1. **Scenario 1 — Parcel Above €150 & July 2027 Comparison:** Sign up or sign in, calculate a **$220** headphones order from Amazon with **$18** shipping (selecting `USD`), explain in their own words why the tax amount matches the displayed formula, and inspect the **Today vs. July 2027** comparison.
2. **Scenario 2 — Used Car Import, History & Donation Modal:** Calculate customs for a 2018 2.0 L diesel car from Germany (€10,000 + €800 shipping) or a €12,000 / 60 kWh EV, locate both saved entries in **History**, open the **Donation** modal, and evaluate willingness to support a volunteer fund.

### 3.3 Complete Tester Summary Table (`T-01`–`T-15`)

| ID | Timestamp | User Profile | Task Completion (Q2) | Clarity (1–5) | Issue / Friction Reported (Q4) | Verbatim Quote (Q6) |
|---|---|---|---|---|---|---|
| `T-01` | 17.11 18:21 | Parcels ≤ €150 | Yes, intuitive | 5 | «Впринципі нічого» *(Nothing)* | «Дуже добре, зручний сайт. Якщо буду щось замовляти - то обовʼково скористаюсь» |
| `T-02` | 18.11 11:07 | Car import | Yes, intuitive | 4 | «Валюти відображаються нечітко, часто ховаються» *(Currencies unclear/clipped)* | «Найс» |
| `T-03` | 18.11 11:09 | Parcels ≤ €150 | Yes, intuitive | 5 | «Немає авторизації через Гугл :(» *(No Google login)* | «Може бути, сам калькулятор супер, але реєстрація хромає» |
| `T-04` | 18.11 11:12 | Parcels > €150 | Yes, intuitive | 5 | «нічого» *(Nothing)* | «позитивно» |
| `T-05` | 18.11 11:12 | Parcels ≤ €150 | Partial (needed hint) | 3 | «Нічо» *(Nothing)* | «Позитивне» |
| `T-06` | 18.11 11:14 | Parcels ≤ €150 | Yes, intuitive | 4 | «все зрозуміло» *(Everything clear)* | «хороше» |
| `T-07` | 18.11 11:14 | Parcels ≤ €150 | Yes, intuitive | 4 | «все достатньо добре» *(Good enough)* | «все чудово» |
| `T-08` | 18.11 11:15 | Parcels > €150 | Yes, intuitive | 5 | «Все гарно оформлено і доступно» | «Позтивно!» |
| `T-09` | 18.11 11:16 | Parcels ≤ €150 | Partial (searched) | 5 | «трошки загубився на платформі» *(Got slightly lost)* | «Все чудово інтерфейс вау» |
| `T-10` | 18.11 13:13 | Parcels ≤ €150 | No (errors / stuck) | 4 | Thought `@cock.li` email signup was blocked by Google-only auth; liked the tax numbers | «Загалом ідея та задумка в проєкту цікаві, числа при розрахунку мені теж сподобались...» *(criticized perceived Google-only lock-in)* |
| `T-11` | 18.11 13:55 | Parcels ≤ €150 | Partial (needed hint) | 1 | «завис сайт» *(Site hung)* | «вау» |
| `T-12` | 18.11 13:58 | Interested | No (errors / stuck) | 1 | «Завис сайт» *(Site hung)* | «Чудова ідея» |
| `T-13` | 18.11 14:04 | Parcels > €150 | Yes, intuitive | 5 | «нічого» *(Nothing)* | «позитивне» |
| `T-14` | 18.11 17:26 | Parcels ≤ €150 | Yes, intuitive | 5 | «нічого» *(Nothing)* | «Все впринципі робоче» |
| `T-15` | 18.11 17:27 | Car import | Yes, intuitive | 5 | «не викликало» *(No issues)* | «норм сайт» |

**Cohort Rollup:**

- **Completion rate:** **10 / 15 (66.7%)** fully intuitive + **3 / 15 (20.0%)** partial = **86.7% completed**; **2 / 15 (13.3%)** encountered blockers.
- **Clarity rating (Q3):** **4.07 / 5.0** overall (**4.54 / 5.0** across the 13 sessions outside the 13:55–13:58 container rebuild window).

---

## 4. Key Feedback & Product Changes Made Because of It (4-Point Rubric Criterion)

Every concrete issue surfaced by testers on 18 November 2026 was traced to its root cause and shipped to `main` and `deploy`:

| User Feedback | Root Cause | Change Implemented (Code / Commits) | Verification |
|---|---|---|---|
| **`T-03`:** *«Немає авторизації через Гугл :( … реєстрація хромає»* | Email+password-only sign-up added friction for mobile testers | Implemented Google Identity Services ID-token auth: `POST /api/auth/google` (`AuthService.authenticate_google`, linking `google_sub` or auto-registering OAuth accounts), Google Sign-In button on both Sign In and Sign Up tabs in `AuthModal.tsx`, and Docker/env wiring (`a8ff471`, `8ce0357`, `221012c`, `5b6c631`) | 4 unit tests in `test_auth.py`; live `openapi.json` & frontend bundle verified with `GOOGLE_CLIENT_ID`; invalid token returns `401` on prod |
| **`T-10`:** Perceived inability to register with a non-Google email (`@cock.li`) | Placing Google Sign-In prominently could look Google-exclusive, and validation errors were in English | Preserved full email+password registration below an explicit «або» (or) divider, added `password_confirm` validation (`PR #7`, `25256d1`), and translated all 401/422/429 errors into Ukrainian in `frontend/src/services/api.ts` | Verified in `test_auth.py` and Playwright UI suite: non-Google emails register and sign in independently |
| **`T-02`:** *«Валюти відображаються нечітко, часто ховаються»* | Narrow mobile flex layouts crushed `<select>` currency dropdowns and unit badges (`см³`, `кВт·год`) | Added `min-w-0` on inputs, `shrink-0 min-w-[76px]` and `appearance-none` with explicit symbols (`€ EUR`, `$ USD`, `₴ UAH`) in `ParcelForm.tsx` and `CarForm.tsx`, then removed redundant top pills for a clean single-row selector (`e2c5554`, Anna's 17:00/17:15 fixes) | `npm run build` (0 errors); verified at 360px/375px viewports with zero currency truncation |
| **`T-09`:** *«трошки загубився на платформі»* | Mobile navbar overflowed horizontally, errors/results appeared off-screen, and the unused parcel category picker added a confusing step | Split mobile navigation into a dedicated tab bar below the header (`Navbar.tsx`, `f1666c5`, `PR #9`), removed the non-functional parcel category picker (`PR #8`, `c4bbd03`), added auto-scroll to results/errors (`App.tsx`, `PR #7`), added an interactive sender explainer card, and unified accessible modals via `ModalShell.tsx` (`54aa6d9`) | Mobile Playwright audit (320–768 px) clean with zero horizontal overflow; 82/82 UI checks passing |
| **`T-11`, `T-12` (13:55–13:58):** *«завис сайт»* (rating `1`) | Both testers hit the server during a live Docker container rebuild on `t3.micro` | Standardized releases through the `deploy` branch in `.github/workflows/ci-cd.yml` (`PR #5`, `PR #6`, `13d7b04`) with `backend` `HEALTHCHECK`, Caddy reload detection, and post-deploy HTTPS health checks | Automated `deploy` runs `44276538099`, `44340546457`, `44355562135`, `44359901645` all green |
| Legal edge-case review triggered during live testing | Testing highlighted edge cases in 2027 parcel VAT, new cars, luggage excise, and car origin | Fixed July 2027 >€150 base to `full_value` (`PR #8`), added 5% duty & `K_age = 1` for new cars (`PR #7`/`PR #8`), added the 11-item **Excise Goods in Luggage** tab (`PR #9`), and implemented `Origin × ShippedFrom` + russia import bans (`PR #10`, `6370012`) | **257** passing `pytest` tests (including `test_law_oracle.py` & `test_spec_fixtures.py`) and 25/25 `check_law_updates.py` checks |

---

## 5. Willingness to Pay & Real-World Traction (Bonus Criterion)

To validate whether users value PidKlyuch beyond polite feedback, we included a voluntary volunteer-donation modal (`DonationModal.tsx` linking to Come Back Alive, Serhiy Prytula Foundation, and Monobank) and asked about donation behavior in Q5 of the survey (`docs/feedback/responces.csv`):

| Survey Response (Q5) | Count | Share | Tester IDs |
|---|---|---|---|
| **Already donated** (*«Так, вже задонатив(ла) (надішлю/прикріплю скріншот)»*) | **3** | **20.0%** | `T-04`, `T-05`, `T-06` |
| **Willing to donate 20–100 UAH on a real order** (*«Готовий(а) задонатити 20–100 грн при реальному замовленні»*) | **11** | **73.3%** | `T-01`, `T-02`, `T-03`, `T-07`, `T-08`, `T-09`, `T-10`, `T-11`, `T-12`, `T-13`, `T-14` |
| **Not yet** (*«Поки ні»*) | **1** | **6.7%** | `T-15` |
| **Total positive (donated or willing to donate):** | **14 / 15** | **93.3%** | — |

**Transparency on Evidence & Live Usage Metrics:**

- **Donation screenshots:** While 3 respondents (`T-04`, `T-05`, `T-06`) reported having already donated, column 8 (screenshot URL) in `docs/feedback/responces.csv` was left blank and no image files were uploaded to `docs/assets/`. We therefore report **3 self-reported donations without uploaded screenshots** alongside **11 explicit commitments to donate 20–100 UAH** on real orders.
- **Production `/api/stats` snapshot (`https://16.170.212.120.sslip.io/api/stats`, 18 Nov 2026 20:55):**
  - **77** total saved calculations in PostgreSQL (**73** user calculations after subtracting **4** documented anonymous verification runs by the team);
  - **4** registered user accounts (most testers evaluated the calculator anonymously or tested before Google Sign-In was deployed);
  - **0** multi-day `returning_users` (expected within a 2-day testing window).

---

## 6. Lessons Learned

1. **Shared Context (`AGENTS.md`) Enables Multi-Agent Parallelism:** Because team members worked across different AI agents (Claude Code and Gemini CLI / Antigravity), maintaining a single source of truth in `AGENTS.md` (API contract §8, change log §12, operational runbooks §14) allowed backend, frontend, and AWS infrastructure to evolve rapidly in parallel without integration drift.
2. **Primary Legal Sources Beat Secondary Summaries:** Re-reading the enacted texts on `zakon.rada.gov.ua` uncovered critical rules that news articles glossed over — including full-value taxation for parcels > €150 starting in July 2027, `K_age = 1` for never-used vehicles regardless of manufacture year, and the postal ban on alcohol/tobacco/e-liquids. Encoding these in `tax_rates.json` with an independent law oracle (`test_law_oracle.py`) and automated clause fingerprinting (`check_law_updates.py`) prevented regressions.
3. **Deployment Stability Directly Impacts User Trust:** The two `1/5` ratings (`T-11`, `T-12`) occurred solely because testers accessed the site during a live container rebuild. Moving releases onto the gated `deploy` branch in GitHub Actions with `HEALTHCHECK` and automated HTTP verification eliminated ad-hoc manual restarts on the server.
4. **Auth Friction & Mobile Ergonomics Matter Most:** Real users immediately flagged missing Google Sign-In (`T-03`), unclear mobile currency selectors (`T-02`), and mobile navigation crowding (`T-09`) — none of which were obvious in desktop developer testing, underscoring the value of testing with external users on mobile devices.

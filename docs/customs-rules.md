# Ukrainian Customs Calculation Rules & Specification (`PidKlyuch`)

> **Owner:** Anton Vertyporokh (`docs/`)  
> **Consumer:** Liubomyr Voskalo (`backend/` calculation engine & unit tests)  
> **Status:** Active specification (2026-11-16)

---

## Overview & Precision Rules

This document is the single source of truth for all customs duty, excise, and VAT calculations performed by **PidKlyuch («Під ключ»)**. Customs calculation logic lives strictly in one backend module and must not be duplicated on the frontend.

### Monetary Precision & Rounding Conventions
1. **Never use binary floating-point types (`float` / `double`)** for money or exchange-rate calculations. Use exact decimal arithmetic (e.g., Python `decimal.Decimal` or integer minor units / cents).
2. **Base calculation currency:**
   - Statutory thresholds (e.g., €150 parcel threshold) and car excise base rates (€/1,000 cm³, €/kWh) are defined in **EUR** by Ukrainian law.
   - Official Ukrainian customs declaration settlement is performed in **UAH** converted at the official daily National Bank of Ukraine (NBU) exchange rate.
3. **Rounding rule:** Round individual tax line items (`duty`, `excise`, `vat`) to **2 decimal places using `ROUND_HALF_UP`** at tax line-item boundaries, then compute:
   - `total_tax = duty + excise + vat`
   - `total_landed_price = item_price + shipping_cost + total_tax` (for parcels) or `customs_value + total_tax` (for cars, where `customs_value` already includes delivery to the Ukrainian border).
4. **Always store and display the currency code** (`EUR`, `UAH`, `USD`, etc.) alongside every monetary value.

---

## Official Sources

| Source | Relevance | URL |
|---|---|---|
| **Customs Code of Ukraine (МКУ)** | Articles 234 (taxation of postal & express shipments), 374 (personal goods & vehicle import thresholds) | https://zakon.rada.gov.ua/laws/show/4495-17 |
| **Tax Code of Ukraine (ПКУ)** | Articles 191, 196.1.17 (parcel VAT threshold), 215.3.5-1 (car excise formulas) | https://zakon.rada.gov.ua/laws/show/2755-17 |
| **State Customs Service of Ukraine** | Official guidance on postal/express parcel clearance & passenger car import | https://customs.gov.ua |
| **State Tax Service of Ukraine** | Official VAT & excise clarifications | https://tax.gov.ua |
| **National Bank of Ukraine (NBU) API** | Official daily UAH exchange rates (JSON) | https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json |

---

## 1. Current Parcel Import Rules (Today's Rules)

**Legal basis:** Customs Code of Ukraine (МКУ) Art. 234 & Art. 374, Tax Code of Ukraine (ПКУ) Art. 196.1.17.

### 1.1 Scope & Base Value
- Applies to international postal and express shipments (**міжнародні поштові та експрес-відправлення**) addressed to an individual recipient for personal use in a single dispatch/day (up to €10,000 customs value).
- **Customs Value Base ($V_{\text{EUR}}$):** Invoice/declared value of the goods converted to **EUR** via the NBU daily rate.
- **Shipping cost ($S_{\text{EUR}}$):** For personal international postal/express parcels where freight is itemized separately on the invoice, shipping is **excluded** from the €150 duty/VAT base, though it is added to the final **Total Landed Price** paid by the buyer.

### 1.2 Threshold & Tax Rates
- **Duty-free threshold:** $T = 150.00\text{ EUR}$
- **Import Duty rate:** $10\%$ on the excess above €150
- **VAT (ПДВ) rate:** $20\%$ on $(\text{Excess} + \text{Duty})$

### 1.3 Formulas

#### Case A: $V_{\text{EUR}} \le 150.00\text{ EUR}$ (Within duty-free threshold)
$$\text{Excess}_{\text{EUR}} = 0.00$$
$$\text{Duty}_{\text{EUR}} = 0.00$$
$$\text{VAT}_{\text{EUR}} = 0.00$$
$$\text{Total Tax}_{\text{EUR}} = 0.00$$
$$\text{Total Landed Price}_{\text{EUR}} = V_{\text{EUR}} + S_{\text{EUR}}$$

#### Case B: $V_{\text{EUR}} > 150.00\text{ EUR}$ (Above duty-free threshold, $\le 10,000\text{ EUR}$)
$$\text{Excess}_{\text{EUR}} = V_{\text{EUR}} - 150.00$$
$$\text{Duty}_{\text{EUR}} = \text{round}_2(0.10 \times \text{Excess}_{\text{EUR}})$$
$$\text{VAT}_{\text{EUR}} = \text{round}_2\big(0.20 \times (\text{Excess}_{\text{EUR}} + \text{Duty}_{\text{EUR}})\big)$$
$$\text{Total Tax}_{\text{EUR}} = \text{Duty}_{\text{EUR}} + \text{VAT}_{\text{EUR}}$$
$$\text{Total Landed Price}_{\text{EUR}} = V_{\text{EUR}} + S_{\text{EUR}} + \text{Total Tax}_{\text{EUR}}$$

*(Note: Combined effective tax rate on the excess is $10\% + 20\% \times (1 + 0.10) = 32\%$ of $\text{Excess}_{\text{EUR}}$.)*

### 1.4 Pitch Consistency Check
For a parcel with goods value $V_{\text{EUR}} = 200.00\text{ EUR}$:
- $\text{Excess} = 200.00 - 150.00 = 50.00\text{ EUR}$
- $\text{Duty} = 0.10 \times 50.00 = 5.00\text{ EUR}$
- $\text{VAT} = 0.20 \times (50.00 + 5.00) = 0.20 \times 55.00 = 11.00\text{ EUR}$
- $\text{Total Tax} = 5.00 + 11.00 = \mathbf{16.00\text{ EUR}}$ ✔

---

## 2. Upcoming July 2027 Parcel Import Rules (VAT Threshold Abolition)

**Context:** Ukrainian tax reform aligning cross-border e-commerce imports with EU Council Directive 2017/2455 (IOSS / import VAT framework) and the PidKlyuch pitch specification taking effect **July 2027**.

### 2.1 Key Change vs. Today's Rules
- The **€150 VAT-free threshold is abolished**: mandatory **20% VAT** applies to **every** imported parcel starting from **€0.01**.
- Under the MVP specification, **Customs Duty (10%)** remains governed by the €150 threshold on the excess over €150 (subject to final enacted wording — see `TODO` items below).

### 2.2 Formulas (July 2027 Rules)

#### Case A: $V_{\text{EUR}} \le 150.00\text{ EUR}$
$$\text{Duty}_{2027} = 0.00$$
$$\text{VAT}_{2027} = \text{round}_2(0.20 \times V_{\text{EUR}})$$
$$\text{Total Tax}_{2027} = \text{VAT}_{2027}$$
$$\text{Total Landed Price}_{2027} = V_{\text{EUR}} + S_{\text{EUR}} + \text{Total Tax}_{2027}$$

#### Case B: $V_{\text{EUR}} > 150.00\text{ EUR}$ (up to $10,000\text{ EUR}$)
$$\text{Excess}_{\text{EUR}} = V_{\text{EUR}} - 150.00$$
$$\text{Duty}_{2027} = \text{round}_2(0.10 \times \text{Excess}_{\text{EUR}})$$
$$\text{VAT}_{2027} = \text{round}_2\big(0.20 \times (V_{\text{EUR}} + \text{Duty}_{2027})\big)$$
$$\text{Total Tax}_{2027} = \text{Duty}_{2027} + \text{VAT}_{2027}$$
$$\text{Total Landed Price}_{2027} = V_{\text{EUR}} + S_{\text{EUR}} + \text{Total Tax}_{2027}$$

*(Comparison note: For a €200.00 parcel, today's tax is `€5.00 + €11.00 = €16.00`, whereas under July 2027 rules duty stays `€5.00` and VAT jumps to `0.20 × (€200.00 + €5.00) = €41.00`, giving `€46.00` total tax — a `€30.00` increase because the initial €150 is no longer VAT-exempt.)*

### 2.3 Open Edge Cases (`TODO: Legal Verification`)
- **`TODO 1 (Legal Verification)` — Shipping inside sub-€150 VAT base:** Verify in the final enacted Verkhovna Rada bill whether international shipping ($S_{\text{EUR}}$) is included in the 20% VAT taxable base for B2C parcels $\le 150\text{ EUR}$, or whether VAT applies solely to the intrinsic value of goods ($V_{\text{EUR}}$) + duty. *MVP default:* tax $V_{\text{EUR}} + \text{Duty}_{2027}$ so the "Today vs. July 2027" comparison isolates the removal of the €150 VAT threshold cleanly.
- **`TODO 2 (Legal Verification)` — Duty threshold & C2C gifts:** Confirm whether 10% customs duty above €150 remains strictly on the excess ($V_{\text{EUR}} - 150$) or shifts to the full value above €150, and whether non-commercial C2C private gifts retain a €45 exemption threshold.

---

## 3. Currency Conversion & NBU Daily Exchange Rates

**Official source:** National Bank of Ukraine (NBU) public JSON API:
```http
GET https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json
```

Optional date parameter for deterministic lookups/debugging: `?valcode=EUR&date=YYYYMMDD&json`.

### 3.1 Response Payload Structure
Each item in the JSON array contains:
- `r030` (int): ISO 4217 numeric code (e.g., `978` for EUR, `840` for USD)
- `txt` (string): Ukrainian currency name
- `rate` (number): Official exchange rate in **UAH per 1 unit** of foreign currency
- `cc` (string): 3-letter ISO 4217 alphabetic code (`EUR`, `USD`, `PLN`, `GBP`, etc.)
- `exchangedate` (string): Effective date (`DD.MM.YYYY`)

### 3.2 Conversion Formulas
Let $\text{rate}(\text{CC})$ be the NBU official rate for currency $\text{CC}$ converted to `Decimal`, with $\text{rate}(\text{UAH}) = 1.0$.

For any input amount $A_{\text{CC}}$ in currency $\text{CC}$:
1. **Convert to UAH (statutory settlement currency):**
   $$A_{\text{UAH}} = \text{round}_2\big(A_{\text{CC}} \times \text{rate}(\text{CC})\big)$$
2. **Convert to EUR (statutory threshold & car excise currency):**
   $$A_{\text{EUR}} = \begin{cases} A_{\text{CC}}, & \text{if } \text{CC} = \text{EUR} \\ \text{round}_2\left(\dfrac{A_{\text{CC}} \times \text{rate}(\text{CC})}{\text{rate}(\text{EUR})}\right), & \text{otherwise} \end{cases}$$

*(Implementation note: Perform cross-currency conversion $\text{CC} \to \text{UAH} \to \text{EUR}$ without premature intermediate rounding if exact precision is needed, or round $A_{\text{EUR}}$ to 2 decimal places `ROUND_HALF_UP` before applying thresholds; test cases in §5 use exact terminating ratios so both orders agree.)*

### 3.3 Caching & Fallback Specification (`backend/`)
1. **Tier 1 — Live NBU Fetch + Daily Cache:** Fetch rates from the NBU endpoint (HTTP timeout $\le 3\text{ s}$) and cache them in memory + database keyed by Kyiv date (`YYYY-MM-DD`, timezone `Europe/Kyiv`), refreshing once per day (or TTL 6 hours). Return `rate_source: "nbu_live"` (or `"nbu_cached"` when served from today's fresh cache).
2. **Tier 2 — Stale DB Cache Fallback:** If the NBU API is unreachable, returns non-200, or times out, serve the most recent persisted rate snapshot from the database and return `rate_source: "nbu_stale_cache"` alongside `rate_date`.
3. **Tier 3 — Static Cold-Start Fallback:** If the NBU API fails and no database snapshot exists yet, use the static baseline constants below and return `rate_source: "fallback"` so the frontend displays a warning banner:
   - `EUR`: `45.00 UAH`
   - `USD`: `41.50 UAH`
   - `PLN`: `10.50 UAH`
   - `GBP`: `53.00 UAH`
   - `UAH`: `1.00 UAH`

---

## 4. Passenger Car Import Tax Formulas

**Legal basis:** Tax Code of Ukraine (ПКУ) Art. 215.3.5-1 (Laws #2611-VIII / #8487), Customs Code of Ukraine (МКУ).

### 4.1 Scope & Inputs
Applies to passenger vehicles (UKTZED heading `8703`) imported into Ukraine.

| Input Field | Type | Description |
|---|---|---|
| `customs_value_eur` ($V_{\text{EUR}}$) | `Decimal` | Vehicle customs value in EUR (purchase price + delivery/insurance to Ukrainian border) |
| `engine_type` | `enum` | `"petrol"` (бензин), `"diesel"` (дизель), or `"electric"` (електромобіль) |
| `engine_volume_cm3` ($E_{\text{cm3}}$) | `int` | Engine displacement in $\text{cm}^3$ (required for `petrol` and `diesel`) |
| `battery_capacity_kwh` ($B_{\text{kWh}}$) | `Decimal` | Traction battery capacity in kWh (required for `electric`) |
| `production_year` ($Y_{\text{prod}}$) | `int` | Vehicle manufacturing year (used with `current_year` $Y_{\text{curr}}$, default `2026`, to compute $K_{\text{age}}$) |

*(Note: Hybrid vehicles with an internal combustion engine are taxed under the `petrol` or `diesel` formulas using their ICE displacement $E_{\text{cm3}}$ unless classified strictly as pure electric `8703 80`.)*

### 4.2 Customs Duty (Ввізне мито)
- **Internal combustion vehicles (`petrol`, `diesel`):**
  $$\text{Duty}_{\text{EUR}} = \text{round}_2(0.10 \times V_{\text{EUR}})$$
  *(Note: Preferential EU EUR.1 certificate rates may reduce duty for qualifying EU-origin vehicles, but the statutory 10% rate is the MVP baseline used in calculations and the pitch.)*
- **Electric vehicles (`electric`, UKTZED `8703 80`):**
  $$\text{Duty}_{\text{EUR}} = 0.00$$

### 4.3 Excise Tax (Акцизний податок — ПКУ Art. 215.3.5-1)

#### Petrol & Diesel Cars
$$\text{Excise}_{\text{EUR}} = \text{round}_2\big(R_{\text{base}} \times K_{\text{engine}} \times K_{\text{age}}\big)$$

where:
1. **Engine volume coefficient ($K_{\text{engine}}$):**
   $$K_{\text{engine}} = \frac{E_{\text{cm3}}}{1000}$$
2. **Base rate ($R_{\text{base}}$ in EUR per $1000\text{ cm}^3$):**

| `engine_type` | Displacement condition | $R_{\text{base}}$ |
|---|---|---|
| `petrol` | $E_{\text{cm3}} \le 3000\text{ cm}^3$ | `50.00 EUR` |
| `petrol` | $E_{\text{cm3}} > 3000\text{ cm}^3$ | `100.00 EUR` |
| `diesel` | $E_{\text{cm3}} \le 3500\text{ cm}^3$ | `75.00 EUR` |
| `diesel` | $E_{\text{cm3}} > 3500\text{ cm}^3$ | `150.00 EUR` |

3. **Age coefficient ($K_{\text{age}}$):**  
   Statutory Ukrainian rule counts full calendar years from the year **following** manufacture up to the year of customs clearance, with a minimum of `1` (for new and 1-year-old vehicles) and a maximum cap of `15`:
   $$K_{\text{age}} = \min\Big(15,\; \max\big(1,\; Y_{\text{curr}} - Y_{\text{prod}} - 1\big)\Big)$$
   *(Deterministic API contract option: if the caller or unit test supplies `age_years` directly, apply $K_{\text{age}} = \min(15, \max(1, \text{age\_years}))$; when only `production_year` is given, use $Y_{\text{curr}} - Y_{\text{prod}} - 1$ clamped to $[1, 15]$.)*

#### Electric Vehicles (`electric`)
Statutory excise rate is **€1.00 per 1 kWh** of traction battery capacity:
$$\text{Excise}_{\text{EUR}} = \text{round}_2(1.00 \times B_{\text{kWh}})$$

### 4.4 Value Added Tax (ПДВ — 20%)
$$\text{VAT}_{\text{EUR}} = \text{round}_2\Big(0.20 \times \big(V_{\text{EUR}} + \text{Duty}_{\text{EUR}} + \text{Excise}_{\text{EUR}}\big)\Big)$$

- **EV VAT note (2026):** As of **1 January 2026**, the transitional VAT exemption for electric vehicles (ПКУ Subsection 2, Section XX, sub-clause 64) expired, so standard **20% VAT** applies to $(V_{\text{EUR}} + \text{Excise}_{\text{EUR}})$ in 2026. Historical 0% EV VAT applied only through 31 December 2025.

### 4.5 Total Tax & Total Landed Price
$$\text{Total Tax}_{\text{EUR}} = \text{Duty}_{\text{EUR}} + \text{Excise}_{\text{EUR}} + \text{VAT}_{\text{EUR}}$$
$$\text{Total Landed Price}_{\text{EUR}} = V_{\text{EUR}} + \text{Total Tax}_{\text{EUR}}$$

### 4.6 Pitch Consistency Check (`€10,000 car → €2,048–€4,640 in taxes`)
- **Lower bound (`€2,048.00`) — Electric car (`€10,000`, `40 kWh` battery):**
  - $\text{Duty} = 0.00\text{ EUR}$
  - $\text{Excise} = 1.00 \times 40 = 40.00\text{ EUR}$
  - $\text{VAT} = 0.20 \times (10000 + 0 + 40) = 2008.00\text{ EUR}$
  - $\text{Total Tax} = \mathbf{2,048.00\text{ EUR}}$ ✔
- **Mid ICE example (`€3,296.00`) — Petrol car (`€10,000`, $1600\text{ cm}^3$, $K_{\text{age}} = 1$):**
  - $\text{Duty} = 0.10 \times 10000 = 1000.00\text{ EUR}$
  - $\text{Excise} = 50 \times 1.6 \times 1 = 80.00\text{ EUR}$
  - $\text{VAT} = 0.20 \times (10000 + 1000 + 80) = 2216.00\text{ EUR}$
  - $\text{Total Tax} = \mathbf{3,296.00\text{ EUR}}$ ✔
- **Upper bound (`€4,640.00`) — Diesel car (`€10,000`, $2000\text{ cm}^3$, $K_{\text{age}} = 8$):**
  - $\text{Duty} = 0.10 \times 10000 = 1000.00\text{ EUR}$
  - $\text{Excise} = 75 \times 2.0 \times 8 = 1200.00\text{ EUR}$
  - $\text{VAT} = 0.20 \times (10000 + 1000 + 1200) = 2440.00\text{ EUR}$
  - $\text{Total Tax} = \mathbf{4,640.00\text{ EUR}}$ ✔

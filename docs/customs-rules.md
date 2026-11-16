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

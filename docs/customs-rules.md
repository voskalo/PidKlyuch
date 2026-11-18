# Ukrainian Customs Calculation Rules & Specification (`PidKlyuch`)

> **Owner:** Anton Vertyporokh (`docs/`) & Liubomyr Voskalo (`backend/app/customs/tax_rates.json`)  
> **Consumer:** Liubomyr Voskalo (`backend/` calculation engine & unit tests)  
> **Status:** Verified & Locked Specification (2026-11-17)

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
| **Customs Code of Ukraine (МКУ)** | Articles 234 & 374 p.7–8 (postal/express thresholds up to €150 and €10,000) | https://zakon.rada.gov.ua/laws/show/4495-17 |
| **Tax Code of Ukraine (ПКУ)** | Articles 14.1.49-1 (distance sales VAT), 191, 196.1.17, 215.3.5-1 (car excise) | https://zakon.rada.gov.ua/laws/show/2755-17 |
| **Laws № 5025-IX & № 5026-IX (15.10.2026)** | July 2027 parcel reform: ≤€150 → VAT 20% on the full value, no duty; P2P gifts ≤€45 VAT-free (ПКУ 197.30); **>€150 → duty 10% and VAT 20% on the FULL value** (Law 5026-IX item 19 rewrites МКУ 374 p.7; Law 5025-IX item 6 rewrites ПКУ 191.1.1) | https://zakon.rada.gov.ua/laws/show/5025-20 , https://zakon.rada.gov.ua/laws/show/5026-20 |
| **Customs Code Art. 368** | Invoice value of citizens' goods; freight/insurance are added only for unaccompanied baggage and cargo shipments, so **shipping is not counted for postal/express parcels** | https://zakon.rada.gov.ua/laws/show/4495-17 |
| **Tax Code Art. 191.1.1** | Today's VAT base for parcels of individuals: the part of the invoice value above €150 **plus the duty** | https://zakon.rada.gov.ua/laws/show/2755-17 |
| **Customs Tariff (Law № 2697-IX), heading 8703** | 10% passenger car duty; **5% for new petrol cars and new petrol hybrids > 3000 cm³** (8703 24 10 00, 8703 40 10 80, 8703 60 10 80); 0% for electric cars (8703 80 x0 10). **Not modeled:** range-extender EVs (8703 80 x0 90: 8% duty, €100 excise per TC 215.3.5-1) and new motorhomes 1500–3000 cm³ (5%). Diesel hybrids (8703 50/70) = diesel rates (10%, diesel excise) | https://zakon.rada.gov.ua/laws/show/2697б-20 |
| **EU-Ukraine Association Agreement (DCFTA)** | 0% duty for EU-origin cars in 2026 (State Customs Service letter № 15/15-03-02/20836 of 22.12.2025), only with EUR.1 / origin declaration; set per calendar year | https://www.qdpro.com.ua/goodinfo/8703239013 |
| **State Budget Law 2026 (№ 4695-IX)** | Expiry of EV 0% VAT exemption as of 01.01.2026 (standard 20% VAT applies) | https://zakon.rada.gov.ua |
| **State Customs Service of Ukraine** | Official guidance on postal/express parcel clearance & passenger car import | https://customs.gov.ua |
| **State Tax Service of Ukraine** | Official VAT & excise clarifications | https://tax.gov.ua |
| **National Bank of Ukraine (NBU) API** | Official daily UAH exchange rates (JSON) | https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json |

---

## 1. Current Parcel Import Rules (Today's Rules)

**Legal basis:** Customs Code of Ukraine (МКУ) Art. 234 & Art. 374, Tax Code of Ukraine (ПКУ) Art. 196.1.17.

### 1.1 Scope & Base Value
- Applies to non-excisable goods in international postal and express shipments (**міжнародні поштові та експрес-відправлення**) addressed to an individual recipient in a single dispatch/day (simplified regime up to **€10,000.00** customs value per МКУ Art. 374 p.7).
- **Shipments > €10,000.00 (МКУ Art. 374 p.8):** Require full commercial customs declaration at full Customs Tariff rates; the calculator still applies the baseline formula and attaches a warning note that the estimate is approximate.
- **Customs Value Base ($V_{\text{EUR}}$):** Invoice/declared value of the goods converted to **EUR** via the NBU daily rate.
- **Shipping cost ($S_{\text{EUR}}$):** For personal international postal/express parcels where freight is itemized separately on the invoice, shipping is **excluded** from the €150 duty/VAT base, though it is added to the final **Total Landed Price** paid by the buyer.
- **Exclusions:** Excisable goods (alcohol, tobacco, etc.) in parcels follow separate rules and are out of scope for the MVP parcel calculator.

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

## 2. Upcoming July 2027 Parcel Import Rules (Laws № 5025-IX & № 5026-IX)

**Legal basis:** Laws of Ukraine **№ 5025-IX** (Tax Code amendments, Art. 14.1.49-1 "distance sale of goods") and **№ 5026-IX** (Customs Code amendments, Art. 374 p.7), adopted **15.10.2026**, taking effect **no earlier than 1 July 2027** following Cabinet of Ministers implementation decision.

### 2.1 Key Change vs. Today's Rules
- **Marketplace / commercial parcels $\le €150.00$ (`sender = "marketplace"`):** The €150 VAT-free threshold is abolished; mandatory **20% VAT** applies from €0.01 (collected at checkout for distance sales), with **0% customs duty**.
- **Private C2C parcels $\le €45.00$ (`sender = "private"`):** Non-commercial shipments sent from one private individual to another remain **tax-free** (`Duty = 0.00`, `VAT = 0.00`) up to **€45.00**; private parcels between `€45.01` and `€150.00` pay **20% VAT** on $V_{\text{EUR}}$.
- **Parcels $> €150.00$:** **Changed.** Law № 5026-IX (item 19) rewrites МКУ Art. 374 p.7: "Базою оподаткування ввізним митом для таких товарів є їхня сумарна фактурна вартість" (the duty base becomes the **whole** invoice value), and Law № 5025-IX (item 6) changes ПКУ 191.1.1 from "частина сумарної фактурної вартості" to "сумарна фактурна вартість" (VAT base = whole value + duty). A €200 parcel goes from **€16** today to **€64** in tax.

### 2.2 Formulas (July 2027 Rules)

#### Case A: $V_{\text{EUR}} \le 45.00\text{ EUR}$ and `sender == "private"`
$$\text{Duty}_{2027} = 0.00, \quad \text{VAT}_{2027} = 0.00, \quad \text{Total Tax}_{2027} = 0.00$$
$$\text{Total Landed Price}_{2027} = V_{\text{EUR}} + S_{\text{EUR}}$$

#### Case B: $V_{\text{EUR}} \le 150.00\text{ EUR}$ (`sender == "marketplace"`, or `sender == "private"` with $V_{\text{EUR}} > 45.00$)
$$\text{Duty}_{2027} = 0.00$$
$$\text{VAT}_{2027} = \text{round}_2(0.20 \times V_{\text{EUR}})$$
$$\text{Total Tax}_{2027} = \text{VAT}_{2027}$$
$$\text{Total Landed Price}_{2027} = V_{\text{EUR}} + S_{\text{EUR}} + \text{Total Tax}_{2027}$$

#### Case C: $V_{\text{EUR}} > 150.00\text{ EUR}$ (up to $10,000\text{ EUR}$)
$$\text{Duty}_{2027} = \text{round}_2(0.10 \times V_{\text{EUR}})$$
$$\text{VAT}_{2027} = \text{round}_2\big(0.20 \times (V_{\text{EUR}} + \text{Duty}_{2027})\big)$$
$$\text{Total Tax}_{2027} = \text{Duty}_{2027} + \text{VAT}_{2027}$$
$$\text{Total Landed Price}_{2027} = V_{\text{EUR}} + S_{\text{EUR}} + \text{Total Tax}_{2027}$$

### 2.3 Resolved Legal Edge Cases (Locked for Backend Unit Tests)
1. **Shipping cost in the base:** Resolved — МКУ Art. 368 p.1 defines the invoice value of citizens' goods by receipts / online-shop confirmations, and p.2 adds freight and insurance **only** for unaccompanied baggage and cargo shipments. So for postal/express parcels the base ($V_{\text{EUR}}$) **excludes shipping** ($S_{\text{EUR}}$), both today and in 2027 (distance-sale VAT base = "сумарна фактурна вартість", ПКУ 191-1.3).
2. **Treatment of parcels $> €150$ and C2C gifts:** Resolved (re-verified 18.11.2026 against the enacted texts of Laws № 5025-IX / № 5026-IX) — the €45.00 VAT exemption applies only to non-commercial gifts sent **without payment** from one private person to another (ПКУ 197.30, `sender = "private"`), and for parcels $> €150.00$ the **enacted** law taxes the **whole** value (see 2.1). *(Correction: an earlier version of this document said the excess-based formula stays; that contradicted item 19 of Law № 5026-IX.)*

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
1. **Tier 1 — Live NBU Fetch + In-Memory Cache:** Fetch rates from the NBU endpoint (HTTP timeout $\le 3\text{ s}$) and cache them in memory (TTL `1 hour` in `backend/app/services/rates_service.py`, or daily `Europe/Kyiv` refresh). Return `rate_source: "nbu"`.
2. **Tier 2 — Stale Cache Fallback:** If the NBU API is unreachable, returns non-200, or times out, serve the most recent valid cached NBU rate table if present.
3. **Tier 3 — Static Cold-Start Fallback:** If the NBU API fails and no cached snapshot exists in memory, use static baseline fallback constants and return `rate_source: "fallback"` with a Ukrainian warning note so the frontend notifies the user.

---

## 4. Passenger Car Import Tax Formulas

**Legal basis:** Tax Code of Ukraine (ПКУ) Art. 215.3.5-1 (Laws #2611-VIII / #8487), Customs Code of Ukraine (МКУ).

### 4.1 Scope & Inputs
Applies to passenger vehicles (UKTZED heading `8703`) imported into Ukraine.

| Input Field | Type | Description |
|---|---|---|
| `car_price_eur` + `shipping_eur` ($V_{\text{EUR}}$) | `Decimal` | Vehicle customs value in EUR: `customs_value_eur = car_price_eur + shipping_eur` (purchase price + delivery/insurance to Ukrainian border) |
| `engine_type` | `enum` | `"petrol"` (бензин), `"diesel"` (дизель), `"hybrid"` (гібрид), or `"electric"` (електромобіль) |
| `engine_volume_cm3` ($E_{\text{cm3}}$) | `int` | Engine displacement in $\text{cm}^3$ (required for `petrol`, `diesel`, and `hybrid`) |
| `battery_capacity_kwh` ($B_{\text{kWh}}$) | `Decimal` | Traction battery capacity in kWh (required for `electric`) |
| `production_year` ($Y_{\text{prod}}$) | `int` | Vehicle manufacturing year (used with `current_year` $Y_{\text{curr}}$, default `2026`, to compute $K_{\text{age}}$) |
| `origin` | `enum` | `"other"` (standard 10% duty) or `"eu"` (0% preferential duty under DCFTA **only** with EUR.1 / origin declaration) |
| `is_new` | `bool?` | Optional. Customs Tariff "new" (never used). If omitted, a car made in the current year or later counts as new. Affects the 5% rate below and sets $K_{\text{age}} = 1$ |

*(Note: Under ПКУ Art. 215.3.5-1, spark-ignition `hybrid` vehicles have no separate flat excise rate; they pay excise by their internal combustion engine displacement $E_{\text{cm3}}$ using the `petrol` base rate. Diesel hybrids should select `engine_type = "diesel"`.)*

### 4.2 Customs Duty (Ввізне мито)
- **Internal combustion & hybrid vehicles (`petrol`, `diesel`, `hybrid`):**
  - If `origin == "other"` (standard rate, including EU-purchased non-EU-origin cars or cars without EUR.1):
    $$\text{Duty}_{\text{EUR}} = \text{round}_2(0.10 \times V_{\text{EUR}})$$
    **Exception:** a **new** `petrol` or `hybrid` car with $E_{\text{cm3}} > 3000$ pays **5%** (tariff 8703 24 10 00, 8703 40 10 80, 8703 60 10 80). New diesels and all used cars stay at 10%.
  - If `origin == "eu"` (documented EU origin via EUR.1 / origin declaration under EU-Ukraine DCFTA):
    $$\text{Duty}_{\text{EUR}} = 0.00$$
- **Electric vehicles (`electric`, UKTZED `8703 80 10 10` / `8703 90 10`):**
  $$\text{Duty}_{\text{EUR}} = 0.00 \quad (\text{regardless of origin})$$

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
   **A new (never used) car always has $K_{\text{age}} = 1$, whatever its production year** — TC 215.3.5-1: "для нових транспортних засобів … коефіцієнт дорівнює 1" (e.g. an unsold 2022 car cleared in 2026: $K_{\text{age}} = 1$, not 3).
   *(Deterministic API contract option: if the caller or unit test supplies `age_years` directly, apply $K_{\text{age}} = \min(15, \max(1, \text{age\_years}))$; when only `production_year` is given, use $Y_{\text{curr}} - Y_{\text{prod}} - 1$ clamped to $[1, 15]$.)*

#### Electric Vehicles (`electric`)
Statutory excise rate is **€1.00 per 1 kWh** of traction battery capacity:
$$\text{Excise}_{\text{EUR}} = \text{round}_2(1.00 \times B_{\text{kWh}})$$

### 4.4 Value Added Tax (ПДВ — 20%)
$$\text{VAT}_{\text{EUR}} = \text{round}_2\Big(0.20 \times \big(V_{\text{EUR}} + \text{Duty}_{\text{EUR}} + \text{Excise}_{\text{EUR}}\big)\Big)$$

- **EV VAT note (2026):** As of **1 January 2026**, the transitional VAT exemption for electric vehicles (ПКУ Subsection 2, Section XX, sub-clause 64) expired, so standard **20% VAT** applies to $(V_{\text{EUR}} + \text{Excise}_{\text{EUR}})$ in 2026. Historical 0% EV VAT applied only through 31 December 2025.

### 4.5 Total Tax, Landed Price & Exclusions
$$\text{Total Tax}_{\text{EUR}} = \text{Duty}_{\text{EUR}} + \text{Excise}_{\text{EUR}} + \text{VAT}_{\text{EUR}}$$
$$\text{Total Landed Price}_{\text{EUR}} = V_{\text{EUR}} + \text{Total Tax}_{\text{EUR}}$$

*(Not included in customs tax total: Pension Fund levy on first registration in Ukraine (3–5%), vehicle certification, and customs broker fees.)*

### 4.6 Pitch Consistency Check (`€10,000 car → €2,048–€4,640 in taxes`)
- **Lower bound (`€2,048.00`) — Electric car (`€10,000`, `40 kWh` battery) OR new EU-origin 0.8L petrol (`origin="eu"`, $K_{\text{age}}=1$):**
  - $\text{Duty} = 0.00\text{ EUR}$
  - $\text{Excise} = 40.00\text{ EUR}$ (`1.00 × 40 kWh`, or `50 × 0.8 × 1`)
  - $\text{VAT} = 0.20 \times (10000 + 0 + 40) = 2008.00\text{ EUR}$
  - $\text{Total Tax} = \mathbf{2,048.00\text{ EUR}}$ ✔
- **Mid ICE example (`€3,296.00`) — Non-EU petrol car (`€10,000`, $1600\text{ cm}^3$, $K_{\text{age}} = 1$):**
  - $\text{Duty} = 0.10 \times 10000 = 1000.00\text{ EUR}$
  - $\text{Excise} = 50 \times 1.6 \times 1 = 80.00\text{ EUR}$
  - $\text{VAT} = 0.20 \times (10000 + 1000 + 80) = 2216.00\text{ EUR}$
  - $\text{Total Tax} = \mathbf{3,296.00\text{ EUR}}$ ✔
- **Upper bound (`€4,640.00`) — Non-EU diesel (`€10,000`, $2000\text{ cm}^3$, $K_{\text{age}} = 8$) OR 2013 non-EU petrol (`€10,000`, $2000\text{ cm}^3$, $K_{\text{age}} = 12$):**
  - $\text{Duty} = 0.10 \times 10000 = 1000.00\text{ EUR}$
  - $\text{Excise} = 1200.00\text{ EUR}$ (`75 × 2.0 × 8`, or `50 × 2.0 × 12`)
  - $\text{VAT} = 0.20 \times (10000 + 1000 + 1200) = 2440.00\text{ EUR}$
  - $\text{Total Tax} = \mathbf{4,640.00\text{ EUR}}$ ✔

---

## 5. Worked Test Cases (`TC-P1` – `TC-P5`, `TC-C1` – `TC-C5`)

All 10 test cases below use a deterministic reference NBU rate fixture so unit tests can run offline with exact decimal equality:
- `EUR = 45.00 UAH`
- `USD = 41.40 UAH` (cross-rate: `1 USD = 0.92 EUR`)
- `UAH = 1.00 UAH`
- `current_year = 2026` (for car age calculation)

### 5.1 Parcel Test Cases (Current Rules vs. July 2027 Rules, `sender = "marketplace"`)

*(Note: Under July 2027 Laws № 5025-IX / № 5026-IX, parcels `≤ €150` pay 20% VAT on `goods_value_eur` (private P2P gifts `≤ €45` exempt), and parcels `> €150` pay 10% duty and 20% VAT on the **full** value instead of only the excess.)*

| ID | Description | Input (`item_price`, `shipping`, `currency`) | Current Rules (`duty`, `vat`, `total_tax`, `landed_eur`) | July 2027 Rules (`duty`, `vat`, `total_tax`, `landed_eur`) |
|---|---|---|---|---|
| **TC-P1** | Under €150 threshold | `120.00`, `15.00`, `EUR` | `0.00`, `0.00`, **`0.00`**, `135.00` (`6075.00 UAH`) | `0.00`, `24.00`, **`24.00`**, `159.00` (`7155.00 UAH`) |
| **TC-P2** | Exact €150 boundary | `150.00`, `10.00`, `EUR` | `0.00`, `0.00`, **`0.00`**, `160.00` (`7200.00 UAH`) | `0.00`, `30.00`, **`30.00`**, `190.00` (`8550.00 UAH`) |
| **TC-P3** | Pitch benchmark (€200) | `200.00`, `20.00`, `EUR` | `5.00`, `11.00`, **`16.00`**, `236.00` (`10620.00 UAH`) | `20.00`, `44.00`, **`64.00`**, `284.00` (`12780.00 UAH`) |
| **TC-P4** | USD conversion (`$300` → `€276`) | `300.00`, `25.00`, `USD` | `12.60`, `27.72`, **`40.32`**, `339.32` (`15269.40 UAH`) | `27.60`, `60.72`, **`88.32`**, `387.32` (`17429.40 UAH`) |
| **TC-P5** | High-value parcel (€1,000) | `1000.00`, `40.00`, `EUR` | `85.00`, `187.00`, **`272.00`**, `1312.00` (`59040.00 UAH`) | `100.00`, `220.00`, **`320.00`**, `1360.00` (`61200.00 UAH`) |

### 5.2 Passenger Car Test Cases (`current_year = 2026`, `origin = "other"`)

| ID | Description | Input (`customs_value_eur`, `engine_type`, `volume_cm3` / `kwh`, `production_year`, `K_age`) | `duty_eur` | `excise_eur` | `vat_eur` | `total_tax_eur` (`total_tax_uah`) | `total_landed_eur` (`total_landed_uah`) |
|---|---|---|---|---|---|---|---|
| **TC-C1** | Pitch lower bound EV | `10000.00`, `electric`, `40 kWh`, `2022` (`3`) | `0.00` | `40.00` | `2008.00` | **`2048.00`** (`92160.00 UAH`) | `12048.00` (`542160.00 UAH`) |
| **TC-C2** | Standard petrol (1.6L, $K_{\text{age}}=1$) | `10000.00`, `petrol`, `1600 cm³`, `2024` (`1`) | `1000.00` | `80.00` | `2216.00` | **`3296.00`** (`148320.00 UAH`) | `13296.00` (`598320.00 UAH`) |
| **TC-C3** | Pitch upper bound diesel (2.0L, 8yo) | `10000.00`, `diesel`, `2000 cm³`, `2017` (`8`) | `1000.00` | `1200.00` | `2440.00` | **`4640.00`** (`208800.00 UAH`) | `14640.00` (`658800.00 UAH`) |
| **TC-C4** | Large petrol (`>3000 cm³`, `R=100`) | `15000.00`, `petrol`, `3500 cm³`, `2020` (`5`) | `1500.00` | `1750.00` | `3650.00` | **`6900.00`** (`310500.00 UAH`) | `21900.00` (`985500.00 UAH`) |
| **TC-C5** | Old large diesel (`>3500 cm³`, age cap 15) | `8000.00`, `diesel`, `4000 cm³`, `2007` (`18→15`) | `800.00` | `9000.00` | `3560.00` | **`13360.00`** (`601200.00 UAH`) | `21360.00` (`961200.00 UAH`) |

### 5.3 Structured Fixture Data (JSON for Backend Unit Tests)

```json
{
  "nbu_test_rates_uah": {
    "EUR": "45.00",
    "USD": "41.40",
    "UAH": "1.00"
  },
  "current_year": 2026,
  "parcel_cases": [
    {
      "id": "TC-P1",
      "input": { "item_price": "120.00", "shipping_cost": "15.00", "currency": "EUR", "sender": "marketplace" },
      "expected": {
        "item_value_eur": "120.00",
        "shipping_eur": "15.00",
        "current_rules": { "excess_eur": "0.00", "duty_eur": "0.00", "vat_eur": "0.00", "total_tax_eur": "0.00", "total_tax_uah": "0.00", "total_landed_eur": "135.00", "total_landed_uah": "6075.00" },
        "july_2027_rules": { "duty_base_eur": "0.00", "duty_eur": "0.00", "vat_eur": "24.00", "total_tax_eur": "24.00", "total_tax_uah": "1080.00", "total_landed_eur": "159.00", "total_landed_uah": "7155.00" }
      }
    },
    {
      "id": "TC-P2",
      "input": { "item_price": "150.00", "shipping_cost": "10.00", "currency": "EUR", "sender": "marketplace" },
      "expected": {
        "item_value_eur": "150.00",
        "shipping_eur": "10.00",
        "current_rules": { "excess_eur": "0.00", "duty_eur": "0.00", "vat_eur": "0.00", "total_tax_eur": "0.00", "total_tax_uah": "0.00", "total_landed_eur": "160.00", "total_landed_uah": "7200.00" },
        "july_2027_rules": { "duty_base_eur": "0.00", "duty_eur": "0.00", "vat_eur": "30.00", "total_tax_eur": "30.00", "total_tax_uah": "1350.00", "total_landed_eur": "190.00", "total_landed_uah": "8550.00" }
      }
    },
    {
      "id": "TC-P3",
      "input": { "item_price": "200.00", "shipping_cost": "20.00", "currency": "EUR", "sender": "marketplace" },
      "expected": {
        "item_value_eur": "200.00",
        "shipping_eur": "20.00",
        "current_rules": { "excess_eur": "50.00", "duty_eur": "5.00", "vat_eur": "11.00", "total_tax_eur": "16.00", "total_tax_uah": "720.00", "total_landed_eur": "236.00", "total_landed_uah": "10620.00" },
        "july_2027_rules": { "duty_base_eur": "200.00", "duty_eur": "20.00", "vat_eur": "44.00", "total_tax_eur": "64.00", "total_tax_uah": "2880.00", "total_landed_eur": "284.00", "total_landed_uah": "12780.00" }
      }
    },
    {
      "id": "TC-P4",
      "input": { "item_price": "300.00", "shipping_cost": "25.00", "currency": "USD", "sender": "marketplace" },
      "expected": {
        "item_value_eur": "276.00",
        "shipping_eur": "23.00",
        "current_rules": { "excess_eur": "126.00", "duty_eur": "12.60", "vat_eur": "27.72", "total_tax_eur": "40.32", "total_tax_uah": "1814.40", "total_landed_eur": "339.32", "total_landed_uah": "15269.40" },
        "july_2027_rules": { "duty_base_eur": "276.00", "duty_eur": "27.60", "vat_eur": "60.72", "total_tax_eur": "88.32", "total_tax_uah": "3974.40", "total_landed_eur": "387.32", "total_landed_uah": "17429.40" }
      }
    },
    {
      "id": "TC-P5",
      "input": { "item_price": "1000.00", "shipping_cost": "40.00", "currency": "EUR", "sender": "marketplace" },
      "expected": {
        "item_value_eur": "1000.00",
        "shipping_eur": "40.00",
        "current_rules": { "excess_eur": "850.00", "duty_eur": "85.00", "vat_eur": "187.00", "total_tax_eur": "272.00", "total_tax_uah": "12240.00", "total_landed_eur": "1312.00", "total_landed_uah": "59040.00" },
        "july_2027_rules": { "duty_base_eur": "1000.00", "duty_eur": "100.00", "vat_eur": "220.00", "total_tax_eur": "320.00", "total_tax_uah": "14400.00", "total_landed_eur": "1360.00", "total_landed_uah": "61200.00" }
      }
    }
  ],
  "car_cases": [
    {
      "id": "TC-C1",
      "input": { "car_price": "10000.00", "shipping_price": "0.00", "currency": "EUR", "engine_type": "electric", "battery_capacity_kwh": "40", "production_year": 2022, "origin": "other" },
      "expected": { "k_age": 3, "duty_eur": "0.00", "excise_eur": "40.00", "vat_eur": "2008.00", "total_tax_eur": "2048.00", "total_tax_uah": "92160.00", "total_landed_eur": "12048.00", "total_landed_uah": "542160.00" }
    },
    {
      "id": "TC-C2",
      "input": { "car_price": "10000.00", "shipping_price": "0.00", "currency": "EUR", "engine_type": "petrol", "engine_volume_cm3": 1600, "production_year": 2024, "origin": "other" },
      "expected": { "k_age": 1, "duty_eur": "1000.00", "excise_eur": "80.00", "vat_eur": "2216.00", "total_tax_eur": "3296.00", "total_tax_uah": "148320.00", "total_landed_eur": "13296.00", "total_landed_uah": "598320.00" }
    },
    {
      "id": "TC-C3",
      "input": { "car_price": "10000.00", "shipping_price": "0.00", "currency": "EUR", "engine_type": "diesel", "engine_volume_cm3": 2000, "production_year": 2017, "origin": "other" },
      "expected": { "k_age": 8, "duty_eur": "1000.00", "excise_eur": "1200.00", "vat_eur": "2440.00", "total_tax_eur": "4640.00", "total_tax_uah": "208800.00", "total_landed_eur": "14640.00", "total_landed_uah": "658800.00" }
    },
    {
      "id": "TC-C4",
      "input": { "car_price": "15000.00", "shipping_price": "0.00", "currency": "EUR", "engine_type": "petrol", "engine_volume_cm3": 3500, "production_year": 2020, "origin": "other" },
      "expected": { "k_age": 5, "duty_eur": "1500.00", "excise_eur": "1750.00", "vat_eur": "3650.00", "total_tax_eur": "6900.00", "total_tax_uah": "310500.00", "total_landed_eur": "21900.00", "total_landed_uah": "985500.00" }
    },
    {
      "id": "TC-C5",
      "input": { "car_price": "8000.00", "shipping_price": "0.00", "currency": "EUR", "engine_type": "diesel", "engine_volume_cm3": 4000, "production_year": 2007, "origin": "other" },
      "expected": { "k_age": 15, "duty_eur": "800.00", "excise_eur": "9000.00", "vat_eur": "3560.00", "total_tax_eur": "13360.00", "total_tax_uah": "601200.00", "total_landed_eur": "21360.00", "total_landed_uah": "961200.00" }
    }
  ]
}
```

---

## 6. Excise Goods (alcohol, tobacco, e-liquids, fuel) — added 18.11.2026 (Liubomyr)

- **Not in parcels:** Customs Code art. 235 p.1 items 6–7 ban alcohol, tobacco and other UKTZED chapter 1–24 goods (except
  food ≤ 10 kg) in postal and express items to private persons, regardless of value. Art. 234 p.6: excise goods that may
  be sent are taxed regardless of value (no €150 threshold). Fuel is a dangerous good under UPU rules.
- **In luggage (what the calculator models, `delivery_type: "excise"`):** duty-free per adult (art. 376 p.2): 5 l beer,
  2 l wine, 1 l spirits > 22 %, 200 cigarettes or 50 cigars or 250 g tobacco; fuel: tank + 20 l canister (art. 374 p.10
  item 12). Abroad < 24 h: no alcohol/tobacco allowance (art. 376 p.3). Above the norm, only the excess is taxed:

$$\text{Duty} + \text{Excise} + \text{VAT}_{20\%}(V_{\text{excess}} + \text{Duty} + \text{Excise}),\quad V_{\text{excess}} = V \times \frac{Q - Q_{\text{norm}}}{Q}$$

| Kind | Duty (Customs Tariff, preferential) | Excise 2026 (TC) |
|---|---|---|
| Beer | €0.05 / l | 59.82 UAH per l of 100 % alcohol |
| Still wine | €0.3 / l | 0.01 UAH / l |
| Sparkling wine | €1.5 / l | 12.23 UAH / l |
| Spirits > 22 % | 0 | 133.31 UAH per l of 100 % alcohol |
| Cigarettes | €1.5 / 1000 | €61 / 1000 + 12 % of price, min €82 / 1000 |
| Cigars | 10 % | €77 / kg |
| Smoking / hookah tobacco | 20 % | €77 / kg |
| Heated tobacco sticks | €1.8 / kg | €70.8 / 1000 |
| E-liquid | 3 % | €300 / l |
| Petrol | 10 % (≥ 5 % bio components) | €300.8 / 1000 l |
| Diesel | 0 | €253.8 / 1000 l |

Worked examples (1 EUR = 50 UAH, `backend/tests/test_excise.py`): 2 l whisky 40 %, €60 → 1 l taxed: duty 0, excise
133.31 × 0.4 / 50 = €1.07, VAT 20 % × (30 + 0 + 1.07) = €6.21, **total €7.28**; 400 cigarettes, €12 → 200 taxed:
duty €0.30, excise max(61 × 0.2 + 12 % × 6; 82 × 0.2) = €16.40, VAT €4.54, **total €21.24**.


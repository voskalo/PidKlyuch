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

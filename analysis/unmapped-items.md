# Unmapped Items

> ⚠ **SUPERSEDED (2026-08-12)** — Kingspan added 13 Power BI Dataflow tables **and** enriched the Datasphere Billing / SalesOrders views. The forecast-measure blocker (Billing `ISO Rate Fcst IS`, `Sum Fcst Sales in FT2 for Membranes`) is now **resolved** via `Billing[ISO_Rate_Forecast]`, `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` (native columns) and the standalone `KRW_NA_FF_FORECAST_INTAKE` dataflow.
>
> Also resolved: nearly all of the "Fields referenced in visuals but NOT in SAP Datasphere" section below — the fields now exist as native `Billing` / `SalesOrders` columns (Application, Industry, Sales_Representative_T, Project_Coordinator_T, ProjectName, CustomerFullName, Territory_Name × 4, Material_D17_T, NetSlsCostAmount, Gross_Margin, Margin_Percent) or via dataflow tables.
>
> **Read [`recovered-missing-fields.md`](recovered-missing-fields.md), [`dataflow-production-crosswalk.md`](dataflow-production-crosswalk.md), and [`still-missing-after-dataflows.md`](still-missing-after-dataflows.md) for the current status.** This file is kept for historical context only.

## ⚠ Forecast measures — NOT FOUND in RL data model

**Verified 2026-08-10 via DAX diagnostic queries.**

The following 4 production measures cannot be reproduced faithfully from `SAP_SD_RL_*` because RL stores forecast data on separate rows that carry no product-family classification.

### Evidence

`SUMMARIZECOLUMNS(Billing[FC_Product_Group], Billing[Product_Family], Billing[MaterialGroup], ...)` filtered to forecast rows returns:

| FC_Product_Group | Product_Family | MaterialGroup | Rows | Fcst SQFT | Fcst BDFT |
|---|---|---|---|---|---|
| (blank) | (blank) | (blank) | 43 | 13,538,375 | 16,384,476 |

All 78 forecast-carrying rows have `FC_Product_Group = blank`; 43 also have `Product_Family` and `MaterialGroup` blank. Production HL apparently populated `FC Product Group` on forecast rows, but RL does not.

### Blocked measures (revised 2026-08-10 after Phase 7 verification)

| Measure | DAX pattern | Returns in RL | Status |
|---|---|---|---|
| `Sum Fcst Sales in FT2 for Membranes` (Billing) | SUMX(FILTER(rows where FC_Product_Group contains "TPO"), ForecastSalesSQFT) | **0** | **BLOCKED** — Billing forecast rows have `FC_Product_Group = blank` |
| `ISO Rate Fcst IS` (Billing) | DIVIDE(SUM(ForecastSalesBDFT), [Sum Fcst Sales in FT2 for Membranes]) → divides by 0 | **0** | **BLOCKED** — depends on measure above |
| `Sum Fcst Order Qty. in FT2 for Membranes OI` (SalesOrders) | Same DAX pattern on Sales side | **~5M (non-zero)** | ✅ **WORKS** — Sales forecast rows DO carry FC_Product_Group |
| `ISO Rate Fcst OI` (SalesOrders) | Same | **2.63** | ✅ **WORKS** |

**Revised: only 2 of 4 forecast measures blocked** (both on Billing/Invoiced Sales side). Sales/Order Intake side forecast measures work correctly because the SalesOrders RL view properly classifies forecast rows with `FC_Product_Group`. This is a **Billing RL view design gap**, not a general RL limitation.

17 of 19 production measures reproduce correctly (verified live values from Phase 7 pages: `ISO Rate IS = 0.91`, `ISO Rate OI = 1.61`, `ISO Rate SB = 0.59`, `ISO Rate Fcst OI = 2.63`, `Total Backlog $ = $173,169`).

### Options for resolution (business decision required — narrowed after Phase 7)

Only 2 Billing forecast measures are affected. Order-Intake forecast side already works.

1. **Ask Ana / James: why does the Billing RL view drop `FC_Product_Group` on forecast rows** when the Sales RL view keeps it? This is likely a fixable Datasphere modelling issue rather than a fundamental data-availability problem. The fix on the Datasphere side would automatically enable `ISO Rate Fcst IS` and `Sum Fcst Sales in FT2 for Membranes` without any DAX change.
2. **Accept the divergence** — display "0" for the 2 Billing-side forecast measures. Order Intake side displays correctly.
3. **Deviate from production DAX** — rewrite Billing forecast measures without the product-family filter (total forecast BDFT / total forecast SQFT). Produces a real number for AWIP data but is *not* the same concept as production. **Not recommended** without business sign-off.

### Scope for Phase 7 (report rebuild) — outcome

- **Invoiced Sales - Dashboard:** ISO Rate Fcst tile displays `0.00`. Confirmed with live data. Note in the tile title that data is pending Billing RL forecast-classification fix.
- **Order Intake - Dashboard:** ISO Rate Fcst OI tile displays `2.63` — works correctly, no action needed.
- Fcst gauge MaxValue references (deferred to Phase 7.5) use raw column totals (`SUM(ForecastSalesBDFT)`, `SUM(ForecastSalesSQFT)`), which return non-zero on both Billing and Sales sides, so gauges will render correctly on both dashboards.

---



Items that appear in production but have no confirmed equivalent in the new Billing/Sales Datasphere sources. Follows the Phase 3 rule: **do not create artificial replacements.**

## Fields referenced in visuals but NOT in SAP Datasphere

| Field | Where used | Production source | New source | Action |
|---|---|---|---|---|
| `Account Assignment Group Description` | AAGC slicer (Invoiced Sales Dashboard) | KNVV.csv | NOT FOUND in RL | Confirm KNVV strategy with owner |
| `Sales Representative` (as name) | Invoiced Sales detail table | Customer.xlsx | NOT FOUND | Same |
| `Project Coordinator` | Invoiced Sales detail table | Customer.xlsx | NOT FOUND | Same |
| `ProjectName` / `Customer Project Name` | Invoiced Sales detail table | Customer.xlsx | NOT FOUND | Same |
| `Material Description` | Invoiced Sales detail table | Customer.xlsx | NOT FOUND | Same |
| `Industry` | Not confirmed on inventoried pages; likely Extended pages | Customer.xlsx | NOT FOUND | Confirm scope |
| `Company Type` | Not confirmed | Customer.xlsx | NOT FOUND | Same |
| `Application` | Not confirmed on inventoried pages | Customer.xlsx | RL has `Application_Product_Number` — **semantics unverified** | Verify with owner if these are the same field |
| `Secondary Grouping` | Not confirmed | Customer.xlsx | NOT FOUND | Same |
| `Territory Sold-to / Ship-to / Bill-to / Payer` | Not confirmed | Customer.xlsx | NOT FOUND | Same |
| `Sold to party Description` (customer name) | Not confirmed | Customer.xlsx | NOT FOUND (SAP KNA1 not in RL) | Same |
| `Cost of sales` | Not confirmed | Customer.xlsx | NOT FOUND | Same |
| `Gross Margin` / `Gross margin %` | Not confirmed | Customer.xlsx | NOT FOUND | Same |

## Fields with multiple RL variants — canonical choice unclear

| Production HL field | RL candidates | Notes |
|---|---|---|
| `Plant` | `Plant`, `Plant_D2`, `Plant_D2_T`, `Plant_A_2`, `PlantCategory` | Plain `Plant` if present is likely correct; `_D2` = dimension key form. Verify which one Kingspan considers canonical. |
| `Country` | `Country`, `Country1..Country6` (variants exist for sold-to, ship-to, bill-to, payer, etc.) | Sold-to country is business default. Verify. |
| `Region` | `Region`, `Region1..Region3` | Same |
| `Material` | `Material`, `Material_D17` | `_D17` is dimension key form. |
| `SalesOrganization` | `SalesOrganization2`, `SalesOrganization_D13`, `SalesOrganization_D13_T` | `_D13` is dimension key (used in existing M query parameter). |
| `Division` | `Division`, `Division2`, `Division_Product_Number` (+ `_T` versions) | Plain `Division` most likely. |
| `Product Family` | `Product_Family_Product_Number` | RL only has the `_Product_Number` variant — check if the value domain (Membrane, iso) is identical to production's plain `Product Family`. |
| `BaseUnit` | `BaseUnit`, `BaseUnit1` | Unclear why RL has two. |
| `Fiscal_Month` | verify in Sales.tmdl | Not in the grep for Billing; need to check |

**Recommendation for Phase 3–5:** for each ambiguous field, pull a sample of DISTINCT values via `SELECT DISTINCT column FROM table` and compare against production values. Only after value-domain match confirmed can we upgrade POSSIBLE to STRONG or EXACT.

## Report content NOT yet fully inventoried

The following pages had visual counts but not per-visual field-level inventory (out of Phase 1 scope for the first pass):

- Extended Invoiced Sales - Dashboard (14 visuals)
- Extended Order Intake - Dashboard (16 visuals)
- Backlog (11 visuals) — beyond the confirmed page-level filter
- Backlog - Details (5 visuals)
- Backlog by Rep (7 visuals)
- Invoiced Sales - Detail (6 visuals) — 2 confirmed, 4 remaining
- Order Intake - Detail (7 visuals) — 1 confirmed, 6 remaining
- Order Intake - Dashboard (16 visuals) — 1 confirmed, 15 remaining

If these pages use Customer.xlsx fields (Application, Sales Rep, Cost/GM, etc.) or Salesforce Quote data, they will be blocked by the external-source resolutions.

**Recommendation:** if any of the Extended / Backlog pages are in scope for reproduction, run a second Explore pass focused on those specific pages to enumerate their field usage before starting Phase 5 rebuild.

## Report content whose external source can't be assumed

- **Kingspan logo image** (`kingspan-roofing-waterproofing8422940714883275.png`) — embedded in production Report/StaticResources/RegisteredResources. Must be copied into new project to reproduce branding.
- **Report theme `CY26SU05`** — Power BI July 2026 built-in theme. No custom JSON needed.

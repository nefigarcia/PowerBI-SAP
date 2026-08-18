# Phase 6 — Deep Dive: Calendar/Fiscal, Forecast, Geography

## 6a. Calendar / Fiscal group

### Tables involved in dev
- `KRW_NA_FF_CALENDAR` — dataflow, one row per day, columns include `Date` (dateTime), `Calendar Date` (string), `Year`, `Month`, `Month Name`, `Day of Week`, `Day Name`, `Start of Month`, `End of Month`, `Year Month`, `Current Month`, `Month Type`, `Subtraction`.
- `KRW_NA_FF_FISCALPERIOD` — dataflow, columns `Calendar Date` (string), `Fiscal Year`, `Fiscal Period`, `Fiscal Year Period` (all strings). Grain: one row per day (or per calendar date/fiscal period combination). Bi-di join on `Calendar Date` string to CALENDAR.
- `Fiscal Period Selector` — calculated table `DISTINCT(SELECTCOLUMNS(Billing, "FiscalYearPeriod", Billing[FiscalYearPeriod]))`. Format: `YYYYPPP` e.g. `2026007`. Used as the primary user-facing fiscal-period slicer.
- `DimDate` — calculated table `CALENDAR(2020-01-01 … 2030-12-31)`. Was created before the FF calendar was imported; duplicate architecture.

### Production analog
- Prod has `KRW_NA_FF_CALENDAR` + `OI` + `SB` role-play copies.
- Prod has `KRW_NA_FF_FISCALPERIOD` + `OI` + `SB` role-play copies.
- Prod has `FiscalYearPeriods Slicer` + `OI` + `SB` role-play copies.
- Role-plays exist because production is 3 AAS cubes stitched together.

### Decision
- **Dev needs only single copies** — no OI/SB variants. The two OData facts (Billing, SalesOrders) with USERELATIONSHIP handle all three date semantics (Billing Date on Billing, Creation Date on SalesOrders active, Requested Delivery Date on SalesOrders inactive role-play).
- **`DimDate` is redundant.** All Billing/SalesOrders date filters should route through `KRW_NA_FF_CALENDAR`. `Fiscal Period Selector` is the user slicer.
- **Deletion order (Phase 12):** deactivate DimDate relationships → verify no measure references `DimDate[Year]` / `DimDate[MonthName]` / etc. → delete DimDate.

### Filter propagation chain (target)
```
Fiscal Period Selector[FiscalYearPeriod] ──▶ Billing (via direct filter in measures)
Fiscal Period Selector[FiscalYearPeriod] ◀──▶ KRW-NA_FF_FORECAST[Fiscal Year Period Billing Format]  (bothDir)
Fiscal Period Selector[FiscalYearPeriod] ◀──▶ KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Billing Format]  (bothDir — NEW)

KRW_NA_FF_FISCALPERIOD ◀──▶ KRW_NA_FF_CALENDAR  (bothDir on Calendar Date)
KRW_NA_FF_CALENDAR[Date] ──▶ Billing[BillingDocumentDate_D5]  (single, active)
KRW_NA_FF_CALENDAR[Date] ──▶ SalesOrders[CreationDate_D8]  (single, active)
KRW_NA_FF_CALENDAR[Date] ──▶ SalesOrders[RequestedDeliveryDate_dt]  (single, INACTIVE role-play)
```

This chain reproduces production behavior: selecting a period in the Fiscal Period Selector filters Billing directly and filters SalesOrders via CALENDAR (since the reverse-direction FISCALPERIOD↔CALENDAR bothDir enables the propagation).

---

## 6b. Forecast group

### Tables
- `KRW-NA_FF_FORECAST` — dataflow, columns `Period`, `Year`, `Sales $`, `Sales Membrane sqft`, `Sales ISO sqft`, `Sales ISO bdft`, `Fiscal Year Period`, `Fiscal Year Period Sorted`, `Fiscal Year Period Billing Format` (calculated). Grain: one row per period per forecast dimension. Holds 8 INVOICED-side measures. Bridged to `Fiscal Period Selector` via the calculated column.
- `KRW_NA_FF_FORECAST_INTAKE` — dataflow, same column shape (Period, Year, Sales $, Sales Membrane sqft, Sales ISO sqft, Sales ISO bdft, Fiscal Year Period, Fiscal Year Period Sorted). **No bridge column yet.** Holds 9 SORDERS-side measures.

### Production analog
- Prod: FORECAST ↔ FiscalYearPeriods Slicer (bothDir, on `Fiscal Year Period 2` = `Fiscal Year Period`).
- Prod: FORECAST_INTAKE ↔ FiscalYearPeriods Slicer OI (bothDir, on `Fiscal Year Period`).

### Findings
- The FORECAST table already has its bridge column and relationship.
- **FORECAST_INTAKE is missing the bridge**. Symptom: the SalesOrders-side forecast measures cannot be filtered by the Fiscal Period Selector; they return grand totals regardless of user selection. This is a known-broken behavior documented in the ISO Rate investigation status.
- SO_INTAKE-side measures (`Current Fiscal Month Sales Membrane sqft`, `Current Fiscal Month Sales ISO sqft/bdft`) use `[Current FYP VBAP OI]` which reads FISCALPERIOD, so those specific measures work — but any visual that slices FORECAST_INTAKE by the Fiscal Period Selector directly is broken.

### Fix (Phase 7)
1. Add calculated column `Fiscal Year Period Billing Format` to `KRW_NA_FF_FORECAST_INTAKE`.
2. Create bothDir relationship: `Fiscal Period Selector[FiscalYearPeriod]` ↔ `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Billing Format]`.

---

## 6c. Geography group

### Tables
- `KRW_NA_FF_GEOINFO` — Country, Code, State, Latitude, Longitude, COUNTRY_REGION. Grain: appears to be one row per country/state combination (state within country).
- `KRW_NA_FF_TERRITORY` — territory master (Kingspan-defined sales territories). Not currently in relationships.
- `KRW_NA_FF_ZIPCODES` — zip-to-territory mapping. Not currently in relationships.

### Production analog
- Prod: `KNA1.COUNTRY_REGION → GEOINFO.COUNTRY_REGION` on customer master, plus OI and SB variants.
- Prod does NOT use TERRITORY or ZIPCODES in relationships.

### Findings
- Prod joins customer→geo on a COUNTRY_REGION composite key. Dev joins fact→geo directly on `State_Name → State`. **These are semantically similar but not identical.**
- The `State` join works when State values are unique within the dataset (which they usually are in a US-centric dataset with 50 states + a few territories) but fails if the FF_GEOINFO dataflow returns multiple rows per state (e.g., "TX" appearing under both USA and Mexico).
- `KRW_NA_FF_TERRITORY` and `KRW_NA_FF_ZIPCODES` are present in dev but not related. They may be intended for a Kingspan-specific territory report page not covered by production. **Leave disconnected — flag in Phase 12 if they should be removed.**

### Path from geography to sales
```
Current dev (kept, simplified from prod):
  KRW_NA_FF_GEOINFO[State] ──▶ Billing[State_Name]      (single)
  KRW_NA_FF_GEOINFO[State] ──▶ SalesOrders[State_Name]  (single)

Production (more precise):
  GEOINFO[COUNTRY_REGION] ──▶ KNA1[COUNTRY_REGION] ──▶ VBRP[Sold To]
```

### Decision
Keep dev's `State` join. Flag potential grain issue for Phase 11 (Ana confirmation). Recommend adding a `COUNTRY_REGION` calculated column bridge only if a Phase 9 filter propagation test reveals wrong totals in geographic slicers.

---

## 6d. Other existing dev FF tables (leave disconnected, document)

| Table | Purpose | Relationship in dev | Relationship in prod | Action |
|---|---|---|---|---|
| `CAPEX Approved` | CAPEX project list | `KRW_NA_FF_HISTSB1[Internal CAPEX ID] → CAPEX Approved[Internal CAPEX ID]` (already exists) | Not in prod (different report) | Keep — belongs to a different report page. Not part of Commercial Sales scope. |
| `KRW_NA_FF_HISTSB1` | Historical strategic business plan (?) | Related to CAPEX Approved | Not in prod | Keep for other report page. |
| `KRW_NA_FF_COSTCENTREHIER` | Cost center hierarchy | Not related | Not in prod | Disconnected — different report domain (P&L / cost). |
| `KRW_NA_FF_COSTCTHIER_ONDULINE` | Cost center hierarchy (Onduline division) | Not related | Not in prod | Disconnected — different report domain. |
| `KRW_NA_FF_COSTELEMHIER` | Cost element hierarchy | `KRW_NA_FF_COSTELEM_OH1[Cost Element Key] ↔ KRW_NA_FF_COSTELEMHIER[CostElement]` (bothDir) | Not in prod | Keep for P&L report page. |
| `KRW_NA_FF_COSTELEM_OH1` | Cost element operational hierarchy | Related to COSTELEMHIER | Not in prod | Keep. |
| `KRW_NA_FF_PLSTRUCTURE` | P&L structure | Not related | Not in prod | Disconnected — P&L domain. |
| `KRW_NA_FF_TERRITORY` | Territory master | Not related | Not in prod | Disconnected — may connect to VBRP.Territory_Name; needs a specific requirement to justify. |
| `KRW_NA_FF_ZIPCODES` | Zip code lookup | Not related | Not in prod | Disconnected — may be intended for a zip-level territory map. |

**None of these should participate in this task's relationship rebuild.** They belong to other report domains (P&L, CAPEX, territory reporting) that are out of scope for Commercial Sales.

---

## Summary

- **Calendar/Fiscal:** consolidate on `KRW_NA_FF_CALENDAR` + `KRW_NA_FF_FISCALPERIOD` + `Fiscal Period Selector`. Retire `DimDate`.
- **Forecast:** fix the missing `Fiscal Period Selector ↔ FORECAST_INTAKE` bridge.
- **Geography:** keep the existing `State` join, flag COUNTRY_REGION alternative as Phase 11 risk.
- **Other FF tables:** leave disconnected — they belong to non-Commercial-Sales domains.

# Phase 9 — Filter Propagation Tests

**Status:** Test plan only. Cannot execute Power BI runtime queries from Claude Code — user (or automated PBI Desktop runner) must open `AWIP_Commercial_Sales.pbip`, apply each slicer, and record the measure value into the Development Result column.

**Baseline:** compare each Development Result against production (`Amalgamated Sales Reports - JC.pbip` — open in a second Power BI Desktop window with the same slicer selection).

**Test fiscal period:** 2026007 (July 2026) — same period used in the ISO Rate investigation.

---

## Test set 1 — Fiscal period propagation

| # | Test | Slicer selection | Measure | Expected (prod) | Actual (dev) | Status |
|---|---|---|---|---|---|---|
| F1 | Fiscal period → Billing Revenue | Fiscal Period Selector = 2026007 | `Billing[Revenue]` (sum) | (TBD from prod) | (TBD) | ⏳ |
| F2 | Fiscal period → Billing Quantity FT2 | Fiscal Period Selector = 2026007 | `SUM(Billing[Billing_Quantity_in_FT2])` | (TBD) | (TBD) | ⏳ |
| F3 | Fiscal period → Billing Quantity BFT2 | Fiscal Period Selector = 2026007 | `SUM(Billing[Billing_Quantity_in__BFT2])` | (TBD) | (TBD) | ⏳ |
| F4 | Fiscal period → SalesOrders Revenue Order Intake | Fiscal Period Selector = 2026007 | `SUM(SalesOrders[Revenue_Order_Intake])` | (TBD) | (TBD) | ⏳ |
| F5 | Fiscal period → SalesOrders Backlog Revenue | Fiscal Period Selector = 2026007 | `SUM(SalesOrders[Revenue_Backlog])` (requires backlog measure using RequestedDeliveryDate role-play) | (TBD) | (TBD) | ⏳ |
| F6 | Fiscal period → Forecast (Invoiced-side) | Fiscal Period Selector = 2026007 | `SUM(KRW-NA_FF_FORECAST[Sales $])` | (TBD) | (TBD) | ⏳ |
| F7 | Fiscal period → Forecast Intake (SO-side) | Fiscal Period Selector = 2026007 | `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales $])` | (TBD) — should now be filtered, not grand total | (TBD) | ⏳ |

**F7 is the most important:** validates that the new `Fiscal Period Selector ↔ FORECAST_INTAKE` relationship works. If F7 still returns the grand total across all periods, the relationship or the calculated bridge column is broken.

---

## Test set 2 — Forecast (calendar/product) propagation

| # | Test | Slicer selection | Measure | Expected (prod) | Actual (dev) | Status |
|---|---|---|---|---|---|---|
| FC1 | Sales Forecast — INVOICED grand total | none | `SUM(KRW-NA_FF_FORECAST[Sales $])` | (TBD — should match prod exactly, table is imported not calc) | (TBD) | ⏳ |
| FC2 | Sales Forecast INVOICED at period 2026007 | Fiscal Period Selector = 2026007 | `SUM(KRW-NA_FF_FORECAST[Sales $])` | (TBD) | (TBD) | ⏳ |
| FC3 | Sales Forecast INTAKE grand total | none | `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales $])` | (TBD) | (TBD) | ⏳ |
| FC4 | Sales Forecast INTAKE at period 2026007 | Fiscal Period Selector = 2026007 | `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales $])` | (TBD) | (TBD) | ⏳ |
| FC5 | ISO Rate Fcst IS | Fiscal Period Selector = 2026007 | `Billing[ISO Rate Fcst IS]` = DIVIDE(SUM Forecast ISO bdft, SUM Forecast Membrane sqft) | (TBD) | (TBD) | ⏳ |
| FC6 | ISO Rate Fcst OI | Fiscal Period Selector = 2026007 | `SalesOrders[ISO Rate Fcst OI]` | (TBD) | (TBD) | ⏳ |

---

## Test set 3 — Geography / territory propagation

| # | Test | Slicer selection | Measure | Expected (prod) | Actual (dev) | Status |
|---|---|---|---|---|---|---|
| G1 | Filter Billing Revenue by state | KRW_NA_FF_GEOINFO[State] = "Texas" | `SUM(Billing[Revenue])` | (TBD) | (TBD) | ⏳ |
| G2 | Filter Order Intake Revenue by state | KRW_NA_FF_GEOINFO[State] = "Texas" | `SUM(SalesOrders[Revenue_Order_Intake])` | (TBD) | (TBD) | ⏳ |
| G3 | Filter customer totals by country | KRW_NA_FF_GEOINFO[Country] = "USA" | `SUM(Billing[Revenue])` | (TBD) | (TBD) | ⏳ |
| G4 | Grand-total invariant | none | `SUM(Billing[Revenue])` — must equal sum of state totals from G1 with all states iterated | (TBD) | (TBD) | ⏳ |

**G4** protects against the grain risk flagged in Phase 5: if `KRW_NA_FF_GEOINFO[State]` is non-unique (e.g., "TX" under multiple countries), G1's per-state total may double-count rows. If G4 fails, we need the `COUNTRY_REGION` alternative (Phase 11).

---

## Test set 4 — Product / product-family propagation

| # | Test | Slicer selection | Measure | Expected (prod) | Actual (dev) | Status |
|---|---|---|---|---|---|---|
| P1 | Filter Billing by Product Family | Billing[Product_Family] = "TPO Membranes" | `SUM(Billing[Billing_Quantity_in_FT2])` | (TBD) | (TBD) | ⏳ |
| P2 | Filter SalesOrders by Product Family | SalesOrders[Product_Family_Product_Number] = "TPO Membranes" | `SUM(SalesOrders[Order_Quantity_in_FT2])` | (TBD) | (TBD) | ⏳ |
| P3 | Filter Forecast Membrane sqft by product | (product family lives on facts; Forecast filtered via measure) | `Current Fiscal Month Sales Membrane sqft` | (TBD — should equal 812,400 for 2026007 based on SAC-verified data) | (TBD) | ⏳ |

---

## How to execute

1. Open `AWIP_Commercial_Sales.pbip` in Power BI Desktop.
2. Add a slicer on `Fiscal Period Selector[FiscalYearPeriod]` — select `2026007`.
3. Create a card visual for each measure in the tests above.
4. Record the returned value in the "Actual (dev)" column.
5. Open `production-reference-odata/Amalgamated Sales Reports - JC.pbip` in a second window (or Power BI Service — depends on whether the AAS connection is available locally).
6. Apply the same slicer selection.
7. Record the production value in "Expected (prod)".
8. Mark ✅ (within 1% of prod), ⚠ (within 10%), or ❌ (>10% difference) in Status.

**Priority order:** F7 first (biggest structural change), then F1–F5 (activation of Billing/SalesOrders → CALENDAR chain), then FC/G/P sets.

---

## Fallback if production is not accessible

If production dashboard values cannot be pulled directly, use the values recorded in the ISO Rate investigation status (2026-08-17) as the reference for period 2026007:

- Billing ISO BFT2 = 633,613
- Billing Membrane FT2 = 812,400
- These come from SAC direct query, so they represent the true underlying data and are authoritative for column-sum verification (though not for measure-level verification, since production AAS applies additional transforms).

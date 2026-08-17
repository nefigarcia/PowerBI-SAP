# Phase 10 — KPI Validation (AWIP vs OData Production)

**Test fiscal period:** `2026007` (July 2026 — same one used throughout the ISO Rate investigation).
**Date:** 2026-08-17.
**AWIP model state:** post-Phase 9 v2, ~87 new measures ported from production.
**Production reference:** `KRW_NA_SM_INVOICED`, `KRW_NA_SM_SORDERS`, `KRW_NA_SM_BACKLOG` semantic models + `Amalgamated Sales Reports - JC.pbip` report.

**How to use this file:** for each row, drop the AWIP measure on a Card visual filtered to `Fiscal Period Selector = 2026007` and record the value. Then repeat in production (either the report or by direct-connect to the semantic model in Power BI Desktop). Populate the AWIP + Production columns and I'll compute the delta + status.

---

## 1. Headline KPIs — 6 must-match values

If these 6 don't match, nothing else matters.

| # | KPI | AWIP measure | AWIP source | Prod measure equivalent | AWIP value | Prod value | Δ % | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Revenue (Invoiced) | `_Measures[Sales]` = `SUM(Billing[SlsVolNetAmt_CC])` | Billing | `KRW_NA_SAP_VBRP[Revenue]` (SUM of Revenue in DC with Sign) | $1,138,072 | ??? | | |
| 2 | Order Intake | `_Measures[Order Intake]` = `SUM(SalesOrders[IncSalesOrdNetAmnt_CC])` | SalesOrders | `KRW_NA_SAP_VBAP OI[Revenue OI]` | ??? | ??? | | |
| 3 | Backlog $ | `SalesOrders[Total Backlog $]` = `SUM(SalesOrders[Revenue_Backlog])` | SalesOrders | `KRW_NA_SAP_VBAP SB[Total Backlog $]` | ??? | ??? | | |
| 4 | Sum Billing Qty. in FT2 for Membranes | `Billing[Sum Billing Qty. in FT2 for Membranes]` | Billing | Same-named on VBRP | 812,400 | ??? | | ⚠ suspected mismatch — see iso-rate-investigation-status.md |
| 5 | Sum Billing Qty. in BFT2 for ISO | `Billing[Sum Billing Qty. in BFT2 for ISO]` | Billing | Same-named on VBRP | 633,613 | ??? | | ⚠ same |
| 6 | ISO Rate IS | `Billing[ISO Rate IS]` = `[BFT2 ISO] / [FT2 Membranes]` | Billing | `KRW_NA_SAP_VBRP[ISO Rate]` | **0.78** | **1.34** (per user) | -42% | ❌ **FAILING** — under investigation |

Fill in the ??? cells to unblock the rest.

---

## 2. Forecast-side KPIs (post KRW-NA_FF_FORECAST import)

| # | KPI | AWIP measure | AWIP source | Prod measure equivalent | AWIP value | Prod value | Δ % | Status |
|---|---|---|---|---|---|---|---|---|
| 7 | Sales $ Fcst (grand total 2026) | `KRW-NA_FF_FORECAST[Sales $]` summed | dataflow | `KRW-NA_FF_FORECAST[Sales $]` in prod semantic model | ~$10.5M (from dataflow snapshot) | ??? | | |
| 8 | Sum Fcst Sales in FT2 for Membranes (period 2026007) | `Billing[Sum Fcst Sales in FT2 for Membranes]` = `SUM(FORECAST[Sales Membrane sqft])` | Billing → FORECAST | Production's `KRW-NA_FF_FORECAST[Sales Membrane sqft]` filtered to `2026007` | ??? (should be ~573,828 if filter propagates via bridge) | ~573,828 (from dataflow) | | |
| 9 | ISO Rate Fcst IS (period 2026007) | `Billing[ISO Rate Fcst IS]` | Billing → FORECAST | `KRW-NA_FF_FORECAST[ISO Rate Fcst]` for 2026007 | 2.80 (grand-total all 2026, per user's July screenshot) | **2.94** (per user) | -5% | ⚠ filter-propagation issue — should be ~2.96 for 2026-07 alone |
| 10 | Sum Fcst Order Qty. in FT2 for Membranes OI (period 2026007) | `SalesOrders[Sum Fcst Order Qty. in FT2 for Membranes OI]` = `SUM(FORECAST_INTAKE[Sales Membrane sqft])` | SalesOrders → FORECAST_INTAKE | Production's `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` filtered to `2026007` | ??? | ??? | | |
| 11 | ISO Rate Fcst OI (period 2026007) | `SalesOrders[ISO Rate Fcst OI]` | SalesOrders → FORECAST_INTAKE | `KRW_NA_FF_FORECAST_INTAKE[ISO Rate Fcst VBAP]` for 2026007 | 2.63 (per prior baseline) | ??? | | |
| 12 | Current Month Invoice Revenue Fcst | `KRW-NA_FF_FORECAST[Current Month Invoice Revenue Fcst]` | FORECAST | Same on prod | ??? | ??? | | Should = 2026007 value = ~$1,234,930 |
| 13 | YTD Invoice Revenue Fcst | `KRW-NA_FF_FORECAST[YTD Invoice Revenue Fcst]` | FORECAST | Same on prod | ??? | ??? | | Should be ~$2M cumulative Jan-Jul |

---

## 3. Current-Month / YTD suite (newly ported)

These use the `Current FYP VBRP` / `Current FYP VBAP OI` helpers. Verify each returns a non-BLANK value for period 2026007.

**Billing (invoice-side)**

| # | Measure | AWIP value | Prod value | Status |
|---|---|---|---|---|
| 14 | `Current Month Billing Qty. in FT2 for Membranes` | | | |
| 15 | `YTD Billing Qty. in FT2 for Membranes` | | | |
| 16 | `Current Month Billing Qty. in BFT2 for ISO` | | | |
| 17 | `YTD Billing Qty. in BFT2 for ISO` | | | |
| 18 | `Current Month Billing Qty. in FT2 for ISO` | | | |
| 19 | `YTD Billing Qty. in FT2 for ISO` | | | |
| 20 | `Current Month Invoiced Revenue Billing Date` | | | |
| 21 | `YTD Invoiced Revenue Billing Date` | | | |
| 22 | `Current Fiscal Month Invoiced Revenue` | | | |
| 23 | `Current Fiscal Month Billing Qty. in FT2 for Membranes` | | | |
| 24 | `Current Fiscal Month Billing Qty. in FT2 for ISO` | | | |
| 25 | `Current Fiscal Month Billing Qty. in BFT2 for ISO` | | | |
| 26 | `Current Fiscal Month Invoiced Revenue FT2 Membranes` | | | |

**SalesOrders (order-intake side)**

| # | Measure | AWIP value | Prod value | Status |
|---|---|---|---|---|
| 27 | `Current Month Order Revenue` | | | |
| 28 | `Current Month Order Revenue Doc Date` | | | |
| 29 | `Current Calendar Month Order FT2 for Membranes` | | | |
| 30 | `YTD Order FT2 for Membranes` | | | |
| 31 | `YTD Order FT2 for ISO` | | | |
| 32 | `YTD Order BFT for ISO` | | | |
| 33 | `Current Calendar Month Order FT2 for ISO` | | | |
| 34 | `Current Calendar Month Order BFT for ISO` | | | |
| 35 | `YTD Order Revenue Doc Date` | | | |
| 36 | `Current Fiscal Month Order FT2 for ISO` | | | |
| 37 | `Current Fiscal Month Order BFT for ISO` | | | |
| 38 | `Current Fiscal Month Order Revenue` | | | |

---

## 4. Prior Year & YoY (self-consistency)

These we can validate WITHOUT production if the underlying data is correct. AWIP has two PY techniques (SAMEPERIODLASTYEAR via DimDate vs Kingspan pattern via KRW_NA_FF_CALENDAR) — verify they give the same value.

| # | KPI | AWIP measure | Prod measure equivalent | AWIP value | Prod value | Status |
|---|---|---|---|---|---|---|
| 39 | Sales PY (`_Measures` technique) | `_Measures[Sales PY]` = `CALCULATE([Sales], SAMEPERIODLASTYEAR(DimDate[Date]))` | Prod uses PY variants on VBRP | | | |
| 40 | Revenue Previous Year (Billing technique) | `Billing[Revenue Previous Year]` = Kingspan pattern via KRW_NA_FF_CALENDAR | `KRW_NA_SAP_VBRP[Revenue Previous Year]` | | | Should equal #39 if data is consistent |
| 41 | Sum Billing Qty. in FT2 for Membranes Prior Year | `Billing[Sum Billing Qty. in FT2 for Membranes Prior Year]` | Same on prod VBRP | | | |
| 42 | Sum Billing Qty. in BFT2 for ISO Prior Year | `Billing[Sum Billing Qty. in BFT2 for ISO Prior Year]` | Same on prod VBRP | | | |
| 43 | Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year | `Billing[Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year]` | Same on prod VBRP | | | |
| 44 | Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year | `Billing[Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year]` | Same on prod VBRP | | | |
| 45 | Sales YoY % | `_Measures[Sales YoY %]` | (derived KPI, not in prod TMDL) | | n/a | Should = ([Sales] - [Sales PY])/[Sales PY] |
| 46 | Order Intake YoY % | `_Measures[Order Intake YoY %]` | (derived) | | n/a | |
| 47 | PY Revenue Order Intake | `SalesOrders[PY Revenue Order Intake]` (Kingspan pattern) | `KRW_NA_SAP_VBAP OI[Revenue Previous Year OI]` | | | |
| 48 | Sum PY Order Qty. in FT2 for Membranes OI | `SalesOrders[Sum PY Order Qty. in FT2 for Membranes OI]` | Same on prod | | | |
| 49 | Sum PY Order Qty. in BFT2 for ISO OI | `SalesOrders[Sum PY Order Qty. in BFT2 for ISO OI]` | Same on prod | | | |

---

## 5. Delta / % Fcst composites

These depend on both the actual AND forecast measures — validate only after row 6, 9, 11 are green.

| # | Composite | AWIP measure | AWIP value | Prod value | Status |
|---|---|---|---|---|---|
| 50 | $ Difference Current Month VBRP | `Billing[$ Difference Current Month VBRP]` = `[Current Fiscal Month Invoiced Revenue] - [Current Month Invoice Revenue Fcst]` | | | |
| 51 | $ Difference YTD VBRP | `Billing[$ Difference YTD VBRP]` = `[YTD Invoiced Revenue Billing Date] - [YTD Invoice Revenue Fcst]` | | | |
| 52 | % Fcst VBRP CM | `Billing[% Fcst VBRP CM]` | | | Should be actuals/forecast ratio |
| 53 | % Fcst VBRP FM | `Billing[% Fcst VBRP FM]` | | | |
| 54 | $ Difference Current Month (OI) | `SalesOrders[$ Difference Current Month]` | | | |
| 55 | $ Difference YTD (OI) | `SalesOrders[$ Difference YTD]` | | | |
| 56 | % Fcst CM (OI) | `SalesOrders[% Fcst CM]` | | | |
| 57 | % Fcst FM (OI) | `SalesOrders[% Fcst FM]` | | | |

---

## 6. Rates & derived (ISO Rate variants + AOP)

| # | KPI | AWIP measure | Prod measure | AWIP value | Prod value | Status |
|---|---|---|---|---|---|---|
| 58 | ISO Rate IS (actual, invoice) | `Billing[ISO Rate IS]` | `KRW_NA_SAP_VBRP[ISO Rate]` | 0.78 | 1.34 | ❌ under investigation |
| 59 | ISO Rate OI (actual, order intake) | `SalesOrders[ISO Rate OI]` | `KRW_NA_SAP_VBAP OI[ISO Rate VBAP OI]` | | | |
| 60 | ISO Rate SB (actual, backlog) | `SalesOrders[ISO Rate SB]` | `KRW_NA_SAP_VBAP SB[ISO Rate VBAP SB]` | | | |
| 61 | ISO Rate Fcst IS | `Billing[ISO Rate Fcst IS]` | `KRW-NA_FF_FORECAST[ISO Rate Fcst]` | 2.80 (grand) / 2.96 expected | 2.94 (user reported) | ⚠ filter propagation |
| 62 | ISO Rate Fcst OI | `SalesOrders[ISO Rate Fcst OI]` | `KRW_NA_FF_FORECAST_INTAKE[ISO Rate Fcst VBAP]` | 2.63 | | |
| 63 | ISO AOP - $/bdft IS | `Billing[ISO AOP - $/bdft IS]` (just fixed to use BFT2) | `KRW_NA_SAP_VBRP[ISO AOP - $/bdft VBRP]` | | | |
| 64 | ISO AOP - $/bdft OI | `SalesOrders[ISO AOP - $/bdft OI]` | `KRW_NA_SAP_VBAP OI[ISO AOP - $/bdft VBAP OI]` | | | |
| 65 | Margin Perc | `Billing[Margin Perc]` | `KRW_NA_SAP_VBRP[Margin Perc]` | | | |
| 66 | Margin Perc VBAP | `SalesOrders[Margin Perc VBAP]` | `KRW_NA_SAP_VBAP OI[Margin Perc VBAP]` | | | |

---

## 7. Product-family sanity checks (Membrane vs ISO split)

For period 2026007, verify the split of Revenue and Quantity across Product Family values:

| Product Family | Billing rows for 2026007 | Membrane FT2 | ISO BDFT | ISO FT2 | Revenue |
|---|---|---|---|---|---|
| Cover Board | | | | | |
| ISO GF | | | | | |
| ISO GF Taper | | | | | |
| Polyiso Insulation | | | | | |
| PVC Membranes | | | | | |
| Roofing Assesories | | | | | |
| TPO Membranes | | | | | |
| (Blank / 8th) | | | | | |
| **TOTAL** | | 812,400 | 633,613 | | $1,138,072 |

Same table for SalesOrders (Product_Family_Product_Number):

| Product Family | SalesOrders rows | Order Qty FT2 | Order Qty BFT | Order Revenue |
|---|---|---|---|---|
| … | | | | |

Compare row-by-row against production if possible.

---

## 8. Row-count sanity checks

Not KPIs, but useful cross-check:

| # | Metric | AWIP | Prod | Status |
|---|---|---|---|---|
| C1 | Distinct Product_Family values on Billing | 8 (confirmed) | ??? | Should match |
| C2 | Distinct Fiscal Year Periods present in Billing | | | Both should include 2026007 |
| C3 | Distinct Fiscal Year Periods present in KRW-NA_FF_FORECAST | 12 (2026001 to 2026012, plus zero 2025 rows) | | |
| C4 | Distinct State_Name values on Billing | | | Sanity — should match `KRW_NA_FF_GEOINFO[State]` slice |
| C5 | Row count on SalesOrders where `Sales_Representative_T` is non-blank | | | Percent-blank tells us if the enrichment column is populated |

---

## 9. Test-plan checklist (in order)

- [ ] **Precheck:** cold-reload the AWIP PBIP. Confirm all ~87 new measures appear in the field list with no error. If any table shows a load error, fix before proceeding.
- [ ] Fill in section 1 (headline 6). If more than 1 fails by >5%, STOP and investigate before continuing — likely a data-source drift.
- [ ] Fill in section 6 (rates). ISO Rate IS already known to fail (0.78 vs 1.34). If other ratios also diverge in the same direction, that points to a systemic Membrane / ISO quantity issue affecting all ratios.
- [ ] Fill in section 2 (forecast). If AWIP forecast values differ from production, likely the filter-propagation bridge (Fiscal Period Selector) is misfiring — check that `_Diag Candidate ISO Rate v2` responds to the fiscal period slicer.
- [ ] Fill in section 3 (current-month / YTD suite) — spot-check any 3-4 measures, don't need to fill every row unless a specific dashboard tile depends on it.
- [ ] Fill in section 4 (PY) — for period 2026007, compare `_Measures[Sales PY]` and `Billing[Revenue Previous Year]`. If they differ, one of the two PY techniques is wrong.
- [ ] Fill in section 5 (composites) — only meaningful if the underlying measures are green.
- [ ] Fill in section 7 (product-family split) — this is the most informative diagnostic for ISO Rate IS mystery. If the Membrane row shows different values in AWIP vs production, we've found the discrepancy source.

---

## 10. Known-failing baseline (already documented, tracked separately)

- **KPI #6: ISO Rate IS = 0.78 vs prod 1.34** — see [`iso-rate-investigation-status.md`](iso-rate-investigation-status.md). Blocked pending direct production value comparison (option A/B/C in that file).
- **KPI #9: ISO Rate Fcst IS = 2.80 grand total, should be ~2.96 for period 2026007** — filter propagation issue via the new `Fiscal Period Selector` bridge. Fix candidate: rework the disconnected slicer, or repoint the visual to filter by `KRW-NA_FF_FORECAST[Fiscal Year Period]` directly.

---

## 11. When Phase 10 is done

**Definition of done:**
- All rows in sections 1, 2, and 6 have both AWIP and production values filled in.
- All rows with Δ% > 5% have a root-cause note (either "fixed in Phase 11" or "known limitation / blocker").
- No AWIP measure returns a `#ERROR` or unexpectedly BLANK value for a filled test period.
- The two ISO Rate blockers are either resolved OR explicitly deferred with rationale.

**Written:** 2026-08-17

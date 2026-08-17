# OData Production vs AWIP Development — Diff

**Purpose:** Table-by-table, measure-by-measure diff of `production-reference-odata/` vs `AWIP_Commercial_Sales.PBIP/`.

**Classification legend:**
- **EXACT** — same name AND same semantics AND same DAX / structure
- **FUNCTIONALLY EQUIVALENT** — different implementation, same result under the same filter context
- **DIFFERENT** — same name / concept, different semantics — needs reconciliation
- **MISSING** — present in production, absent in AWIP
- **EXTRA** — present in AWIP, absent in production (may indicate ODBC-derived leftover)
- **ODBC-DERIVED (INVALID)** — item traces back to the deprecated ODBC reference; not in OData production
- **NEEDS REVIEW** — undecidable from static inspection; needs value-domain probe or business input

---

## 1. Tables

| Prod table | AWIP equivalent | Status | Notes |
|---|---|---|---|
| `KRW_NA_SAP_VBRP` | `Billing` (Datasphere OData) | FUNCTIONALLY EQUIVALENT | Different source path (AAS cube vs OData), same underlying SAP VBRP entity |
| `KRW_NA_SAP_VBAP OI` | `SalesOrders` (Datasphere OData) | FUNCTIONALLY EQUIVALENT | Same underlying SAP VBAP entity |
| `KRW_NA_SAP_VBAP SB` | `SalesOrders` (filter subset) | FUNCTIONALLY EQUIVALENT | Backlog is a projection of VBAP; AWIP already has `Revenue_Backlog`, `Open_*`, `Gross_Margin_for_open_orders` native columns |
| `KRW_NA_SAP_KNA1` (× 3) | (columns promoted onto `Billing` / `SalesOrders`) | FUNCTIONALLY EQUIVALENT | AWIP has `CustomerFullName`, `SoldToParty_D*_T`, `Sales_Representative_T` etc. |
| `KRW_NA_SAP_KNVV` (× 3) | (columns promoted onto `Billing` / `SalesOrders`) | FUNCTIONALLY EQUIVALENT | AWIP has `CustomerAccountAssignmentGroup_T` etc. |
| `KRW_NA_SAP_LIKP` / `LIPS` | (delivery joins collapsed) | FUNCTIONALLY EQUIVALENT | AWIP fact tables carry joined result columns |
| `KRW_NA_SAP_MARM_BFT` (× 2) | (columns promoted onto fact tables) | FUNCTIONALLY EQUIVALENT | AWIP has `Factor_UoM_BFT`, `Billing_Quantity_in_BFT` etc. |
| `KRW_NA_SAP_TVAPT` / `TVM3T` / `VBPA2` | (`_T` columns on fact tables) | FUNCTIONALLY EQUIVALENT | Standard SAP text tables absorbed into fact-table columns |
| `KRW_NA_FF_CALENDAR` (+ OI + SB) | `KRW_NA_FF_CALENDAR` (single copy) | FUNCTIONALLY EQUIVALENT | AWIP uses shared-dim pattern instead of role-playing copies |
| `KRW_NA_FF_FISCALPERIOD` (+ OI + SB) | `KRW_NA_FF_FISCALPERIOD` (single copy) | FUNCTIONALLY EQUIVALENT | same |
| `KRW_NA_FF_GEOINFO` (+ OI + SB) | `KRW_NA_FF_GEOINFO` (single copy) | FUNCTIONALLY EQUIVALENT | same |
| `KRW_NA_FF_FORECAST_INTAKE` | `KRW_NA_FF_FORECAST_INTAKE` | EXACT | Both use PowerPlatform.Dataflows |
| `KRW-NA_FF_FORECAST` **(hyphen)** | ❌ **MISSING** | MISSING | Invoice-side forecast dataflow — not imported into AWIP |
| `Salesforce Quote Line Item` | ❌ MISSING | MISSING | Business decision required |
| `Salesforce Quotes` | ❌ MISSING | MISSING | Business decision required |
| `FiscalYearPeriods Slicer` (+ OI + SB) | ❌ MISSING (or use `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` directly) | MISSING (functionally covered) | Prod uses disconnected slicer with bi-di to FORECAST tables; AWIP can wire this differently |
| — | `DimDate` | EXTRA | Custom date table in AWIP; not in prod. Prod uses CALENDAR (+ OI + SB) copies + LocalDateTables |
| — | `_Measures` | EXTRA (harmless) | Measure-only table for organisation; internal convention |
| — | `KRW_NA_FF_TERRITORY` | EXTRA | Not used in Amalgamated Sales scope — different report |
| — | `KRW_NA_FF_ZIPCODES` | EXTRA | Not used in Amalgamated Sales scope |
| — | `KRW_NA_FF_PLSTRUCTURE` | EXTRA | P&L / Tagetik scope, out of Amalgamated Sales |
| — | `KRW_NA_FF_HISTSB1` | EXTRA | CAPEX-related, out of scope |
| — | `KRW_NA_FF_COSTCENTREHIER` | EXTRA | Cost accounting, out of scope |
| — | `KRW_NA_FF_COSTCTHIER_ONDULINE` | EXTRA | Cost accounting, out of scope |
| — | `KRW_NA_FF_COSTELEM_OH1` | EXTRA | Cost accounting, out of scope |
| — | `KRW_NA_FF_COSTELEMHIER` | EXTRA | Cost accounting, out of scope |
| — | `'CAPEX Approved'` | EXTRA | CAPEX, out of scope |

**Summary:**
- **In common (equivalent):** 12 conceptual tables
- **Missing from AWIP:** 3 (KRW-NA_FF_FORECAST, Salesforce Quotes, Salesforce Quote Line Item) + arguably FiscalYearPeriods Slicer
- **Extra in AWIP:** 8 dataflows (all for CAPEX / cost-accounting / P&L / territory scopes outside Amalgamated Sales) + `DimDate` + `_Measures`

## 2. Measures — production TMDL vs AWIP TMDL

Production has **17 TMDL measures** (10 on `KRW-NA_FF_FORECAST`, 7 on `KRW_NA_FF_FORECAST_INTAKE`). AWIP has **~37 TMDL measures** across `_Measures`, `Billing`, `SalesOrders`. The count difference is because AWIP reconstructs what the AAS cubes provided in production.

### 2a. Production measure → AWIP measure (mapping)

| Production measure (table) | AWIP measure (table) | Status | Reconciliation notes |
|---|---|---|---|
| `ISO Rate Fcst` on `KRW-NA_FF_FORECAST` — `DIVIDE(SUM(Sales ISO bdft), SUM(Sales Membrane sqft))` | `ISO Rate Fcst IS` on `Billing` — `DIVIDE(SUM(ForecastSalesBDFT), [Sum Fcst Sales in FT2 for Membranes])` | DIFFERENT (source) | Same shape (bdft/sqft), different source. Prod pulls from FORECAST dataflow; AWIP pulls numerator from Billing[ForecastSalesBDFT] and denominator from Billing[Sales_Forecast_Membrane_Qty_in_FT2]. Values may differ if the forecast grain differs. Fix candidate: import KRW-NA_FF_FORECAST into AWIP and rewrite AWIP's measure to use it. |
| `ISO Rate Fcst VBAP` on `KRW_NA_FF_FORECAST_INTAKE` — `DIVIDE(SUM(Sales ISO bdft), SUM(Sales Membrane sqft))` | `ISO Rate Fcst OI` on `SalesOrders` — different DAX pattern | FUNCTIONALLY EQUIVALENT (needs verification) | Both compute bdft/sqft ratio; AWIP uses SalesOrders columns, prod uses FORECAST_INTAKE dataflow columns. Grain may differ. |
| `Current Month Invoice Revenue Fcst` on `KRW-NA_FF_FORECAST` — filter by `[Current FYP VBRP]` | ❌ NOT IN AWIP | MISSING | Requires reconstructing `[Current FYP VBRP]` from `KRW_NA_FF_FISCALPERIOD` + TODAY() |
| `Current Month Invoiced Sales Membrane sqft` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | same |
| `YTD Invoiced Sales Membrane sqft` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | Pattern: CALCULATE(SUM([Sales Membrane sqft]), FILTER('KRW_NA_FF_CALENDAR', YEAR([Date])=YEAR(TODAY()))) |
| `Current Month Invoiced Sales ISO bdft` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | Same pattern as above |
| `YTD Invoiced Sales ISO bdft` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | same |
| `Current Month Invoiced Sales ISO sqft` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | same |
| `YTD Invoiced Sales ISO sqft` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | same |
| `YTD Invoice Revenue Fcst` on `KRW-NA_FF_FORECAST` | ❌ NOT IN AWIP | MISSING | same |
| `Current Month Invoiced Sales ISO sqft FM` on `KRW-NA_FF_FORECAST` — hardcoded to `"2026.02"` | ❌ NOT IN AWIP | MISSING (and hardcoded — likely stale) | Avoid reproducing the hardcode; use `[Current FYP VBRP]` pattern instead |
| `Current Month Order Revenue Fcst` on `KRW_NA_FF_FORECAST_INTAKE` | ❌ NOT IN AWIP | MISSING | same reconstruction pattern needed for `[Current FYP VBAP OI]` |
| `Current Fiscal Month Sales Membrane sqft` on `KRW_NA_FF_FORECAST_INTAKE` — uses `CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane")` | ❌ NOT IN AWIP | MISSING — remap SAP-table ref to `SalesOrders[Product_Family_Product_Number]` | STRONG confidence in remapping |
| `Current Fiscal Month Sales ISO sqft` on `KRW_NA_FF_FORECAST_INTAKE` — same pattern with "iso" filter | ❌ NOT IN AWIP | MISSING — same remapping | STRONG |
| `Current Month Sales ISO bdft` on `KRW_NA_FF_FORECAST_INTAKE` | ❌ NOT IN AWIP | MISSING | Pattern: use `KRW_NA_FF_CALENDAR` filter for MONTH=TODAY |
| `YTD Sales ISO bdft` on `KRW_NA_FF_FORECAST_INTAKE` | ❌ NOT IN AWIP | MISSING | Pattern: same YEAR filter |
| `YTD Sales ISO sqft` on `KRW_NA_FF_FORECAST_INTAKE` | ❌ NOT IN AWIP | MISSING | same |

**Every production TMDL measure is missing from AWIP** — the only two "equivalents" are DIFFERENT-source or FUNCTIONALLY EQUIVALENT with different tables. AWIP will need to import the missing measures once we have `KRW-NA_FF_FORECAST` in the model.

### 2b. AWIP measures → production status

| AWIP measure (table) | Production equivalent? | Status | Notes |
|---|---|---|---|
| `Sales` on `_Measures` = `SUM(Billing[SlsVolNetAmt_CC])` | (AAS cube measure `Revenue` — invisible) | FUNCTIONALLY EQUIVALENT (likely) | Prod visuals use `Revenue` on `KRW_NA_SAP_VBRP`; AWIP uses `SlsVolNetAmt_CC`. Both are "sales net amount in company currency". Verify numeric match in Phase 10. |
| `Sales Quantity` on `_Measures` = `SUM(Billing[SalesVolumeQuantity])` | (AAS cube measure — invisible) | NEEDS REVIEW | Verify against prod `Sum Billing Qty. in ...` values |
| `Order Intake` on `_Measures` = `SUM(SalesOrders[IncSalesOrdNetAmnt_CC])` | (AAS cube) | FUNCTIONALLY EQUIVALENT (likely) | |
| `Order Intake Quantity` on `_Measures` = `SUM(SalesOrders[IncSalesOrderQty])` | (AAS cube) | FUNCTIONALLY EQUIVALENT (likely) | |
| `Sales PY` / `Sales Quantity PY` / `Order Intake PY` / `Order Intake Quantity PY` on `_Measures` — SAMEPERIODLASTYEAR pattern via `DimDate` | (AAS cube variants like `Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year`) | DIFFERENT | Prod uses AAS cube's built-in PY measures (invisible); AWIP uses SAMEPERIODLASTYEAR. Numeric outcome should match if `DimDate` is fully connected. |
| `Sales YoY %` / `Sales Quantity YoY %` / `Order Intake YoY %` / `Order Intake Quantity YoY %` on `_Measures` | (invisible in prod) | EXTRA (harmless) | Derived KPIs |
| `Order Intake vs Sales` on `_Measures` | (invisible in prod) | EXTRA (harmless) | |
| `Avg Sales Price` on `_Measures` | (invisible in prod) | EXTRA (harmless) | |
| `Avg Order Price` on `_Measures` | (invisible in prod) | EXTRA (harmless) | |
| `Sum Billing Qty. in FT2 for Membranes` on `Billing` | AAS cube measure (same name in visuals) | FUNCTIONALLY EQUIVALENT | Uses `Billing_quantity_in_FT2_for_Membrane` (string col via VALUE) — see string-type memory |
| `Sum Billing Qty. in BFT2 for ISO` on `Billing` | AAS cube measure | FUNCTIONALLY EQUIVALENT | |
| `Sum Billing Qty. in BFT2 for ISO 2` on `Billing` | (likely duplicate) | NEEDS REVIEW / possibly DUPLICATE | Two "for ISO" measures — reconcile |
| `Sum Fcst Sales in FT2 for Membranes` on `Billing` — now uses `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` | Prod: `Current Month Invoiced Sales Membrane sqft` on `KRW-NA_FF_FORECAST` | DIFFERENT (source) | AWIP uses Billing's pre-computed string column; prod uses the FORECAST dataflow. **Reconciliation needed** — grain may differ (fact-row level vs fiscal-period-level). |
| `Sum Revenue in DC with sign IS` on `Billing` = `SUM(Billing[Revenue])` | AAS cube `Revenue` | FUNCTIONALLY EQUIVALENT | Same SAP column |
| `ISO AOP - $/bdft IS` on `Billing` = `SUM(Revenue)/SUM(Billing_Quantity_with_Signs)` | AAS cube variant | NEEDS REVIEW | Verify formula matches prod's AAS-side "ISO AOP" measure |
| `ISO Rate IS` on `Billing` = `[Sum Billing Qty. in BFT2 for ISO]/[Sum Billing Qty. in FT2 for Membranes]` | AAS cube measure (same name) | FUNCTIONALLY EQUIVALENT | ✅ formula pattern matches |
| `ISO Rate Fcst IS` on `Billing` — uses Billing forecast columns | Prod: `ISO Rate Fcst` on `KRW-NA_FF_FORECAST` uses FORECAST dataflow | DIFFERENT (source) | Same shape (bdft/sqft), different source table. **Reconciliation needed once we import KRW-NA_FF_FORECAST**. |
| `Selected Fiscal Period` on `Billing` | (unknown production equivalent) | NEEDS REVIEW | |
| `ISO AOP - $/bdft OI` on `SalesOrders` | AAS cube variant | NEEDS REVIEW | |
| `Sum Fcst Order Qty. in FT2 for Membranes OI` on `SalesOrders` | Prod: `Current Fiscal Month Sales Membrane sqft` on `KRW_NA_FF_FORECAST_INTAKE` | DIFFERENT (source) | Prod filters on VBAP OI Product Family; AWIP presumably uses SalesOrders columns. Reconciliation needed. |
| `Sum Order Qty. in BFT2 for ISO OI` / `SB` on `SalesOrders` | AAS cube measures | FUNCTIONALLY EQUIVALENT | |
| `Sum Order Qty. in FT2 for Membranes OI` / `SB` / `SB 2` on `SalesOrders` | AAS cube measures | FUNCTIONALLY EQUIVALENT | 3 variants — reconcile SB vs SB 2 |
| `ISO Rate OI` / `SB` / `Fcst OI` on `SalesOrders` | AAS cube measures | FUNCTIONALLY EQUIVALENT | |
| `Total Backlog $` on `SalesOrders` | AAS cube BACKLOG measure | FUNCTIONALLY EQUIVALENT | |
| `PY Revenue Order Intake` on `SalesOrders` | AAS cube PY variant | DIFFERENT (implementation) | AWIP uses SAMEPERIODLASTYEAR via DimDate; prod uses AAS PY logic |
| `Sum PY Order Qty. in FT2 for Membranes OI` on `SalesOrders` | AAS cube PY variant | DIFFERENT (implementation) | same |
| `Sum PY Order Qty. in BFT2 for ISO OI` on `SalesOrders` | AAS cube PY variant | DIFFERENT (implementation) | same |

**Duplicates / redundancies to reconcile in AWIP:**
- `Sum Billing Qty. in BFT2 for ISO` vs `Sum Billing Qty. in BFT2 for ISO 2`
- `Sum Order Qty. in FT2 for Membranes SB` vs `Sum Order Qty. in FT2 for Membranes SB 2`

## 3. Relationships

| Prod relationship | AWIP equivalent | Status |
|---|---|---|
| `KRW_NA_FF_FISCALPERIOD ↔ CALENDAR` on Calendar Date (bi-di, 1:1) — × 3 role-copies | `KRW_NA_FF_FISCALPERIOD ↔ CALENDAR` (auto-detected, bi-di 1:1) — single copy | FUNCTIONALLY EQUIVALENT |
| `KRW_NA_SAP_KNA1 → GEOINFO` on COUNTRY_REGION — × 3 role-copies | `Billing[State_Name] → GEOINFO[State]` + `SalesOrders[State_Name] → GEOINFO[State]` (auto-detected) | DIFFERENT (key column) | Prod joins on COUNTRY_REGION, AWIP on State_Name — different granularity |
| `KRW_NA_SAP_VBRP → KNA1` (customer) | (columns promoted, no join needed) | ELIMINATED (by design) |
| `KRW_NA_SAP_VBAP OI → KNA1 OI` | (columns promoted) | ELIMINATED |
| `KRW_NA_SAP_VBAP SB → LIPS` (bi-di) | (not needed — SalesOrders backlog columns are pre-joined) | ELIMINATED |
| `FiscalYearPeriods Slicer ↔ FORECAST` (bi-di, 1:many) — × 3 role-copies | ❌ NOT IN AWIP | MISSING (blocked — no FORECAST table in AWIP yet) |
| Salesforce Quote Line Item → Quotes | ❌ NOT IN AWIP | MISSING |
| Salesforce → LocalDateTable_* (many) | (n/a — AWIP has no Salesforce) | MISSING (irrelevant unless Salesforce is added) |
| `Billing[BillingDocumentDate_D5] → DimDate[Date]` (AWIP-only) | — | EXTRA | AWIP-specific, correct for a shared-DimDate model |
| `SalesOrders[CreationDate_D8] → DimDate[Date]` (AWIP-only) | — | EXTRA | AWIP-specific, correct |

## 4. Report pages

Production and AWIP have **overlapping page sets**. Compared to production (13 pages, 158 visuals), AWIP has ~8 rebuilt pages (Invoiced Sales Dashboard, Invoiced Sales Detail, Order Intake Dashboard, Order Intake Detail, Backlog, Backlog Details, Backlog by Rep, Summary) — the two Extended pages and the Navigation pages have not been rebuilt yet.

Deferred to Phase 11 rebuild; documented at page-level in `odata-production-report-inventory.md`.

---

## Diff summary — decisions required

| Decision | Recommendation | Blocker on |
|---|---|---|
| Add `KRW-NA_FF_FORECAST` (invoice-side forecast dataflow) to AWIP? | **YES** — enables direct measure parity with production for the ISO Rate Fcst tile | User approval + Kingspan dataflow ID |
| Add Salesforce Quote / Quote Line Item to AWIP? | **DEFER** — pending Ana / James confirmation of scope | Business decision |
| Keep AWIP's 8 extra dataflows (Territory, Zipcodes, PLstructure, HISTSB1, cost accounting, CAPEX)? | **KEEP** — but hide from the report field picker to keep the field list clean. They may be needed for future non-Amalgamated-Sales pages. | User preference |
| Adopt production's role-playing dim copies pattern? | **NO** — stick with AWIP's shared `DimDate` + shared dim copies. Simpler, less overhead. Confirmed FUNCTIONALLY EQUIVALENT. | — |
| Reconstruct the 15 missing forecast/YTD measures in AWIP? | **YES** — needed for Extended dashboards, Summary page, and PY comparison. Deferred to Phase 9. | `KRW-NA_FF_FORECAST` import + `[Current FYP]` pattern |
| Reconcile `SB` vs `SB 2` duplicate measures | **DELETE the "2" duplicates** after value-domain probe confirms they return the same values under all filters | Phase 5 verification |
| Change AWIP's `Billing[State_Name]→GEOINFO[State]` relationship to production's `KNA1→GEOINFO[COUNTRY_REGION]`? | **NO** — production's KNA1 join is absorbed into AWIP fact-table columns. AWIP's State join is a different, but valid, path. | — |

**Written:** 2026-08-13

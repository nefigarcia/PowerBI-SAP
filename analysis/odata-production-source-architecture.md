# OData Production Source Architecture

**Scope:** Classify every table referenced by the OData production reference (`production-reference-odata/Amalgamated Sales Reports - JC.pbip`) into one of the six categories below, and map each to its intended AWIP replacement path.

**Classification categories:**
1. **SAP Datasphere OData Billing** — replaceable by `Billing` OData connection (AWIP already has this)
2. **SAP Datasphere OData SalesOrders** — replaceable by `SalesOrders` OData connection (AWIP already has this)
3. **Power BI Dataflow** — sourced via `PowerPlatform.Dataflows` (non-`_SAP_` only per rule)
4. **Salesforce** — sourced via `Salesforce.Data` connector
5. **Derived model object** — calculated table / measure-only table / disconnected slicer
6. **Auto-generated** — Time Intelligence `LocalDateTable_*` / `DateTableTemplate_*` (out of scope)

---

## Master classification table (production tables → category → AWIP replacement)

### Fact-stream tables (SAP-sourced in production, Datasphere OData in AWIP)

| Production table | AAS cube | Category | AWIP replacement | Fields / notes |
|---|---|---|---|---|
| `KRW_NA_SAP_VBRP` | INVOICED | (excluded — `_SAP_`) | `Billing` (Datasphere OData) | Billing document + item; source of Invoiced Sales pages |
| `KRW_NA_SAP_VBAP OI` | SORDERS | (excluded — `_SAP_`) | `SalesOrders` (Datasphere OData) | Sales-order intake; source of Order Intake pages |
| `KRW_NA_SAP_VBAP SB` | BACKLOG | (excluded — `_SAP_`) | `SalesOrders` (Datasphere OData, filter to open orders) | Uses the same underlying VBAP with backlog semantics; AWIP's `SalesOrders` already has `Revenue_Backlog`, `Open_*`, `Gross_Margin_for_open_orders` native columns |

**Rationale:** All three `VBAP*/VBRP` variants collapse to the two AWIP OData fact tables. The BACKLOG cube is not a distinct data set — it's the same VBAP with backlog-relevant projections. AWIP already has the columns needed to reproduce this without a separate table.

### SAP master-data tables (excluded — fields already promoted to fact tables in AWIP)

| Production table | Category | AWIP replacement | Notes |
|---|---|---|---|
| `KRW_NA_SAP_KNA1` (+ OI + SB) | (excluded — `_SAP_`) | Native columns on `Billing` / `SalesOrders` | Customer master; AWIP has `CustomerFullName`, `SoldToParty_D12_T`, `Sales_Representative_T` etc. |
| `KRW_NA_SAP_KNVV` (+ OI + SB) | (excluded — `_SAP_`) | Native columns on `Billing` / `SalesOrders` | Sales-area / AAGC data; AWIP has `CustomerAccountAssignmentGroup_T` etc. |
| `KRW_NA_SAP_LIKP` | (excluded — `_SAP_`) | (not directly needed for AWIP scope) | Delivery header — used only in Invoiced-side joins in production; AWIP fact tables already carry the joined result columns |
| `KRW_NA_SAP_LIPS` | (excluded — `_SAP_`) | (not directly needed for AWIP scope) | Delivery item — same |
| `KRW_NA_SAP_MARM_BFT` (×2) | (excluded — `_SAP_`) | Native columns on `Billing` / `SalesOrders` | Material unit-of-measure conversions; AWIP has `Factor_UoM_BFT`, `Billing_Quantity_in_BFT` etc. |
| `KRW_NA_SAP_TVAPT` | (excluded — `_SAP_`) | Native `_T` text columns on fact tables | Sales-document-type text table |
| `KRW_NA_SAP_TVM3T` | (excluded — `_SAP_`) | Native `_T` text columns on fact tables | Material-group text table |
| `KRW_NA_SAP_VBPA2` | (excluded — `_SAP_`) | Native partner columns on fact tables | Partner functions; AWIP has `_T` variants for each partner direction |

### Non-`_SAP_` Dataflows (VALID sources per rule — used by AWIP and production)

| Production table | Category | AAS cube (prod) | AWIP replacement | Verified in AWIP? |
|---|---|---|---|---|
| `KRW_NA_FF_CALENDAR` | Power BI Dataflow | INVOICED | `KRW_NA_FF_CALENDAR` (AWIP dataflow) | ✅ present, workspace `24b96353-…`, dataflowId `ba1d8f9b-…` |
| `KRW_NA_FF_CALENDAR OI` | Power BI Dataflow (role-playing copy) | SORDERS | (single AWIP `KRW_NA_FF_CALENDAR` used for both fact tables — AWIP uses shared model instead of role-playing) | ✅ implicit — one copy is enough for AWIP's shared-model pattern |
| `KRW_NA_FF_CALENDAR SB` | Power BI Dataflow (role-playing copy) | BACKLOG | same as above | ✅ implicit |
| `KRW_NA_FF_FISCALPERIOD` (+ OI + SB) | Power BI Dataflow | INVOICED / SORDERS / BACKLOG | `KRW_NA_FF_FISCALPERIOD` (AWIP dataflow, single copy) | ✅ present |
| `KRW-NA_FF_FORECAST` **(hyphen)** | Power BI Dataflow | INVOICED | ⚠ **NOT in AWIP** — this is the invoice-side forecast; AWIP has `KRW_NA_FF_FORECAST_INTAKE` (order-side) but not the invoice-side variant | ❌ gap for Phase 6 |
| `KRW_NA_FF_FORECAST_INTAKE` | Power BI Dataflow | SORDERS | `KRW_NA_FF_FORECAST_INTAKE` | ✅ present |
| `KRW_NA_FF_GEOINFO` (+ OI + SB) | Power BI Dataflow | INVOICED / SORDERS / BACKLOG | `KRW_NA_FF_GEOINFO` (single copy) | ✅ present |

### Derived model objects (in the TMDL, not sourced externally)

| Production table | Category | Purpose | AWIP replacement |
|---|---|---|---|
| `FiscalYearPeriods Slicer` | Derived (disconnected slicer) | UI-side fiscal-year-period picker for INVOICED cube | AWIP needs equivalent — could reuse `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` directly since AWIP uses a shared dim |
| `FiscalYearPeriods Slicer OI` | Derived (disconnected slicer, role-copy) | Same for SORDERS cube | same |
| `FiscalYearPeriods Slicer SB` | Derived (disconnected slicer, role-copy) | Same for BACKLOG cube | same |

### Salesforce (external — currently not in AWIP)

| Production table | Category | Source | AWIP status |
|---|---|---|---|
| `Salesforce Quote Line Item` | Salesforce | `Salesforce.Data("https://krw.my.salesforce.com/", [ApiVersion=48])` entity `QuoteLineItem` | ❌ NOT in AWIP |
| `Salesforce Quotes` | Salesforce | same connector, entity `Quote` | ❌ NOT in AWIP |

### Auto-generated (out of scope)

| Category | Count | Notes |
|---|---|---|
| Time Intelligence `LocalDateTable_*` | 20 | Auto-generated per date column when `__PBI_TimeIntelligenceEnabled = 1` |
| `DateTableTemplate_*` | 1 | Template for the above |

---

## AWIP dataflow inventory (recap, cross-referenced)

For completeness — the 13 dataflows AWIP currently has, classified against the OData production reference. None contain `_SAP_`, so all pass the rule.

| AWIP dataflow | Also in OData production? | Purpose in AWIP |
|---|---|---|
| `KRW_NA_FF_CALENDAR` | ✅ (as 3 role-copies) | Calendar dim |
| `KRW_NA_FF_FISCALPERIOD` | ✅ (as 3 role-copies) | Fiscal calendar |
| `KRW_NA_FF_GEOINFO` | ✅ (as 3 role-copies) | State geography + Country_Region rollup |
| `KRW_NA_FF_FORECAST_INTAKE` | ✅ (single copy) | Order-side forecast (fiscal-period grain) |
| `KRW_NA_FF_TERRITORY` | ❌ not in OData production | Territory dim (AWIP-only extra) |
| `KRW_NA_FF_ZIPCODES` | ❌ not in OData production | Zip → territory bridge (AWIP-only extra) |
| `KRW_NA_FF_PLSTRUCTURE` | ❌ not in OData production | P&L / Tagetik structure (AWIP-only extra, different report scope) |
| `KRW_NA_FF_HISTSB1` | ❌ not in OData production | CAPEX-related postings (AWIP-only extra, different report scope) |
| `KRW_NA_FF_COSTCENTREHIER` | ❌ not in OData production | Cost centre hierarchy (AWIP-only, different report scope) |
| `KRW_NA_FF_COSTCTHIER_ONDULINE` | ❌ not in OData production | Onduline cost centres (AWIP-only, different report scope) |
| `KRW_NA_FF_COSTELEM_OH1` | ❌ not in OData production | Cost element leaf list (AWIP-only, different report scope) |
| `KRW_NA_FF_COSTELEMHIER` | ❌ not in OData production | Cost element hierarchy (AWIP-only, different report scope) |
| `'CAPEX Approved'` | ❌ not in OData production | CAPEX orders (AWIP-only, different report scope) |

**Observation:** AWIP has 8 dataflows that are **not** in OData production. These support CAPEX / P&L / cost-accounting scopes that are outside the Amalgamated Sales Reports scope. Two options for Phase 9:
1. Keep them in the AWIP model but hide them (they're loaded but not referenced by any relationship or visual in the sales-report pages).
2. Remove them entirely if AWIP is scoped to Amalgamated Sales only.

Business decision — do not change without asking Ana / James.

---

## Missing from AWIP (Phase-7 gap list)

The following tables exist in OData production but are missing from AWIP:

1. **`KRW-NA_FF_FORECAST` (hyphen — invoice-side forecast)** — this is the source of `Sales Membrane sqft` / `Sales ISO bdft` / `Sales $` / `ISO Rate Forecast` for the INVOICED cube. AWIP's current fix routes the equivalent measure through `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` (a native column). That works but may diverge from production numbers if the forecast is maintained upstream on a different grain. **Recommendation:** add `KRW-NA_FF_FORECAST` as a new dataflow import to AWIP so both sides of the ISO Rate Fcst calculation (Invoiced-side and Order-Intake-side) use the same source pattern that production does.
2. **`Salesforce Quote Line Item` + `Salesforce Quotes`** — required for any Extended-dashboard visual that shows quote data. Confirmed present in production. Awaiting business decision on whether to wire up Salesforce connection.
3. **AAS-cube measures** (e.g. `Sum Billing Qty. in FT2 for Membranes`, `Revenue`, `Current FYP VBRP`, `Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year`) — these live inside the AAS cubes and are invisible in the TMDL. AWIP has to reconstruct them from `Billing` / `SalesOrders` columns. Some are trivial (`Revenue = SUM(Billing[Revenue])`), some need real work (prior-year variants need SAMEPERIODLASTYEAR patterns).

---

## Architectural comparison — production vs AWIP

| Aspect | OData production | AWIP development |
|---|---|---|
| Fact-table connection | DirectQuery to 3 AAS databases | Import from 2 Datasphere OData views |
| Fact-table role-playing | 3 copies of every dim (INVOICED / OI / SB) | Single shared `DimDate` + single dataflow dim copies |
| Number of fact tables | 3 conceptual (Billing / OI / Backlog) via 2 SAP tables (VBRP, VBAP) | 2 fact tables (`Billing`, `SalesOrders`); backlog is a subset of `SalesOrders` |
| Measures in TMDL | 17 (all on FORECAST tables) | ~19 in `_Measures` + several on `Billing` and `SalesOrders` |
| Measures in AAS cubes | many (invisible to TMDL) | n/a — AWIP has to reconstruct these in DAX |
| Data-refresh model | DirectQuery — live | Import — scheduled refresh |
| Table naming | `KRW_NA_SAP_*` for SAP, `KRW_(-|_)NA_FF_*` for dataflows | `Billing`, `SalesOrders`, `KRW_NA_FF_*` for dataflows |

---

## Summary tally

| Category | Count in production | Count in AWIP replacement |
|---|---|---|
| SAP-sourced (excluded per rule) | 16 tables (`_SAP_`) | replaced by 2 Datasphere OData tables (`Billing`, `SalesOrders`) |
| Power BI Dataflows (valid) | 13 (5 unique × role-copies) | 13 (all unique, no role-copies) |
| Derived / slicer | 3 (`FiscalYearPeriods Slicer` × 3 role-copies) | 1 (`_Measures` calc table) |
| Salesforce | 2 | ❌ 0 (gap) |
| Auto-generated | 21 | (varies — Time Intelligence not enabled in AWIP `model.tmdl`) |

**Written:** 2026-08-13

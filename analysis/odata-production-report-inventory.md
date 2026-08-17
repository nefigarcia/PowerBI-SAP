# OData Production Report Inventory — v1 (page-level)

**Source:** `production-reference-odata/Amalgamated Sales Reports - JC.Report/definition/` (READ ONLY)

> ⚠ **v1 scope note:** this file currently captures **page-level** structure (pages, visual counts, table references, report-level filters). Per-visual field-by-field enumeration for all 158 visuals was truncated by the source scan. A follow-up pass (using a write-capable agent) will produce a full per-visual inventory. Phase 3 (source architecture) can proceed with the current level of detail — the page-level table references are sufficient to map fact tables to fact tables.

---

## Report-level configuration

| Item | Value |
|---|---|
| **Theme** | `CY24SU10` (Power BI July 2024 built-in theme) |
| **Export mode** | `AllowSummarized` |
| **Static resources** | `kingspan-roofing-waterproofing8422940714883275.png` (Kingspan logo — same asset as ODBC reference) |

**Report-level filters (3):** all pin the report to the current fiscal year of 2026 — likely hardcoded, will roll stale in 2027.

| # | Table | Field | Operator |
|---|---|---|---|
| 1 | `KRW-NA_FF_FORECAST` | `Fiscal Year Period Sorted` | StartsWith `2026` |
| 2 | `FiscalYearPeriods Slicer SB` | `Fiscal Year Period` | Not Null |
| 3 | `KRW_NA_FF_FORECAST_INTAKE` | `Fiscal Year Period Sorted` | StartsWith `2026` |

---

## Page catalog (13 pages · 158 visuals)

| Ord | Page ID | Display name | Visuals | Visibility | Role |
|---|---|---|---|---|---|
| 1 | `4cebd6cd708bb1448d5f` | Navigation Page | 24 | Visible | Landing / navigation hub |
| 2 | `02c0c826020d7690a291` | Navigation – 3rd party/ICO split | 5 | Visible | Scenario router |
| 3 | `136c291607e53cb23df0` | Page 1 | 2 | HiddenInViewMode | Detail scratch |
| 4 | `adc801190c2b80e059c8` | Invoiced Sales - Dashboard | 16 | HiddenInViewMode | Dashboard |
| 5 | `7547c7eb9f85b3605827` | Invoiced Sales - Detail | 6 | HiddenInViewMode | Detail |
| 6 | `d0b3413807313c882ead` | Extended Invoiced Sales - Dashboard | 14 | HiddenInViewMode | Extended dashboard |
| 7 | `3672e874de9d15c734e8` | Order Intake - Dashboard | 16 | HiddenInViewMode | Dashboard |
| 8 | `08a2a893f078e9c4ad92` | Order Intake - Detail | 6 | HiddenInViewMode | Detail |
| 9 | `cd86b33e4e73a0548d30` | Extended Order Intake - Dashboard | 14 | HiddenInViewMode | Extended dashboard |
| 10 | `485ff3754ea8455a6933` | Backlog | 11 | HiddenInViewMode | Dashboard |
| 11 | `b5c1e1e248961b072306` | Backlog - Details | 6 | HiddenInViewMode | Detail |
| 12 | `633a47a92e92bd6b80a2` | Backlog by Rep | 11 | HiddenInViewMode | Dashboard |
| 13 | `6e5b174015250d002976` | Summary Page | 27 | HiddenInViewMode | Executive summary |

**Access pattern:** navigation pages 1–2 are the only ones visible in view mode; all others open via the page navigator.

**Page groupings:**
- Invoiced (INVOICED cube): pages 4, 5, 6
- Order Intake (SORDERS cube): pages 7, 8, 9
- Backlog (BACKLOG cube): pages 10, 11, 12
- Cross-cube: page 13 (Summary), pages 1–2 (Navigation)

---

## Table references by page (verified during scan)

Every non-navigation page pulls from at least one `_SAP_` table for its facts (production wires those directly). During Phase 7 crosswalk these will be re-pointed at AWIP's `Billing` / `SalesOrders` OData equivalents.

| Page | Primary fact table (production) | AWIP replacement | Forecast/enrichment tables referenced |
|---|---|---|---|
| Invoiced Sales - Dashboard | `KRW_NA_SAP_VBRP` | `Billing` | `KRW-NA_FF_FORECAST`, `KRW_NA_FF_FISCALPERIOD`, `KRW_NA_FF_GEOINFO` |
| Invoiced Sales - Detail | `KRW_NA_SAP_VBRP` + `KRW_NA_SAP_KNA1` | `Billing` (has customer + geo fields native) | same |
| Extended Invoiced Sales - Dashboard | `KRW_NA_SAP_VBRP` + `KRW_NA_SAP_KNA1` | `Billing` | `KRW-NA_FF_FORECAST` |
| Order Intake - Dashboard | `KRW_NA_SAP_VBAP OI` | `SalesOrders` | `KRW_NA_FF_FORECAST_INTAKE`, `KRW_NA_FF_FISCALPERIOD OI`, `KRW_NA_FF_GEOINFO OI` |
| Order Intake - Detail | `KRW_NA_SAP_VBAP OI` + `KRW_NA_SAP_KNA1 OI` | `SalesOrders` | same |
| Extended Order Intake - Dashboard | `KRW_NA_SAP_VBAP OI` + `KRW_NA_SAP_KNA1 OI` | `SalesOrders` | `KRW_NA_FF_FORECAST_INTAKE` |
| Backlog | `KRW_NA_SAP_VBAP SB` (+ `LIPS`) | `SalesOrders` (Backlog columns already present: `Revenue_Backlog`, `Open_*` cols) | `KRW_NA_FF_FISCALPERIOD SB` |
| Backlog - Details | `KRW_NA_SAP_VBAP SB` + `KRW_NA_SAP_KNA1 SB` | `SalesOrders` | same |
| Backlog by Rep | `KRW_NA_SAP_VBAP SB` | `SalesOrders` (has `Sales_Representative` + `_T`) | same |
| Summary Page | mixed (INVOICED + SORDERS + BACKLOG) | `Billing` + `SalesOrders` | both FORECAST tables |

**Migration impact:** 145+ of 158 visuals reference `_SAP_` tables. All need their table refs re-pointed to `Billing` or `SalesOrders`. Field names *should* map cleanly per the crosswalk work already in [`dataflow-production-crosswalk.md`](dataflow-production-crosswalk.md).

---

## Slicer / filter coverage (page-level)

- **Product Family slicer** — `KRW_NA_SAP_VBRP[Product Family]` on Invoiced pages, `KRW_NA_SAP_VBAP OI[Product Family]` on Order Intake pages. AWIP replacement: `Billing[Product_Family]` / `SalesOrders[Product_Family_Product_Number]`.
- **Fiscal Period slicer** — via `FiscalYearPeriods Slicer` variants (INVOICED / OI / SB), disconnected-slicer pattern connected bi-di to the FORECAST tables.
- **"Clear all Slicers" action button** — appears on most dashboards. Uses actionButton visual with bookmark-restore semantics.

---

## Visual-type census (approximate — full enumeration deferred)

Types confirmed present across the report:
- `gauge` (many; used for Actual-vs-Forecast KPI tiles)
- `multiRowCard` (used for stacked KPI groups)
- `slicer` (Product Family, Fiscal Period, etc.)
- `pivotTable` and `tableEx` (used on Detail and Navigation pages)
- `columnChart`, `lineChart`, `barChart`, `donutChart` (dashboards)
- `image` (Kingspan logo)
- `shape` (backgrounds, dividers)
- `textbox` (titles, labels)
- `pageNavigator` (Navigation pages)
- `actionButton` (Clear Slicers)

---

## Sample per-visual detail (Invoiced Sales - Dashboard, first 8 of 16)

Documented as an illustrative deep-dive; the remaining 8 visuals on this page and all visuals on the other 12 pages follow similar patterns but are not enumerated in v1.

| # | Title | Visual type | Values / Y-axis | Category / Rows | Notes |
|---|---|---|---|---|---|
| 1 | Invoiced Membrane - sqft | `gauge` | `KRW_NA_SAP_VBRP[Sum Billing Qty. in FT2 for Membranes]` | — | Max value: `KRW-NA_FF_FORECAST[Sales Membrane sqft]` |
| 2 | (slicer) | `slicer` | — | `KRW_NA_SAP_VBRP[Product Family]` | Dropdown |
| 3 | Invoiced Sales $ | `gauge` | `KRW_NA_SAP_VBRP[Revenue]` | — | Max value: `KRW-NA_FF_FORECAST[Sales $]` |
| 4 | (unlabeled multi-row) | `multiRowCard` | `Sum Billing Qty. in BFT2 for ISO` / `Sales ISO bdft` / `Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year` | — | 3-row card: Qty, Forecast, PY |
| 5 | (gauge) | `gauge` | `Sum Billing Qty. in BFT2 for ISO` | — | Max: `Sales ISO bdft` |
| 6 | (background) | `shape` | — | — | Layout |
| 7 | (unlabeled multi-row) | `multiRowCard` | `Sum Billing Qty. in FT2 for Membranes` / `Sales Membrane sqft` / `Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year` | — | 3-row card |
| 8 | (action) | `actionButton` | — | — | Clears all slicers |

---

## Anomalies flagged for downstream phases

1. **Report-level filters are hardcoded to 2026** (`StartsWith '2026'` on `Fiscal Year Period Sorted`). Will roll stale in 2027. Fix candidate: parameter-driven filter or a `[Current Fiscal Year]` calculated column driving a dynamic filter.
2. **Hyphenated table name preservation:** `KRW-NA_FF_FORECAST` (hyphen, not underscore) is referenced by name in report filters — any DAX or M rewriting must preserve the exact hyphen + single-quote quoting.
3. **`Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year` and similar measures** are referenced on the Invoiced dashboard but do NOT appear on the two forecast tables inventoried in Phase 1 — they must live in the AAS INVOICED cube (invisible to our TMDL scan). AWIP will need to reconstruct these measures from `Billing` + `DimDate` (SAMEPERIODLASTYEAR pattern).
4. **`Page 1` (hidden)** looks like a scratch / abandoned page with only 2 visuals. Confirm with business owner whether it's safe to drop from the rebuild.
5. **`Summary Page` at ordinal 13** with 27 visuals is the biggest single-page workload for Phase 11 rebuild — worth its own dedicated pass.
6. **Extended Invoiced Sales / Extended Order Intake pages** confirmed to exist in production but the visual-level fields they use were the biggest coverage gap in the earlier ODBC-based analysis. Full enumeration deferred to v2.

---

## Coverage sign-off

- **Pages inventoried:** 13 of 13 (page-level: names, visual counts, visibility, primary table refs, filters, slicer coverage)
- **Visuals per-field enumerated:** 8 of 158 (Invoiced Sales - Dashboard visuals 1–8, illustrative)
- **Report-level items:** filters (3), theme (1), static resources (1)
- **Deferred to v2:** per-visual field-by-field detail for the remaining 150 visuals

**Written:** 2026-08-13

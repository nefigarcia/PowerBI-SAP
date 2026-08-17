# Phase 11 — Report Rebuild Playbook

**Objective:** align AWIP's report pages with the OData production report (`Amalgamated Sales Reports - JC`) page-by-page. Preserve AWIP's older single-file `report.json` format — **do NOT migrate to the new folder-per-page format**.

**Source of truth:** `production-reference-odata/Amalgamated Sales Reports - JC.Report/definition/pages/` (13 pages, 158 visuals).

**Target of change:** `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.Report/report.json` (currently 8 sections, 81 visuals).

**Read-only assumption for this document.** Every actual edit happens in Power BI Desktop (or by a follow-up task that carefully patches the monolithic `report.json`); this file only tells the user WHAT to do.

**Table-name discipline used everywhere below:**

| Production ref | AWIP ref |
|---|---|
| `KRW_NA_SAP_VBRP[...]` | `Billing[...]` |
| `KRW_NA_SAP_VBAP OI[...]` | `SalesOrders[...]` |
| `KRW_NA_SAP_VBAP SB[...]` | `SalesOrders[...]` (backlog subset — filter `Open_order_qty_flag = "Y"`) |
| `KRW_NA_SAP_KNA1[...]` / `KNVV[...]` | native columns already on `Billing` / `SalesOrders` |
| `KRW_NA_FF_CALENDAR OI` / `SB` | `KRW_NA_FF_CALENDAR` (single shared) |
| `KRW_NA_FF_FISCALPERIOD OI` / `SB` | `KRW_NA_FF_FISCALPERIOD` |
| `KRW_NA_FF_GEOINFO OI` / `SB` | `KRW_NA_FF_GEOINFO` |
| `[Product Family]` on VBRP | `Billing[Product_Family]` |
| `[Product Family]` on VBAP OI/SB | `SalesOrders[Product_Family_Product_Number]` |
| `[Fiscal Year Period Sorted]` on FORECAST | `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]` (hyphen preserved) |
| `[Revenue in DC with Sign]` on VBRP | `Billing[Revenue]` |
| `[Revenue in DC with Sign]` on VBAP OI | `SalesOrders[Revenue_Order_Intake]` |
| `[Revenue in DC with Sign]` on VBAP SB | `SalesOrders[Revenue_Backlog]` (open-order subset) |
| `[Billing Qty. in FT2]` | `Billing[Billing_Quantity_in_FT2]` |
| `[Billing Qty. in BFT2]` | `Billing[Billing_Quantity_in_BFT]` (BFT vs BFT2 caveat — see Phase 5 v2) |
| `[Order Qty. in FT2]` | `SalesOrders[Order_Quantity_in_FT2]` |
| `[Order Qty. in BFT2]` | `SalesOrders[Requested_Quantity_in_BFT]` |
| `[Customer Description]` | `Billing[CustomerFullName]` / `SalesOrders[SoldToParty_D12_T]` |
| `[Account Assignment Group Description]` | `Billing[CustomerAccountAssignmentGroup_T]` (equivalent on SalesOrders) |
| `[Sales Representative]` | `Billing[Sales_Representative_T]` / `SalesOrders[Sales_Representative_T]` |
| `[State]` on GEOINFO | `KRW_NA_FF_GEOINFO[State]` |
| `[Ship-to State Name]` on VBRP | `Billing[ShipToParty_State_T]` (or equivalent — verify against column inventory) |

---

## 0. Current AWIP state (baseline)

**Total sections:** 8 pages · **Total visuals:** 81
Extracted from `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.Report/report.json`, sections[] with visualContainers[].

| Ord | Section (name in file) | Visuals | Notes |
|---|---|---|---|
| — | Backlog - Details | 7 | ordinal missing on this section — appears first in the sections array; treat as a hidden detail page |
| 1 | Extended Invoiced Sales - Dashboard Error | 7 | AWIP-only "Error" scratch page — Extended Invoiced not properly built |
| 2 | Invoiced Sales - Dashboard | 20 | Active default page (activeSectionIndex = 2 in report config). Closest to production. |
| 3 | Extended Order Intake - Dashboard | 7 | Skeleton — needs a rebuild pass |
| 4 | Invoiced Sales - Detail | 8 | Table + slicers only; matches production shape |
| 5 | Order Intake - Detail | 8 | Table + slicers only; matches production shape |
| 6 | Backlog | 12 | Card / gauge / donut / tableEx — most complete AWIP dashboard |
| 7 | Order Intake - Dashboard | 12 | Cards / gauges / donut; missing "Trend Over Time" etc. |

**Static resources on the AWIP side:** custom theme `AWIP6636503754310693.json`, base theme `CY26SU07`, `kingspan-logo.png` (also loaded as `kingspan-roofing-waterproofing8422940714883275.png`).

**Report-level filters on AWIP:** none currently declared in the config header (verify by inspecting the report-level filter tray in Desktop).

---

## 1. Gap analysis — pages in production but missing (or thin) in AWIP

| # | Production page name | Prod visuals | In AWIP? | AWIP page name (if renamed) | Rebuild priority |
|---|---|---|---|---|---|
| 1 | Navigation Page | 24 | ❌ MISSING | — | **H** — this is the landing hub the user opens the report on |
| 2 | Navigation – 3rd party/ICO split | 5 | ❌ MISSING | — | **M** — depends on Account Assignment Group data; useful but not critical |
| 3 | Page 1 (hidden scratch) | 2 | ❌ MISSING | — | **L** — production's own README flags this as an abandoned scratch page; **skip** |
| 4 | Invoiced Sales - Dashboard | 16 | ✅ PRESENT (20 visuals) | Invoiced Sales - Dashboard | **H** — biggest KPI page; AWIP already has drafts, just align to prod |
| 5 | Invoiced Sales - Detail | 6 | ✅ PRESENT (8 visuals) | Invoiced Sales - Detail | **M** — mostly a wide table + 3 slicers; low complexity |
| 6 | Extended Invoiced Sales - Dashboard | 14 | ⚠ PARTIAL (7 visuals, page name says "Error") | Extended Invoiced Sales - Dashboard Error | **H** — currently broken/skeleton |
| 7 | Order Intake - Dashboard | 16 | ✅ PRESENT (12 visuals) | Order Intake - Dashboard | **H** — missing 4 visuals + slicers vs prod |
| 8 | Order Intake - Detail | 6 | ✅ PRESENT (8 visuals) | Order Intake - Detail | **M** — mirror of Invoiced Detail; align columns |
| 9 | Extended Order Intake - Dashboard | 14 | ⚠ PARTIAL (7 visuals) | Extended Order Intake - Dashboard | **H** — skeleton, needs full build |
| 10 | Backlog | 11 | ✅ PRESENT (12 visuals) | Backlog | **M** — the closest match already; needs alignment |
| 11 | Backlog - Details | 6 | ✅ PRESENT (7 visuals) | Backlog - Details | **L** — cosmetic alignment only |
| 12 | Backlog by Rep | 11 | ❌ MISSING | — | **H** — the ONLY page with a map (`shapeMap`) driven by `KRW_NA_FF_GEOINFO`; users depend on the by-rep breakdown |
| 13 | Summary Page | 27 | ❌ MISSING | — | **H** — executive dashboard; largest page; cross-cube; expected by leadership |

**Summary:**

- **Fully missing from AWIP:** 4 pages (Nav, Nav-3rd, Backlog-by-Rep, Summary) + optionally 1 scratch (Page 1)
- **Partial / broken in AWIP:** 2 pages (both "Extended" dashboards)
- **Present and roughly aligned:** 6 pages (Invoiced Dash, Invoiced Detail, Order Intake Dash, Order Intake Detail, Backlog, Backlog Details)

---

## 2. Gap analysis — pages in AWIP but not in production

| AWIP page | Purpose (inferred) | Recommendation |
|---|---|---|
| `Extended Invoiced Sales - Dashboard Error` | Placeholder from an earlier failed build attempt (the word "Error" is in the display name). Contains a slicer, an image, 2 textboxes and one multi-row card. | **Rename** to `Extended Invoiced Sales - Dashboard` and rebuild in place (page 6 in prod). Do NOT create a second page. |

No other pages exist in AWIP that don't have a production counterpart. The AWIP ISO Rate investigation work is in the **analysis/** folder (`iso-rate-investigation-status.md`) not in the report itself, so nothing to flag there.

---

## 3. Per-page playbook (13 pages)

For every production page, this section lists each visual, its type, title (if any), the fields it renders, the AWIP-side table/column/measure references, position, and any risk notes.

Position grid is 1280×720 canvas. Positions are approximate — reported to the nearest whole pixel from the production `visual.json` `position` block.

### 3.1 Navigation Page (production id `4cebd6cd708bb1448d5f`) — 24 visuals — **PRIORITY H**

This is the landing page. Left column is a page navigator; the middle+right areas are grouped 6-cell KPI grids (Invoiced, Order Intake, Backlog) with a page-navigation bookmark selector at the top right.

**Section: page-nav column (x≈0)**
- **[00]** `pageNavigator` — pos (0, 0), size 340×720. No fields. Native visual that auto-lists visible pages. Set `Show Icons/Text = true`, order = pageOrder from `pages.json`.

**Section: top-right bookmark chooser**
- **[07]** `bookmarkNavigator` — pos (1207, 0), size 74×40. No fields. Configure to a bookmark group named e.g. "Nav toggles" once you have bookmarks.

**Section: Invoiced KPI grid (rows y≈80 and y≈168)**
- **[01]** `pivotTable` (Revenue current-month) — pos (351, 81), size 460×81. Rows: `Billing[Product_Family]`. Values: three measures — `Billing[Current Fiscal Month Invoiced Revenue]`, `KRW-NA_FF_FORECAST[Current Month Invoice Revenue Fcst]`, `Billing[$ Difference Current Month VBRP]`. **NOTE:** none of these three measures exist in AWIP yet (see Phase 5 v2 gap). Blocked until Phase 10 measure work adds them, or substitute the closer-existing measures: `_Measures[Sales]` for current-month, and skip forecast/diff.
- **[02]** `pivotTable` (Membrane sqft current-month) — pos (351, 81), size 460×80. Rows: `Billing[Product_Family]`. Values: `Billing[Current Fiscal Month Billing Qty. in FT2 for Membranes Split]`, `KRW-NA_FF_FORECAST[Current Month Invoiced Sales Membrane sqft]`. Same blocker as above.
- **[05]** `pivotTable` (YTD Revenue) — pos (819, 81), size 461×81. Rows: `Billing[Product_Family]`. Values: `Billing[YTD Invoiced Revenue Billing Date]`. Blocker: no AWIP YTD-Invoiced-Revenue measure yet.
- **[06]** `pivotTable` (YTD Membrane sqft) — pos (819, 82), size 461×80. Rows: `Billing[Product_Family]`. Values: `Billing[YTD Billing Qty. in FT2 for Membranes]`. Blocker: same.
- **[08]** `pivotTable` (row 2 Revenue) — pos (351, 169), size 460×81. Same fields as [01] (this appears to be a duplicate row for a bookmark-driven layout variant).
- **[09]** `pivotTable` (row 2 ISO qty) — pos (352, 169), size 460×80. Rows: `Billing[Product_Family]`. Values: `Billing[Current Fiscal Month Billing Qty. in FT2 for ISO]`, `KRW-NA_FF_FORECAST[Current Month Invoiced Sales ISO sqft]`, `Billing[Current Fiscal Month Billing Qty. in BFT2 for ISO]`, `KRW-NA_FF_FORECAST[Current Month Invoiced Sales ISO bdft]`.
- **[10]** `pivotTable` (row 2 YTD Revenue) — pos (819, 169), size 461×81. Same as [05].
- **[11]** `pivotTable` (row 2 YTD ISO qty) — pos (819, 169), size 461×80. Rows: `Billing[Product_Family]`. Values: `Billing[YTD Billing Qty. in FT2 for ISO]`, `Billing[YTD Billing Qty. in BFT2 for ISO]`.

**Section: Order Intake KPI grid (rows y≈330 and y≈419)**
- **[14]** `pivotTable` — pos (351, 330), size 460×81. Rows: `SalesOrders[Product_Family_Product_Number]`. Values: `SalesOrders[Current Fiscal Month Order FT2 for Membranes 2]`, `KRW_NA_FF_FORECAST_INTAKE[Current Month Sales Membrane sqft]`.
- **[15]** `pivotTable` — pos (351, 330), size 460×81. Rows: same. Values: `SalesOrders[Current Fiscal Month Order Revenue]`, `KRW_NA_FF_FORECAST_INTAKE[Current Month Order Revenue Fcst Doc Date]`, `SalesOrders[$ Difference]`.
- **[16]** `pivotTable` — pos (819, 330), size 461×80. Rows: same. Values: `SalesOrders[YTD Order FT2 for Membranes]`.
- **[17]** `pivotTable` — pos (819, 330), size 461×81. Rows: same. Values: `SalesOrders[YTD Order Revenue Doc Date]`.
- **[18]** `pivotTable` — pos (351, 419), size 460×80. Rows: same. Values: same as [15] (duplicate for the variant layout).
- **[19]** `pivotTable` — pos (352, 419), size 460×80. Rows: same. Values: `SalesOrders[Current Fiscal Month Order FT2 for ISO Split]`, `KRW_NA_FF_FORECAST_INTAKE[Current Month Sales ISO sqft]`, `SalesOrders[Current Fiscal Month Order BFT for ISO Split]`, `KRW_NA_FF_FORECAST_INTAKE[Current Month Sales ISO bdft 2]`.
- **[20]** `pivotTable` — pos (819, 419), size 461×80. Rows: same. Values: `SalesOrders[YTD Order Revenue Doc Date]`.
- **[21]** `pivotTable` — pos (819, 419), size 461×80. Rows: same. Values: `SalesOrders[YTD Order FT2 for ISO]`, `SalesOrders[YTD Order BFT for ISO]`.

**Section: Backlog chart (bottom)**
- **[22]** `columnChart` — pos (352, 512), size 713×193. Category: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`. Y-axis: `SUM(SalesOrders[Revenue_Backlog])` (production wires this to `KRW_NA_SAP_VBAP SB[Revenue in DC with Sign]`; on AWIP filter for `Open_order_qty_flag = "Y"`).

**Section: labels + logo**
- **[03]** `textbox` — pos (352, 12), size 135×56. "Invoiced" section header.
- **[04]** `textbox` — pos (352, 12), size 135×56. Duplicate (bookmark toggle variant).
- **[12]** `textbox` — pos (350, 263), size 135×56. "Order Intake" section header.
- **[13]** `textbox` — pos (350, 264), size 135×55. Duplicate.
- **[23]** `image` — pos (1065, 650), size 205×70. Kingspan logo (RegisteredResources `kingspan-roofing-waterproofing8422940714883275.png` — AWIP already has this).

**Layout notes:** the 12 KPI pivot tables actually form two states (rows [01–06] and [08–11] look like duplicate rows for a bookmark-driven state selector). If Phase 11 is short on time, build only ONE state (skip the duplicates) — the user can add bookmarks later.

**Blocker:** production Navigation Page's KPI tables depend on ~10 measures (`Current Fiscal Month …`, `YTD …`, `$ Difference …`) that don't exist in AWIP. These are all listed in the "missing 78" measure gap in `odata-measure-validation-v2.md`. **Recommend:** rebuild Navigation Page LAST, after Phase 10 delivers those measures.

---

### 3.2 Navigation – 3rd party/ICO split (production id `02c0c826020d7690a291`) — 5 visuals — **PRIORITY M**

This page splits invoiced/OI by Account Assignment Group (3rd-party vs intercompany).

- **[00]** `pageNavigator` — pos (0, 0), size 395×721.
- **[01]** `pivotTable` (Invoiced by AAG) — pos (410, 12), size 616×178. Columns: `KRW-NA_FF_FORECAST[Fiscal Year Period]`. Rows: `Billing[CustomerAccountAssignmentGroup_T]`. Values: `Billing[Current Fiscal Month Billing Qty. in FT2 for Membranes]`, `Billing[Current Fiscal Month Invoiced Revenue FT2 Membranes]`, `KRW-NA_FF_FORECAST[Current Month Invoice Revenue Fcst]`, `Billing[% Fcst VBRP FM]`.
- **[02]** `pivotTable` (OI by AAG) — pos (410, 200), size 616×176. Columns: `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]`. Rows: `SalesOrders[CustomerAccountAssignmentGroup_T]` (OI-side AAG). Values: `SalesOrders[Current Fiscal Month Order FT2 for Membranes1]`, `SalesOrders[Current Fiscal Month Order Revenue FT2 Membranes]`, `KRW_NA_FF_FORECAST_INTAKE[Current Month Order Revenue Fcst]`, `SalesOrders[% Fcst FM]`.
- **[03]** `barChart` (Backlog by Fiscal Period) — pos (410, 388), size 615×297. Category: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`. Y: `SUM(SalesOrders[Revenue_Backlog])` (filter `Open_order_qty_flag = "Y"`).
- **[04]** `image` — pos (1065, 650), size 205×70. Kingspan logo.

**Blocker:** all four AAG-split measures (`% Fcst VBRP FM`, `% Fcst FM`, `Current Fiscal Month Order Revenue FT2 Membranes`, etc.) are in the "missing 78" list. Same recommendation as 3.1 — defer until Phase 10 delivers.

---

### 3.3 Page 1 (production id `136c291607e53cb23df0`) — 2 visuals — **SKIP**

Hidden scratch page in production. Marked as "confirm with business owner whether it's safe to drop" in the inventory. **Do not build.** If asked, note that it contains a pivot table on `Billing[Product_Family]` with 6 current-vs-PY measures, and a tableEx of `KRW_NA_FF_CALENDAR` dates.

---

### 3.4 Invoiced Sales - Dashboard (production id `adc801190c2b80e059c8`) — 16 visuals — **PRIORITY H**

AWIP has this page with 20 visuals; the shape is close but the field wiring drifted.

**Top ribbon (y≈0, height≈80–100)**
- **[00]** `actionButton` — pos (0, 0), size 85×57. Back / clear-slicers button. Bookmark action = "Clear slicers".
- **[01]** `slicer` — pos (96, 0), size 250×86. Field: `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]`. Style: Dropdown.
- **[02]** `slicer` — pos (381, 0), size 250×86. Field: `Billing[Product_Family]`. Style: Dropdown.
- **[03]** `slicer` — pos (666, 0), size 250×86. Field: `Billing[CustomerAccountAssignmentGroup_T]`. Style: Dropdown.
- **[04]** `shape` — pos (937, 0), size 343×100. Background rectangle behind the ISO Rate cards.
- **[05]** `card` — pos (961, 8), size 148×80. Field: `Billing[ISO Rate IS]` (production `[ISO Rate VBRP]`).
- **[06]** `card` — pos (1109, 8), size 148×80. Field: `Billing[ISO Rate Fcst IS]` (production `[ISO Rate Fcst]` on `KRW-NA_FF_FORECAST`).

**Middle band — 3-row cards (y≈109, height=90)**
- **[07]** `multiRowCard` (Revenue vs Fcst vs PY) — pos (1, 109), size 420×90. Values: `SUM(Billing[Revenue])`, `SUM(KRW-NA_FF_FORECAST[Sales $])`, `Billing[Revenue For Fiscal Month Previous Year]` — the last measure is MISSING in AWIP, substitute `_Measures[Sales PY]` for now.
- **[08]** `multiRowCard` (Membrane sqft) — pos (430, 109), size 420×90. Values: `Billing[Sum Billing Qty. in FT2 for Membranes]`, `SUM(KRW-NA_FF_FORECAST[Sales Membrane sqft])`, `Billing[Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year]` (MISSING; substitute `_Measures[Sales Quantity PY]` filtered to Membranes).
- **[09]** `multiRowCard` (ISO bdft) — pos (860, 109), size 420×90. Values: `Billing[Sum Billing Qty. in BFT2 for ISO]`, `SUM(KRW-NA_FF_FORECAST[Sales ISO bdft])`, `Billing[Sum Billing Qty. in FT2 for ISO Fiscal Month Prior Year]` (MISSING).

**Middle band — gauges (y≈202, height=160)**
- **[10]** `gauge` (Revenue) — pos (0, 202), size 420×160. Y-axis: `SUM(Billing[Revenue])`. MaxValue: `SUM(KRW-NA_FF_FORECAST[Sales $])`.
- **[11]** `gauge` (Membranes sqft) — pos (430, 202), size 420×160. Y-axis: `Billing[Sum Billing Qty. in FT2 for Membranes]`. MaxValue: `SUM(KRW-NA_FF_FORECAST[Sales Membrane sqft])`.
- **[12]** `gauge` (ISO bdft) — pos (860, 202), size 420×160. Y-axis: `Billing[Sum Billing Qty. in BFT2 for ISO]`. MaxValue: `SUM(KRW-NA_FF_FORECAST[Sales ISO bdft])`.

**Bottom — detail table + actions**
- **[13]** `tableEx` — pos (0, 370), size 1280×261. Fields: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`, `Billing[BillingDocument]`, `Billing[CustomerFullName]`, `Billing[Product_Family]`, `Billing[Secondary_Grouping]` (verify column name — may be `Product_Group_Secondary`), `Billing[Material_D17_T]`, `SUM(Billing[Billing_Quantity_in_FT2])`, `SUM(Billing[Billing_Quantity_in_BFT])`, `SUM(Billing[Unit_Price_in_DC])`, `Billing[Price_UoM]`, + ~18 more columns (matches Invoiced Detail table structure).
- **[14]** `actionButton` (Clear all slicers) — pos (10, 656), size 200×49.
- **[15]** `image` (logo) — pos (1065, 650), size 205×70.

**⚠ Known risk:** `tableEx` has crashed in this project before. If it crashes on load, delete and rebuild as a standard `Table` visual with the same field list.

**Where AWIP diverges (extras to reconcile):**
AWIP has today an extra `donutChart` (Sales by Product Family), an extra `lineChart` (Trend Over Time), a duplicate slicer on `Billing[ProductGroup]`, and an extra gauge that mixes `Billing[Revenue]` with `KRW_NA_FF_FORECAST_INTAKE[Sales $]` (wrong — FORECAST_INTAKE is for OI, not Invoiced). Recommend: delete AWIP's Trend line + Sales-by-Family donut + duplicate slicer + wrong-source gauge to align with production.

---

### 3.5 Invoiced Sales - Detail (production id `7547c7eb9f85b3605827`) — 6 visuals — **PRIORITY M**

Mostly a big table + slicers.

- **[00]** `tableEx` — pos (0, 98), size 1280×532. Same field list as [13] in section 3.4 above (`KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`, `Billing[BillingDocument]`, `Billing[CustomerFullName]`, `Billing[Product_Family]`, `Billing[Secondary_Grouping]`, `Billing[Material_D17_T]`, `SUM(Billing[Billing_Quantity_in_FT2])`, `SUM(Billing[Billing_Quantity_in_BFT])`, `SUM(Billing[Unit_Price_in_DC])`, `Billing[Price_UoM]`, + ~18 more). ⚠ **tableEx risk** — rebuild as `Table` if it crashes.
- **[01]** `actionButton` (back) — pos (0, 0), size 85×57.
- **[02]** `slicer` — pos (120, 0), size 280×86. Field: `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]`.
- **[03]** `slicer` — pos (437, 0), size 280×86. Field: `Billing[Product_Family]`.
- **[04]** `slicer` — pos (753, 0), size 280×86. Field: `Billing[CustomerAccountAssignmentGroup_T]`.
- **[05]** `image` — pos (1065, 650), size 205×70. Kingspan logo.

**AWIP has extras to remove:** `cardVisual` (Filtered Revenue), slicers on `Billing[BillingDocumentType]`, `Billing[FiscalYearPeriod]`, `Billing[FC_Product_Group]`, `Billing[MaterialGroup]`. Keep only if a business user asked for them; production's Detail page only has 3 slicers (Fiscal Period, Product Family, AAG).

---

### 3.6 Extended Invoiced Sales - Dashboard (production id `d0b3413807313c882ead`) — 14 visuals — **PRIORITY H**

Currently in AWIP as `Extended Invoiced Sales - Dashboard Error` — must be rebuilt entirely.

**Top ribbon**
- **[00]** `actionButton` — pos (0, 0), size 85×57. Clear slicers.
- **[01]** `slicer` — pos (91, 0), size 160×86. Field: `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]`.
- **[02]** `slicer` — pos (259, 0), size 160×86. Field: `Billing[Product_Family]`.
- **[03]** `slicer` — pos (427, 0), size 160×86. Field: `Billing[CustomerAccountAssignmentGroup_T]`.
- **[04]** `card` (Revenue) — pos (600, 0), size 220×100. Field: `Billing[Sum Revenue in DC with sign IS]`.
- **[05]** `card` (Membrane sqft) — pos (830, 0), size 220×100. Field: `Billing[Sum Billing Qty. in FT2 for Membranes]`.
- **[06]** `card` (ISO bdft) — pos (1060, 0), size 220×100. Field: `Billing[Sum Billing Qty. in BFT2 for ISO]`.

**Chart row 1 (y≈107, height≈230)**
- **[07]** `clusteredColumnChart` (Avg unit price by Secondary Grouping) — pos (11, 107), size 620×230. Category: `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]`. Series: `Billing[Secondary_Grouping]`. Y: `AVERAGE(Billing[Unit_Price_in_DC])`.
- **[08]** `columnChart` (ISO AOP over time) — pos (650, 107), size 620×230. Category: `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]`. Y: `Billing[ISO AOP - $/bdft IS]`.

**Chart row 2 (y≈355, height≈289)**
- **[09]** `barChart` (Revenue by Material) — pos (11, 355), size 409×289. Category: `Billing[Material_D17_T]`. Y: `SUM(Billing[Revenue])`.
- **[10]** `donutChart` (Revenue by Sales Rep) — pos (435, 355), size 410×289. Category: `Billing[Sales_Representative_T]`. Y: `SUM(Billing[Revenue])`.
- **[11]** `barChart` (Revenue by Customer) — pos (860, 355), size 410×289. Category: `Billing[CustomerFullName]`. Y: `SUM(Billing[Revenue])`.

**Bottom**
- **[12]** `actionButton` (Clear all slicers) — pos (10, 656), size 200×49.
- **[13]** `image` (logo) — pos (1065, 650), size 205×70.

---

### 3.7 Order Intake - Dashboard (production id `3672e874de9d15c734e8`) — 16 visuals — **PRIORITY H**

AWIP has 12 visuals; missing: the 3 top slicers, the AAG slicer, the tableEx, and the actionButton.

**Top ribbon**
- **[00]** `actionButton` (Back) — pos (0, 0), size 85×57.
- **[01]** `slicer` — pos (97, 0), size 250×86. Field: `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]`.
- **[02]** `slicer` — pos (378, 0), size 250×86. Field: `SalesOrders[Product_Family_Product_Number]`.
- **[03]** `slicer` — pos (659, 0), size 249×86. Field: `SalesOrders[CustomerAccountAssignmentGroup_T]`.
- **[04]** `shape` (background) — pos (937, 0), size 343×100.
- **[05]** `card` — pos (960, 8), size 148×80. Field: `SalesOrders[ISO Rate OI]` (production `[ISO Rate VBAP]`).
- **[06]** `card` — pos (1109, 8), size 148×80. Field: `SalesOrders[ISO Rate Fcst OI]` (production `[ISO Rate Fcst VBAP]`).

**3-row cards**
- **[07]** `multiRowCard` (Revenue) — pos (1, 109), size 420×90. Values: `SUM(SalesOrders[Revenue_Order_Intake])`, `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales $])`, `SalesOrders[Revenue Fiscal Month Previous Year OI]` (MISSING; substitute `_Measures[Order Intake PY]`).
- **[08]** `multiRowCard` (Membrane sqft) — pos (430, 109), size 420×90. Values: `SalesOrders[Sum Order Qty. in FT2 for Membranes OI]`, `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft])`, `SalesOrders[Sum Order Qty. in FT2 for Membranes Fiscal Month Prior Year OI]` (MISSING).
- **[09]** `multiRowCard` (ISO bdft) — pos (860, 109), size 420×90. Values: `SalesOrders[Sum Order Qty. in BFT2 for ISO OI]`, `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales ISO bdft])`, `SalesOrders[Sum Order Qty. in BFT2 for ISO Fiscal Month Prior Year OI]` (MISSING).

**Gauges (y≈202)**
- **[10]** `gauge` — pos (0, 202), size 420×160. Y: `SUM(SalesOrders[Revenue_Order_Intake])`. Max: `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales $])`.
- **[11]** `gauge` — pos (430, 202), size 420×160. Y: `SalesOrders[Sum Order Qty. in FT2 for Membranes OI]`. Max: `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft])`.
- **[12]** `gauge` — pos (860, 202), size 420×160. Y: `SalesOrders[Sum Order Qty. in BFT2 for ISO OI]`. Max: `SUM(KRW_NA_FF_FORECAST_INTAKE[Sales ISO bdft])`.

**Bottom detail**
- **[13]** `tableEx` — pos (0, 367), size 1280×258. Fields: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`, `SalesOrders[SoldToParty_D12_T]`, `SalesOrders[Product_Family_Product_Number]`, `SalesOrders[Product_Group_Secondary]` (verify column name), `SalesOrders[Material_D17_T]`, `SUM(SalesOrders[Order_Quantity_in_FT2])`, `SUM(SalesOrders[Requested_Quantity_in_BFT])`, `SUM(SalesOrders[Unit_Price_in_DC])` (verify column), `SalesOrders[Price_UoM]`, `SUM(SalesOrders[Revenue_Order_Intake])`, + ~17 more. ⚠ tableEx risk.
- **[14]** `actionButton` (Clear slicers) — pos (10, 656), size 200×49.
- **[15]** `image` (logo) — pos (1065, 650), size 205×70.

**AWIP extras to reconcile:** `donutChart` (Order Intake by Product Family) — production doesn't have this on the dashboard (it's on the Extended dashboard). Keep only if a user wants it, otherwise move to Extended OI page.

---

### 3.8 Order Intake - Detail (production id `08a2a893f078e9c4ad92`) — 6 visuals — **PRIORITY M**

Mirror of Invoiced Detail on the OI side.

- **[00]** `actionButton` (Back) — pos (0, 0), size 85×57.
- **[01]** `tableEx` — pos (0, 98), size 1280×528. Same fields as [13] above (OI detail). ⚠ tableEx risk.
- **[02]** `slicer` — pos (119, 0), size 279×86. Field: `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]`.
- **[03]** `slicer` — pos (432, 0), size 280×86. Field: `SalesOrders[Product_Family_Product_Number]`.
- **[04]** `slicer` — pos (747, 0), size 281×86. Field: `SalesOrders[CustomerAccountAssignmentGroup_T]`.
- **[05]** `image` (logo) — pos (1065, 650), size 205×70.

**AWIP extras to remove:** `cardVisual` (Filtered Order Intake $), extra slicers on `SalesOrders[FiscalPeriod]`, `SalesOrders[Open_order_qty_flag]`, `SalesOrders[SalesDocumentType]`, `SalesOrders[FC_Product_Group]`. Same reasoning as Invoiced Detail — production keeps this page minimal.

---

### 3.9 Extended Order Intake - Dashboard (production id `cd86b33e4e73a0548d30`) — 14 visuals — **PRIORITY H**

Structural mirror of Extended Invoiced. Currently just a 7-visual skeleton on AWIP.

**Top ribbon**
- **[00]** `actionButton` — pos (0, 0), size 85×57.
- **[01]** `slicer` — pos (92, 0), size 160×86. Field: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` (production uses `FiscalYearPeriods Slicer OI` — see source-architecture doc: AWIP replacement is the shared FISCALPERIOD table).
- **[02]** `slicer` — pos (259, 0), size 160×86. Field: `SalesOrders[Product_Family_Product_Number]`.
- **[03]** `slicer` — pos (425, 0), size 160×86. Field: `SalesOrders[CustomerAccountAssignmentGroup_T]`.
- **[04]** `card` (Revenue) — pos (600, 0), size 220×100. Field: `SUM(SalesOrders[Revenue_Order_Intake])` (production wraps this as `[Sum Revenue in DC with sign VBAP OI]`; AWIP has no wrapper — use the raw SUM or add a wrapper measure).
- **[05]** `card` (Membrane sqft) — pos (829, 0), size 220×100. Field: `SalesOrders[Sum Order Qty. in FT2 for Membranes OI]`.
- **[06]** `card` (ISO bdft) — pos (1059, 0), size 221×100. Field: `SalesOrders[Sum Order Qty. in BFT2 for ISO OI]`.

**Chart row 1**
- **[07]** `clusteredColumnChart` — pos (10, 113), size 619×230. Category: `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]`. Series: `SalesOrders[Product_Group_Secondary]`. Y: `SUM(SalesOrders[Unit_Price_in_DC])` (verify column).
- **[08]** `columnChart` — pos (651, 113), size 619×230. Category: `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]`. Y: `SalesOrders[ISO AOP - $/bdft OI]`.

**Chart row 2**
- **[09]** `barChart` — pos (11, 354), size 409×289. Category: `SalesOrders[Material_Group]` (verify column — may be `MaterialGroup` or `Material_Group_T`). Y: `SUM(SalesOrders[Revenue_Order_Intake])`.
- **[10]** `donutChart` — pos (436, 354), size 409×289. Category: `SalesOrders[Sales_Representative_T]`. Y: `SUM(SalesOrders[Revenue_Order_Intake])`.
- **[11]** `barChart` — pos (861, 354), size 409×289. Category: `SalesOrders[SoldToParty_D12_T]`. Y: `SUM(SalesOrders[Revenue_Order_Intake])`.

**Bottom**
- **[12]** `actionButton` — pos (10, 656), size 200×49.
- **[13]** `image` — pos (1065, 650), size 205×70.

---

### 3.10 Backlog (production id `485ff3754ea8455a6933`) — 11 visuals — **PRIORITY M**

AWIP has this page (12 visuals) with a very similar shape.

**Top row: two big charts**
- **[00]** `barChart` (by Product Family) — pos (11, 12), size 615×340. Category: `SalesOrders[Product_Family_Product_Number]`. Y: `SUM(SalesOrders[Revenue_Backlog])` (filter `Open_order_qty_flag = "Y"`).
- **[01]** `barChart` (by Fiscal Period) — pos (654, 12), size 615×340. Category: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`. Y: `SUM(SalesOrders[Revenue_Backlog])`.

**Middle: tableEx**
- **[02]** `tableEx` — pos (0, 360), size 1280×257. Fields: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`, `SalesOrders[SoldToParty_D12_T]`, `SalesOrders[Product_Family_Product_Number]`, `SalesOrders[Product_Group_Secondary]`, `SalesOrders[Material_D17_T]`, `SUM(SalesOrders[Order_Quantity_in_FT2])`, `SUM(SalesOrders[Requested_Quantity_in_BFT])`, `SUM(SalesOrders[Unit_Price_in_DC])`, `SalesOrders[Price_UoM]`, `SUM(SalesOrders[Revenue_Backlog])`, + ~18 more. ⚠ tableEx risk.

**Bottom ribbon (KPI cards + slicers)**
- **[03]** `actionButton` — pos (0, 663), size 85×57.
- **[04]** `card` — pos (96, 633), size 140×87. Field: `SalesOrders[ISO Rate SB]` (production `[ISO Rate VBAP SB]`).
- **[05]** `card` — pos (250, 633), size 140×87. Field: `SalesOrders[Total Backlog $]`.
- **[06]** `card` — pos (405, 633), size 140×87. Field: `SalesOrders[Sum Order Qty. in FT2 for Membranes SB]`.
- **[07]** `slicer` — pos (564, 633), size 180×87. Field: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`.
- **[08]** `slicer` — pos (756, 633), size 180×87. Field: `SalesOrders[Product_Family_Product_Number]`.
- **[09]** `slicer` — pos (949, 633), size 180×87. Field: `SalesOrders[CustomerAccountAssignmentGroup_T]`.
- **[10]** `image` (logo) — pos (1128, 650), size 142×70.

**Note on AWIP's version:** AWIP put the slicers at the TOP (y≈54) not the BOTTOM. Recommend moving to match production (bottom band). AWIP also has an extra `donutChart` (Backlog $ by Sales Doc Type) and two extra multiRowCards — keep if useful, or remove to match production.

---

### 3.11 Backlog - Details (production id `b5c1e1e248961b072306`) — 6 visuals — **PRIORITY L**

Mirror of Invoiced Detail / OI Detail on the backlog side.

- **[00]** `actionButton` (Back) — pos (0, 0), size 85×57.
- **[01]** `tableEx` — pos (0, 98), size 1280×520. Fields: same as [02] above (Backlog tableEx). ⚠ tableEx risk.
- **[02]** `slicer` — pos (105, 0), size 250×87. Field: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`.
- **[03]** `slicer` — pos (381, 0), size 250×87. Field: `SalesOrders[Product_Family_Product_Number]`.
- **[04]** `slicer` — pos (657, 0), size 250×87. Field: `SalesOrders[CustomerAccountAssignmentGroup_T]`.
- **[05]** `image` (logo) — pos (1065, 650), size 205×70.

**AWIP has extras to remove:** `cardVisual` (Filtered Backlog $), slicer on `SalesOrders[Open_order_qty_flag]`, `SalesOrders[SalesDocumentType]`, plus two decorative textboxes.

---

### 3.12 Backlog by Rep (production id `633a47a92e92bd6b80a2`) — 11 visuals — **PRIORITY H**

Completely missing in AWIP. Distinctive: contains the only `shapeMap` visual in the report.

**Top row: map + rep chart**
- **[00]** `shapeMap` (Revenue by State) — pos (11, 10), size 614×339. Category: `KRW_NA_FF_GEOINFO[State]`. Value: `SUM(SalesOrders[Revenue_Backlog])`. **Requires:** `KRW_NA_FF_GEOINFO` dataflow imported into AWIP with a relationship to `SalesOrders` on state/customer/ship-to.
- **[01]** `clusteredColumnChart` (Revenue by Sales Rep) — pos (654, 10), size 615×339. Category: `SalesOrders[Sales_Representative_T]`. Y: `SUM(SalesOrders[Revenue_Backlog])`.

**Middle: tableEx**
- **[02]** `tableEx` — pos (0, 360), size 1280×257. Same fields as Backlog tableEx.

**Bottom ribbon (identical to Backlog page 3.10)**
- **[03]** `actionButton` — pos (0, 663), size 85×57.
- **[04]** `card` — pos (100, 633), size 140×87. Field: `SalesOrders[ISO Rate SB]`.
- **[05]** `card` — pos (254, 633), size 141×87. Field: `SalesOrders[Total Backlog $]`.
- **[06]** `card` — pos (409, 633), size 140×87. Field: `SalesOrders[Sum Order Qty. in FT2 for Membranes SB]`.
- **[07]** `slicer` — pos (564, 633), size 181×87. Field: `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`.
- **[08]** `slicer` — pos (756, 633), size 180×87. Field: `SalesOrders[Product_Family_Product_Number]`.
- **[09]** `slicer` — pos (948, 633), size 181×87. Field: `SalesOrders[CustomerAccountAssignmentGroup_T]`.
- **[10]** `image` (logo) — pos (1128, 650), size 142×70.

**Blocker:** `shapeMap` requires a TopoJSON custom shape file for US states. If AWIP doesn't have one, either (a) import the same shape file from `production-reference-odata\Amalgamated Sales Reports - JC.Report\StaticResources\SharedResources\` if present, or (b) substitute a standard `map` or `filledMap` visual against the same GEOINFO state field.

---

### 3.13 Summary Page (production id `6e5b174015250d002976`) — 27 visuals — **PRIORITY H**

Largest page in production. Cross-cube executive dashboard. Best grouped by section.

**Section A: Top-of-page KPI ribbon (Invoiced summary)** — y≈0–110
- **[00]** `actionButton` (Back) — pos (0, 0), size 85×57.
- **[01]** `image` (Kingspan logo alt) — pos (153, 0), size 160×106.
- **[02]** `multiRowCard` (Invoiced KPIs) — pos (335, 1), size 344×104. Values: `SUM(Billing[Revenue])`, `Billing[Revenue Previous Year]` (missing — use `_Measures[Sales PY]`), `Billing[Sum Billing Qty. in FT2 for Membranes]`, `Billing[Sum Billing Qty. in FT2 for Membranes Prior Year]` (missing).
- **[03]** `card` (arrow icon $) — pos (679, 1), size 50×53. Field: `Billing[Sales with Arrow]` (measure returning up/down glyph — missing in AWIP).
- **[04]** `card` (arrow icon qty) — pos (679, 54), size 50×51. Field: `Billing[PercDiff Arrow Sales QTY]` (missing).
- **[05]** `card` (%diff qty) — pos (729, 52), size 75×53. Field: `Billing[PercDiff PY Sales QTY]` (missing).
- **[06]** `card` (%diff $) — pos (729, 2), size 75×52. Field: `Billing[Perc diff PY]` (missing).
- **[07]** `multiRowCard` (OI KPIs) — pos (816, 1), size 333×104. Values: `SUM(SalesOrders[Revenue_Order_Intake])`, `SalesOrders[Revenue Previous Year OI]` (missing), `SalesOrders[Sum Order Qty. in FT2 for Membranes OI]`, `SalesOrders[Sum Order Qty. in FT2 for Membranes Prior Year OI]` (missing).
- **[08]** `card` (arrow qty OI) — pos (1143, 53), size 56×52. Field: `SalesOrders[PercDiff Arrow Orders QTY]` (missing).
- **[09]** `card` (arrow $ OI) — pos (1143, 0), size 56×54. Field: `SalesOrders[PercDiff Arrow Orders]` (missing).
- **[10]** `card` (%diff $ OI) — pos (1192, 2), size 82×52. Field: `SalesOrders[PercDiff PY Orders]` (missing).
- **[11]** `card` (%diff qty OI) — pos (1192, 53), size 82×52. Field: `SalesOrders[PercDiff PY Orders QTY]` (missing).

**Section B: middle band — slicer + chart column + right tables** — y≈110–436
- **[12]** `slicer` (Invoiced Rep) — pos (12, 150), size 160×93. Field: `Billing[Sales_Representative_T]`.
- **[13]** `pieChart` (Revenue by AAG) — pos (172, 112), size 285×325. Category: `Billing[CustomerAccountAssignmentGroup_T]`. Y: `SUM(Billing[Revenue])`.
- **[14]** `shapeMap` (Revenue by Ship-to State) — pos (470, 112), size 269×325. Category: `Billing[ShipToParty_State_T]` (verify column). Value: `SUM(Billing[Revenue])`. Same shape-file requirement as 3.12.
- **[15]** `tableEx` (Salesforce Quotes) — pos (751, 150), size 523×287. Fields: `Salesforce Quotes[Name]`, `Salesforce Quotes[Status]`, `SUM(Salesforce Quote Line Item[Quantity])`, `SUM(Salesforce Quotes[TotalPrice])`. **⚠ Blocker:** Salesforce Quotes / Quote Line Item tables are NOT in AWIP (missing per source-architecture doc). **Skip this visual** or ask user to import the Salesforce dataflow first.
- **[16]** `tableEx` (Top OI Projects) — pos (751, 151), size 523×287. Fields: `SalesOrders[Customer_Project_Name]` (verify — may be `Customer_Project_Name_T`), `SalesOrders[Sum Order Qty. in FT2 for Membranes OI]`, `SUM(SalesOrders[Revenue_Order_Intake])`.
- **[17]** `actionButton` (toggle to Quotes) — pos (752, 111), size 130×32.
- **[18]** `tableEx` (Top Backlog Projects) — pos (752, 152), size 521×287. Fields: `SalesOrders[Customer_Project_Name]`, `SalesOrders[Sum Order Qty. in FT2 for Membranes SB]`, `SUM(SalesOrders[Revenue_Backlog])`.
- **[19]** `tableEx` (Top Invoiced Projects) — pos (752, 151), size 521×285. Fields: `Billing[Customer_Project_Name]` (verify column), `Billing[Sum Billing Qty. in FT2 for Membranes]`, `SUM(Billing[Revenue])`.
- **[20]** `actionButton` (toggle to OI) — pos (881, 111), size 131×32.
- **[21]** `actionButton` (toggle to Backlog) — pos (1011, 111), size 132×32.
- **[22]** `actionButton` (toggle to Invoiced) — pos (1142, 111), size 131×32.

**Section C: bottom row — 3 wide charts** — y≈446–710
- **[23]** `slicer` (OI Rep) — pos (12, 293), size 160×93. Field: `SalesOrders[Sales_Representative_T]`.
- **[24]** `clusteredColumnChart` (Invoiced revenue over time) — pos (11, 446), size 445×264. Category: `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]`. Y: `SUM(Billing[Revenue])`.
- **[25]** `clusteredColumnChart` (OI revenue over time) — pos (470, 446), size 445×263. Category: `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]`. Y: `SUM(SalesOrders[Revenue_Order_Intake])`.
- **[26]** `treemap` (Invoiced revenue by Sales Rep) — pos (925, 446), size 349×264. Group: `Billing[Sales_Representative_T]`. Values: `SUM(Billing[Revenue])`.

**Structural blockers on this page:**
1. ~14 of the 27 visuals depend on measures that don't exist in AWIP (all `PercDiff …`, `Prior Year …`, `Sales with Arrow`, `Revenue Previous Year OI`). Blocked on Phase 10.
2. The Salesforce tableEx has no data source in AWIP. Either import Salesforce dataflow or skip.
3. `shapeMap` needs a state topojson (see 3.12 note).
4. The 4 `actionButton` toggles [17,20,21,22] drive a bookmark-based state selector (which of 3 tables to show). Manual bookmark work required — see section 7.

---

## 4. Page-level filters and slicers

### 4.1 Report-level filters (from production)

| # | Table | Field | Operator | Value | Applied to |
|---|---|---|---|---|---|
| 1 | `KRW-NA_FF_FORECAST` | `Fiscal Year Period Sorted` | StartsWith | `2026` | all pages |
| 2 | `FiscalYearPeriods Slicer SB` | `Fiscal Year Period` | Not Null | — | all pages |
| 3 | `KRW_NA_FF_FORECAST_INTAKE` | `Fiscal Year Period Sorted` | StartsWith | `2026` | all pages |

**AWIP mapping:**
- Filter 1: use `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]` (dataflow imported directly).
- Filter 2: use `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` (AWIP consolidates SB / OI slicer copies into the shared FISCALPERIOD dataflow — see source-architecture doc).
- Filter 3: use `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]` (dataflow imported directly).

⚠ **All three filters hardcode 2026** — will roll stale in 2027. Consider a `[Current Fiscal Year]` calculated column or a parameter-driven filter. Track this as a follow-up.

### 4.2 Page-level filters

None declared on production pages beyond report-level. Slicers do the rest.

### 4.3 Slicers per page (summary)

| Page | Slicers |
|---|---|
| Navigation Page | — (uses pageNavigator instead) |
| Nav – 3rd party/ICO | — |
| Invoiced Sales - Dashboard | Fiscal Period Sorted · Product Family · AAG |
| Invoiced Sales - Detail | Fiscal Period Sorted · Product Family · AAG |
| Extended Invoiced Sales | Fiscal Period Sorted · Product Family · AAG |
| Order Intake - Dashboard | Fiscal Period Sorted · Product Family · AAG |
| Order Intake - Detail | Fiscal Period Sorted · Product Family · AAG |
| Extended Order Intake | Fiscal Period · Product Family · AAG |
| Backlog | Fiscal Period · Product Family · AAG (bottom band) |
| Backlog - Details | Fiscal Period · Product Family · AAG |
| Backlog by Rep | Fiscal Period · Product Family · AAG |
| Summary Page | Invoiced Sales Rep · OI Sales Rep |

**Slicer sync recommendation:** enable "Sync slicers" for Fiscal Period / Product Family / AAG across the three Invoiced pages, then across the three OI pages, then across the three Backlog pages. The three cube groups have their own natural sync scopes. This is a manual step — see section 7.

---

## 5. Report-level configuration

**Keep AWIP's current setup, with these deltas:**

| Item | AWIP now | Production | Action |
|---|---|---|---|
| Base theme | `CY26SU07` | `CY24SU10` | Keep AWIP's (newer). |
| Custom theme | `AWIP6636503754310693.json` | (none custom in prod, just base) | Keep AWIP's custom theme — likely holds Kingspan brand colors. |
| Static resources | `kingspan-logo.png`, `kingspan-roofing-waterproofing8422940714883275.png` | same second image | Already aligned. |
| activeSectionIndex | 2 (`Invoiced Sales - Dashboard`) | 0 (`Navigation Page`) | Change to Navigation Page index once that page is built. |
| filterPaneHiddenInEditMode | true | (not set) | Fine either way. |
| Report-level filters | none | 3 (see 4.1) | **Add all 3.** |
| useNewFilterPaneExperience | true | (same) | OK. |

---

## 6. Execution order recommendation

Ordered by (a) VALUE — how much the org uses this page, (b) DEPENDENCY — measures/imports required, (c) COMPLEXITY.

**Wave 1 — quick wins on already-drafted pages (no new dataflows, no new measures)**

1. **Invoiced Sales - Detail** (§3.5, 6 visuals) — trim AWIP extras, one table + 3 slicers.
2. **Order Intake - Detail** (§3.8, 6 visuals) — mirror of above.
3. **Backlog - Details** (§3.11, 6 visuals) — mirror pattern.

**Wave 2 — main KPI dashboards (need existing AWIP measures + a subset of new ones)**

4. **Invoiced Sales - Dashboard** (§3.4, 16 visuals) — deletes and re-aligns; measures ~70% present.
5. **Order Intake - Dashboard** (§3.7, 16 visuals) — same status.
6. **Backlog** (§3.10, 11 visuals) — mostly present, just move slicer band to bottom + trim extras.

**Wave 3 — new pages that mostly reuse existing measures**

7. **Extended Invoiced Sales - Dashboard** (§3.6, 14 visuals) — rebuild from the "Error" placeholder.
8. **Extended Order Intake - Dashboard** (§3.9, 14 visuals) — sibling of #7.
9. **Backlog by Rep** (§3.12, 11 visuals) — requires `KRW_NA_FF_GEOINFO` import + shape-map file.

**Wave 4 — measure-heavy, defer until Phase 10 delivers the missing DAX**

10. **Summary Page** (§3.13, 27 visuals) — 14 missing measures + Salesforce blocker.
11. **Navigation Page** (§3.1, 24 visuals) — 10+ missing measures.
12. **Nav – 3rd party/ICO** (§3.2, 5 visuals) — 4 missing measures.

**Skip permanently:** Page 1 (§3.3) — scratch.

**Top 3 rebuild priorities (per user request):**

1. **Invoiced Sales - Dashboard** — the default landing today, biggest KPI page, ~70% present already; highest bang-for-buck alignment.
2. **Backlog by Rep** — completely missing; the only page that uses the state map + rep breakdown; leadership expects this view.
3. **Summary Page** — executive dashboard; largest single-page workload; unblocks C-level reporting once Phase 10 measures land.

---

## 7. Manual UI steps that CAN'T be automated

These require the human user in Power BI Desktop:

1. **Bookmarks** — production has bookmark-driven state toggles on Navigation Page (bookmarkNavigator top-right) and Summary Page (4 actionButtons swap between 3 project tables). Author these manually via View → Bookmarks pane.
2. **Sync slicers** — enable via View → Sync slicers pane. Cross-page sync groups suggested in §4.3.
3. **Page navigation** — `pageNavigator` visual is native but the ORDER of pages shown comes from the actual page order in the sections array; drag pages in the Pages pane to match the production `pageOrder`.
4. **Action buttons** — every `actionButton` in production has an "Action" tab (Type = Bookmark). Configure each one to invoke the matching bookmark.
5. **Drill-through** — production does NOT use drill-through pages (verified by scan). Nothing to configure here.
6. **Interactions** — Format menu → Edit interactions. Cross-visual interactions weren't inventoried in the source scan; verify one page at a time by comparing hover behavior against production.
7. **shapeMap topojson** — copy `US-states.json` (or equivalent) from production's StaticResources into AWIP's StaticResources folder OR substitute with a `filledMap` visual.
8. **Theme customization** — AWIP already has a custom theme; verify colors match Kingspan brand guide before publishing.
9. **actionButton bookmark bindings** — the "Clear all slicers" buttons need to point at a bookmark that captures the "all slicers cleared" state. Create the bookmark first, then bind.

---

## 8. Rebuild in Power BI Desktop — general recipe

For each page in §3 that you're rebuilding:

1. **Open the PBIP:** `AWIP_Commercial_Sales.PBIP\AWIP_Commercial_Sales.pbip` in Power BI Desktop.
2. **Select the target page** in the bottom page tabs.
3. **For pages present in AWIP that need alignment (Waves 1–2):**
   a. Compare each visual to the §3 spec for that page.
   b. Delete visuals not in the production spec.
   c. For each production visual not present in AWIP, insert it via the Visualizations pane.
   d. Drag fields into the correct wells — Values / Y-axis / Category / Rows — using the AWIP-side table names from §3.
   e. Set title from the § spec.
   f. Position via right-side Format pane → General → Properties → Size and position. Type in the x/y/w/h from the §3 spec.
4. **For pages completely missing (Waves 3–4):**
   a. Right-click the page tab area → New page.
   b. Name it exactly per §3 heading.
   c. Set visibility (View mode vs Hidden) to match production visibility.
   d. Build each visual per the numbered list in §3 for that page.
5. **After each visual is placed, save** (`Ctrl+S`) — the PBIP writes back to `report.json`.
6. **After completing a page, do a full report refresh** to catch any measure resolution failures.
7. **Test-drive the page** in Reading view.
8. **Commit** with a message like `Phase 11: rebuild <page name>`.

**Field-well cheat sheet by visual type:**

| Visual | Wells |
|---|---|
| `cardVisual` / `card` | Fields (single measure) |
| `multiRowCard` | Fields (N measures — stacked rows) |
| `gauge` | Value (Y-axis measure), Maximum value (max measure) |
| `slicer` | Field (single column) |
| `pivotTable` | Rows (dim), Columns (optional dim), Values (measures) |
| `tableEx` / `Table` | Values (columns + measures — order matters) |
| `columnChart` / `barChart` / `clusteredColumnChart` | X-axis / Y-axis / Legend (Series) |
| `lineChart` | Axis, Values |
| `donutChart` / `pieChart` | Legend (dim), Values (measure) |
| `treemap` | Group (dim), Values (measure) |
| `shapeMap` | Location (state), Color saturation (measure) |
| `actionButton` | (no data) — set Action tab |
| `image` | (no data) — set image URL |
| `textbox` | (no data) — inline text |
| `pageNavigator` | (no data) — configure appearance |
| `bookmarkNavigator` | (no data) — pick bookmark group |
| `shape` | (no data) — decoration only |

**Field-name resolution rule:** when a production visual uses `KRW_NA_SAP_VBRP[X]`, look up `X` in the source-architecture doc's column crosswalk (or in `analysis/billing-field-inventory.md`) to find the AWIP `Billing[Y]` equivalent. Same for VBAP OI/SB → SalesOrders.

**Measure-name resolution rule:** for each production `[Measure Name]` cited in §3, first check `analysis/odata-measure-validation-v2.md` — if it says "ADAPTED CORRECTLY" the same measure name exists in AWIP with a suffix (`IS`, `OI`, `SB`). If it says "MISSING", use the "substitute" hint noted inline in §3, or wait for Phase 10.

---

## Appendix A — production `pageOrder`

From `production-reference-odata/Amalgamated Sales Reports - JC.Report/definition/pages/pages.json`:

```
1. 4cebd6cd708bb1448d5f  Navigation Page                            (Visible)   24 visuals
2. 02c0c826020d7690a291  Navigation – 3rd party/ICO split           (Visible)    5 visuals
3. 136c291607e53cb23df0  Page 1                                     (Hidden)     2 visuals
4. adc801190c2b80e059c8  Invoiced Sales - Dashboard                 (Hidden)    16 visuals
5. 7547c7eb9f85b3605827  Invoiced Sales - Detail                    (Hidden)     6 visuals
6. d0b3413807313c882ead  Extended Invoiced Sales - Dashboard        (Hidden)    14 visuals
7. 3672e874de9d15c734e8  Order Intake - Dashboard                   (Hidden)    16 visuals
8. 08a2a893f078e9c4ad92  Order Intake - Detail                      (Hidden)     6 visuals
9. cd86b33e4e73a0548d30  Extended Order Intake - Dashboard          (Hidden)    14 visuals
10. 485ff3754ea8455a6933 Backlog                                    (Hidden)    11 visuals
11. b5c1e1e248961b072306 Backlog - Details                          (Hidden)     6 visuals
12. 633a47a92e92bd6b80a2 Backlog by Rep                             (Hidden)    11 visuals
13. 6e5b174015250d002976 Summary Page                               (Hidden)    27 visuals
```

Pages 1–2 are the only ones visible in view mode; all others open via the page navigator.

---

## Appendix B — AWIP section inventory (as it stands today)

From `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.Report/report.json`:

```
Backlog - Details                            (ordinal missing)  7 visuals
1. Extended Invoiced Sales - Dashboard Error                    7 visuals   ← placeholder / "Error" page
2. Invoiced Sales - Dashboard              (activeSectionIndex) 20 visuals  ← default landing
3. Extended Order Intake - Dashboard                            7 visuals   ← skeleton
4. Invoiced Sales - Detail                                      8 visuals
5. Order Intake - Detail                                        8 visuals
6. Backlog                                                     12 visuals   ← most complete AWIP dashboard
7. Order Intake - Dashboard                                    12 visuals
```

Total AWIP: 8 sections · 81 visuals.

---

## Appendix C — helper scripts (temporary)

Two ad-hoc Python scanners were written during this Phase 11 pass and can be deleted once the playbook is used:

- `analysis/_scan_awip.py` — enumerates AWIP sections + visualContainers from monolithic `report.json`.
- `analysis/_scan_prod.py` — enumerates production pages + visual.json files from folder-per-page tree.

Both are idempotent, read-only, and can be re-run to refresh the numbers if the source files change.

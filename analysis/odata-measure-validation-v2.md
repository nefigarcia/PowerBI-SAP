# Phase 5 v2 — Measure Validation (Full Comparison)

**Baseline:** 113 production measures x 38 AWIP measures (excluding 11 `_Diagnostics` throwaways), all cross-referenced.

Source-of-truth production file: `analysis/odata-production-measures-full.md`.
AWIP measure files scanned:
- `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/_Measures.tmdl` — 15 measures (Sales / OI / PY / YoY / Avg)
- `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/Billing.tmdl` — 9 kept (skipped 11 `_Diagnostics`)
- `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/SalesOrders.tmdl` — 14 measures

Table-name mapping applied throughout:
- `KRW_NA_SAP_VBRP` -> `Billing` (Datasphere `SlsVolNetAmt_CC`, `SalesVolumeQuantity`, `Revenue`, `Billing_Quantity_*`, `Product_Family`, `FC_Product_Group`, etc.)
- `KRW_NA_SAP_VBAP OI` -> `SalesOrders` (`IncSalesOrdNetAmnt_CC`, `Revenue_Order_Intake`, `Requested_Quantity_in_BFT`, `Order_Quantity_in_FT2`, `Product_Family_Product_Number`, `FC_Product_Group`, `CreationDate_D8`)
- `KRW_NA_SAP_VBAP SB` -> `SalesOrders` (backlog subset via `FC_Product_Group`, `Revenue_Backlog`)
- `KRW_NA_FF_CALENDAR` / `KRW_NA_FF_CALENDAR OI` -> `KRW_NA_FF_CALENDAR` (single dataflow calendar; inactive rel on `CreationDate_D8`)
- `KRW-NA_FF_FORECAST` -> `KRW-NA_FF_FORECAST` (hyphen preserved)
- `KRW_NA_FF_FORECAST_INTAKE` -> `KRW_NA_FF_FORECAST_INTAKE`

---

## 1. Executive summary

- Total production measures: **113**
- Total AWIP measures (excluding `_Diagnostics`): **38**
- EXACT matches: **0** (name/source diverged in every AWIP case due to Datasphere rename)
- ADAPTED CORRECTLY: **18**
- WRONG SOURCE / WRONG DAX (needs repair): **6**
- MISSING IN AWIP (need to add): **~78** — the vast majority of composite / PY / YTD / Current-Month production DAX has not been ported. Details in section 3.
- EXTRA IN AWIP (harmless / cleanup optional / rename): **13** (all `_Measures` table entries + a couple of Billing/SalesOrders extras)
- NEEDS REVIEW: **11** — cross-table filter measures + hardcoded literals

Bottom line: AWIP today implements the KPI aggregates (`Sales`, `Order Intake`, `Sales PY`, YoY %) as its OWN native measures on `_Measures`, plus a slim subset of production's ISO-rate / forecast measures on `Billing` and `SalesOrders`. **Every VBRP/VBAP-side PY, YTD, Current-Month, Fiscal-Month, PercDiff, Split, Difference, % Fcst measure from production is missing.** That gap explains why the ISO / Sales dashboards and the Summary page will not render the way they do in production once fully wired up.

---

## 2. AWIP measures -> production status

### 2.1 `_Measures` table (15)

| AWIP measure | Classification | Production equivalent (if any) | Notes / action |
|---|---|---|---|
| `Sales` = SUM('Billing'[SlsVolNetAmt_CC]) | EXTRA IN AWIP (semantic overlap with `Revenue` / `Sum Revenue in DC with sign VBRP`) | production has `Revenue`, `Sum Revenue in DC with sign VBRP` (both SUM of `[Revenue in DC with Sign]`) | Column `SlsVolNetAmt_CC` is Datasphere's "net sales amount, company currency" (i.e. `Revenue in DC with Sign` equivalent). KEEP. Consider aliasing `Revenue` -> `[Sales]`. |
| `Sales Quantity` = SUM('Billing'[SalesVolumeQuantity]) | EXTRA IN AWIP | none exact — production only has product-family-filtered qty | KEEP. Useful blanket total. |
| `Order Intake` = SUM('SalesOrders'[IncSalesOrdNetAmnt_CC]) | EXTRA IN AWIP (overlap with `Revenue OI` / `Sum Revenue in DC with sign VBAP OI`) | `Revenue OI` = SUM of `[Revenue in DC with Sign]` | KEEP. `IncSalesOrdNetAmnt_CC` is the correct Datasphere order-intake revenue column. |
| `Order Intake Quantity` = SUM('SalesOrders'[IncSalesOrderQty]) | EXTRA IN AWIP | none exact | KEEP. |
| `Sales PY` = CALCULATE([Sales], SAMEPERIODLASTYEAR('DimDate'[Date])) | ADAPTED (different technique from prod) | production `Revenue Previous Year` uses YEAR(TODAY())-1 filter + LOOKUPVALUE; AWIP uses SAMEPERIODLASTYEAR against `DimDate` | KEEP but be aware AWIP version is filter-context-aware (prefers time-intel), production is fixed to server clock. Materially different for any dashboard NOT filtered on current date. |
| `Sales Quantity PY` = CALCULATE([Sales Quantity], SAMEPERIODLASTYEAR('DimDate'[Date])) | EXTRA IN AWIP | none exact | KEEP. |
| `Order Intake PY` = CALCULATE([Order Intake], SAMEPERIODLASTYEAR('DimDate'[Date])) | ADAPTED | production `Revenue Previous Year OI` (see note above) | KEEP. |
| `Order Intake Quantity PY` = CALCULATE([Order Intake Quantity], SAMEPERIODLASTYEAR('DimDate'[Date])) | EXTRA IN AWIP | none | KEEP. |
| `Sales YoY %` = DIVIDE([Sales]-[Sales PY],[Sales PY]) | ADAPTED (equivalent semantics to `PercDiff PY Sales`) | prod `PercDiff PY Sales` = DIVIDE(SUM(VBRP[Revenue])-[Revenue Previous Year], [Revenue Previous Year], 0) | Semantically equivalent. KEEP. |
| `Sales Quantity YoY %` | EXTRA IN AWIP | prod `PercDiff PY Sales QTY` uses Membrane-filtered qty; this AWIP measure is un-filtered | KEEP; add Membrane-filtered variant if a report page needs the prod behavior. |
| `Order Intake YoY %` | ADAPTED (equivalent to `PercDiff PY Orders`) | prod `PercDiff PY Orders` | KEEP. |
| `Order Intake Quantity YoY %` | EXTRA IN AWIP | prod `PercDiff PY Orders QTY` is Membrane-filtered | KEEP. |
| `Order Intake vs Sales` = [Order Intake]-[Sales] | EXTRA IN AWIP | none | KEEP. Nice-to-have. |
| `Avg Sales Price` = DIVIDE([Sales],[Sales Quantity]) | EXTRA IN AWIP | none | KEEP. Different from `ISO AOP - $/bdft VBRP` which divides revenue by BFT2. |
| `Avg Order Price` = DIVIDE([Order Intake],[Order Intake Quantity]) | EXTRA IN AWIP | none | KEEP. |

### 2.2 `Billing` table — 9 kept (11 `_Diagnostics` skipped)

| AWIP measure | Classification | Production equivalent | Notes / action |
|---|---|---|---|
| `Sum Billing Qty. in FT2 for Membranes` (Billing lines 113-131) | ADAPTED CORRECTLY | `Sum Billing Qty. in FT2 for Membranes` (VBRP) | DAX shape identical, sources retargeted: `Billing[Product_Family]` + `Billing[Billing_Quantity_in_FT2]`. GOOD. |
| `Sum Billing Qty. in BFT2 for ISO 2` (Billing lines 135-153) | WRONG SOURCE (variant) | Nearest prod: `Sum Billing Qty. in BFT2 for ISO` filters `[Product Family]` "iso" and sums `[Billing Qty. in BFT2]` | AWIP filters `Billing[FC_Product_Group] CONTAINSSTRING "iso"` and sums `Billing[Billing_Quantity_with_Signs]`. Two divergences: (a) product filter uses FC group, not Product_Family; (b) column is `_with_Signs` not the BFT2 column. Keep as diagnostic only; remove once `Sum Billing Qty. in BFT2 for ISO` (below) is proven right. |
| `Sum Billing Qty. in BFT2 for ISO` (Billing lines 157-174) | ADAPTED (but uses `Billing_Quantity_in_BFT`, not `..._in_BFT2`) | production `Sum Billing Qty. in BFT2 for ISO` -> `[Billing Qty. in BFT2]` | NEEDS REVIEW — Datasphere gives both `Billing_Quantity_in_BFT` and (per column inventory) may or may not have `_in_BFT2`. If BFT vs BFT2 is a unit difference this is a QUANTITATIVE bug. Cross-check the Datasphere column glossary before shipping. |
| `Sum Fcst Sales in FT2 for Membranes` | ADAPTED (variant naming) | closest match: production's forecast side `Current Month Invoiced Sales Membrane sqft` filters by `[Current FYP VBRP]`; AWIP measure does an UN-filtered SUM | This is a different aggregate (blanket total, not fiscal-month). Not a direct port. Rename to something like `Sum Fcst Sales Membrane sqft` or delete if unused. |
| `Sum Revenue in DC with sign IS` | ADAPTED CORRECTLY | `Sum Revenue in DC with sign VBRP` | Wraps SUM(Billing[Revenue]) with IF(...BLANK())=0. GOOD (Datasphere `Revenue` = production `Revenue in DC with Sign`). Suffix `IS` (invoice side) is AWIP's own convention. |
| `ISO AOP - $/bdft IS` = SUM(Billing[Revenue])/SUM(Billing[Billing_Quantity_with_Signs]) | WRONG SOURCE | `ISO AOP - $/bdft VBRP` = SUM([Revenue in DC with Sign]) / SUM([Billing Qty. in BFT2]) | AWIP denominator is `Billing_Quantity_with_Signs` (all products, all UoM). Production denominator is `Billing Qty. in BFT2` (board-feet, ISO products). Denominator swap will give a materially different $/bdft number. **FIX:** change denominator to the BFT2 column and add ISO product-family filter. |
| `ISO Rate IS` | ADAPTED CORRECTLY | `ISO Rate` (VBRP) | Same helper-measure ratio: [Sum Billing Qty. in BFT2 for ISO] / [Sum Billing Qty. in FT2 for Membranes], IF-BLANK guard. GOOD. But note it inherits the BFT-vs-BFT2 uncertainty from `Sum Billing Qty. in BFT2 for ISO`. |
| `ISO Rate Fcst IS` | ADAPTED CORRECTLY | `ISO Rate Fcst` (KRW-NA_FF_FORECAST) | Identical DAX: DIVIDE(SUM([Sales ISO bdft]), SUM([Sales Membrane sqft])). GOOD. |
| `Selected Fiscal Period` = VALUE(MAX('Fiscal Period Selector'[FiscalYearPeriod])) | EXTRA IN AWIP | no production analog | KEEP — used by AWIP's own fiscal-period slicer. Not present in production. |

### 2.3 `SalesOrders` table (14)

| AWIP measure | Classification | Production equivalent | Notes / action |
|---|---|---|---|
| `ISO AOP - $/bdft OI` = SUM(SalesOrders[Revenue_Order_Intake])/SUM(SalesOrders[Order_Quantity_in_BFT2]) | ADAPTED CORRECTLY | `ISO AOP - $/bdft VBAP OI` = SUM([Revenue in DC with Sign])/SUM([Order Qty. in BFT2]) | Column names retargeted, semantics preserved. GOOD. |
| `Sum Fcst Order Qty. in FT2 for Membranes OI` | EXTRA / variant | nearest prod `Current Month Order Revenue Fcst` filters by `[Current FYP VBAP OI]`; this is un-filtered SUM | Blanket total; not a direct port. Keep or delete. |
| `Sum Order Qty. in BFT2 for ISO OI` | ADAPTED CORRECTLY | `Sum Order Qty. in BFT2 for ISO OI` (VBAP OI) | Uses `Product_Family_Product_Number` + `Requested_Quantity_in_BFT`. GOOD but BFT vs BFT2 same caveat as invoice side. |
| `Sum Order Qty. in BFT2 for ISO SB` | ADAPTED CORRECTLY | `Sum Order Qty. in BFT2 for ISO SB` (VBAP SB) | Uses `FC_Product_Group CONTAINSSTRING "ISO"` + `Requested_Quantity_in_BFT`. Prod version filters `[Product Family]` "iso". Different filter column but same intent (SB = backlog subset via FC group). NEEDS REVIEW to confirm row counts match. |
| `Sum Order Qty. in FT2 for Membranes OI` | ADAPTED CORRECTLY | `Sum Order Qty. in FT2 for Membranes OI` (VBAP OI) | GOOD. |
| `Sum Order Qty. in FT2 for Membranes SB` | ADAPTED (subset via FC_Product_Group) | `Sum Order Qty. in FT2 for Membranes SB` (VBAP SB) | AWIP filters `FC_Product_Group = "TPO"` (a Membrane variant); prod filters `[Product Family]` "Membrane". SUMs `RequestedQuantityInBaseUnit`. NEEDS REVIEW — TPO is only ONE of the membrane sub-families in prod. |
| `Sum Order Qty. in FT2 for Membranes SB 2` | DUPLICATE (diagnostic variant) | none | Uses CALCULATE + `[Open_Order_Quantity_in_FT2]` measure that isn't defined. LIKELY BROKEN. Delete or fix. |
| `ISO Rate OI` | ADAPTED CORRECTLY | `ISO Rate VBAP OI` | GOOD. |
| `ISO Rate SB` | ADAPTED CORRECTLY | `ISO Rate VBAP SB` | GOOD. |
| `ISO Rate Fcst OI` | ADAPTED CORRECTLY | `ISO Rate Fcst VBAP` (FORECAST_INTAKE) | DIVIDE(SUM([Sales ISO bdft]), SUM([Sales Membrane sqft])). GOOD. |
| `Total Backlog $` = SUM(SalesOrders[Revenue_Backlog]) with IF-blank | ADAPTED CORRECTLY | `Total Backlog $` (VBAP SB) = SUM('KRW_NA_SAP_VBAP SB'[Revenue in DC with Sign]) | AWIP uses `[Revenue_Backlog]` (Datasphere backlog-only revenue column). Prod uses the SB table (only-backlog rows). Semantic equivalence assuming `Revenue_Backlog` is populated only for open items. GOOD. |
| `PY Revenue Order Intake` | ADAPTED CORRECTLY (Kingspan-preferred pattern) | `Revenue Previous Year OI` | AWIP uses YEAR/MONTH filter on `KRW_NA_FF_CALENDAR[Date]` via inactive USERELATIONSHIP on `CreationDate_D8`. Matches the AWIP PY pattern documented in project memory. Kingspan-owned enhancement over prod. GOOD. |
| `Sum PY Order Qty. in FT2 for Membranes OI` | ADAPTED CORRECTLY | `Sum Order Qty. in FT2 for Membranes Prior Year OI` | Same YEAR/MONTH + USERELATIONSHIP pattern as above. GOOD. |
| `Sum PY Order Qty. in BFT2 for ISO OI` | ADAPTED CORRECTLY | `Sum Order Qty. in BFT2 for ISO Prior Year OI` | Same pattern. GOOD. |

---

## 3. Production measures -> AWIP coverage

Priority key: **High** = referenced by a visible dashboard element in production; **Medium** = referenced by a summary page or drill-through; **Low** = internal helper / duplicate / obvious throwaway. If unsure, defaulted to Medium.

### 3.1 `KRW_NA_SAP_VBRP` (45) -> `Billing`

| Production measure | Present in AWIP? | AWIP equivalent | Priority | Action |
|---|---|---|---|---|
| Average Revenue per Product Family | No | none | Low | Broken cross-ref to `KRW_NA_SAP_AUSP`. SKIP unless AUSP is re-hooked. |
| Average Margin per Product Family | No | none | Low | Same broken cross-ref. SKIP. |
| Average Margin per Fiscal Year Period | No | none | Low | Requires `[Margin in DC]` — not in Datasphere Billing. NEEDS REVIEW. |
| Sum Billing Qty. in FT2 for Membranes | Yes | `Sum Billing Qty. in FT2 for Membranes` (Billing) | High | Done. |
| Sum Billing Qty. in BFT2 for ISO | Partial | `Sum Billing Qty. in BFT2 for ISO` (Billing) | High | Verify BFT vs BFT2 column. |
| Margin Perc | No | none | Low | Needs `[Margin in DC]`. NEEDS REVIEW. |
| Current Month Billing Qty. in FT2 for Membranes | No | none | High | ADD. See section 4. |
| YTD Billing Qty. in FT2 for Membranes | No | none | High | ADD. |
| Current Month Billing Qty. in BFT2 for ISO | No | none | High | ADD. |
| YTD Billing Qty. in BFT2 for ISO | No | none | High | ADD. |
| Current Month Billing Qty. in FT2 for ISO | No | none | Medium | ADD. |
| YTD Billing Qty. in FT2 for ISO | No | none | Medium | ADD. |
| Current Month Invoiced Revenue Billing Date | No | none | High | ADD (uses BillingDateType) — Datasphere field `BillingDate` present per Billing.tmdl column inventory. |
| YTD Invoiced Revenue Billing Date | No | none | High | ADD. |
| $ Difference Current Month VBRP | No | none | Medium | Depends on the two above + `Current Month Invoice Revenue Fcst`. |
| $ Difference YTD VBRP | No | none | Medium | Depends on YTD equivalents. |
| ISO Rate | Yes | `ISO Rate IS` (Billing) | High | Done. |
| % Fcst VBRP CM | No | none | Medium | ADD — depends on `Current Month Invoiced Revenue Billing Date` + `Current Month Invoice Revenue Fcst`. |
| Revenue | Partial | `[Sales]` in `_Measures` + `Sum Revenue in DC with sign IS` (Billing) | Low | Semantically covered. Consider adding named `Revenue` alias if any legacy report references it. |
| Billing Year | No | none | Low | Trivial helper `YEAR(SELECTEDVALUE(Billing[BillingDate]))`. ADD if PY measures need it. |
| Revenue Previous Year | Partial | `[Sales PY]` (SAMEPERIODLASTYEAR) approximates it | Medium | AWIP uses filter-context PY; prod uses TODAY()-1 with side-check on `[Billing Year]`. Different behavior on drill-through. ADD the prod version if that specific behavior is needed. |
| Sum Billing Qty. in FT2 for Membranes Prior Year | No | none | High | ADD (use PY pattern from `Sum PY Order Qty. in FT2 for Membranes OI` on SalesOrders). |
| Sum Billing Qty. in BFT2 for ISO Prior Year | No | none | High | ADD (same PY pattern). |
| Sum Revenue in DC with sign VBRP | Yes | `Sum Revenue in DC with sign IS` (Billing) | Low | Done. |
| Current Fiscal Month Billing Qty. in FT2 for Membranes | No | none | High | ADD. Requires `[Current FYP VBRP]` helper first. |
| Current Fiscal Month Billing Qty. in FT2 for ISO | No | none | Medium | ADD. |
| Current Fiscal Month Billing Qty. in BFT2 for ISO | No | none | High | ADD. |
| Current Fiscal Month Invoiced Revenue | No | none | High | ADD. |
| % Fcst VBRP FM | No | none | Medium | ADD. |
| Revenue For Fiscal Month Previous Year | No | none | Medium | ADD. |
| Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year | No | none | Medium | ADD. |
| Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year | No | none | Medium | ADD. |
| Current FYP VBRP **(HELPER)** | No | none — but `Selected Fiscal Period` reads a slicer | **High** | ADD FIRST. Blocks 6+ other measures. See section 4. |
| ISO AOP - $/bdft VBRP | Partial (with bug) | `ISO AOP - $/bdft IS` (Billing) | Low | AWIP uses wrong denominator column (see 2.2). Fix denominator + add ISO filter. |
| Current Fiscal Month Invoiced Revenue FT2 Membranes | No | none | High | ADD. |
| Current Fiscal Month Billing Qty. in FT2 for Membranes Split | No | none | Medium | ADD (no product filter, for legend/slicer). |
| Sum of Revenue in DC with Sign % difference from Revenue Previous Year | Partial | `[Sales YoY %]` in `_Measures` is semantically equivalent | Low | No action. |
| PercDiff PY Sales | Partial | `[Sales YoY %]` | Low | Covered. |
| PercDiff Arrow Sales | No | none | Low | Trivial arrow variant. ADD only if UI cards need it. |
| PercDiff PY Sales QTY | No | none | Medium | AWIP `[Sales Quantity YoY %]` is un-filtered; prod is Membrane-only. ADD Membrane-filtered variant. |
| PercDiff Arrow Sales QTY | No | none | Low | Arrow variant. |
| Prior Year FYP VBRP | No | none | High | ADD (helper for FM-PY split). |
| Current Date FYP VBRP | No | none | Low | Trivial helper. |
| Prior Year Date FYP VBRP | No | none | Low | Trivial helper. |
| Prior Year Fiscal Month Billing Qty. in FT2 for Membranes Split | No | none | Medium | ADD after helpers exist. |

### 3.2 `KRW_NA_SAP_VBAP OI` (43) -> `SalesOrders`

| Production measure | Present in AWIP? | AWIP equivalent | Priority | Action |
|---|---|---|---|---|
| Margin Perc VBAP | No | none | Low | Needs `[Margin in DC]`. NEEDS REVIEW. |
| Sum Order Qty. in FT2 for Membranes OI | Yes | `Sum Order Qty. in FT2 for Membranes OI` (SalesOrders) | High | Done. |
| Sum Order Qty. in BFT2 for ISO OI | Yes | `Sum Order Qty. in BFT2 for ISO OI` (SalesOrders) | High | Done (verify BFT vs BFT2). |
| Current Month Order Revenue | No | none | High | ADD. |
| Current Month Order Revenue Doc Date | No | none | High | ADD. |
| Current Calendar Month Order FT2 for Membranes | No | none | High | ADD. |
| YTD Order FT2 for Membranes | No | none | High | ADD. |
| YTD Order FT2 for ISO | No | none | Medium | ADD. |
| YTD Order BFT for ISO | No | none | High | ADD. |
| Current Calendar Month Order FT2 for ISO | No | none | Medium | ADD. |
| Current Calendar Month Order BFT for ISO | No | none | High | ADD. |
| YTD Order Revenue Doc Date | No | none | High | ADD. |
| $ Difference Current Month | No | none | Medium | ADD. |
| $ Difference YTD | No | none | Medium | ADD. |
| % Fcst CM | No | none | Medium | ADD. |
| Current Month Membrane Order Revenue Doc Date | No | none | High | ADD. |
| Current Month ISO Order Revenue Doc Date | No | none | High | ADD. |
| Order Year OI | No | none | Low | Trivial helper. |
| Revenue OI | Partial | `[Order Intake]` in `_Measures` + `[PY Revenue Order Intake]` on SalesOrders | Low | Covered by `[Order Intake]` if you use it consistently. |
| Revenue Previous Year OI | Yes | `PY Revenue Order Intake` (SalesOrders) | High | Done — Kingspan-preferred pattern. |
| Sum Order Qty. in FT2 for Membranes Prior Year OI | Yes | `Sum PY Order Qty. in FT2 for Membranes OI` (SalesOrders) | High | Done. |
| Sum Order Qty. in BFT2 for ISO Prior Year OI | Yes | `Sum PY Order Qty. in BFT2 for ISO OI` (SalesOrders) | High | Done. |
| Sum Revenue in DC with sign VBAP OI **(BUG: sums VBRP)** | No | none | Low | **DO NOT REPLICATE BUG.** Correct version = SUM(SalesOrders[Revenue_Order_Intake]) already available as `[Order Intake]`. See section 7. |
| Current Fiscal Month Order FT2 for Membranes Hardcoded **(HARDCODED "2026.2")** | No | none | Low | **DO NOT REPLICATE HARDCODE.** Replace with proper `Current FYP` helper. See section 4 + section 7. |
| Revenue Fiscal Month Previous Year OI | No | none | Medium | ADD (use PY pattern). |
| Sum Order Qty. in FT2 for Membranes Fiscal Month Prior Year OI | No | none | Medium | ADD. |
| Sum Order Qty. in BFT2 for ISO Fiscal Month Prior Year OI | No | none | Medium | ADD. |
| Current Calendar Month Order FT2 for Membranes 2 **(DUPLICATE)** | No | none | Low | SKIP — duplicate of the non-`2` version. |
| Current FYP VBAP OI **(HELPER)** | No | none | **High** | ADD FIRST. Blocks 7+ others. |
| ISO AOP - $/bdft VBAP OI | Yes | `ISO AOP - $/bdft OI` (SalesOrders) | Low | Done. |
| Current Fiscal Month Order FT2 for ISO | No | none | Medium | ADD. |
| Current Fiscal Month Order BFT for ISO | No | none | High | ADD. |
| Current Fiscal Month Order Revenue | No | none | High | ADD. |
| % Fcst FM | No | none | Medium | ADD. |
| Current Fiscal Month Order FT2 for Membranes | No | none | High | ADD. |
| Current Fiscal Month Order Revenue FT2 Membranes | No | none | High | ADD. |
| PercDiff PY Orders | Partial | `[Order Intake YoY %]` | Low | Covered. |
| PercDiff PY Orders QTY | No | none | Medium | Filter-preserving variant. ADD if needed. |
| PercDiff Arrow Orders | No | none | Low | Arrow variant. |
| PercDiff Arrow Orders QTY | No | none | Low | Arrow variant. |
| Current Fiscal Month Order BFT for ISO Split | No | none | Medium | ADD (no product filter). |
| Current Fiscal Month Order FT2 for ISO Split | No | none | Medium | ADD. |
| ISO Rate VBAP OI | Yes | `ISO Rate OI` (SalesOrders) | High | Done. |

### 3.3 `KRW_NA_SAP_VBAP SB` (5) -> `SalesOrders`

| Production measure | Present in AWIP? | AWIP equivalent | Priority | Action |
|---|---|---|---|---|
| Margin Perc VBAP SB | No | none | Low | Needs `[Margin in DC]`. NEEDS REVIEW. |
| Sum Order Qty. in BFT2 for ISO SB | Yes | `Sum Order Qty. in BFT2 for ISO SB` (SalesOrders) | High | Done. Verify FC_Product_Group filter equivalence. |
| Sum Order Qty. in FT2 for Membranes SB | Partial | `Sum Order Qty. in FT2 for Membranes SB` (SalesOrders) | High | AWIP filters `FC_Product_Group = "TPO"` — narrower than prod's `[Product Family] contains "Membrane"`. NEEDS REVIEW. |
| ISO Rate VBAP SB | Yes | `ISO Rate SB` (SalesOrders) | Medium | Done. |
| Total Backlog $ | Yes | `Total Backlog $` (SalesOrders) | High | Done via `[Revenue_Backlog]` column. |

### 3.4 `KRW-NA_FF_FORECAST` (10)

| Production measure | Present in AWIP? | AWIP equivalent | Priority | Action |
|---|---|---|---|---|
| ISO Rate Fcst | Yes | `ISO Rate Fcst IS` (Billing) | High | Done. |
| Current Month Invoice Revenue Fcst | No | none | High | ADD (needs `[Current FYP VBRP]` helper). |
| Current Month Invoiced Sales Membrane sqft | No | none | High | ADD. |
| YTD Invoiced Sales Membrane sqft | No | none | High | ADD. |
| Current Month Invoiced Sales ISO bdft | No | none | High | ADD. |
| YTD Invoiced Sales ISO bdft | No | none | High | ADD. |
| Current Month Invoiced Sales ISO sqft | No | none | Medium | ADD. |
| YTD Invoiced Sales ISO sqft | No | none | Medium | ADD. |
| YTD Invoice Revenue Fcst | No | none | High | ADD. |
| Current Month Invoiced Sales ISO sqft FM **(HARDCODED "2026.02")** | No | none | Low | **DO NOT REPLICATE HARDCODE.** Rewrite against `[Current FYP VBRP]`. |

### 3.5 `KRW_NA_FF_FORECAST_INTAKE` (10)

| Production measure | Present in AWIP? | AWIP equivalent | Priority | Action |
|---|---|---|---|---|
| ISO Rate Fcst VBAP | Yes | `ISO Rate Fcst OI` (SalesOrders) | High | Done. |
| Current Month Order Revenue Fcst | No | none | High | ADD (needs `[Current FYP VBAP OI]`). |
| Current Fiscal Month Sales Membrane sqft **(CROSS-TABLE)** | No | none | High | ADD. Cross-table filter must reroute to `SalesOrders[Product_Family_Product_Number]`. See section 6. |
| Current Fiscal Month Sales ISO sqft **(CROSS-TABLE)** | No | none | Medium | ADD (same reroute). |
| Current Month Sales ISO bdft | No | none | Medium | ADD. |
| YTD Sales ISO bdft | No | none | Medium | ADD. |
| YTD Sales ISO sqft | No | none | Medium | ADD. |
| YTD Sales Membrane sqft | No | none | Medium | ADD. |
| YTD Order Revenue Fcst | No | none | High | ADD. |
| Current Fiscal Month Sales ISO bdft **(CROSS-TABLE)** | No | none | High | ADD (reroute). |

---

## 4. Prioritized Phase 9 repair actions

### Immediate (fixes user-visible dashboard values)

- [ ] **Build the two helper measures first — every High-priority Current-Fiscal-Month measure depends on them.**
  ```dax
  // On Billing (or _Measures)
  Current FYP VBRP =
      LOOKUPVALUE(
          KRW_NA_FF_CALENDAR[Fiscal Year Period],
          KRW_NA_FF_CALENDAR[Date], TODAY()
      )
  ```
  ```dax
  // On SalesOrders (or _Measures)
  Current FYP VBAP OI =
      LOOKUPVALUE(
          KRW_NA_FF_CALENDAR[Fiscal Year Period],
          KRW_NA_FF_CALENDAR[Date], TODAY()
      )
  ```
- [ ] **Fix `ISO AOP - $/bdft IS`** — denominator swap and add ISO filter.
  Current AWIP:
  ```dax
  SUM(Billing[Revenue])/SUM(Billing[Billing_Quantity_with_Signs])
  ```
  Target (production `ISO AOP - $/bdft VBRP`):
  ```dax
  SUM(Billing[Revenue])/SUM(Billing[Billing_Quantity_in_BFT2])
  ```
- [ ] **Confirm the `Billing_Quantity_in_BFT` vs `_in_BFT2` column** used by `Sum Billing Qty. in BFT2 for ISO` and `Sum Order Qty. in BFT2 for ISO OI`. If Datasphere exposes both, the AWIP measures likely need `_in_BFT2` to match production output.
- [ ] **Delete `Sum Order Qty. in FT2 for Membranes SB 2`** — references undefined `[Open_Order_Quantity_in_FT2]` measure; will produce a runtime error.

### High priority (needed for Invoiced / Order Intake / Backlog dashboards to match production)

- [ ] Add `Current Month Billing Qty. in FT2 for Membranes` (VBRP -> Billing).
  ```dax
  SUMX(
      FILTER(
          Billing,
          CONTAINSSTRING(Billing[Product_Family], "Membrane") &&
          YEAR(Billing[BillingDate]) = YEAR(TODAY()) &&
          MONTH(Billing[BillingDate]) = MONTH(TODAY())
      ),
      Billing[Billing_Quantity_in_FT2]
  )
  ```
- [ ] Add `YTD Billing Qty. in FT2 for Membranes`, `Current Month Billing Qty. in BFT2 for ISO`, `YTD Billing Qty. in BFT2 for ISO` (same shape, drop MONTH filter for YTD, swap column/filter as needed).
- [ ] Add `Current Month Invoiced Revenue Billing Date`, `YTD Invoiced Revenue Billing Date` (SUM of `Billing[Revenue]` under YEAR/MONTH filter on `Billing[BillingDate]`).
- [ ] Add `Current Fiscal Month Invoiced Revenue`, `Current Fiscal Month Invoiced Revenue FT2 Membranes`, `Current Fiscal Month Billing Qty. in FT2 for Membranes`, `Current Fiscal Month Billing Qty. in BFT2 for ISO` — all depend on `[Current FYP VBRP]`.
- [ ] Add `Sum Billing Qty. in FT2 for Membranes Prior Year`, `Sum Billing Qty. in BFT2 for ISO Prior Year` (use Kingspan-preferred YEAR/MONTH + USERELATIONSHIP pattern via `Billing[BillingDate]` and `KRW_NA_FF_CALENDAR[Date]`).
- [ ] Add `Current Month Order Revenue`, `Current Month Order Revenue Doc Date`, `Current Calendar Month Order FT2 for Membranes`, `YTD Order FT2 for Membranes`, `YTD Order BFT for ISO`, `Current Calendar Month Order BFT for ISO`, `YTD Order Revenue Doc Date`, `Current Month Membrane/ISO Order Revenue Doc Date` on SalesOrders.
- [ ] Add `Current Fiscal Month Order Revenue`, `Current Fiscal Month Order Revenue FT2 Membranes`, `Current Fiscal Month Order FT2 for Membranes`, `Current Fiscal Month Order BFT for ISO` — all depend on `[Current FYP VBAP OI]`.
- [ ] Add `Current Month Invoice Revenue Fcst`, `YTD Invoice Revenue Fcst`, `Current Month Invoiced Sales Membrane sqft`, `Current Month Invoiced Sales ISO bdft`, `YTD Invoiced Sales Membrane sqft`, `YTD Invoiced Sales ISO bdft` on `KRW-NA_FF_FORECAST`.
- [ ] Add `Current Month Order Revenue Fcst`, `YTD Order Revenue Fcst`, and the three cross-table `Current Fiscal Month Sales *` measures on `KRW_NA_FF_FORECAST_INTAKE` (re-pointing cross-table filter to `SalesOrders[Product_Family_Product_Number]`).

### Medium priority (needed for Extended dashboards and Summary page)

- [ ] Add all `Fiscal Month Prior Year` variants (Membranes / ISO / Revenue) on both Billing and SalesOrders using the PY pattern.
- [ ] Add `$ Difference Current Month`, `$ Difference YTD`, `$ Difference Current Month VBRP`, `$ Difference YTD VBRP`, `% Fcst CM`, `% Fcst FM`, `% Fcst VBRP CM`, `% Fcst VBRP FM` composites.
- [ ] Add `Split` variants (`Current Fiscal Month Billing Qty. in FT2 for Membranes Split`, `Prior Year Fiscal Month Billing Qty. in FT2 for Membranes Split`, `Current Fiscal Month Order BFT for ISO Split`, `Current Fiscal Month Order FT2 for ISO Split`) — no product filter, used with legends/slicers.
- [ ] Add `PercDiff PY Sales QTY`, `PercDiff PY Orders QTY` (Membrane-filtered qty YoY %).

### Low priority (cleanup / duplicate removal / hardcoded-value fixes)

- [ ] Delete AWIP's 11 `_Diagnostics` measures on Billing (throwaway per Phase 5 direction).
- [ ] Delete AWIP `Sum Billing Qty. in BFT2 for ISO 2` (variant using `FC_Product_Group`) once ISO row-count matches the Product_Family version.
- [ ] Rename / delete AWIP `Sum Fcst Sales in FT2 for Membranes` (blanket total, not the prod fiscal-month measure).
- [ ] Do NOT replicate production BUG `Sum Revenue in DC with sign VBAP OI` (sums VBRP) — `[Order Intake]` already covers the correct behavior.
- [ ] Do NOT replicate production HARDCODES `"2026.2"` / `"2026.02"`. Rewrite against `[Current FYP VBRP]` / `[Current FYP VBAP OI]`.
- [ ] Add `Billing Year`, `Order Year OI`, `Prior Year FYP VBRP`, `Current Date FYP VBRP`, `Prior Year Date FYP VBRP` trivial helpers only if a composite needs them.
- [ ] Arrow measures (`PercDiff Arrow *`) only if a report card requires the up/down glyph.

---

## 5. AWIP measures to delete (if any)

| AWIP measure | Reason |
|---|---|
| All 11 `_Diagnostics` measures on Billing (lines 7-111) | Throwaway ISO Rate investigation. |
| `Sum Order Qty. in FT2 for Membranes SB 2` (SalesOrders lines 111-125) | Uses undefined `[Open_Order_Quantity_in_FT2]` measure — will error at query time. |
| `Sum Billing Qty. in BFT2 for ISO 2` (Billing lines 135-153) | Variant that filters `FC_Product_Group` instead of `Product_Family`; use the canonical `Sum Billing Qty. in BFT2 for ISO` once verified. |
| Optionally: `Sum Fcst Sales in FT2 for Membranes` (Billing lines 178-190) | Blanket SUM without fiscal filter — not the production port; misleading name. |

---

## 6. Cross-table dependencies flagged

Production measures whose DAX crosses table boundaries. Since AWIP has excluded all `KRW_NA_SAP_*` tables, every one of these needs a remap:

| Production measure | Home table | Foreign col referenced | AWIP remap target |
|---|---|---|---|
| `Sum Revenue in DC with sign VBAP OI` | VBAP OI | `KRW_NA_SAP_VBRP[Revenue in DC with Sign]` | **Do not replicate — this is the copy-paste BUG.** Use `SalesOrders[Revenue_Order_Intake]`. |
| `Current Fiscal Month Sales Membrane sqft` | FORECAST_INTAKE | `KRW_NA_SAP_VBAP OI[Product Family]` | `SalesOrders[Product_Family_Product_Number]` |
| `Current Fiscal Month Sales ISO sqft` | FORECAST_INTAKE | `KRW_NA_SAP_VBAP OI[Product Family]` | `SalesOrders[Product_Family_Product_Number]` |
| `Current Fiscal Month Sales ISO bdft` | FORECAST_INTAKE | `KRW_NA_SAP_VBAP OI[Product Family]` | `SalesOrders[Product_Family_Product_Number]` |
| `Average Revenue per Product Family` | VBRP | `KRW_NA_SAP_AUSP[Product Family]` | Broken in production too. Reroute to `Billing[Product_Family]` OR skip. |
| `Average Margin per Product Family` | VBRP | `KRW_NA_SAP_AUSP[Product Family]` | Same — skip unless a report needs it. |

Additionally, every FORECAST measure referencing `[Current FYP VBRP]` or `[Current FYP VBAP OI]` is a cross-table MEASURE reference, not a column reference — will work as long as the helper measures exist in the model.

The AWIP `KRW_NA_FF_CALENDAR` relationship model must expose an active relationship (or an inactive one used via `USERELATIONSHIP`) between `SalesOrders[Product_Family_Product_Number]` (or a dedicated key) and the INTAKE dataflow. If not, the three cross-table filters above will not push into the forecast facts and will silently return unfiltered totals.

---

## 7. Special notes / gotchas

1. **`Current FYP VBRP` and `Current FYP VBAP OI` are the linchpins.** 13+ Current-Fiscal-Month / % Fcst / Split measures depend on them. Build them **first** in Phase 9; nothing else in the Current-Fiscal-Month cluster works without them. AWIP's `Selected Fiscal Period` reads a user-slicer, not the calendar for today — it is NOT a drop-in replacement.

2. **Hardcoded literals — DO NOT PORT AS-IS.**
   - Production `Current Fiscal Month Order FT2 for Membranes Hardcoded` filters `'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = "2026.2"`. Rewrite with `[Current FYP VBAP OI]`.
   - Production `Current Month Invoiced Sales ISO sqft FM` filters `[Fiscal Year Period Sorted] = "2026.02"`. Rewrite with `[Current FYP VBRP]`. Note the two literals use different month formatting (`.2` vs `.02`) suggesting different developers wrote them.

3. **Production copy-paste BUG:** `Sum Revenue in DC with sign VBAP OI` is defined on VBAP OI but sums VBRP. Do NOT replicate. The correct semantic — SUM of order-intake revenue — is already covered by AWIP's `[Order Intake]` on `_Measures`.

4. **Kingspan-preferred PY pattern is BETTER than production.** AWIP's `PY Revenue Order Intake`, `Sum PY Order Qty. in FT2 for Membranes OI`, `Sum PY Order Qty. in BFT2 for ISO OI` use `CALCULATE + YEAR/MONTH filter on KRW_NA_FF_CALENDAR[Date] + USERELATIONSHIP(SalesOrders[CreationDate_D8], KRW_NA_FF_CALENDAR[Date])`. Production uses either `SAMEPERIODLASTYEAR` (via `_Measures`) or the older `YEAR(...) = YEAR(TODAY())-1 + IF([Order Year OI] = ...)` guard. **Use the Kingspan pattern for all new PY measures** (this matches the project memory note).

5. **BFT vs BFT2 unit ambiguity.** Datasphere Billing exposes `Billing_Quantity_in_BFT` (used by AWIP `Sum Billing Qty. in BFT2 for ISO`). Production uses `[Billing Qty. in BFT2]`. If BFT != BFT2 in Datasphere semantics, the AWIP measure is numerically wrong. Same issue on SalesOrders `Requested_Quantity_in_BFT`. Verify against Datasphere column catalog **before** Phase 9.

6. **`Product Family` filter inconsistency.** Production mixes `"iso"`, `"ISO"`, `"Membrane"` — safe under DAX's case-insensitive `CONTAINSSTRING`. AWIP mostly uses `"iso"` and `"Membrane"`; the `SalesOrders[FC_Product_Group]` variant uses `"ISO"` and `"TPO"`. Preserve case-insensitive `CONTAINSSTRING` in any new measure.

7. **`DimDate` vs `KRW_NA_FF_CALENDAR`.** AWIP's `_Measures` PY family uses `'DimDate'[Date]` (a Power BI auto-generated or dedicated calendar), while the Kingspan pattern uses `KRW_NA_FF_CALENDAR[Date]`. This creates two parallel PY techniques in the same model. In Phase 9, decide which is canonical — mixing them will produce different PY numbers for the same visual depending on which measure is referenced.

8. **`Fiscal Year Period Sorted` vs `Fiscal Year Period`.** Production `Current Month Invoiced Sales ISO sqft FM` uses `[Fiscal Year Period Sorted]` (a numeric-sort variant). Other measures use `[Fiscal Year Period]`. When adding measures in AWIP, check which column exists on `KRW_NA_FF_CALENDAR` — the Datasphere calendar dataflow may expose only one.

9. **`Selected Fiscal Period` on Billing** is AWIP-only and reads a user slicer (`'Fiscal Period Selector'[FiscalYearPeriod]`). It is NOT equivalent to `[Current FYP VBRP]`. If a Phase 9 measure needs "the fiscal period for TODAY", use `[Current FYP VBRP]`; if it needs "the fiscal period the user selected in the slicer", use `[Selected Fiscal Period]`. Both belong in the model.

10. **`Sales` (AWIP) vs `Revenue` (prod) vs `Sum Revenue in DC with sign IS` (AWIP).** Three names for the same aggregate (SUM of net sales in company currency). Pick one canonical measure to expose on visuals and mark the others as internal / hidden to avoid confusion in the field list.

---

## Appendix — count reconciliation

- AWIP measures scanned: 15 (_Measures) + 20 (Billing raw) + 14 (SalesOrders) = 49
- Minus 11 `_Diagnostics` on Billing = **38** AWIP measures in scope
- Of those, AWIP-native / EXTRA IN AWIP: 15 (all of `_Measures`) + `Selected Fiscal Period` + `Sum Fcst Sales in FT2 for Membranes` + `Sum Billing Qty. in BFT2 for ISO 2` + `Sum Order Qty. in FT2 for Membranes SB 2` + `Sum Fcst Order Qty. in FT2 for Membranes OI` = 20
- Ports of production measures (with adaptation): 18
- Production measures with an AWIP counterpart (any classification): ~24 of 113 -> **~78% of production DAX has NOT been ported**.

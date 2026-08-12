# Phase 7 — Report Page Rebuild

**Scope authorization:** SAP-only. Customer.xlsx / KNVV / Salesforce dependencies deferred.

**Status as of 2026-08-11:** 8 production-mirror pages authored (3 verified live, 3 additional scaffolds pending user reload, 2 explicit "MISSING SOURCE" scaffolds). All 5 legacy pages retired.

---

## Pages delivered

### Page 1 — Invoiced Sales - Dashboard  ✅ verified with live data

Mirrors production page `76b1cd50241131d198dc`.

| Visual | Bound to | Live value |
|---|---|---|
| Title | "Invoiced Sales - Dashboard" | — |
| Slicer | `Billing.FiscalYearPeriod` | — |
| Slicer | `Billing.FC_Product_Group` | — |
| Card — ISO Rate | `[ISO Rate IS]` | **0.91** ✓ |
| Card — ISO Rate Fcst | `[ISO Rate Fcst IS]` | **0.00** (see finding #2 below) |
| multiRowCard — Invoiced Sales $ | SUM(Revenue), SUM(ForecastSales), SUM(PY_Revenue) | $3.09M / $12.64M / $3.12M |
| multiRowCard — Invoiced Membrane sqft | `[Sum Billing Qty. in FT2 for Membranes]`, SUM(ForecastSalesSQFT) | 2,471,200 / 13,538,375 |
| multiRowCard — Invoiced ISO bdft | `[Sum Billing Qty. in BFT2 for ISO]`, SUM(ForecastSalesBDFT) | 2,242,064 / 16,384,476 |
| Detail table (11 cols, built via UI) | Billing fields | ✓ rows populated |

### Page 2 — Order Intake - Dashboard  ✅ verified with live data

Mirrors production page `330491e0244bbed41069`.

| Visual | Bound to | Live value |
|---|---|---|
| Title | "Order Intake - Dashboard" | — |
| Slicer | `SalesOrders.FiscalPeriod` | — |
| Slicer | `SalesOrders.FC_Product_Group` | — |
| Card — ISO Rate OI | `[ISO Rate OI]` | **1.61** ✓ |
| Card — ISO Rate Fcst OI | `[ISO Rate Fcst OI]` | **2.63** ✓ **works** (unexpected — see finding #2) |
| multiRowCard — Order Intake $ | SUM(Revenue_Order_Intake), SUM(ForecastSales) | $4.76M / $12.64M |
| multiRowCard — Order Intake Membrane sqft | `[Sum Order Qty. in FT2 for Membranes OI]`, SUM(ForecastSalesSQFT) | 3,254,548 / 13,538,375 |
| multiRowCard — Order Intake ISO bdft | `[Sum Order Qty. in BFT2 for ISO OI]`, SUM(ForecastSalesBDFT) | 5,244,659 / 16,384,476 |
| Detail table (built via UI) | SalesOrders fields | ✓ |

### Page 3 — Backlog  ✅ verified with live data

Mirrors production page `d7d82ccc80735b013d61`. Production filters at page level (`Open_order_qty_flag='Y'`); we use a slicer instead — user sets to Y.

Values at fiscal period 2026007, `Open_order_qty_flag='Y'`:

| Visual | Bound to | Live value |
|---|---|---|
| Title | "Backlog" | — |
| Slicer | `SalesOrders.FiscalPeriod` | 2026007 |
| Slicer | `SalesOrders.FC_Product_Group` | (All) |
| Slicer | `SalesOrders.Open_order_qty_flag` | **Y** ← required for backlog semantics |
| Card — ISO Rate SB | `[ISO Rate SB]` | **0.59** ✓ |
| Card — Total Backlog $ | `[Total Backlog $]` | **$173,169** ✓ |
| multiRowCard — Backlog $ & Open Qty FT2 | SUM(Revenue_Backlog), SUM(Open_Order_Quantity_in_FT2) | $173,169 / 268,464 |
| multiRowCard — Backlog Membrane sqft (SB & SB 2) | `[Sum Order Qty. in FT2 for Membranes SB]`, `[... SB 2]` | **196,400 / 196,400** ← identical (see finding #4) |
| multiRowCard — Backlog ISO bdft (SB) | `[Sum Order Qty. in BFT2 for ISO SB]` | 115,200 |
| Detail table (built via UI) | SalesOrders fields | ✓ |

---

## Findings from building and running the pages

### Finding #1 — `tableEx` visualType is not reliably hand-authorable
JavaScript crash `TypeError: Cannot read properties of undefined (reading 'queryName')` in `TableExColumnHierarchyNavigator.getColumnIndexFromQueryName`. Occurs even with `NativeReferenceName` on all projections. **Workaround:** create tables via Power BI UI (drag fields onto Table visual). Once created, Power BI writes correct JSON we can copy as a template.

### Finding #2 — Forecast measures: RL treats OI-side differently than IS-side
Original Phase 1 assumption (documented in `unmapped-items.md`) was that ALL 4 forecast measures would return 0 because forecast rows in RL lack product-family classification. **Actual result:**

| Measure | Expected | Actual | Status |
|---|---|---|---|
| `ISO Rate Fcst IS` (Billing) | 0 (blocked) | **0** | Confirmed blocked — Billing forecast rows have `FC_Product_Group = blank` |
| `Sum Fcst Sales in FT2 for Membranes` (Billing) | 0 (blocked) | 0 | Same |
| `ISO Rate Fcst OI` (SalesOrders) | 0 (predicted blocked) | **2.63** ✓ | **Works** — Sales forecast rows DO carry FC_Product_Group |
| `Sum Fcst Order Qty. in FT2 for Membranes OI` (SalesOrders) | 0 (predicted blocked) | non-zero (~5M) | **Works** |

**Only 2 of 4 forecast measures are blocked** (both on the Billing side). The Sales-side forecast columns are properly classified — different Datasphere view design. `unmapped-items.md` must be corrected.

### Finding #3 — Visual-config format overrides get stripped by PBI validator
`objects.labels.labelDisplayUnits` and `labelPrecision` in visual JSON survive PBI's parser but format on the rendered card sometimes reverts to auto-scale (produces `$173.16907K` instead of `$173K`). Reliable fix is via UI: **Format pane → Callout value → Display units + Value decimal places**. Would need to check if there's a PBI-preferred spelling for these format overrides.

### Finding #4 — SB and SB 2 measures produce identical values (verified at 2026007)
Production has two measures for Backlog Membrane sqft:
- `Sum Order Qty. in FT2 for Membranes SB` = `SUMX(FILTER(SalesOrders, CONTAINSSTRING(FC_Product_Group, "TPO")), RequestedQuantityInBaseUnit)`
- `Sum Order Qty. in FT2 for Membranes SB 2` = `CALCULATE(SUMX(SalesOrders, [Open_Order_Quantity_in_FT2]), FC_Product_Group = "TPO")`

Different DAX approaches AND different underlying columns (`RequestedQuantityInBaseUnit` vs `Open_Order_Quantity_in_FT2`), yet **both return 196,400** at fiscal 2026007 with Open_order_qty_flag=Y. Suggests:
- When Open_order_qty_flag='Y' filter is active, `RequestedQuantityInBaseUnit` = `Open_Order_Quantity_in_FT2` for TPO rows (i.e. the requested quantity IS the open quantity for open orders)
- Production likely kept both because SB was original, SB 2 was added for a different scenario/QA. Without knowing which is preferred, we display both for transparency.

Consider asking Ana / James which measure is canonical for the Backlog dashboard so we can drop the other.

### Finding #5 — `Material` column is `Material_D17` in RL, not `Material`
Detail table initial version failed with "Something's wrong with one or more fields." Root cause: production HL exposed plain `Material`, RL exposes `Material_D17` (dimension-key form) plus `Material_D17_T` (text description). Detail tables must use `Material_D17` or `Material_D17_T`.

### Finding #6 — Multiple RL variants exist for several classification fields
When looking for fields in the Data pane, be aware RL has variants:
- `Plant` — plain, `Plant_D2`, `Plant_D2_T`, `Plant_A_2`, `PlantCategory`
- `Country` — plain, `Country1..Country6`
- `Region` — plain, `Region1..Region3`
- `Material` — `Material_D17`, `Material_D17_T` (no plain `Material` in RL)
- `Division` — plain, `Division2`, `Division_Product_Number`
- `SalesOrganization` — `SalesOrganization2`, `SalesOrganization_D13`, `SalesOrganization_D13_T`
- `FC_Product_Group` — plain, `FC_Product_Group1`, `FC_Product_Group_Product_Number` (Sales only)
- `Product_Family` — only `Product_Family_Product_Number` in RL (no plain)

Which variant is canonical depends on the visual purpose — use plain form for slicers/tables when it exists; use `_D#` for measure filters that match production semantics.

---

## Phase 7.5 additions (2026-08-11)

- **Kingspan logo** — copied from production `RegisteredResources/kingspan-roofing-waterproofing8422940714883275.png` to our `RegisteredResources/kingspan-logo.png`. Registered in report.json `resourcePackages`. Added to all pages via image visual at bottom-right (x=1080, y=650, 190×60). `image` visualType is hand-authorable ✓.
- **6 gauges** — 3 on Invoiced Sales - Dashboard, 3 on Order Intake - Dashboard. Placed off-canvas at y=720 (user drags into visible area). `gauge` visualType IS hand-authorable — the earlier failure was caused by `discourageImplicitMeasures` model setting, not by the visualType itself.
- **`discourageImplicitMeasures` removed** from `model.tmdl`. This unblocked drag-column-to-Value in ALL visual types (gauges, cards, charts). Trade-off: loses the governance guardrail against implicit aggregations. Re-enable by adding line 4 back if governance matters more than authoring speed.

## Phase 7 additions on 2026-08-11 (pages 6–8)

- **Backlog - Details** (Task 3) — 7 visuals: title, 3 slicers (Fiscal Period, Open Order Flag, Sales Doc Type), Filtered Backlog $ card, placeholder for detail table, Kingspan logo. Same pattern as Backlog Dashboard but detail-focused.
- **Extended Invoiced Sales - Dashboard** (Task 6a) — scaffold with 6 visuals: title, 2 SAP-native slicers, MISSING SOURCE placeholder text explaining Customer.xlsx blocker, working SAP multiRowCard (Revenue/Forecast/PY), detail table placeholder, Kingspan logo.
- **Extended Order Intake - Dashboard** (Task 6b) — parallel scaffold with 7 visuals following the same pattern.

Extended pages **partially reproduced only** — visuals depending on `Application`, `Industry`, `Sales Rep Name`, `Project Coordinator`, `Region (business-friendly)`, `Sold to party Description` are documented as MISSING SOURCE and left unresolved per the Phase 7 rule. Full reproduction blocked pending Customer.xlsx resolution.

## Task 4: Legacy pages retired (2026-08-11)

Deleted 2 pages that predate the reverse-engineering pivot:
- `Sales Overview` (custom, used our _Measures)
- `Sales Breakdown` (custom)

Retained: 8 production-mirror pages. Clean tab bar aligned to production intent.

## Task 5: Navigation buttons — UI recipe

Kept out of JSON. `actionButton` with pageNavigation is another untested visualType that may fail like tableEx. Fastest reliable path is the built-in Page Navigator:

1. Report view → any dashboard page
2. **Insert ribbon → Buttons → Navigator → Page navigator**
3. Power BI auto-generates a nav strip listing every page — click to jump. Drop it in the top-left where production has the home button.
4. To match production's per-page home+back pair instead: **Insert → Buttons → Blank** → Format → Action → Type = "Page navigation" → Destination = "Invoiced Sales - Dashboard" (or wherever home should be). Repeat for a Back button pointing to previous page.
5. Ctrl+S. Power BI writes the correct actionButton JSON.

## What's deferred / open for later phases

### Deferred (Phase 7.5)
- **AAGC Description slicer** — blocked by KNVV.csv dependency.
- **Shape band decorations** — cosmetic, low priority.
- **Backlog by Rep** page — needs Sales Rep Name from Customer.xlsx.

### Detail-table columns dropped from production (Customer.xlsx dependency)
- ProjectName / Customer Project Name
- Material Description
- Sales Representative (name)
- Project Coordinator

### Cosmetic issues to fix via UI (30 seconds each)
- Total Backlog $ card display: Callout value → Display units = Thousands, decimals = 0
- Consider auto-sizing detail table columns to fit content

### Pages not yet built
- Invoiced Sales - Detail (6 visuals in production)
- Order Intake - Detail (7 visuals)
- Extended Invoiced Sales - Dashboard (14 visuals — likely blocked by Customer.xlsx)
- Extended Order Intake - Dashboard (16 visuals — same)
- Backlog - Details (5 visuals)
- Backlog by Rep (7 visuals — needs SalesRep name from Customer.xlsx)

---

## Reusable pattern (for future pages)

Every dashboard page we built follows this recipe:

```
Row 0 (y=0, h=45)    : Title textbox (14, 0, 900x45)
Row 1 (y=55, h=80)   : 2-3 slicers (dropdown mode, 200x80 each) + 1-2 rate/KPI cards
Row 2 (y=150, h=235) : 3 multiRowCard KPI panels (415x235 each — dark blue / green / amber)
Row 3 (y=400, h=305) : Placeholder textbox for detail table (built via UI)
```

**Verified working visual types:** `textbox`, `slicer` (Dropdown mode), `cardVisual`, `multiRowCard`
**Verified broken:** `tableEx` (JavaScript crash — use UI to build tables)
**Untested:** `gauge`, `actionButton` (PageNavigation), `image`, `shape`

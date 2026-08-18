# Phase 12 — Post-Relationship Cleanup Plan

**Rule:** Do not remove an object until dependent visuals/measures have been checked. Every candidate below is classified as **KEEP**, **REPLACE**, **REMOVE**, or **REVIEW**.

---

## Cleanup candidates

### C1 — `DimDate` calculated table

**Location:** `AWIP_Commercial_Sales.SemanticModel/definition/tables/DimDate.tmdl`
**Current relationships:** two active (`Billing.BillingDocumentDate_D5 → DimDate.Date`, `SalesOrders.CreationDate_D8 → DimDate.Date`).
**Current dependents:**
- `_Measures[Sales PY]` — `SAMEPERIODLASTYEAR('DimDate'[Date])`
- `_Measures[Sales Quantity PY]` — same pattern
- `_Measures[Order Intake PY]` — same pattern
- `_Measures[Order Intake Quantity PY]` — same pattern
- 4 dependent variance measures (`Sales YoY %`, etc.) that reference the PY measures indirectly

**Classification:** **REPLACE** (with `KRW_NA_FF_CALENDAR` PY pattern).

**Migration steps:**
1. Rewrite the 4 PY measures. Options:
   - **Option A (SAMEPERIODLASTYEAR on FF calendar):** `CALCULATE([Sales], SAMEPERIODLASTYEAR('KRW_NA_FF_CALENDAR'[Date]))`. Requires KRW_NA_FF_CALENDAR marked as a date table with unique Date column.
   - **Option B (explicit YEAR filter, matching Kingspan's OI-side pattern from memory):**
     ```dax
     Sales PY =
         CALCULATE(
             [Sales],
             CALCULATETABLE(
                 VALUES('KRW_NA_FF_CALENDAR'[Date]),
                 FILTER(ALL('KRW_NA_FF_CALENDAR'),
                     YEAR('KRW_NA_FF_CALENDAR'[Date]) = MAX('KRW_NA_FF_CALENDAR'[Year]) - 1
                     && MONTH('KRW_NA_FF_CALENDAR'[Date]) = MAX('KRW_NA_FF_CALENDAR'[Month])
                 )
             )
         )
     ```
   - Prefer Option A if FF_CALENDAR has contiguous dates and can be marked as Date table.
2. Test each PY measure against production PY equivalents for period 2026007.
3. Delete the two `DimDate` relationships from `relationships.tmdl`.
4. Delete `DimDate.tmdl`.
5. Confirm no diagramLayout.json reference blocks load (safe to leave).

**Do NOT** delete DimDate in this task — the PY-measure rewrite is a small but nontrivial DAX change that deserves its own test cycle.

---

### C2 — Duplicate fiscal selectors

Not applicable — only `Fiscal Period Selector` exists. `KRW_NA_FF_FISCALPERIOD` is a separate role (calendar bridge, not a slicer target). **KEEP both.**

---

### C3 — Auto-detected relationships to review

The following relationships have `AutoDetected_*` GUIDs, indicating Power BI created them via the auto-detect feature (not via explicit design):

- `AutoDetected_5fec0261…` — KRW_NA_FF_FISCALPERIOD ↔ KRW_NA_FF_CALENDAR — **KEEP** (matches production exactly).
- `AutoDetected_db66fffc…` — KRW_NA_FF_HISTSB1 → CAPEX Approved — **KEEP** (out-of-scope but valid).
- `AutoDetected_b57492e0…` — Billing.State_Name → GEOINFO.State — **KEEP** (validated in Phase 5, flagged in Phase 11).
- `AutoDetected_da5932da…` — SalesOrders.State_Name → GEOINFO.State — **KEEP**.
- `AutoDetected_91ebea43…` — COSTELEM_OH1 ↔ COSTELEMHIER — **KEEP** (out-of-scope but valid).

None of these need rewriting; they just happen to have auto-detect naming.

---

### C4 — Disconnected FF tables (potentially removable, but preserve for other reports)

| Table | Related to any in-scope table? | Classification | Reason |
|---|---|---|---|
| KRW_NA_FF_COSTCENTREHIER | No | **REVIEW** | Cost domain, not Commercial Sales. Verify with Ana if AWIP scope includes P&L. If not, remove. |
| KRW_NA_FF_COSTCTHIER_ONDULINE | No | **REVIEW** | Same as above. |
| KRW_NA_FF_COSTELEMHIER | Yes (COSTELEM_OH1) | **KEEP** | Cost domain relationship exists. |
| KRW_NA_FF_COSTELEM_OH1 | Yes (COSTELEMHIER) | **KEEP** | Same. |
| KRW_NA_FF_PLSTRUCTURE | No | **REVIEW** | P&L structure, out of scope. |
| KRW_NA_FF_TERRITORY | No | **REVIEW** | Territory master — may connect to Billing.Territory_Name. Confirm with Ana. |
| KRW_NA_FF_ZIPCODES | No | **REVIEW** | Zip lookup — may be intended for zip-level map. Confirm. |
| KRW_NA_FF_HISTSB1 | Yes (CAPEX) | **KEEP** | CAPEX relationship exists. |
| CAPEX Approved | Yes (HISTSB1) | **KEEP** | Same. |

**Do not remove any of the REVIEW-classified tables in this task.** They may be legitimate infrastructure for other report pages. Confirm scope with Ana first.

---

### C5 — Legacy DAX helper measures (Billing / SalesOrders _Diagnostics folder)

Referenced in `iso-rate-investigation-status.md`:

> 11 diagnostic measures under `_Diagnostics` display folder on Billing table (not deleted — leave for now so we can pick up where we left off; safe to delete once resolved)

**Classification:** **REVIEW** — leave for now (ISO Rate investigation is paused, not closed).

---

### C6 — Backlog measures (SalesOrders side)

Any DAX measure that computes Backlog Revenue currently uses `CreationDate_D8` (implicitly via the active edge). Production uses `RequestedDeliveryDate`.

**Classification:** **REPLACE** — wrap in `USERELATIONSHIP(SalesOrders[RequestedDeliveryDate_dt], KRW_NA_FF_CALENDAR[Date])` for backlog-specific measures.

**Migration steps (follow-up work, NOT this task):**
1. Enumerate all measures on SalesOrders whose semantic is backlog (Revenue_Backlog, Open_Cost, Open_Order_Quantity_*, PY_Revenue_Backlog, Gross_Margin_for_open_orders, etc.).
2. For each, wrap the underlying date-dependent computation with USERELATIONSHIP as above.
3. Validate against production Backlog Dashboard for period 2026007.

---

### C7 — Auto Date/Time hidden tables

If Power BI's Auto Date/Time is on, hidden `LocalDateTable_*` tables will appear at model load. These are ignored by production (which explicitly relates to `KRW_NA_FF_CALENDAR`) but should be disabled for consistency.

**Steps:**
1. In Power BI Desktop → File → Options → Current file → Data Load → Time intelligence → uncheck "Auto date/time for new files" and "Auto date/time" (both).
2. Save + reload.

**Classification:** **REMOVE** by turning off the feature (no TMDL edit required — the tables disappear on reload).

---

## Summary decision matrix

| Object | Class | Action taken in this task? |
|---|---|---|
| DimDate table | REPLACE | No — deferred (see C1 migration steps) |
| DimDate → Billing/SalesOrders relationships | REPLACE | Kept active as legacy during transition |
| AutoDetected_* relationships | KEEP | All kept |
| KRW_NA_FF_COSTCENTREHIER, ONDULINE, PLSTRUCTURE | REVIEW | No — needs Ana confirmation |
| KRW_NA_FF_TERRITORY, ZIPCODES | REVIEW | No — needs Ana confirmation |
| Cost element hierarchy chain | KEEP | Kept |
| CAPEX + HISTSB1 | KEEP | Kept |
| Backlog measures | REPLACE (with USERELATIONSHIP) | No — follow-up work |
| _Diagnostics measures | REVIEW | Kept (ISO Rate paused) |
| Auto Date/Time LocalDateTable_* | REMOVE (via Power BI setting) | Requires Power BI Desktop action |

## What was DONE in this task's cleanup pass

- **Nothing was deleted.** All Phase 12 actions are documented but deferred to follow-up work with proper validation. The relationship rebuild (Phase 7) is complete; cleanup of DimDate, PY measure rewrites, backlog measure rewrites, and out-of-scope FF table pruning are follow-ups that each need their own change window and validation.

## What was ADDED in this task

- 2 calculated columns (`SalesOrders[RequestedDeliveryDate_dt]`, `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Billing Format]`)
- 3 new relationships (Billing→CALENDAR, SalesOrders→CALENDAR via RequestedDeliveryDate_dt inactive, Fiscal Period Selector↔FORECAST_INTAKE bothDir)
- 1 relationship activated (SalesOrders.CreationDate_D8 → CALENDAR, flipped from inactive to active)
- 6 new analysis documents (Phase 1–6, 8–12)

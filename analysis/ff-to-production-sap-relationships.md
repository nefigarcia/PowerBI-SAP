# Phase 2 — FF ↔ Production `_SAP_` Relationships (Translation Candidates)

**Rule:** Every production relationship where one side is a non-`_SAP_` FF dataflow table and the other is a `_SAP_` production table is a candidate for translation to the OData architecture (dev must use `Billing` / `SalesOrders` in place of the `_SAP_` side).

**Sourced from:** `analysis/production-odata-relationships-complete.md`

---

## 2a. Direct FF ↔ `_SAP_` relationships (6 rows)

| # | FF Table | FF Key | Prod `_SAP_` Table | Prod `_SAP_` Key | Active | Cardinality | Filter Direction |
|---|---|---|---|---|---|---|---|
| 4 | KRW_NA_FF_CALENDAR | Date | KRW_NA_SAP_VBRP | 'Billing Date' | true | one → many | single (FF filters SAP) |
| 7 | KRW_NA_FF_GEOINFO | COUNTRY_REGION | KRW_NA_SAP_KNA1 | COUNTRY_REGION | true | one → many | single (FF filters SAP) |
| 17 | 'KRW_NA_FF_GEOINFO OI' | COUNTRY_REGION | 'KRW_NA_SAP_KNA1 OI' | COUNTRY_REGION | true | one → many | single (FF filters SAP) |
| 22 | 'KRW_NA_FF_CALENDAR OI' | Date | 'KRW_NA_SAP_VBAP OI' | 'Document Date' | true | one → many | single (FF filters SAP) |
| 27 | 'KRW_NA_FF_GEOINFO SB' | COUNTRY_REGION | 'KRW_NA_SAP_KNA1 SB' | COUNTRY_REGION | true | one → many | single (FF filters SAP) |
| 35 | 'KRW_NA_FF_CALENDAR SB' | Date | 'KRW_NA_SAP_VBAP SB' | 'Requested Delivery Date' | true | one → many | single (FF filters SAP) |

**Reading:** `from` is the *many* side per the TMDL default (`fromCardinality: many` is implicit); TMDL `fromColumn: SAP…` → `toColumn: FF…` means SAP is the many-side and FF is the one-side. Filter flows from `to` (one) → `from` (many), i.e. FF → SAP. This IS the classic dim → fact direction.

---

## 2b. Indirect FF ↔ `_SAP_` chains (via FF-only bridge)

These are FF↔FF relationships that connect an FF dimension to a SAP fact through another FF table. They must be preserved in dev, but the terminal SAP-side attachment is one of rows 4/22/35 above.

| # | FF Table A | Bridge | FF Table B | Terminates on | Filter mechanism |
|---|---|---|---|---|---|
| 1 | KRW_NA_FF_FISCALPERIOD | 'Calendar Date' ↔ 'Calendar Date' (bothDir) | KRW_NA_FF_CALENDAR | KRW_NA_SAP_VBRP (via row 4) | Fiscal Year Period slicer → FISCALPERIOD → CALENDAR → VBRP |
| 2 | KRW_NA_FF_FISCALPERIOD | 'Fiscal Year Period' → 'Fiscal Year Period' (single) | 'FiscalYearPeriods Slicer' | (used as slicer only; the Slicer→FORECAST bothDir edge does the fact-side filtering) | |
| 12 | 'FiscalYearPeriods Slicer' | 'Fiscal Year Period' → 'Fiscal Year Period 2' (bothDir) | KRW-NA_FF_FORECAST | KRW_NA_SAP_VBRP filtering via VBRP.Billing Date → CALENDAR → FISCALPERIOD → Slicer | |
| 16 | 'KRW_NA_FF_FISCALPERIOD OI' | 'Calendar Date' ↔ 'Calendar Date' (bothDir) | 'KRW_NA_FF_CALENDAR OI' | 'KRW_NA_SAP_VBAP OI' (via row 22) | Fiscal Year Period slicer OI → FISCALPERIOD OI → CALENDAR OI → VBAP OI |
| 15 | 'KRW_NA_FF_FISCALPERIOD OI' | 'Fiscal Year Period' → 'Fiscal Year Period' | 'FiscalYearPeriods Slicer OI' | (slicer relay) | |
| 25 | 'FiscalYearPeriods Slicer OI' | 'Fiscal Year Period' → 'Fiscal Year Period' (bothDir) | KRW_NA_FF_FORECAST_INTAKE | Forecast intake side | |
| 26 | 'KRW_NA_FF_FISCALPERIOD SB' | 'Calendar Date' ↔ 'Calendar Date' (bothDir) | 'KRW_NA_FF_CALENDAR SB' | 'KRW_NA_SAP_VBAP SB' (via row 35) | |
| 31 | 'KRW_NA_FF_CALENDAR SB' | 'Fiscal Year Period' → 'Fiscal Year Period' | 'FiscalYearPeriods Slicer SB' | (SB variant places Fiscal Year Period on CALENDAR, not FISCALPERIOD — subtle difference from base and OI variants) | |

---

## 2c. Development translation target (per candidate)

| # (from 2a) | Production edge | Dev target edge | Notes |
|---|---|---|---|
| 4 | KRW_NA_FF_CALENDAR.Date ← VBRP.'Billing Date' | KRW_NA_FF_CALENDAR.Date ← Billing.BillingDocumentDate_D5 | VBRP = Billing (both are billing document items). Billing already has a relationship to DimDate on BillingDocumentDate_D5 — needs to be redirected/paralleled to KRW_NA_FF_CALENDAR.Date. |
| 22 | 'KRW_NA_FF_CALENDAR OI'.Date ← 'VBAP OI'.'Document Date' | KRW_NA_FF_CALENDAR.Date ← SalesOrders.CreationDate_D8 | VBAP OI = SalesOrders (order-intake view). "Document Date" ≈ SAP VBAK-AUDAT = the sales order creation date = `CreationDate_D8` in Datasphere. Dev has no `CALENDAR OI` variant → reuse the single `KRW_NA_FF_CALENDAR`. Existing dev already has an INACTIVE `SalesOrders.CreationDate_D8 → KRW_NA_FF_CALENDAR.Date` relationship — activate it (and inactivate the DimDate one). |
| 35 | 'KRW_NA_FF_CALENDAR SB'.Date ← 'VBAP SB'.'Requested Delivery Date' | KRW_NA_FF_CALENDAR.Date ← SalesOrders.RequestedDeliveryDate | VBAP SB = SalesOrders (backlog view). Backlog measures use RequestedDeliveryDate as the primary business date. Dev must add this as an inactive role-playing relationship (activated by USERELATIONSHIP in backlog measures). |
| 7 | KRW_NA_FF_GEOINFO.COUNTRY_REGION ← KNA1.COUNTRY_REGION | (see below) | KNA1 (customer master) is subsumed by Billing's flat customer columns. `COUNTRY_REGION` is a concatenation not present on Billing — replacement path: State-based join **or** compute equivalent COUNTRY_REGION on Billing. Existing dev uses `Billing.State_Name → KRW_NA_FF_GEOINFO.State` — a different key. Grain/coverage must be validated (Phase 5). |
| 17 | 'KRW_NA_FF_GEOINFO OI'.COUNTRY_REGION ← 'KNA1 OI'.COUNTRY_REGION | (single GEOINFO; SalesOrders.State_Name → KRW_NA_FF_GEOINFO.State — already exists) | Same as row 7, applied to SalesOrders. |
| 27 | 'KRW_NA_FF_GEOINFO SB'.COUNTRY_REGION ← 'KNA1 SB'.COUNTRY_REGION | (same physical relationship as row 17 — SB is a role-play, but Billing/SalesOrders don't have SB variants; a single geographical filter on SalesOrders covers both OI and SB reads if the SB DAX uses SalesOrders too) | Ana-side clarification needed if SB uses a distinct SalesOrders subset. |

---

## 2d. Additional production edges to be preserved with pure-FF variants (no SAP translation needed)

These stay purely FF ↔ FF and must be recreated in dev (with role-play collapse to a single FF variant):

| Production edge | Dev edge |
|---|---|
| KRW_NA_FF_FISCALPERIOD ↔ KRW_NA_FF_CALENDAR on 'Calendar Date' (bothDir, 1:many) | Same edge on dev's single KRW_NA_FF_FISCALPERIOD ↔ KRW_NA_FF_CALENDAR (already exists) |
| KRW_NA_FF_FISCALPERIOD → 'FiscalYearPeriods Slicer' on 'Fiscal Year Period' | Not needed — dev uses `Fiscal Period Selector` (calculated distinct from Billing[FiscalYearPeriod]). The `Fiscal Period Selector`↔KRW-NA_FF_FORECAST via billing-format bridge already provides the same behavior. |
| 'FiscalYearPeriods Slicer' ↔ KRW-NA_FF_FORECAST on 'Fiscal Year Period 2' (bothDir) | Already exists in dev via `KRW-NA_FF_FORECAST[Fiscal Year Period Billing Format]` ↔ `Fiscal Period Selector[FiscalYearPeriod]` |
| 'FiscalYearPeriods Slicer OI' ↔ KRW_NA_FF_FORECAST_INTAKE on 'Fiscal Year Period' (bothDir) | **MISSING in dev.** Must be added: KRW_NA_FF_FORECAST_INTAKE[?] ↔ Fiscal Period Selector[FiscalYearPeriod] with matching format. |

---

## 2e. Production edges that are pure SAP↔SAP (NOT translated — subsumed by OData flat columns)

These are production relationships internal to the SAP dataflow graph. They are subsumed by the OData facts (Billing/SalesOrders already carry customer, delivery, material, item category attributes as flat columns):

| # | Prod edge | Why not translated |
|---|---|---|
| 3 | VBRP.'Sold To' → KNA1.Customer | Billing.SoldToParty_D12, Billing.CustomerFullName* already flat on Billing |
| 5 | VBRP.'Delivery Document' → LIKP.'Delivery Document' | Billing already carries delivery-related date fields where needed |
| 6 | VBRP.CUST_SALES → KNVV.CUST_SALES | Billing.CustomerGroup, Billing.CustomerClassification* flat on Billing |
| 14 | VBRP.'Item Category' → TVAPT.'Item Category' | Billing.SalesDocumentItemCategory, SalesDocumentItemType flat on Billing |
| 23 | 'VBAP OI'.Sold-To → 'KNA1 OI'.Customer | SalesOrders.SoldToParty_D3 flat on SalesOrders |
| 24 | 'VBAP OI'.CUST_SALES → 'KNVV OI'.CUST_SALES | SalesOrders.CustomerGroup* flat on SalesOrders |
| 32 | 'VBAP SB'.Material → 'MARM_BFT 2'.Material | UoM conversion factors — Billing already carries `Factor_UoM_BFT`, `Factor_Alternative_UoM_to_Base_UoM`; SalesOrders equivalents to be confirmed |
| 33 | 'VBAP SB'.Sold-To → 'KNA1 SB'.Customer | Same as row 23 |
| 36 | 'VBAP SB'.SO_ITEM ↔ LIPS.DOC_ITM (bothDir) | Delivery quantities not modeled in OData directly — potential gap for Backlog quantities delivered; flag in Phase 11 |
| 37 | 'VBAP SB'.CUST_SALES → 'KNVV SB'.CUST_SALES | Same as row 24 |

Row 36 (VBAP SB ↔ LIPS) is the one non-trivial subsumption — the LIPS "Quantity Delivered" columns feed backlog calculations. If AWIP's Backlog measures use these fields, we may need a substitute source for delivered quantities. **Flag for Phase 11.**

---

## Summary — what changes in dev

**Add (or activate)** these relationships:

1. `Billing.BillingDocumentDate_D5` → `KRW_NA_FF_CALENDAR.Date` (many-to-one, single) — replaces VBRP.'Billing Date' → CALENDAR.Date
2. `SalesOrders.CreationDate_D8` → `KRW_NA_FF_CALENDAR.Date` (many-to-one, single, **activate existing inactive**) — replaces VBAP OI.'Document Date' → CALENDAR OI.Date
3. `SalesOrders.RequestedDeliveryDate` → `KRW_NA_FF_CALENDAR.Date` (many-to-one, single, **inactive role-play** — activated via USERELATIONSHIP in backlog measures) — replaces VBAP SB.'Requested Delivery Date' → CALENDAR SB.Date
4. `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period]`-format ↔ `Fiscal Period Selector[FiscalYearPeriod]` (one-to-many, bothDir) — replaces Slicer OI ↔ FORECAST_INTAKE

**Keep existing:**
- `KRW_NA_FF_FISCALPERIOD.'Calendar Date'` ↔ `KRW_NA_FF_CALENDAR.'Calendar Date'` (bothDir, 1:many)
- `KRW-NA_FF_FORECAST[Fiscal Year Period Billing Format]` ↔ `Fiscal Period Selector[FiscalYearPeriod]` (bothDir, 1:1)
- `Billing.State_Name` → `KRW_NA_FF_GEOINFO.State` (subject to Phase 5 grain validation)
- `SalesOrders.State_Name` → `KRW_NA_FF_GEOINFO.State` (subject to Phase 5 grain validation)

**Retire / deactivate:**
- `Billing.BillingDocumentDate_D5` → `DimDate.Date` (superseded by KRW_NA_FF_CALENDAR)
- `SalesOrders.CreationDate_D8` → `DimDate.Date` (superseded)
- Potentially the entire `DimDate` table (Phase 12)

**Do NOT recreate:**
- All `LocalDateTable_*` auto-generated tables (turn Auto Date/Time off in dev)
- SAP↔SAP internal edges (rows 3, 5, 6, 14, 23, 24, 32, 33, 36, 37)
- OI/SB role-play copies of FF dims — collapse to single instances (dev has no CALENDAR OI/SB, FISCALPERIOD OI/SB, GEOINFO OI/SB, or Slicer OI/SB variants and does not need them since the two OData facts do double-duty)

**Flag as unresolved (Phase 11):**
- KRW_NA_FF_GEOINFO join key — production uses `COUNTRY_REGION`, dev uses `State`; grain differs and needs Ana-side clarification
- VBAP SB ↔ LIPS delivered-quantity subsumption — confirm no measure in AWIP relies on LIPS delivered-quantity columns

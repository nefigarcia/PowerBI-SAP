# Phase 5 — Relationship Grain Validation (Pre-Implementation)

**Purpose:** for every relationship targeted by Phase 7, validate cardinality, data-type, null/blank behavior, uniqueness on the one-side, and filter direction *before* creating the relationship. This is a static (schema-level) validation because we do not have direct data access; runtime grain will be re-tested in Phases 9–10.

---

## R1 — `Billing[BillingDocumentDate_D5]` → `KRW_NA_FF_CALENDAR[Date]`

| Check | Result |
|---|---|
| Data types | dateTime ↔ dateTime ✅ |
| One-side uniqueness | `KRW_NA_FF_CALENDAR[Date]` — one row per calendar day, assumed unique per the dataflow's design; verify by loading. |
| Many-side null/blank | `Billing[BillingDocumentDate_D5]` — expected non-null on every posted billing document; unposted/draft rows may be null but are filtered out by Datasphere's `SAP_SD_RL_BillingDocumentItem_V2` view. |
| Cardinality | many-to-one ✅ |
| Filter direction | single (CALENDAR → Billing) — matches production `VBRP.Billing Date → CALENDAR.Date` (production TMDL default is many→one, single). |
| Active | true |
| Composite key needed | no |
| Bridge needed | no |
| Bidirectional required | no (production is single direction) |

**Verdict:** SAFE to create.

---

## R2 — `SalesOrders[CreationDate_D8]` → `KRW_NA_FF_CALENDAR[Date]` (activate existing inactive)

| Check | Result |
|---|---|
| Data types | dateTime ↔ dateTime ✅ |
| One-side uniqueness | Same as R1 ✅ |
| Many-side null/blank | Non-null on every posted sales order line. |
| Cardinality | many-to-one ✅ |
| Filter direction | single (CALENDAR → SalesOrders) |
| Active | **true** (currently inactive — flip to active) |
| Composite key needed | no |

**Verdict:** SAFE to activate. Corresponding `SalesOrders[CreationDate_D8] → DimDate[Date]` must be inactivated (or removed in Phase 12) to prevent ambiguity.

---

## R3 — `SalesOrders[RequestedDeliveryDate_dt]` (calculated) → `KRW_NA_FF_CALENDAR[Date]` (inactive role-play)

| Check | Result |
|---|---|
| Data types | dateTime ↔ dateTime ✅ (after calculated-column addition) |
| Source `RequestedDeliveryDate` type | string ⚠ — must add calculated `RequestedDeliveryDate_dt` first (see Phase 4) |
| One-side uniqueness | Same as R1 ✅ |
| Many-side null/blank | `RequestedDeliveryDate` may be BLANK on lines where SAP has no requested date populated. Calculated column handles this by returning BLANK; BLANK on many-side is legal but rows won't participate in date filtering — matches production behavior. |
| Cardinality | many-to-one ✅ |
| Filter direction | single (CALENDAR → SalesOrders) |
| Active | **false** — role-play; measures activate via `USERELATIONSHIP` |
| Composite key needed | no |

**Verdict:** SAFE to create as INACTIVE role-play. Do not activate — leave the OI-side (`CreationDate_D8`) as the active date relationship on SalesOrders.

---

## R4 — Keep existing `Billing[State_Name]` → `KRW_NA_FF_GEOINFO[State]`

| Check | Result |
|---|---|
| Data types | string ↔ string ✅ |
| One-side uniqueness | ⚠ `KRW_NA_FF_GEOINFO[State]` is NOT guaranteed unique — the same state name can appear multiple times if the dataflow rows contain multiple countries or duplicate territory entries. Production avoided this by joining on `COUNTRY_REGION` (a country+region composite). |
| Many-side null/blank | `Billing[State_Name]` — international rows may have BLANK. |
| Cardinality | Currently declared `many-to-many`? Need to inspect. Existing dev relationship (`AutoDetected_b57492e0…`) omits `fromCardinality`, so TMDL defaults to many→one. Power BI would have rejected load if State is non-unique — so it IS unique in the current dataset, or the current relationship line is quietly wrong. |
| Bridge needed | Depends on grain. If uniqueness holds → no bridge. If not → replace with a `COUNTRY_REGION` calculated-column join. |
| Bidirectional required | no |

**Verdict:** KEEP for now, **FLAG in Phase 11** for Ana-side validation. If a KPI test in Phase 9/10 reveals geographic filter propagation gives wrong totals, replace with a `COUNTRY_REGION` calculated column join.

Same verdict applies to R4b: `SalesOrders[State_Name]` → `KRW_NA_FF_GEOINFO[State]`.

---

## R5 — Add `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Billing Format]` (calculated) ↔ `Fiscal Period Selector[FiscalYearPeriod]`

| Check | Result |
|---|---|
| Data types | string ↔ string ✅ (both `YYYYPPP`, e.g. `2026007`) |
| One-side uniqueness | `Fiscal Period Selector[FiscalYearPeriod]` — DISTINCT of Billing[FiscalYearPeriod], so unique by construction ✅ |
| Many-side null/blank | FORECAST_INTAKE has one row per period per forecast dimension; `Fiscal Year Period Sorted` non-null. |
| Cardinality | one-to-many (Selector → FORECAST_INTAKE) ✅ |
| Filter direction | **bothDirections** — production requires bothDir so that FORECAST_INTAKE row selection can filter the selector (and consequently Billing). Matches prod `FiscalYearPeriods Slicer OI ↔ FORECAST_INTAKE`. |
| Active | true |
| Composite key needed | no |
| Bridge needed | no — the calculated column IS the bridge |

**Verdict:** SAFE to create after calculated column is added.

---

## Grain risks summary

| Relationship | Risk | Mitigation |
|---|---|---|
| R1, R2 | None significant | — |
| R3 | RequestedDeliveryDate string format may not be ISO-8601 | Phase 5 runtime check: sample one value; DATEVALUE fallback |
| R4 | GEOINFO.State may not be unique across countries | Kept as-is with flag; test in Phase 9 |
| R5 | FORECAST_INTAKE[Fiscal Year Period Sorted] may have different format than KRW-NA_FF_FORECAST's | Pattern-mirror the calculated column; verify sample value |

## Cardinality decision matrix (final)

| Edge | Cardinality | Filter direction | Active |
|---|---|---|---|
| Billing[BillingDocumentDate_D5] → KRW_NA_FF_CALENDAR[Date] | many-to-one | single | ✅ active |
| SalesOrders[CreationDate_D8] → KRW_NA_FF_CALENDAR[Date] | many-to-one | single | ✅ active (flip from inactive) |
| SalesOrders[RequestedDeliveryDate_dt] → KRW_NA_FF_CALENDAR[Date] | many-to-one | single | ❌ inactive (role-play) |
| KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Billing Format] ↔ Fiscal Period Selector[FiscalYearPeriod] | many-to-one | **bothDirections** | ✅ active |
| Billing[BillingDocumentDate_D5] → DimDate[Date] | (existing) | single | ❌ **retire in Phase 12** |
| SalesOrders[CreationDate_D8] → DimDate[Date] | (existing) | single | ❌ **retire in Phase 12** |
| Billing[State_Name] → KRW_NA_FF_GEOINFO[State] | (existing, keep) | single | ✅ active (flag Phase 11) |
| SalesOrders[State_Name] → KRW_NA_FF_GEOINFO[State] | (existing, keep) | single | ✅ active (flag Phase 11) |

**No many-to-many introduced. No bidirectional introduced beyond what production requires.**

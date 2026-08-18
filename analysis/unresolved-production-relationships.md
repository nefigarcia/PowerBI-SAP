# Phase 11 — Unresolved Production Relationships

Production relationships that we deliberately did NOT translate to dev, along with the reason and what would be needed to close the gap.

---

## U1 — LIKP delivery header (Delivery Document + Delivery Date)

**Production edge:** `KRW_NA_SAP_VBRP.'Delivery Document' → KRW_NA_SAP_LIKP.'Delivery Document'` (row 5)
**Also:** `KRW_NA_SAP_LIKP.'Delivery Date' → LocalDateTable_89c50fe7…` (row 11)

**Why not translated in dev:**
- Dev `Billing` OData feed does not carry `DeliveryDocument` or `DeliveryDate` columns.
- Dataflow `SAP_SD_RL_BillingDocumentItem_V2` (Datasphere) does not project these fields.

**Candidate replacement:** none currently available in dev.

**Impact:**
- Any measure or visual that displays or filters by `LIKP.Delivery Date` is not reproducible in dev.
- Scan production DAX for `LIKP.Delivery Date` references — if found, those measures cannot be ported without extending the OData feed.

**Ask Ana:**
- Is `Delivery Date` (from LIKP) required for any Commercial Sales dashboard visuals?
- If yes, can Datasphere expose a `SAP_SD_RL_DeliveryHeader` view for OData ingestion?

---

## U2 — LIPS delivery item (Quantity Delivered)

**Production edge:** `KRW_NA_SAP_VBAP SB.SO_ITEM ↔ KRW_NA_SAP_LIPS.DOC_ITM` (row 36, bothDir 1:many)

**Why not translated in dev:**
- Dev `SalesOrders` does not carry `Quantity Delivered BUoM` or `Quantity Delivered SUoM`.
- Backlog logic in production reads from `LIPS.Quantity Delivered` to compute how much of an ordered quantity has actually been delivered.

**Candidate replacement:** partial — dev SalesOrders has `ConfdDelivQtyInOrderQtyUnit`, `TargetDelivQtyInOrderQtyUnit`, `ConfdDeliveryQtyInBaseUnit` which may cover the same semantic if backlog measures use "confirmed delivery" instead of "actually delivered".

**Impact:**
- Backlog "delivered" quantities may be under- or over-reported vs. production if the "confirmed" values diverge from the "actually delivered" values at the row level.

**Ask Ana:**
- Do production backlog measures reference `LIPS.Quantity Delivered` directly?
- If yes, is `ConfdDeliveryQtyInBaseUnit` an acceptable substitute, or must we ingest a `SAP_SD_RL_DeliveryItem` OData feed?

---

## U3 — Customer master (KNA1) → Geography via COUNTRY_REGION

**Production edge:** `KRW_NA_SAP_KNA1.COUNTRY_REGION → KRW_NA_FF_GEOINFO.COUNTRY_REGION` (rows 7, 17, 27)

**Why not translated exactly in dev:**
- Neither `Billing` nor `SalesOrders` has a pre-concatenated `COUNTRY_REGION` column.
- The concatenation format is unknown without sample data (`US_TX`? `USA-TX`? `US|TX`? etc.).

**Dev substitute in place:** `Billing.State_Name → KRW_NA_FF_GEOINFO.State` (existing) and `SalesOrders.State_Name → KRW_NA_FF_GEOINFO.State`.

**Impact:**
- If State is unique across all countries in `KRW_NA_FF_GEOINFO`, functionally equivalent.
- If State duplicates across countries (e.g., "Chihuahua" in Mexico could collide with a state named "Chihuahua" elsewhere, or "Ontario" appears in both Canada and California), state-level filters may aggregate wrong rows.

**Ask Ana:**
- Confirm the format of `KRW_NA_FF_GEOINFO.COUNTRY_REGION` values (sample: 5 rows).
- Confirm whether `KRW_NA_FF_GEOINFO.State` is unique across all rows or whether State duplicates across Country.
- If duplicates exist and any dashboard uses country-level slicers, we need to add a `COUNTRY_REGION` calculated column on Billing/SalesOrders and switch the relationship.

**Test that would settle it in dev alone:**
```dax
DEFINE MEASURE 'KRW_NA_FF_GEOINFO'[State non-unique count] =
    COUNTROWS(FILTER(SUMMARIZE('KRW_NA_FF_GEOINFO', 'KRW_NA_FF_GEOINFO'[State], "Rows", COUNTROWS('KRW_NA_FF_GEOINFO')), [Rows] > 1))
```
If > 0 → duplicates exist → COUNTRY_REGION alternative needed.

---

## U4 — MARM_BFT UoM conversion factors for SalesOrders

**Production edge:** `KRW_NA_SAP_VBAP SB.Material → KRW_NA_SAP_MARM_BFT 2.Material` (row 32)

**Why not translated in dev:**
- Dev `SalesOrders` carries pre-computed conversion factors as flat columns (`Requested_Quantity_in_BFT`, `Order_Quantity_in_BFT2`, `Order_Quantity_in_FT2`, `Order_Quantity_in_M2`).
- These are Datasphere-side calculated columns and are expected to be equivalent to production's MARM-joined per-row calculation.

**Impact:**
- If the pre-computed columns use different UoM factors than MARM_BFT (e.g., stale factors, wrong denominator), the totals will diverge.

**Ask Ana:**
- Are the OData-side UoM conversion columns computed from the same MARM master data as production?
- Are there ever cases where a material has multiple valid UoM factors and the OData column picks the wrong one?

---

## U5 — Salesforce Quote / Quote Line Item tables

**Production tables:** `Salesforce Quotes`, `Salesforce Quote Line Item` (rows 38–45).

**Why not translated in dev:**
- These tables are absent from `AWIP_Commercial_Sales.PBIP`.
- Task scope does not include the Salesforce quote data pipeline.

**Impact:**
- Any production report page using Salesforce quotes is not reproducible in dev.

**Ask Ana:**
- Is a Salesforce quotes report page part of AWIP scope? If yes, source (dataflow / OData / connector) needs to be identified.

---

## Non-issues explicitly cleared

The following production edges are NOT unresolved — they are subsumed by OData flat columns:

- VBRP.Sold To → KNA1.Customer (row 3) — Billing.SoldToParty_D12 flat column
- VBRP.CUST_SALES → KNVV.CUST_SALES (row 6) — Billing.CustomerGroup etc. flat
- VBRP.Item Category → TVAPT.Item Category (row 14) — Billing.SalesDocumentItemCategory + _T flat
- All OI/SB role-play copies of KNA1, KNVV — same subsumption
- All LocalDateTable_* Auto Date/Time relationships — dev has Auto Date/Time OFF; single KRW_NA_FF_CALENDAR handles all
- FiscalYearPeriods Slicer OI/SB variants — dev uses single Fiscal Period Selector

---

## Priority ranking

| Item | Blocks a report page? | Blocks a KPI? | Fixable in dev alone? |
|---|---|---|---|
| U1 (LIKP Delivery Date) | Possibly | Only if a measure uses `LIKP.Delivery Date` | No — needs Datasphere feed |
| U2 (LIPS Quantity Delivered) | Possibly (Backlog) | Only if backlog measures use LIPS | Partial — with confirmed-delivery substitute |
| U3 (COUNTRY_REGION join key) | No | Possibly geographic totals | Yes — with calculated columns |
| U4 (MARM UoM) | No | Possibly Order Intake / Backlog quantities | Partial — trust OData pre-compute |
| U5 (Salesforce Quotes) | Yes (if quotes page in scope) | Yes (quote-based KPIs) | No — needs Salesforce feed |

**Recommend addressing U3 first** (small dev-only change) then bringing U1/U2/U5 to Ana with impact statements.

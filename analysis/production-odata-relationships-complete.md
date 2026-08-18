# Phase 1 — Complete Production OData Relationship Inventory

**Source:** `production-reference-odata/Amalgamated Sales Reports - JC.SemanticModel/definition/relationships.tmdl`
**Extraction date:** 2026-08-17
**Total relationships:** 45

## Table classification legend

- **NON_SAP_DATAFLOW** — Kingspan-authored FF dataflow table (Power BI dataflow). Not sourced from raw SAP.
- **SAP_DATAFLOW** — `_SAP_`-named table sourced (in production) via DirectQuery to AAS cubes `KRW_NA_SM_INVOICED`, `KRW_NA_SM_SORDERS`, or `KRW_NA_SM_BACKLOG`. **These must NOT be imported into the development model**; the SAP Datasphere OData facts `Billing` and `SalesOrders` replace them.
- **LOCAL_OR_CALCULATED** — Slicer table, auto-generated `LocalDateTable_*`, or calculated table (e.g. `FiscalYearPeriods Slicer` variants, `LocalDateTable_*`).
- **UNKNOWN** — Salesforce or other external source.

---

## Full relationship inventory

| # | From Table | From Column | To Table | To Column | Cardinality | Cross Filter | Active | From Class | To Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | KRW_NA_FF_FISCALPERIOD | 'Calendar Date' | KRW_NA_FF_CALENDAR | 'Calendar Date' | one-to-many | bothDirections | true | NON_SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 2 | KRW_NA_FF_FISCALPERIOD | 'Fiscal Year Period' | 'FiscalYearPeriods Slicer' | 'Fiscal Year Period' | many-to-one (default) | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 3 | KRW_NA_SAP_VBRP | 'Sold To' | KRW_NA_SAP_KNA1 | Customer | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 4 | KRW_NA_SAP_VBRP | 'Billing Date' | KRW_NA_FF_CALENDAR | Date | many-to-one | single | true | SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 5 | KRW_NA_SAP_VBRP | 'Delivery Document' | KRW_NA_SAP_LIKP | 'Delivery Document' | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 6 | KRW_NA_SAP_VBRP | CUST_SALES | KRW_NA_SAP_KNVV | CUST_SALES | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 7 | KRW_NA_SAP_KNA1 | COUNTRY_REGION | KRW_NA_FF_GEOINFO | COUNTRY_REGION | many-to-one | single | true | SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 8 | KRW_NA_FF_CALENDAR | Date | LocalDateTable_7549747c…061b | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 9 | KRW_NA_FF_CALENDAR | 'Start of Month' | LocalDateTable_2db857ee…8a5a | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 10 | KRW_NA_FF_CALENDAR | 'End of Month' | LocalDateTable_8f0aa0e5…f2a9 | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 11 | KRW_NA_SAP_LIKP | 'Delivery Date' | LocalDateTable_89c50fe7…41a3 | Date | one-to-one | single | true | SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 12 | 'FiscalYearPeriods Slicer' | 'Fiscal Year Period' | KRW-NA_FF_FORECAST | 'Fiscal Year Period 2' | one-to-many | bothDirections | true | LOCAL_OR_CALCULATED | NON_SAP_DATAFLOW |
| 13 | KRW_NA_SAP_VBRP | 'Requested Delivery Date' | LocalDateTable_750892a4…feb0 | Date | one-to-one | single | true | SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 14 | KRW_NA_SAP_VBRP | 'Item Category' | KRW_NA_SAP_TVAPT | 'Item Category' | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 15 | 'KRW_NA_FF_FISCALPERIOD OI' | 'Fiscal Year Period' | 'FiscalYearPeriods Slicer OI' | 'Fiscal Year Period' | many-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 16 | 'KRW_NA_FF_FISCALPERIOD OI' | 'Calendar Date' | 'KRW_NA_FF_CALENDAR OI' | 'Calendar Date' | one-to-many | bothDirections | true | NON_SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 17 | 'KRW_NA_SAP_KNA1 OI' | COUNTRY_REGION | 'KRW_NA_FF_GEOINFO OI' | COUNTRY_REGION | many-to-one | single | true | SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 18 | 'KRW_NA_FF_CALENDAR OI' | Date | 'LocalDateTable_7549747c…061b 2' | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 19 | 'KRW_NA_FF_CALENDAR OI' | 'Start of Month' | 'LocalDateTable_2db857ee…8a5a 2' | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 20 | 'KRW_NA_FF_CALENDAR OI' | 'End of Month' | 'LocalDateTable_8f0aa0e5…f2a9 2' | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 21 | 'KRW_NA_SAP_VBAP OI' | 'Requested Delivery Date' | LocalDateTable_fe6033ef…abbcf | Date | one-to-one | single | true | SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 22 | 'KRW_NA_SAP_VBAP OI' | 'Document Date' | 'KRW_NA_FF_CALENDAR OI' | Date | many-to-one | single | true | SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 23 | 'KRW_NA_SAP_VBAP OI' | Sold-To | 'KRW_NA_SAP_KNA1 OI' | Customer | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 24 | 'KRW_NA_SAP_VBAP OI' | CUST_SALES | 'KRW_NA_SAP_KNVV OI' | CUST_SALES | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 25 | 'FiscalYearPeriods Slicer OI' | 'Fiscal Year Period' | KRW_NA_FF_FORECAST_INTAKE | 'Fiscal Year Period' | one-to-many | bothDirections | true | LOCAL_OR_CALCULATED | NON_SAP_DATAFLOW |
| 26 | 'KRW_NA_FF_FISCALPERIOD SB' | 'Calendar Date' | 'KRW_NA_FF_CALENDAR SB' | 'Calendar Date' | one-to-many | bothDirections | true | NON_SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 27 | 'KRW_NA_SAP_KNA1 SB' | COUNTRY_REGION | 'KRW_NA_FF_GEOINFO SB' | COUNTRY_REGION | many-to-one | single | true | SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 28 | 'KRW_NA_FF_CALENDAR SB' | Date | 'LocalDateTable_7549747c…061b 3' | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 29 | 'KRW_NA_FF_CALENDAR SB' | 'Start of Month' | 'LocalDateTable_2db857ee…8a5a 3' | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 30 | 'KRW_NA_FF_CALENDAR SB' | 'End of Month' | 'LocalDateTable_8f0aa0e5…f2a9 3' | Date | one-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 31 | 'KRW_NA_FF_CALENDAR SB' | 'Fiscal Year Period' | 'FiscalYearPeriods Slicer SB' | 'Fiscal Year Period' | many-to-one | single | true | NON_SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 32 | 'KRW_NA_SAP_VBAP SB' | Material | 'KRW_NA_SAP_MARM_BFT 2' | Material | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 33 | 'KRW_NA_SAP_VBAP SB' | Sold-To | 'KRW_NA_SAP_KNA1 SB' | Customer | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 34 | 'KRW_NA_SAP_VBAP SB' | 'Document Date' | LocalDateTable_78efd809…3fb2 | Date | one-to-one | single | true | SAP_DATAFLOW | LOCAL_OR_CALCULATED |
| 35 | 'KRW_NA_SAP_VBAP SB' | 'Requested Delivery Date' | 'KRW_NA_FF_CALENDAR SB' | Date | many-to-one | single | true | SAP_DATAFLOW | NON_SAP_DATAFLOW |
| 36 | 'KRW_NA_SAP_VBAP SB' | SO_ITEM | KRW_NA_SAP_LIPS | DOC_ITM | one-to-many | bothDirections | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 37 | 'KRW_NA_SAP_VBAP SB' | CUST_SALES | 'KRW_NA_SAP_KNVV SB' | CUST_SALES | many-to-one | single | true | SAP_DATAFLOW | SAP_DATAFLOW |
| 38 | 'Salesforce Quotes' | CreatedDate | LocalDateTable_7a2d5ba1…078d | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 39 | 'Salesforce Quotes' | LastModifiedDate | LocalDateTable_c07dbbc8…ac9c | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 40 | 'Salesforce Quotes' | SystemModstamp | LocalDateTable_a8248b06…f33b | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 41 | 'Salesforce Quotes' | LastViewedDate | LocalDateTable_5cf4f00f…a72a | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 42 | 'Salesforce Quotes' | LastReferencedDate | LocalDateTable_b630bc67…e244 | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 43 | 'Salesforce Quotes' | ExpirationDate | LocalDateTable_7973285a…7319 | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 44 | 'Salesforce Quote Line Item' | (7 date columns) | (7 LocalDateTable_*) | Date | one-to-one | single (datePartOnly) | true | UNKNOWN | LOCAL_OR_CALCULATED |
| 45 | 'Salesforce Quote Line Item' | QuoteId | 'Salesforce Quotes' | Id | many-to-one | single | true | UNKNOWN | UNKNOWN |

Rows 38–44 in the table above collapse the individual Salesforce date-hierarchy relationships for brevity — see the underlying `relationships.tmdl` for the individual GUIDs.

---

## Relationship counts by class combination

| From Class → To Class | Count |
|---|---|
| SAP_DATAFLOW → SAP_DATAFLOW | 11 |
| SAP_DATAFLOW → NON_SAP_DATAFLOW | 4 |
| SAP_DATAFLOW → LOCAL_OR_CALCULATED | 5 |
| NON_SAP_DATAFLOW → NON_SAP_DATAFLOW | 3 |
| NON_SAP_DATAFLOW → LOCAL_OR_CALCULATED | 8 |
| LOCAL_OR_CALCULATED → NON_SAP_DATAFLOW | 2 |
| UNKNOWN (Salesforce) → LOCAL_OR_CALCULATED / UNKNOWN | 12 |
| **TOTAL** | **45** |

---

## Notes for downstream phases

### Non-obvious observations

- **Only 3 production relationships live entirely inside the FF world** (rows 1, 16, 26 — each `FISCALPERIOD.Calendar Date ↔ CALENDAR.Calendar Date`, one per AAS cube). None of these link to a SAP fact.
- **Every SAP-fact-to-FF-dim relationship** (the ones we must translate to OData) is a `SAP_DATAFLOW → NON_SAP_DATAFLOW` edge — 4 rows (4, 22, 35, plus indirectly row 7 which is SAP → NON_SAP through geography). Rows 15 SAP_DATAFLOW → SAP_DATAFLOW (VBRP→LIKP, VBAP OI→KNA1 OI, etc.) are internal to the SAP graph and are subsumed by the OData facts (the OData facts already carry the relevant customer / delivery / material attributes as flat columns).
- **`FiscalYearPeriods Slicer` (base/OI/SB)** — production models the slicer as a *dimension* filtering `FORECAST` (`Slicer → FORECAST`) with bothDirections. FISCALPERIOD filters into the Slicer (`FISCALPERIOD → Slicer`, single direction). This is a bridge chain: `FF_CALENDAR ↔ FISCALPERIOD → Slicer ↔ FORECAST`.
- **LocalDateTable_* relationships are auto-generated** by Power BI's Auto Date/Time feature. They should NOT be recreated in dev — dev should turn Auto Date/Time OFF and rely on `KRW_NA_FF_CALENDAR` (or a single equivalent) for all date variation hierarchies.
- **`Salesforce Quotes` / `Salesforce Quote Line Item`** exist in production but are NOT the subject of this task. They have no cross-relationship to the SAP/FF graph in production. In dev they are absent — leave them out.
- **Fiscal Year Period format mismatch:** production `FiscalYearPeriods Slicer.[Fiscal Year Period]` (matched by `KRW_NA_FF_FISCALPERIOD.[Fiscal Year Period]` — same string format) has one format; `KRW-NA_FF_FORECAST.[Fiscal Year Period 2]` matches it (string join). Compare with `Billing[FiscalYearPeriod]` = `"2026007"` (YYYYPPP). Dev must reconcile these formats (already done via calculated column `Fiscal Year Period Billing Format` on `KRW-NA_FF_FORECAST`).
- **VBRP has TWO date-facing relationships**: `Billing Date → CALENDAR.Date` (active) and `Requested Delivery Date → LocalDateTable_750892a4` (auto date hierarchy only). The primary business date is Billing Date.
- **VBAP OI has TWO date-facing relationships**: `Document Date → CALENDAR OI.Date` (active), `Requested Delivery Date → LocalDateTable_fe6033ef` (auto date hierarchy only). Primary business date is Document Date.
- **VBAP SB has TWO date-facing relationships**: `Document Date → LocalDateTable_78efd809` (auto date only), `Requested Delivery Date → CALENDAR SB.Date` (active). Primary business date is **Requested Delivery Date** (not Document Date — inverted from OI).

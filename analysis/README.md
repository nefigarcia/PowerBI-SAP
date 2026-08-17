# Amalgamated Sales — Reverse Engineering Analysis

> ⚠ **SCOPE RESET (2026-08-13):** The previous reverse-engineering used the WRONG production reference (`production-reference/`, ODBC-based). That work is invalid as the source of truth. The correct production reference is **`production-reference-odata/`** (OData-based) — architecturally much closer to what we are rebuilding.

## Source-of-truth priority (in order)

1. `production-reference-odata/Amalgamated Sales Reports - JC.SemanticModel/` — business logic source of truth
2. `production-reference-odata/Amalgamated Sales Reports - JC.Report/` — report / page / visual source of truth
3. SAP Datasphere OData Billing (`Billing.pbix` extracted to `_extract/Billing/`)
4. SAP Datasphere OData SalesOrders (`Sales.pbix` extracted to `_extract/Sales/`)
5. Kingspan Power BI Dataflows — **excluding any dataflow whose entity name contains `_SAP_`** (see rule below)
6. Screenshots — visual reference only

The old `production-reference/` (ODBC) is **not** a source of truth anymore.

## Dataflow inclusion rule

Include ALL dataflows EXCEPT those whose entity name contains `_SAP_`. `_SAP_` dataflows are duplicates of the SAP Datasphere OData Billing / SalesOrders feeds — using them would double-count the same data.

- **Excluded** (from the OData production reference): `KRW_NA_SAP_KNA1` (+ OI + SB), `KRW_NA_SAP_KNVV` (+ OI + SB), `KRW_NA_SAP_LIKP`, `KRW_NA_SAP_LIPS`, `KRW_NA_SAP_MARM_BFT` (×2), `KRW_NA_SAP_TVAPT`, `KRW_NA_SAP_TVM3T`, `KRW_NA_SAP_VBAP` (+ OI + SB), `KRW_NA_SAP_VBPA2`, `KRW_NA_SAP_VBRP`
- **Included:** `KRW-NA_FF_FORECAST`, `KRW_NA_FF_CALENDAR` (+ OI + SB), `KRW_NA_FF_FISCALPERIOD` (+ OI + SB), `KRW_NA_FF_FORECAST_INTAKE`, `KRW_NA_FF_GEOINFO` (+ OI + SB), `FiscalYearPeriods Slicer` (+ OI + SB), `Salesforce Quote Line Item`, `Salesforce Quotes`
- **AWIP dataflows check (2026-08-13):** none of AWIP's 13 dataflow tables contain `_SAP_` → all 13 remain valid.

## Projects

| Role | Path |
|---|---|
| Production reference — OData (source of truth, READ ONLY) | `production-reference-odata/Amalgamated Sales Reports - JC.pbip` |
| Production reference — ODBC (DEPRECATED, do not use) | `production-reference/Amalgamated Sales Production.pbip` |
| New Billing source | `Billing.pbix` (extracted to `_extract/Billing/`) |
| New SalesOrders source | `Sales.pbix` (extracted to `_extract/Sales/`) |
| Development target | `AWIP_Commercial_Sales.PBIP` |

## Confidence levels used in mappings

- **EXACT** — identical field name AND identical data content AND identical measure semantics
- **STRONG** — identical semantics with minor naming differences, verified by data type + sample values
- **POSSIBLE** — plausible mapping but not proven; requires business validation before use
- **NOT FOUND** — no equivalent in the accepted-source hierarchy; measure/field cannot be reproduced without an additional dataset

## Files in this folder — current status

### Current (OData-based) — post-reset analysis
| File | Purpose | Status |
|---|---|---|
| `odata-production-model-inventory.md` | OData production semantic model inventory | Phase 1 — in progress |
| `odata-production-report-inventory.md` | OData production report inventory | Phase 2 — in progress |
| `odata-production-source-architecture.md` | Table classification (Billing/Sales/Dataflow/Derived) | Phase 3 — pending |
| `odata-vs-development-diff.md` | Diff production vs AWIP | Phase 4 — pending |
| `odata-measure-validation.md` | Measure-by-measure validation | Phase 5 — pending |
| `odata-dataflow-crosswalk.md` | Non-`_SAP_` dataflow crosswalk to production | Phase 6 — pending |
| `odata-source-mapping.md` | Production field → new-source crosswalk | Phase 7 — pending |
| `obsolete-odbc-derived-work.md` | ODBC-derived logic to remove | Phase 8 — pending |
| `odata-validation-results.md` | KPI comparison AWIP vs OData production | Phase 10 — pending |

### Historical (superseded — kept for context)
| File | Notes |
|---|---|
| `README.md` (this file) | Updated for OData reset |
| `production-model-inventory.md` | Based on ODBC reference — DEPRECATED |
| `production-measures.md` | Based on ODBC reference — DEPRECATED |
| `production-relationships.md` | Based on ODBC reference — DEPRECATED |
| `production-report-pages.md` | Based on ODBC reference — DEPRECATED |
| `billing-field-inventory.md` | Field inventory of Billing.pbix — still valid |
| `sales-field-inventory.md` | Field inventory of Sales.pbix — still valid |
| `source-mapping.md` | Based on ODBC comparison — may be wrong |
| `measure-dependency-map.md` | Based on ODBC measures — DEPRECATED |
| `unmapped-items.md` | Marked SUPERSEDED (dataflow discovery, then OData reset) |
| `missing-data-sources.md` | Marked SUPERSEDED (dataflow discovery, then OData reset) |
| `validation-results.md` | Based on old comparison — DEPRECATED |
| `phase5-changes.md` / `phase7-changes.md` | Historical — retained |
| `dataflow-inventory.md` | Inventory of the 13 dataflows added to AWIP — still valid |
| `dataflow-production-crosswalk.md` | Crossmap of dataflows to previously-missing fields — reconcile against OData in Phase 6 |
| `dataflow-relationships.md` | Relationships analysis — still valid |
| `recovered-missing-fields.md` | Fields recovered via dataflows — reconcile against OData in Phase 12 |
| `still-missing-after-dataflows.md` | Salesforce residual — likely valid, verify in Phase 12 |

## Phase status (12-phase re-run against OData)

- [ ] Phase 1: OData semantic model inventory (running)
- [ ] Phase 2: OData report inventory (running)
- [ ] Phase 3: Source architecture classification
- [ ] Phase 4: Compare OData production vs AWIP
- [ ] Phase 5: Measure validation (special check on ISO Rate)
- [ ] Phase 6: Dataflow re-evaluation (exclude `_SAP_`)
- [ ] Phase 7: Source crosswalk
- [ ] Phase 8: Remove ODBC-derived work
- [ ] Phase 9: Repair semantic model to match OData behaviour
- [ ] Phase 10: KPI validation
- [ ] Phase 11: Report rebuild
- [ ] Phase 12: Re-evaluate false MISSING SOURCE warnings

## Guardrails (unchanged)

- `production-reference-odata/` = READ ONLY
- `production-reference/` = DEPRECATED (do not rely on)
- `AWIP_Commercial_Sales.PBIP/` = DEVELOPMENT TARGET (only editable target)
- `analysis/` = all outputs land here
- Do not invent substitutes for missing production content
- Do not use `_SAP_` dataflows
- Do not rely on the ODBC reference

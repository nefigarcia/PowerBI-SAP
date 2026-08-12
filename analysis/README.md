# Amalgamated Sales — Reverse Engineering Analysis

**Status:** Phase 1 in progress. Read-only inventory of production model + new Billing/Sales sources. No modifications yet.

## Projects

| Role | Path |
|---|---|
| Production reference (source of truth, READ ONLY) | `production-reference/Amalgamated Sales Production.pbip` |
| New Billing source | `Billing.pbix` (extracted to `_extract/Billing/`) |
| New Sales source | `Sales.pbix` (extracted to `_extract/Sales/`) |
| Current combined dev project | `AWIP_Commercial_Sales.PBIP` (existing — will be aligned to production in Phase 5+) |

## Source system change

- **Production** connects to `SAP_SD_HL_*` views (H-suffix = *historical/persisted* CDS/analytic views).
- **New Billing/Sales** connect via **SAP Datasphere OData** to `SAP_SD_RL_*` views (R-suffix = *runtime/replication* analytic model exposed by Datasphere).
- Column naming may differ (e.g. `FC Product Group` vs `FC_Product_Group`). Column existence must be verified per measure before we can call any mapping EXACT.

## Files in this folder

| File | Purpose |
|---|---|
| `production-model-inventory.md` | Every production table, column, calc column, measure, hierarchy — verbatim |
| `production-measures.md` | Every production DAX measure with dependencies traced |
| `production-relationships.md` | All relationships, cardinalities, active/inactive |
| `production-report-pages.md` | Every page + every visual + fields referenced |
| `billing-field-inventory.md` | Columns/fields available in new Billing.pbix (SAP Datasphere OData) |
| `sales-field-inventory.md` | Columns/fields available in new Sales.pbix (SAP Datasphere OData) |
| `source-mapping.md` | Production field → new source crosswalk, with confidence |
| `measure-dependency-map.md` | Recursive DAX dependency graph per measure |
| `unmapped-items.md` | Fields/measures with no proven equivalent in the new source |
| `missing-data-sources.md` | Production tables/tables that don't have a new-source counterpart at all (Quote, User, KNVV, Customer) |
| `validation-results.md` | Filled in Phase 8 after model is rebuilt |

## Confidence levels used in mappings

- **EXACT** — identical field name AND identical data content AND identical measure semantics
- **STRONG** — identical semantics with minor naming differences (e.g. `FC Product Group` ↔ `FC_Product_Group`), verified by data type + sample values
- **POSSIBLE** — plausible mapping but not proven; requires business validation before use
- **NOT FOUND** — no equivalent in the new source; measure/field cannot be reproduced without an additional dataset

## Phase status

- [x] Phase 1: Read-only inventory (in progress — 3 parallel Explore agents running)
- [ ] Phase 2: Extract production measures (in progress)
- [ ] Phase 3: Field crosswalk
- [ ] Phase 4: Classify KPI sources (Billing / Sales / derived / dimension / external / unknown)
- [ ] Phase 5: Rebuild semantic model
- [ ] Phase 6: No hardcoded values (rule)
- [ ] Phase 7: Rebuild report pages
- [ ] Phase 8: Validation
- [ ] Phase 9: ISO Rate deep dive (partial — dependency chain traced, mapping pending)
- [ ] Phase 10: Safety (git baseline commit — pending user go-ahead)

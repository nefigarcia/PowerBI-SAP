# Obsolete ODBC-Derived Work

**Rule:** the `production-reference/` (ODBC) project is DEPRECATED. Anything derived from it must be re-verified against `production-reference-odata/` before use.

**Method:** cross-reference every analysis file + AWIP semantic-model artefact against the OData reference. Flag items whose provenance is the ODBC reference.

---

## 1. Analysis files (`analysis/`) — status after the ODBC → OData reset

| File | Provenance | Status | Reconciled by |
|---|---|---|---|
| `README.md` | Updated 2026-08-13 for reset | ✅ Current | — |
| `production-model-inventory.md` | ODBC (Phase 1 pre-reset) | ⚠ DEPRECATED — do not use for measure/field truth | Superseded by `odata-production-model-inventory.md` |
| `production-measures.md` | ODBC | ⚠ DEPRECATED — production measures listed here are H-view names, not OData/AAS-cube names | Superseded by `odata-measure-validation.md` |
| `production-relationships.md` | ODBC | ⚠ DEPRECATED — relationships shown here are for H-view SAP tables, not the AAS-cube DirectQuery topology | Superseded by relationships section of `odata-production-model-inventory.md` |
| `production-report-pages.md` | ODBC (may partially match) | ⚠ DEPRECATED — page IDs, visual JSON, and visual counts differ | Superseded by `odata-production-report-inventory.md` |
| `billing-field-inventory.md` | Field inventory of `Billing.pbix` — Datasphere-native | ✅ Still valid (Datasphere-side inventory, not ODBC-derived) | — |
| `sales-field-inventory.md` | Field inventory of `Sales.pbix` — Datasphere-native | ✅ Still valid | — |
| `source-mapping.md` | ODBC-comparison-based | ⚠ DEPRECATED (misclassified sources due to ODBC vs OData semantics mismatch) | Superseded by `odata-source-mapping.md` |
| `measure-dependency-map.md` | ODBC measure graph | ⚠ DEPRECATED — dependency graph anchored on H-view measures, not applicable | Superseded by `odata-measure-validation.md` §1 |
| `unmapped-items.md` | ODBC-era classifications | ⚠ SUPERSEDED (already marked 2026-08-12; re-anchored by OData reset) | Superseded by `still-missing-after-dataflows.md` + `odata-source-mapping.md` |
| `missing-data-sources.md` | ODBC-era classifications | ⚠ SUPERSEDED (already marked 2026-08-12) | Superseded by `still-missing-after-dataflows.md` (which itself needs a Phase-12 review vs OData) |
| `validation-results.md` | ODBC-comparison-based | ⚠ DEPRECATED — KPI comparisons were vs ODBC, not vs OData | Superseded by `odata-validation-results.md` (Phase 10, pending) |
| `phase5-changes.md` | ODBC-based phase 5 rebuild log | ⚠ HISTORICAL — kept for audit trail | — |
| `phase7-changes.md` | ODBC-based phase 7 rebuild log | ⚠ HISTORICAL | — |
| `dataflow-inventory.md` | Post-dataflow (still valid, TMDL inventory of AWIP dataflows) | ✅ Still valid | — |
| `dataflow-production-crosswalk.md` | Crosswalk against ODBC missing-source list | ⚠ PARTIALLY VALID — the AWIP-column recoveries are correct, but the "confidence promoted from ODBC list" logic needs Phase 12 re-check vs OData | Superseded by `odata-source-mapping.md` for confidence, retained for AWIP column names |
| `dataflow-relationships.md` | Purely on AWIP dataflows | ✅ Still valid | — |
| `recovered-missing-fields.md` | Post-dataflow recovery list | ⚠ PARTIALLY VALID — recoveries themselves are correct; the "solves this production visual" claims need Phase 12 re-check vs OData visual inventory | Retained; annotate with OData-side confirmation in Phase 12 |
| `still-missing-after-dataflows.md` | Post-dataflow residual | ⚠ PARTIALLY VALID — Salesforce residual confirmed, but the "everything else is recovered" claim needs Phase 12 re-check vs OData visual inventory | Retained; extend in Phase 12 |
| `odata-production-model-inventory.md` | OData reference | ✅ CURRENT (Phase 1) | — |
| `odata-production-report-inventory.md` | OData reference (v1 page-level) | ✅ CURRENT (Phase 2 v1) | — |
| `odata-production-source-architecture.md` | OData reference | ✅ CURRENT (Phase 3) | — |
| `odata-vs-development-diff.md` | OData reference | ✅ CURRENT (Phase 4) | — |
| `odata-measure-validation.md` | OData reference | ✅ CURRENT (Phase 5) | — |
| `odata-dataflow-crosswalk.md` | OData reference | ✅ CURRENT (Phase 6) | — |
| `odata-source-mapping.md` | OData reference | ✅ CURRENT (Phase 7) | — |
| `obsolete-odbc-derived-work.md` (this file) | OData reference | ✅ CURRENT (Phase 8) | — |

**Recommended cleanup action:** for each deprecated file, add a SUPERSEDED banner at the top pointing to its replacement. Do NOT delete — the historical audit trail is valuable. The two SUPERSEDED banners already added on 2026-08-12 (`unmapped-items.md`, `missing-data-sources.md`) are good templates.

## 2. AWIP semantic-model artefacts — provenance check

| Artefact | Provenance | Impact |
|---|---|---|
| `_Measures[Sales / Sales Quantity / …]` (15 measures) | Written during ODBC-era rebuild | ✅ FUNCTIONALLY EQUIVALENT to production (verified in Phase 5). Underlying columns (`SlsVolNetAmt_CC` etc.) are Datasphere-native, not ODBC-derived. Retain. |
| `Billing[ISO Rate IS]` and related "ISO Rate" measures | Written during ODBC-era rebuild | ✅ Formula shape matches production; retain. |
| `Billing[Sum Fcst Sales in FT2 for Membranes]` (as fixed 2026-08-12) | Written to fix an ODBC-era measure using dataflow-added Billing columns | ⚠ WRONG SOURCE per OData reference. Retain as a stopgap; **re-source in Phase 9** to use `KRW-NA_FF_FORECAST` once imported. |
| `Billing[ISO Rate Fcst IS]` | Same | ⚠ WRONG SOURCE per OData reference. Same treatment. |
| `SalesOrders[ISO Rate Fcst OI]` and related order-intake forecast measures | Written during ODBC-era rebuild | ⚠ WRONG SOURCE potentially — should use `KRW_NA_FF_FORECAST_INTAKE` (already in AWIP) columns directly like production does. Rewrite in Phase 9. |
| `SB` / `SB 2` duplicate measures | ODBC-era artefacts | ⚠ Reconcile duplicates in Phase 5 verification / Phase 9 cleanup. |
| `DimDate` (custom date table) | AWIP-original design | ✅ Not ODBC-derived. Retain (or optionally align to production's `KRW_NA_FF_CALENDAR`-based date columns). |
| Relationships: `Billing[BillingDocumentDate_D5]→DimDate[Date]`, `SalesOrders[CreationDate_D8]→DimDate[Date]` | AWIP-original | ✅ Not ODBC-derived. Retain. |
| Auto-detected relationships: State→GEOINFO, FISCALPERIOD↔CALENDAR (× 2), COSTELEM_OH1↔COSTELEMHIER, HISTSB1→CAPEX Approved | Auto-detected by PBI post-dataflow addition | ✅ Verified in Phase 4. Retain. |
| Report visuals (8 pages rebuilt during ODBC-era Phase 7) | ODBC-comparison-based | ⚠ NEEDS REVIEW in Phase 11 — page structure may match production but underlying field references need re-verification against `odata-production-report-inventory.md` |

## 3. AWIP report artefacts — provenance check

| Page (as built in AWIP) | ODBC-era or OData-verified? | Action |
|---|---|---|
| Invoiced Sales - Dashboard | ODBC-era rebuild — page structure inferred from ODBC report | Phase 11 review vs OData `Invoiced Sales - Dashboard` (16 visuals) |
| Invoiced Sales - Detail | same | Phase 11 review vs OData `Invoiced Sales - Detail` (6 visuals) |
| Order Intake - Dashboard | same | Phase 11 review vs OData `Order Intake - Dashboard` (16 visuals) |
| Order Intake - Detail | same | Phase 11 review vs OData `Order Intake - Detail` (6 visuals) |
| Backlog | same | Phase 11 review vs OData `Backlog` (11 visuals) |
| Backlog Details | same | Phase 11 review vs OData `Backlog - Details` (6 visuals) |
| Backlog by Rep | same | Phase 11 review vs OData `Backlog by Rep` (11 visuals) |
| Summary | same | Phase 11 review vs OData `Summary Page` (27 visuals — biggest single-page workload) |
| (not yet built) Extended Invoiced Sales | — | Phase 11 build vs OData (14 visuals) |
| (not yet built) Extended Order Intake | — | Phase 11 build vs OData (14 visuals) |
| (not yet built) Navigation Page + Navigation split | — | Phase 11 build vs OData (24 + 5 visuals) |
| (not yet built) Page 1 (hidden scratch in prod) | — | Confirm with business owner whether to build |

## 4. Cleanup checklist for Phase 9 (semantic model) and Phase 11 (report)

**Phase 9 model repair actions traced to ODBC obsolescence:**
1. Rewrite `Billing[Sum Fcst Sales in FT2 for Membranes]` to source from `KRW-NA_FF_FORECAST[Sales Membrane sqft]` (after dataflow import).
2. Rewrite `Billing[ISO Rate Fcst IS]` to use `KRW-NA_FF_FORECAST` columns directly.
3. Rewrite `SalesOrders[ISO Rate Fcst OI]` and `SalesOrders[Sum Fcst Order Qty. in FT2 for Membranes OI]` to source from `KRW_NA_FF_FORECAST_INTAKE` verbatim.
4. Delete or repurpose `Sum Billing Qty. in BFT2 for ISO 2` and `Sum Order Qty. in FT2 for Membranes SB 2` (duplicates from ODBC era).
5. Add missing measures per `odata-measure-validation.md` §4 (10 invoice-side + 5 order-side + PY variants).

**Phase 11 report review actions:**
1. Compare each rebuilt AWIP page against its OData counterpart (per `odata-production-report-inventory.md`).
2. Verify field references on each visual — replace any leftover `KRW_NA_SAP_VBRP[…]` / `KRW_NA_SAP_VBAP OI[…]` refs (if any exist from an earlier attempt) with `Billing[…]` / `SalesOrders[…]`.
3. Confirm slicer coverage matches production (Product Family, Fiscal Period).

## 5. What is NOT ODBC-derived (retain as-is)

- The 13 AWIP dataflow imports (all `PowerPlatform.Dataflows`, Kingspan workspace, no ODBC involvement).
- `Billing.pbix` / `Sales.pbix` OData connections (native Datasphere).
- The `discourageImplicitMeasures = false` state on the model (set during a UI probe in ODBC era, but the setting itself is not ODBC-tied).
- The report theme (`CY26SU05`) — actually AWIP uses this while production uses `CY24SU10`. Not a defect; theme drift.
- All UTF-8 file conventions, TMDL formatting, and Git structure.

**Written:** 2026-08-13

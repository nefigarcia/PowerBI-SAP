# OData Dataflow Crosswalk (excluding `_SAP_`)

**Rule:** exclude every table whose name contains `_SAP_` — they're covered by SAP Datasphere OData Billing/SalesOrders.

**Sources of truth:**
- Production dataflow tables: see `odata-production-model-inventory.md` §Role-playing dimension copies + §Forecast tables
- AWIP dataflow tables: see `dataflow-inventory.md`

---

## 1. Master dataflow crosswalk (non-`_SAP_` only)

| OData production dataflow | AWIP equivalent | AWIP dataflowId | Status | Role in report |
|---|---|---|---|---|
| `KRW_NA_FF_CALENDAR` (INVOICED role) | `KRW_NA_FF_CALENDAR` (single, workspaceId `24b96353-…`) | `ba1d8f9b-3b34-4e61-907e-7ca9db97b302` | ✅ IN AWIP | Calendar dim |
| `KRW_NA_FF_CALENDAR OI` (SORDERS role) | (same AWIP CALENDAR, shared) | same | ✅ IN AWIP | Same dim reused for OI fact |
| `KRW_NA_FF_CALENDAR SB` (BACKLOG role) | (same AWIP CALENDAR, shared) | same | ✅ IN AWIP | Same dim reused for SB fact |
| `KRW_NA_FF_FISCALPERIOD` (INVOICED role) | `KRW_NA_FF_FISCALPERIOD` (single) | *(not captured in earlier read)* | ✅ IN AWIP | Fiscal calendar dim |
| `KRW_NA_FF_FISCALPERIOD OI` | (same, shared) | same | ✅ IN AWIP | Reused |
| `KRW_NA_FF_FISCALPERIOD SB` | (same, shared) | same | ✅ IN AWIP | Reused |
| `KRW_NA_FF_GEOINFO` (INVOICED role) | `KRW_NA_FF_GEOINFO` (single) | `447d5626-27df-44c5-bc5e-b56916bdb28c` | ✅ IN AWIP | State geography (via `Billing/SalesOrders[State_Name]` join) |
| `KRW_NA_FF_GEOINFO OI` | (same, shared) | same | ✅ IN AWIP | Reused |
| `KRW_NA_FF_GEOINFO SB` | (same, shared) | same | ✅ IN AWIP | Reused |
| `KRW_NA_FF_FORECAST_INTAKE` | `KRW_NA_FF_FORECAST_INTAKE` | *(not captured)* | ✅ IN AWIP | Order-intake forecast (fiscal-period grain) — source of `ISO Rate Fcst VBAP` / `Current Fiscal Month Sales Membrane sqft` in prod |
| `KRW-NA_FF_FORECAST` **(hyphen — invoice-side forecast)** | ❌ **NOT IN AWIP** | *(unknown — needs Kingspan)* | **MISSING** | Source of `ISO Rate Fcst` / `Current Month Invoice Revenue Fcst` / all `Current Month Invoiced Sales *` / all `YTD Invoiced Sales *` measures in prod (10 measures) |
| `FiscalYearPeriods Slicer` (INVOICED) | ❌ NOT IN AWIP (functionally covered by `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`) | — | MISSING (functionally covered) | Disconnected slicer for FORECAST filtering. Prod pattern: bi-di relationship to FORECAST |
| `FiscalYearPeriods Slicer OI` | ❌ NOT IN AWIP | — | Same |
| `FiscalYearPeriods Slicer SB` | ❌ NOT IN AWIP | — | Same |
| `Salesforce Quote Line Item` | ❌ NOT IN AWIP | — | MISSING | Business decision |
| `Salesforce Quotes` | ❌ NOT IN AWIP | — | MISSING | Business decision |

## 2. AWIP dataflows NOT in OData production (8 tables — different report scope)

| AWIP dataflow | AWIP dataflowId | Confirmed absent from OData? | Assessment |
|---|---|---|---|
| `KRW_NA_FF_TERRITORY` | `bd3aacdc-369c-486d-b9bc-a3837dc9cda1` | ✅ absent | Territory dim — extra for a non-Amalgamated-Sales report |
| `KRW_NA_FF_ZIPCODES` | *(not captured)* | ✅ absent | Zip → territory bridge — same |
| `KRW_NA_FF_PLSTRUCTURE` | `bd64cee7-1d35-46fb-97c7-5c3e15128af9` | ✅ absent | Tagetik P&L structure — different report scope |
| `KRW_NA_FF_HISTSB1` | `84b23137-ac92-40f8-a3f8-0df06d8f2399` | ✅ absent | CAPEX postings — different scope |
| `KRW_NA_FF_COSTCENTREHIER` | `d28982b1-b94f-43cd-b719-bbaa14b77ba1` | ✅ absent | Cost centre hierarchy — different scope |
| `KRW_NA_FF_COSTCTHIER_ONDULINE` | `eb55fefb-ef02-45d0-bd04-a6acf7d801a0` | ✅ absent | Onduline cost centres — different scope |
| `KRW_NA_FF_COSTELEM_OH1` | `e5c6d724-cdf3-4ed9-9d6b-93a946f4b312` | ✅ absent | Cost element leaves — different scope |
| `KRW_NA_FF_COSTELEMHIER` | `a5cced2b-1fe6-48a6-937e-b8d2ec91ad34` | ✅ absent | Cost element hierarchy — different scope |
| `'CAPEX Approved'` | *(not captured)* | ✅ absent | CAPEX orders — different scope |

**Recommendation:** for the Amalgamated Sales rebuild, these 8+CAPEX tables should be **hidden from the field picker** (`isHidden: true` on table level in TMDL) but retained in the model — they may be needed later. Do not remove unless Ana / James confirm the CAPEX / cost-accounting scope is fully out.

## 3. Enrichment-field lookups (re-verified against OData reference)

Re-checking previously-recovered enrichment items against the OData production dataflow set:

| Enrichment field | Previous status (dataflow crosswalk) | Now in OData production? | Verdict |
|---|---|---|---|
| Geography — State / lat/long / Country_Region | STRONG via `KRW_NA_FF_GEOINFO` | ✅ same in prod (3 role-copies) | CONFIRMED STRONG |
| Fiscal calendar (Fiscal Year / Period / Year Period) | EXACT via `KRW_NA_FF_FISCALPERIOD` | ✅ same in prod (3 role-copies) | CONFIRMED EXACT |
| Territory | STRONG via `KRW_NA_FF_TERRITORY` | ❌ absent from prod — prod uses `Territory_Name` columns native on VBRP / VBAP | DOWNGRADE — territory dataflow is AWIP-extra, use fact-table native `Territory_Name` for parity with prod |
| Zip → territory bridge | STRONG via `KRW_NA_FF_ZIPCODES` | ❌ absent from prod | Same — AWIP-extra |
| Forecast values — order-intake side | STRONG via `KRW_NA_FF_FORECAST_INTAKE` | ✅ same in prod (SORDERS cube) | CONFIRMED STRONG |
| Forecast values — invoice side | STRONG via `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` (native string column) | ⚠ Prod uses `KRW-NA_FF_FORECAST` dataflow, not Billing column | DOWNGRADE — AWIP's current approach diverges from prod. Import the dataflow to match. |
| Application | EXACT via `Billing[Application]` / `SalesOrders[Application_Product_Number]` | (prod uses AAS-cube exposed columns — behavior matches) | CONFIRMED EXACT |
| Industry / Secondary Grouping / Sales Rep Name / Project Coordinator / Customer Full Name / Product Family | EXACT / STRONG via native fact-table columns | (prod exposes via AAS cube) | CONFIRMED |
| Gross Margin / Cost of Sales | EXACT via native columns | (prod exposes via AAS cube) | CONFIRMED |

## 4. Relationships needed if `KRW-NA_FF_FORECAST` is added to AWIP

Following the production pattern:

| From | To | Cardinality | Cross-filter | Purpose |
|---|---|---|---|---|
| `KRW-NA_FF_FORECAST[Fiscal Year Period]` | `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | many:one | single | Enable fiscal-period slicing of forecast |
| (later, if slicer needed) | Disconnected `FiscalYearPeriods Slicer` bi-di ↔ `KRW-NA_FF_FORECAST` on Fiscal Year Period 2 | one:many | bothDirections | Matches production's disconnected-slicer pattern |

Optional (probably not needed): direct `Billing → KRW-NA_FF_FORECAST` relationship. Production doesn't have this either — the FORECAST table is filtered via the fiscal-period slicer, not via a fact-table join.

## 5. Gaps for Phase 9 (semantic model repair) related to dataflows

1. **Add `KRW-NA_FF_FORECAST` (hyphen) dataflow** — needs the Kingspan dataflow ID; ask Ana / James or check Power BI Service workspace.
2. **Verify** dataflow IDs on AWIP's existing `KRW_NA_FF_FISCALPERIOD`, `KRW_NA_FF_FORECAST_INTAKE`, `KRW_NA_FF_ZIPCODES`, `'CAPEX Approved'` (I noted "not captured" above — should be extracted from the AWIP TMDL for the record).
3. **Hide the 8 out-of-scope dataflow tables** from the field picker (`isHidden: true`) so users building visuals don't accidentally reference them.
4. **Decide** on the disconnected slicer pattern: implement in AWIP (matching prod) or use `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` directly as a slicer field (simpler).

**Written:** 2026-08-13

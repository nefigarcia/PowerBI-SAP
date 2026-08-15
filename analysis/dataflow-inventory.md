# Power BI Dataflow Inventory — AWIP_Commercial_Sales

**Scope:** Inventory of the 13 Dataflow tables added to `AWIP_Commercial_Sales.SemanticModel` in addition to the SAP Datasphere `Billing` and `SalesOrders` fact tables.

**Workspace ID (all tables):** `24b96353-204c-4526-b94b-2128574aa2f0`
**Connector:** `PowerPlatform.Dataflows`
**Read for this inventory:** 13 of 13 Dataflow TMDL files (all)
**Source of truth:** `AWIP_Commercial_Sales.PBIP\AWIP_Commercial_Sales.SemanticModel\definition\tables\*.tmdl` at commit `40205b3`.

> ⚠ Table names are **preserved as-is** per user directive — no renaming has been applied.

---

## 1. Table catalog

| # | Table (as loaded) | Dataflow ID | Purpose (from column analysis) | Row-grain guess | Columns |
|---|---|---|---|---|---|
| 1 | `KRW_NA_FF_CALENDAR`               | `ba1d8f9b-3b34-4e61-907e-7ca9db97b302` | Daily calendar with `Date`, `Year`, `Month`, `Month Name`, `Day of Week`, `Start/End of Month`, `Year Month`, `Current Month`, `Month Type`, `Calendar Date` (string key) | 1 row per date | 12 |
| 2 | `KRW_NA_FF_FISCALPERIOD`           | (dataflow id not printed above) | Maps calendar dates to fiscal calendar. Cols: `Calendar Date`, `Fiscal Year`, `Fiscal Period`, `Fiscal Year Period` | 1 row per date | 4 |
| 3 | `KRW_NA_FF_TERRITORY`              | `bd3aacdc-369c-486d-b9bc-a3837dc9cda1` | Zip → territory hierarchy. Cols: `Zip Code ID`, `Zip Code Name`, `Territory Name` | 1 row per zip | 3 |
| 4 | `KRW_NA_FF_ZIPCODES`               | (dataflow id not printed above) | Zip → territory bridge. Cols: `Zip Code ID` (int64), `Zip Code Name`, `Territory ID` | 1 row per zip | 3 |
| 5 | `KRW_NA_FF_GEOINFO`                | `447d5626-27df-44c5-bc5e-b56916bdb28c` | Country/state geography incl. coordinates. Cols: `Country`, `Code`, `State`, `Latitude` (double), `Longitude` (double), `COUNTRY_REGION` | 1 row per state | 6 |
| 6 | `KRW_NA_FF_FORECAST_INTAKE`        | (dataflow id not printed above) | **Pre-classified forecast values.** Cols: `Period`, `Year`, `Sales $` (double), `Sales Membrane sqft` (double), `Sales ISO sqft` (double), `Sales ISO bdft` (double), `Fiscal Year Period`, `Fiscal Year Period Sorted` | 1 row per fiscal period | 8 |
| 7 | `KRW_NA_FF_PLSTRUCTURE`            | `bd64cee7-1d35-46fb-97c7-5c3e15128af9` | Tagetik P&L structure (Group Sort, Group Description, Line Number, Tagetik Account code + Description, GL Account, `Text for B/S P&L Item`). **Not** product/application classification. | 1 row per Tagetik line | 7 |
| 8 | `KRW_NA_FF_COSTCENTREHIER`         | `d28982b1-b94f-43cd-b719-bbaa14b77ba1` | Cost centre hierarchy (Group + Group Description + Centre + Centre Description) | 1 row per cost centre | 4 |
| 9 | `KRW_NA_FF_COSTCTHIER_ONDULINE`    | `eb55fefb-ef02-45d0-bd04-a6acf7d801a0` | **Same schema** as `COSTCENTREHIER` but scoped to Onduline subset | 1 row per cost centre | 4 |
| 10 | `KRW_NA_FF_COSTELEM_OH1`          | `e5c6d724-cdf3-4ed9-9d6b-93a946f4b312` | Cost element leaf list (Sort, Group Key, Group Text, Element Key, Element Text, CostElem Group Sort) | 1 row per cost element | 6 |
| 11 | `KRW_NA_FF_COSTELEMHIER`          | `a5cced2b-1fe6-48a6-937e-b8d2ec91ad34` | Cost element hierarchy (Group Key, Group Text, Group Sorting, CostElement, Description, Exclude) | 1 row per cost element | 6 |
| 12 | `KRW_NA_FF_HISTSB1`                | `84b23137-ac92-40f8-a3f8-0df06d8f2399` | Historical SB1 postings — invoice lines against CAPEX orders. Cols: `Internal CAPEX ID`, Project, Location, Order, Period, Fiscal Year, Invoice, Invoice Date, Posting Date, Description, Amount DC (double), Curr, Amount LC (double), Vendor, Purchase Order, Item | 1 row per invoice/item | 16 |
| 13 | `'CAPEX Approved'`                | (dataflow id not printed above) | CAPEX approvals. Cols: Order, `Internal CAPEX ID`, Location, Project, Currency, `CAPEX Approved` (double), ORD_CAPID | 1 row per CAPEX order | 7 |

**Total: 13 Dataflow tables, ~86 columns.**

---

## 2. Table clusters (by business domain)

### 2.1 Calendar / fiscal (2 tables)
`KRW_NA_FF_CALENDAR` + `KRW_NA_FF_FISCALPERIOD`
- Auto-detected relationship exists: `KRW_NA_FF_FISCALPERIOD[Calendar Date]` → `KRW_NA_FF_CALENDAR[Calendar Date]` (one:many, bothDirections).
- Neither is currently related to `DimDate` (the existing production-mirror date table) or to the fact tables. **Action required** in repair phase.

### 2.2 Geography / territory (3 tables)
`KRW_NA_FF_TERRITORY` + `KRW_NA_FF_ZIPCODES` + `KRW_NA_FF_GEOINFO`
- Auto-detected: `Billing[State_Name]` → `KRW_NA_FF_GEOINFO[State]` and `SalesOrders[State_Name]` → `KRW_NA_FF_GEOINFO[State]` (both single-direction).
- No relationship yet from Billing/SalesOrders to Territory/Zipcodes. Bridge candidate: Billing/SalesOrders `PostalCode*` columns → `KRW_NA_FF_ZIPCODES[Zip Code Name]` (verify value domain first).

### 2.3 Forecast (1 table)
`KRW_NA_FF_FORECAST_INTAKE` — **standalone**; no relationships yet auto-detected.
- Grain (`Fiscal Year Period`) does not match `DimDate` grain. Relationship candidate: to `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`.
- **Critical**: this is the true source of the forecast figures that Billing's `Sum Fcst Sales in FT2 for Membranes` measure was trying to compute. Kingspan replaced the row-level product-family filter approach with a pre-aggregated dataflow.

### 2.4 CAPEX (2 tables)
`'CAPEX Approved'` + `KRW_NA_FF_HISTSB1`
- Auto-detected: `KRW_NA_FF_HISTSB1[Internal CAPEX ID]` → `'CAPEX Approved'[Internal CAPEX ID]`.
- This is a separate reporting domain (CAPEX vs. Commercial Sales). Not required for the AWIP Commercial Sales pages we are rebuilding. Likely added to the model in error or shared for a different report scope.

### 2.5 Cost accounting (4 tables)
`KRW_NA_FF_COSTCENTREHIER` + `KRW_NA_FF_COSTCTHIER_ONDULINE` + `KRW_NA_FF_COSTELEM_OH1` + `KRW_NA_FF_COSTELEMHIER`
- Auto-detected: `KRW_NA_FF_COSTELEM_OH1[Cost Element Key]` → `KRW_NA_FF_COSTELEMHIER[CostElement]` (one:many, bothDirections).
- No relationship yet to Billing (`Billing[CostCenter]` exists — candidate for a relationship to `KRW_NA_FF_COSTCENTREHIER[Cost Centre]`).
- Overlap between `COSTCENTREHIER` and `COSTCTHIER_ONDULINE` (identical schema). Need business rule for which one to use as the primary — Onduline appears to be a subset for a specific brand/BU.

### 2.6 P&L structure (1 table)
`KRW_NA_FF_PLSTRUCTURE`
- Standalone. Bridges via `GL Account` — but no `GL Account` column exists on Billing or SalesOrders in the current TMDL. Not linkable to the commercial-sales fact tables directly.

---

## 3. Auto-detected relationships already present

Extracted verbatim from `relationships.tmdl`:

| Relationship GUID | From | To | Cardinality | Filter |
|---|---|---|---|---|
| `AutoDetected_5fec0261` | `KRW_NA_FF_FISCALPERIOD[Calendar Date]` | `KRW_NA_FF_CALENDAR[Calendar Date]` | one:many | both directions |
| `AutoDetected_db66fffc` | `KRW_NA_FF_HISTSB1[Internal CAPEX ID]` | `'CAPEX Approved'[Internal CAPEX ID]` | many:one | single |
| `AutoDetected_b57492e0` | `Billing[State_Name]` | `KRW_NA_FF_GEOINFO[State]` | many:one | single |
| `AutoDetected_da5932da` | `SalesOrders[State_Name]` | `KRW_NA_FF_GEOINFO[State]` | many:one | single |
| `AutoDetected_91ebea43` | `KRW_NA_FF_COSTELEM_OH1[Cost Element Key]` | `KRW_NA_FF_COSTELEMHIER[CostElement]` | one:many | both directions |

**Existing production-mirror relationships preserved:**
- `Billing[BillingDocumentDate_D5]` → `DimDate[Date]`
- `SalesOrders[CreationDate_D8]` → `DimDate[Date]`

---

## 4. Relationships not yet created but implied by data

Candidates that we may need in the semantic-model repair (verify value-domain match first):

| From | To | Confidence | Notes |
|---|---|---|---|
| `Billing[Fiscal_Month]` or `Billing[FiscalYearPeriod]` | `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | POSSIBLE | Format compatibility unverified — Billing has both `Fiscal_Month` and `FiscalYearPeriod`; need distinct-values comparison |
| `SalesOrders[Fiscal_Month]` or `SalesOrders[FiscalPeriod]` | `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | POSSIBLE | Same |
| `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period]` | `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | STRONG | Same domain (fiscal-year-period), same source ownership |
| `Billing[PostalCode]` or `PostalCode1..3` | `KRW_NA_FF_ZIPCODES[Zip Code Name]` | POSSIBLE | Zip format compatibility unverified; Billing has 4 zip variants (sold-to, ship-to, bill-to, payer) |
| `Billing[Territory_Name]` | `KRW_NA_FF_TERRITORY[Territory Name]` | STRONG | Territory names already present on Billing; question is whether text values match exactly. Similar for SalesOrders and its 4 territory variants (`Billto_Territory`, `Payer_Territory`, `Shipto_Territory`, `Territory_Name`). |
| `Billing[CostCenter]` | `KRW_NA_FF_COSTCENTREHIER[Cost Centre]` | POSSIBLE | Value-domain unverified. Also unclear whether `_ONDULINE` variant should be used for a subset of rows. |
| `KRW_NA_FF_CALENDAR[Date]` | `DimDate[Date]` | POSSIBLE | Would double-model the calendar; alternative is to drop `KRW_NA_FF_CALENDAR` entirely and rely on `DimDate`. |

---

## 5. Provenance / source-of-truth notes

- **Table names use SAP naming (`KRW_NA_FF_*`) rather than business-friendly names.** Deferred rename per user directive.
- All 13 tables use the same workspace ID — they are 13 separate dataflows under one Kingspan workspace.
- No custom M transformations are applied downstream in Power BI — every partition is a straight `Navigation 4` step onto the dataflow entity.
- No incremental refresh / RangeStart-RangeEnd parameters on any of the 13 dataflow imports.

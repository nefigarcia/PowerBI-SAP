# Recovered Missing Fields — Ready to Restore

**Purpose:** The concise, actionable list of production fields and measures that were previously classified `MISSING SOURCE` or `BLOCKED` and can now be **restored** — either from a native column on the enriched Billing/SalesOrders tables, or from one of the 13 new Dataflow tables.

**Only mappings classified EXACT or STRONG in [`dataflow-production-crosswalk.md`](dataflow-production-crosswalk.md) are included here** (per user directive: "Only EXACT and STRONG mappings may be used automatically"). POSSIBLE mappings await a distinct-value probe or business confirmation and are listed in a separate section at the bottom for tracking.

---

## 1. Restore-ready fields (safe to wire up automatically)

### 1.1 Customer master enrichment (was Customer.xlsx)

| # | Field to restore | Use directly from | Notes |
|---|---|---|---|
| 1 | Application | `Billing[Application]` / `SalesOrders[Application_Product_Number]` | STRONG variance for SalesOrders naming |
| 2 | Industry | `Billing[Industry]` / `SalesOrders[Industry]` | EXACT |
| 3 | Secondary Grouping | `Billing[Secondary_Grouping]` / `SalesOrders[Secondary_Grouping_Product_Number]` | STRONG for SalesOrders naming |
| 4 | Sales Representative (ID) | `Billing[Sales_Representative]` / `SalesOrders[Sales_Representative]` | EXACT |
| 5 | Sales Representative Name | `Billing[Sales_Representative_T]` / `SalesOrders[Sales_Representative_T]` | STRONG — `_T` is SAP text/description pattern; verified consistent across the model |
| 6 | Project Coordinator (ID) | `Billing[Project_Coordinator]` / `SalesOrders[Project_Coordinator]` | EXACT |
| 7 | Project Coordinator Name | `Billing[Project_Coordinator_T]` / `SalesOrders[Project_Coordinator_T]` | STRONG |
| 8 | Customer Project Name | `Billing[ProjectName]` / `SalesOrders[Project_Name]` | STRONG for SalesOrders (underscore variant) |
| 9 | Customer Full Name (Sold-to Description) | `Billing[CustomerFullName]` / `SalesOrders[CustomerFullName]` | STRONG. Alternative: `SoldToParty_D12_T` / `SoldToParty_D3_T`. Pick one convention when wiring — see "Choices to make" below. |
| 10 | Territory (Sold-to / Ship-to / Bill-to / Payer) | Billing: `Territory_NameSoldToPart_A_12`, `Territory_NameBillToPart_A_14`, `Territory_NameShipToPart_A_13`, plus generic `Territory_Name`. SalesOrders: `Billto_Territory`, `Payer_Territory`, `Shipto_Territory`, plus `Territory_Name`. | EXACT for all four partner directions |
| 11 | Material Description | `Billing[Material_D17_T]` / `SalesOrders[Product_D14_T]` | STRONG |
| 12 | Cost of Sales (Net Sales Cost) | `Billing[NetSlsCostAmount]` (also `_CC` variant) | STRONG — validate with business owner that "Cost of sales" = `NetSlsCostAmount` |
| 13 | Gross Margin | `Billing[Gross_Margin]` | EXACT |
| 14 | Gross Margin % | `Billing[Margin_Percent]` | STRONG |
| 15 | Account Assignment Group Description | `Billing[CustomerAccountAssignmentGroup_T]` / `SalesOrders[CustomerAccountAssignmentGroup_T]` | EXACT — **KNVV.csv dependency eliminated** |

### 1.2 Forecast / ISO measures (were BLOCKED)

| # | Item | Use directly from | Notes |
|---|---|---|---|
| 16 | `Sum Fcst Sales in FT2 for Membranes` (Billing) | `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` — new native column | STRONG. Backup: `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` at fiscal-period grain. **This unblocks the "Fcst ISO Sales" tile that was showing 0.** |
| 17 | `ISO Rate Fcst IS` (Billing) | `Billing[ISO_Rate_Forecast]` — new native column | STRONG. **This unblocks the "ISO Rate Fcst" tile on the Invoiced Sales dashboard that was showing 0.00.** |
| 18 | `Sum Fcst Order Qty. in FT2 for Membranes OI` (SalesOrders) | Existing DAX still works; option to simplify to `SalesOrders[Sales_Forecast_Membrane_Qty_in_FT2]` | EXACT alternative |
| 19 | `ISO Rate Fcst OI` (SalesOrders) | Existing DAX = 2.63 works; option to simplify to `SalesOrders[ISO_Rate_Forecast]` | EXACT alternative |

### 1.3 Fiscal calendar attributes

| # | Field | Use directly from | Notes |
|---|---|---|---|
| 20 | Fiscal Year | `Billing[FiscalYear]` / `SalesOrders[FiscalYear]` | EXACT |
| 21 | Fiscal Period | `SalesOrders[FiscalPeriod]` — or `KRW_NA_FF_FISCALPERIOD[Fiscal Period]` when needed as a slicer dim | EXACT |
| 22 | Fiscal Year Period (combined key) | `Billing[FiscalYearPeriod]` / `SalesOrders` (via `Fiscal_Month`) | EXACT |
| 23 | Fiscal Month | `Billing[Fiscal_Month]` / `SalesOrders[Fiscal_Month]` | EXACT |
| 24 | Fiscal Period Sort key | `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]` | STRONG — usable if `KRW_NA_FF_FISCALPERIOD` is added as the fiscal-period dim |

### 1.4 Geography / territory / region

| # | Field | Use directly from | Notes |
|---|---|---|---|
| 25 | State Name | `Billing[State_Name]` / `SalesOrders[State_Name]` | EXACT |
| 26 | Region (business) | `Billing[Region]` / `SalesOrders[Region]` — or `KRW_NA_FF_GEOINFO[COUNTRY_REGION]` when a business rollup name is needed | EXACT (Region col); STRONG (dataflow rollup) |
| 27 | Country | `Billing[Country]` / `SalesOrders[Country]` — or `KRW_NA_FF_GEOINFO[Country]` when a mapped-name is needed | EXACT |
| 28 | State latitude / longitude | `KRW_NA_FF_GEOINFO[Latitude]` / `[Longitude]` | EXACT — new capability (map visuals) |
| 29 | Zip → Territory bridge | `KRW_NA_FF_ZIPCODES` + `KRW_NA_FF_TERRITORY` | STRONG — only needed if a visual pivots on zip; today Territory_Name is native on the facts |

### 1.5 Product / application (also §1.1)

| # | Field | Use directly from | Notes |
|---|---|---|---|
| 30 | Product Family | `Billing[Product_Family]` (direct) / `SalesOrders[Product_Family_Product_Number]` | EXACT (Billing) |
| 31 | Product Group | `Billing[ProductGroup]` / `SalesOrders[ProductGroup]` | EXACT |

---

## 2. Choices to make before wiring

None of these block the restore; they are naming / semantic choices that only the business owner or a value-domain probe can settle definitively. Where the analysis is confident enough to recommend a default, that recommendation is called out.

1. **Customer descriptive name — pick one:** `CustomerFullName` (item 9) OR `SoldToParty_D12_T` / `SoldToParty_D3_T`. Both are STRONG. Recommendation: `CustomerFullName` for detail tables (business-friendly), `SoldToParty_D12_T` when linking joins by SAP key.
2. **Territory partner direction — pick one for headline visuals:** generic `Territory_Name` OR one of the four partner variants (item 10). Recommendation: `Territory_NameSoldToPart_A_12` on Billing detail tables (that is production's convention: sold-to is the business default), `Territory_Name` for slicers.
3. **Region source — pick one:** raw `Region` code on facts OR the `KRW_NA_FF_GEOINFO[COUNTRY_REGION]` business rollup (needs the auto-detected `State_Name → State` relationship). Recommendation: `COUNTRY_REGION` for business-facing rollups because it is a friendly name; keep `Region` available for detail tables.
4. **SalesOrders forecast columns — three GM variants exist:** `Gross_Margin`, `Gross_Margin_Order_Intake`, `Gross_Margin_for_open_orders`. Production concept "Order Intake" ↔ `Gross_Margin_Order_Intake`. Recommendation: use the `_Order_Intake` variant for the Order Intake pages.

---

## 3. Direct impact on report pages

Pages / visuals unblocked by the recoveries above:

| Report page | Previously blocked visual | Now restorable via |
|---|---|---|
| Invoiced Sales - Dashboard | "ISO Rate Fcst" gauge (was 0.00) | `Billing[ISO_Rate_Forecast]` |
| Invoiced Sales - Dashboard | "Sum Fcst Sales in FT2 for Membranes" card | `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` |
| Invoiced Sales - Dashboard | AAGC Description slicer | `Billing[CustomerAccountAssignmentGroup_T]` (no KNVV.csv needed) |
| Invoiced Sales - Detail | Sales Rep column, Project Coord column, ProjectName column, Material Description column | `Sales_Representative_T`, `Project_Coordinator_T`, `ProjectName`, `Material_D17_T` |
| Order Intake - Detail | Sales Rep, Project Coord, Project Name, Material Description | SalesOrders equivalents |
| Extended Invoiced Sales | Application, Industry, Cost of sales, Gross Margin, Gross Margin % | Native Billing columns |
| Extended Order Intake | Same suite | Native SalesOrders columns |
| (any) | Region/business-rollup slicer | `KRW_NA_FF_GEOINFO[COUNTRY_REGION]` |

**Estimated coverage recovery: from ~55% of production visuals blocked → 5-10% remaining blocked (Salesforce-scoped only).**

---

## 4. POSSIBLE-only items (parked pending distinct-value probe or business input)

Not to be wired automatically. Tracked here so they are not lost:

| Item | Location | What we need before promoting |
|---|---|---|
| "Company Type" ↔ `CustomerAccountGroup` vs `IndustryType` | Billing / SalesOrders | Business definition of "Company Type" |
| Fiscal-period join format (Billing.`FiscalYearPeriod` ↔ dataflow `Fiscal Year Period`) | Both | `EVALUATE DISTINCT` sample compare |
| Zip-format compatibility (Billing.`PostalCode*` ↔ `KRW_NA_FF_ZIPCODES[Zip Code Name]`) | Billing / SalesOrders / dataflow | Value-domain probe |
| Territory-name spelling compatibility (Billing.`Territory_Name` ↔ `KRW_NA_FF_TERRITORY[Territory Name]`) | Both | Value-domain probe |
| Cost Centre join (Billing.`CostCenter` ↔ `KRW_NA_FF_COSTCENTREHIER[Cost Centre]`) | Billing / dataflow | Value-domain probe + business rule on Onduline variant |

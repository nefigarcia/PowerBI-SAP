# Phase 5 — Semantic Model Rebuild (SAP-only scope)

**Date:** 2026-08-09
**Scope authorization:** User approved *"proceed on just SAP measures"*. Customer.xlsx / KNVV.csv / Salesforce dependencies deferred.

## Files modified

| File | Change |
|---|---|
| [AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/Billing.tmdl](../AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/Billing.tmdl) | Inserted **8 production measures** at top of table |
| [AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/SalesOrders.tmdl](../AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/SalesOrders.tmdl) | Inserted **11 production measures** at top of table |

## Files NOT modified

- `production-reference/` — READ ONLY (per Phase 10 safety)
- `Billing.pbix`, `Sales.pbix` — untouched
- `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/_Measures.tmdl` — our existing custom measures (Sales, Order Intake, Sales YoY %, Avg Sales Price, etc.) kept as-is. Left in place so existing report visuals continue to work while production measures are validated.
- All existing columns, relationships, DimDate calculated table — untouched
- Report layer (`AWIP_Commercial_Sales.Report/`) — untouched (Phase 7 work)

## Measures added

All 19 measures placed under `displayFolder: "Production Measures"` for clean separation from our custom `_Measures.*` set. All DAX is verbatim from production except for two mechanical column-reference rewrites (documented per-measure below).

### Billing table (8 measures)

| # | Name | Depends on | Adaptations vs production |
|---|---|---|---|
| 1 | Sum Billing Qty. in FT2 for Membranes | `FC_Product_Group`, `Billing_Quantity_in_FT2` | Table `SAP_SD_HL_BillingDocumentItem_V2` → `Billing`; `[FC Product Group]` → `[FC_Product_Group]` |
| 2 | Sum Billing Qty. in BFT2 for ISO 2 | `FC_Product_Group`, `Billing_Quantity_with_Signs` | Same 2 adaptations |
| 3 | Sum Billing Qty. in BFT2 for ISO | `FC_Product_Group`, `Billing_Quantity_in__BFT2` | Same 2 adaptations |
| 4 | Sum Fcst Sales in FT2 for Membranes | `FC_Product_Group`, `ForecastSalesSQFT` | Same 2 adaptations |
| 5 | Sum Revenue in DC with sign IS | `Revenue` | Table adaptation only |
| 6 | ISO AOP - $/bdft IS | `Revenue`, `Billing_Quantity_with_Signs` | Table adaptation only |
| 7 | ISO Rate IS | ↑ measures #1, #3 | none (only refs measures) |
| 8 | ISO Rate Fcst IS | `ForecastSalesBDFT`, ↑ measure #4 | Table adaptation only |

### SalesOrders table (11 measures)

| # | Name | Depends on | Adaptations vs production |
|---|---|---|---|
| 1 | ISO AOP - $/bdft OI | `Revenue_Order_Intake`, `Order_Quantity_in_BFT2` | Table `SAP_SD_HL_SalesDocumentItem_V2` → `SalesOrders` |
| 2 | Sum Fcst Order Qty. in FT2 for Membranes OI | `FC_Product_Group`, `ForecastSalesSQFT` | Table + `[FC Product Group]` → `[FC_Product_Group]` |
| 3 | Sum Order Qty. in BFT2 for ISO OI | `Product_Family_Product_Number`, `Requested_Quantity_in_BFT` | Table + `[Product Family]` → `[Product_Family_Product_Number]` ⚠ |
| 4 | Sum Order Qty. in BFT2 for ISO SB | `FC_Product_Group`, `Requested_Quantity_in_BFT` | Table + `[FC Product Group]` → `[FC_Product_Group]` |
| 5 | Sum Order Qty. in FT2 for Membranes OI | `Product_Family_Product_Number`, `Order_Quantity_in_FT2` | Table + `[Product Family]` → `[Product_Family_Product_Number]` ⚠ |
| 6 | Sum Order Qty. in FT2 for Membranes SB | `FC_Product_Group`, `RequestedQuantityInBaseUnit` | Table + `[FC Product Group]` → `[FC_Product_Group]` |
| 7 | Sum Order Qty. in FT2 for Membranes SB 2 | `FC_Product_Group`, `Open_Order_Quantity_in_FT2` | Table + `[FC Product Group]` → `[FC_Product_Group]` |
| 8 | ISO Rate OI | ↑ measures #3, #5 | none |
| 9 | ISO Rate SB | ↑ measures #4, #6 | none |
| 10 | ISO Rate Fcst OI | `ForecastSalesBDFT`, ↑ measure #2 | Table adaptation only |
| 11 | Total Backlog $ | `Revenue_Backlog` | Table adaptation only |

⚠ = uses `Product_Family_Product_Number` which is the RL variant of production `Product Family`. **Domain values (Membrane, iso) must be confirmed identical in Phase 8** — if the RL variant contains different values, these measures will return zero.

## Preserved from production

- Every VAR / RETURN / IF-BLANK guard byte-for-byte identical
- Every `formatString` identical
- Every `PBI_FormatHint` annotation identical
- Function calls preserved: `SUMX`, `FILTER`, `CONTAINSSTRING`, `SUM`, `DIVIDE`, `CALCULATE`, `IF`, `BLANK`
- Case of filter string arguments preserved: `"TPO"`, `"iso"`, `"ISO"`, `"Membrane"` (production has mixed casing — CONTAINSSTRING is case-insensitive, but we match production exactly)

## NOT reproduced (Customer.xlsx / KNVV / Salesforce scope — deferred)

Per the "SAP only" scope authorization, these are not built:

- Any measure that would depend on `Customer.xlsx` columns (Cost of sales, Gross Margin, Gross margin %, Application-business, Industry, Region-business, Sales Representative Name, Project Coordinator, Material Description, Customer Project Name, Sold to party Description, Territory columns)
- Any dimensional slicer sourced from `KNVV.csv` (AAGC Description)
- Any Salesforce Quote / Quote Line Item / User measures
- The relationships `SAP_SD_HL_BillingDocumentItem_V2 → KNVV` and `Customer → SAP_SD_HL_BillingDocumentItem_V2` (both blocked by missing external sources)

These remain as open questions for Ana / James per [missing-data-sources.md](missing-data-sources.md).

## Phase 8 validation plan

Before considering these measures production-quality, execute the following:

### Step 1 — Domain-value verification (BLOCKS Phase 7 report build)

Run in Power BI Desktop → **DAX Query view** or **Modeling → New table**:

```dax
// Verify FC_Product_Group values
EVALUATE DISTINCT(SELECTCOLUMNS(Billing, "FC_Product_Group", Billing[FC_Product_Group]))

// Verify Product_Family_Product_Number values
EVALUATE DISTINCT(SELECTCOLUMNS(SalesOrders, "Product_Family_Product_Number", SalesOrders[Product_Family_Product_Number]))

// Verify Sales FC_Product_Group values
EVALUATE DISTINCT(SELECTCOLUMNS(SalesOrders, "FC_Product_Group", SalesOrders[FC_Product_Group]))
```

Expected — must include:
- `Billing.FC_Product_Group` must include values containing `"TPO"` (case-insensitive) AND `"iso"` (case-insensitive)
- `SalesOrders.FC_Product_Group` must include values containing `"TPO"` (case-insensitive) AND `"ISO"` (case-insensitive)
- `SalesOrders.Product_Family_Product_Number` must include values containing `"iso"` (case-insensitive) AND `"Membrane"` (case-insensitive)

If any check fails, the corresponding measures will return `0`. In that case we need to find the correct column and rewrite the affected measures.

### Step 2 — Cross-value reconciliation (once model refreshes cleanly)

For each of the 19 measures, capture value under identical filter contexts against production and new:

| Filter context | Priority |
|---|---|
| Unfiltered (grand total) | HIGH |
| `FiscalYearPeriod = "2026007"` (production default slicer) | HIGH |
| `FC_Product_Group = "TPO"` | MEDIUM |
| `FC_Product_Group = "ISO"` | MEDIUM |
| One specific `SalesDocument` (drill-down) | LOW |

Log results in [validation-results.md](validation-results.md).

Expected tolerances (per that file):
- Monetary / quantity totals: exact match
- Ratios (ISO Rate, AOP): ±0.01% (floating-point)

### Step 3 — If matches ≠ production, diagnose

Most likely causes if numbers diverge:
1. **RL view has different row-level filtering** than HL (e.g. RL excludes cancelled invoices, HL includes them)
2. **`Product_Family_Product_Number` value domain ≠ `Product Family`** (needs different column)
3. **RL and HL use different sign conventions** on `_with_Signs` columns
4. **Datasphere parameter defaults** (CompanyCode_D1, SalesOrganization_D16) filter more/less data than production ODBC view

## What to do next

1. **Reopen** `AWIP_Commercial_Sales.pbip` in Power BI Desktop (close first if it's still open).
2. **Refresh** the model to load the new measures (they're metadata — should compile immediately, no data pull needed).
3. Check the **Data pane** → `Billing` table → `Production Measures` folder → verify all 8 measures show up. Same for `SalesOrders` → 11 measures.
4. In DAX Query view, run the 3 domain-value queries above. Report back which values appear.
5. Once we know the domains are correct, we can:
   - Add these measures to KPI cards on Page 1 to see live values (replaces or supplements existing cards), OR
   - Start Phase 7 rebuild of the production `Invoiced Sales - Dashboard` page.

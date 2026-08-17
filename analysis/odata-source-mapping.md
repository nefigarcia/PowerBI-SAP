# OData Source Mapping (field-level crosswalk)

**Rule:** only use SAP Datasphere OData Billing, OData SalesOrders, and non-`_SAP_` Power BI Dataflows as new-project sources. Ignore the deprecated ODBC reference. Ignore `_SAP_` dataflows.

**Sources of truth:**
- Production field references: extracted from OData semantic model DAX + report visual bindings
- AWIP available fields: `Billing.tmdl` (471 cols), `SalesOrders.tmdl` (432 cols), non-`_SAP_` dataflow TMDLs

**Confidence:** EXACT / STRONG / POSSIBLE / NOT FOUND (per prior convention).

---

## 1. Production fields most heavily used in visuals — mapping to AWIP source

### 1a. Fact / measure-inputs

| Production field | Production table | AWIP source | Confidence | Notes |
|---|---|---|---|---|
| Revenue ($) | `KRW_NA_SAP_VBRP[Revenue]` | `Billing[Revenue]` | EXACT | Same SAP column exposed via Datasphere |
| Sales Volume Net Amount (CC) | (AAS cube exposes as `Revenue` variant) | `Billing[SlsVolNetAmt_CC]` | STRONG | Used as `Sales` measure basis in AWIP |
| Sales Volume Quantity | (AAS cube) | `Billing[SalesVolumeQuantity]` | STRONG | |
| Billing Quantity (FT2 for Membranes) | AAS-cube measure sums this | `Billing[Billing_quantity_in_FT2_for_Membrane]` (⚠ string — needs VALUE) | STRONG | See string-type memory |
| Billing Quantity (BFT2 for ISO) | AAS-cube measure | `Billing[Billing_quantity_in_BFT2_For_ISO]` (⚠ string) | STRONG | |
| Forecast Sales (SQFT) — invoice side | `KRW-NA_FF_FORECAST[Sales Membrane sqft]` (fiscal-period grain) | AWIP options: (a) `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` (row-level, string), or (b) **add `KRW-NA_FF_FORECAST` dataflow** and use it directly | STRONG (option b) / POSSIBLE (option a) | Option b matches prod grain and formula; option a diverges. Choose option b in Phase 9. |
| Forecast Sales (BDFT) — invoice side | `KRW-NA_FF_FORECAST[Sales ISO bdft]` | AWIP options: same as above | STRONG (option b) | |
| Forecast Sales ($) — invoice side | `KRW-NA_FF_FORECAST[Sales $]` | (needed after dataflow import) | STRONG (option b) | |
| Forecast Sales Membrane sqft — order-intake side | `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` | `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` (already in AWIP) | EXACT | Use directly |
| Forecast Sales ISO bdft — order-intake side | `KRW_NA_FF_FORECAST_INTAKE[Sales ISO bdft]` | same | EXACT | |
| Order Intake Net Amount | AAS `IncSalesOrdNetAmnt` | `SalesOrders[IncSalesOrdNetAmnt_CC]` | EXACT | Same |
| Order Intake Quantity | AAS `IncSalesOrderQty` | `SalesOrders[IncSalesOrderQty]` | EXACT | |
| Revenue Order Intake ($) | AAS-cube measure | `SalesOrders[Revenue_Order_Intake]` | EXACT | |
| Revenue Backlog ($) | AAS BACKLOG measure | `SalesOrders[Revenue_Backlog]` | EXACT | |
| Order Quantity BFT2 / FT2 / M2 | AAS-cube measures | `SalesOrders[Order_Quantity_in_BFT2]` / `[Order_Quantity_in_FT2]` / `[Order_Quantity_in_M2]` | EXACT | |
| Open Order Quantity BFT2 / FT2 / etc. | AAS BACKLOG measures | `SalesOrders[Open_Order_Quantity_in_BFT2]` / `[Open_Order_Quantity_in_FT2]` / … | EXACT | |
| Gross Margin (open orders) | AAS BACKLOG measure | `SalesOrders[Gross_Margin_for_open_orders]` | EXACT | |
| Gross Margin (order intake) | AAS SORDERS measure | `SalesOrders[Gross_Margin_Order_Intake]` | EXACT | |
| Gross Margin (invoice) | AAS INVOICED measure | `Billing[Gross_Margin]` | EXACT | |
| Gross Margin % (invoice) | AAS INVOICED measure | `Billing[Margin_Percent]` | STRONG | |
| Cost of Sales | AAS INVOICED measure | `Billing[NetSlsCostAmount]` (or `_CC` variant) | STRONG | Business confirmation recommended |

### 1b. Dimension / attribute fields (used for slicers, categories, table columns)

| Production field | Production table | AWIP source | Confidence |
|---|---|---|---|
| Product Family | `KRW_NA_SAP_VBRP[Product Family]` / `KRW_NA_SAP_VBAP OI[Product Family]` | `Billing[Product_Family]` / `SalesOrders[Product_Family_Product_Number]` | EXACT (Billing) / STRONG (SalesOrders naming) |
| Product Group | (AAS-exposed) | `Billing[ProductGroup]` / `SalesOrders[ProductGroup]` | EXACT |
| Material Description | AAS-exposed via MARM/TVM3T | `Billing[Material_D17_T]` / `SalesOrders[Product_D14_T]` | STRONG |
| Application | AAS-exposed | `Billing[Application]` / `SalesOrders[Application_Product_Number]` | EXACT |
| Industry | AAS-exposed | `Billing[Industry]` / `SalesOrders[Industry]` | EXACT |
| Secondary Grouping | AAS-exposed | `Billing[Secondary_Grouping]` / `SalesOrders[Secondary_Grouping_Product_Number]` | EXACT |
| Sales Representative (name) | AAS `KNA1`-based | `Billing[Sales_Representative_T]` / `SalesOrders[Sales_Representative_T]` | STRONG |
| Sales Representative (ID) | AAS `KNA1`-based | `Billing[Sales_Representative]` / `SalesOrders[Sales_Representative]` | EXACT |
| Project Coordinator (name) | AAS-exposed | `Billing[Project_Coordinator_T]` / `SalesOrders[Project_Coordinator_T]` | STRONG |
| Project Coordinator (ID) | AAS-exposed | `Billing[Project_Coordinator]` / `SalesOrders[Project_Coordinator]` | EXACT |
| Project Name | AAS-exposed | `Billing[ProjectName]` / `SalesOrders[Project_Name]` | STRONG (naming variant) |
| Customer Full Name | AAS `KNA1[NAME1]` | `Billing[CustomerFullName]` / `SalesOrders[CustomerFullName]` | STRONG |
| Sold-to Description | AAS `KNA1[NAME1]` (sold-to variant) | `Billing[SoldToParty_D12_T]` / `SalesOrders[SoldToParty_D3_T]` | STRONG |
| Customer Account Assignment Group (Description) | (AAS `KNVV`-based — was previously KNVV.csv missing) | `Billing[CustomerAccountAssignmentGroup_T]` / `SalesOrders[CustomerAccountAssignmentGroup_T]` | EXACT |
| Territory Name (Sold-to / Ship-to / Bill-to / Payer) | AAS-exposed | Billing: `Territory_NameSoldToPart_A_12` / `Territory_NameBillToPart_A_14` / `Territory_NameShipToPart_A_13` / generic `Territory_Name`. SalesOrders: `Billto_Territory` / `Payer_Territory` / `Shipto_Territory` / generic `Territory_Name`. | EXACT |
| State Name | AAS-exposed | `Billing[State_Name]` / `SalesOrders[State_Name]` | EXACT |
| Country | AAS-exposed | `Billing[Country]` / `SalesOrders[Country]` | EXACT |
| Region (raw) | AAS-exposed | `Billing[Region]` / `SalesOrders[Region]` | EXACT |
| Region (business rollup) | (was via KNA1→GEOINFO in prod) | `KRW_NA_FF_GEOINFO[COUNTRY_REGION]` (via State_Name join) | STRONG |
| Fiscal Year | AAS `KRW_NA_FF_FISCALPERIOD[Fiscal Year]` | `Billing[FiscalYear]` / `SalesOrders[FiscalYear]` / dataflow `KRW_NA_FF_FISCALPERIOD[Fiscal Year]` | EXACT |
| Fiscal Period | dataflow `KRW_NA_FF_FISCALPERIOD[Fiscal Period]` | `SalesOrders[FiscalPeriod]` / dataflow same | EXACT |
| Fiscal Year Period | dataflow | `Billing[FiscalYearPeriod]` / dataflow same | EXACT |
| Fiscal Month | AAS-exposed | `Billing[Fiscal_Month]` / `SalesOrders[Fiscal_Month]` | EXACT |
| Calendar Date | dataflow `KRW_NA_FF_CALENDAR[Date]` | `KRW_NA_FF_CALENDAR[Date]` + `DimDate[Date]` (AWIP has both) | EXACT |
| Latitude / Longitude | dataflow `KRW_NA_FF_GEOINFO[Latitude/Longitude]` | same in AWIP | EXACT |

### 1c. Salesforce-sourced fields (still missing from AWIP)

| Production field | Production table | AWIP source | Confidence |
|---|---|---|---|
| Quote Number | `Salesforce Quotes[QuoteNumber]` | ❌ NOT FOUND | — |
| Quote Amount / Grand Total | `Salesforce Quotes[GrandTotal]` | ❌ NOT FOUND | — |
| Quote Status | `Salesforce Quotes[Status]` | ❌ NOT FOUND | — |
| Quote Expiration Date | `Salesforce Quotes[ExpirationDate]` | ❌ NOT FOUND | — |
| Quote Line Product | `Salesforce Quote Line Item[Product_Name__c]` / `[Product_Family__c]` | ❌ NOT FOUND | — |
| Quote Line Net Unit Price | `Salesforce Quote Line Item[Net_Unit_Price__c]` | ❌ NOT FOUND | — |
| Quote Line List Extended | `Salesforce Quote Line Item[List_Extended__c]` | ❌ NOT FOUND | — |
| Quote Line Net Extended | `Salesforce Quote Line Item[Net_Extended__c]` | ❌ NOT FOUND | — |
| Owner (Sales Rep for the quote) | `Salesforce Quotes[OwnerId]` / (User lookup) | ❌ NOT FOUND | — |

All Salesforce fields await the business decision on whether to add a Salesforce connection to AWIP.

## 2. Summary

- **Fully mapped (EXACT / STRONG):** ~50 production fields → AWIP columns
- **Partially mapped / needs Phase 9 rebuild:** ~5 fields (forecast columns — resolved by importing `KRW-NA_FF_FORECAST`)
- **NOT FOUND (Salesforce-scoped):** ~10 fields (blocked pending business decision)
- **Deprecated (from ODBC-era `Customer.xlsx` / `KNVV.csv` classifications):** 0 remain — all recovered via native fact-table columns

**Written:** 2026-08-13

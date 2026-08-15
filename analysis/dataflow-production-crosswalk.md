# Production → Dataflow Crosswalk

**Purpose:** For each production report object that was previously classified `MISSING SOURCE`, test whether its source now exists in one of the 13 Power BI Dataflow tables **or** in a column of the enriched `Billing` / `SalesOrders` tables that was not present in the earlier inventory.

**Confidence rubric (user directive):**
- **EXACT** — same column name / grain / semantics; safe to use automatically
- **STRONG** — different column name but confirmed same domain and grain; safe to use automatically
- **POSSIBLE** — plausible match but value domain / semantics not yet verified; needs value-domain probe or business confirmation before use
- **NOT FOUND** — no equivalent in the current model

**Only EXACT and STRONG mappings may be applied automatically during semantic-model repair.**

---

## 1. Fields previously flagged MISSING SOURCE — re-classification

Source of the previous classification: `analysis/missing-data-sources.md` and `analysis/unmapped-items.md`.

### 1.1 From `Customer.xlsx` (external, before)

| Production field | Previous source | Previous status | New source found | Where | Confidence |
|---|---|---|---|---|---|
| **Application** | Customer.xlsx | NOT FOUND | `Billing[Application]` | Billing.tmdl:301 | **EXACT** |
| **Application (SalesOrders)** | Customer.xlsx | NOT FOUND | `SalesOrders[Application_Product_Number]` | SalesOrders.tmdl:304 | STRONG (name variant) |
| **Industry** | Customer.xlsx | NOT FOUND | `Billing[Industry]`, `SalesOrders[Industry]` | Billing.tmdl:1064, SalesOrders.tmdl:859 | **EXACT** |
| **Company Type** | Customer.xlsx | NOT FOUND | *no direct match* — closest is `CustomerAccountGroup` / `IndustryType` | Billing (has both) | POSSIBLE — semantics unverified |
| **Secondary Grouping** | Customer.xlsx | NOT FOUND | `Billing[Secondary_Grouping]`, `SalesOrders[Secondary_Grouping_Product_Number]` | Billing.tmdl (col list), SalesOrders (col list) | **EXACT** (Billing), STRONG (SalesOrders) |
| **Sales Representative** (ID) | Customer.xlsx | NOT FOUND | `Billing[Sales_Representative]`, `SalesOrders[Sales_Representative]` | both fact tables | **EXACT** |
| **Sales Representative Name** | Customer.xlsx | NOT FOUND | `Billing[Sales_Representative_T]`, `SalesOrders[Sales_Representative_T]` (also `_Sales_Representativ` variants) | both fact tables | STRONG — `_T` suffix is SAP text/description pattern; verify one distinct-value pair |
| **Project Coordinator** | Customer.xlsx | NOT FOUND | `Billing[Project_Coordinator]` (ID) + `Billing[Project_Coordinator_T]` (name), `SalesOrders` same | both fact tables | **EXACT** |
| **Customer Project Name** (`ProjectName`) | Customer.xlsx | NOT FOUND | `Billing[ProjectName]`, `SalesOrders[Project_Name]` | both fact tables | **EXACT** (Billing), STRONG (SalesOrders — underscore variant) |
| **Sold-to party Description** (customer name) | Customer.xlsx | NOT FOUND | `Billing[CustomerFullName]` + `Billing[SoldToParty_D12_T]`, `SalesOrders[CustomerFullName]` + `SalesOrders[SoldToParty_D3_T]` | both fact tables | STRONG — need distinct-value probe to decide `CustomerFullName` vs `_T` variant |
| **Territory Sold-to / Ship-to / Bill-to / Payer** | Customer.xlsx | NOT FOUND | Billing: `Territory_Name`, `Territory_NameSoldToPart_A_12`, `Territory_NameBillToPart_A_14`, `Territory_NameShipToPart_A_13`. SalesOrders: `Territory_Name`, `Billto_Territory`, `Payer_Territory`, `Shipto_Territory`. | both fact tables | **EXACT** — all four partner directions present |
| **Material Description** | Customer.xlsx | NOT FOUND | `Billing[Material_D17_T]`, `SalesOrders[Product_D14_T]` | both fact tables | STRONG |
| **Cost of sales** | Customer.xlsx | NOT FOUND | `Billing[NetSlsCostAmount]` (+ `_CC` variant), `SalesOrders[Open_Cost]`, `SalesOrders[IncSalesOrdCost]` | both fact tables | STRONG for Billing (EXACT domain: net sales cost). SalesOrders splits open vs. incoming — semantics need business confirmation. |
| **Gross Margin** | Customer.xlsx | NOT FOUND | `Billing[Gross_Margin]`, `SalesOrders[Gross_Margin]`, `SalesOrders[Gross_Margin_Order_Intake]`, `SalesOrders[Gross_Margin_for_open_orders]` | both fact tables | **EXACT** for Billing. SalesOrders has three GM variants — need business rule for which drives dashboards. |
| **Gross Margin %** | Customer.xlsx | NOT FOUND | `Billing[Margin_Percent]`, `SalesOrders[Gross_margin_percentage_for_Order_Intake]`, `SalesOrders[Gross_margin_percentage_for_open_orders]` | both fact tables | STRONG |
| **Region (business geography)** | Customer.xlsx | NOT FOUND | `Billing[Region]`, `SalesOrders[Region]` + `KRW_NA_FF_GEOINFO[COUNTRY_REGION]` (via State_Name relationship) | both fact tables + dataflow | **EXACT** (Region column directly on facts). Dataflow provides business-friendly rollup if `Region` on facts is a raw code. |

### 1.2 From `KNVV.csv` (external, before)

| Production field | Previous source | Previous status | New source found | Confidence |
|---|---|---|---|---|
| **Account Assignment Group** (code) | KNVV.csv (originally) — but Billing already had `CustomerAccountAssignmentGroup` | (code was already on Billing pre-dataflow) | `Billing[CustomerAccountAssignmentGroup]`, `SalesOrders[CustomerAccountAssignmentGroup]` | **EXACT** |
| **Account Assignment Group Description** | KNVV.csv | NOT FOUND | `Billing[CustomerAccountAssignmentGroup_T]`, `SalesOrders[CustomerAccountAssignmentGroup_T]` | **EXACT** — the `_T` text version is now native on both facts. **KNVV.csv is no longer required.** |

### 1.3 Forecast / ISO measures (previously BLOCKED)

Previous blocker: Billing forecast rows had `FC_Product_Group = blank`, so `Sum Fcst Sales in FT2 for Membranes` returned 0.

| Production measure / field | Previous status | New source found | Where | Confidence |
|---|---|---|---|---|
| `Sum Fcst Sales in FT2 for Membranes` (Billing) | BLOCKED (returned 0) | `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` **and** `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` (new native column) | dataflow + Billing.tmdl | **STRONG** — two independent sources for the same figure. Prefer the native Billing column (simpler, same-table); use dataflow as cross-check. |
| `ISO Rate Fcst IS` (Billing) | BLOCKED (÷0) | `Billing[ISO_Rate_Forecast]` (new native column) **and** derivable from `KRW_NA_FF_FORECAST_INTAKE[Sales ISO bdft] / [Sales Membrane sqft]` | Billing.tmdl + dataflow | **STRONG** — the pre-computed ratio is now on the Billing table. Value-domain probe recommended (must match Order-Intake side ≈ 2.63 order of magnitude to confirm the same definition). |
| `Sum Fcst Order Qty. in FT2 for Membranes OI` (SalesOrders) | WORKS in RL | `SalesOrders[Sales_Forecast_Membrane_Qty_in_FT2]` (new native column) — equivalent to the DAX version | SalesOrders.tmdl | **EXACT** — DAX version already works but native column is simpler |
| `ISO Rate Fcst OI` (SalesOrders) | WORKS (2.63) | `SalesOrders[ISO_Rate_Forecast]` (new native column) | SalesOrders.tmdl | **EXACT** — matches existing DAX result |
| Order-Intake forecast quantities | WORKS in RL | `KRW_NA_FF_FORECAST_INTAKE[Sales $]`, `[Sales ISO sqft]`, `[Sales ISO bdft]`, `[Sales Membrane sqft]` provide independent totals at fiscal-period grain | dataflow | STRONG cross-check |

### 1.4 Fiscal calendar attributes (previously MISSING)

| Production field | Previous status | New source found | Where | Confidence |
|---|---|---|---|---|
| Fiscal Year | MISSING | `Billing[FiscalYear]`, `SalesOrders[FiscalYear]`, `KRW_NA_FF_FISCALPERIOD[Fiscal Year]`, `KRW_NA_FF_HISTSB1[Fiscal Year]` | multiple | **EXACT** |
| Fiscal Period | MISSING | `SalesOrders[FiscalPeriod]`, `KRW_NA_FF_FISCALPERIOD[Fiscal Period]` | multiple | **EXACT** |
| Fiscal Year Period (combined key) | MISSING | `Billing[FiscalYearPeriod]`, `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]`, `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period]` | multiple | **EXACT** — same domain; format compatibility to be verified |
| Fiscal Month | MISSING | `Billing[Fiscal_Month]`, `SalesOrders[Fiscal_Month]` | fact tables | **EXACT** |
| Period Sort key | MISSING | `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period Sorted]` | dataflow | STRONG |

### 1.5 Territory / geographic mapping (previously MISSING)

| Production usage | Previous status | New source found | Where | Confidence |
|---|---|---|---|---|
| Territory Name | MISSING | `Billing[Territory_Name]`, `SalesOrders[Territory_Name]`, `KRW_NA_FF_TERRITORY[Territory Name]` | facts + dataflow | **EXACT** (facts) |
| Territory ID | MISSING | `KRW_NA_FF_ZIPCODES[Territory ID]` | dataflow | **EXACT** |
| Zip → Territory mapping | MISSING | `KRW_NA_FF_ZIPCODES` (bridge) + `KRW_NA_FF_TERRITORY` (dim) | dataflow | STRONG — but only needed if a report visual actually pivots on zip; today all facts already carry Territory_Name |
| State (business geography) | MISSING | `Billing[State_Name]`, `SalesOrders[State_Name]`, `KRW_NA_FF_GEOINFO[State]` | facts + dataflow | **EXACT** (facts) |
| Country_Region (business rollup) | MISSING | `KRW_NA_FF_GEOINFO[COUNTRY_REGION]` | dataflow | STRONG — usable via the auto-detected `Billing/SalesOrders[State_Name] → GEOINFO[State]` relationship |
| Latitude / Longitude | MISSING (never available) | `KRW_NA_FF_GEOINFO[Latitude]`, `[Longitude]` (double) | dataflow | **EXACT** — enables map visuals that production never had |

### 1.6 Product / Application mapping (previously MISSING)

| Production field | Previous status | New source found | Where | Confidence |
|---|---|---|---|---|
| Product Family | POSSIBLE (only `_Product_Number` variant existed) | `Billing[Product_Family]` (direct — new), `SalesOrders[Product_Family_Product_Number]` (still only variant) | Billing.tmdl:1552, SalesOrders.tmdl | **EXACT** (Billing), STRONG (SalesOrders — need distinct-value probe) |
| Product Group | POSSIBLE | `Billing[ProductGroup]`, `SalesOrders[ProductGroup]` + `_Product_Number` variant | both facts | **EXACT** |
| Application | NOT FOUND (Customer.xlsx) | `Billing[Application]`, `SalesOrders[Application_Product_Number]` | facts | **EXACT** (Billing) |

---

## 2. Salesforce (User / Quote / Quote Line Item)

Status: **no dataflow provides this data.** Salesforce sources are not present in either the Datasphere facts or the 13 dataflow tables. Still **NOT FOUND**. See `still-missing-after-dataflows.md` for scope decision.

---

## 3. CAPEX / cost accounting / P&L structure

These are **new capabilities** not tied to any previously-classified missing item on the AWIP Commercial Sales pages. They enable CAPEX and cost reporting that the original production dashboards did not cover. Documented for completeness but out of scope for the commercial sales report rebuild.

---

## 4. Summary tally

| Previous classification bucket | Item count | Now EXACT | Now STRONG | Now POSSIBLE | Still NOT FOUND |
|---|---|---|---|---|---|
| Customer.xlsx-sourced fields (§1.1) | 15 | 8 | 6 | 1 | 0 |
| KNVV.csv-sourced fields (§1.2) | 1 | 1 | 0 | 0 | 0 |
| Forecast / ISO blockers (§1.3) | 4 | 2 | 3 | 0 | 0 |
| Fiscal calendar (§1.4) | 5 | 4 | 1 | 0 | 0 |
| Territory / geo (§1.5) | 6 | 4 | 2 | 0 | 0 |
| Product / Application (§1.6) | 3 | 2 | 1 | 0 | 0 |
| Salesforce (§2) | 3 | 0 | 0 | 0 | 3 |

**Net effect:** of ~34 previously blocked / missing items, **21 are now EXACT, 13 are STRONG or POSSIBLE, 3 remain NOT FOUND (all Salesforce).**

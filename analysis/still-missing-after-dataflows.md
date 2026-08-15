# Still Missing After Dataflows

**Purpose:** After including the 13 new Power BI Dataflow tables and re-inspecting the enriched Datasphere `Billing` / `SalesOrders` columns, this file lists the production items that remain **NOT FOUND** and cannot be reproduced from any source currently in the AWIP_Commercial_Sales model.

This supersedes the previous `analysis/missing-data-sources.md` and the `MISSING SOURCE` section of `analysis/unmapped-items.md` for anything **not** listed here.

---

## 1. Confirmed still-missing (Salesforce)

### 1.1 Salesforce Quote / Quote Line Item / User

**Production source:**
```m
Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48, CreateNavigationProperties=true])
```

**What it provides in production:**
- `User` — Salesforce user records (100+ cols)
- `Quote` — quote headers with custom fields (`Expiry_Day_Count__c`, `Project__c`, `Total_List_Price__c`, `Size_Sqft__c`, …)
- `Quote Line Item` — quote lines with custom fields (`Net_Unit_Price__c`, `Product_Family__c`, `List_Extended__c`, `Net_Extended__c`, …)

**Where used:** Internal relationships among `Quote` / `QLI` / `User`. **Not confirmed on any of the pages inventoried** (Invoiced Sales, Order Intake, Backlog). Possibly used on Extended Invoiced Sales (14 visuals) / Extended Order Intake (16 visuals), which were not fully field-inventoried in Phase 1.

**Impact:** If a report visual references Salesforce list price, discount, opportunity link, or quote status, that visual cannot be reproduced without a new Salesforce connection.

**Options:**
1. Wire a Salesforce connection into the new PBIP (independent of SAP Datasphere and independent of dataflows). Requires org Salesforce credentials + Power BI service gateway.
2. Drop any quote-related visuals if they are not core to the reproduction.
3. Ask Ana / James whether Salesforce data is still in scope.

**Recommendation:** ask business owner. Do **not** attempt to fabricate quote-shaped data from SAP.

---

## 2. Previously-listed items that ARE recovered

For the record — these items were previously marked missing and are **no longer** missing:

- Customer.xlsx-sourced Application, Industry, Sales Rep name, Project Coordinator, Territory (4 partners), Material Description, Cost of Sales, Gross Margin, Gross Margin %, Region — all now on `Billing` / `SalesOrders` as native columns.
- KNVV.csv Account Assignment Group Description — now on `Billing[CustomerAccountAssignmentGroup_T]`.
- Fiscal calendar attributes — now on `Billing` / `SalesOrders` + `KRW_NA_FF_FISCALPERIOD`.
- Territory / geography mapping — native `Territory_Name` + `KRW_NA_FF_TERRITORY` / `KRW_NA_FF_ZIPCODES` / `KRW_NA_FF_GEOINFO`.
- Forecast values (previously BLOCKED for Billing side ISO Rate Fcst IS) — now on `Billing[ISO_Rate_Forecast]`, `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` **and** `KRW_NA_FF_FORECAST_INTAKE`.

See [`recovered-missing-fields.md`](recovered-missing-fields.md) and [`dataflow-production-crosswalk.md`](dataflow-production-crosswalk.md) for the details.

---

## 3. Nice-to-haves flagged in previous docs but not blockers

### 3.1 Report content not yet fully inventoried

The following production pages had visual counts but no per-visual field-level inventory:
- Extended Invoiced Sales - Dashboard (14 visuals)
- Extended Order Intake - Dashboard (16 visuals)
- Backlog (11 visuals) — beyond the confirmed page-level filter
- Backlog - Details (5 visuals)
- Backlog by Rep (7 visuals)
- Invoiced Sales - Detail (6 visuals) — 2 confirmed, 4 remaining
- Order Intake - Detail (7 visuals) — 1 confirmed, 6 remaining
- Order Intake - Dashboard (16 visuals) — 1 confirmed, 15 remaining

**Impact of dataflow discovery on this list:** most of the fields these pages are likely to use (Application, Industry, Gross Margin, Cost of sales, Project fields) are now available in the enriched Billing/SalesOrders columns. The residual risk of missing fields on these pages is limited to Salesforce quote data — which will hit the blocker in §1.

**Recommendation:** if any of these pages are in scope for reproduction, run a second Explore pass focused on those specific pages to enumerate their field usage. Now most fields will map; only Salesforce items will surface as still-missing.

### 3.2 Kingspan logo image

`kingspan-roofing-waterproofing8422940714883275.png` — embedded in production `Report/StaticResources/RegisteredResources`. Must be copied into the new project to reproduce branding.

Status: **carry-over housekeeping**, no new blocker.

### 3.3 Report theme `CY26SU05`

Built-in Power BI theme (July 2026). No custom JSON needed. No blocker.

---

## 4. Blocker summary — revised

| Missing source | Blocks | Severity | Resolution |
|---|---|---|---|
| Salesforce (Quote / QLI / User) | Any Quote-related visuals on Extended pages (not yet fully inventoried) | UNKNOWN — depends on scope | Business decision: wire up Salesforce, or drop those visuals |

(This table previously had 3 rows; KNVV.csv and Customer.xlsx are removed as their fields are now sourced from native columns.)

---

## 5. Questions to Ana / James — revised

The previous list of 6 questions is reduced to 2:

1. **Salesforce scope:** Are Salesforce Quote / Quote Line Item / User data required in the new AWIP Commercial Sales dashboards? If yes, we need to add a Salesforce connection to the new PBIP.
2. **Report scope confirmation:** Extended Invoiced Sales / Extended Order Intake pages (14 / 16 visuals) — are they in scope for the reproduction? If yes, we will do a targeted field inventory and confirm nothing beyond Salesforce is still blocked.

Previously-open questions that are now resolved:
- ~~Customer.xlsx ownership~~ → not required, native SAP columns cover the fields.
- ~~KNVV strategy~~ → not required, `CustomerAccountAssignmentGroup_T` covers it.
- ~~Application / Industry / Sold-to description / Sales Rep origin~~ → confirmed as native SAP columns.
- ~~Cost of sales / Gross Margin / GM %~~ → native `NetSlsCostAmount` / `Gross_Margin` / `Margin_Percent` columns.

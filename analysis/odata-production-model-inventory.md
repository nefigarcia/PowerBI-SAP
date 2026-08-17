# OData Production Model Inventory

> ⚠ **Measure count on this page is INCOMPLETE (v1).** The v1 inventory only captured 17 measures on the two FORECAST tables. Kingspan actually has **113 total measures** in the production `.pbip` TMDL — the missing 96 live on the `_SAP_` tables (VBRP: 45, VBAP OI: 43, VBAP SB: 5, FORECAST_INTAKE undercount +3 for the correct 10). For the **complete measure inventory including full DAX for every measure, see [`odata-production-measures-full.md`](odata-production-measures-full.md)**.
>
> The `_SAP_` tables are excluded as *data sources* per the dataflow rule (they duplicate SAP Datasphere OData), but their **measures on those tables are Kingspan's canonical production DAX** — those need to be ported / adapted to AWIP.
>
> Everything else on this page (tables, columns, relationships, model architecture) remains correct.

**Source:** `production-reference-odata/Amalgamated Sales Reports - JC.SemanticModel/definition/` (READ ONLY)

**Coverage:** 11 in-scope tables · ~~17 measures~~ **113 measures** (see full-measures file) · 25 relationships · 3 expressions
**Excluded per rule for data sourcing:** 16 `_SAP_` tables + 21 auto-generated Time Intelligence tables (but their MEASURE DAX is captured in the full-measures file since it's canonical production logic)

---

## Critical architectural finding

**The OData production reference is NOT a native OData connection to SAP Datasphere.** All partitions on all tables are `DirectQuery` to **Azure Analysis Services** — three separate AAS databases hosted on the shared server `powerbi://api.powerbi.com/v1.0/myorg/KRW - North America Reporting`:

| AAS database | Consumed by |
|---|---|
| `KRW_NA_SM_INVOICED` | Base variants: CALENDAR, FISCALPERIOD, FORECAST, GEOINFO, FiscalYearPeriods Slicer + `_SAP_` INVOICED variants |
| `KRW_NA_SM_SORDERS` | OI (Order-Intake) variants: CALENDAR OI, FISCALPERIOD OI, FORECAST_INTAKE, GEOINFO OI, FiscalYearPeriods Slicer OI + `_SAP_` OI variants |
| `KRW_NA_SM_BACKLOG` | SB (Sales-Backlog) variants: CALENDAR SB, FISCALPERIOD SB, GEOINFO SB, FiscalYearPeriods Slicer SB + `_SAP_` SB variants |

**Implication for AWIP alignment:**
- Production uses DirectQuery + role-playing dim copies (one CALENDAR / FISCALPERIOD / GEOINFO per AAS cube).
- AWIP uses Import mode from Power BI Dataflows and a shared `DimDate`.
- The `_SAP_` exclusion rule the user set applies because **the same SAP data reaches AWIP via two paths** (Datasphere OData Billing/Sales AND via SAP dataflows) — pick one to avoid double-counting.

---

## Role-playing dimension copies

Each of these dimensions has three copies — one per AAS cube:

| Base | OI variant | SB variant | Column-level differences |
|---|---|---|---|
| `KRW_NA_FF_CALENDAR` (15 cols) | `KRW_NA_FF_CALENDAR OI` | `KRW_NA_FF_CALENDAR SB` | Identical structure; different partition source (INVOICED / SORDERS / BACKLOG) and different `LocalDateTable_*` variation refs |
| `KRW_NA_FF_FISCALPERIOD` (4 cols) | `KRW_NA_FF_FISCALPERIOD OI` | `KRW_NA_FF_FISCALPERIOD SB` | Identical structure; different partition source |
| `KRW_NA_FF_GEOINFO` (5 cols + COUNTRY_REGION key) | `KRW_NA_FF_GEOINFO OI` | `KRW_NA_FF_GEOINFO SB` | `COUNTRY_REGION` is **hidden** in OI and SB variants — visible only in the INVOICED base |
| `FiscalYearPeriods Slicer` (1 col — disconnected slicer) | `FiscalYearPeriods Slicer OI` | `FiscalYearPeriods Slicer SB` | Identical structure; each connects to its own FORECAST/FORECAST_INTAKE table via bi-di relationship |

None of these dim copies carry measures. All measures live on the two FORECAST tables (below) or in the AAS cubes (invisible to us in TMDL).

---

## Forecast tables (this is where the DAX lives)

### `KRW-NA_FF_FORECAST` — 10 measures — INVOICED cube

Note the **hyphen** in the name — not `KRW_NA_FF_FORECAST`. Confirmed intentional.

**Columns (11):**
| Column | Type | Notes |
|---|---|---|
| `Period` | string | source |
| `Year` | string | source |
| `Sales $` | double | formatString `$#,0.###############...` |
| `Sales Membrane sqft` | double | formatString `#,0` |
| `Sales ISO sqft` | double | source |
| `Sales ISO bdft` | double | formatString `#,0` |
| `Fiscal Year Period` | calculated | `[Year] & "." & [Period]` |
| `Fiscal Year Period 2` | string | source, key |
| `ISO Rate Forecast` | **calculated column** | `IF([Sales Membrane sqft]=0, 0, [Sales ISO bdft]/[Sales Membrane sqft])`, formatString `0.0` |
| `Fiscal Year Period Sorted` | string | source |
| `Prior Year` | calculated | int64 |

**Measures (10):**

1. **`ISO Rate Fcst`** — formatString `#,0.00`
```dax
VAR IsoRateFcst =
    DIVIDE(SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
           SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft]))
RETURN IF(IsoRateFcst = BLANK(), 0, IsoRateFcst)
```

2. **`Current Month Invoice Revenue Fcst`** — formatString `$#,0;($#,0);$#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales $]),
          FILTER('KRW-NA_FF_FORECAST',
                 'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]))
```

3. **`Current Month Invoiced Sales Membrane sqft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft]),
          FILTER('KRW-NA_FF_FORECAST',
                 'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]))
```

4. **`YTD Invoiced Sales Membrane sqft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft]),
          FILTER('KRW_NA_FF_CALENDAR',
                 YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())))
```

5. **`Current Month Invoiced Sales ISO bdft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
          FILTER('KRW-NA_FF_FORECAST',
                 'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]))
```

6. **`YTD Invoiced Sales ISO bdft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
          FILTER('KRW_NA_FF_CALENDAR',
                 YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())))
```

7. **`Current Month Invoiced Sales ISO sqft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales ISO sqft]),
          FILTER('KRW-NA_FF_FORECAST',
                 'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]))
```

8. **`YTD Invoiced Sales ISO sqft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales ISO sqft]),
          FILTER('KRW_NA_FF_CALENDAR',
                 YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())))
```

9. **`YTD Invoice Revenue Fcst`** — formatString `$#,0;($#,0);$#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales $]),
          FILTER('KRW_NA_FF_CALENDAR',
                 YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())))
```

10. **`Current Month Invoiced Sales ISO sqft FM`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[Sales ISO sqft]),
          'KRW-NA_FF_FORECAST'[Fiscal Year Period Sorted] = "2026.02")
```

### `KRW_NA_FF_FORECAST_INTAKE` — 7 measures — SORDERS cube

**Columns (10):**
| Column | Type | Notes |
|---|---|---|
| `Period` | string | source |
| `Year` | string | source |
| `Sales $` | double | source |
| `Sales Membrane sqft` | double | source |
| `Sales ISO sqft` | double | source |
| `Sales ISO bdft` | double | source |
| `Fiscal Year Period` | string | source, key |
| `Fiscal Year Period Sorted` | string | source |
| `Prior Year` | int64 | source |
| `ISO Rate Forecast` | double | **source column** (not calculated) — comes from the AAS cube pre-computed |

**Measures (7):**

1. **`ISO Rate Fcst VBAP`** — formatString `0.00`
```dax
VAR IsoRateFcstVBAP =
    DIVIDE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
           SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales Membrane sqft]))
RETURN IF(IsoRateFcstVBAP = BLANK(), 0, IsoRateFcstVBAP)
```

2. **`Current Month Order Revenue Fcst`** — formatString `$#,0;($#,0);$#,0`
```dax
CALCULATE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales $]),
          FILTER('KRW_NA_FF_FORECAST_INTAKE',
                 'KRW_NA_FF_FORECAST_INTAKE'[Fiscal Year Period] = [Current FYP VBAP OI]))
```

3. **`Current Fiscal Month Sales Membrane sqft`** — formatString `#,0`
**⚠ References `_SAP_` table** `KRW_NA_SAP_VBAP OI` in filter — must be remapped to `SalesOrders[Product_Family]` in AWIP.
```dax
VAR CurrentFYPValueMOIFT2Fcst = [Current FYP VBAP OI]
RETURN
CALCULATE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales Membrane sqft]),
          CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
          KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period] = CurrentFYPValueMOIFT2Fcst)
```

4. **`Current Fiscal Month Sales ISO sqft`** — formatString `#,0`
**⚠ References `_SAP_` table** `KRW_NA_SAP_VBAP OI` in filter — must be remapped to `SalesOrders[Product_Family]` in AWIP.
```dax
VAR CurrentFYPValueISOOIFT2Fcst = [Current FYP VBAP OI]
RETURN
CALCULATE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO sqft]),
          CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
          KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period] = CurrentFYPValueISOOIFT2Fcst)
```

5. **`Current Month Sales ISO bdft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
          FILTER('KRW_NA_FF_CALENDAR OI',
                 YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) &&
                 MONTH('KRW_NA_FF_CALENDAR OI'[Date]) = MONTH(TODAY())))
```

6. **`YTD Sales ISO bdft`** — formatString `#,0`
```dax
CALCULATE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
          FILTER('KRW_NA_FF_CALENDAR OI',
                 YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY())))
```

7. **`YTD Sales ISO sqft`** — formatString `#,0` (plus additional YTD variants for Membrane sqft, Order Revenue Fcst, Current Fiscal Month ISO bdft, same pattern)

---

## Salesforce tables

### `Salesforce Quote Line Item`
- Partition: `Salesforce.Data("https://krw.my.salesforce.com/", [ApiVersion=48])`, entity `QuoteLineItem`, import mode
- Columns (30): Id, IsDeleted, LineNumber, CurrencyIsoCode, CreatedDate, CreatedById, LastModifiedDate, LastModifiedById, SystemModstamp, LastViewedDate, LastReferencedDate, QuoteId, PricebookEntryId, OpportunityLineItemId, Quantity, UnitPrice, Discount, Description, ServiceDate, Product2Id, SortOrder, ListPrice, Subtotal, TotalPrice, `Net_Unit_Price__c`, `Product_Family__c`, `Product_Name__c`, `UOM__c`, `List_Extended__c`, `Net_Extended__c`, `Net_Unit_Price_Flow__c`, `Actual_Discount__c`, `Total_List_Price__c`
- Note: `QuoteId` → `Salesforce Quotes[Id]` relationship

### `Salesforce Quotes`
- Partition: `Salesforce.Data(...)`, entity `Quote`, import mode
- Columns (80+): Id (key), OwnerId, IsDeleted, Name, CurrencyIsoCode, RecordTypeId, dates (CreatedDate / LastModifiedDate / SystemModstamp / LastViewedDate / LastReferencedDate / ExpirationDate), OpportunityId, Pricebook2Id, ContactId, QuoteNumber, IsSyncing, ShippingHandling, Tax, Status, Description, Subtotal, TotalPrice, LineItemCount, full billing/shipping/quote-to/additional address fields (Street/City/State/PostalCode/Country + StateCode/CountryCode + Lat/Long/GeocodeAccuracy/Address), BillingName / ShippingName / QuoteToName / AdditionalName, Email, Phone, Fax, ContractId, AccountId, Discount, GrandTotal, CanCreateQuoteLineItems, custom fields: `Expiry_Day_Count__c`, `Project__c`, `Tax_Exempt__c`, `Primary_Warranty_Quote__c`, `Total_List_Price__c`, `Actual_Discount__c`

---

## Model-level configuration

- **Culture:** `en-GB` (source query culture `en-IE`)
- **DataSourceVersion:** `powerBI_V3`
- **__PBI_TimeIntelligenceEnabled:** `1` (accounts for 21 auto-generated Local/Template date tables)
- **DataAccessOptions:** legacyRedirects, returnErrorValuesAsNull
- **PBI_ProTooling:** DevMode

### Expressions (3) — all point at the same AAS server

| Name | Kind | Path |
|---|---|---|
| `DirectQuery to AS - KRW_NA_SM_INVOICED` | AnalysisServices.Database | `powerbi://api.powerbi.com/v1.0/myorg/KRW - North America Reporting`, db `KRW_NA_SM_INVOICED` |
| `DirectQuery to AS - KRW_NA_SM_SORDERS` | AnalysisServices.Database | same server, db `KRW_NA_SM_SORDERS` |
| `DirectQuery to AS - KRW_NA_SM_BACKLOG` | AnalysisServices.Database | same server, db `KRW_NA_SM_BACKLOG` |

### Relationships (25)

**INVOICED cube:**
1. `KRW_NA_FF_FISCALPERIOD[Calendar Date]` ↔ `KRW_NA_FF_CALENDAR[Calendar Date]` — bothDirections, 1:many
2. `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` → `FiscalYearPeriods Slicer` (no direction printed)
3. `KRW_NA_SAP_KNA1` → `KRW_NA_FF_GEOINFO` on COUNTRY_REGION
4. `KRW_NA_SAP_VBRP` → `KRW_NA_SAP_KNA1` (Sold-To → Customer)
5. `KRW_NA_SAP_VBRP` → `KRW_NA_SAP_LIKP` (Delivery Document)
6. `KRW_NA_SAP_VBRP` → `KRW_NA_SAP_KNVV` (CUST_SALES)

**SORDERS cube (OI):**
7. `KRW_NA_FF_FISCALPERIOD OI[Calendar Date]` ↔ `KRW_NA_FF_CALENDAR OI[Calendar Date]` — bothDirections, 1:many
8. `KRW_NA_FF_FISCALPERIOD OI` → `FiscalYearPeriods Slicer OI` on Fiscal Year Period
9. `KRW_NA_SAP_KNA1 OI` → `KRW_NA_FF_GEOINFO OI` on COUNTRY_REGION
10. `KRW_NA_FF_CALENDAR OI[Date]` → `LocalDateTable_*` (3 relationships: Date / Start of Month / End of Month)
11. `KRW_NA_SAP_VBAP OI` → `KRW_NA_FF_CALENDAR OI` (Document Date)
12. `KRW_NA_SAP_VBAP OI` → `LocalDateTable_*` (Requested Delivery Date)
13. `KRW_NA_SAP_VBAP OI` → `KRW_NA_SAP_KNA1 OI` (Sold-To → Customer)
14. `KRW_NA_SAP_VBAP OI` → `KRW_NA_SAP_KNVV OI` (CUST_SALES)
15. `FiscalYearPeriods Slicer OI` ↔ `KRW_NA_FF_FORECAST_INTAKE` on Fiscal Year Period — bothDirections, 1:many

**BACKLOG cube (SB):**
16. `KRW_NA_FF_FISCALPERIOD SB[Calendar Date]` ↔ `KRW_NA_FF_CALENDAR SB[Calendar Date]` — bothDirections, 1:many
17. `KRW_NA_FF_CALENDAR SB` → `FiscalYearPeriods Slicer SB` on Fiscal Year Period
18. `KRW_NA_SAP_KNA1 SB` → `KRW_NA_FF_GEOINFO SB` on COUNTRY_REGION
19. `KRW_NA_FF_CALENDAR SB[Date]` → `LocalDateTable_*` (3 relationships)
20. `KRW_NA_SAP_VBAP SB` → `KRW_NA_SAP_MARM_BFT 2` (Material)
21. `KRW_NA_SAP_VBAP SB` → `KRW_NA_SAP_KNA1 SB` (Sold-To → Customer)
22. `KRW_NA_SAP_VBAP SB` → `KRW_NA_FF_CALENDAR SB` (Requested Delivery Date)
23. `KRW_NA_SAP_VBAP SB` → `LocalDateTable_*` (Document Date)
24. `KRW_NA_SAP_VBAP SB` ↔ `KRW_NA_SAP_LIPS` on SO_ITEM → DOC_ITM — bothDirections, 1:many
25. `KRW_NA_SAP_VBAP SB` → `KRW_NA_SAP_KNVV SB` (CUST_SALES)

**Salesforce (auto-generated relationships to Local date tables not counted in the 25):**
- Salesforce Quotes → 6 `LocalDateTable_*` (on CreatedDate, LastModifiedDate, SystemModstamp, LastViewedDate, LastReferencedDate, ExpirationDate)
- Salesforce Quote Line Item → 6 `LocalDateTable_*` (same date fields + ServiceDate)
- Salesforce Quote Line Item → Salesforce Quotes (QuoteId → Id)

**Relationship metadata notes:**
- Bi-di relationships are limited to two contexts:
  1. FISCALPERIOD ↔ CALENDAR (all three cube variants) — needed for calendar filter to propagate to fiscal period
  2. FiscalYearPeriods Slicer ↔ FORECAST / FORECAST_INTAKE — disconnected-slicer bi-di so the slicer filters the forecast table without being a "one" side
- All Salesforce date relationships use `joinOnDateBehavior: datePartOnly`

---

## Excluded `_SAP_` tables (16)

| # | Table | AAS cube |
|---|---|---|
| 1 | `KRW_NA_SAP_KNA1` | INVOICED |
| 2 | `KRW_NA_SAP_KNA1 OI` | SORDERS |
| 3 | `KRW_NA_SAP_KNA1 SB` | BACKLOG |
| 4 | `KRW_NA_SAP_KNVV` | INVOICED |
| 5 | `KRW_NA_SAP_KNVV OI` | SORDERS |
| 6 | `KRW_NA_SAP_KNVV SB` | BACKLOG |
| 7 | `KRW_NA_SAP_LIKP` | INVOICED |
| 8 | `KRW_NA_SAP_LIPS` | BACKLOG |
| 9 | `KRW_NA_SAP_MARM_BFT` | INVOICED |
| 10 | `KRW_NA_SAP_MARM_BFT 2` | BACKLOG |
| 11 | `KRW_NA_SAP_TVAPT` | INVOICED |
| 12 | `KRW_NA_SAP_TVM3T` | INVOICED |
| 13 | `KRW_NA_SAP_VBAP OI` | SORDERS |
| 14 | `KRW_NA_SAP_VBAP SB` | BACKLOG |
| 15 | `KRW_NA_SAP_VBPA2` | (unspecified) |
| 16 | `KRW_NA_SAP_VBRP` | INVOICED |

Consumed by many production relationships and by 2 non-`_SAP_` measures (`Current Fiscal Month Sales Membrane sqft` and `Current Fiscal Month Sales ISO sqft` on FORECAST_INTAKE — see Phase 5 remapping notes).

**Auto-generated Time Intelligence tables (21):** 20 × `LocalDateTable_*` + 1 × `DateTableTemplate_86f3efbe-b4de-42f6-8730-5a6c63c9bab1`. Not inventoried.

---

## Anomalies flagged for downstream phases

1. **FORECAST_INTAKE has soft dependencies on `_SAP_` tables** via `CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], …)` inside measures 3 & 4. When we align AWIP, these must be re-pointed at `SalesOrders[Product_Family_Product_Number]` (STRONG confidence — see previous crosswalk work).
2. **`ISO Rate Forecast` column exists twice with different semantics:**
   - `KRW-NA_FF_FORECAST[ISO Rate Forecast]` — **calculated column**, row-level `IF Membrane=0 → 0 ELSE bdft/sqft`
   - `KRW_NA_FF_FORECAST_INTAKE[ISO Rate Forecast]` — **source column**, computed upstream in the AAS SORDERS cube
   Do not conflate the two. Aggregation semantics differ (SUM vs AVG vs DIVIDE-of-SUMs).
3. **`GEOINFO OI` and `GEOINFO SB` hide `COUNTRY_REGION`** — kept only on the INVOICED base variant. Reason inferred: prevent duplicate-key ambiguity in composite model queries against OI/SB cubes.
4. **`Current Month Invoiced Sales ISO sqft FM` measure is hard-coded** to `Fiscal Year Period Sorted = "2026.02"`. Almost certainly a leftover from a specific month's dashboard — will roll stale in March 2026. Flag for the business owner.
5. **Naming inconsistency:** `KRW-NA_FF_FORECAST` uses a **hyphen** where every other Kingspan table uses underscore (`KRW_NA_FF_*`). Not a typo — verified by exact string match in filename and DAX. Any AWIP DAX referring to this table must preserve the hyphen and single-quote wrap.
6. **AAS `Current FYP VBRP` and `Current FYP VBAP OI` references** — these are measures defined *inside the AAS cubes*, not visible in the TMDL. AWIP cannot see or reproduce them without direct AAS access. Requires either (a) reconstructing the "current fiscal year period" DAX ourselves in AWIP using `KRW_NA_FF_FISCALPERIOD` filtered by TODAY(), or (b) asking Ana / James for the AAS definitions.

---

## Inventory sign-off

**Coverage:** 11 in-scope tables · 17 measures · 25 relationships · 3 expressions
**Excluded:** 16 `_SAP_` tables + 21 auto-generated Time Intelligence tables
**Written:** 2026-08-13

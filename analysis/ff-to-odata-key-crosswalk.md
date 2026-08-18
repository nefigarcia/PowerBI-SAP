# Phase 4 — FF ↔ OData Relationship-Key Crosswalk

For every candidate translation identified in Phase 2, map the production `_SAP_` key to the equivalent field in `Billing`, `SalesOrders`, or an intermediate dimension.

## Key column type reference

**Dev FF dimension keys (already imported in AWIP):**

| Table | Column | Data type |
|---|---|---|
| KRW_NA_FF_CALENDAR | Date | dateTime |
| KRW_NA_FF_CALENDAR | Calendar Date | string |
| KRW_NA_FF_FISCALPERIOD | Calendar Date | string |
| KRW_NA_FF_FISCALPERIOD | Fiscal Year Period | string |
| KRW_NA_FF_GEOINFO | State | string |
| KRW_NA_FF_GEOINFO | COUNTRY_REGION | string |
| KRW_NA_FF_GEOINFO | Country | string |
| Fiscal Period Selector | FiscalYearPeriod | string (from Billing[FiscalYearPeriod], `2026007` format) |
| KRW-NA_FF_FORECAST | Fiscal Year Period Billing Format | calculated string (`YYYYPPP`) |
| KRW-NA_FF_FORECAST | Fiscal Year Period | string (`YYYY.PP` = `2026.07`) |
| KRW_NA_FF_FORECAST_INTAKE | Fiscal Year Period | string (assumed `YYYY.PP` format — matches sister FORECAST table) |

**Dev OData fact keys (already imported in AWIP):**

| Table | Column | Data type |
|---|---|---|
| Billing | BillingDocumentDate_D5 | dateTime |
| Billing | FiscalYearPeriod | string (`2026007`) |
| Billing | State_Name | string |
| Billing | Country | string |
| Billing | Region | string |
| SalesOrders | CreationDate_D8 | dateTime |
| SalesOrders | RequestedDeliveryDate | **string** ⚠ (cannot bind to dateTime directly) |
| SalesOrders | State_Name | string |
| SalesOrders | Country | string |
| SalesOrders | Region | string |

---

## Crosswalk table

| # | FF Table | FF Key | Prod `_SAP_` Table | Prod `_SAP_` Key | OData Table | OData Key | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|
| 4 | KRW_NA_FF_CALENDAR | Date (dateTime) | KRW_NA_SAP_VBRP | Billing Date (dateTime) | **Billing** | **BillingDocumentDate_D5** (dateTime) | **EXACT** | 1:1 type match. Semantics = the billing document date. Create m→1, single-direction, active. |
| 22 | KRW_NA_FF_CALENDAR | Date (dateTime) | KRW_NA_SAP_VBAP OI | Document Date (dateTime) | **SalesOrders** | **CreationDate_D8** (dateTime) | **EXACT** | 1:1 type match. In SAP VBAK, AUDAT is the document (created-on) date. This relationship ALREADY EXISTS in dev as INACTIVE (id `a1b2c3d4-e5f6…`). **Activate it** and inactivate the DimDate one. |
| 35 | KRW_NA_FF_CALENDAR | Date (dateTime) | KRW_NA_SAP_VBAP SB | Requested Delivery Date (dateTime) | **SalesOrders** | **RequestedDeliveryDate** ⚠ (string) | **STRONG (with transform)** | RequestedDeliveryDate is stored as string in dev SalesOrders. Options: (a) Add calculated column `RequestedDeliveryDate_dt = DATEVALUE(SalesOrders[RequestedDeliveryDate])` typed as dateTime, then join to CALENDAR.Date, **INACTIVE** (role-play, activated by USERELATIONSHIP in backlog measures). (b) Skip the relationship and use a filter in DAX. Prefer (a) for consistency with production semantics. |
| 7 | KRW_NA_FF_GEOINFO | COUNTRY_REGION (string) | KRW_NA_SAP_KNA1 | COUNTRY_REGION (string) | Billing (or intermediate) | *(no pre-concatenated column)* | **POSSIBLE** | Production join is on a concatenated key `COUNTRY_REGION` (likely `<Country>_<Region>` — cannot verify without inspecting KNA1 sample data). Dev options: (a) Keep existing `Billing.State_Name → KRW_NA_FF_GEOINFO.State` — DIFFERENT grain but may cover the same use case (state-level filtering). (b) Add calculated columns on Billing AND on KRW_NA_FF_GEOINFO named COUNTRY_REGION and join on that. Preferred: keep (a), flag any breakage in Phase 5/9. |
| 17 | KRW_NA_FF_GEOINFO | COUNTRY_REGION (string) | KRW_NA_SAP_KNA1 OI | COUNTRY_REGION (string) | SalesOrders | (same options as row 7) | **POSSIBLE** | Existing dev: `SalesOrders.State_Name → KRW_NA_FF_GEOINFO.State`. Same rationale. |
| 27 | KRW_NA_FF_GEOINFO | COUNTRY_REGION (string) | KRW_NA_SAP_KNA1 SB | COUNTRY_REGION (string) | SalesOrders | (same options as row 17) | **POSSIBLE** | SB and OI both target SalesOrders — a single geographic edge on SalesOrders covers both consumers. |
| 25 | 'FiscalYearPeriods Slicer OI' | Fiscal Year Period (string) | *(no SAP side — this is FF-to-slicer)* | — | Fiscal Period Selector | FiscalYearPeriod (string, `2026007` format) | **STRONG (with transform)** | Prod SlicerOI ↔ FORECAST_INTAKE.'Fiscal Year Period' — dev uses `Fiscal Period Selector` (from Billing distinct FYP). FORECAST_INTAKE `Fiscal Year Period` is `YYYY.PP` format; need calculated column `Fiscal Year Period Billing Format` on FORECAST_INTAKE (identical to the pattern already applied on `KRW-NA_FF_FORECAST`). |
| 1 | KRW_NA_FF_FISCALPERIOD | Calendar Date (string) | *(FF-to-FF only)* | — | *(FF-to-FF only)* | — | **EXACT** | Already exists in dev — nothing to do. |

---

## Column changes required to enable the crosswalk

### On `SalesOrders`
Add calculated column:
```dax
column 'RequestedDeliveryDate_dt' = 
    IF(
        LEN(SalesOrders[RequestedDeliveryDate]) >= 10,
        DATEVALUE(SalesOrders[RequestedDeliveryDate]),
        BLANK()
    )
    dataType: dateTime
    isHidden
```
This lets us build the row-35 relationship without breaking the existing string column.

Alternative: if `RequestedDeliveryDate` string is `YYYY-MM-DD` (which Datasphere's Date-of-Type-D fields typically are), `DATEVALUE` handles it. If the format is different, use `DATE(VALUE(LEFT(…,4)), VALUE(MID(…,6,2)), VALUE(RIGHT(…,2)))`. Phase 5 validation will confirm the format.

### On `KRW_NA_FF_FORECAST_INTAKE`
Add calculated column (mirroring the one already on `KRW-NA_FF_FORECAST`):
```dax
column 'Fiscal Year Period Billing Format' = 
    LEFT('KRW_NA_FF_FORECAST_INTAKE'[Fiscal Year Period Sorted], 4) & "0" 
    & RIGHT('KRW_NA_FF_FORECAST_INTAKE'[Fiscal Year Period Sorted], 2)
    dataType: string
```
This lets us bridge FORECAST_INTAKE to `Fiscal Period Selector` on a common `YYYYPPP` key.

---

## Anti-patterns to avoid

1. **Do NOT** create a relationship between `SalesOrders.RequestedDeliveryDate` (string) and `KRW_NA_FF_CALENDAR.Date` (dateTime). Power BI will accept it as a text join, but the actual date semantics (year/month arithmetic in DAX) will silently break.
2. **Do NOT** create a bidirectional relationship between `Billing` / `SalesOrders` and `KRW_NA_FF_CALENDAR` — production keeps these single-direction. Bidirectional here would let Billing/SalesOrders filter each other via CALENDAR, which is not the desired semantic.
3. **Do NOT** invent a `COUNTRY_REGION` calculated column without first verifying (Phase 5) that Billing.Country + Billing.Region concatenated matches KRW_NA_FF_GEOINFO.COUNTRY_REGION values. If they don't, the join returns 0 rows.
4. **Do NOT** create a role-play copy of `KRW_NA_FF_CALENDAR` (base + OI + SB) to mirror production 1:1. Dev is single-cube; a single CALENDAR + inactive role-play relationships handles all three date semantics.

# OData Production — Complete Measure Inventory (v2)

**Source:** production-reference-odata (READ ONLY)
**Coverage:** 5 tables, **113 measures** total (v1 inventory only captured ~17 across the two FORECAST tables and completely missed the 93 measures on the `_SAP_` tables).
**Motivation:** the v1 Phase 1 inventory (`odata-production-model-inventory.md`) reported only the FORECAST-side DAX. Kingspan's "AAS-cube measures" are, in fact, defined in the production `.pbip` TMDL directly — on `KRW_NA_SAP_VBRP`, `KRW_NA_SAP_VBAP OI`, and `KRW_NA_SAP_VBAP SB` — not in an external AAS cube. This document is the missing piece.

---

## Summary table

| Table                       | Measure count | TMDL line range | Notes                                     |
|-----------------------------|---------------|------------------|-------------------------------------------|
| `KRW_NA_SAP_VBRP`           | 45            | 5 – 730          | Invoiced / billing side                   |
| `KRW_NA_SAP_VBAP OI`        | 43            | 5 – 732          | Order intake side                         |
| `KRW_NA_SAP_VBAP SB`        | 5             | 5 – 96           | Sales backlog side                        |
| `KRW-NA_FF_FORECAST`        | 10            | 5 – 184          | Invoiced forecast (matches v1: 10)        |
| `KRW_NA_FF_FORECAST_INTAKE` | 10            | 5 – 182          | Intake forecast (v1 undercount: v1 = 7)   |
| **TOTAL**                   | **113**       |                  |                                           |

Other tables checked and confirmed measure-free:
`KRW_NA_SAP_KNVV`, `KRW_NA_SAP_KNVV OI`, `KRW_NA_SAP_KNVV SB`, `KRW_NA_SAP_KNA1`, `KRW_NA_SAP_KNA1 OI`, `KRW_NA_SAP_KNA1 SB`, `KRW_NA_SAP_LIKP`, `KRW_NA_SAP_LIPS`, `KRW_NA_SAP_MARM_BFT`, `KRW_NA_SAP_MARM_BFT 2`, `KRW_NA_SAP_TVAPT`, `KRW_NA_SAP_TVM3T`, `KRW_NA_SAP_VBPA2`, `Salesforce Quotes`, `Salesforce Quote Line Item`, `FiscalYearPeriods Slicer` (all three variants), `KRW_NA_FF_CALENDAR` (all three variants), `KRW_NA_FF_FISCALPERIOD` (all three variants), `KRW_NA_FF_GEOINFO` (all three variants).

---

## Cross-cutting anomalies (see per-table sections for detail)

1. **`Sum Revenue in DC with sign VBAP OI` sources the WRONG table.**
   Defined on `KRW_NA_SAP_VBAP OI` but the DAX body reads `SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign])` — copy-paste bug that makes the OI measure return VBRP invoice revenue instead of order revenue.
2. **Hardcoded fiscal period `"2026.2"` on `KRW_NA_SAP_VBAP OI`.**
   `Current Fiscal Month Order FT2 for Membranes Hardcoded` filters `'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = "2026.2"` — stale as soon as calendar month rolls.
3. **Hardcoded fiscal period `"2026.02"` on `KRW-NA_FF_FORECAST`.**
   `Current Month Invoiced Sales ISO sqft FM` filters `[Fiscal Year Period Sorted] = "2026.02"` — inconsistent literal format from #2 (`.02` vs `.2`) suggests two different developers.
4. **Cross-table dependency: forecast INTAKE measures filter on `KRW_NA_SAP_VBAP OI[Product Family]`.**
   `Current Fiscal Month Sales Membrane sqft`, `Current Fiscal Month Sales ISO sqft`, `Current Fiscal Month Sales ISO bdft` all reference the OI product-family column while summing INTAKE columns. Will need re-pointing when porting to AWIP Datasphere.
5. **`Product Family` filter values are inconsistent (`"iso"`, `"ISO"`, `"Membrane"`).**
   `CONTAINSSTRING` is case-insensitive in DAX, so this works — but future refactors on case-sensitive engines will break.
6. **`Current FYP VBRP` and `Current FYP VBAP OI` are helper measures** referenced by 15+ other measures. They use `LOOKUPVALUE(...TODAY())` and thus refresh only when the report is refreshed.
7. **Duplicate-ish measures.** `Current Calendar Month Order FT2 for Membranes` and `Current Calendar Month Order FT2 for Membranes 2` have identical DAX bodies on `KRW_NA_SAP_VBAP OI` — the "2" variant differs only in that it lacks `formatString` and `changedProperty = FormatString`.
8. **Column-reference-as-measure pattern.** `PercDiff PY Sales`, `PercDiff Arrow Sales`, `PercDiff PY Orders`, `PercDiff Arrow Orders` reference `KRW_NA_SAP_VBRP[Revenue Previous Year]` / `'KRW_NA_SAP_VBAP OI'[Revenue Previous Year OI]` using table-column syntax — the referent is actually a **measure**, not a column. Works in DAX but obscures dependency traceability.
9. **`Revenue Previous Year` (VBRP) and `Revenue Previous Year OI` (VBAP OI) use `KRW_NA_FF_CALENDAR[Date]` and `KRW_NA_FF_CALENDAR OI[Date]` respectively** inside `CALCULATE`, but also reference `KRW_NA_SAP_VBRP[Billing Year]` / `[Order Year OI]` — where "Billing Year" and "Order Year OI" are themselves measures returning `YEAR(SELECTEDVALUE(...))`, not columns.
10. **Almost every date-based filter in VBRP/VBAP OI hard-references `TODAY()`** — no snapshot column pattern. Every refresh recomputes from server time.

---

## `Product Family` `CONTAINSSTRING` filter-value catalog

All literals passed to `CONTAINSSTRING([Product Family], "...")` in the model:

| Literal      | Where used                                                             |
|--------------|-------------------------------------------------------------------------|
| `"Membrane"` | 22 measures (both VBRP and VBAP OI/SB, plus FORECAST_INTAKE cross-ref)  |
| `"iso"`      | 19 measures (lowercase — used most often)                              |
| `"ISO"`      | 4 measures on VBRP: `Current Month Billing Qty. in BFT2 for ISO`, `YTD Billing Qty. in BFT2 for ISO`, `Current Month Billing Qty. in FT2 for ISO`, `YTD Billing Qty. in FT2 for ISO` |

`CONTAINSSTRING` is case-insensitive so `"iso"` == `"ISO"` at runtime; keeping the case inconsistency here is a bug of hygiene, not correctness.

---

## `KRW_NA_SAP_VBRP` — invoice-side measures (45)

**Leaf measures** (reference only columns of `KRW_NA_SAP_VBRP` or a `KRW_NA_FF_*` column):
`Average Revenue per Product Family`, `Average Margin per Product Family`, `Average Margin per Fiscal Year Period`, `Sum Billing Qty. in FT2 for Membranes`, `Sum Billing Qty. in BFT2 for ISO`, `Margin Perc`, `Current Month Billing Qty. in FT2 for Membranes`, `YTD Billing Qty. in FT2 for Membranes`, `Current Month Billing Qty. in BFT2 for ISO`, `YTD Billing Qty. in BFT2 for ISO`, `Current Month Billing Qty. in FT2 for ISO`, `YTD Billing Qty. in FT2 for ISO`, `Current Month Invoiced Revenue Billing Date`, `YTD Invoiced Revenue Billing Date`, `Revenue`, `Billing Year`, `Sum Revenue in DC with sign VBRP`, `ISO AOP - $/bdft VBRP`, `Sum Billing Qty. in FT2 for Membranes Prior Year`, `Sum Billing Qty. in BFT2 for ISO Prior Year`, `Revenue Previous Year`, `Revenue For Fiscal Month Previous Year`, `Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year`, `Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year`, `Current FYP VBRP`, `Prior Year FYP VBRP`, `Current Date FYP VBRP`, `Prior Year Date FYP VBRP`.

**Composite measures** (reference other measures):
`$ Difference Current Month VBRP`, `$ Difference YTD VBRP`, `ISO Rate`, `% Fcst VBRP CM`, `Current Fiscal Month Billing Qty. in FT2 for Membranes`, `Current Fiscal Month Billing Qty. in FT2 for ISO`, `Current Fiscal Month Billing Qty. in BFT2 for ISO`, `Current Fiscal Month Invoiced Revenue`, `% Fcst VBRP FM`, `Current Fiscal Month Invoiced Revenue FT2 Membranes`, `Current Fiscal Month Billing Qty. in FT2 for Membranes Split`, `Sum of Revenue in DC with Sign % difference from Revenue Previous Year`, `PercDiff PY Sales`, `PercDiff Arrow Sales`, `PercDiff PY Sales QTY`, `PercDiff Arrow Sales QTY`, `Prior Year Fiscal Month Billing Qty. in FT2 for Membranes Split`.

**Cross-table references** in this table:
- `Average Revenue per Product Family` and `Average Margin per Product Family` reference `'KRW_NA_SAP_AUSP'[Product Family]` — **`KRW_NA_SAP_AUSP` is NOT a defined table in this semantic model**. Broken reference (or column reroute via lineage).
- `Average Margin per Fiscal Year Period` references `'KRW_NA_FF_FISCALPERIOD'[Fiscal Year Period]` (fine).
- Multiple measures reference `KRW_NA_FF_CALENDAR[Date]` and `KRW_NA_FF_CALENDAR[Fiscal Year Period]`.
- `Current Month Invoice Revenue Fcst`, `YTD Invoice Revenue Fcst` (both live on `KRW-NA_FF_FORECAST`) are referenced by `% Fcst VBRP CM`, `% Fcst VBRP FM`, `$ Difference Current Month VBRP`, `$ Difference YTD VBRP`.

### `Average Revenue per Product Family`
- lineageTag: `74ac5421-b2db-4059-b51a-fb3c25332a6b`
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
```dax
AVERAGEX(
    KEEPFILTERS(VALUES('KRW_NA_SAP_AUSP'[Product Family])),
    CALCULATE(SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign]))
)
```
- Anomaly: `KRW_NA_SAP_AUSP` table not defined in this model.

### `Average Margin per Product Family`
- lineageTag: `5ee1c695-a59c-4cbb-8bf2-eee127896678`
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
```dax
AVERAGEX(
    KEEPFILTERS(VALUES('KRW_NA_SAP_AUSP'[Product Family])),
    CALCULATE(SUM('KRW_NA_SAP_VBRP'[Margin in DC]))
)
```
- Anomaly: `KRW_NA_SAP_AUSP` table not defined in this model.

### `Average Margin per Fiscal Year Period`
- lineageTag: `00a3561b-cf01-4ba2-a924-3f0e30af4683`
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
```dax
AVERAGEX(
    KEEPFILTERS(VALUES('KRW_NA_FF_FISCALPERIOD'[Fiscal Year Period])),
    CALCULATE(SUM('KRW_NA_SAP_VBRP'[Margin in DC]))
)
```

### `Sum Billing Qty. in FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `54ffc693-5371-4db5-a68c-0322a3815841`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR BillingQtyFT2Membranes =
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "Membrane")
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in FT2]
)
RETURN
IF(BillingQtyFT2Membranes = BLANK(), 0, BillingQtyFT2Membranes)
```

### `Sum Billing Qty. in BFT2 for ISO`
- formatString: `#,0`
- lineageTag: `e28088f6-61eb-47c3-b082-46ad782ddf65`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR BillingQtyBFT2ISO =
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "iso")
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in BFT2]
)
RETURN
IF(BillingQtyBFT2ISO = BLANK(), 0, BillingQtyBFT2ISO)
```

### `Margin Perc`
- formatString: `0.0%;-0.0%;0.0%`
- lineageTag: `85429bcf-41ce-4ae1-a373-93d1dcd1f123`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    SUM('KRW_NA_SAP_VBRP'[Margin in DC]),
    SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign])
)
```

### `Current Month Billing Qty. in FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `aeb5bf70-3a91-43b1-bfa9-96de9950dc6c`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "Membrane") &&
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBRP'[Billing Date]) = MONTH(TODAY())
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in FT2]
)
```

### `YTD Billing Qty. in FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `cd7ef08e-108e-4468-97d6-2b8b280e2e79`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "Membrane") &&
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY())
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in FT2]
)
```

### `Current Month Billing Qty. in BFT2 for ISO`
- formatString: `#,0`
- lineageTag: `2502025b-6a7f-42b9-a3ec-041fe0a03862`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "ISO") &&
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBRP'[Billing Date]) = MONTH(TODAY())
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in BFT2]
)
```

### `YTD Billing Qty. in BFT2 for ISO`
- formatString: `#,0`
- lineageTag: `f9bd3369-09d7-445a-856a-21d89c8d2a4e`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "ISO") &&
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY())
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in BFT2]
)
```

### `Current Month Billing Qty. in FT2 for ISO`
- formatString: `#,0`
- lineageTag: `9ade7eca-490d-403b-9e55-0f14699abcea`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "ISO") &&
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBRP'[Billing Date]) = MONTH(TODAY())
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in FT2]
)
```

### `YTD Billing Qty. in FT2 for ISO`
- formatString: `#,0`
- lineageTag: `e24a88fc-eea7-4b50-90d2-7cf1ec627f89`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        KRW_NA_SAP_VBRP,
        CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "ISO") &&
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY())
    ),
    KRW_NA_SAP_VBRP[Billing Qty. in FT2]
)
```

### `Current Month Invoiced Revenue Billing Date`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `0928a355-e51d-4157-8003-8baf1ff35f89`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_SAP_VBRP',
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBRP'[Billing Date]) = MONTH(TODAY())
    )
)
```

### `YTD Invoiced Revenue Billing Date`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `87f3e699-3280-4cab-ab92-7ca58a4a73e7`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_SAP_VBRP',
        YEAR('KRW_NA_SAP_VBRP'[Billing Date]) = YEAR(TODAY())
    )
)
```

### `$ Difference Current Month VBRP`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `c8e3531b-220b-4495-a86a-c7db72191768`
- changedProperty: Name, FormatString
```dax
[Current Fiscal Month Invoiced Revenue] - [Current Month Invoice Revenue Fcst]
```
- Dependencies: `[Current Fiscal Month Invoiced Revenue]` (this table), `[Current Month Invoice Revenue Fcst]` (on `KRW-NA_FF_FORECAST`)

### `$ Difference YTD VBRP`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `1ec76214-b798-4412-9ea4-cfb74f6cc67e`
- changedProperty: Name, FormatString
```dax
[YTD Invoiced Revenue Billing Date] - [YTD Invoice Revenue Fcst]
```
- Dependencies: `[YTD Invoiced Revenue Billing Date]` (this table), `[YTD Invoice Revenue Fcst]` (on `KRW-NA_FF_FORECAST`)

### `ISO Rate`
- formatString: `0.00`
- lineageTag: `9ce58344-1828-4680-af33-2e86c18aacab`
- changedProperty: Name, FormatString
```dax
VAR IsoRate =
[Sum Billing Qty. in BFT2 for ISO]/[Sum Billing Qty. in FT2 for Membranes]
RETURN
IF(IsoRate = BLANK(), 0, IsoRate)
```

### `% Fcst VBRP CM`
- formatString: `0%;-0%;0%`
- lineageTag: `6dd4dbf1-dc86-4064-9691-7bfdda667531`
- changedProperty: Name, FormatString
```dax
[Current Month Invoiced Revenue Billing Date]/[Current Month Invoice Revenue Fcst]
```

### `Revenue`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `d94c9b7f-0fdc-45ab-9d67-7623d89cffda`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"currencyCulture":"en-US"}`
```dax
VAR SumRevenue =
SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign])
RETURN
IF(SumRevenue = BLANK(), 0, SumRevenue)
```

### `Revenue Previous Year`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `4000af86-3d67-4807-aa81-a95fa4eb4085`
- changedProperty: Name, FormatString
```dax
VAR RevenueLastYear =
CALCULATE(
    SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign]),
    YEAR(KRW_NA_FF_CALENDAR[Date]) = YEAR(TODAY()) - 1
)
RETURN
IF(
    (KRW_NA_SAP_VBRP[Billing Year] = YEAR(TODAY()) - 1 || SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign]) = 0),
    0,
    RevenueLastYear
)
```
- Note: `KRW_NA_SAP_VBRP[Billing Year]` is a MEASURE (see below), not a column, even though the syntax looks column-like.

### `Billing Year`
- formatString: `0`
- lineageTag: `8bcc4515-7f55-4375-a099-8c47688a54c0`
- changedProperty: Name
```dax
YEAR ( SELECTEDVALUE ( 'KRW_NA_SAP_VBRP'[Billing Date] ) )
```

### `Sum Billing Qty. in FT2 for Membranes Prior Year`
- formatString: `#,0`
- lineageTag: `fbdae60c-8fca-4266-a01d-709e7f36a45a`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR BillingQtyFT2MembranesPriorYear =
CALCULATE(
    SUM(KRW_NA_SAP_VBRP[Billing Qty. in FT2]),
    CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "Membrane"),
    YEAR(KRW_NA_FF_CALENDAR[Date]) = YEAR(TODAY()) - 1
)
RETURN
IF(
    KRW_NA_SAP_VBRP[Billing Year] = YEAR(TODAY()) - 1 || SUM(KRW_NA_SAP_VBRP[Billing Qty. in FT2]) = 0,
    0,
    BillingQtyFT2MembranesPriorYear
)
```

### `Sum Billing Qty. in BFT2 for ISO Prior Year`
- formatString: `#,0`
- lineageTag: `4fdf8018-6187-49d5-88a7-7526ab030109`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR BillingQtyBFT2ISOPriorYear =
CALCULATE(
    SUM(KRW_NA_SAP_VBRP[Billing Qty. in BFT2]),
    CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "iso"),
    YEAR(KRW_NA_FF_CALENDAR[Date]) = YEAR(TODAY()) - 1
)
RETURN
IF(
    KRW_NA_SAP_VBRP[Billing Year] = YEAR(TODAY()) - 1 || SUM(KRW_NA_SAP_VBRP[Billing Qty. in BFT2]) = 0,
    0,
    BillingQtyBFT2ISOPriorYear
)
```

### `Sum Revenue in DC with sign VBRP`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `d0537acc-af41-4dcc-b49a-2c71146cd662`
- changedProperty: Name, FormatString
```dax
VAR RevDcVBRP =
SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign])
RETURN
IF(RevDcVBRP = BLANK(), 0, RevDcVBRP)
```

### `Current Fiscal Month Billing Qty. in FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `03692620-2f95-46c5-a053-b130fd521416`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueMIS = [Current FYP VBRP]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBRP'[Billing Qty. in FT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBRP'[Product Family], "Membrane"),
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = CurrentFYPValueMIS
)
```

### `Current Fiscal Month Billing Qty. in FT2 for ISO`
- formatString: `#,0`
- lineageTag: `17af32d6-6d7f-4062-a5c9-21e28257527d`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOISFT2 = [Current FYP VBRP]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBRP'[Billing Qty. in FT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBRP'[Product Family], "iso"),
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = CurrentFYPValueISOISFT2
)
```

### `Current Fiscal Month Billing Qty. in BFT2 for ISO`
- formatString: `#,0`
- lineageTag: `9cd96476-c213-49dc-924b-91f2dd80eeb4`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOISBFT2 = [Current FYP VBRP]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBRP'[Billing Qty. in BFT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBRP'[Product Family], "iso"),
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = CurrentFYPValueISOISBFT2
)
```

### `Current Fiscal Month Invoiced Revenue`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `8cfd96bf-5eb7-4165-82a4-da0461d21b9a`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_FF_CALENDAR',
        'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = [Current FYP VBRP]
    )
)
```

### `% Fcst VBRP FM`
- formatString: `0.00%;-0.00%;0.00%`
- lineageTag: `a3b684d7-c0b0-4b9b-9828-5e458ff04b3a`
- changedProperty: Name, FormatString
```dax
[Current Fiscal Month Invoiced Revenue FT2 Membranes]/[Current Month Invoice Revenue Fcst]
```

### `Revenue For Fiscal Month Previous Year`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `6d71679e-ac95-4b68-a343-d865361d9030`
- changedProperty: Name, FormatString
```dax
VAR RevenueFMLastYear =
CALCULATE(
    SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign]),
    YEAR(KRW_NA_FF_CALENDAR[Date]) = YEAR(TODAY()) - 1,
    MONTH(KRW_NA_FF_CALENDAR[Date]) = MONTH(TODAY())
)
RETURN
IF(RevenueFMLastYear = BLANK(), 0, RevenueFMLastYear)
```

### `Sum Billing Qty. in FT2 for Membranes Fiscal Month Prior Year`
- formatString: `#,0`
- lineageTag: `59ba2e03-4a6e-470c-a76c-95badaf5e140`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR BillingQtyFT2MembranesFMPriorYear =
CALCULATE(
    SUM(KRW_NA_SAP_VBRP[Billing Qty. in FT2]),
    CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "Membrane"),
    YEAR(KRW_NA_FF_CALENDAR[Date]) = YEAR(TODAY()) - 1,
    MONTH(KRW_NA_FF_CALENDAR[Date]) = MONTH(TODAY())
)
RETURN
IF(BillingQtyFT2MembranesFMPriorYear = BLANK(), 0, BillingQtyFT2MembranesFMPriorYear)
```

### `Sum Billing Qty. in BFT2 for ISO Fiscal Month Prior Year`
- formatString: `#,0`
- lineageTag: `1494ad90-e7be-4a1b-99a7-9dd59be6eb27`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR BillingQtyBFT2ISOFMPriorYear =
CALCULATE(
    SUM(KRW_NA_SAP_VBRP[Billing Qty. in BFT2]),
    CONTAINSSTRING(KRW_NA_SAP_VBRP[Product Family], "iso"),
    YEAR(KRW_NA_FF_CALENDAR[Date]) = YEAR(TODAY()) - 1,
    MONTH(KRW_NA_FF_CALENDAR[Date]) = MONTH(TODAY())
)
RETURN
IF(BillingQtyBFT2ISOFMPriorYear = BLANK(), 0, BillingQtyBFT2ISOFMPriorYear)
```

### `Current FYP VBRP` **(HELPER — heavily referenced)**
- lineageTag: `a9a961c1-6bc9-4ed9-bebb-9f0faaa54b91`
- changedProperty: Name
```dax
LOOKUPVALUE(
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period],   -- Column to return
    'KRW_NA_FF_CALENDAR'[Date], TODAY()          -- Search column & value
)
```
- Referenced by: `Current Fiscal Month Billing Qty. in FT2 for Membranes`, `Current Fiscal Month Billing Qty. in FT2 for ISO`, `Current Fiscal Month Billing Qty. in BFT2 for ISO`, `Current Fiscal Month Invoiced Revenue`, `Current Fiscal Month Invoiced Revenue FT2 Membranes`, `Current Fiscal Month Billing Qty. in FT2 for Membranes Split`, and also by `KRW-NA_FF_FORECAST` measures (`Current Month Invoice Revenue Fcst`, `Current Month Invoiced Sales Membrane sqft`, `Current Month Invoiced Sales ISO bdft`, `Current Month Invoiced Sales ISO sqft`).

### `ISO AOP - $/bdft VBRP`
- formatString: `\$#,0.000;(\$#,0.000);\$#,0.000`
- lineageTag: `393b39d9-1275-43b3-b1d1-d3fcac69e711`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"currencyCulture":"en-US"}`
```dax
SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign])/SUM('KRW_NA_SAP_VBRP'[Billing Qty. in BFT2])
```

### `Current Fiscal Month Invoiced Revenue FT2 Membranes`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `e9d58bbe-0a8c-4127-9b65-dd2dc4e8594e`
- changedProperty: Name, FormatString
```dax
VAR CurrentFMInvoicedRevMFT2 = [Current FYP VBRP]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBRP'[Revenue in DC with Sign]),
    CONTAINSSTRING('KRW_NA_SAP_VBRP'[Product Family], "Membrane"),
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = CurrentFMInvoicedRevMFT2
)
```

### `Current Fiscal Month Billing Qty. in FT2 for Membranes Split`
- formatString: `#,0`
- lineageTag: `9eb7fec9-9080-4d97-92fe-73f8f7ba4340`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueMISSplit = [Current FYP VBRP]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBRP'[Billing Qty. in FT2]),
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = CurrentFYPValueMISSplit
)
```
- Note: no `CONTAINSSTRING` filter, so this returns ALL product families in the fiscal month — the "Split" naming implies it's used with a slicer/legend.

### `Sum of Revenue in DC with Sign % difference from Revenue Previous Year`
- formatString: `0.00%;-0.00%;0.00%`
- lineageTag: `38c647d8-7c3e-478b-98fa-26e9fe65e941`
- extendedProperty MeasureTemplate: `{"version":0,"daxTemplateName":"MathematicalPercentageDifference"}`
- changedProperty: FormatString
```dax
VAR __BASELINE_VALUE = [Revenue Previous Year]
VAR __VALUE_TO_COMPARE = SUM('KRW_NA_SAP_VBRP'[Revenue in DC with Sign])
RETURN
    DIVIDE(__VALUE_TO_COMPARE - __BASELINE_VALUE, __BASELINE_VALUE)
```

### `PercDiff PY Sales`
- formatString: `0.00%;-0.00%;0.00%`
- lineageTag: `81e7f108-d79f-4432-a4ec-dbb3350f56df`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign]) - KRW_NA_SAP_VBRP[Revenue Previous Year],
    KRW_NA_SAP_VBRP[Revenue Previous Year],
    0
)
```
- Note: `KRW_NA_SAP_VBRP[Revenue Previous Year]` is a MEASURE reference using column-style syntax.

### `PercDiff Arrow Sales`
- lineageTag: `d4c74fab-07cc-4f59-b0b6-511a5c39b66e`
- changedProperty: Name
- DAX enclosed in triple-backtick fences in TMDL
```dax
VAR PercDiff =
DIVIDE(
    SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign]) - KRW_NA_SAP_VBRP[Revenue Previous Year],
    KRW_NA_SAP_VBRP[Revenue Previous Year],
    0
)
RETURN
IF(
    PercDiff > 0,
    UNICHAR(9650),  -- ▲ Up arrow
    UNICHAR(9660)   -- ▼ Down arrow
)
```

### `PercDiff PY Sales QTY`
- formatString: `0.00%;-0.00%;0.00%`
- lineageTag: `aa6e9e92-4748-4e4a-ae63-417fe5647c36`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    [Sum Billing Qty. in FT2 for Membranes] - [Sum Billing Qty. in FT2 for Membranes Prior Year],
    [Sum Billing Qty. in FT2 for Membranes Prior Year],
    0
)
```

### `PercDiff Arrow Sales QTY`
- lineageTag: `6f588f1e-cfb8-4231-89a4-6207dadfa156`
- changedProperty: Name
- DAX enclosed in triple-backtick fences in TMDL
```dax
VAR PercDiffQTY =
DIVIDE(
    [Sum Billing Qty. in FT2 for Membranes] - [Sum Billing Qty. in FT2 for Membranes Prior Year],
    [Sum Billing Qty. in FT2 for Membranes Prior Year],
    0
)
RETURN
IF(
    PercDiffQTY > 0,
    UNICHAR(9650),  -- ▲ Up arrow
    UNICHAR(9660)   -- ▼ Down arrow
)
```

### `Prior Year FYP VBRP`
- lineageTag: `2ad3a517-4865-4fc1-b45a-1a61a462cc4a`
- changedProperty: Name
```dax
LOOKUPVALUE(
    'KRW_NA_FF_CALENDAR'[Fiscal Year Period],
    'KRW_NA_FF_CALENDAR'[Date], (TODAY() - 365)
)
```

### `Current Date FYP VBRP`
- formatString: `General Date`
- lineageTag: `86c98cb2-7c8f-4b17-88df-9377577bd9fd`
- changedProperty: Name
```dax
LOOKUPVALUE(
    'KRW_NA_FF_CALENDAR'[Date],
    'KRW_NA_FF_CALENDAR'[Date], TODAY()
)
```

### `Prior Year Date FYP VBRP`
- formatString: `General Date`
- lineageTag: `0f8ad91b-20c8-4e6e-9330-40b5c1e59142`
- changedProperty: Name
```dax
LOOKUPVALUE(
    'KRW_NA_FF_CALENDAR'[Date],
    'KRW_NA_FF_CALENDAR'[Date], (TODAY() - 365)
)
```

### `Prior Year Fiscal Month Billing Qty. in FT2 for Membranes Split`
- formatString: `#,0`
- lineageTag: `84001992-2dee-4075-85ec-bc49cd5b0679`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR PYFYPValueMIS = [Prior Year FYP VBRP]
RETURN
IF(
    CALCULATE (
        SUM ( 'KRW_NA_SAP_VBRP'[Billing Qty. in FT2]),
        'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = PYFYPValueMIS
    ) = BLANK(),
    0,
    CALCULATE (
        SUM ( 'KRW_NA_SAP_VBRP'[Billing Qty. in FT2]),
        'KRW_NA_FF_CALENDAR'[Fiscal Year Period] = PYFYPValueMIS
    )
)
```

---

## `KRW_NA_SAP_VBAP OI` — order-intake-side measures (43)

**Leaf measures:**
`Margin Perc VBAP`, `Sum Order Qty. in FT2 for Membranes OI`, `Sum Order Qty. in BFT2 for ISO OI`, `Current Month Order Revenue`, `Current Month Order Revenue Doc Date`, `Current Calendar Month Order FT2 for Membranes`, `YTD Order FT2 for Membranes`, `YTD Order FT2 for ISO`, `YTD Order BFT for ISO`, `Current Calendar Month Order FT2 for ISO`, `Current Calendar Month Order BFT for ISO`, `YTD Order Revenue Doc Date`, `Current Month Membrane Order Revenue Doc Date`, `Current Month ISO Order Revenue Doc Date`, `Order Year OI`, `Revenue OI`, `Revenue Previous Year OI`, `Sum Order Qty. in FT2 for Membranes Prior Year OI`, `Sum Order Qty. in BFT2 for ISO Prior Year OI`, `Sum Revenue in DC with sign VBAP OI` (BUG — reads VBRP), `Current Fiscal Month Order FT2 for Membranes Hardcoded` (BUG — hardcoded "2026.2"), `Revenue Fiscal Month Previous Year OI`, `Sum Order Qty. in FT2 for Membranes Fiscal Month Prior Year OI`, `Sum Order Qty. in BFT2 for ISO Fiscal Month Prior Year OI`, `Current Calendar Month Order FT2 for Membranes 2`, `Current FYP VBAP OI`, `ISO AOP - $/bdft VBAP OI`.

**Composite measures:**
`ISO Rate VBAP OI`, `$ Difference Current Month`, `$ Difference YTD`, `% Fcst CM`, `Current Fiscal Month Order FT2 for ISO`, `Current Fiscal Month Order BFT for ISO`, `Current Fiscal Month Order Revenue`, `% Fcst FM`, `Current Fiscal Month Order FT2 for Membranes`, `Current Fiscal Month Order Revenue FT2 Membranes`, `PercDiff PY Orders`, `PercDiff PY Orders QTY`, `PercDiff Arrow Orders`, `PercDiff Arrow Orders QTY`, `Current Fiscal Month Order BFT for ISO Split`, `Current Fiscal Month Order FT2 for ISO Split`.

### `Margin Perc VBAP`
- formatString: `0.0%;-0.0%;0.0%`
- lineageTag: `e13b5a92-e204-405a-825f-2a6b933f8625`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    SUM('KRW_NA_SAP_VBAP OI'[Margin in DC]),
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign])
)
```

### `Sum Order Qty. in FT2 for Membranes OI`
- formatString: `#,0`
- lineageTag: `99dddc91-a96d-4ab9-800d-38ea835fdf70`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyFT2MembranesOI =
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane")
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]
)
RETURN
IF(OrderQtyFT2MembranesOI = BLANK(), 0, OrderQtyFT2MembranesOI)
```

### `Sum Order Qty. in BFT2 for ISO OI`
- formatString: `#,0`
- lineageTag: `5d4a89d9-f7ae-49a8-8abc-9d5d0c9f63c6`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyBFT2ISOOI =
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso")
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2]
)
RETURN
IF(OrderQtyBFT2ISOOI = BLANK(), 0, OrderQtyBFT2ISOOI)
```

### `ISO Rate VBAP OI`
- formatString: `0.00`
- lineageTag: `f2e3228d-520b-4c52-b5af-eba2d1603b76`
- changedProperty: Name, FormatString
```dax
VAR IsoRateVBAP =
[Sum Order Qty. in BFT2 for ISO OI]/[Sum Order Qty. in FT2 for Membranes OI]
RETURN
IF(IsoRateVBAP = BLANK(), 0, IsoRateVBAP)
```

### `Current Month Order Revenue`
- formatString: `#,0`
- lineageTag: `cbb22085-03ec-4247-ab10-24de653c4715`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_FF_CALENDAR OI'[Date]) = MONTH(TODAY())
    )
)
```

### `Current Month Order Revenue Doc Date`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `f50e4a37-74c8-453c-9700-d90c11d8428e`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    )
)
```

### `Current Calendar Month Order FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `2046df28-a62a-4896-b9cd-02c1c4c7d54f`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]
)
```

### `YTD Order FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `4bd40d23-112d-4cb3-be28-0ca9e1cd524d`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]
)
```

### `YTD Order FT2 for ISO`
- formatString: `#,0`
- lineageTag: `ffb803d8-2ba6-4be5-aa7c-32abacf1abb0`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]
)
```

### `YTD Order BFT for ISO`
- formatString: `#,0`
- lineageTag: `f9f6978d-17fa-4b28-8702-f69f1f2108af`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2]
)
```

### `Current Calendar Month Order FT2 for ISO`
- formatString: `#,0`
- lineageTag: `0723a0d0-3a86-4c38-9211-62330b3cdd2d`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]
)
```

### `Current Calendar Month Order BFT for ISO`
- formatString: `#,0`
- lineageTag: `8ab45777-87c7-42ea-820f-81557e73a768`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2]
)
```

### `YTD Order Revenue Doc Date`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `cffce8de-08fd-4a87-8669-c5713d992817`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY())
    )
)
```

### `$ Difference Current Month`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `58f0ff26-a729-4cff-a735-1b4e0278d46b`
- changedProperty: Name, FormatString
```dax
[Current Fiscal Month Order Revenue] - [Current Month Order Revenue Fcst]
```
- Dependencies: `[Current Fiscal Month Order Revenue]` (this table), `[Current Month Order Revenue Fcst]` (on `KRW_NA_FF_FORECAST_INTAKE`)

### `$ Difference YTD`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `bc9c90ab-bea2-40d9-9f6b-e19befe406d9`
- changedProperty: Name, FormatString
```dax
[YTD Order Revenue Doc Date] - [YTD Order Revenue Fcst]
```

### `% Fcst CM`
- formatString: `0%;-0%;0%`
- lineageTag: `5d488900-cc6c-4dc3-9891-8a1239539e3a`
- changedProperty: Name, FormatString
```dax
[Current Month Order Revenue Doc Date]/[Current Month Order Revenue Fcst]
```

### `Current Month Membrane Order Revenue Doc Date`
- lineageTag: `cdab22b1-7e5b-4fe9-b28b-953aa0c903c6`
- changedProperty: Name
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
- (no formatString)
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    )
)
```

### `Current Month ISO Order Revenue Doc Date`
- lineageTag: `54fff1d2-dcef-4a65-821a-4d9a88107fe9`
- changedProperty: Name
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    )
)
```

### `Order Year OI`
- formatString: `0`
- lineageTag: `3a603bf3-511c-46b6-8f45-6e3d77764b23`
- changedProperty: Name
```dax
YEAR ( SELECTEDVALUE ( 'KRW_NA_SAP_VBAP OI'[Document Date] ) )
```

### `Revenue OI`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `403f778c-ca30-4c3d-8614-5ba2e81e13e0`
- changedProperty: Name, FormatString
```dax
VAR SumRevenueOI =
SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign])
RETURN
IF(SumRevenueOI = BLANK(), 0, SumRevenueOI)
```

### `Revenue Previous Year OI`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `62aa3bb3-a278-4f13-8344-a989d41e4bcd`
- changedProperty: Name, FormatString
```dax
VAR RevenueLastYearOI =
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) - 1
)
RETURN
IF(
    ('KRW_NA_SAP_VBAP OI'[Order Year OI] = YEAR(TODAY()) - 1 || SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]) = 0),
    0,
    RevenueLastYearOI
)
```

### `Sum Order Qty. in FT2 for Membranes Prior Year OI`
- formatString: `#,0`
- lineageTag: `d5caecfc-cdc5-45a7-ba8b-1099ac783cb9`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyFT2MembranesPriorYearOI =
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
    YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) - 1
)
RETURN
IF(
    ('KRW_NA_SAP_VBAP OI'[Order Year OI] = YEAR(TODAY()) - 1 || SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]) = 0),
    0,
    OrderQtyFT2MembranesPriorYearOI
)
```

### `Sum Order Qty. in BFT2 for ISO Prior Year OI`
- formatString: `#,0`
- lineageTag: `206bf582-9504-4a10-94bf-812e6142fdb3`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyBFT2ISOPriorYearOI =
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
    YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) - 1
)
RETURN
IF(
    ('KRW_NA_SAP_VBAP OI'[Order Year OI] = YEAR(TODAY()) - 1 || SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2]) = 0),
    0,
    OrderQtyBFT2ISOPriorYearOI
)
```
- Note: filters on `YEAR('KRW_NA_SAP_VBAP OI'[Document Date])` here — inconsistent with sibling that filters `YEAR('KRW_NA_FF_CALENDAR OI'[Date])`.

### `Sum Revenue in DC with sign VBAP OI` **BUG**
- lineageTag: `4dc98f09-7bc0-4a28-be29-956fc6bb6a81`
- changedProperty: Name
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
```dax
VAR RevDcVBAPOI =
SUM(KRW_NA_SAP_VBRP[Revenue in DC with Sign])
RETURN
IF(RevDcVBAPOI = BLANK(), 0, RevDcVBAPOI)
```
- **BUG:** Measure is defined on `KRW_NA_SAP_VBAP OI` but sums `KRW_NA_SAP_VBRP` (the invoice table). Almost certainly a copy-paste bug from `Sum Revenue in DC with sign VBRP`.

### `Current Fiscal Month Order FT2 for Membranes Hardcoded` **BUG**
- formatString: `#,0`
- lineageTag: `de9ca85e-9561-46f1-adc1-3a25cb9a93f3`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = "2026.2"
)
```
- **HARDCODED VALUE:** literal `"2026.2"` will stop matching current data as soon as the fiscal calendar moves. Note the format is `.2` here, but the sibling FORECAST-side hardcode is `.02` — inconsistent.

### `Current Fiscal Month Order FT2 for ISO`
- formatString: `#,0`
- lineageTag: `57d23a30-1e73-47eb-85a4-e3f708be36d2`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOOIFT2 = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = CurrentFYPValueISOOIFT2
)
```

### `Current Fiscal Month Order BFT for ISO`
- formatString: `#,0`
- lineageTag: `b4fd3674-5055-4ac3-bb4b-a3e1406df39f`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOOIBFT2 = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = CurrentFYPValueISOOIBFT2
)
```

### `Current Fiscal Month Order Revenue`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `b1ef7bd7-6e56-4cdf-a588-b1af43629b0e`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = [Current FYP VBAP OI]
    )
)
```

### `% Fcst FM`
- formatString: `0%;-0%;0%`
- lineageTag: `25c62c01-0fc0-48cc-87bf-10b1e4a8319a`
- changedProperty: Name, FormatString
```dax
[Current Fiscal Month Order Revenue]/[Current Month Order Revenue Fcst]
```

### `Revenue Fiscal Month Previous Year OI`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `83236c81-2f96-4d70-837e-c36e7a4cc548`
- changedProperty: Name, FormatString
```dax
VAR RevenueFMLastYearOI =
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]),
    YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) - 1,
    MONTH('KRW_NA_FF_CALENDAR OI'[Date]) = MONTH(TODAY())
)
RETURN
IF(RevenueFMLastYearOI = BLANK(), 0, RevenueFMLastYearOI)
```

### `Sum Order Qty. in FT2 for Membranes Fiscal Month Prior Year OI`
- formatString: `#,0`
- lineageTag: `d48d12a8-144f-4630-898f-cb45beba6496`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyFT2MembranesFMPriorYearOI =
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
    YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) - 1,
    MONTH('KRW_NA_FF_CALENDAR OI'[Date]) = MONTH(TODAY())
)
RETURN
IF(OrderQtyFT2MembranesFMPriorYearOI = BLANK(), 0, OrderQtyFT2MembranesFMPriorYearOI)
```

### `Sum Order Qty. in BFT2 for ISO Fiscal Month Prior Year OI`
- formatString: `#,0`
- lineageTag: `477baf64-a1d0-4bbd-936d-84c84d7e74a2`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyBFT2ISOFMPriorYearOI =
CALCULATE(
    SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2]),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
    YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) - 1,
    MONTH('KRW_NA_FF_CALENDAR OI'[Date]) = MONTH(TODAY())
)
RETURN
IF(OrderQtyBFT2ISOFMPriorYearOI = BLANK(), 0, OrderQtyBFT2ISOFMPriorYearOI)
```

### `Current Fiscal Month Order FT2 for Membranes`
- formatString: `#,0`
- lineageTag: `4a24f731-5099-47cc-8139-7649f0b6a5a2`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueMOI = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = CurrentFYPValueMOI
)
```

### `Current Calendar Month Order FT2 for Membranes 2` **DUPLICATE**
- lineageTag: `fed23815-cbb2-402a-a2b8-79da4cc3c7e7`
- changedProperty: Name
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
- (no formatString)
```dax
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP OI',
        CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane") &&
        YEAR('KRW_NA_SAP_VBAP OI'[Document Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_SAP_VBAP OI'[Document Date]) = MONTH(TODAY())
    ),
    'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2]
)
```
- **DUPLICATE:** identical DAX body to `Current Calendar Month Order FT2 for Membranes`. Only difference is this one has no `formatString`. Candidate for cleanup.

### `Current FYP VBAP OI` **(HELPER — heavily referenced)**
- lineageTag: `c8af07df-23d3-4bf8-92e0-44020b201613`
- changedProperty: Name
```dax
LOOKUPVALUE(
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period],   -- Column to return
    'KRW_NA_FF_CALENDAR OI'[Date], TODAY()          -- Search column & value
)
```
- Referenced by: `Current Fiscal Month Order FT2 for ISO`, `Current Fiscal Month Order BFT for ISO`, `Current Fiscal Month Order Revenue`, `Current Fiscal Month Order FT2 for Membranes`, `Current Fiscal Month Order Revenue FT2 Membranes`, `Current Fiscal Month Order BFT for ISO Split`, `Current Fiscal Month Order FT2 for ISO Split`, and cross-table by `KRW_NA_FF_FORECAST_INTAKE` measures `Current Month Order Revenue Fcst`, `Current Fiscal Month Sales Membrane sqft`, `Current Fiscal Month Sales ISO sqft`, `Current Fiscal Month Sales ISO bdft`.

### `ISO AOP - $/bdft VBAP OI`
- formatString: `\$#,0.000;(\$#,0.000);\$#,0.000`
- lineageTag: `09945c82-6982-4a9b-b04c-603698227be2`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"currencyCulture":"en-US"}`
```dax
SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign])/SUM('KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2])
```

### `Current Fiscal Month Order Revenue FT2 Membranes`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `a9ee125a-1dc9-4e7e-b29c-dccfdddf3949`
- changedProperty: Name, FormatString
```dax
VAR CurrentFYPValueMOIFT2 = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = CurrentFYPValueMOIFT2
)
```

### `PercDiff PY Orders`
- formatString: `0.00%;-0.00%;0.00%`
- lineageTag: `9d371853-43c9-42d1-9141-68e9f798ebd4`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]) - 'KRW_NA_SAP_VBAP OI'[Revenue Previous Year OI],
    'KRW_NA_SAP_VBAP OI'[Revenue Previous Year OI],
    0
)
```
- Note: `'KRW_NA_SAP_VBAP OI'[Revenue Previous Year OI]` is a MEASURE reference in column syntax.

### `PercDiff PY Orders QTY`
- formatString: `0.00%;-0.00%;0.00%`
- lineageTag: `d33a7c3e-cf3d-4294-bff5-712ea736adde`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    [Sum Order Qty. in FT2 for Membranes OI] - [Sum Order Qty. in FT2 for Membranes Prior Year OI],
    [Sum Order Qty. in FT2 for Membranes Prior Year OI],
    0
)
```

### `PercDiff Arrow Orders`
- lineageTag: `914240c4-17b2-4083-93ca-7ae252b411f0`
- changedProperty: Name
- DAX enclosed in triple-backtick fences in TMDL
```dax
VAR PercDiff =
DIVIDE(
    SUM('KRW_NA_SAP_VBAP OI'[Revenue in DC with Sign]) - 'KRW_NA_SAP_VBAP OI'[Revenue Previous Year OI],
    'KRW_NA_SAP_VBAP OI'[Revenue Previous Year OI],
    0
)
RETURN
IF(
    PercDiff > 0,
    UNICHAR(9650),  -- ▲ Up arrow
    UNICHAR(9660)   -- ▼ Down arrow
)
```

### `PercDiff Arrow Orders QTY`
- lineageTag: `c9f9338a-c7e1-4356-b914-b31e10180041`
- changedProperty: Name
- DAX enclosed in triple-backtick fences in TMDL
```dax
VAR PercDiff =
DIVIDE(
    [Sum Order Qty. in FT2 for Membranes OI] - [Sum Order Qty. in FT2 for Membranes Prior Year OI],
    [Sum Order Qty. in FT2 for Membranes Prior Year OI],
    0
)
RETURN
IF(
    PercDiff > 0,
    UNICHAR(9650),  -- ▲ Up arrow
    UNICHAR(9660)   -- ▼ Down arrow
)
```

### `Current Fiscal Month Order BFT for ISO Split`
- formatString: `#,0`
- lineageTag: `270e5e86-d1ae-4660-9277-5fc24543de32`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOOIBFT2Split = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Order Qty. in BFT2] ),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = CurrentFYPValueISOOIBFT2Split
)
```
- Note: no product-family filter — returns all product families in fiscal month.

### `Current Fiscal Month Order FT2 for ISO Split`
- formatString: `#,0`
- lineageTag: `a5228641-7759-4522-a92b-769a99925e6b`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOOIFT2Split = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_SAP_VBAP OI'[Order Qty. in FT2] ),
    'KRW_NA_FF_CALENDAR OI'[Fiscal Year Period] = CurrentFYPValueISOOIFT2Split
)
```

---

## `KRW_NA_SAP_VBAP SB` — sales-backlog measures (5)

**Leaf measures:** `Margin Perc VBAP SB`, `Sum Order Qty. in BFT2 for ISO SB`, `Sum Order Qty. in FT2 for Membranes SB`, `Total Backlog $`.
**Composite:** `ISO Rate VBAP SB`.

### `Margin Perc VBAP SB`
- formatString: `0.0%;-0.0%;0.0%`
- lineageTag: `8bd11b42-a80b-4f45-93c4-b1789713ccb8`
- changedProperty: Name, FormatString
```dax
DIVIDE(
    SUM('KRW_NA_SAP_VBAP SB'[Margin in DC]),
    SUM('KRW_NA_SAP_VBAP SB'[Revenue in DC with Sign])
)
```

### `Sum Order Qty. in BFT2 for ISO SB`
- lineageTag: `c177d6dd-1f9e-437c-a2dd-988f9d969b8c`
- changedProperty: Name
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`
- (no formatString)
```dax
VAR OrderQtyBFT2ISOSB =
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP SB',
        CONTAINSSTRING('KRW_NA_SAP_VBAP SB'[Product Family], "iso")
    ),
    'KRW_NA_SAP_VBAP SB'[Order Qty. in BFT2]
)
RETURN
IF(OrderQtyBFT2ISOSB = BLANK(), 0, OrderQtyBFT2ISOSB)
```

### `Sum Order Qty. in FT2 for Membranes SB`
- formatString: `#,0`
- lineageTag: `58de1384-8722-46db-9f7f-1900133b3ef1`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR OrderQtyFT2MembranesSB =
SUMX(
    FILTER(
        'KRW_NA_SAP_VBAP SB',
        CONTAINSSTRING('KRW_NA_SAP_VBAP SB'[Product Family], "Membrane")
    ),
    'KRW_NA_SAP_VBAP SB'[Order Qty. in FT2]
)
RETURN
IF(OrderQtyFT2MembranesSB = BLANK(), 0, OrderQtyFT2MembranesSB)
```

### `ISO Rate VBAP SB`
- formatString: `0.00`
- lineageTag: `c35c78ed-dce4-4c93-8b04-6c913d1488c6`
- changedProperty: Name, FormatString
```dax
VAR IsoRateVBAPSB =
[Sum Order Qty. in BFT2 for ISO SB]/[Sum Order Qty. in FT2 for Membranes SB]
RETURN
IF(IsoRateVBAPSB = BLANK(), 0, IsoRateVBAPSB)
```

### `Total Backlog $`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `09a68fd1-9217-44e7-92de-43a608d12217`
- changedProperty: Name, FormatString
- DAX enclosed in triple-backtick fences in TMDL
```dax
VAR TotalBacklog =
SUM('KRW_NA_SAP_VBAP SB'[Revenue in DC with Sign])
RETURN
IF(TotalBacklog = Blank(), 0, TotalBacklog)
```

---

## `KRW-NA_FF_FORECAST` — invoiced forecast measures (10)

Confirmation of v1: `odata-production-model-inventory.md` line 44 stated 10 measures on this table. Verified.

**Cross-table refs:** every non-YTD measure filters on `[Current FYP VBRP]` (helper measure on `KRW_NA_SAP_VBRP`). YTD measures filter on `KRW_NA_FF_CALENDAR[Date]`.

### `ISO Rate Fcst`
- formatString: `#,0.00`
- lineageTag: `389772dd-01a6-4345-93d9-05db59d094c2`
- extendedProperty MeasureTemplate: `{"version":0,"daxTemplateName":"MathematicalDivision"}`
- changedProperty: FormatString, Name
```dax
VAR IsoRateFcst =
DIVIDE(
    SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
    SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft])
)
RETURN
IF(IsoRateFcst = BLANK(), 0, IsoRateFcst)
```

### `Current Month Invoice Revenue Fcst`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `0c1893cc-588b-43da-8f6a-9231eb973885`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales $]),
    FILTER(
        'KRW-NA_FF_FORECAST',
        'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]
    )
)
```

### `Current Month Invoiced Sales Membrane sqft`
- formatString: `#,0`
- lineageTag: `dd4a4386-e4f2-4a68-9422-5a6324379fa9`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft]),
    FILTER(
        'KRW-NA_FF_FORECAST',
        'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]
    )
)
```

### `YTD Invoiced Sales Membrane sqft`
- formatString: `#,0`
- lineageTag: `ecde9692-ad21-44ad-8805-750485382c57`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft]),
    FILTER(
        'KRW_NA_FF_CALENDAR',
        YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())
    )
)
```

### `Current Month Invoiced Sales ISO bdft`
- formatString: `#,0`
- lineageTag: `1eb6b801-e763-4ae0-974d-f1a29ec138f1`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
    FILTER(
        'KRW-NA_FF_FORECAST',
        'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]
    )
)
```

### `YTD Invoiced Sales ISO bdft`
- formatString: `#,0`
- lineageTag: `e157e68c-b163-44ad-81e4-b4746899c3f7`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
    FILTER(
        'KRW_NA_FF_CALENDAR',
        YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())
    )
)
```

### `Current Month Invoiced Sales ISO sqft`
- formatString: `#,0`
- lineageTag: `4e0ded2b-28c5-4cdf-bcab-ceaca2edda3e`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales ISO sqft]),
    FILTER(
        'KRW-NA_FF_FORECAST',
        'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]
    )
)
```

### `YTD Invoiced Sales ISO sqft`
- formatString: `#,0`
- lineageTag: `e2281cd7-8040-46a1-bff0-385913725fc7`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales ISO sqft]),
    FILTER(
        'KRW_NA_FF_CALENDAR',
        YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())
    )
)
```

### `YTD Invoice Revenue Fcst`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `cfdf5acd-9e78-4f07-9e97-8d1480f46544`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales $]),
    FILTER(
        'KRW_NA_FF_CALENDAR',
        YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())
    )
)
```

### `Current Month Invoiced Sales ISO sqft FM` **HARDCODED**
- formatString: `#,0`
- lineageTag: `3e38010e-9a14-4d25-b52d-e643497329f5`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW-NA_FF_FORECAST'[Sales ISO sqft]),
    'KRW-NA_FF_FORECAST'[Fiscal Year Period Sorted] = "2026.02"
)
```
- **HARDCODED VALUE:** literal `"2026.02"`. Note also uses `[Fiscal Year Period Sorted]` (different column from `[Fiscal Year Period]` used elsewhere on this table).

---

## `KRW_NA_FF_FORECAST_INTAKE` — intake forecast measures (10)

**v1 UNDERCOUNT:** `odata-production-model-inventory.md` line 135 says 7 measures. Actual grep says 10. Missing from v1: probably `Current Fiscal Month Sales ISO bdft`, `YTD Sales Membrane sqft`, and one other — verify against v1 doc.

**Cross-table refs:** the three `Current Fiscal Month Sales *` measures cross-reference `'KRW_NA_SAP_VBAP OI'[Product Family]` inside their `CONTAINSSTRING` filter — an unusual cross-table dependency that must be preserved during any port to AWIP.

### `ISO Rate Fcst VBAP`
- formatString: `0.00`
- lineageTag: `da6abc2a-26c4-4b6d-a576-9515ffeba5c5`
- changedProperty: Name, FormatString
```dax
VAR IsoRateFcstVBAP =
DIVIDE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales Membrane sqft])
)
RETURN
IF(IsoRateFcstVBAP = BLANK(), 0, IsoRateFcstVBAP)
```

### `Current Month Order Revenue Fcst`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `b538d943-51c2-46ca-9ce9-dda2d8f7b483`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales $]),
    FILTER(
        'KRW_NA_FF_FORECAST_INTAKE',
        'KRW_NA_FF_FORECAST_INTAKE'[Fiscal Year Period] = [Current FYP VBAP OI]
    )
)
```

### `Current Fiscal Month Sales Membrane sqft` **CROSS-TABLE**
- formatString: `#,0`
- lineageTag: `d085e6fa-ead8-4eda-99c7-12a0522accaf`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueMOIFT2Fcst = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_FF_FORECAST_INTAKE'[Sales Membrane sqft] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "Membrane"),
    KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period] = CurrentFYPValueMOIFT2Fcst
)
```
- **CROSS-TABLE FILTER:** `CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], ...)` — filters INTAKE fact by OI dimension. Requires an active relationship between the two.

### `Current Fiscal Month Sales ISO sqft` **CROSS-TABLE**
- formatString: `#,0`
- lineageTag: `7e11aebb-82a3-46f3-ae32-e2d6dc0d2cea`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOOIFT2Fcst = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_FF_FORECAST_INTAKE'[Sales ISO sqft] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
    KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period] = CurrentFYPValueISOOIFT2Fcst
)
```

### `Current Month Sales ISO bdft`
- formatString: `#,0`
- lineageTag: `f394ca2f-918a-4ae5-ad29-15fe87b8e743`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY()) &&
        MONTH('KRW_NA_FF_CALENDAR OI'[Date]) = MONTH(TODAY())
    )
)
```

### `YTD Sales ISO bdft`
- formatString: `#,0`
- lineageTag: `1af14c14-e46b-4aab-97c1-bf11dfe51fdc`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY())
    )
)
```

### `YTD Sales ISO sqft`
- formatString: `#,0`
- lineageTag: `805007f9-83c1-4d91-bdfe-2e6935af9d19`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO sqft]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY())
    )
)
```

### `YTD Sales Membrane sqft`
- formatString: `#,0`
- lineageTag: `eaaf9cb5-a5ad-4592-bdc8-f4e6a6b4228e`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
CALCULATE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales Membrane sqft]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY())
    )
)
```

### `YTD Order Revenue Fcst`
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `3bb0fb78-a927-4456-a5fe-803d2924fd2e`
- changedProperty: Name, FormatString
```dax
CALCULATE(
    SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales $]),
    FILTER(
        'KRW_NA_FF_CALENDAR OI',
        YEAR('KRW_NA_FF_CALENDAR OI'[Date]) = YEAR(TODAY())
    )
)
```

### `Current Fiscal Month Sales ISO bdft` **CROSS-TABLE**
- formatString: `#,0`
- lineageTag: `1ff1d92a-0136-405e-8e9e-c5816f6f562d`
- changedProperty: Name, FormatString
- annotation: `PBI_FormatHint = {"isDecimal":true}`
```dax
VAR CurrentFYPValueISOOIBFT2Fcst = [Current FYP VBAP OI]
RETURN
CALCULATE (
    SUM ( 'KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft] ),
    CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "iso"),
    KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period] = CurrentFYPValueISOOIBFT2Fcst
)
```

---

## Consolidated hardcoded-literal inventory

| Measure | Table | Literal | Column |
|---|---|---|---|
| `Current Fiscal Month Order FT2 for Membranes Hardcoded` | `KRW_NA_SAP_VBAP OI` | `"2026.2"` | `KRW_NA_FF_CALENDAR OI[Fiscal Year Period]` |
| `Current Month Invoiced Sales ISO sqft FM` | `KRW-NA_FF_FORECAST` | `"2026.02"` | `KRW-NA_FF_FORECAST[Fiscal Year Period Sorted]` |

Note the two literals differ in month format (`.2` vs `.02`), suggesting they filter different physical columns with different sort keys.

---

## Consolidated cross-`_SAP_` reference inventory (measures that will need re-pointing to Datasphere)

| Measure | Home table | Foreign table referenced |
|---|---|---|
| `Sum Revenue in DC with sign VBAP OI` | `KRW_NA_SAP_VBAP OI` | `KRW_NA_SAP_VBRP` (BUG) |
| `Current Fiscal Month Sales Membrane sqft` | `KRW_NA_FF_FORECAST_INTAKE` | `KRW_NA_SAP_VBAP OI` |
| `Current Fiscal Month Sales ISO sqft` | `KRW_NA_FF_FORECAST_INTAKE` | `KRW_NA_SAP_VBAP OI` |
| `Current Fiscal Month Sales ISO bdft` | `KRW_NA_FF_FORECAST_INTAKE` | `KRW_NA_SAP_VBAP OI` |
| `Average Revenue per Product Family` | `KRW_NA_SAP_VBRP` | `KRW_NA_SAP_AUSP` (broken/undefined) |
| `Average Margin per Product Family` | `KRW_NA_SAP_VBRP` | `KRW_NA_SAP_AUSP` (broken/undefined) |

Plus every FORECAST-side measure that references `[Current FYP VBRP]` (VBRP measure) or `[Current FYP VBAP OI]` (VBAP OI measure) — these are helper-measure references, not column references, but still cross the table boundary.

---

## Duplicate / near-duplicate measure inventory (candidates for cleanup)

| Measure A | Measure B | Difference |
|---|---|---|
| `Current Calendar Month Order FT2 for Membranes` | `Current Calendar Month Order FT2 for Membranes 2` | Identical DAX; `2` lacks `formatString`. Same table (`KRW_NA_SAP_VBAP OI`). |
| `Sum of Revenue in DC with Sign % difference from Revenue Previous Year` | `PercDiff PY Sales` | Very similar intent (both compute (current - baseline)/baseline); the "template" version subtracts explicit baseline var; `PercDiff PY Sales` uses column-syntax measure reference. |

---

## Sign-off

- Total measures inventoried: **113**
- Tables scanned for measures: **all 60 TMDL files** in the production semantic-model tables directory (LocalDateTable_*.tmdl skipped by design).
- v1 undercount identified: **93 measures** were missed by the v1 inventory across the three `_SAP_` tables, plus **3 measures** were undercounted on `KRW_NA_FF_FORECAST_INTAKE` (v1 said 7, actual is 10).
- v1 accuracy re-confirmed for `KRW-NA_FF_FORECAST` = 10 measures.

# Production Measures — Verbatim

**Source:** `production-reference/Amalgamated Sales Production.SemanticModel/definition/tables/`
**Count:** 19 measures — 8 in `SAP_SD_HL_BillingDocumentItem_V2`, 11 in `SAP_SD_HL_SalesDocumentItem_V2`.

All DAX below is copied byte-for-byte from the production TMDL. Do NOT modify these in Phase 5 without documented business approval.

---

## `SAP_SD_HL_BillingDocumentItem_V2` measures (8)

### 1. Sum Billing Qty. in FT2 for Membranes
- formatString: `#,0`
- lineageTag: `0f303726-f02f-45e8-85b4-9d3588ddfa65`
- annotation: `PBI_FormatHint = {"isDecimal":true}`

```dax
VAR BillingQtyFT2Membranes =
SUMX(
    FILTER(
        SAP_SD_HL_BillingDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_BillingDocumentItem_V2[FC Product Group], "TPO")
    ),
    SAP_SD_HL_BillingDocumentItem_V2[Billing_Quantity_in_FT2]
)
RETURN
IF(
    BillingQtyFT2Membranes = BLANK(),
    0,
    BillingQtyFT2Membranes
)
```

**Depends on columns:** `FC Product Group` (contains "TPO"), `Billing_Quantity_in_FT2`.

---

### 2. Sum Billing Qty. in BFT2 for ISO 2
- formatString: `#,0`
- lineageTag: `374a835e-c332-4beb-a4c2-9c8fd2898a1b`
- annotation: `PBI_FormatHint = {"isDecimal":true}`

```dax
VAR BillingQtyBFT2ISO =
SUMX(
    FILTER(
        SAP_SD_HL_BillingDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_BillingDocumentItem_V2[FC Product Group], "iso")
    ),
    SAP_SD_HL_BillingDocumentItem_V2[Billing_Quantity_with_Signs]
)
RETURN
IF(
    BillingQtyBFT2ISO = BLANK(),
    0,
    BillingQtyBFT2ISO
)
```

**Depends on columns:** `FC Product Group` (contains "iso" — lowercase, case-insensitive match), `Billing_Quantity_with_Signs`.

**Note:** This is a *variant* of "Sum Billing Qty. in BFT2 for ISO" that uses `Billing_Quantity_with_Signs` instead of `Billing_Quantity_in__BFT2`. Two similarly named measures with different underlying columns — treat as distinct.

---

### 3. ISO Rate IS
- lineageTag: `24145154-956a-4c27-a116-3bccbe772af7`
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`

```dax
VAR IsoRateIS =
[Sum Billing Qty. in BFT2 for ISO]/[Sum Billing Qty. in FT2 for Membranes]
RETURN
IF(
    IsoRateIS = BLANK(),
    0,
    IsoRateIS
)
```

**Depends on measures:** `[Sum Billing Qty. in BFT2 for ISO]` (#8 below), `[Sum Billing Qty. in FT2 for Membranes]` (#1 above).
**Ultimate columns:** `FC Product Group`, `Billing_Quantity_in__BFT2` (double underscore), `Billing_Quantity_in_FT2`.

---

### 4. ISO Rate Fcst IS
- lineageTag: `3950f1ba-2e87-4ac9-b1a0-772c5fa71bff`
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`

```dax
VAR IsoRateFcstIS =
DIVIDE(
    SUM(SAP_SD_HL_BillingDocumentItem_V2[ForecastSalesBDFT]),
    ([Sum Fcst Sales in FT2 for Membranes])
)
RETURN
IF(
    IsoRateFcstIS = BLANK(),
    0,
    IsoRateFcstIS
)
```

**Depends on:** `ForecastSalesBDFT` column, measure `[Sum Fcst Sales in FT2 for Membranes]` (#7).

---

### 5. Sum Revenue in DC with sign IS
- formatString: `\$#,0;(\$#,0);\$#,0`
- lineageTag: `d99635c7-2936-4a53-9c07-cd06ac112690`

```dax
VAR RevDcIS =
SUM(SAP_SD_HL_BillingDocumentItem_V2[Revenue])
RETURN
IF(
    RevDcIS = BLANK(),
    0,
    RevDcIS
)
```

**Depends on:** `Revenue` column. Simple wrapper that turns BLANK into 0.

---

### 6. ISO AOP - $/bdft IS
- formatString: `\$#,0.00;(\$#,0.00);\$#,0.00`
- lineageTag: `88e7cc35-d088-41fd-b343-9013a834af86`
- annotation: `PBI_FormatHint = {"currencyCulture":"en-US"}`

```dax
SUM(SAP_SD_HL_BillingDocumentItem_V2[Revenue])/SUM(SAP_SD_HL_BillingDocumentItem_V2[Billing_Quantity_with_Signs])
```

**Depends on:** `Revenue`, `Billing_Quantity_with_Signs`. AOP = Average Order Price (or Actual Operating Price). No BLANK guard — will error/blank if denominator = 0.

---

### 7. Sum Fcst Sales in FT2 for Membranes
- formatString: `0`
- lineageTag: `3e0b610e-d1b5-496e-b009-2c77362e1a12`

```dax
VAR FcstSalesQtyFT2Membranes =
SUMX(
    FILTER(
        SAP_SD_HL_BillingDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_BillingDocumentItem_V2[FC Product Group], "TPO")
    ),
    SAP_SD_HL_BillingDocumentItem_V2[ForecastSalesSQFT]
)
RETURN
IF(
    FcstSalesQtyFT2Membranes = BLANK(),
    0,
    FcstSalesQtyFT2Membranes
)
```

**Depends on:** `FC Product Group` (contains "TPO"), `ForecastSalesSQFT`.

---

### 8. Sum Billing Qty. in BFT2 for ISO
- lineageTag: `d27e9636-2a18-487a-b964-426f33289710`
- annotation: `PBI_FormatHint = {"isGeneralNumber":true}`

```dax
VAR BillingQtyBFT2ISO =
SUMX(
    FILTER(
        SAP_SD_HL_BillingDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_BillingDocumentItem_V2[FC Product Group], "iso")
    ),
    SAP_SD_HL_BillingDocumentItem_V2[Billing_Quantity_in__BFT2]
)
RETURN
IF(
    BillingQtyBFT2ISO = BLANK(),
    0,
    BillingQtyBFT2ISO
)
```

**Depends on columns:** `FC Product Group` (contains "iso"), `Billing_Quantity_in__BFT2` (**note double underscore in column name**).

---

## `SAP_SD_HL_SalesDocumentItem_V2` measures (11)

### 1. ISO AOP - $/bdft OI
- formatString: `\$#,0.00;(\$#,0.00);\$#,0.00`
- lineageTag: `69f73e56-0b0e-418d-ad27-dea25f62f963`
- annotation: `PBI_FormatHint = {"currencyCulture":"en-US"}`

```dax
SUM(SAP_SD_HL_SalesDocumentItem_V2[Revenue_Order_Intake])/SUM(SAP_SD_HL_SalesDocumentItem_V2[Order_Quantity_in_BFT2])
```

**Depends on:** `Revenue_Order_Intake`, `Order_Quantity_in_BFT2`.

---

### 2. ISO Rate Fcst OI
- lineageTag: `b5e2dffc-65da-4d73-8b4f-3d1afb58c127`

```dax
VAR IsoRateFcstOI =
DIVIDE(
    SUM(SAP_SD_HL_SalesDocumentItem_V2[ForecastSalesBDFT]),
    [Sum Fcst Order Qty. in FT2 for Membranes OI]
)
RETURN
IF(
    IsoRateFcstOI = BLANK(),
    0,
    IsoRateFcstOI
)
```

**Depends on:** `ForecastSalesBDFT` column, measure `[Sum Fcst Order Qty. in FT2 for Membranes OI]` (#5).

---

### 3. ISO Rate OI
- lineageTag: `23d43a48-233d-4061-a092-4af6672843db`

```dax
VAR IsoRateOI =
[Sum Order Qty. in BFT2 for ISO OI]/[Sum Order Qty. in FT2 for Membranes OI]
RETURN
IF(
    IsoRateOI = BLANK(),
    0,
    IsoRateOI
)
```

**Depends on:** measures #6 and #8.

---

### 4. ISO Rate SB
- lineageTag: `f934cb04-9cb2-4455-b966-2ec5d0e17c56`

```dax
VAR IsoRateVBAPSB =
[Sum Order Qty. in BFT2 for ISO SB]/[Sum Order Qty. in FT2 for Membranes SB]
RETURN
IF(
    IsoRateVBAPSB = BLANK(),
    0,
    IsoRateVBAPSB
)
```

**Depends on:** measures #7 and #9. `SB` likely = Sales Backlog / Standing Backlog. `VBAP` is the SAP table name for Sales Document Item (hint from variable naming).

---

### 5. Sum Fcst Order Qty. in FT2 for Membranes OI
- formatString: `0`
- lineageTag: `5c3dbf78-2d79-4e18-85a6-5f9b80442434`

```dax
VAR FcstOrderQtyFT2MembranesOI =
SUMX(
    FILTER(
        SAP_SD_HL_SalesDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_SalesDocumentItem_V2[FC Product Group], "TPO")
    ),
    SAP_SD_HL_SalesDocumentItem_V2[ForecastSalesSQFT]
)
RETURN
IF(
    FcstOrderQtyFT2MembranesOI = BLANK(),
    0,
    FcstOrderQtyFT2MembranesOI
)
```

---

### 6. Sum Order Qty. in BFT2 for ISO OI
- lineageTag: `cdc5faf8-08dd-4fee-b727-d955357fe8ed`

```dax
VAR OrderQtyBFT2ISOOI =
SUMX(
    FILTER(
        SAP_SD_HL_SalesDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_SalesDocumentItem_V2[Product Family], "iso")
    ),
    SAP_SD_HL_SalesDocumentItem_V2[Requested_Quantity_in_BFT]
)
RETURN
IF(
    OrderQtyBFT2ISOOI = BLANK(),
    0,
    OrderQtyBFT2ISOOI
)
```

**Note:** filters on `Product Family` (not `FC Product Group`) with lowercase "iso".

---

### 7. Sum Order Qty. in BFT2 for ISO SB
- lineageTag: `d4c8559f-4ee1-452a-815b-c1130de97959`

```dax
VAR OrderQtyBFT2ISOSB =
SUMX(
    FILTER(
        'SAP_SD_HL_SalesDocumentItem_V2',
        CONTAINSSTRING(SAP_SD_HL_SalesDocumentItem_V2[FC Product Group], "ISO")
    ),
    SAP_SD_HL_SalesDocumentItem_V2[Requested_Quantity_in_BFT]
)
RETURN
IF(
    OrderQtyBFT2ISOSB = BLANK(),
    0,
    OrderQtyBFT2ISOSB
)
```

**Note:** filters on `FC Product Group` with "ISO" (uppercase). Case-insensitive match via CONTAINSSTRING.

---

### 8. Sum Order Qty. in FT2 for Membranes OI
- lineageTag: `a740fc2b-7c1b-4934-96ae-3ef9a3d9f2a1`

```dax
VAR OrderQtyFT2MembranesOI =
SUMX(
    FILTER(
        SAP_SD_HL_SalesDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_SalesDocumentItem_V2[Product Family], "Membrane")
    ),
    SAP_SD_HL_SalesDocumentItem_V2[Order_Quantity_in_FT2]
)
RETURN
IF(
    OrderQtyFT2MembranesOI = BLANK(),
    0,
    OrderQtyFT2MembranesOI
)
```

---

### 9. Sum Order Qty. in FT2 for Membranes SB
- lineageTag: `b2ad524e-d250-422c-85b3-a729b40d6816`

```dax
VAR OrderQtyFT2MembranesSB =
SUMX(
    FILTER(
        SAP_SD_HL_SalesDocumentItem_V2,
        CONTAINSSTRING(SAP_SD_HL_SalesDocumentItem_V2[FC Product Group], "TPO")
    ),
    SAP_SD_HL_SalesDocumentItem_V2[RequestedQuantityInBaseUnit]
)
RETURN
IF(
    OrderQtyFT2MembranesSB = BLANK(),
    0,
    OrderQtyFT2MembranesSB
)
```

**Note:** uses `RequestedQuantityInBaseUnit` (SAP standard camelCase, single word), NOT `Requested_Quantity_in_BFT`.

---

### 10. Total Backlog $
- formatString: `\$#,0.###############;(\$#,0.###############);\$#,0.###############`
- lineageTag: `9f32114d-cb95-47ee-9dca-86132c5120fe`

**Note:** DAX body is wrapped in triple backticks in the TMDL, which is TMDL's way of escaping a multi-line raw string. The actual DAX is:

```dax
VAR TotalBacklog =
SUM(SAP_SD_HL_SalesDocumentItem_V2[Revenue_Backlog])
RETURN
IF(TotalBacklog = Blank(),
0,
TotalBacklog)
```

**Depends on:** `Revenue_Backlog` column.

---

### 11. Sum Order Qty. in FT2 for Membranes SB 2
- lineageTag: `545d4ca8-07c4-455f-b9c0-1a97b39c1589`

```dax
VAR OrderQtyFT2MembranesSB2 =
CALCULATE(
    SUMX(SAP_SD_HL_SalesDocumentItem_V2, [Open_Order_Quantity_in_FT2]),
    SAP_SD_HL_SalesDocumentItem_V2[FC Product Group] = "TPO"
)
RETURN
IF(
    OrderQtyFT2MembranesSB2 = BLANK(),
    0,
    OrderQtyFT2MembranesSB2
)
```

**Note:** Alternative implementation using CALCULATE + exact equality on `[FC Product Group] = "TPO"` instead of `CONTAINSSTRING(... "TPO")`. Also uses `Open_Order_Quantity_in_FT2` (open backlog qty), differentiating this from #9 which uses `RequestedQuantityInBaseUnit`.

---

## Recurring patterns

1. **Every measure wraps result in `IF(x = BLANK(), 0, x)`** to prevent BLANK propagation into ratios and to keep KPI cards showing "0" rather than blank when there's no data. Reproduce this exactly.
2. **Filters use `CONTAINSSTRING` with lowercase/mixed case** — CONTAINSSTRING is case-insensitive so "iso", "ISO", "Iso" all match. Reproduce case exactly to avoid divergence claims.
3. **"IS" = Invoiced Sales, "OI" = Order Intake, "SB" = Sales Backlog** (naming convention throughout).
4. **`Sum Billing Qty. in BFT2 for ISO` (measure #8 in Billing) has a "2" variant** (#2) that uses `Billing_Quantity_with_Signs` instead — separate measure, keep both.

# OData Measure Validation

**Purpose:** Validate every AWIP measure against the OData production reference. Includes special deep-check on ISO Rate.

**Sources of truth:**
- Production measures: `production-reference-odata/.../SemanticModel/definition/tables/KRW-NA_FF_FORECAST.tmdl` and `KRW_NA_FF_FORECAST_INTAKE.tmdl` (17 TMDL measures — the rest live in the AAS cubes and are invisible)
- AWIP measures: `AWIP_Commercial_Sales.PBIP/.../SemanticModel/definition/tables/{_Measures,Billing,SalesOrders}.tmdl` (~37 TMDL measures)

**Classification legend:**
- **EXACT** — matches production DAX verbatim
- **ADAPTED CORRECTLY** — semantically identical but implemented differently for AWIP's model (e.g. shared-dim vs role-playing dim)
- **WRONG SOURCE** — uses a table/column that's not the production source
- **WRONG DAX** — logic error compared to production
- **NOT IN ODATA** — the measure has no production equivalent (either an AWIP extra, or a reconstruction of an AAS-cube measure)
- **NEEDS REBUILD** — production has it, AWIP is missing it → add during Phase 9

---

## 1. Full AWIP measure inventory + classification

### 1a. `_Measures` table (15 measures)

| Measure | AWIP DAX | Classification | Production reference | Action |
|---|---|---|---|---|
| `Sales` | `SUM(Billing[SlsVolNetAmt_CC])` | ADAPTED CORRECTLY (reconstructing AAS `Revenue` in DAX) | AAS `Revenue` measure on VBRP — invisible | Verify numeric match in Phase 10 |
| `Sales Quantity` | `SUM(Billing[SalesVolumeQuantity])` | ADAPTED CORRECTLY | AAS `Sum Billing Qty. ...` variant | Same |
| `Order Intake` | `SUM(SalesOrders[IncSalesOrdNetAmnt_CC])` | ADAPTED CORRECTLY | AAS measure on VBAP | Same |
| `Order Intake Quantity` | `SUM(SalesOrders[IncSalesOrderQty])` | ADAPTED CORRECTLY | AAS measure on VBAP | Same |
| `Sales PY` | `CALCULATE([Sales], SAMEPERIODLASTYEAR('DimDate'[Date]))` | ADAPTED CORRECTLY | AAS PY measure — invisible | Verify against AAS Fiscal-Month-Prior-Year variants |
| `Sales Quantity PY` | `CALCULATE([Sales Quantity], SAMEPERIODLASTYEAR('DimDate'[Date]))` | ADAPTED CORRECTLY | AAS PY measure | Same |
| `Order Intake PY` | `CALCULATE([Order Intake], SAMEPERIODLASTYEAR('DimDate'[Date]))` | ADAPTED CORRECTLY | AAS PY measure | Same |
| `Order Intake Quantity PY` | same pattern | ADAPTED CORRECTLY | AAS PY measure | Same |
| `Sales YoY %` | `DIVIDE([Sales]-[Sales PY], [Sales PY])` | NOT IN ODATA (AWIP-added convenience KPI) | — | Keep |
| `Sales Quantity YoY %` | same pattern | NOT IN ODATA | — | Keep |
| `Order Intake YoY %` | same pattern | NOT IN ODATA | — | Keep |
| `Order Intake Quantity YoY %` | same pattern | NOT IN ODATA | — | Keep |
| `Order Intake vs Sales` | `[Order Intake] - [Sales]` | NOT IN ODATA | — | Keep |
| `Avg Sales Price` | `DIVIDE([Sales], [Sales Quantity])` | NOT IN ODATA (AWIP convenience) | — | Keep |
| `Avg Order Price` | `DIVIDE([Order Intake], [Order Intake Quantity])` | NOT IN ODATA | — | Keep |

### 1b. `Billing` table (9 measures)

| Measure | AWIP DAX (summary) | Classification | Production reference | Action |
|---|---|---|---|---|
| `Sum Billing Qty. in FT2 for Membranes` | `SUMX(Billing, IFERROR(VALUE(Billing[Billing_quantity_in_FT2_for_Membrane]), 0))` | ADAPTED CORRECTLY | AAS-cube measure (visible in report visuals as `Sum Billing Qty. in FT2 for Membranes`) | Verify numeric parity |
| `Sum Billing Qty. in BFT2 for ISO` | similar SUMX-VALUE pattern using `Billing_quantity_in_BFT2_For_ISO` | ADAPTED CORRECTLY | AAS-cube measure | Verify |
| `Sum Billing Qty. in BFT2 for ISO 2` | possibly duplicate of above | NEEDS REVIEW / DUPLICATE | — | Value-domain probe: if equal, DELETE the "2" variant |
| `Sum Fcst Sales in FT2 for Membranes` (fixed 2026-08-12) | `SUMX(Billing, IFERROR(VALUE(Billing[Sales_Forecast_Membrane_Qty_in_FT2]), 0))` | **WRONG SOURCE** | Prod `Current Month Invoiced Sales Membrane sqft` sources from `KRW-NA_FF_FORECAST[Sales Membrane sqft]` filtered by `[Current FYP VBRP]` | See §2 for ISO Rate deep-check. **Reconciliation candidate** after `KRW-NA_FF_FORECAST` import. |
| `Sum Revenue in DC with sign IS` | `SUM(Billing[Revenue])` | ADAPTED CORRECTLY | AAS `Revenue` measure | Verify |
| `ISO AOP - $/bdft IS` | `SUM(Billing[Revenue])/SUM(Billing[Billing_Quantity_with_Signs])` | ADAPTED CORRECTLY | AAS `ISO AOP` measure | Verify formula (`Revenue / Qty` shape correct) |
| `ISO Rate IS` | `DIVIDE([Sum Billing Qty. in BFT2 for ISO], [Sum Billing Qty. in FT2 for Membranes])` (with IF/BLANK guard) | ADAPTED CORRECTLY | AAS measure — same formula pattern (bdft/sqft) | ✅ Formula shape matches production's `ISO Rate Fcst`. Numeric verify. |
| `ISO Rate Fcst IS` | `DIVIDE(SUM(Billing[ForecastSalesBDFT]), [Sum Fcst Sales in FT2 for Membranes])` (with IF/BLANK guard) | **WRONG SOURCE (numerator + denominator)** | Prod `ISO Rate Fcst` sources both from `KRW-NA_FF_FORECAST` | See §2 |
| `Selected Fiscal Period` | (not read — likely a text/context measure) | NEEDS REVIEW | — | Inspect |

### 1c. `SalesOrders` table (13 measures)

| Measure | AWIP DAX (summary) | Classification | Production reference | Action |
|---|---|---|---|---|
| `ISO AOP - $/bdft OI` | `SUM(Revenue_Order_Intake)/SUM(Order_Quantity_in_BFT2)` | ADAPTED CORRECTLY | AAS AOP OI | Verify |
| `Sum Fcst Order Qty. in FT2 for Membranes OI` | SUMX-based on SalesOrders forecast columns | **WRONG SOURCE (potentially)** | Prod `Current Fiscal Month Sales Membrane sqft` sources from `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` filtered by `[Current FYP VBAP OI]` + Product Family CONTAINSSTRING | Both AWIP and prod use different source columns. Reconciliation: use `KRW_NA_FF_FORECAST_INTAKE[Sales Membrane sqft]` (already in AWIP) with equivalent filter. |
| `Sum Order Qty. in BFT2 for ISO OI` | SUMX on SalesOrders | ADAPTED CORRECTLY | AAS-cube measure | Verify |
| `Sum Order Qty. in BFT2 for ISO SB` | SUMX on SalesOrders (backlog filter) | ADAPTED CORRECTLY | AAS BACKLOG measure | Verify backlog filter matches prod |
| `Sum Order Qty. in FT2 for Membranes OI` | SUMX on SalesOrders | ADAPTED CORRECTLY | AAS-cube measure | Verify |
| `Sum Order Qty. in FT2 for Membranes SB` | SUMX on SalesOrders (backlog filter) | ADAPTED CORRECTLY | AAS BACKLOG measure | Verify |
| `Sum Order Qty. in FT2 for Membranes SB 2` | possibly duplicate | NEEDS REVIEW / DUPLICATE | — | Value-domain probe |
| `ISO Rate OI` | DIVIDE + IF/BLANK | ADAPTED CORRECTLY | AAS `ISO Rate` OI variant | ✅ Formula shape matches |
| `ISO Rate SB` | same | ADAPTED CORRECTLY | AAS `ISO Rate` SB variant | Verify |
| `ISO Rate Fcst OI` | uses SalesOrders forecast columns | ADAPTED CORRECTLY | Prod `ISO Rate Fcst VBAP` on `KRW_NA_FF_FORECAST_INTAKE` — same formula shape (bdft/sqft) | Numeric parity likely; grain check needed |
| `Total Backlog $` | SUMX using SalesOrders[Revenue_Backlog] | ADAPTED CORRECTLY | AAS BACKLOG measure | Verify |
| `PY Revenue Order Intake` | CALCULATE + SAMEPERIODLASTYEAR | ADAPTED CORRECTLY (per project memory: AWIP uses KRW_NA_FF_CALENDAR filter, not PY_ snapshot columns) | AAS PY measure — invisible | Verify |
| `Sum PY Order Qty. in FT2 for Membranes OI` | CALCULATE + SAMEPERIODLASTYEAR | ADAPTED CORRECTLY | AAS PY measure | Verify |
| `Sum PY Order Qty. in BFT2 for ISO OI` | same pattern | ADAPTED CORRECTLY | AAS PY measure | Verify |

---

## 2. ⭐ ISO Rate — special deep check

### 2a. Production canonical formulas (verbatim)

**Invoice-side — `KRW-NA_FF_FORECAST[ISO Rate Fcst]`:**
```dax
VAR IsoRateFcst =
    DIVIDE(SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]),
           SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft]))
RETURN IF(IsoRateFcst = BLANK(), 0, IsoRateFcst)
```

**Order-intake side — `KRW_NA_FF_FORECAST_INTAKE[ISO Rate Fcst VBAP]`:**
```dax
VAR IsoRateFcstVBAP =
    DIVIDE(SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales ISO bdft]),
           SUM('KRW_NA_FF_FORECAST_INTAKE'[Sales Membrane sqft]))
RETURN IF(IsoRateFcstVBAP = BLANK(), 0, IsoRateFcstVBAP)
```

**Also — `KRW-NA_FF_FORECAST[ISO Rate Forecast]` calculated column (row-level):**
```dax
IF([Sales Membrane sqft]=0, 0, [Sales ISO bdft]/[Sales Membrane sqft])
```

Note: production has **both** a measure (aggregated `DIVIDE(SUM, SUM)`) and a calculated column (row-level `IF/DIV`). They give different results under filters — the measure is the one used in dashboards.

### 2b. AWIP current formulas

**Invoice-side — `Billing[ISO Rate Fcst IS]`:**
```dax
VAR IsoRateFcstIS =
    DIVIDE(
        SUM(Billing[ForecastSalesBDFT]),
        ([Sum Fcst Sales in FT2 for Membranes])
    )
RETURN IF(IsoRateFcstIS = BLANK(), 0, IsoRateFcstIS)
```

Where `[Sum Fcst Sales in FT2 for Membranes]` = `SUMX(Billing, IFERROR(VALUE(Billing[Sales_Forecast_Membrane_Qty_in_FT2]), 0))`.

**Order-intake side — `SalesOrders[ISO Rate Fcst OI]`:** analogous pattern using SalesOrders forecast columns.

### 2c. Divergence analysis

| Aspect | Production | AWIP | Divergence |
|---|---|---|---|
| Formula shape | `DIVIDE(SUM(bdft), SUM(sqft))` | `DIVIDE(SUM(bdft), [Sum Fcst Sales Membrane])` | ✅ Same (SUM inside DIVIDE) |
| Numerator source | `KRW-NA_FF_FORECAST[Sales ISO bdft]` | `Billing[ForecastSalesBDFT]` | **DIFFERENT source table** |
| Denominator source | `KRW-NA_FF_FORECAST[Sales Membrane sqft]` | `Billing[Sales_Forecast_Membrane_Qty_in_FT2]` | **DIFFERENT source table** |
| Numerator granularity | Fiscal-period rollup in FORECAST dataflow | Fact-row level in Billing (many rows per fiscal period) | **DIFFERENT grain** |
| Denominator granularity | Fiscal-period rollup in FORECAST dataflow | Fact-row level in Billing | **DIFFERENT grain** |
| Filter propagation | Via `FiscalYearPeriods Slicer ↔ FORECAST` bi-di | Via Billing's own filter context | **DIFFERENT** |

**Impact:** the ratio value may or may not match production depending on how Kingspan populates the two data sources. If the FORECAST dataflow contains the same aggregated bdft/sqft totals per fiscal period as the row-level SUMs of Billing's forecast columns, results match. If not, AWIP's ISO Rate Fcst diverges from production's.

**Resolution:**
- **STRONG recommendation:** import `KRW-NA_FF_FORECAST` (the hyphenated invoice-side dataflow) into AWIP.
- Then rewrite `ISO Rate Fcst IS` to use `SUM('KRW-NA_FF_FORECAST'[Sales ISO bdft]) / SUM('KRW-NA_FF_FORECAST'[Sales Membrane sqft])` — verbatim production formula.
- This aligns AWIP with production's canonical source AND removes AWIP's dependency on Billing's string-typed `Sales_Forecast_Membrane_Qty_in_FT2` column (no more `VALUE()` wrapper needed).
- The order-intake side (`ISO Rate Fcst OI`) is already compatible because AWIP has `KRW_NA_FF_FORECAST_INTAKE` — should be rewritten to use its columns directly the same way.

### 2d. ISO Rate action items (Phase 9)

1. Add `KRW-NA_FF_FORECAST` to AWIP model (dataflow import).
2. Rewrite `Billing[ISO Rate Fcst IS]` and `Billing[Sum Fcst Sales in FT2 for Membranes]` to source from the new dataflow.
3. Rewrite `SalesOrders[ISO Rate Fcst OI]` and `SalesOrders[Sum Fcst Order Qty. in FT2 for Membranes OI]` to source from `KRW_NA_FF_FORECAST_INTAKE` verbatim.
4. Delete the Billing[Sales_Forecast_*] / [ISO_Rate_Forecast] string-column DAX workarounds (they were a stopgap — production doesn't use them).

---

## 3. Duplicate / redundant measures to reconcile

| Measure A | Measure B | Verdict candidate |
|---|---|---|
| `Sum Billing Qty. in BFT2 for ISO` | `Sum Billing Qty. in BFT2 for ISO 2` | Compare DAX + values; delete "2" if equivalent |
| `Sum Order Qty. in FT2 for Membranes SB` | `Sum Order Qty. in FT2 for Membranes SB 2` | Same |

Historical note from ODBC-era work: these "2" variants were kept because value probes showed identical results (`196,400` per prior verification), but the naming suggests intent to differ. Investigate source column selection.

---

## 4. Missing production measures — reconstruct in AWIP (Phase 9)

The 15 missing production TMDL measures (invoice-side + order-intake side, plus their PY / YTD variants) all follow the same three patterns:

**Pattern A — current fiscal month total:**
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[<column>]),
          FILTER('KRW-NA_FF_FORECAST',
                 'KRW-NA_FF_FORECAST'[Fiscal Year Period] = [Current FYP VBRP]))
```
Needs `[Current FYP VBRP]` reconstructed. Proposed DAX: derive from `MAX('KRW_NA_FF_FISCALPERIOD'[Fiscal Year Period])` filtered by `TODAY()`, OR from a `Fiscal Year Period` column on Billing filtered to the current calendar month.

**Pattern B — YTD total:**
```dax
CALCULATE(SUM('KRW-NA_FF_FORECAST'[<column>]),
          FILTER('KRW_NA_FF_CALENDAR',
                 YEAR('KRW_NA_FF_CALENDAR'[Date]) = YEAR(TODAY())))
```
Straight port; requires the CALENDAR dataflow in the model (already present in AWIP).

**Pattern C — product-family filtered:**
```dax
CALCULATE(SUM('KRW_NA_FF_FORECAST_INTAKE'[<column>]),
          CONTAINSSTRING('KRW_NA_SAP_VBAP OI'[Product Family], "<Membrane|iso>"),
          KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period] = [Current FYP VBAP OI])
```
Remap: `KRW_NA_SAP_VBAP OI[Product Family]` → `SalesOrders[Product_Family_Product_Number]`. Confidence STRONG.

**Written:** 2026-08-13

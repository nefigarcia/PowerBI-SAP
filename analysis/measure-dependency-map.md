# Measure Dependency Map + Phase 9 ISO Rate Trace

**Purpose:** Recursive dependency graph for every production measure, and confirmed mapping to new RL source. Answers "can this measure be reproduced exactly, and if so how?".

Legend:
- `→ M[X]` measure dependency
- `→ C[X]` column dependency
- `✓ EXACT` — column exists in new RL source with identical name
- `≈ STRONG` — column exists with minor name variant, same semantics
- `? POSSIBLE` — plausible but unverified
- `✗ NOT FOUND` — column missing from new source (blocks reproduction)

---

## Billing measures

### Sum Billing Qty. in FT2 for Membranes  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group   (RL Billing.tmdl line 829)
→ C[Billing_Quantity_in_FT2]             ✓ EXACT  → same               (line 3439)
```
**Reproducible: YES (STRONG)** — replace `FC Product Group` with `FC_Product_Group` in the CONTAINSSTRING filter.

### Sum Billing Qty. in BFT2 for ISO 2  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group
→ C[Billing_Quantity_with_Signs]         ✓ EXACT                        (line 3318)
```
**Reproducible: YES (STRONG)**

### Sum Billing Qty. in BFT2 for ISO  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group
→ C[Billing_Quantity_in__BFT2]           ✓ EXACT (double underscore)    (line 3375)
```
**Reproducible: YES (STRONG)**

### Sum Fcst Sales in FT2 for Membranes  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group
→ C[ForecastSalesSQFT]                   ✓ EXACT                        (line 3302)
```
**Reproducible: YES (STRONG)**

### Sum Revenue in DC with sign IS  *(atomic)*
```
→ C[Revenue]                             ✓ EXACT                        (line 3335)
```
**Reproducible: YES (EXACT)**

### ISO AOP - $/bdft IS  *(atomic)*
```
→ C[Revenue]                             ✓ EXACT
→ C[Billing_Quantity_with_Signs]         ✓ EXACT
```
**Reproducible: YES (EXACT)**

### ⭐ ISO Rate IS  *(composite — see Phase 9 below)*
```
→ M[Sum Billing Qty. in BFT2 for ISO]    (reproducible: STRONG)
→ M[Sum Billing Qty. in FT2 for Membranes] (reproducible: STRONG)
   Ultimate columns:
   → C[FC Product Group]                 ≈ STRONG → FC_Product_Group
   → C[Billing_Quantity_in__BFT2]        ✓ EXACT
   → C[Billing_Quantity_in_FT2]          ✓ EXACT
```
**Reproducible: YES (STRONG)** — Only rewrite needed is the column-name space→underscore in the two dependent measures.

### ISO Rate Fcst IS  *(composite)*
```
→ C[ForecastSalesBDFT]                   ✓ EXACT                        (line 3294)
→ M[Sum Fcst Sales in FT2 for Membranes] (reproducible: STRONG)
   Ultimate columns:
   → C[FC Product Group]                 ≈ STRONG
   → C[ForecastSalesSQFT]                ✓ EXACT
```
**Reproducible: YES (STRONG)**

---

## Sales measures

### ISO AOP - $/bdft OI  *(atomic)*
```
→ C[Revenue_Order_Intake]                ✓ EXACT                        (RL SalesOrders line 3097)
→ C[Order_Quantity_in_BFT2]              ✓ EXACT                        (line 3081)
```
**Reproducible: YES (EXACT)**

### Sum Fcst Order Qty. in FT2 for Membranes OI  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group     (line 568)
→ C[ForecastSalesSQFT]                   ✓ EXACT                        (line 3057)
```
**Reproducible: YES (STRONG)**

### Sum Order Qty. in BFT2 for ISO OI  *(atomic)*
```
→ C[Product Family]                      ≈ STRONG → Product_Family_Product_Number (line 1080)
   ⚠ verify values (should contain "iso") — RL suffix may indicate this is a product-number-based derivation, not the same
→ C[Requested_Quantity_in_BFT]           ✓ EXACT                        (line 3041)
```
**Reproducible: STRONG (with value-domain verification recommended)**

### Sum Order Qty. in BFT2 for ISO SB  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group
→ C[Requested_Quantity_in_BFT]           ✓ EXACT
```
**Reproducible: YES (STRONG)**

### Sum Order Qty. in FT2 for Membranes OI  *(atomic)*
```
→ C[Product Family]                      ≈ STRONG (see above caveat)
→ C[Order_Quantity_in_FT2]               ✓ EXACT                        (line 3089)
```
**Reproducible: STRONG**

### Sum Order Qty. in FT2 for Membranes SB  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group
→ C[RequestedQuantityInBaseUnit]         ✓ EXACT                        (line 2880)
```
**Reproducible: YES (STRONG)**

### Sum Order Qty. in FT2 for Membranes SB 2  *(atomic)*
```
→ C[FC Product Group]                    ≈ STRONG → FC_Product_Group
→ C[Open_Order_Quantity_in_FT2]          ✓ EXACT                        (line 3121)
```
**Reproducible: YES (STRONG)**

### ISO Rate OI  *(composite)*
```
→ M[Sum Order Qty. in BFT2 for ISO OI]   (STRONG)
→ M[Sum Order Qty. in FT2 for Membranes OI] (STRONG)
```
**Reproducible: STRONG**

### ISO Rate SB  *(composite)*
```
→ M[Sum Order Qty. in BFT2 for ISO SB]   (STRONG)
→ M[Sum Order Qty. in FT2 for Membranes SB] (STRONG)
```
**Reproducible: STRONG**

### ISO Rate Fcst OI  *(composite)*
```
→ C[ForecastSalesBDFT]                   ✓ EXACT                        (line 3065)
→ M[Sum Fcst Order Qty. in FT2 for Membranes OI] (STRONG)
```
**Reproducible: STRONG**

### Total Backlog $  *(atomic)*
```
→ C[Revenue_Backlog]                     ✓ EXACT                        (line 3105)
```
**Reproducible: YES (EXACT)**

---

## Phase 9 — ISO Rate IS Deep Trace

Per the plan, the ISO Rate IS chain is fully documented above. Full expansion:

```
ISO Rate IS  =
    VAR IsoRateIS = [Sum Billing Qty. in BFT2 for ISO] / [Sum Billing Qty. in FT2 for Membranes]
    RETURN IF(IsoRateIS = BLANK(), 0, IsoRateIS)

    ▼

    [Sum Billing Qty. in BFT2 for ISO] =
        VAR BillingQtyBFT2ISO = SUMX(
            FILTER(SAP_SD_HL_BillingDocumentItem_V2, CONTAINSSTRING([FC Product Group], "iso")),
            [Billing_Quantity_in__BFT2]
        )
        RETURN IF(BillingQtyBFT2ISO = BLANK(), 0, BillingQtyBFT2ISO)

    [Sum Billing Qty. in FT2 for Membranes] =
        VAR BillingQtyFT2Membranes = SUMX(
            FILTER(SAP_SD_HL_BillingDocumentItem_V2, CONTAINSSTRING([FC Product Group], "TPO")),
            [Billing_Quantity_in_FT2]
        )
        RETURN IF(BillingQtyFT2Membranes = BLANK(), 0, BillingQtyFT2Membranes)

    ▼

    Ultimate columns needed:
    - SAP_SD_HL_BillingDocumentItem_V2.FC Product Group  → RL: FC_Product_Group  (STRONG)
    - SAP_SD_HL_BillingDocumentItem_V2.Billing_Quantity_in__BFT2  → RL: same  (EXACT)
    - SAP_SD_HL_BillingDocumentItem_V2.Billing_Quantity_in_FT2  → RL: same  (EXACT)
```

### Reproduction in the new project — recommended TMDL

Assuming the new billing table is named `Billing` (matching AWIP_Commercial_Sales convention) with source column names as in RL:

```tmdl
measure 'Sum Billing Qty. in FT2 for Membranes' =
    VAR BillingQtyFT2Membranes =
    SUMX(
        FILTER(
            Billing,
            CONTAINSSTRING(Billing[FC_Product_Group], "TPO")
        ),
        Billing[Billing_Quantity_in_FT2]
    )
    RETURN
    IF(BillingQtyFT2Membranes = BLANK(), 0, BillingQtyFT2Membranes)
    formatString: #,0

measure 'Sum Billing Qty. in BFT2 for ISO' =
    VAR BillingQtyBFT2ISO =
    SUMX(
        FILTER(
            Billing,
            CONTAINSSTRING(Billing[FC_Product_Group], "iso")
        ),
        Billing[Billing_Quantity_in__BFT2]
    )
    RETURN
    IF(BillingQtyBFT2ISO = BLANK(), 0, BillingQtyBFT2ISO)

measure 'ISO Rate IS' =
    VAR IsoRateIS =
    [Sum Billing Qty. in BFT2 for ISO] / [Sum Billing Qty. in FT2 for Membranes]
    RETURN
    IF(IsoRateIS = BLANK(), 0, IsoRateIS)
```

**Only 3 changes vs production:**
1. Table name `SAP_SD_HL_BillingDocumentItem_V2` → `Billing` (or whatever the new table is named)
2. Column name `[FC Product Group]` → `[FC_Product_Group]` (underscore)
3. Everything else copied verbatim (VAR names, BLANK guards, CONTAINSSTRING casing "TPO"/"iso", formatString)

**Validation checkpoint for Phase 8:** After reproduction, run these DAX queries side-by-side against production and new project — the numbers must match within monetary/quantity tolerance to be considered reproduced:
```dax
EVALUATE ROW("ISO Rate IS", [ISO Rate IS])
EVALUATE ROW("Numerator", [Sum Billing Qty. in BFT2 for ISO])
EVALUATE ROW("Denominator", [Sum Billing Qty. in FT2 for Membranes])
```

Same for a filtered context (e.g. `FiscalYearPeriod = "2026007"`).

---

## Reproducibility summary

| Measure | Base confidence | Verification blocker |
|---|---|---|
| Sum Billing Qty. in FT2 for Membranes | STRONG | Verify `FC_Product_Group` values include "TPO" |
| Sum Billing Qty. in BFT2 for ISO | STRONG | Verify "iso" value present |
| Sum Billing Qty. in BFT2 for ISO 2 | STRONG | Same |
| Sum Fcst Sales in FT2 for Membranes | STRONG | Same |
| Sum Revenue in DC with sign IS | EXACT | — |
| ISO AOP - $/bdft IS | EXACT | — |
| **ISO Rate IS** | STRONG | Domain values in `FC_Product_Group` |
| **ISO Rate Fcst IS** | STRONG | Same |
| ISO AOP - $/bdft OI | EXACT | — |
| Sum Fcst Order Qty. in FT2 for Membranes OI | STRONG | Domain values in `FC_Product_Group` |
| Sum Order Qty. in BFT2 for ISO OI | STRONG | Verify `Product_Family_Product_Number` values include "iso" |
| Sum Order Qty. in BFT2 for ISO SB | STRONG | Domain values in `FC_Product_Group` |
| Sum Order Qty. in FT2 for Membranes OI | STRONG | Verify `Product_Family_Product_Number` includes "Membrane" |
| Sum Order Qty. in FT2 for Membranes SB | STRONG | Domain values |
| Sum Order Qty. in FT2 for Membranes SB 2 | STRONG | Domain values |
| **ISO Rate OI** | STRONG | Chain of above |
| **ISO Rate SB** | STRONG | Chain of above |
| **ISO Rate Fcst OI** | STRONG | Chain of above |
| **Total Backlog $** | EXACT | — |

**19 of 19 measures reproducible.** Zero blockers from the SAP data side. All STRONG mappings need one confirmation step in Phase 8: verify the domain values (TPO / ISO / Membrane / iso) exist in the RL column equivalents by running a `DISTINCT([FC_Product_Group])` query.

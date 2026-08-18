# ISO Rate Investigation — Paused

**Status:** paused pending direct comparison with production. Resume when we have production's filtered Membrane FT2, ISO BFT2, and Revenue numbers for period 2026-07.

**Date paused:** 2026-08-16

---

## The problem

AWIP's `ISO Rate IS` measure on the Invoiced Sales Dashboard shows **0.78** for fiscal period 2026007 (July 2026). Production's equivalent tile shows **1.34** for the same period. The formula shape matches production verbatim:

```dax
ISO Rate IS =
    VAR IsoRateIS =
        [Sum Billing Qty. in BFT2 for ISO] / [Sum Billing Qty. in FT2 for Membranes]
    RETURN IF(IsoRateIS = BLANK(), 0, IsoRateIS)
```

## What we verified works ✅

- **Filter propagation:** the fiscal period slicer (`Fiscal Period Selector` disconnected table) DOES propagate to Billing (changing period 2026007 → 2026006 changed the values, confirming the filter reaches the fact table).
- **Product Family list has 8 distinct values:** Cover Board, ISO GF, ISO GF Taper, Polyiso Insulation, PVC Membranes, Roofing Assesories, TPO Membranes, and one more likely `(Blank)`.
- **Production DAX exactly matches AWIP shape:**
  ```dax
  Sum Billing Qty. in FT2 for Membranes = SUMX(FILTER(VBRP, CONTAINSSTRING(Product Family, "Membrane")), Billing Qty. in FT2)
  Sum Billing Qty. in BFT2 for ISO = SUMX(FILTER(VBRP, CONTAINSSTRING(Product Family, "iso")), Billing Qty. in BFT2)
  ISO Rate = [BFT2 ISO] / [FT2 Membranes]
  ```
- **ISO Rate Fcst IS fix WORKED partially:** Shows 2.80 (vs expected 2.94) — this is the grand total across all 2026 periods because filter propagation to `KRW-NA_FF_FORECAST` is inconsistent (the bridge relationship was created but the visual may not use the Fiscal Period Selector slicer as its filter path).

## Diagnostic values recorded for period 2026007

Recorded in Billing table diagnostic measures (all under `_Diagnostics` display folder):

| Diagnostic measure | Value | Notes |
|---|---|---|
| `_Diag Distinct Product_Family Count` | 8 | Confirmed |
| `_Diag ISO BFT (single)` | 633,613 | Uses `Billing_Quantity_in_BFT` (single BFT), filter contains "iso" |
| `_Diag ISO BFT2 (double_underscore)` | 633,613 | Uses `Billing_Quantity_in__BFT2` (double underscore) — **identical to single BFT** |
| `_Diag Membrane FT2` | 812,400 | Uses `Billing_Quantity_in_FT2`, filter contains "Membrane" |
| `_Diag ISO BFT (ISO GF only)` | 630,093 | Excludes Polyiso — negligible difference |
| `_Diag Membrane FT2 (TPO Membranes exact)` | 811,900 | Excludes PVC Membranes — negligible difference |
| `_Diag Candidate ISO Rate` | 0.78 | (ISO GF only / TPO Membranes exact) = 0.78 |
| `_Diag Membrane FT2 (string Qty col)` | **69,430** | Uses Kingspan-added `Billing_Qty_in_FT2` STRING column — dramatically smaller |
| `_Diag ISO BFT (pre-classified string)` | 385,664 | Uses `Billing_quantity_in_BFT2_For_ISO` pre-classified string |
| `_Diag Membrane FT2 (pre-classified string)` | 811,900 | Uses `Billing_quantity_in_FT2_for_Membrane` pre-classified string |
| `_Diag Candidate ISO Rate v2` | 0.48 | (pre-classified ISO / pre-classified Membrane) = 0.48 |

## Semantic conclusions

- **`Billing_Quantity_in_BFT` and `Billing_Quantity_in__BFT2` return identical totals** — likely the same data with different labels.
- **`Billing_Qty_in_FT2` string column has a dramatically different total (69,430 vs 812,400 for Membrane)** — this is a different data element, not just a name variant. Kingspan-specific meaning unknown.
- **Filter narrowing (`Polyiso` out, `TPO Membranes` exact) doesn't help** — the excluded families contribute <0.4% to totals in this period.
- **None of the column combinations we tried give 1.34** — best candidates were 0.48, 0.78, and 0.78.

## Production baseline (from KRW_NA_SM_INVOICED semantic model view)

- `Sum of Billing Qty. in FT2` **unfiltered grand total = 4,191,044** across all rows/periods
- `Billing Qty. in FT2` is a **numeric column** (Σ icon in field list, shown as "Sum of..." when dropped on a visual — Power BI's auto-implicit-measure pattern)
- Column shows an "eye" icon on hover — likely marked as **hidden** in the semantic model, but still visible in field list

## The unresolved question

**AWIP's `Billing_Quantity_in_FT2` sums to 812,400 for Membrane rows in 2026007. Production's `Billing Qty. in FT2` sums to ??? for the same filter.** We haven't yet made that direct comparison. Three explanations remain:

1. **Different underlying data.** Kingspan's semantic model may source from a different Datasphere view or apply upstream filtering that AWIP doesn't (e.g., excluding void/cancelled billing docs).
2. **Column identity mismatch.** Production's "Billing Qty. in FT2" (with a **dot after Qty**) may be a completely different column than AWIP's `Billing_Quantity_in_FT2`. AWIP's `Billing_Qty_in_FT2` (with the short "Qty") is the closer NAME match but has different values (69,430).
3. **Sign / reversal handling.** Production might apply signs (subtract credit memos) via a calculated column upstream, giving a net value lower than AWIP's gross.

---

## Update 2026-08-17 — SAC direct-query results settle the "AWIP data is wrong" hypothesis

User connected Excel to SAP Analytics Cloud, live-queried `SAP_SD_RL_BillingDocumentItem_V2` (the exact same Datasphere view AWIP reads), filtered to `Fiscal Year Period = 2026007`, grouped by `Product Family`. Complete breakdown from SAC:

| Product Family | BFT2 (long) | FT2 (long) | Qty in FT2 (short — STRING) | FT2 for Membrane | BFT2 For ISO |
|---|---|---|---|---|---|
| Cover Board | 0 | 53,760 | `PAL56.000` | — | — |
| ISO GF | **609,356.80** | 365,056 | * | — | 365,056 |
| ISO GF Taper | 20,736 | 13,568 | * | — | 13,568 |
| Polyiso Insulation | 3,520 | 7,040 | * | — | 7,040 |
| PVC Membranes | 0 | 500 | `ROL1.000` | — | — |
| Roofing Assessories | 0 | 0 | — | — | — |
| TPO Membranes | 0 | 811,900 | * | 811,900 | — |
| **TOTAL** | **633,613** | 1,251,824 | (n/a — string) | 811,900 | 385,664 |

**AWIP is 100% correct on the raw numbers.** SAC directly confirms:
- ISO BFT2 (long-form, ISO product families) = **633,613** — matches AWIP exactly
- Membrane FT2 (with `CONTAINSSTRING "Membrane"`, catches TPO + PVC) = **812,400** — matches AWIP exactly
- Short-form `Billing Qty in FT2` is a **STRING** measure with sales-unit codes (`PAL56.000`, `ROL1.000`) — NOT what production uses
- Pre-classified `Billing quantity in BFT2 For ISO` (misleading name — actually stores FT2 values) = 385,664

**Every possible raw-column ratio computed:**

| Formula | Result | 1.34? |
|---|---|---|
| BFT2 ISO / FT2 Membrane (AWIP + production TMDL formula) | 633,613 / 812,400 = **0.78** | ❌ |
| BFT2 ISO / FT2 ISO (unit conversion within ISO product) | 633,613 / 385,664 = **1.643** | ❌ |
| BFT2 ISO (ISO GF only) / FT2 ISO (ISO GF only) | 609,357 / 365,056 = **1.669** | ❌ |
| pre-classified For ISO / pre-classified for Membrane | 385,664 / 811,900 = **0.475** | ❌ |
| unfiltered BFT2 / unfiltered FT2 | 2,638,352 / 4,063,828 = **0.649** | ❌ |

**Definitive conclusion:** production's 1.34 CANNOT come from any raw-column combination on the Datasphere view. Production must apply a transformation in the AAS cube layer (`KRW_NA_SM_INVOICED`) that isn't visible from Datasphere-side inspection. Most likely candidates:

1. **Unit-conversion factor** (`Factor_UoM_BFT` or similar) applied per row before aggregation.
2. **Different Product Family mapping** in the AAS cube (e.g., `"TPO Membranes"` → `"Membrane"` and PVC Membranes excluded from the "Membrane" bucket).
3. **A completely different measure formula** defined only in the AAS cube's calculated columns / measures.

**AWIP hypothesis #1 (different underlying data) is DISPROVEN.** SAC shows identical values to AWIP.
**AWIP hypothesis #2 (column identity mismatch) is DISPROVEN.** The long-form is confirmed as what production TMDL references.
**AWIP hypothesis #3 (signs / reversal) is DISPROVEN.** SAC totals match AWIP totals.

## To resume — 2 direct paths (revised)

### Option A — Get the AAS `ISO Rate` DAX directly (FASTEST — 5-minute task for Kingspan)
Ask Ana / James to open `KRW_NA_SM_INVOICED` semantic model in Tabular Editor or SSMS via XMLA endpoint `powerbi://api.powerbi.com/v1.0/myorg/KRW - North America Reporting`. Copy the DAX definition of:
- The `ISO Rate` measure itself
- `Sum Billing Qty. in FT2 for Membranes` (if defined at cube level, may override the .pbip-side measure)
- `Sum Billing Qty. in BFT2 for ISO`
- Any `Product Family` calculated column that maps raw SAP values to consolidated business categories

### Option B — Read production dashboard values for 2026-07
In the production `Amalgamated Sales Reports - JC.pbip` (or the Power BI Service report):
- Invoiced Membrane - SQFT card = ?
- Invoiced ISO - BDFT card = ?
- ISO Rate tile = 1.34 (already confirmed by user)

If Membrane card shows ≈**473,000** (not our 812,400) → AAS cube reduces Membrane denominator by ~340K. That's the smoking gun.
If ISO card shows ≈**1,088,000** (not our 633,613) → AAS cube multiplies ISO numerator by ~1.72. That's the smoking gun.

## The original 3 options below are historical

(SAC investigation has effectively resolved options B and C — data is same, universe is same.)

## To resume: 3 things to check (any one of them settles it)

### Option A — direct value comparison in production semantic model
In KRW_NA_SM_INVOICED semantic model (Power BI Service or Desktop live-connected):
1. Add slicer for **Fiscal Year Period = 2026007**
2. Add slicer for **Product Family contains "Membrane"** (or select "TPO Membranes")
3. Drop `Billing Qty. in FT2` on a card visual → tell us the value
4. Repeat with `Billing Qty. in BFT2` + Product Family contains "iso" → get numerator
5. Compare directly to AWIP's 812,400 and 633,613

### Option B — get the production DAX from Kingspan
Ask Ana / James for the DAX definitions of these fields on the `KRW_NA_SAP_VBRP` table in the `KRW_NA_SM_INVOICED` semantic model:
- `Billing Qty. in FT2` (probably a calculated column)
- `Billing Qty. in BFT2`
- `Revenue in DC with Sign`
- Any related calculated columns / measures the Sum Billing Qty. measures depend on

Their answer will let us reproduce the exact transformation in AWIP.

### Option C — compare Revenue as sanity check
Same universe check — production's Revenue for period 2026007 vs AWIP's $1,138,072. If Revenues match, the row universe is the same and the difference is a column-level definition. If Revenues differ, the datasets are simply different underlying sets of rows.

## Current AWIP state (as of pause)

- `Billing[Sum Billing Qty. in FT2 for Membranes]` — uses `CONTAINSSTRING(Product_Family, "Membrane")` + `Billing_Quantity_in_FT2` → 812,400
- `Billing[Sum Billing Qty. in BFT2 for ISO]` — uses `CONTAINSSTRING(Product_Family, "iso")` + `Billing_Quantity_in_BFT` (single BFT) → 633,613
- `Billing[ISO Rate IS]` — unchanged shape, currently returns 0.78
- 11 diagnostic measures under `_Diagnostics` display folder on Billing table (not deleted — leave for now so we can pick up where we left off; safe to delete once resolved)
- `KRW-NA_FF_FORECAST` dataflow imported with 8 source columns + 1 calculated column (`Fiscal Year Period Billing Format`)
- Relationship `KRW-NA_FF_FORECAST[Fiscal Year Period Billing Format]` ↔ `Fiscal Period Selector[FiscalYearPeriod]` (bothDirections, 1:1)
- `Billing[Sum Fcst Sales in FT2 for Membranes]` — now `SUM(KRW-NA_FF_FORECAST[Sales Membrane sqft])`, returns 2.80 grand total (filter propagation to FORECAST still inconsistent)
- `Billing[ISO Rate Fcst IS]` — production verbatim: `DIVIDE(SUM(KRW-NA_FF_FORECAST[Sales ISO bdft]), SUM(KRW-NA_FF_FORECAST[Sales Membrane sqft]))`
- Corresponding SalesOrders measures rewritten to use `KRW_NA_FF_FORECAST_INTAKE` verbatim

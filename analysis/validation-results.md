# Validation Results

**Status:** Not yet populated — Phase 8. Populated after the new model is rebuilt.

## Validation protocol (to run in Phase 8)

For every measure, execute the equivalent DAX in both the production model and the new model with matching filter context. Record:

| Measure | Filter context | Production value | New value | Δ absolute | Δ % | Tolerance | Status |
|---|---|---|---|---|---|---|---|

## Tolerances (proposed — confirm with business)

- **Monetary totals (Revenue, Order Intake, Backlog):** exact match required (Δ = 0). Any variance indicates a wrong column mapping or wrong filter semantics.
- **Quantity totals:** exact match required.
- **Ratios (ISO Rate, AOP):** ±0.01% tolerance (floating-point rounding).
- **Prior-year measures:** exact match required.

## Minimum test contexts to run per KPI

- Unfiltered
- FiscalYearPeriod = "2026007" (default slicer)
- FiscalYearPeriod = "2026006" (prior period)
- Filter FC_Product_Group = "TPO"
- Filter FC_Product_Group = "ISO"
- One specific SalesDocument (drill-down)
- One specific Customer (via AAGC if KNVV is available)

## Minimum measures to validate

**Billing side:**
- Sum Revenue in DC with sign IS
- Sum Billing Qty. in FT2 for Membranes
- Sum Billing Qty. in BFT2 for ISO
- ISO Rate IS
- ISO Rate Fcst IS
- ISO AOP - $/bdft IS

**Sales side:**
- ISO AOP - $/bdft OI
- ISO Rate OI
- ISO Rate SB
- ISO Rate Fcst OI
- Total Backlog $

## Blocked-until dependencies

- Customer.xlsx-dependent measures (Cost of sales, Gross Margin) — validation blocked until source resolution
- Any Extended-page measure using Application / Industry — blocked

# Phase 10 — Post-Relationship KPI Validation

**Status:** Test plan only. Requires opening `AWIP_Commercial_Sales.pbip` in Power BI Desktop with production comparison. Do not execute from Claude Code.

**Baseline:** production `Amalgamated Sales Reports - JC.pbip` — same slicer selection, same visual.

**Reference period:** 2026007 (July 2026) — same as filter propagation tests.

---

## KPI checklist

| # | KPI | Location (report page) | Prod value | Dev value | Δ | Verdict | Notes |
|---|---|---|---|---|---|---|---|
| K1 | Revenue | Invoiced Sales Dashboard | (TBD) | (TBD) | | ⏳ | `SUM(Billing[Revenue])`. Should now respect Fiscal Period Selector. |
| K2 | PY Revenue | Invoiced Sales Dashboard | (TBD) | (TBD) | | ⏳ | Uses `KRW_NA_FF_CALENDAR` filter — depends on new Billing→CALENDAR edge. |
| K3 | Forecast Sales | Invoiced Sales Dashboard | (TBD) | (TBD) | | ⏳ | Uses `KRW-NA_FF_FORECAST`. Existing edge should already work. |
| K4 | Billing Quantity FT2 | Invoiced Sales Dashboard | (TBD) | (TBD) | | ⏳ | Grand total. Compare vs SAC unfiltered 4,191,044 to sanity-check unfiltered case. |
| K5 | Billing Quantity BFT2 | Invoiced Sales Dashboard | (TBD) | (TBD) | | ⏳ | Same. |
| K6 | Order Intake Revenue | Order Intake Dashboard | (TBD) | (TBD) | | ⏳ | `SUM(SalesOrders[Revenue_Order_Intake])`. Depends on activated SalesOrders→CALENDAR edge. |
| K7 | Order Intake Quantity | Order Intake Dashboard | (TBD) | (TBD) | | ⏳ | Same. |
| K8 | Backlog | Backlog Dashboard | (TBD) | (TBD) | | ⏳ | `SUM(SalesOrders[Revenue_Backlog])`. Uses inactive RequestedDeliveryDate_dt role-play → requires backlog measures to be updated to USERELATIONSHIP. |
| K9 | ISO Rate IS | Invoiced Sales Dashboard | 1.34 | 0.78 (as of 2026-08-17 pause) | -0.56 | ❌ known open | AAS-cube-side transform — see `iso-rate-investigation-status.md`. Not fixable by relationship changes alone. |
| K10 | ISO Rate Fcst IS | Invoiced Sales Dashboard | 2.94 | 2.80 (grand total, filter propagation broken pre-Phase 7) | | ⏳ | Should improve after new Fiscal Period Selector ↔ FORECAST_INTAKE relationship — need to remeasure. |
| K11 | ISO Rate OI | Order Intake Dashboard | (TBD) | (TBD) | | ⏳ | Depends on SalesOrders BFT2/FT2 columns. |
| K12 | ISO Rate Fcst OI | Order Intake Dashboard | (TBD) | (TBD) | | ⏳ | Uses `KRW_NA_FF_FORECAST_INTAKE` — should now be filterable by Fiscal Period Selector. |
| K13 | ISO Rate SB | Backlog Dashboard | (TBD) | (TBD) | | ⏳ | Backlog side — depends on RequestedDeliveryDate role-play activation in the DAX. |

---

## Interpretation guide

- ✅ **Correct**: dev value within 1% of prod value.
- ⚠ **Approximate**: dev value within 10% of prod value. Investigate before accepting.
- ❌ **Wrong**: dev value >10% off. Blocks release.
- ⏳ **Not yet tested**: needs Power BI Desktop time.

**Do not** mark a KPI ✅ just because it returns a non-blank value. Value must match production.

**Do not** treat K9 (ISO Rate IS) as blocking this task's success. It is a pre-existing paused investigation that hinges on AAS-cube transformations invisible from Datasphere — Phase 7 relationship rebuild cannot fix it.

---

## Expected improvements from Phase 7 (before running tests)

- **K10 (ISO Rate Fcst IS)** — expected to improve from 2.80 grand total to a period-scoped value. If it moves, the new FORECAST_INTAKE bridge is working.
- **K12 (ISO Rate Fcst OI)** — should now be period-scoped instead of grand total.
- **K1–K7** — should be unchanged in absolute terms (data hasn't changed) but should now be *properly filtered* by Fiscal Period Selector. If a period slicer is applied and K1 changes, the new Billing→CALENDAR edge is working.
- **K8, K13** — depend on backlog measures being rewritten to use USERELATIONSHIP(RequestedDeliveryDate_dt, CALENDAR.Date). If backlog measures still use CreationDate, they won't reflect the Requested Delivery Date semantics production uses.

---

## Backlog measure porting (follow-up work, not Phase 7 scope)

The Phase 7 relationship rebuild lays the foundation for backlog measures, but the measures themselves still filter by CreationDate. To fully replicate production Backlog semantics, each Backlog measure on SalesOrders should be wrapped:

```dax
Backlog Revenue = 
    CALCULATE(
        SUM(SalesOrders[Revenue_Backlog]),
        USERELATIONSHIP(SalesOrders[RequestedDeliveryDate_dt], KRW_NA_FF_CALENDAR[Date])
    )
```

This is Phase 12 / follow-up work — not required for the relationship rebuild to be structurally complete.

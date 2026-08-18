# Phase 8 — Model View Expectation

**Goal:** confirm that after the Phase 7 changes, the Power BI Model view no longer resembles a set of disconnected FF tables but structurally mirrors production — with `Billing` / `SalesOrders` in place of `_SAP_` facts.

**Verification status:** static (TMDL-only). Runtime model load must be confirmed by opening `AWIP_Commercial_Sales.pbip` in Power BI Desktop and inspecting the Model view.

---

## Expected topology (Commercial Sales subgraph)

```
                    ┌──────────────────────────────┐
                    │      Fiscal Period Selector  │
                    │  (calculated DISTINCT of      │
                    │   Billing[FiscalYearPeriod])  │
                    └──────┬────────────────┬──────┘
                     bothDir│         bothDir│
                            ▼                ▼
              ┌──────────────────┐   ┌───────────────────────────┐
              │ KRW-NA_FF_FORECAST│   │ KRW_NA_FF_FORECAST_INTAKE │
              └──────────────────┘   └───────────────────────────┘
                              (INVOICED-side)   (SORDERS-side)

    ┌────────────────────┐
    │ KRW_NA_FF_FISCALPERIOD │◀──bothDir──▶┌─────────────────────┐
    └────────────────────┘  (Calendar Date)│  KRW_NA_FF_CALENDAR │
                                            └─────────┬───────────┘
                                                      │ (Date)
                            ┌──────────single──────────┼──────single──────────┐
                            ▼                          ▼                       ▼
                    ┌───────────────┐         ┌───────────────┐        (INACTIVE role-play)
                    │    Billing    │         │  SalesOrders  │◀── RequestedDeliveryDate_dt
                    └───────┬───────┘         └───────┬───────┘         (SB backlog date)
                            │ State_Name              │ State_Name
                            ▼                         ▼
                    ┌─────────────────────────────────────┐
                    │        KRW_NA_FF_GEOINFO            │
                    └─────────────────────────────────────┘
```

## Comparison to production topology

| Aspect | Production | Development (post-Phase 7) |
|---|---|---|
| Facts | VBRP + VBAP OI + VBAP SB (three copies of same physical source) | Billing + SalesOrders (single copies, two OData feeds) |
| Calendar copies | CALENDAR + OI + SB (role-play) | KRW_NA_FF_CALENDAR (single) with USERELATIONSHIP for OI/SB semantics |
| FiscalPeriod copies | FISCALPERIOD + OI + SB | KRW_NA_FF_FISCALPERIOD (single) |
| Fiscal slicer | FiscalYearPeriods Slicer + OI + SB | Fiscal Period Selector (single, calculated from Billing) |
| GEOINFO copies | GEOINFO + OI + SB, joined on COUNTRY_REGION → KNA1.COUNTRY_REGION | KRW_NA_FF_GEOINFO (single), joined on State → Billing/SalesOrders.State_Name |
| Forecast tables | FORECAST + FORECAST_INTAKE, both bothDir to their slicer variant | Same shape, both bothDir to the single Fiscal Period Selector |
| SAP dim tables | KNA1, KNVV, LIKP, LIPS, TVAPT, MARM_BFT — all present as separate dims | Absent; attributes flat on Billing/SalesOrders |
| Auto Date/Time LocalDateTable_* | 21 auto-generated | None (Auto Date/Time should be OFF in dev) |

## Load-time checks to perform in Power BI Desktop

1. **Open `AWIP_Commercial_Sales.pbip`** — verify no parse errors on the modified TMDL files:
   - `SalesOrders.tmdl` (calculated column `RequestedDeliveryDate_dt`)
   - `KRW_NA_FF_FORECAST_INTAKE.tmdl` (calculated column `Fiscal Year Period Billing Format`)
   - `relationships.tmdl` (3 new + 1 activated relationship)
2. **Refresh the semantic model** — verify no relationship errors (particularly around the `Billing → KRW_NA_FF_CALENDAR` many-to-one which requires State_Name / date uniqueness).
3. **Model view inspection** — confirm Billing and SalesOrders both show relationship lines to `KRW_NA_FF_CALENDAR`, `KRW_NA_FF_GEOINFO`, and (for SalesOrders) an inactive dotted-line to CALENDAR via `RequestedDeliveryDate_dt`.
4. **`Fiscal Period Selector`** should be visibly connected to `KRW-NA_FF_FORECAST` (existing) AND `KRW_NA_FF_FORECAST_INTAKE` (new).
5. **Auto Date/Time** — verify File → Options → Current file → Data Load → Time intelligence → "Auto date/time for new files" is UNCHECKED. If auto date tables have appeared, disable and reload.

**If load fails**, most likely causes:
- Calculated column syntax error → check `RequestedDeliveryDate_dt` DAX with sample data.
- Relationship ambiguity → Power BI rejects if multiple active paths between the same two tables. Should not occur here (Billing ↔ CALENDAR: 1 active; SalesOrders ↔ CALENDAR: 1 active + 1 inactive).
- Uniqueness violation on many-to-one → `KRW_NA_FF_CALENDAR[Date]` must be unique. If dataflow returns duplicate dates, load fails; will need to add DISTINCT upstream.

**Deliverable:** manual confirmation from user (or Power BI Desktop screenshot) that the Model view resembles the expected topology and no errors on load.

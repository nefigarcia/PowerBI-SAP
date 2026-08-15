# Dataflow Relationships — Existing vs. Required

**Purpose:** Document the current relationship state after Kingspan added the 13 Dataflow tables to `AWIP_Commercial_Sales.SemanticModel`, and specify the relationships that should be created during the semantic-model repair phase.

**Format per row:** Production concept · Production key · New Dataflow table · New key · Fact table · Cardinality · Filter direction · Confidence.

**Constraint:** Only EXACT and STRONG relationships may be automatically created in the repair phase. POSSIBLE relationships stay listed as "needs value-domain probe" and are not applied without confirmation.

---

## 1. Existing relationships (already in `relationships.tmdl`)

### 1.1 Production-mirror (from Phase-5/7 repair — preserved as-is)

| # | GUID | From | To | Cardinality | Filter | Note |
|---|---|---|---|---|---|---|
| 1 | `3f7497dd-e016-449d-1c9d-f312dbab782e` | `Billing[BillingDocumentDate_D5]` | `DimDate[Date]` | many:one | single | production date connection |
| 2 | `d4b935e9-705f-1d3a-fc4e-fce6b0208d54` | `SalesOrders[CreationDate_D8]` | `DimDate[Date]` | many:one | single | production date connection |

### 1.2 Auto-detected on last Power BI save

| # | GUID | From | To | Cardinality | Filter | Note |
|---|---|---|---|---|---|---|
| 3 | `AutoDetected_5fec0261-dced-49ea-aede-16dc5aae5305` | `KRW_NA_FF_FISCALPERIOD[Calendar Date]` | `KRW_NA_FF_CALENDAR[Calendar Date]` | one:many | **both directions** | Bi-di on a bridge dim — reconsider (see §3) |
| 4 | `AutoDetected_db66fffc-ccb2-45f5-aa6f-4191678f3564` | `KRW_NA_FF_HISTSB1[Internal CAPEX ID]` | `'CAPEX Approved'[Internal CAPEX ID]` | many:one | single | CAPEX domain — out of scope for Commercial Sales but harmless |
| 5 | `AutoDetected_b57492e0-ec1b-4d14-86c1-3211f94c6c62` | `Billing[State_Name]` | `KRW_NA_FF_GEOINFO[State]` | many:one | single | ✅ enables `COUNTRY_REGION`, lat/long lookups |
| 6 | `AutoDetected_da5932da-e567-4bdf-a7c2-4bb9b8847c55` | `SalesOrders[State_Name]` | `KRW_NA_FF_GEOINFO[State]` | many:one | single | ✅ same on Sales side |
| 7 | `AutoDetected_91ebea43-f7db-4490-ab2c-b0af1c41c6f8` | `KRW_NA_FF_COSTELEM_OH1[Cost Element Key]` | `KRW_NA_FF_COSTELEMHIER[CostElement]` | one:many | **both directions** | Cost accounting — out of scope for Commercial Sales but harmless |

---

## 2. Relationships to create (repair phase — STRONG/EXACT only)

| # | Production concept | Prod key | Dataflow / target table | Target key | Fact | Cardinality | Filter | Confidence |
|---|---|---|---|---|---|---|---|---|
| R1 | Forecast values by fiscal period | (n/a) | `KRW_NA_FF_FORECAST_INTAKE[Fiscal Year Period]` | `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | forecast is not on a fact — it's a period dim rollup | many:one | single | STRONG — same fiscal-period domain, same source ownership |
| R2 | Fiscal-period to date bridge | `KRW_NA_FF_FISCALPERIOD[Calendar Date]` | `DimDate[Date]` | `DimDate[Date]` | via DimDate to both facts | many:one | single | STRONG — dates are the same domain |

**None of the other cross-table joins meet the EXACT / STRONG bar** without a value-domain probe. See §3 for the POSSIBLE list.

**Note:** Both auto-detected bi-directional relationships (#3 `FISCALPERIOD↔CALENDAR` and #7 `COSTELEM_OH1↔COSTELEMHIER`) **must remain `bothDirections`** — Power BI classifies both as one-to-one at load time because their key columns are unique in the imported data, and TOM rejects any 1:1 relationship with single-direction filtering (verified 2026-08-12 — both downgrades failed on load, both had to be reverted). The TMDL `fromCardinality: one` / default `toCardinality: many` markers are *not* reliable indicators of 1:many vs 1:1 — Power BI decides based on actual data. If you need to change cross-filter direction on these, do it via the Power BI Desktop UI, not via TMDL edits.

---

## 3. Relationships to defer (POSSIBLE — need probe before creating)

| # | Prod concept | Candidate | Why deferred |
|---|---|---|---|
| P1 | Fact → fiscal period dim (Billing) | `Billing[FiscalYearPeriod]` → `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | Value-domain format compatibility unverified (e.g. `2026001` vs `2026/001`) |
| P2 | Fact → fiscal period dim (SalesOrders) | `SalesOrders[Fiscal_Month]` (or equivalent) → `KRW_NA_FF_FISCALPERIOD[Fiscal Year Period]` | Same |
| P3 | Fact → territory dim (Billing) | `Billing[Territory_Name]` (or one of the partner-direction variants) → `KRW_NA_FF_TERRITORY[Territory Name]` | Territory names on the facts may include suffixes or different capitalisation than the dim |
| P4 | Fact → territory dim (SalesOrders) | `SalesOrders[Territory_Name]` → `KRW_NA_FF_TERRITORY[Territory Name]` | Same |
| P5 | Fact → zip bridge (Billing) | `Billing[PostalCode]` → `KRW_NA_FF_ZIPCODES[Zip Code Name]` | 4 zip variants on Billing (sold-to / ship-to / bill-to / payer); need business rule + zip-format check |
| P6 | Fact → zip bridge (SalesOrders) | `SalesOrders[PostalCode]` → `KRW_NA_FF_ZIPCODES[Zip Code Name]` | Same |
| P7 | Zip → territory (dataflow-internal) | `KRW_NA_FF_ZIPCODES[Territory ID]` → `KRW_NA_FF_TERRITORY` (needs a Territory ID key — doesn't currently exist; TERRITORY table keys on Territory Name and Zip Code ID/Name) | Territory table currently has no `Territory ID` column — a schema decision needed by data owner |
| P8 | Fact → cost centre (Billing) | `Billing[CostCenter]` → `KRW_NA_FF_COSTCENTREHIER[Cost Centre]` | Value-domain unverified AND scope: cost-accounting is not on the commercial-sales pages we're rebuilding |
| P9 | Fact → GL account (Billing) | (no `GL Account` column exists on Billing / SalesOrders) → `KRW_NA_FF_PLSTRUCTURE[GL Account]` | No bridge key — can't be joined |

---

## 4. Tables to consider dropping from the AWIP Commercial Sales model

If the CAPEX and cost-accounting domains are truly out of scope for this specific report (Commercial Sales), the following tables are unused and could be removed to keep the model small and unambiguous:

- `KRW_NA_FF_COSTCENTREHIER` — unused (no relationship to Billing)
- `KRW_NA_FF_COSTCTHIER_ONDULINE` — unused (duplicate schema of above)
- `KRW_NA_FF_COSTELEM_OH1` — unused (only relates to `COSTELEMHIER`)
- `KRW_NA_FF_COSTELEMHIER` — unused
- `KRW_NA_FF_PLSTRUCTURE` — unused (no bridge key)
- `KRW_NA_FF_HISTSB1` — unused (CAPEX/postings, not commercial sales)
- `'CAPEX Approved'` — unused (CAPEX not commercial sales)

**Recommendation:** Do **not** drop them yet. Confirm scope with Ana / James first. It is possible Kingspan intends to add CAPEX or cost-vs-sales pages to this same PBIP.

---

## 5. Relationships repair plan (summary)

For the semantic-model repair phase, when authorized:

1. **Keep** relationships #1, #2, #5, #6 (production-mirror + State→GeoInfo).
2. **Downgrade** relationship #3 from both-directions to single (to avoid calendar cross-filter ambiguity).
3. **Keep** relationships #4, #7 as-is if we retain the CAPEX / cost-accounting tables; otherwise drop them together with their tables.
4. **Create** R1 (`FORECAST_INTAKE` → `FISCALPERIOD`) and R2 (`FISCALPERIOD` → `DimDate`) — STRONG.
5. **Do not create** any of P1–P9 without a value-domain probe or a business decision.
6. **Do not** create fact-to-dataflow relationships in bi-directional mode by default; use single-direction unless a specific measure requires bi-di.

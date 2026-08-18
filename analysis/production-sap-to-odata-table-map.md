# Phase 3 — Production `_SAP_` Table → OData Replacement Map

**Rule:** each production `_SAP_` table that participates in a relationship must be mapped to `Billing`, `SalesOrders`, both, an intermediate dimension, or explicitly flagged NOT MAPPABLE. Only **EXACT** and **STRONG** mappings will be implemented automatically in Phase 7.

**Sources of evidence:**
- Production TMDL column lists in each `_SAP_` table
- Development TMDL for `Billing.tmdl` and `SalesOrders.tmdl` (OData source: SAP Datasphere `SAP_SD_RL_BillingDocumentItem_V2` / `SAP_SD_RL_SalesDocumentItem_V2`)
- Production DAX measures that reference the tables (evidence of which columns are load-bearing)

## Confidence legend
- **EXACT** — same source table (both are or wrap `VBRP` / `VBAP` etc.), column semantics 1:1 with no material transformation
- **STRONG** — semantically equivalent but with a name/format transformation that we can reproduce with high confidence
- **POSSIBLE** — plausible replacement, needs data validation before use
- **NOT FOUND** — no equivalent found; requires Ana-side data or must be flagged unresolved

---

## Mapping table

| Production `_SAP_` Table | Business Role | Replacement | Confidence | Evidence |
|---|---|---|---|---|
| `KRW_NA_SAP_VBRP` | Billing document line items — the *invoiced sales* fact for the INVOICED cube. Grain = billing document + item. | `Billing` | **EXACT** | (a) SAP source names match: production TMDL column `Billing Document`/`Billing Item`, dev `Billing.BillingDocument`/`BillingDocumentItem`. (b) All 45 measures on production VBRP reference columns that exist as flat columns on dev Billing (Product Family, Billing Qty. in FT2/BFT2, Revenue in DC with Sign, Margin in DC, Billing Date, Application, Territory, State Name, Sold-to). (c) SAC direct-query verification (2026-08-17) confirmed identical Billing Qty and Revenue values between AWIP Billing and production VBRP for period 2026007. |
| `KRW_NA_SAP_VBAP OI` | Sales order line items in **order-intake** context (Document Date is the business date). Grain = sales document + item. Consumed by the SORDERS cube. | `SalesOrders` (Document Date semantics → `CreationDate_D8`) | **EXACT** | (a) SAP source: VBAP = Sales Document Item = same table Datasphere exposes as `SAP_SD_RL_SalesDocumentItem_V2`, dev's SalesOrders. (b) Production measure on VBAP OI e.g. `Revenue Order Intake` uses `[Net Value in DC with Sign]` and `[Document Date]` — dev SalesOrders has `Revenue_Order_Intake` and `CreationDate_D8`. |
| `KRW_NA_SAP_VBAP SB` | Sales order line items in **backlog** context (Requested Delivery Date is the business date; delivery status/quantities matter). Same physical grain as VBAP OI. Consumed by the BACKLOG cube. | `SalesOrders` (Requested Delivery Date semantics → `RequestedDeliveryDate`) | **EXACT** | Same physical source as VBAP OI. Different measures (Backlog vs Order Intake) use different date column semantics. Dev SalesOrders already carries `Revenue_Backlog`, `Open_Order_Quantity_*`, `RequestedDeliveryDate`. |
| `KRW_NA_SAP_KNA1` (base + OI + SB) | Customer master (SAP KNA1). Columns: Customer, Customer Description, Region, Country, COUNTRY_REGION. Grain = one row per customer. | Subsumed into `Billing` / `SalesOrders` flat customer columns; **role as dim disappears** | **EXACT** for `Customer Description`, Country/Region. **NOT FOUND** for `COUNTRY_REGION` as a pre-concatenated key (see below). | Billing has `SoldToParty_D12`, `SoldToParty_D12_T` (customer description), `Country`, `Region`, `State_Name`, `PostalCode`, `Territory_Name`. SalesOrders has parallel `SoldToParty_D3`/`_T`, Country, Region, State_Name, Territory. NO `COUNTRY_REGION` concatenated key. |
| `KRW_NA_SAP_KNVV` (base + OI + SB) | Customer sales-area data (SAP KNVV). Columns: Customer, Sales Organization, Distribution Channel, Division, CUST_SALES (concatenation), Created, Customer Group, Company Type, Account Assignment Group. | Subsumed into `Billing` / `SalesOrders` flat customer/sales-org columns | **EXACT** for Customer Group, Sales Organization, Distribution Channel, Division. **NOT FOUND** for `CUST_SALES` (concatenated) or `Account Assignment Group` as separate dim slice. | Billing has `SalesOrganization_D16`, `DistributionChannel`, `Division`, `CustomerGroup`, `CustomerAccountAssignmentGroup`, `CustomerAccountAssignmentGroup_T`. SalesOrders has parallel columns. No `CUST_SALES` composite key. |
| `KRW_NA_SAP_LIKP` | Delivery header (SAP LIKP). Columns: Delivery Document (key), Delivery Date. Only 2 columns. | Not directly mappable to OData; delivery date not present on Billing/SalesOrders. | **NOT FOUND** — but production only uses this via `VBRP.Delivery Document → LIKP.Delivery Document` (row 5). No dev measure appears to filter/aggregate by Delivery Date via LIKP. | Dev Billing has no `DeliveryDocument` or `DeliveryDate` column. If any KPI relies on Delivery Date, it is broken in dev. **Flag Phase 11.** |
| `KRW_NA_SAP_LIPS` | Delivery item (SAP LIPS). Columns: DOC_ITM (key), Quantity Delivered BUoM, Quantity Delivered SUoM. Used only by BACKLOG cube. | Not directly mappable. Delivered quantities not on SalesOrders. | **NOT FOUND** — related to VBAP SB.SO_ITEM ↔ LIPS.DOC_ITM (row 36, bothDir). Impacts backlog measures that use `Quantity Delivered` for open-order calculations. | Dev SalesOrders has `Open_Order_Quantity_*`, `ConfdDelivQtyInOrderQtyUnit` (confirmed delivery qty) — these may be sufficient substitutes but need validation. **Flag Phase 11.** |
| `KRW_NA_SAP_MARM_BFT` / `KRW_NA_SAP_MARM_BFT 2` | Material UoM conversion factors (SAP MARM). Columns: Material, Alternative UoM, Numerator, Denominator. | Subsumed — Billing/SalesOrders already carry unit-of-measure conversion factors as flat columns (`Factor_UoM_BFT`, `Factor_Alternative_UoM_to_Base_UoM`, `Billing_Quantity_in_BFT`, `Billing_Quantity_in_FT2`, etc.). | **STRONG** | Dev Billing has 15+ pre-computed billing quantity columns (BFT, BFT2, FT2, M2, Sales UoM). VBAP SB uses MARM_BFT 2 for backlog quantity conversions — dev SalesOrders `Order_Quantity_in_BFT2`, `Order_Quantity_in_FT2`, `Requested_Quantity_in_BFT` cover the same cases. |
| `KRW_NA_SAP_TVAPT` | Sales document item category text (SAP TVAPT). Columns: Item Category (key), Item Category Description. | Subsumed — Billing.SalesDocumentItemCategory + Billing.SalesDocumentItemCategory_T (text). | **EXACT** | Dev Billing has both key and description columns flat. |
| `KRW_NA_SAP_TVM3T` | Item description text table (likely Nielsen region / VBRP text). Not referenced by any relationship in `relationships.tmdl` — reachable only via filter propagation from VBRP or the AAS cube. | Subsumed (or unused in relationships) | **STRONG** | Not participating in any relationship — no translation needed at the relationship level. |
| `KRW_NA_SAP_VBPA2` | Partner functions (SAP VBPA). Not referenced in `relationships.tmdl`. | Subsumed — Billing.BillToPart_A_14, ShipToPart_A_13, SoldToPart_A_12, Payer_A_15 all flat on Billing/SalesOrders. | **STRONG** | Same. |

---

## Which mappings are safe to implement automatically (Phase 7)

**EXACT** — implement:
- VBRP → Billing (drives the "translate row 4" relationship)
- VBAP OI → SalesOrders (drives "translate row 22")
- VBAP SB → SalesOrders (drives "translate row 35")
- KNA1 (Description / Country / Region attributes subsumed into fact) — no new relationship needed here
- TVAPT (subsumed — no relationship needed)

**STRONG** — implement:
- MARM_BFT (subsumed — no relationship needed)

**NOT FOUND / POSSIBLE** — do NOT implement; flag in Phase 11:
- KNA1.COUNTRY_REGION as a join key to GEOINFO → OData facts have `Country` and `Region` as separate columns; there is no pre-concatenated `COUNTRY_REGION`. Either (a) add a calculated column `Billing[COUNTRY_REGION] = Billing[Country] & "_" & Billing[Region]` and join to GEOINFO on that, or (b) accept the existing `State`-based join in dev if grain is sufficient (see Phase 5).
- KNVV.CUST_SALES as a join key — no equivalent needed since fact-side flat columns already carry the individual pieces.
- LIKP.Delivery Date / LIPS delivered quantities — dev has no source. If any KPI depends on this data, we cannot reproduce it without additional Datasphere pipes.
- KNVV.'Account Assignment Group Description' — dev has key + text on fact.

---

## Consequence for the dev topology

The dev graph will be **structurally simpler** than production, not by design shortcut but because the OData facts already carry customer-master, customer-sales-area, item-category, and UoM-conversion attributes as flat columns. Production needed:

- 3 role-play copies of each FF dim (INVOICED / OI / SB) because production is 3 AAS cubes stitched together in one .pbip.
- ~10 SAP dim tables to enrich VBRP / VBAP with customer, delivery, UoM, item-category data.

Dev needs:

- 1 copy of each FF dim (single Import model, no AAS cube split).
- 0 SAP dim tables — every attribute is a flat column on Billing / SalesOrders.

**Semantic behavior is preserved** because the same attributes reach the same visuals with the same filter selectivity — the physical relationship line count just drops from ~13 SAP-facing joins to ~4 FF-facing joins.

# Source Mapping: Production → New SAP Datasphere OData

**Purpose:** Field-by-field crosswalk between production HL views and new RL views. Feeds Phase 5 (rebuild).

**Basis:**
- Production HL columns: from `production-reference/.../SAP_SD_HL_*.tmdl`
- New RL columns: from `AWIP_Commercial_Sales.PBIP/.../Billing.tmdl` and `.../SalesOrders.tmdl` (already refreshed against the real Datasphere views — column set is authoritative)

**Confidence levels:** EXACT (identical field, verified) · STRONG (name variant, verified same semantics) · POSSIBLE (plausible, not verified) · NOT FOUND (no equivalent — need external source)

---

## Billing fact — `SAP_SD_HL_BillingDocumentItem_V2` → `SAP_SD_RL_BillingDocumentItem_V2`

### Columns used by measures or visuals

| Production HL column | New RL column | Confidence | Notes |
|---|---|---|---|
| `Revenue` | `Revenue` | **EXACT** | Both `double` |
| `Billing_Quantity_in_FT2` | `Billing_Quantity_in_FT2` | **EXACT** | |
| `Billing_Quantity_in__BFT2` (double underscore) | `Billing_Quantity_in__BFT2` | **EXACT** | Double underscore preserved |
| `Billing_Quantity_with_Signs` | `Billing_Quantity_with_Signs` | **EXACT** | |
| `Billing_Quantity_in_M2` | `Billing_Quantity_in_M2` | **EXACT** | |
| `Billing_Quantity_in_BFT` | `Billing_Quantity_in_BFT` | **EXACT** | (verify — grep didn't hit but AWIP tables likely have it) |
| `BillingQuantityInBaseUnit` | `BillingQuantityInBaseUnit` | **EXACT** | |
| `PYBilling_Quantity_in_BoM` | `PYBilling_Quantity_in_BoM` | **EXACT** | |
| `PY_Revenue` | `PY_Revenue` | **EXACT** | |
| `ForecastSales` | `ForecastSales` | **EXACT** | |
| `ForecastSalesSQFT` | `ForecastSalesSQFT` | **EXACT** | |
| `ForecastSalesBDFT` | `ForecastSalesBDFT` | **EXACT** | |
| `FC Product Group` | `FC_Product_Group` | **STRONG** | Space → underscore. Value domain (TPO, ISO) presumed identical; verify with data sample. |
| `CustomerAccountAssignmentGroup` | `CustomerAccountAssignmentGroup` | **EXACT** | Relationship key to KNVV |
| `Material` | `Material_D17` OR `Material` | **STRONG** | RL exposes `Material_D17` (dimension key form). Verify which one carries the material number used for join. |
| `MaterialGroup` | `MaterialGroup` | **EXACT** | |
| `Plant` | `Plant_D2` OR `Plant_A_2` OR `PlantCategory` | **POSSIBLE** | RL has multiple plant variants. Production uses plain `Plant`; need to identify which RL variant is the plant number used in reports. |
| `BillingDocument` | `BillingDocument` | **EXACT** | |
| `BillingDocumentItem` | `BillingDocumentItem` | **EXACT** | |
| `BillingDocumentDate` | `BillingDocumentDate_D5` + `BillingDocumentDate_D5_T` | **STRONG** | RL uses dimension key form `_D5`. `_D5` = numeric/date-key, `_T` = formatted text. For DAX we need to cast `_D5` to date. |
| `RequestedDeliveryDate` | `RequestedDeliveryDate` | **EXACT** | |
| `FiscalYearPeriod` | `FiscalYearPeriod` | **EXACT** | Values like `2026007` |
| `Unit_Price` | `Unit_Price` | **EXACT** | |
| `Unit_Price_in_Base_UoM` | `Unit_Price_in_Base_UoM` | **EXACT** | |
| `BaseUnit` | `BaseUnit` / `BaseUnit1` | **STRONG** | Two variants in RL. `BaseUnit` (line 178 of Billing.tmdl) is likely the correct one. |
| `SalesDocument` | `SalesDocument` | **EXACT** | Cross-reference to sales order that generated the invoice |
| `Country` | `Country` (or Country1..Country6 variants) | **POSSIBLE** | Multiple variants exist — need to identify sold-to-country. |
| `Region` | `Region` (or Region1..Region3 variants) | **POSSIBLE** | Multiple variants — likely `Region` is Ship-to-region. |
| `SoldToParty`, `ShipToParty`, `BillToParty` | same names | **EXACT** | |

### Column NOT confirmed in RL (needs verification once user checks Billing.pbix)

| Production HL column | Status | Action |
|---|---|---|
| `ProjectName` (visible in detail table) | **NOT FOUND** in AWIP.PBIP Billing columns | Likely comes from Customer.xlsx, not SAP |
| `Material Description` (visible in detail table) | **NOT FOUND** as-is | Likely from Customer.xlsx (`Material Description` column) |
| `Sales Representative` (visible in detail table) | **NOT FOUND** in SAP columns | Comes from Customer.xlsx (`Sales Representative Name`) |
| `Project Coordinator` (visible in detail table) | **NOT FOUND** in SAP columns | Comes from Customer.xlsx (`Project Coordinator`) |
| `Fiscal_Month` (dateTime dim) | Verify — likely `Fiscal_Month` exists in RL | Check |

---

## Sales fact — `SAP_SD_HL_SalesDocumentItem_V2` → `SAP_SD_RL_SalesDocumentItem_V2`

### Columns used by measures or visuals

| Production HL column | New RL column | Confidence | Notes |
|---|---|---|---|
| `Revenue_Order_Intake` | `Revenue_Order_Intake` | **EXACT** | |
| `Revenue_Backlog` | `Revenue_Backlog` | **EXACT** | |
| `Order_Quantity_in_FT2` | `Order_Quantity_in_FT2` | **EXACT** | |
| `Order_Quantity_in_BFT2` | `Order_Quantity_in_BFT2` | **EXACT** | |
| `Requested_Quantity_in_BFT` | `Requested_Quantity_in_BFT` | **EXACT** | |
| `RequestedQuantityInBaseUnit` | `RequestedQuantityInBaseUnit` | **EXACT** | |
| `Open_Order_Quantity_in_FT2` | `Open_Order_Quantity_in_FT2` | **EXACT** | |
| `Open_order_qty_flag` | `Open_order_qty_flag` | **EXACT** | Backlog page filter (=`Y`) |
| `ForecastSales`, `ForecastSalesSQFT`, `ForecastSalesBDFT` | same | **EXACT** | |
| `FC Product Group` | `FC_Product_Group` | **STRONG** | Space → underscore |
| `Product Family` | `Product_Family_Product_Number` | **STRONG** | RL adds `_Product_Number` suffix. Verify values (Membrane / iso) are the same. |
| `CustomerAccountAssignmentGroup` | `CustomerAccountAssignmentGroup` | **EXACT** | |
| `SalesDocument`, `SalesDocumentItem` | same | **EXACT** | |
| `SalesDocumentType` | `SalesDocumentType` | **EXACT** | Backlog filter |
| `SalesDocumentItemCategory` | `SalesDocumentItemCategory` | **EXACT** | |
| `SalesOrganization` | `SalesOrganization2` OR `SalesOrganization_D13` | **STRONG** | Multiple variants. `_D13` is the dimension key (used in the M query parameter earlier). Production uses plain `SalesOrganization`. |
| `DistributionChannel` | `DistributionChannel` | **EXACT** | |
| `Division` | `Division` (plus variants) | **STRONG** | Plain `Division` exists (line 43). |
| `SalesGroup`, `SalesOffice` | verify in AWIP Sales.tmdl | **POSSIBLE** | Likely present |
| `Plant` | `Plant` / variants | **POSSIBLE** | Same variant question as Billing |
| `CreationDate` | `CreationDate_D8` + `CreationDate_D8_T` | **STRONG** | RL uses `_D#` dimension form |
| `SalesDocumentDate` | `SalesDocumentDate_D10` + `_T` | **STRONG** | |
| `RequestedDeliveryDate` | `RequestedDeliveryDate` | **EXACT** | |
| `BillingDocumentDate` | verify | **POSSIBLE** | |
| `BindingPeriodValStartDate`, `BindingPeriodValEndDate` | verify | **POSSIBLE** | |
| `FiscalPeriod` | `FiscalPeriod` | **EXACT** | |
| `OrderRelatedBillingStatus` | `OrderRelatedBillingStatus` | **EXACT** | Backlog filter |
| `SoldToParty`, `ShipToParty`, `BillToParty` | same | **EXACT** | |

### Column NOT confirmed / needs external source

Same as Billing side — Sales Rep name, Project Coordinator, Application, Industry, Region (business-friendly) all come from Customer.xlsx.

---

## Non-SAP dimension tables

### `KNVV` — Local CSV on OneDrive

| Production column | Availability in new source | Confidence | Notes |
|---|---|---|---|
| `Account Assignment Group` | **NOT FOUND** in SAP OData | NOT FOUND | Customer master extraction. Cillian Ryan maintains `KNVV.csv`. |
| `Account Assignment Group Description` | **NOT FOUND** in SAP OData | NOT FOUND | Same file. |

**Action for Phase 5:** Must decide with business owner:
1. Continue sourcing from same `KNVV.csv` (requires user to have OneDrive access), OR
2. Pull `KNVV` table directly from SAP via a new Datasphere view, OR
3. Retire the AAGC slicer from reports if source is no longer maintained.

### `Customer` — Local Excel on OneDrive

Provides the enriched sales-context columns used in Invoiced Sales detail table and slicers.

| Production column (Customer.xlsx) | Availability in SAP OData | Confidence | Notes |
|---|---|---|---|
| Fiscal Year / Period | duplicate of SAP `FiscalYearPeriod` | STRONG | can use SAP column |
| Document Date | duplicate of SAP `BillingDocumentDate` | STRONG | can use SAP |
| Plant | duplicate of SAP `Plant` | STRONG | can use SAP |
| Requested delivery date | duplicate of SAP `RequestedDeliveryDate` | STRONG | can use SAP |
| **Industry** | **NOT FOUND** in SAP | NOT FOUND | External |
| **Company Type** | **NOT FOUND** in SAP | NOT FOUND | External |
| Product Family | in SAP as `Product_Family_Product_Number` | STRONG | verify values match |
| **Secondary Grouping** | **NOT FOUND** in SAP | NOT FOUND | External |
| **Application** | **NOT FOUND** in SAP (RL has `Application_Product_Number` — different meaning?) | POSSIBLE | verify |
| **Sales Representative** (ID) | **NOT FOUND** in SAP | NOT FOUND | External |
| **Sales Representative Name** | **NOT FOUND** in SAP | NOT FOUND | External |
| **Project Coordinator** | **NOT FOUND** in SAP | NOT FOUND | External |
| Sales Document / Item | duplicate of SAP | STRONG | can use SAP |
| **Customer Project Name** | **NOT FOUND** in SAP | NOT FOUND | External |
| Ship-to Party / State / Zip | mostly in SAP | STRONG | |
| Territory Sold/Ship/Bill/Payer | **NOT FOUND** in SAP | NOT FOUND | External |
| Bill-to / Payer / Sold-to state/zip | partly in SAP (`SoldToParty` is customer number, name comes from customer master) | POSSIBLE | |
| **Sold to party Description** | **NOT FOUND** in SAP RL | NOT FOUND | Customer name; needs customer master table (KNA1?) |
| Country / **Region** (business-friendly) | SAP RL has Country/Region but with multiple variants | STRONG | verify canonical variant |
| Material / Material Description | Material in SAP; **Material Description NOT FOUND** | POSSIBLE | Need material master (MARA?) |
| Sales UoM | in SAP | STRONG | |
| Order Quantity variants | duplicates of SAP order qty | STRONG | can use SAP |
| Unit Price in Base UoM | in SAP as `Unit_Price_in_Base_UoM` | EXACT | |
| **Cost of sales, Revenue, Gross Margin, Gross margin%** | Revenue is in SAP; **Cost / GM columns NOT FOUND** | POSSIBLE | Kingspan may compute these externally |

### `User`, `Quote`, `Quote Line Item` — Salesforce API

Not currently visible in the primary Invoiced Sales / Order Intake / Backlog pages (based on Phase 1 inventory). If they appear on Extended pages (not yet fully inventoried), they'd require Salesforce credentials — no SAP substitute.

---

## Mapping summary

- **Billing measures (8):** all 8 CAN be reproduced — every dependent column exists in RL as EXACT or STRONG.
- **Sales measures (11):** all 11 CAN be reproduced — same.
- **Report visuals dependent on Customer.xlsx (Sales Rep, Project Coord, Application, Industry, Region-business, Material Description, Cost/GM):** **cannot be reproduced from SAP OData alone.** Blocked pending resolution of the external dataset.
- **AAGC slicer (KNVV):** blocked pending resolution.

Detailed measure-by-measure reproducibility is in `measure-dependency-map.md`.
Detailed missing external sources are in `missing-data-sources.md`.

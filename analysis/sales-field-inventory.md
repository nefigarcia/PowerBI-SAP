# Sales.pbix — Field Inventory (New Source)

**Source:** `Sales.pbix` (extracted to `_extract/Sales/`).

## Extraction limitation

Same as Billing.pbix: the report has 0 visuals; the data model is in the binary DataModel (~500 KB, XPress-compressed) and can't be read directly.

## Working proxy: `AWIP_Commercial_Sales.PBIP` SalesOrders table

The `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/SalesOrders.tmdl` file (3,460 lines) is sourced from `SAP_SD_RL_SalesDocumentItem_V2` — the same view Sales.pbix connects to.

## M source (verbatim from AWIP proxy)

```m
let
    Source = SapDataWarehouseCloudConnector.Contents(
        #"p_DatasphereServer",
        "analytical",
        #"p_DatasphereSpace",
        "SAP_SD_RL_SalesDocumentItem_V2",
        "SalesOrganization_D13='IN """ & #"p_SalesOrganization" & """'"
    ),
    Typed = Table.TransformColumns(Source, {
        {"CreationDate_D8",       each try Date.From(_) otherwise null, type nullable date},
        {"IncSalesOrdNetAmnt_CC", each try Number.From(_) otherwise null, Currency.Type},
        {"IncSalesOrdNetAmnt",    each try Number.From(_) otherwise null, Currency.Type},
        {"NetPriceAmount",        each try Number.From(_) otherwise null, Currency.Type},
        {"IncSalesOrderQty",      each try Number.From(_) otherwise null, type number},
        {"OrderQuantity",         each try Number.From(_) otherwise null, type number}
    })
in
    Typed
```

## Columns confirmed to exist (subset relevant to production)

### Keys
- `SalesDocument`, `SalesDocumentItem`
- Various document-item categories: `SalesDocumentItemCategory`, `SalesDocumentType`

### Dates
- `CreationDate_D8` + `_T` (= HL `CreationDate`)
- `SalesDocumentDate_D10` + `_T` (= HL `SalesDocumentDate`)
- `LastChangeDate_D9` + `_T` (= HL `LastChangeDate`)
- `RequestedDeliveryDate` (verify — production has this)
- `BindingPeriodValStartDate`, `BindingPeriodValEndDate` (verify)
- `BillingDocumentDate` (verify)
- Attribute dates: `DocDate_A_10`, `Changedat_*`, etc.

### Fiscal
- `FiscalPeriod` (= HL — EXACT)

### Product
- `FC_Product_Group` (= HL `FC Product Group` — space→underscore)
- `FC_Product_Group_Product_Number` (variant)
- `Product_Family_Product_Number` — the RL equivalent of production `Product Family` (needs value-domain verification)
- `Application_Product_Number` — RL exposes this, production `Application` comes from Customer.xlsx — likely NOT the same field

### Customer / Org
- `CustomerAccountAssignmentGroup` + `_T` (= HL — for KNVV relationship)
- `CustomerFullName` + variants `CustomerFullName1..3`
- `SalesOrganization2` (plain SalesOrganization)
- `SalesOrganization_D13` + `_T` (dimension key form, used in M parameter)
- `DistributionChannel` + `_T`
- `Division` + `_T`, plus `Division2` + `_T`, `Division_Product_Number` + `_T`

### Backlog-related
- `Open_order_qty_flag` (= HL — EXACT, Backlog page filter)
- `Open_Order_Quantity_in_FT2` (= HL — EXACT)
- `Open_Order_Quantity_in_BFT2`, `Open_Order_Quantity_in_M2`, `Open_Order_Quantity_in_Base_UoM`, `Open_Order_Quantity_in_Base_UOM_with_Signs`, `Open_quantity_in_Sales_UoM`
- `OrderRelatedBillingStatus` + `_T` (= HL — Backlog filter)

### Quantities
- `Order_Quantity_in_FT2` (= HL — EXACT)
- `Order_Quantity_in_BFT2` (= HL — EXACT)
- `Order_Quantity_in_M2`, `Order_Quantity_in_FT2` (variants)
- `Requested_Quantity_in_BFT` (= HL — EXACT)
- `RequestedQuantityInBaseUnit` (= HL — EXACT)
- `OrderQuantity`, `OrderQuantityUnit`, `TargetQuantity`, `TargetQuantityUnit`
- `ConfdDelivQtyInOrderQtyUnit`, `ConfdDeliveryQtyInBaseUnit`, `TargetDelivQtyInOrderQtyUnit`
- `MinDeliveryQtyInBaseUnit`

### Amounts
- `Revenue_Order_Intake` (= HL — EXACT)
- `Revenue_Backlog` (= HL — EXACT)
- `NetPriceAmount`, `NetPriceQuantity`, `NetPriceQuantityUnit`
- `IncSalesOrdNetAmnt`, `IncSalesOrdNetAmnt_CC` (Incoming Sales Order Net Amount, in transaction and company code currency)
- `IncSalesOrderQty`
- `QuotBasedSalesOrdNetAmnt`, `QuotBasedSalesOrdNetAmnt_CC` (Quote-based sales order — separate from Salesforce Quotes)
- `CustReturnsNetAmnt`, `CustReturnsNetAmnt_CC`, `CustReturnsQty`
- `Subtotal1Amount..Subtotal6Amount`
- `SUBTOTAL1AMOUNT_CC_CUR..SUBTOTAL6AMOUNT_CC_CUR`
- `Unit_Price`, `Unit_Price_in_Base_UoM`

### Forecast
- `ForecastSales` (= HL — EXACT)
- `ForecastSalesSQFT` (= HL — EXACT)
- `ForecastSalesBDFT` (= HL — EXACT)

### Prior year
- `PY_Sales_Order_Quantity_in_Base_UoM` (verify)

## Columns NOT confirmed in RL vs. production visuals

Same customer.xlsx enrichment fields as Billing: Sales Rep name, Project Coord, Application (business), Industry, Region-business, Customer Project Name, Material Description, Cost/Margin.

## Field count observations

- RL Sales exposes **~430 columns**
- Production HL uses ~35 columns directly in visuals or measure DAX
- **Coverage:** all 35 production-referenced columns exist in RL (with space→underscore + `_D#` conventions)

## Key confirmed differences vs. production HL

| Production HL | New RL | Difference type |
|---|---|---|
| `FC Product Group` | `FC_Product_Group` | Space → underscore |
| `Product Family` | `Product_Family_Product_Number` | Suffix change (verify value domain) |
| `CreationDate` | `CreationDate_D8` | `_D#` dimension key form |
| `SalesDocumentDate` | `SalesDocumentDate_D10` | Same |
| `LastChangeDate` | `LastChangeDate_D9` | Same |
| `SalesOrganization` | `SalesOrganization2` or `SalesOrganization_D13` | Multiple variants |
| `Division` | `Division` or `Division2` or `Division_Product_Number` | Multiple variants |

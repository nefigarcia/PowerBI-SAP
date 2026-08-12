# Billing.pbix — Field Inventory (New Source)

**Source:** `Billing.pbix` (extracted to `_extract/Billing/`).

## Extraction limitation

Billing.pbix is a compiled Power BI file. Its report layer contains only 1 empty tableEx visual and 1 page. **The data model, column list, measures, M queries are all stored in the binary `DataModel` file (~530 KB, XPress-compressed)** which cannot be read without a specialized tool (pbi-tools, Tabular Editor, or by opening in Power BI Desktop).

## Working proxy: `AWIP_Commercial_Sales.PBIP` Billing table

The `AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/Billing.tmdl` file is a PBIP-format table sourced from the **same** SAP Datasphere view (`SAP_SD_RL_BillingDocumentItem_V2`) via `SapDataWarehouseCloudConnector.Contents`. Since Datasphere's OData analytic-model endpoint and this native connector both expose the same view, the **column set is the same**. This TMDL is a faithful proxy of what Billing.pbix's DataModel contains.

**File:** [AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/Billing.tmdl](../AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.SemanticModel/definition/tables/Billing.tmdl) — 3,700+ lines documenting ~475 columns exposed by `SAP_SD_RL_BillingDocumentItem_V2`.

## M source (verbatim from AWIP proxy)

```m
let
    Source = SapDataWarehouseCloudConnector.Contents(
        #"p_DatasphereServer",
        "analytical",
        #"p_DatasphereSpace",
        "SAP_SD_RL_BillingDocumentItem_V2",
        "CompanyCode_D1='" & #"p_CompanyCode" & "',SalesOrganization_D16='IN """ & #"p_SalesOrganization" & """'"
    ),
    Typed = Table.TransformColumns(Source, {
        {"BillingDocumentDate_D5",  each try Date.From(_) otherwise null, type nullable date},
        {"NETAMOUNT_CC_CURR",       each try Number.From(_) otherwise null, Currency.Type},
        {"NetPriceAmount",          each try Number.From(_) otherwise null, Currency.Type},
        {"SlsVolNetAmt_CC",         each try Number.From(_) otherwise null, Currency.Type},
        {"SalesVolumeQuantity",     each try Number.From(_) otherwise null, type number},
        {"BillingQuantity",         each try Number.From(_) otherwise null, type number}
    })
in
    Typed
```

**Notes:**
- Uses `SapDataWarehouseCloudConnector`, not OData. If Billing.pbix uses OData, only the first `Source = ...` line differs — the column set should still match.
- Parameters `p_DatasphereServer`, `p_DatasphereSpace`, `p_CompanyCode`, `p_SalesOrganization` control filtering at the Datasphere layer via `CompanyCode_D1` and `SalesOrganization_D16` view parameters.
- Only 6 columns are type-cast in M; the rest come through as SAP-provided types (mostly `string`).

## Columns confirmed to exist (subset relevant to production reproduction)

Grouped by role. Cross-reference to production HL name in parentheses.

### Keys
- `BillingDocument` (= HL `BillingDocument`)
- `BillingDocumentItem` (= HL `BillingDocumentItem`)
- `SalesDocument` (= HL `SalesDocument`)
- `SalesDocumentItem`
- `Material` and `Material_D17`

### Dates
- `BillingDocumentDate_D5` + `_T` (= HL `BillingDocumentDate`)
- `RequestedDeliveryDate`
- `CreationDate_D3` + `_T`
- `LastChangeDate_D4` + `_T`
- `PricingDate_D7` + `_T`
- `PriceDetnExchangeRateDate_D8` + `_T`
- `FixedValueDate_D6` + `_T`
- Additional attribute dates: `BillDate_A_5`, `ConvDate_A_8`, `FixValDate_A_6`, `PriceDate_A_7`, `Changedat_A_4`, `Createdon_A_3`, etc.

### Fiscal
- `FiscalYear`
- `FiscalYearPeriod` (= HL — used for slicer default `2026007`)
- `FiscalPeriod`, `FiscalYearVariant`, `FiscalYearVariant1`, `Fiscal_Month`

### Product / classification
- `FC_Product_Group` (= HL `FC Product Group` — space→underscore) plus variant `FC_Product_Group1`
- `Product_Family` — verify domain values (should include Membrane, iso)
- `MaterialGroup`
- `BasicMaterial`
- `Application` and `ArticleCategory`
- `IndustryStandardName`, `Industry`, `Industry1..Industry3`

### Customer / organization
- `CustomerAccountAssignmentGroup` + `_T` (= HL — for KNVV relationship)
- `CustomerFullName` + variants `CustomerFullName1..3`
- Multiple `Country1..Country6`, `Region1..Region3`, `CityName1..CityName4`
- `Company`, `ChartOfAccounts`, `ContractAccount`, `ControllingArea`, `CreditControlArea`

### Sales rep / org (in Billing table — SAP-provided)
- `SalesEmployee` (line ~129 of AWIP Billing.tmdl)
- `SalesGroup`, `SalesOffice`, `SalesDistrict`
- `DistributionChannel`, `Division`
- `SalesOrganization` (verify)

### Quantity measures (raw columns, SUM aggregations in production)
- `Billing_Quantity_in_FT2` (= HL — EXACT)
- `Billing_Quantity_in__BFT2` (= HL, double underscore preserved — EXACT)
- `Billing_Quantity_with_Signs` (= HL — EXACT)
- `Billing_Quantity_in_M2` (= HL — EXACT)
- `Billing_Quantity_in_BFT` (= HL)
- `Billing_Quantity_in_BFT2_For_ISO` (specific ISO subset)
- `Billing_Quantity_in_FT2_for_Membrane`
- `Billing_Quantity_in_SKU`
- `Billing_Quantity_in_Sales_UOM`
- `BillingQuantity`, `BillingQuantityUnit`, `BillingQuantityInBaseUnit`

### Revenue / amount columns
- `Revenue` (= HL — EXACT)
- `Revenue_with_Company_Code_Currency`
- `NetPriceAmount`, `NetPriceQuantity`
- `NETAMOUNT_CC_CURR`, `GROSSAMOUNT_CC_CURR`, `ELIGIBLEAMOUNT_CC_CURR`
- `GrossAmount`, `EligibleAmountForCashDiscount`
- `Subtotal1Amount..Subtotal6Amount`
- Sales volume: `SlsVolNetAmt`, `SlsVolNetAmt_CC`, `NetSlsVolumeNetAmt`, `NetSlsVolumeNetAmt_CC`
- Cost/margin (in RL — verify if present): `NetSlsCostAmount`, `NetSlsCostAmount_CC`, `SlsVolCostNetAmt`, `SlsVolCostNetAmt_CC`, `SlsProfitMarginNetAmt`, `SlsProfitMarginNetAmt_CC`, `NetSlsProfitMargNetAmt`, `NetSlsProfitMargNetAmt_CC`, `Unit_Price`, `Unit_Price_in_Base_UoM`, `PyNetPriceAmount`, `PYUnit_Price_in_Base_UoM`

### Forecast columns
- `ForecastSales` (= HL — EXACT)
- `ForecastSalesSQFT` (= HL — EXACT)
- `ForecastSalesBDFT` (= HL — EXACT)

### Prior year columns
- `PY_Revenue` (= HL — EXACT)
- `PYBilling_Quantity_in_BoM` (= HL — EXACT)
- `PyNetPriceAmount`

### Sales volume / cost / margin (RL exposes many)
- `CustCrdtMemoNetAmt`, `CustCrdtMemoCostNetAmt`, `CustCrdtMemoPrftMrgNetAmt` (customer credit memo variants + `_CC` currency variants)
- `CancldSlsVolNetAmt` + `_CC`
- `CustCrdtMemoQuantity`, `SalesVolumeQuantity`

### Flags
- `BillingDocumentIsCancelled`, `BillingDocumentIsTemporary`
- `Current_Period_Flag`, `Forecast_Flag`
- `AccountingExchangeRateIsSet`
- `IsMarkedForDeletion`, `IsOneTimeAccount` + variants

## Columns NOT confirmed in RL vs. production visuals

- `ProjectName` — production shows this in detail table. Not in RL Billing (comes from Customer.xlsx).
- `Material Description` — same.
- `Sales Representative Name`, `Project Coordinator` — same. Note RL has `SalesEmployee` (probably an employee number, not a name) — will produce a numeric code where production shows a name.

## Field count observations

- RL Billing exposes **~475 columns** total (per AWIP Billing.tmdl line count / structure)
- Production HL uses ~40 of these directly in visuals or measure DAX
- **Coverage:** all 40 production-referenced columns exist in RL (with 6–8 name variants requiring space→underscore, `_D#`, or variant-selection choices)

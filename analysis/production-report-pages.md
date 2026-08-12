# Production Report Pages Inventory

**Source:** `production-reference/Amalgamated Sales Production.Report/definition/`
**Extraction method:** Direct read of PBIP `page.json` and `visual.json` files (READ ONLY).

## Report-level config

- **Theme:** CY26SU05 (Shared Resources) — Kingspan branding, primary color `#004288`, accent `#C0995D`
- **Report-level filters:** *None* (all filters are page or visual level)
- **Enhanced settings enabled:** `useStylableVisualContainerHeader`, `useEnhancedTooltips`, `useDefaultAggregateDisplayName`, `defaultDrillFilterOtherVisuals`

## Page order (from `pages.json`)

| Ord | GUID | displayName | Visuals |
|-----|------|-------------|---------|
| 0 | `76b1cd50241131d198dc` | Invoiced Sales - Dashboard | 16 |
| 1 | `4c2a62afe18e95907a8b` | Invoiced Sales - Detail | 6 |
| 2 | `4a182fabaa835894b97a` | Extended Invoiced Sales - Dashboard | 14 |
| 3 | `330491e0244bbed41069` | Order Intake - Dashboard | 16 |
| 4 | `6d21068a5db0ab200838` | Order Intake - Detail | 7 |
| 5 | `2ac9bb486359319b2006` | Extended Order Intake - Dashboard | 16 |
| 6 | `d7d82ccc80735b013d61` | Backlog | 11 |
| 7 | `c315f0779353e20bc094` | Backlog - Details | 5 |
| 8 | `5633c2a8bb88a89820a0` | Backlog by Rep | 7 |

**Total: 9 pages, ~100 visuals.** Canvas 1280×720 on every page.

## Page: Invoiced Sales - Dashboard  `76b1cd50241131d198dc`

Home dashboard for Billing. No page-level filters.

| Visual GUID | Type | Title | Key fields | VL filters |
|---|---|---|---|---|
| `86465bfc619521979cee` | actionButton | (home icon) | — | PageNavigation → section `4cebd6cd708bb1448d5f` |
| `2025b6cc00e14097ebd0` | slicer | Fiscal Period | `SAP_SD_HL_BillingDocumentItem_V2.FiscalYearPeriod` | default = `2026007` |
| `50cadbb04ce0504e8db4` | slicer | Product Family | `SAP_SD_HL_BillingDocumentItem_V2.FC Product Group` | — |
| `f49203885a06cd64790d` | slicer | AAGC Description | `KNVV.Account Assignment Group Description` | — |
| `7e3c61a6822d9301a682` | shape | (decorative) | — | — |
| `35978c6bcc04d0e402d0` | **card** | **ISO Rate** | `SAP_SD_HL_BillingDocumentItem_V2.ISO Rate IS` (measure) | — |
| `1c88c846621bcda65ceb` | **card** | **ISO Rate Fcst** | `SAP_SD_HL_BillingDocumentItem_V2.ISO Rate Fcst IS` (measure) | FC Product Group |
| `163d1500dea449809edd` | multiRowCard | Invoiced Sales - $ | `Revenue`, `ForecastSales`, `PY_Revenue` | — |
| `b131e4c5eb0998a50064` | gauge | Invoiced Sales $ | MaxValue=`ForecastSales`, Y=`Revenue` | — |
| `ed7d18d2ecd4029810d0` | multiRowCard | Invoiced Membrane - sqft | `Billing_Quantity_in_FT2`, `ForecastSalesSQFT`, `PYBilling_Quantity_in_BoM` | FC Product Group=TPO, BaseUnit=FT2 |
| `eacd277a817be0221185` | gauge | Invoiced Membrane - sqft | MaxValue=`ForecastSalesSQFT`, Y=`Billing_Quantity_in_FT2` | FC Product Group=TPO, BaseUnit=FT2 |
| `183f4dd7cc2e57220909` | multiRowCard | Invoiced ISO - bdft | `BillingQuantityInBaseUnit`, `ForecastSalesBDFT`, `PYBilling_Quantity_in_BoM` | FC Product Group=ISO |
| `3a8a5b4f7e17722e812e` | gauge | Invoiced ISO - Board Foot | MaxValue=`ForecastSalesBDFT`, Y=`BillingQuantityInBaseUnit` | FC Product Group=ISO |
| `e5664335014e349c21d2` | tableEx | (detail table, 18 cols) | FiscalYearPeriod, BillingDocument(+Item), FC Product Group, Billing_Quantity_in_FT2, Billing_Quantity_in_BFT, Unit_Price, Unit_Price_in_Base_UoM, Revenue, BillingQuantityInBaseUnit, MaterialGroup, Material Description, Plant, SalesDocument, ProjectName, BillingDocumentDate, RequestedDeliveryDate, Sales Representative, Project Coordinator, Billing_Quantity_in_M2 | 9+ categorical filters |
| `d76a7768069cc600bc02` | actionButton | Clear all Slicers | — | action=ClearAllSlicers |
| `b9386d59380b7a007738` | image | (Kingspan logo) | `kingspan-roofing-waterproofing8422940714883275.png` | — |

## Page: Invoiced Sales - Detail  `4c2a62afe18e95907a8b`

6 visuals. Detail drill from dashboard.

- `d3f806fcee8d8306d850` slicer "Product Family" — `SAP_SD_HL_BillingDocumentItem_V2.FC Product Group` (inverted selection)
- `d641c1d914cac10e5795` actionButton (back arrow) — PageNavigation
- 4 remaining visuals: (populated after sub-agent finishes deeper pass)

## Page: Extended Invoiced Sales - Dashboard  `4a182fabaa835894b97a`

14 visuals. Extended slice/analysis of Billing.

## Page: Order Intake - Dashboard  `330491e0244bbed41069`

16 visuals. Mirror of Invoiced Sales but sourced from `SAP_SD_HL_SalesDocumentItem_V2`.

- `6a782df633369c11d0e7` gauge — MaxValue=`ForecastSalesSQFT`, Y=`Order_Quantity_in_FT2`
- Similar KPI structure to Invoiced Sales dashboard using OI equivalents: `Revenue_Order_Intake`, `Order_Quantity_in_BFT2`, `ISO Rate OI`, `ISO Rate Fcst OI`

## Page: Order Intake - Detail  `6d21068a5db0ab200838`

7 visuals.
- `536f6f72777fc8637d53` slicer "Fiscal Period" — `SAP_SD_HL_SalesDocumentItem_V2.FiscalPeriod` (default `2026007`)

## Page: Extended Order Intake - Dashboard  `2ac9bb486359319b2006`

16 visuals.

## Page: Backlog  `d7d82ccc80735b013d61`

11 visuals. **Page-level filters:**
- `SAP_SD_HL_SalesDocumentItem_V2.Open_order_qty_flag` = 'Y'
- `SalesDocumentType` (categorical, no restriction values)
- `OrderRelatedBillingStatus` (categorical)

## Page: Backlog - Details  `c315f0779353e20bc094`

5 visuals. Page-level filter: `Open_order_qty_flag` = 'Y'.

## Page: Backlog by Rep  `5633c2a8bb88a89820a0`

7 visuals. Page-level filter: `Open_order_qty_flag` = 'Y'.

---

## KPI/measure usage catalog

Cross-referencing every distinct measure/column visible in dashboards:

| Field/Measure | Source table | Type | First seen on page |
|---|---|---|---|
| Revenue | Billing_V2 | column (SUM) | Invoiced Sales Dashboard |
| ForecastSales | Billing_V2 | column | Invoiced Sales Dashboard |
| ForecastSalesSQFT | Billing_V2 | column | Invoiced Sales Dashboard |
| ForecastSalesBDFT | Billing_V2 | column | Invoiced Sales Dashboard |
| Billing_Quantity_in_FT2 | Billing_V2 | column | Invoiced Sales Dashboard |
| Billing_Quantity_in_BFT | Billing_V2 | column | Invoiced Sales Dashboard |
| Billing_Quantity_in__BFT2 | Billing_V2 | column | Invoiced Sales (measure dep) |
| Billing_Quantity_in_M2 | Billing_V2 | column | Invoiced Sales table |
| Billing_Quantity_with_Signs | Billing_V2 | column | ISO AOP $/bdft IS |
| BillingQuantityInBaseUnit | Billing_V2 | column | Invoiced Sales Dashboard |
| PYBilling_Quantity_in_BoM | Billing_V2 | column | Invoiced Sales Dashboard |
| PY_Revenue | Billing_V2 | column | Invoiced Sales Dashboard |
| **ISO Rate IS** | Billing_V2 | **measure** | Invoiced Sales card |
| **ISO Rate Fcst IS** | Billing_V2 | **measure** | Invoiced Sales card |
| Revenue_Order_Intake | Sales_V2 | column (SUM) | Order Intake Dashboard |
| Order_Quantity_in_FT2 | Sales_V2 | column | Order Intake gauge |
| Order_Quantity_in_BFT2 | Sales_V2 | column | ISO AOP $/bdft OI |
| Requested_Quantity_in_BFT | Sales_V2 | column | measure deps |
| RequestedQuantityInBaseUnit | Sales_V2 | column | measure deps |
| Open_Order_Quantity_in_FT2 | Sales_V2 | column | measure deps |
| Open_order_qty_flag | Sales_V2 | column | Backlog page filter |
| Revenue_Backlog | Sales_V2 | column | Total Backlog $ measure |
| **ISO Rate OI** | Sales_V2 | **measure** | Order Intake dashboard (implied) |
| **ISO Rate Fcst OI** | Sales_V2 | **measure** | Order Intake dashboard (implied) |
| **ISO Rate SB** | Sales_V2 | **measure** | (Backlog related) |
| **Total Backlog $** | Sales_V2 | **measure** | Backlog page |
| FiscalYearPeriod | Billing_V2 | column | slicer default `2026007` |
| FiscalPeriod | Sales_V2 | column | slicer default `2026007` |
| FC Product Group | both | column | slicer + measure filter (values: TPO, ISO) |
| Product Family | Sales_V2 | column | measure filter (values: iso, Membrane) |
| MaterialGroup | Billing_V2 | column | detail table |
| Material Description | Billing_V2 (via Customer table?) | column | detail table |
| Plant | Billing_V2 | column | detail table |
| SalesDocument | both | column | detail table |
| ProjectName | Billing_V2 | column | detail table |
| BillingDocumentDate | Billing_V2 | column | detail table |
| RequestedDeliveryDate | Billing_V2 | column | detail table |
| Sales Representative | Billing_V2 or User | column | detail table |
| Project Coordinator | Billing_V2 or User | column | detail table |
| Unit_Price | Billing_V2 | column | detail table |
| Unit_Price_in_Base_UoM | Billing_V2 | column | detail table |
| BaseUnit | Billing_V2 | column | visual filter |
| SalesDocumentType | Sales_V2 | column | Backlog filter |
| OrderRelatedBillingStatus | Sales_V2 | column | Backlog filter |
| KNVV.Account Assignment Group Description | KNVV | column | slicer |

**Deeper inventory of Extended pages and Backlog pages pending (sub-agent extracted top-level list; per-visual detail for those pages to be filled after second pass or once user prioritizes).**

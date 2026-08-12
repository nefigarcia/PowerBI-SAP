# Production Relationships

**Source:** `production-reference/Amalgamated Sales Production.SemanticModel/definition/relationships.tmdl` (274 lines).
**Total:** 56 relationships — 8 business, 48 auto-generated for LocalDateTable Time Intelligence.

## Business relationships (8)

| # | From | To | From card. | To card. | Cross-filter | Active | joinOnDate | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `SAP_SD_HL_BillingDocumentItem_V2.CustomerAccountAssignmentGroup` | `KNVV.'Account Assignment Group'` | many | one | **both** | true | none | Billing → KNVV bidirectional (CSV source) |
| 2 | `Customer.Material` | `SAP_SD_HL_BillingDocumentItem_V2.Material` | **one** | many | **both** | true | none | Excel Customer → Billing (many-to-many-like via bidirectional) |
| 3 | `Quote.CreatedById` | `User.Id` | many | one | single | true | none | Salesforce; annotation `PBI_IsFromSource = FS` |
| 4 | `Quote.LastModifiedById` | `User.Id` | many | one | single | **false** | none | inactive |
| 5 | `'Quote Line Item'.QuoteId` | `Quote.Id` | many | one | single | true | none | Salesforce |
| 6 | `'Quote Line Item'.CreatedById` | `User.Id` | many | one | single | **false** | none | inactive |
| 7 | `'Quote Line Item'.LastModifiedById` | `User.Id` | many | one | single | **false** | none | inactive |
| 8 | `SAP_SD_HL_SalesDocumentItem_V2.CustomerAccountAssignmentGroup` | `KNVV.'Account Assignment Group'` | many | one | **both** | true | none | Sales → KNVV bidirectional |

### Observations

- **Only 2 relationships link the two SAP fact tables to anything else** (both to KNVV via `CustomerAccountAssignmentGroup`).
- **No direct Billing ↔ Sales relationship.** The two fact tables are independent islands connected only via KNVV (customer AAG dimension).
- **`Customer` (Excel) → `Billing.Material`** relationship carries all the enriched fields (Application, Industry, Sales Rep Name, Project Coordinator, Region, etc.) INTO the Billing fact. Direction is `Customer` (one side) → `Billing` (many side), bidirectional cross-filter — meaning filters on Billing can filter Customer and vice-versa.
- **NO relationship between `Customer` (Excel) and `SAP_SD_HL_SalesDocumentItem_V2`.** This means Order Intake / Backlog visuals **cannot use Customer.xlsx enrichment fields**. Only Billing (Invoiced Sales) benefits from Customer.xlsx joins.
- **Quote/QLI/User form a separate Salesforce sub-graph** with no relationship to the SAP or KNVV or Customer sides. They live in the model but don't join to sales/billing facts.
- **No relationship uses `joinOnDateBehavior: dateTimePartOnly`.** Date relationships are all handled through auto LocalDateTable variations.

## LocalDateTable relationships (48)

Auto-generated one per date column across:
- `SAP_SD_HL_BillingDocumentItem_V2`: BillingDocumentDate, ServicesRenderedDate, PricingDate, FixedValueDate, CreationDate, LastChangeDate, Fiscal_Month, RequestedDeliveryDate, and more (~10 date columns)
- `SAP_SD_HL_SalesDocumentItem_V2`: SalesDocumentDate, ServicesRenderedDate, PricingDate, ExchangeRateDate, RequestedDeliveryDate, BindingPeriodValStartDate, BindingPeriodValEndDate, BillingDocumentDate, CreationDate, LastChangeDate (~10 date columns)
- `Customer`: Document Date, Requested delivery date (2)
- `User`: LastLoginDate, LastPasswordChangeDate, CreatedDate, LastModifiedDate, SystemModstamp, PasswordExpirationDate, SuAccessExpirationDate, OfflineTrialExpirationDate, OfflinePdaTrialExpirationDate, LastViewedDate, LastReferencedDate (~11)
- `Quote`: CreatedDate, LastModifiedDate, SystemModstamp, LastViewedDate, LastReferencedDate, ExpirationDate (~6)
- `Quote Line Item`: CreatedDate, LastModifiedDate, SystemModstamp, LastViewedDate, LastReferencedDate, ServiceDate (~6)

All use `joinOnDateBehavior: datePartOnly` (implicit) and connect the fact date column to a hidden `LocalDateTable_<guid>.Date` column.

**Decision point for Phase 5:** the new model should EITHER (a) keep Time Intelligence auto-tables per date column, matching production exactly, OR (b) introduce a single shared DimDate. Production uses (a). To be maximally faithful, we should keep (a) in the reproduction.

## Cross-filter and cardinality summary

- **bothDirections** (bi-directional) on **3 relationships**: Billing→KNVV, Sales→KNVV, Customer→Billing. Bi-directional cross-filter on many-to-many-like joins is unusual but intentional — it lets a filter on KNVV.AAGC Description propagate BOTH to Billing AND to Sales facts, and lets Customer.Region filter Billing.
- All Salesforce relationships are **single** direction and **many-to-one** to `User.Id`.
- 3 Salesforce relationships are **inactive** (Quote.LastModifiedById, QLI.CreatedById, QLI.LastModifiedById) — these are alternate paths that would create ambiguity if active. They're kept inactive so you can invoke them explicitly via `USERELATIONSHIP` if needed.

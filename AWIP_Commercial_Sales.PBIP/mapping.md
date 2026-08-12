# AWIP Commercial Sales — Field Mapping

> **Purpose:** Document the fields consumed from the two SAP Datasphere Reuse Layer analytical models and the target semantic-model role each field plays. **This mapping must be verified against the actual Datasphere view exposure before the first refresh.** Column names below use SAP's published RL naming for these views — if your Datasphere space renames or filters them (aliases, technical `_D#` suffixes on parameters), adjust the M expression in `expressions.tmdl` and the column ref in `tables/*.tmdl` accordingly.

## Source models

| Alias in model | Source view                          | Space  | Parameters (from user) |
|----------------|--------------------------------------|--------|-------------------------|
| `Billing`      | `SAP_SD_RL_BillingDocumentItem_V2`   | `PR_KRW` | `CompanyCode_D1='6000'`, `SalesOrganization_D16='IN "6000"'` |
| `SalesOrders`  | `SAP_SD_RL_SalesDocumentItem_V2`     | `PR_KRW` | `SalesOrganization_D13='IN "6000"'` |

Both views are pre-filtered to the AWIP (Sales Organization `6000`) scope.

## Field role mapping

### Roles used across both tables

| Role                | Billing column                          | SalesOrders column                      | Notes |
|---------------------|-----------------------------------------|-----------------------------------------|-------|
| Sales organization  | `SalesOrganization`                     | `SalesOrganization`                     | Constant `6000` after parameter filter — kept for traceability, hidden. |
| Company code        | `CompanyCode`                           | *(via header — not exposed at item)*    | Constant `6000`, hidden. |
| Distribution channel| `DistributionChannel`                   | `DistributionChannel`                   | |
| Division            | `Division`                              | `Division`                              | Used as **Application** proxy — see below. |
| Customer (Sold-to)  | `SoldToParty`                           | `SoldToParty`                           | Key to Customer name; see `SoldToPartyName` if exposed. |
| Ship-to             | `ShipToParty`                           | `ShipToParty`                           | |
| Material            | `Material`                              | `Material`                              | |
| Material group      | `MaterialGroup`                         | `MaterialGroup`                         | |
| Plant               | `Plant`                                 | `Plant`                                 | |
| Sales district      | `SalesDistrict`                         | `SalesDistrict`                         | Used as **Region** proxy — see below. |
| Country             | `Country` *(or `SalesOrganizationCountry`)* | `Country`                           | For US-state map. |
| Region (state)      | `Region` *(customer master region)*     | `Region`                                | ISO region key (US state code). |
| Sales group         | `SalesGroup`                            | `SalesGroup`                            | |
| Sales office        | `SalesOffice`                           | `SalesOffice`                           | |
| Sales rep (person)  | `SalesEmployee` or `PersonResponsibleSalesPersonName` | `SalesEmployee` | **Verify** — some Datasphere deployments expose this as `SalesRep`, `Salesperson`, or a partner function; user must confirm. |
| Transaction currency| `TransactionCurrency`                   | `TransactionCurrency`                   | |
| Company currency    | `CompanyCodeCurrency`                   | *(often not on order item)*             | USD for company `6000`. |

### Billing-specific (Actual invoiced sales)

| Role                     | Column                            | Notes |
|--------------------------|-----------------------------------|-------|
| Invoice date             | `BillingDocumentDate`             | Primary date for **Sales** actuals; joined to `DimDate`. |
| Fiscal year              | `FiscalYear`                      | |
| Fiscal period            | `FiscalPeriod`                    | |
| Billing document         | `BillingDocument`                 | |
| Billing document item    | `BillingDocumentItem`             | |
| Billing document type    | `BillingDocumentType`             | `F2` invoice, `G2` credit-memo, etc. |
| SD document reason       | `SDDocumentReason`                | Cancellations. |
| Net amount (revenue)     | `NetAmount`                       | Revenue in `TransactionCurrency`. **Basis for Sales measures.** |
| Billed quantity          | `BillingQuantity`                 | Basis for Sales Quantity. |
| Billed quantity unit     | `BillingQuantityUnit`             | |

### SalesOrders-specific (Order Intake)

| Role                     | Column                            | Notes |
|--------------------------|-----------------------------------|-------|
| Order (creation) date    | `CreationDate`                    | **Order-intake** basis (booking date). Some RL views expose `SalesDocumentDate` for the same purpose — see verification notes. |
| Sales document           | `SalesDocument`                   | |
| Sales document item      | `SalesDocumentItem`               | |
| Sales document type      | `SalesDocumentType`               | `OR` standard order, `ZOR` variants, etc. |
| Order net amount         | `NetAmount`                       | Basis for **Order Intake** measure. |
| Order quantity           | `OrderQuantity`                   | Basis for Order Intake Quantity. |
| Order quantity unit      | `OrderQuantityUnit`               | |
| Requested delivery date  | `RequestedDeliveryDate`           | Not modeled in v1, but present. |
| Overall process status   | `OverallSDProcessStatus`          | Optional filter (open/closed). |

### Derived roles (not raw fields)

| Report label   | Backing field                              | Rationale |
|----------------|--------------------------------------------|-----------|
| **Application**| `Division` (both tables)                    | AWIP uses SAP Division to segregate application lines (C&I, Cold Storage, Intercompany, OEM). If the customer runs a dedicated `Application` custom field, remap in TMDL. |
| **Region**     | `Region` (US state ISO code)                | For the state-shaded US map. |
| **Sales Rep**  | `SalesEmployee` (person responsible)        | **Verify field name** — could be `PersonResponsibleName`, a partner-function `PartnerFunction = 'VE'`, etc. |
| **Product**    | `Material` + `MaterialGroup`                | `MaterialGroup` used for panels-vs-accessories split shown in the "Panels or Acce…" slicer. |

### Fields hidden as technical

The following are kept in the model (for lineage) but **hidden**:
`CompanyCode`, `SalesOrganization`, `CreatedByUser`, `LastChangedByUser`, `LastChangeDate`, all `_D#` parameter echoes, `SDDocumentCategory`, technical GUIDs, hash keys, and any `SAP__` prefixed audit columns exposed by the RL view.

## Date modeling

A **shared `DimDate` dimension** (`Date` type) is created spanning `2020-01-01` .. `2030-12-31`. It is related to:
- `Billing[BillingDocumentDate]` — single-direction, one-to-many (used by all Sales measures).
- `SalesOrders[CreationDate]` — single-direction, one-to-many (used by all Order Intake measures). If the business defines order-intake by `SalesDocumentDate` instead, swap the FK in `relationships.tmdl`.

Only one active date relationship per fact — no `USERELATIONSHIP` acrobatics needed for v1.

## Verification checklist (before first refresh)

- [ ] Confirm the exact column names for **sales representative** (`SalesEmployee` vs. custom).
- [ ] Confirm **Application** dimension: is `Division` the right backing field, or is there a custom `ApplicationCode`?
- [ ] Confirm **Region** column exposes ISO US-state codes (needed for the map).
- [ ] Confirm **order-intake date**: `CreationDate` vs. `SalesDocumentDate`.
- [ ] Confirm `NetAmount` is in `TransactionCurrency` and USD is the reporting currency for AWIP.
- [ ] Verify Datasphere parameter names still match `CompanyCode_D1` / `SalesOrganization_D16` / `SalesOrganization_D13` (these change if the model is re-published).

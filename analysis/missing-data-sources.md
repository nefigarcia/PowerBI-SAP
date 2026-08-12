# Missing / External Data Sources

**Scope:** Production tables + fields that DO NOT come from SAP Datasphere and therefore cannot be reproduced from the new Billing/Sales OData connections alone.

---

## 1. `KNVV` — Customer Account Assignment Group dimension

**Production source:**
```m
Csv.Document(File.Contents("C:\Users\cillian.ryan\OneDrive - Kingspan\KNVV.csv"), ...)
```

**Contents:** 2 columns — `Account Assignment Group`, `Account Assignment Group Description`.

**Used by:**
- Slicer on Invoiced Sales Dashboard ("AAGC Description")
- 2 bi-directional relationships:
  - `Billing[CustomerAccountAssignmentGroup]` → `KNVV[Account Assignment Group]`
  - `Sales[CustomerAccountAssignmentGroup]` → `KNVV[Account Assignment Group]`

**Impact if not sourced:** The AAGC Description slicer cannot filter reports. Users can only filter by the raw code `CustomerAccountAssignmentGroup` (which is available directly on both SAP fact tables).

**Options:**
1. **Continue sourcing from same CSV** (fastest — but keeps dependency on Cillian's OneDrive)
2. **Point at a shared/central copy** (SharePoint or Azure Blob) so the file isn't tied to one person's OneDrive
3. **Expose KNVV via Datasphere** — SAP KNVV is a customer master table; can be added as a new Datasphere view
4. **Drop the AAGC slicer** — if the description isn't business-critical

**Recommended action:** ask business owner (Ana / James) which option to pursue.

---

## 2. `Customer` — enriched customer/project master (Excel)

**Production source:**
```m
Excel.Workbook(File.Contents("C:\Users\cillian.ryan\OneDrive - Kingspan\Customer.xlsx"), null, true)
```

**Contents:** 45 columns.

**Fields exclusively provided by this Excel (NO SAP equivalent):**

| Field | Used in production report |
|---|---|
| **Industry** | Not seen in inventoried dashboards; likely on Extended pages |
| **Company Type** | Not seen in inventoried dashboards |
| **Secondary Grouping** | Not seen in inventoried dashboards |
| **Application** | Not seen in Invoiced Sales dashboard; may be on Extended pages |
| **Sales Representative** (ID) | Detail table on Invoiced Sales Dashboard |
| **Sales Representative Name** | Detail table |
| **Project Coordinator** | Detail table on Invoiced Sales Dashboard |
| **Customer Project Name** | "ProjectName" in detail table |
| **Territory Sold-to / Ship-to / Bill-to / Payer** | Not seen in inventoried dashboards |
| **Sold to party Description** (customer name) | Not seen in inventoried Invoiced dashboards but likely on Extended/detail pages |
| **Cost of sales** | Not seen in current dashboards; likely on Extended pages |
| **Gross Margin** and **Gross margin %** | Likely on Extended pages |

**Impact:** the Invoiced Sales - Dashboard detail table cannot be fully reproduced without the Sales Rep, Project Coordinator, ProjectName, Material Description columns. All these come from `Customer.xlsx` joined to Billing on `Material`.

**Options:**
1. **Continue sourcing from the same Excel file** (fastest)
2. **Move to a shared/central Excel** (SharePoint/OneLake)
3. **Backfill via SAP masters:** SAP has customer master (KNA1), material master (MARA), sales rep (VBAK.VKGRP or partner functions). Each field would need to be sourced from the right master via a new Datasphere view — significant effort.
4. **Ask business owner** whether the Customer.xlsx pipeline (who maintains it, how often it's refreshed) is a documented process or ad-hoc

**Warning:** Fields like `Application`, `Industry`, `Company Type`, `Secondary Grouping`, `Territory Sold-to` etc. appear to be **manually curated attributes** — they may not exist anywhere in SAP. Verify with business owner.

**Recommended action:** Confirm with Ana / James which Customer.xlsx fields are actually used on the pages that need to be rebuilt. If Extended pages use `Application`, `Industry`, `Gross Margin` — those pages will be blocked without this file.

---

## 3. Salesforce sources (`User`, `Quote`, `Quote Line Item`)

**Production source:**
```m
Salesforce.Data("https://login.salesforce.com/", [ApiVersion=48, CreateNavigationProperties=true])
```

**Contents:**
- `User` — 100+ columns, Salesforce user records
- `Quote` — 90+ columns including custom fields (`Expiry_Day_Count__c`, `Project__c`, `Total_List_Price__c`, `Size_Sqft__c` etc.)
- `Quote Line Item` — 30+ columns including custom fields (`Net_Unit_Price__c`, `Product_Family__c`, `List_Extended__c`, `Net_Extended__c` etc.)

**Used by:** internal relationships among `Quote`/`QLI`/`User`. **Not seen** on any of the pages inventoried so far (Invoiced Sales, Order Intake, Backlog). May be used on pages not yet fully inspected (Extended Invoiced Sales, Extended Order Intake — 14 and 16 visuals each pending deeper analysis).

**Impact:** If a report page uses quote fields (list price, discount, opportunity link), those cannot be reproduced without Salesforce credentials configured.

**Options:**
1. **Continue sourcing from Salesforce API** (requires org's Salesforce credentials + Power BI service connector)
2. **Drop quote-related visuals** if they're not core to the reproduction
3. **Ask business owner** whether Salesforce quote data is required in the new dashboards or is legacy

**Recommended action:** ask business owner. If Salesforce is required, the new project needs its own Salesforce connection separate from SAP Datasphere.

---

## 4. Other observations

### Time Intelligence auto-tables
Production has `__PBI_TimeIntelligenceEnabled = 1`, generating one `LocalDateTable_<guid>` per date column (~44 of them). These are automatic — enabling Time Intelligence in the new project regenerates equivalent ones. No external dependency, just a Power BI setting.

### Report theme
Uses `CY26SU05` (Power BI's default July 2026 theme). No custom theme file — the AWIP branding shown in cells is only via the Kingspan image resource and dark blue `#004288` accent, not a JSON theme override.

### Kingspan logo image
Referenced as `kingspan-roofing-waterproofing8422940714883275.png` in `Report/StaticResources/RegisteredResources`. The image itself is embedded in the pbip's RegisteredResources folder — need to copy this into the new project's resources.

---

## Blocker summary

| Missing source | Blocks | Severity | Resolution needed |
|---|---|---|---|
| KNVV.csv | AAGC Description slicer | LOW | Fastest: keep sourcing from file. Best: move to shared location or add to Datasphere |
| Customer.xlsx | Sales Rep, Project Coord, ProjectName, Material Desc columns in detail tables. Possibly Application/Industry/Region-business on Extended pages. Cost/GM measures. | **HIGH** | Confirm with business owner what's used and where the file should live |
| Salesforce (Quote/QLI/User) | Any Quote-related visuals on Extended pages (not yet fully inventoried) | UNKNOWN | Inventory Extended pages first |

## Questions to Ana / James (Phase 9 deliverable)

1. Is Customer.xlsx a maintained business dataset or a one-off dump? Who owns it? Where should it live in the new architecture?
2. Are the Extended Invoiced Sales / Extended Order Intake pages (14/16 visuals) still in scope for the new project, or being retired?
3. Does the AAGC slicer still need to be functional in the new dashboards? If yes, is there a Datasphere view we can add for `KNVV`?
4. Does the new project need Salesforce Quote / QLI data, or is that scope being dropped?
5. Fields like `Application`, `Industry`, `Sold to party Description`, `Sales Representative Name` — are these SAP-sourced (need to expose via Datasphere) or manually maintained (need shared file)?
6. Do you expect `Cost of sales`, `Gross Margin`, `Gross margin %` KPIs to survive the migration? If yes, source needs to be identified.

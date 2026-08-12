# AWIP Commercial Sales — PBIP project

Reusable Power BI Project (PBIP) that pairs the AWIP Commercial Sales semantic model with the *Sales & Order Intake Summary* report. Sources are the two SAP Datasphere analytical models named in `mapping.md`.

## Layout

```
AWIP_Commercial_Sales.PBIP/
├── AWIP_Commercial_Sales.pbip              ← open this in Power BI Desktop (Developer mode)
├── mapping.md                              ← field mapping + verification checklist
├── AWIP_Commercial_Sales.SemanticModel/
│   └── definition/                         ← TMDL: model, tables, relationships, measures
└── AWIP_Commercial_Sales.Report/
    ├── StaticResources/…/AWIP.json         ← report theme
    └── definition/pages/SalesOrderIntakeSummary/
                                            ← page + visuals (PBIR JSON)
```

## First-refresh checklist

1. Open `AWIP_Commercial_Sales.pbip` in Power BI Desktop (2.140 or later, Developer mode enabled under *Options → Preview features → Power BI Project*).
2. In the Model view, set the **four parameters** (`p_DatasphereServer`, `p_DatasphereSpace`, `p_SalesOrganization`, `p_CompanyCode`) — the shipped defaults are `PR_KRW` / `6000` / `6000`.
3. Sign in to SAP Datasphere with an account that can query the two RL views.
4. Verify the columns in `mapping.md` against the actual view output — remap the M `Table.TransformColumnTypes` calls if any names differ.
5. Refresh both tables. `DimDate` and `_Measures` refresh from DAX and need no source.
6. Save the file (Desktop will re-serialise the PBIR JSON — expect small format-only diffs).

## Do not publish

Nothing in this project has been uploaded to a workspace or overwritten `Billing.pbix` / `Sales.pbix`. Publish only after the checklist above passes locally.

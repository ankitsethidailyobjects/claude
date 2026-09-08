# DailyObjects — Oct/Nov 2026 Inventory Demand Projection

Reproducible pipeline that builds October & November 2026 inventory demand
projections at child-SKU grain (rolled to parent), reconciled to gross-revenue
targets **Oct ₹12.00 cr / Nov ₹11.50 cr**.

## Deliverable
`out/DailyObjects_OctNov2026_Inventory_Projection.xlsx` — 7 tabs: README,
Category_Reconciliation, Parent_Rollup, SKU_Projection (5,105 SKUs),
Assumptions_Method, Flags_Ambiguities, Monthly_Actuals_Reference.

## Method
1. **Base run-rate** = avg of Jul + Aug 2026 sold demand (clean non-sale months).
2. **Demand filter** = order statuses excl. `paymentFailed`/`paymentPending`/`cancel`; gross = units × `Selling Price`.
3. **Seasonality** = 2025 multiplicative category shift (normal Jun/Jul → Oct/Nov) applied to the 2026 base mix.
4. **Event de-distortion** = non-HPS base ⇒ Sep-HPS deep-tail SKUs project ~0.
5. **Reconcile** per-category to targets; roll up to 248 parents.

## Pipeline
```
export GKEY="<google-drive-api-key>"      # never commit the key
bash run_batch.sh < months.txt            # download each DMR -> aggregate -> delete raw
python3 aggregate.py <dmr.csv|xlsx> <label>   # one month -> agg/skus_<label>.csv
python3 build_model.py                     # base + seasonal shift + reconcile -> agg/model_sku.csv
python3 build_tabs.py                       # COGS/margin, parent rollup, flags -> agg/tab_*.csv
python3 build_excel.py                      # -> out/*.xlsx
```

## Data sources (Google Drive)
- 24 monthly DMRs: all 2025 + Jan–Aug 2026 + Sep-2026 HPS (aggregated to disk, never held whole in memory).
- Parent-child mapping: 248 parents / 17,848 SKUs.
- COGS: July 2026 planning sheet (~1,496 SKUs, ~20% of projected gross).

`raw/` (source DMRs / mapping) is git-ignored — inputs, not work product.

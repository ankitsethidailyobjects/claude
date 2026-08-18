# CONTEXT HANDOFF — DailyObjects July 2026 D2C P&L (New vs Repeat, to CM2)

_Purpose: paste/upload this into a new Claude session to continue without re-deriving. Owner: ankit.sethi@dailyobjects.com. Currency ₹ (INR)._

## 1. Objective
Build a July 2026 **D2C P&L at user level, split New vs Repeat, down to CM2**. Pull Meta + Google spend, coupon spend (DMR), CRM (Moengage), and triangulate marketing cost to New vs Repeat.

## 2. Source files (Google Drive IDs)
- **COGS/CM engine** — `Web_Updated_cogs_CMFile.xlsx` · id `1YhQIdUAVU_c8Dn6kPi3i6GVI0EvOjGnY`. SKU/day-level P&L (Website/D2C) with Revenue, Net Rev, Net COGS, Product Margin, Fulfilment, CM1, CM2, Ad Spends. Sheet2 = category pivot; **has NO user-type dimension**.
- **July DMR** — `july_DMR_unmasked.csv` · id `1B0NG665z4p24itpiQqH_mngGPNN_2o3U` · **47 MB**. Line-item level. Key cols: `Last Status` (delivered/shipped/cancel/paymentFailed…), `New User` (**TRUE=new / FALSE=repeat**), `Product Grand Total(FF)` (line revenue, net of coupon), `Order Discount`/`Product Discount`/`Coupon Code`, `Category`, `Qty Ordered`, `Order No.`, `Source`.
- June DMR native sheet id `15QmE2tqXgT5Sxd-l-0B9s91T0_DhzS8zlAfOvpy7Jo8`. Other months as CSV in same folder (parent `1YcnPpUClp9ZGDLLAyDA0iJjYLaThyziy`).
- **Shopify = INTERNATIONAL site — DO NOT use for India D2C P&L.** (Shopify MCP token also expired.)

## 3. HARD CONSTRAINT (why splits are sampled, not exact)
The 47 MB DMR **cannot be fully aggregated** with available tools: Drive download caps at **10 MB**; `read_file_content` **truncates to ~1 MB (only July-31 rows, file is date-sorted desc)**. Oversized MCP outputs DO save to local disk (`/root/.claude/.../tool-results/*.txt`) but the DMR read is still truncated at source. So exact full-month New/Repeat splits are **not computable in-session**.
- **To finalise exactly:** get a July DMR pivot — Rows `New User` × `Category`; split by `Last Status`; Values = Σ `Product Grand Total(FF)`, Σ (`Order Discount`+`Product Discount`), Σ `Qty Ordered`, distinct `Order No.`. Drop into the model's yellow inputs.

## 4. Numbers already extracted

### COGS file — grand total (ALL months, all platforms) — Sheet2 pivot
Revenue 331,557,725 · Return Sales 43,246,094 · Net Sales 288,311,631 · **Net Revenue 247,899,469** · Net COGS 111,138,979 · Product Margin 136,760,490 · Fulfilment 22,651,338 · CM1 114,109,152 · **CM2 6,509,793** · Ad Spends 107,599,359 · Qty 207,715.
**Structural ratios (on Net Revenue) used as the P&L backbone:**
- Net Rev ÷ Gross Rev = **0.7477** (removes ~13% returns + GST)
- Net COGS = **44.83%** · Product Margin = **55.17%** · Fulfilment = **9.14%** · **CM1 = 46.03%** · Blended **CM2 = 2.6%**

### Marketing — July 2026 actuals (Windsor.ai)
- **Meta total ₹2,66,59,664** (facebook acct 376923450580801). Split by campaign-name logic:
  - Prospecting / Category / Influencer (non-DPA) = **₹1,69,56,520 (64%) → New-leaning**
  - DPA / Retargeting / Cross-sell (`DPA_Max_Value`, `XXX_DPA_PDP_Views_3D`, `Cross_Sell_*`) = **₹97,03,144 (36%) → Repeat-leaning**
- **Google total ₹86,41,852** (acct 939-315-2332): PMax `PMax - All (Search+Display+Video)` ₹81,52,672 + `Search - Brand - Apr_2026` ₹4,89,181.
- **Combined paid media = ₹3,53,01,516.**
- **CRM (Moengage):** NO rupee spend in API — July sends were all-user broadcast **PUSH** (≈ zero marginal cost). Real cost = Moengage platform fee (invoice). Modeled as input (placeholder ₹5,00,000), attributed 100% Repeat.

### New vs Repeat mix — from JULY-31 DMR SAMPLE ONLY (2,124 line items; 816 realized orders)
- Revenue share: **New 50.6% / Repeat 49.4%** (realized sales)
- AOV: **New ₹2,602 / Repeat ₹3,111**; items/order New 1.68 / Repeat 1.81
- Coupon usage: New 28% of orders / Repeat 34%; product-discount intensity New ~19% / Repeat ~26% of realized rev
- Category mix similar both segments (Cases, Accessories, Bags lead) → blended margins OK directionally
- ⚠️ Single month-end day — directional only.

## 5. Marketing → New/Repeat allocation logic (EDITABLE % in model)
| Channel | July ₹ | % New | % Repeat | Rationale |
|---|---:|---:|---:|---|
| Meta – Prospecting/Category/Influencer | 16,956,520 | 100% | 0% | Pure acquisition |
| Meta – Retargeting/DPA/Cross-sell | 9,703,144 | 20% | 80% | Retargets past visitors/buyers |
| Google – PMax | 8,152,672 | 70% | 30% | Acquisition-heavy, some returning |
| Google – Brand Search | 489,181 | 40% | 60% | Brand terms skew existing-intent |
| CRM – Moengage | 500,000 (input) | 0% | 100% | Retention |
→ **New media ≈ ₹2.48 Cr · Repeat media+CRM ≈ ₹1.10 Cr.** (Coupons NOT re-subtracted at CM2 — already netted into revenue above CM1.)

## 6. Model result (directional v1; scale anchor = ₹8.3 Cr July net revenue)
| Line | New | Repeat | Total |
|---|---:|---:|---:|
| Net Revenue | 4.20 Cr | 4.10 Cr | 8.30 Cr |
| CM1 (46%) | 1.93 Cr | 1.89 Cr | 3.82 Cr |
| Marketing | 2.48 Cr | 1.10 Cr | 3.58 Cr |
| **CM2** | **−0.55 Cr (−13%)** | **+0.79 Cr (+19%)** | **+0.24 Cr (+2.9%)** |
- CM2/order: **New −₹253 · Repeat +₹447.** Mktg/order: New ₹1,149 (CAC) · Repeat ₹624.
- **Validation:** blended CM2 2.9% ≈ COGS-file blended CM2 2.6% ✔
- **Story:** New users CM2-negative on first order (CAC > first-order contribution); Repeat strongly positive; LTV justifies new-user acquisition loss.

## 7. Scale anchor logic (₹8.3 Cr net rev — an ESTIMATE, replace with DMR actual)
Two methods converge: (a) COGS grand-total net rev 247.9M ÷ ~3 months (ad-spend 107.6M ÷ ~35M/mo) ≈ 82.7M; (b) July paid media 3.53 Cr ÷ 43% ad-to-rev ≈ 82M.

## 8. Deliverable
`DailyObjects_July2026_PnL_New_vs_Repeat.xlsx` — tabs: **Drivers & Sources** (yellow = editable inputs), **P&L — New vs Repeat** (live formulas to CM2), **COGS Reference**, **Method & Caveats**.

## 8b. GA4 calibration of ad-spend split (added)
GA4 India acct `273672074`, July, `new_vs_returning` × `source`/`medium` × `purchase_revenue`/`transactions` (Windsor).
- Site-wide: New = 41% of purchase revenue / 45% of transactions; Returning 59% / 55%. (GA4 new/returning is **session-based**, not first-purchase — differs from DMR.)
- Paid channel observed mix (by revenue): **Meta `facebook instagram/paid` = 45% new / 55% returning**; **Google `google/cpc` = 57% new / 43% returning**.
- GA4-based spend split: New media ₹1.70 Cr, Repeat media ₹1.88 Cr (+CRM).

**KEY FINDING — attribution flips the story (same margins, same totals, blended CM2 = +2.9% either way):**
| Scenario | New CM2 | Repeat CM2 |
|---|---:|---:|
| Intent-based (Meta prospecting=new) | −13% | +19% |
| GA4 last-click (observed) | +5.6% | +0.2% |
GA4 last-click understates new-media (Meta upper-funnel credit goes to Google Brand/Direct on final click; "visited-before" buyers counted as returning). Intent ≈ ceiling on new-media, GA4 ≈ floor. Realistic: New CM2 −13%→+6%, Repeat 0%→+19%. New xlsx tab: **Attribution Scenarios**.

## 9. Open items / next steps
1. Replace scale anchor + split ratios with **full-month DMR pivot** (see §3).
2. Get **actual Moengage CRM cost** (invoice).
3. Optional: refine Meta/Google New/Repeat % with GA4 new-vs-returning purchase data (Windsor `googleanalytics4`, accts DO-GA4 273672074).
4. Optional: per-category COGS mapping (DMR categories ≠ COGS-file categories) for segment-specific margins.

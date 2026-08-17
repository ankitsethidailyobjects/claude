# DailyObjects — Customer Cohort & Retention Project · Handoff Brief

*Context transfer for continuing this work in a new Claude session. Share this file at the start of the new session.*

---

## 0. How to use this brief
Paste/upload this file into the new Claude session and say: *"This is the context from my previous session. Continue from here."* Then provide **data access** (see §2) — do **not** expect the key to be in this file; paste your Google Drive API key separately when asked.

---

## 1. Objective & evolution
Build a **productionizable customer segmentation + CRM-activation framework** for DailyObjects (premium tech accessories & bags, India) from **DMR** order data, feeding **MoEngage**.

The thread evolved through these phases:
1. **Platform retention analysis** — at what lifetime order count does retention stabilize.
2. **Cohort/segmentation system design** (methodology + production architecture proposal).
3. **Execution**: identity resolution → features → K-Means cohorts → category affinity.
4. **Refinements**: user set X=3 (mature = 3+ orders); extended data to Jul 2026; collapsed to **3 named cohorts** (Power / Deal Seekers / Light); added **price-led discount** detection (events, not just coupons); added **sub-category affinity**.
5. **Deliverables**: user repository, multi-grain retention, deck, refresh runbook, retention strategy, cohort×attribute splits.

---

## 2. Data sources & access
- **Data = DMR** (Daily-MIS-Report) order exports on the user's **Google Drive**, 2020–Jul 2026. SKU/order-line grain (one row per item).
- **Access method that worked**: Google **Drive API key** via `curl` (`https://www.googleapis.com/drive/v3/files/<ID>?alt=media&key=<KEY>`). The MCP Drive download caps at 10 MB; the key bypasses it **but only for files shared "anyone with link."**
  - 2025 & 2026 monthly files (colleague `shreyamishra@`) were already link-shared.
  - **2020–2024 annual files (owned by the user) had to be set to "anyone-with-link"** to download. ⚠️ **Open item: revoke that sharing when done.**
- **Key files** (annual = xlsx, monthly = csv/xlsx; layouts/sheet-names differ by year — auto-detect the data sheet & columns):
  - 2020 `DMR_Jan-Dec_2020.xlsx`, 2021 `DMR_Jan-Dec_2021.xlsx`, 2022 `2022 DMR.xlsx`, 2023 `Jan - Dec '23 DMR.xlsx`, 2024 `Jan - Dec '24 DMR.xlsx`
  - 2025: 12 monthly files in Drive folder **"2025 unmasked DMR"**
  - 2026: Jan–Jul in **"2026 unmasked DMR"** (March split HPS / Non-HPS)
- **Price-elasticity workbook** (user-supplied): `DailyObjects_Price_Elasticity_MASTER_2.xlsx` — defines 2025 sale events (weeks) and per-category ASP % drops. Used to validate price-led discount detection.

### Key columns in the DMR
`Order No.` (order id) · `User Email` / `Login Phone Number` / `Mobile` / `Username`(account UUID) (identity) · `Only Date`/`Order Date` · `Item Status` (paid/cancel/etc.) · `Category` / `Sub Category` / `Brand` / `SKU` · `Product Grand Total(FF)` (line GMV / price PAID) · `Qty Ordered` · `Order Discount`/`Product Discount`/`Coupon Code` · `Payment Method` · `Source` (channel).

---

## 3. Data-quality issues discovered (important — carry forward)
1. **Count unique `Order No.`, not rows** (order-line grain; ~1.4 lines/order).
2. **Email masking**: 2024 file masks ~27% of emails to literal `"userEmail"`; 2020–21 use `"na"`. → must resolve identity via **email + phone + account-UUID**.
3. **Phone** looks like scientific notation in some tools but is intact via openpyxl.
4. **Coupon/discount fields unreliable by year**: 2020/21 over-populated (~100%), 2022 absent. → coupon counted only from **2023+**; rely on **price-led signal** cross-year.
5. **DMR hides price-led (event) discounts** — it stores only final price. Detected via **weekly category ASP dips** vs a 65th-pctile reference.
6. **Category taxonomy inconsistent** across years; some labels ("Designer Cases", "Sale") carry **negative GMV** (returns/sign). → floor GMV at 0 for affinity; keyword-map to macro (Tech vs Designer/Bags).
7. **Hub-identifier over-merge**: a shared COD/call-centre phone once merged 14,320 emails into one "customer" → **suppress identifiers with degree >10** before union-find.
8. Negative lifetime GMV for a few users (net returns) → floor at 0 for clustering.

---

## 4. Methodology & key decisions (locked)
- **Identity resolution**: union-find over {valid email, normalized 10-digit phone, account UUID}, with hub suppression (degree>10). → **1,444,804 identities** from 2.86M attributable orders.
- **Valid order** = paid (exclude `paymentPending`/`paymentFailed`). Cancels/returns kept as placed-and-paid.
- **Retention stabilization (X)**: curve elbow ≈ 7 orders; **user chose X = 3** for the lifecycle boundary → **Mature = 3+ orders**. Slices: **O1 (1 order) / O2 (2) / 3+ (mature)**.
- **Discount enrichment**: per order `discounted = max(coupon/DMR [2023+], price-led event depth)`. Event depth from weekly category-ASP dip vs 65th-pctile reference (threshold ≥8%). Coupon-only 21% of orders → **enriched 49%**.
- **Behavioural cohorts** (mature 3+): **K-Means k=3** on frequency + value + enriched discount → **Power Users / Deal Seekers / Light Users** (named deterministically by discount reliance & frequency×GMV). B2B/whales rule-carved (≥50 orders or ≥10 units/order).
- **Category affinity**: macro **Tech vs Designer/Bags** (spend-share score) + **primary/secondary sub-category** (74 sub-cats).
- **Activity state (current definition — GLOBAL, not cohort-specific)**: Active ≤90d since last order · Lapsed 91–270d · Dormant >270d. ⚠️ **Pending: re-run as cohort-relative / per-user cadence** (median inter-order gap: Power ~194d, Deal ~397d, Light ~508d, O2 ~916d) — user said "later, I'll tell you when."
- **Value tier**: lifetime-GMV percentiles (VIP top5% / High next15% / Mid next30% / Low bottom50%).
- **Leakage-safe validation**: assign cohorts at anchor **T0 = 2025-07-31**, measure forward return in next 30/90/365 days (data runs to 2026-07-31). Production snapshot **T0 = 2026-07-31**.

---

## 5. Key results (numbers to reuse)
**Base (as of 31 Jul 2026, 1,377,694 customers):** O1 = 944,518 (68.6%) · O2 = 229,895 (16.7%) · **3+ mature = 203,281 (14.8%)**.

**3 cohorts (mature) + forward 12-mo retention (validated):**
| Cohort | Users | % | Avg orders | Enriched disc% | 1-yr retention |
|---|--:|--:|--:|--:|--:|
| Power Users | 55,806 | 27.5% | 7.3 | 52% | **48.3%** |
| Deal Seekers | 62,502 | 30.7% | 3.6 | **80%** | 28.7% |
| Light Users | 84,973 | 41.8% | 3.7 | 27% | 24.8% |

**Retention by slab (1mo / 1qtr / 1yr):** O1 1.5/3.2/**8.5%** · O2 3.3/6.9/17.4% · Power 12.4/24.3/48.3% · Deal 5.9/12.1/28.7% · Light 4.9/10.3/24.8%.

**Category affinity:** ~74% Tech / ~15% Designer-Bags / ~6% Mixed. **Sub-category stickiness:** Wireless Charger, Organisers, Desks, Backpacks retain best; "Sale", "Mobile Accessories", "Bags & Sleeves" near one-and-done.

**Activity mix (mature):** ~13% Active / ~27% Lapsed / ~59% Dormant. Repurchase spikes around HPS (event-driven).

**Headline finding:** severe leaky bucket (68.6% one-time, 8.5% yearly return) + discount/event dependence. Biggest lever = win the 2nd order.

---

## 6. Deliverables produced (in `analysis/seg/`)
- `user_repository.csv` (1.38M rows — **PII**, not in git): contact keys + cohort + value_tier + activity_state + cat_affinity + tech/bags scores + primary/secondary sub-category + RFM/discount. `moengage_upload.csv` = push subset.
- Retention: `retention_cumulative.csv`, `retention_monthly.csv`, `retention_quarterly.csv`, `retention_curves.png`.
- Cohort×attribute splits: `cohort_splits.csv`, `cohort_splits_chart.png`, `cohort_splits.html`.
- Docs: `DailyObjects_Retention_Strategy.docx`, `DailyObjects_Cohort_Refresh_Runbook.docx`, `DailyObjects_User_Modelling_Deck.pptx`.
- Published artifacts (claude.ai): retention analysis, cohort blueprint, 3-cohort model, cohort×attribute retention.

---

## 7. Pipeline & scripts (in `analysis/`, run in this order for a refresh)
1. `extract_features.py <raw_file> <out>` — per (order, category): ids, gmv, qty, discount, payment, source. Run per DMR file → `data/feat/`.
2. `extract_subcat.py <raw_file> <out>` — per (order, sub_category): gmv, qty → `data/subcat/`.
3. `step1_resolve.py` — identity resolution (union-find + hub suppression) → `seg/orders_resolved.csv`, `seg/ordercat_resolved.csv`.
4. `enrich_discounts.py` — weekly-ASP event detection + per-order enriched discount → `seg/orders_enriched.csv`.
5. `step2_features.py <T0> <suffix> [X=3]` — leakage-safe user features as-of T0 → `seg/userfeat_<suffix>.csv`.
6. `step6_3cohorts.py` — K-Means k=3 (Power/Deal/Light) + affinity + validation → `seg/labels_prod.csv`, `labels_dev.csv`, profiles.
7. `build_repository.py` — assemble master `seg/user_repository.csv` (+ contact keys).
8. `retention_model.py` — monthly/quarterly/yearly retention by cohort.
9. `build_cohort_splits.py` — cohort × attribute retention table + chart.
10. Doc/deck builders: `build_strategy_doc.py`, `build_runbook_doc.py`, `build_deck.py`, `build_results.py`, `build_splits_artifact.py`.

**Environment:** Python + pandas, openpyxl, scikit-learn, matplotlib, python-docx, python-pptx. Repo git-ignores `data/`, `*.csv`, `*.xlsx` (PII kept out of version control).

---

## 8. Open items / pending decisions
1. **Cohort-relative / per-user activity states** — approved in principle, user will trigger later (see §4).
2. **Push cohort attributes to MoEngage** — connector available; not yet pushed. Warehouse = truth, MoEngage = activation (attributes + a few events; not raw ML features).
3. **Revoke "anyone-with-link" sharing** on the 2020–2024 DMR files (privacy).
4. **Sub-category affinity in campaigns** and an **entry-product → retention** acquisition view (offered, not built).
5. Warehouse DDL + orchestration (6-table model in the blueprint) — designed, not implemented.

---

## 9. Working branch
Git branch: `claude/retention-analysis-order-count-ai4xmz` (all scripts + non-PII outputs committed; PII CSVs excluded).

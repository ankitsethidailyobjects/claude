# DailyObjects — August 2026 D2C Revenue Plan

Goal to hand the performance-marketing SPOC: hit **₹10.5 cr** in August at maximum ROAS efficiency,
expressed as a new-vs-repeat user target, a category-level split, and a weekend freebie plan.

## Deliverables
- **`DailyObjects_August_D2C_Plan.xlsx`** — 5 tabs: Exec Summary · New vs Repeat · Category Targets · Meta Baseline (Jun/Jul) · Weekend Freebie.
- **`august_plan.html`** — shareable one-pager (also published as a Claude artifact).
- `meta_2026.py` / `plan_model.py` / `build_xlsx.py` — the model and generators.

## Headline plan
| Lever | July 2026 actual | August target |
|---|---|---|
| Total D2C revenue | ₹10.81 cr | **₹10.50 cr** |
| Orders | 42,138 | 40,626 |
| New orders (users) | 22,727 (3.67 M) | **18,762 (2.97 M)** |
| Repeat orders (users) | 19,411 (1.31 M) | **21,864 (1.43 M)** |
| Order mix (new / repeat) | 54% / 46% | **46% / 54%** |
| Meta spend | ₹2.67 cr | ₹2.36 cr |
| Blended Meta ROAS | 3.01x | **3.39x** (bar to hold: 3.28x, Aug 1–4) |

## How the numbers are built
- `Total revenue = new_orders × ₹2,450 + repeat_orders × ₹2,700`
- `Users required = orders ÷ conversion rate` — new CVR 0.63%, repeat CVR 1.53% (web+app daily tracker).
- Category economics (CAC, ROAS, AOV, LTV tier) from Meta Ads June & July 2026, campaign→category mapping.
- New-acquisition CAC ≈ ₹903; repeat/retargeting cost/order ≈ ₹865 (only ~35% of repeat is paid-assisted).
- High-LTV categories (Power Bank, Stack, Charging Station) get a share uplift; Watch Bands dialled down.

## Key assumptions to validate with Finance
- Segment AOVs (₹2,450 new / ₹2,700 repeat) and LTV tiers.
- Meta-attributed revenue ≈ 76% of total D2C.
- Weekend freebie uplift +14% on a 2-day base (≈ ₹0.38 cr for the 4 remaining weekends).
- Guardrail: keep new intake ≥ ~2.9 M users so the Sept–Oct repeat pool doesn't contract.
